#!/usr/bin/env python3
"""Interleaved cold-start benchmark driver (stdlib only).

Subcommands:
  env  record host facts (kernel, cgroup, Docker, JDK, disk) as JSON
  run  run N cold starts per variant in randomised, interleaved order

Each start is `docker create` + `docker start` + `docker wait`; the apps close
themselves after startup, so "wall" is container start to exit (not time to a
first HTTP response). While the container runs, its cgroup v2 `cpu.stat` and
`memory.peak` are polled; the cgroup disappears on exit, so the last sample is
a lower bound (very short runs may be missed entirely and are recorded as null).

Ratios are only meaningful inside one run on one VM. Never compare absolute
numbers across runs.
"""
import argparse
import datetime
import json
import os
import platform
import random
import re
import shutil
import subprocess
import sys
import threading
import time

CPU_PROFILES = {
    # p06 mirrors measure-runtime.sh (--cpus=.6 and ActiveProcessorCount=1)
    "p06": {"cpus": "0.6", "jto": "-XX:ActiveProcessorCount=1"},
    "p10": {"cpus": "1.0", "jto": None},
    "p20": {"cpus": "2.0", "jto": None},
}
MODULES = ["original", "tomcat", "data-jpa", "data-rest", "activemq", "all"]
PROFILES = ["plain", "aot", "cds", "aot-cds", "aot-caching", "aot-aot-caching", "alpaquita", "native"]
STARTED_RE = re.compile(r"Started Application in ([0-9.]+) seconds")
PROCESS_RE = re.compile(r"process running for ([0-9.]+)")
CGROUP_PATTERNS = ("/sys/fs/cgroup/system.slice/docker-{}.scope", "/sys/fs/cgroup/docker/{}")


def image_name(module, profile, side):
    suffix = "" if side == "head" else f"-{side}"
    return f"docker.io/library/spring-boot-benchmark-{module}-{profile}{suffix}:LOCAL-SNAPSHOT"


def sh(args, **kw):
    return subprocess.run(args, check=True, capture_output=True, text=True, **kw)


def try_out(args, stream="stdout"):
    try:
        res = subprocess.run(args, capture_output=True, text=True, timeout=60)
        return (res.stdout if stream == "stdout" else res.stderr).strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def read_kv(path):
    out = {}
    with open(path) as f:
        for line in f:
            parts = line.split()
            if len(parts) == 2 and parts[1].lstrip("-").isdigit():
                out[parts[0]] = int(parts[1])
    return out


class CgroupPoller(threading.Thread):
    pattern_idx = None  # discovered once, reused for later containers

    def __init__(self, cid):
        super().__init__(daemon=True)
        self.cid = cid
        self.stop_flag = threading.Event()
        self.cpu = None
        self.mem_peak = None

    def run(self):
        while not self.stop_flag.is_set():
            idxs = [CgroupPoller.pattern_idx] if CgroupPoller.pattern_idx is not None else range(len(CGROUP_PATTERNS))
            for i in idxs:
                base = CGROUP_PATTERNS[i].format(self.cid)
                try:
                    self.cpu = read_kv(base + "/cpu.stat")
                    CgroupPoller.pattern_idx = i
                except OSError:
                    continue
                try:
                    with open(base + "/memory.peak") as f:
                        self.mem_peak = int(f.read().strip())
                except (OSError, ValueError):
                    pass
            time.sleep(0.01)

    def stop(self):
        self.stop_flag.set()
        self.join(timeout=2)


def run_once(image, cpus, cpuset, jto, timeout):
    create = ["docker", "create", "--cpus", cpus, "--memory", "1g"]
    if cpuset:
        create += ["--cpuset-cpus", cpuset]
    if jto:
        create += ["-e", f"JAVA_TOOL_OPTIONS={jto}"]
    cid = sh(create + [image]).stdout.strip()
    rec = {"ok": False, "exit_code": None, "timed_out": False, "oom_killed": None}
    try:
        poller = CgroupPoller(cid)
        t0 = time.perf_counter()
        sh(["docker", "start", cid])
        poller.start()
        try:
            subprocess.run(["docker", "wait", cid], check=True, capture_output=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            rec["timed_out"] = True
            subprocess.run(["docker", "kill", cid], capture_output=True)
        t1 = time.perf_counter()
        poller.stop()
        state = sh(["docker", "inspect", "-f", "{{.State.ExitCode}} {{.State.OOMKilled}}", cid]).stdout.split()
        rec["exit_code"] = int(state[0])
        rec["oom_killed"] = state[1] == "true"
        logs = subprocess.run(["docker", "logs", cid], capture_output=True, text=True)
        text = logs.stdout + logs.stderr
        started = STARTED_RE.search(text)
        process = PROCESS_RE.search(text)
        rec["wall_s"] = round(t1 - t0, 4)
        rec["started_s"] = float(started.group(1)) if started else None
        rec["process_s"] = float(process.group(1)) if process else None
        cpu = poller.cpu or {}
        rec["cpu_usage_usec"] = cpu.get("usage_usec")
        rec["nr_periods"] = cpu.get("nr_periods")
        rec["nr_throttled"] = cpu.get("nr_throttled")
        rec["throttled_usec"] = cpu.get("throttled_usec")
        rec["mem_peak_bytes"] = poller.mem_peak
        rec["ok"] = rec["exit_code"] == 0 and not rec["timed_out"] and started is not None
        if not rec["ok"]:
            rec["log_tail"] = text.strip().splitlines()[-15:]
    finally:
        subprocess.run(["docker", "rm", "-f", cid], capture_output=True)
    return rec


def parse_cpuset(spec):
    cpus = set()
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            cpus.update(range(int(a), int(b) + 1))
        else:
            cpus.add(int(part))
    return cpus


def read_first(path, key=None):
    try:
        with open(path) as f:
            for line in f:
                if key is None:
                    return line.strip()
                if line.startswith(key):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return None


def cmd_env(args):
    info = {
        "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "kernel": platform.release(),
        "nproc": os.cpu_count(),
        "cgroup_fs": try_out(["stat", "-fc", "%T", "/sys/fs/cgroup"]),
        "cgroup_controllers": read_first("/sys/fs/cgroup/cgroup.controllers"),
        "docker_version": try_out(["docker", "version", "--format", "{{.Server.Version}}"]),
        "docker_cgroup": try_out(["docker", "info", "--format", "{{.CgroupVersion}} {{.CgroupDriver}}"]),
        "java": try_out(["java", "-version"], stream="stderr") if shutil.which("java") else None,
        "mem_total": read_first("/proc/meminfo", "MemTotal"),
        "cpu_model": read_first("/proc/cpuinfo", "model name"),
        "disk_root_free_gb": round(shutil.disk_usage("/").free / 2**30, 1),
        "runner_image_version": os.environ.get("ImageVersion"),
    }
    if args.out:
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        with open(args.out, "w") as f:
            json.dump(info, f, indent=2)
    print(json.dumps(info, indent=2))


def cmd_run(args):
    cpuset = args.cpuset or None
    if cpuset and hasattr(os, "sched_setaffinity"):
        others = set(range(os.cpu_count())) - parse_cpuset(cpuset)
        if others:
            os.sched_setaffinity(0, others)  # keep the harness off the benchmark cores
    profiles = [p for p in args.profiles.split(",") if p]
    sides = [s for s in args.sides.split(",") if s]
    variants = [{"side": s, "profile": p, "image": image_name(args.module, p, s)} for p in profiles for s in sides]
    for v in variants:
        v["image_id"] = try_out(["docker", "image", "inspect", "-f", "{{.Id}}", v["image"]])
        if not v["image_id"]:
            sys.exit(f"missing image {v['image']}")
    rng = random.Random(args.seed)
    result = {
        "schema": 1, "module": args.module, "cpuset": cpuset, "iterations": args.iterations,
        "repeats": args.repeats, "seed": args.seed, "memory": "1g",
        "harness_affinity": sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None,
        "variants": variants, "samples": [],
        "started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    os.makedirs(args.out, exist_ok=True)
    out_file = os.path.join(args.out, f"results-{args.module}.json")

    def flush():
        tmp = out_file + ".tmp"
        with open(tmp, "w") as f:
            json.dump(result, f)
        os.replace(tmp, out_file)

    for repeat in range(1, args.repeats + 1):
        for cp in [c for c in args.cpu_profiles.split(",") if c]:
            prof = CPU_PROFILES[cp]
            for v in variants:  # discarded warm-up so page cache and image layers are hot for every variant
                run_once(v["image"], prof["cpus"], cpuset, prof["jto"], args.timeout)
            for i in range(args.iterations):
                order = variants[:]
                rng.shuffle(order)
                for v in order:
                    rec = run_once(v["image"], prof["cpus"], cpuset, prof["jto"], args.timeout)
                    rec.update(repeat=repeat, cpu_profile=cp, iteration=i, side=v["side"], profile=v["profile"])
                    result["samples"].append(rec)
                    if not rec["ok"]:
                        print(f"WARNING: failed run {v['side']}/{v['profile']} {cp} #{i}: exit={rec['exit_code']} "
                              f"timeout={rec['timed_out']}", file=sys.stderr)
            flush()
            print(f"done repeat={repeat} cpu_profile={cp}", flush=True)
    result["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    flush()
    bad = [v for v in variants
           if not any(s["ok"] for s in result["samples"] if s["side"] == v["side"] and s["profile"] == v["profile"])]
    if bad:
        sys.exit(f"no successful run for: {[(v['side'], v['profile']) for v in bad]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("env")
    e.add_argument("--out")
    e.set_defaults(fn=cmd_env)
    r = sub.add_parser("run")
    r.add_argument("--module", required=True, choices=MODULES)
    r.add_argument("--profiles", required=True)
    r.add_argument("--sides", default="head")
    r.add_argument("--cpu-profiles", default="p06")
    r.add_argument("--iterations", type=int, default=30)
    r.add_argument("--repeats", type=int, default=1)
    r.add_argument("--cpuset", default="")
    r.add_argument("--timeout", type=int, default=120)
    r.add_argument("--seed", type=int, default=20260101)
    r.add_argument("--out", required=True)
    r.set_defaults(fn=cmd_run)
    args = ap.parse_args()
    if args.cmd == "run":
        unknown = [p for p in args.profiles.split(",") if p not in PROFILES] + \
                  [c for c in args.cpu_profiles.split(",") if c not in CPU_PROFILES]
        if unknown or args.iterations < 1 or args.repeats < 1:
            ap.error(f"invalid arguments: {unknown}")
    args.fn(args)


if __name__ == "__main__":
    main()
