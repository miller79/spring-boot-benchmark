#!/usr/bin/env python3
"""Summaries and trend series from bench.py results (stdlib only).

  report.py summary <results-dir>   markdown for $GITHUB_STEP_SUMMARY
  report.py series  <results-dir> [--module M]
                                    customSmallerIsBetter JSON for github-action-benchmark;
                                    fails (exit 1) on any malformed or non-allowlisted result

Only ratios are published: variant / `plain` of the same module, measured inside
one job. Absolute milliseconds from shared runners are not comparable across runs.
"""
import glob
import json
import math
import os
import random
import statistics
import sys

from bench import CPU_PROFILES, MODULES, PROFILES

BOOTSTRAPS = 2000
MAX_FILE_BYTES = 20 * 1024 * 1024
MAX_SAMPLES = 20000
MAX_RATIO = 100.0
METRICS = (("started_s", "started"), ("wall_s", "wall"))


def percentile(values, q):
    s = sorted(values)
    k = (len(s) - 1) * q
    lo = int(k)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


def ratio_ci(num, den, seed=1):
    """Ratio of medians with a 95% bootstrap interval."""
    point = statistics.median(num) / statistics.median(den)
    rng = random.Random(seed)
    boots = []
    for _ in range(BOOTSTRAPS):
        n = statistics.median(rng.choices(num, k=len(num)))
        d = statistics.median(rng.choices(den, k=len(den)))
        if d > 0:
            boots.append(n / d)
    return point, percentile(boots, 0.025), percentile(boots, 0.975)


def _num(v, allow_none=False):
    if v is None:
        return allow_none
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def validate(res, path):
    """Raise ValueError unless `res` is a well-formed bench.py result for the module named in `path`.

    Results come from jobs that ran third-party build code, so names are checked against
    allowlists (they end up in published series names, issues and comments) and metrics
    must be finite numbers.
    """
    if not isinstance(res, dict):
        raise ValueError("not an object")
    module = res.get("module")
    if module not in MODULES:
        raise ValueError(f"module not allowed: {module!r}")
    if os.path.basename(path) != f"results-{module}.json":
        raise ValueError("file name does not match module")
    for key in ("iterations", "repeats"):
        if not isinstance(res.get(key), int) or isinstance(res.get(key), bool) or not 1 <= res[key] <= 1000:
            raise ValueError(f"bad {key}")
    variants, samples = res.get("variants"), res.get("samples")
    if not isinstance(variants, list) or not isinstance(samples, list) or len(samples) > MAX_SAMPLES:
        raise ValueError("bad variants/samples")
    for v in variants:
        if not isinstance(v, dict) or v.get("profile") not in PROFILES or v.get("side") not in ("head", "base"):
            raise ValueError(f"bad variant: {str(v)[:80]!r}")
    for s in samples:
        if (not isinstance(s, dict) or s.get("cpu_profile") not in CPU_PROFILES
                or s.get("profile") not in PROFILES or s.get("side") not in ("head", "base")
                or not isinstance(s.get("ok"), bool) or not isinstance(s.get("repeat"), int)
                or isinstance(s.get("repeat"), bool)):
            raise ValueError(f"bad sample: {str(s)[:80]!r}")
        for m in ("started_s", "wall_s"):
            if not _num(s.get(m), allow_none=True) or (s.get(m) is not None and s[m] <= 0):
                raise ValueError(f"bad {m}")
        for m in ("nr_periods", "nr_throttled", "mem_peak_bytes"):
            if not _num(s.get(m), allow_none=True):
                raise ValueError(f"bad {m}")


def load(results_dir, strict=False, module=None):
    """Valid results under results_dir. Invalid files are skipped with a warning, or raise when strict."""
    out = []
    pattern = f"results-{module}.json" if module else "results-*.json"
    for path in sorted(glob.glob(os.path.join(results_dir, "**", pattern), recursive=True)):
        try:
            if os.path.getsize(path) > MAX_FILE_BYTES:
                raise ValueError("file too large")
            with open(path) as f:
                res = json.load(f, parse_constant=_reject_constant)
            validate(res, path)
        except (ValueError, OSError, RecursionError, OverflowError) as e:
            if strict:
                raise ValueError(f"{path}: {e}") from e
            print(f"WARNING: skipping {path}: {e}", file=sys.stderr)
            continue
        out.append(res)
    return out


def _reject_constant(name):
    raise ValueError(f"non-finite constant {name}")


def values(samples, metric, **flt):
    return [s[metric] for s in samples
            if s["ok"] and s.get(metric) is not None and all(s[k] == v for k, v in flt.items())]


def fmt_ratio(r):
    return f"{r[0]:.3f} [{r[1]:.3f}-{r[2]:.3f}]"


def throttle_pct(samples, **flt):
    vals = [100 * s["nr_throttled"] / s["nr_periods"] for s in samples
            if s["ok"] and s.get("nr_periods") and s.get("nr_throttled") is not None
            and all(s[k] == v for k, v in flt.items())]
    return f"{statistics.median(vals):.0f}%" if vals else "n/a"


def summary(results_dir):
    out = []
    for res in load(results_dir):
        samples = res["samples"]
        sides = sorted({v["side"] for v in res["variants"]}, key=lambda s: s != "head")
        profiles = list(dict.fromkeys(v["profile"] for v in res["variants"]))
        cpus = list(dict.fromkeys(s["cpu_profile"] for s in samples))
        out.append(f"## {res['module']}\n")
        out.append(f"{res['iterations']} interleaved cold starts per variant x {res['repeats']} repeat(s), "
                   f"cpuset `{res['cpuset']}`, memory {res['memory']}. Ratios are to `plain` in this job; "
                   f"brackets are 95% bootstrap CIs. Failed runs are excluded and counted.\n")
        for cp in cpus:
            out.append(f"### {res['module']} / {cp}\n")
            out.append("| side | profile | ok/total | started median s | p95 s | started ratio | wall median s | wall ratio | throttled periods | peak mem MiB |")
            out.append("|---|---|---|---|---|---|---|---|---|---|")
            for side in sides:
                for p in profiles:
                    sel = [s for s in samples if s["cpu_profile"] == cp and s["side"] == side and s["profile"] == p]
                    started = values(samples, "started_s", cpu_profile=cp, side=side, profile=p)
                    wall = values(samples, "wall_s", cpu_profile=cp, side=side, profile=p)
                    if not started:
                        out.append(f"| {side} | {p} | 0/{len(sel)} | n/a | n/a | n/a | n/a | n/a | n/a | n/a |")
                        continue
                    rs = rw = "1 (anchor)"
                    if p != "plain":
                        ps = values(samples, "started_s", cpu_profile=cp, side=side, profile="plain")
                        pw = values(samples, "wall_s", cpu_profile=cp, side=side, profile="plain")
                        rs = fmt_ratio(ratio_ci(started, ps)) if ps else "n/a"
                        rw = fmt_ratio(ratio_ci(wall, pw)) if ps and wall and pw else "n/a"
                    mem = [s["mem_peak_bytes"] for s in sel if s["ok"] and s.get("mem_peak_bytes")]
                    mem_s = f"{statistics.median(mem) / 2**20:.0f}" if mem else "n/a"
                    out.append(f"| {side} | {p} | {len(started)}/{len(sel)} | {statistics.median(started):.3f} | "
                               f"{percentile(started, 0.95):.3f} | {rs} | "
                               f"{statistics.median(wall):.3f} | {rw} | {throttle_pct(samples, cpu_profile=cp, side=side, profile=p)} | {mem_s} |")
            out.append("")
            if "base" in sides:
                out.append(f"Head vs base (startup ratio; above 1 means the PR is slower), {res['module']} / {cp}:\n")
                out.append("| profile | started head/base | wall head/base |")
                out.append("|---|---|---|")
                for p in profiles:
                    cells = []
                    for m, _ in METRICS:
                        h = values(samples, m, cpu_profile=cp, side="head", profile=p)
                        b = values(samples, m, cpu_profile=cp, side="base", profile=p)
                        cells.append(fmt_ratio(ratio_ci(h, b)) if h and b else "n/a")
                    out.append(f"| {p} | {cells[0]} | {cells[1]} |")
                out.append("")
            if res["repeats"] > 1:
                out.append(f"Run-to-run noise, {res['module']} / {cp} (started ratio to plain per repeat, head only):\n")
                out.append("| profile | " + " | ".join(f"repeat {r}" for r in range(1, res["repeats"] + 1)) + " | spread (max-min)/mean |")
                out.append("|---|" + "---|" * (res["repeats"] + 1))
                for p in profiles:
                    if p == "plain":
                        continue
                    per = []
                    for r in range(1, res["repeats"] + 1):
                        n = values(samples, "started_s", cpu_profile=cp, side="head", profile=p, repeat=r)
                        d = values(samples, "started_s", cpu_profile=cp, side="head", profile="plain", repeat=r)
                        per.append(statistics.median(n) / statistics.median(d) if n and d else None)
                    good = [x for x in per if x is not None]
                    spread = f"{100 * (max(good) - min(good)) / statistics.mean(good):.1f}%" if len(good) > 1 else "n/a"
                    out.append(f"| {p} | " + " | ".join(f"{x:.3f}" if x is not None else "n/a" for x in per) + f" | {spread} |")
                out.append("")
    return "\n".join(out) if out else "No benchmark results found.\n"


def series(results_dir, module=None):
    items = []
    loaded = load(results_dir, strict=True, module=module)
    if module and not loaded:
        raise ValueError(f"no results-{module}.json found under {results_dir}")
    for res in loaded:
        for cp in dict.fromkeys(s["cpu_profile"] for s in res["samples"]):
            for p in dict.fromkeys(v["profile"] for v in res["variants"]):
                if p == "plain":
                    continue
                for metric, label in METRICS:
                    num = values(res["samples"], metric, cpu_profile=cp, side="head", profile=p)
                    den = values(res["samples"], metric, cpu_profile=cp, side="head", profile="plain")
                    if len(num) < 5 or len(den) < 5:
                        continue
                    point, lo, hi = ratio_ci(num, den)
                    if not all(math.isfinite(x) for x in (point, lo, hi)) or not 0 < point < MAX_RATIO:
                        raise ValueError(f"ratio out of range for {res['module']}/{p}/{cp}/{label}: {point}")
                    items.append({
                        "name": f"{res['module']} / {p} / {cp} / {label} ratio to plain",
                        "unit": "ratio",
                        "value": round(point, 4),
                        "range": f"[{lo:.3f}, {hi:.3f}]",
                        "extra": f"n={len(num)} vs plain n={len(den)}",
                    })
    return json.dumps(items, indent=1)


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 2 or args[0] not in ("summary", "series") or len(args) > (4 if args[0] == "series" else 2):
        sys.exit(__doc__)
    try:
        if args[0] == "summary":
            print(summary(args[1]))
        else:
            only = args[3] if len(args) == 4 and args[2] == "--module" else None
            if len(args) > 2 and only is None:
                sys.exit(__doc__)
            print(series(args[1], only))
    except ValueError as e:
        sys.exit(f"invalid results: {e}")
