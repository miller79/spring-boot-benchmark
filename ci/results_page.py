#!/usr/bin/env python3
"""Render published benchmark JSON as static HTML without executing data.js."""
from datetime import datetime, timezone
from html import escape
import json
import math
from pathlib import Path
import re
import sys

REPO = "https://github.com/miller79/spring-boot-benchmark"
MODULES = {
    "original": "WebFlux (Netty)",
    "tomcat": "Spring MVC (Tomcat)",
    "data-jpa": "Data JPA",
    "data-rest": "Data REST",
    "activemq": "ActiveMQ",
    "all": "All dependencies",
}
PROFILES = ("plain", "aot", "cds", "aot-cds", "aot-caching", "aot-aot-caching", "alpaquita", "native")
CPUS = {"p06": "0.6", "p10": "1.0", "p20": "2.0"}
PREFIX = "window.BENCHMARK_DATA = "
MAX_BYTES = 20 * 1024 * 1024
SHA = re.compile(r"[0-9a-f]{40}")
NUMBER = r"[0-9]+(?:\.[0-9]+)?"
INTERVAL = re.compile(rf"\[({NUMBER}), ({NUMBER})\]")


def number(value):
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) and value > 0)


def reject_constant(_):
    raise ValueError("non-finite JSON number")


def load(path):
    if path.stat().st_size > MAX_BYTES:
        raise ValueError("published data exceeds size limit")
    text = path.read_text(encoding="utf-8").strip()
    if not text.startswith(PREFIX):
        raise ValueError("expected benchmark JSON assignment")
    data, end = json.JSONDecoder(parse_constant=reject_constant).raw_decode(text[len(PREFIX):])
    if text[len(PREFIX) + end:].strip() not in ("", ";"):
        raise ValueError("unexpected content after benchmark JSON")
    if not isinstance(data, dict) or not isinstance(data.get("entries", {}), dict):
        raise ValueError("invalid benchmark history")
    return data.get("entries", {})


def checked_entries(entries, module, absolute):
    if not isinstance(entries, list):
        raise ValueError("invalid publication list")
    out = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("invalid publication")
        date, commit, benches = entry.get("date"), entry.get("commit"), entry.get("benches")
        if not number(date) or date > 253402300799999:
            raise ValueError("invalid publication date")
        if not isinstance(commit, dict) or not isinstance(commit.get("id"), str) or not SHA.fullmatch(commit["id"]):
            raise ValueError("invalid benchmark commit")
        if not isinstance(benches, list):
            raise ValueError("invalid measurements")
        cells = {}
        for bench in benches:
            if not isinstance(bench, dict) or not isinstance(bench.get("name"), str):
                raise ValueError("invalid measurement name")
            parts = bench["name"].split(" / ")
            suffix = " median ms" if absolute else " ratio to plain"
            if (len(parts) != 4 or parts[0] != module or parts[1] not in PROFILES
                    or parts[2] not in CPUS or parts[3] not in ("started" + suffix, "wall" + suffix)):
                raise ValueError("measurement name is not allowlisted")
            if bench.get("unit") != ("ms" if absolute else "ratio") or not number(bench.get("value")):
                raise ValueError("invalid measurement unit or value")
            if not absolute:
                interval = bench.get("range")
                match = INTERVAL.fullmatch(interval) if isinstance(interval, str) and len(interval) <= 80 else None
                if not match or not all(math.isfinite(float(v)) for v in match.groups()):
                    raise ValueError("invalid confidence interval")
            key = (parts[1], parts[2], parts[3].split()[0])
            if key in cells:
                raise ValueError("duplicate measurement")
            cells[key] = bench
        out.append({"date": date, "sha": commit["id"], "cells": cells})
    return out


def latest(entries):
    # The final appended rerun wins when timestamps tie.
    return max(enumerate(entries), key=lambda item: (item[1]["date"], item[0]))[1] if entries else None


def median(cells, key):
    return str(cells[key]["value"]) if key in cells else "n/a"


def ratio(cells, absolute, key):
    if key[0] == "plain":
        reference = key in absolute or any(k[1:] == key[1:] for k in cells)
        return "1 (reference)" if reference else "n/a"
    bench = cells.get(key)
    return f"{bench['value']} {bench['range']}" if bench else "n/a"


def render(entries):
    allowed = {f"spring-boot-benchmark-{module}{suffix}"
               for module in MODULES for suffix in ("", "-absolute")}
    if any(name not in allowed for name in entries):
        raise ValueError("publication group is not allowlisted")
    rows = []
    links = []
    any_results = False
    for module, label in MODULES.items():
        group = f"spring-boot-benchmark-{module}"
        ratios = checked_entries(entries.get(group, []), module, False)
        absolutes = checked_entries(entries.get(group + "-absolute", []), module, True)
        publication = latest(ratios)
        absolute = None
        absolute_only = publication is None
        if publication:
            # Absolute publishing follows ratios. Older same-SHA reruns must not fill missing data.
            matching = [e for e in absolutes if e["sha"] == publication["sha"]
                        and e["date"] >= publication["date"]]
            absolute = min(matching, key=lambda e: e["date"]) if matching else None
        else:
            publication = absolute = latest(absolutes)
        links.append(f'<a href="#{module}">{escape(label)}</a>')
        if not publication or not publication["cells"]:
            rows.append(f'<tr id="{module}"><th scope="row">{escape(label)}</th>'
                        '<td colspan="7">Not yet published</td></tr>')
            continue
        any_results = True
        sha = publication["sha"]
        date = datetime.fromtimestamp(publication["date"] / 1000, timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        stamp = f'{date} <a href="{REPO}/commit/{sha}">{sha[:7]}</a>'
        if absolute_only:
            stamp += " (absolute only)"
        ratio_cells = {} if absolute_only else publication["cells"]
        abs_cells = absolute["cells"] if absolute else {}
        first = True
        for cp, cpu in CPUS.items():
            for profile in PROFILES:
                fields = [profile, cpu,
                          median(abs_cells, (profile, cp, "started")),
                          median(abs_cells, (profile, cp, "wall")),
                          ratio(ratio_cells, abs_cells, (profile, cp, "started")),
                          ratio(ratio_cells, abs_cells, (profile, cp, "wall"))]
                anchor = f' id="{module}"' if first else ""
                first = False
                rows.append(f'<tr{anchor}><th scope="row"><a href="{REPO}/tree/{sha}/{group}/">'
                            f'{escape(label)}</a></th>'
                            + "".join(f"<td>{escape(field)}</td>" for field in fields)
                            + f"<td>{stamp}</td></tr>")
    empty = "" if any_results else "<p>No published results are available yet.</p>"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Spring Boot Benchmark - latest results</title>
<style>
body {{ font: 16px/1.5 system-ui, sans-serif; margin: 2rem auto; padding: 0 1rem; max-width: 95rem; color: #222; background: #fff; }}
a {{ color: #0645ad; }}
nav {{ display: flex; gap: 1rem; flex-wrap: wrap; }}
.results {{ overflow-x: auto; }}
table {{ border-collapse: collapse; width: 100%; font-size: .9rem; }}
th, td {{ padding: .5rem; border: 1px solid #ccc; text-align: left; }}
thead {{ background: #eee; }}
tbody tr:nth-child(even) {{ background: #f7f7f7; }}
td {{ white-space: nowrap; }}
code {{ background: #eee; padding: .15rem; }}
</style>
</head>
<body>
<header><h1>Latest benchmark results</h1>
<p><a href="{REPO}">Repository and methodology</a> |
<a href="data.js" download>Download complete published history (data.js)</a> |
<a href="#rerun">How to rerun</a></p></header>
<main>
<p>Spring Boot startup scenarios, by build profile and CPU limit. Each scenario shows its latest
published full run, not necessarily the current repository version. Follow its commit for the
exact source and dependency versions measured. Dates are publication times in UTC and may differ
between scenarios.</p>
<nav aria-label="Jump to scenario">{' '.join(links)}</nav>
<p><strong>Read ratios first:</strong> below 1 is faster than plain in the same job.
Brackets are the original 95% bootstrap confidence intervals.
Absolute medians are in milliseconds (ms); compare variants within one run, not machines or dates.
Started is Spring's startup log timing; wall is container start to exit, including Docker overhead.
CPU is the Docker CPU quota (p06 = 0.6, p10 = 1.0, p20 = 2.0).</p>
<p><strong>n/a</strong> means not published for this run; absolute publication is best effort.
Older absolute measurements are never filled into newer ratio results.
The full benchmark uses 30 cold starts per profile and CPU limit; this page displays the published
medians and ratios unchanged, without recalculating measurements.</p>
{empty}
<div class="results" role="region" aria-label="Latest benchmark results" tabindex="0">
<table>
<caption>Latest published run per scenario; ratios are to plain within the same job</caption>
<thead><tr><th scope="col">Scenario / framework</th><th scope="col">Build profile</th>
<th scope="col">CPU</th><th scope="col">Started median (ms)</th><th scope="col">Wall median (ms)</th>
<th scope="col">Started ratio (95% CI)</th><th scope="col">Wall ratio (95% CI)</th>
<th scope="col">Published / benchmark commit</th></tr></thead>
<tbody>
{chr(10).join(rows)}
</tbody></table></div>
<section id="rerun"><h2>How to rerun</h2>
<p>With JDK 25 and Docker, run <code>./measure-runtime.sh 5</code> from the repository root
for a quick local comparison (logs go to <code>run-logs/</code>).
See the <a href="{REPO}#build-and-measure-runtimes">build and profile guide</a>
and <a href="{REPO}#running-locally--behind-a-corporate-mirror">corporate mirror configuration</a>.</p>
<p>The benchmark workflow publishes full runs only on pushes to main that match its existing path
filters. Pull requests run smoke benchmarks; manual runs do not publish. To refresh this page
from already-published data, rerun the existing Pages workflow on main; no new benchmark is needed.
See <a href="{REPO}#continuous-benchmarking-github-actions">continuous benchmarking</a>.</p>
</section></main>
</body></html>
"""


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: results_page.py <data.js> <index.html>")
    try:
        page = render(load(Path(sys.argv[1])))
        Path(sys.argv[2]).write_text(page, encoding="utf-8")
    except (ValueError, OSError, RecursionError, OverflowError) as error:
        # Do not echo untrusted content, paths or commit metadata into workflow logs.
        detail = str(error) if isinstance(error, ValueError) and not isinstance(error, json.JSONDecodeError) else "cannot render published history"
        sys.exit(f"results page: {type(error).__name__}: {detail}")
