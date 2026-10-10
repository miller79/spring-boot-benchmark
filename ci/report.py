#!/usr/bin/env python3
"""Summaries and trend series from bench.py results (stdlib only).

  report.py summary <results-dir>   markdown for $GITHUB_STEP_SUMMARY
  report.py series  <results-dir>   customSmallerIsBetter JSON for github-action-benchmark

Only ratios are published: variant / `plain` of the same module, measured inside
one job. Absolute milliseconds from shared runners are not comparable across runs.
"""
import glob
import json
import os
import random
import statistics
import sys

BOOTSTRAPS = 2000
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


def load(results_dir):
    out = []
    for path in sorted(glob.glob(os.path.join(results_dir, "**", "results-*.json"), recursive=True)):
        with open(path) as f:
            out.append(json.load(f))
    return out


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


def series(results_dir):
    items = []
    for res in load(results_dir):
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
                    items.append({
                        "name": f"{res['module']} / {p} / {cp} / {label} ratio to plain",
                        "unit": "ratio",
                        "value": round(point, 4),
                        "range": f"[{lo:.3f}, {hi:.3f}]",
                        "extra": f"n={len(num)} vs plain n={len(den)}",
                    })
    return json.dumps(items, indent=1)


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("summary", "series"):
        sys.exit(__doc__)
    print(summary(sys.argv[2]) if sys.argv[1] == "summary" else series(sys.argv[2]))
