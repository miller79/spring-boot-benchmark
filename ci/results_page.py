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


def median(cells, key):
    return str(cells[key]["value"]) if key in cells else "n/a"


def ratio(cells, absolute, key):
    if key[0] == "plain":
        reference = key in absolute or any(k[1:] == key[1:] for k in cells)
        return "1 (reference)" if reference else "n/a"
    bench = cells.get(key)
    return f"{bench['value']} {bench['range']}" if bench else "n/a"


def matrix(module, label, metric, ratio_cells, abs_cells, published=True):
    title = "Started median (ms)" if metric == "started" else "Wall median (ms)"
    headers = "".join(f'<th scope="col">{cp} / {cpu} CPU</th>' for cp, cpu in CPUS.items())
    rows = []
    if published:
        for profile in PROFILES:
            cells = []
            for cp in CPUS:
                key = (profile, cp, metric)
                value = median(abs_cells, key)
                time = f"{value} ms" if key in abs_cells else value
                comparison = ratio(ratio_cells, abs_cells, key)
                cells.append(f"<td><strong>{escape(time)}</strong> "
                             f"<small>Ratio: {escape(comparison)}</small></td>")
            rows.append(f'<tr><th scope="row">{escape(profile)}</th>{"".join(cells)}</tr>')
    else:
        rows.append('<tr><td colspan="4">Not yet published</td></tr>')
    return f"""<div class="results" role="region" aria-labelledby="{module}-{metric}" tabindex="0">
<table>
<caption id="{module}-{metric}">{escape(label)} - {title}</caption>
<thead><tr><th scope="col">Build profile</th>{headers}</tr></thead>
<tbody>{chr(10).join(rows)}</tbody>
</table></div>"""


def paired_absolute(ratios, absolutes, index):
    publication = ratios[index]
    # A later same-SHA rerun bounds this publication, including timestamp ties.
    later = [entry["date"] for i, entry in enumerate(ratios)
             if entry["sha"] == publication["sha"]
             and (entry["date"], i) > (publication["date"], index)]
    end = min(later) if later else math.inf
    matching = [entry for entry in absolutes if entry["sha"] == publication["sha"]
                and publication["date"] <= entry["date"] < end]
    return min(matching, key=lambda entry: entry["date"]) if matching else None


def publication_date(publication):
    return datetime.fromtimestamp(publication["date"] / 1000, timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def publication_matrices(anchor, label, publication, absolute, absolute_only):
    sha = publication["sha"]
    stamp = f'{publication_date(publication)} <a href="{REPO}/commit/{sha}">{sha[:7]}</a>'
    if absolute_only:
        stamp += " (absolute only)"
    ratio_cells = {} if absolute_only else publication["cells"]
    abs_cells = absolute["cells"] if absolute else {}
    return (f'<p class="publication" data-run="{anchor}">Published: {stamp}</p>'
            + matrix(anchor, label, "started", ratio_cells, abs_cells)
            + '<details><summary>Wall time and ratios (includes Docker overhead)</summary>'
            + matrix(anchor, label, "wall", ratio_cells, abs_cells)
            + '</details>')


def render(entries):
    allowed = {f"spring-boot-benchmark-{module}{suffix}"
               for module in MODULES for suffix in ("", "-absolute")}
    if any(name not in allowed for name in entries):
        raise ValueError("publication group is not allowlisted")
    sections = []
    links = []
    any_results = False
    for module, label in MODULES.items():
        group = f"spring-boot-benchmark-{module}"
        ratios = checked_entries(entries.get(group, []), module, False)
        absolutes = checked_entries(entries.get(group + "-absolute", []), module, True)
        absolute_only = not ratios
        runs = sorted(enumerate(ratios or absolutes),
                      key=lambda item: (item[1]["date"], item[0]), reverse=True)
        publication = runs[0][1] if runs else None
        links.append(f'<a href="#{module}">{escape(label)}</a>')
        if not publication or not publication["cells"]:
            sections.append(f'<section id="{module}"><h2>{escape(label)}</h2>'
                            + matrix(module, label, "started", {}, {}, published=False)
                            + '</section>')
            continue
        any_results = True
        sha = publication["sha"]
        run_links, run_sections = [], []
        for position, (index, run) in enumerate(runs):
            anchor = f"{module}-run-{index}"
            title = f'{publication_date(run)} / {run["sha"][:7]} / publication {index + 1}'
            suffix = " (latest)" if position == 0 else ""
            run_links.append(f'<a href="#{anchor}">{escape(title + suffix)}</a>')
            absolute = run if absolute_only else paired_absolute(ratios, absolutes, index)
            content = publication_matrices(module if position == 0 else anchor,
                                           label, run, absolute, absolute_only)
            if position == 0:
                run_sections.append(f'<div id="{anchor}">{content}</div>')
            else:
                run_sections.append(f'<details id="{anchor}" class="history"><summary>'
                                    f'{escape(title)}</summary>{content}</details>')
        history_note = ("No earlier published run for this scenario." if len(runs) == 1
                        else "Follow a dated run link, then expand its older matrices.")
        sections.append(f'<section id="{module}"><h2><a href="{REPO}/tree/{sha}/{group}/">'
                        f'{escape(label)}</a></h2><p>Published runs (newest first):</p>'
                        f'<nav aria-label="Published runs for {escape(label)}">'
                        + " | ".join(run_links) + f'</nav><p>{history_note}</p>'
                        + "".join(run_sections) + '</section>')
    empty = "" if any_results else "<p>No published results are available yet.</p>"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Spring Boot Benchmark - startup time by setting</title>
<style>
:root {{ color-scheme: light dark; --background: #f9f9f9; --surface: #fff; --subtle: #efefef; --text: #333; --secondary: #5c5c5c; --border: #c9c9c9; --link: #005f8d; }}
body {{ font: .875rem/1.5 'proxima-nova', Helvetica, Arial, ui-sans-serif, system-ui, sans-serif; margin: 2rem auto; padding: 0 1rem; max-width: 75rem; color: var(--text); background: var(--background); }}
h1, h2 {{ font-weight: 600; line-height: 1.25; }}
h1 {{ font-size: 1.5rem; }} h2 {{ font-size: 1.25rem; }}
a {{ color: var(--link); }}
:focus-visible {{ outline: 2px solid var(--link); outline-offset: 2px; }}
nav {{ display: flex; gap: 1rem; flex-wrap: wrap; }}
section {{ margin-top: 2rem; }}
.publication, small {{ color: var(--secondary); }}
.results {{ overflow-x: auto; margin: 1rem 0; }}
table {{ border-collapse: collapse; width: 100%; background: var(--surface); }}
caption {{ text-align: left; font-weight: 600; padding-bottom: .5rem; }}
th, td {{ padding: .5rem 1rem; border: 1px solid var(--border); text-align: left; white-space: nowrap; }}
thead, tbody tr:nth-child(even) {{ background: var(--subtle); }}
tbody th {{ position: sticky; left: 0; background: var(--surface); }}
tbody tr:nth-child(even) th {{ background: var(--subtle); }}
strong {{ font-size: 1rem; }}
td small {{ display: block; font-size: .75rem; }}
summary {{ cursor: pointer; color: var(--link); }}
.history {{ margin-top: 1rem; }}
dt {{ font-weight: 600; }} dd {{ margin: 0 0 .5rem; }}
code {{ background: var(--subtle); padding: .125rem; }}
@media (prefers-color-scheme: dark) {{
  :root {{ --background: #131313; --surface: #252525; --subtle: #333; --text: #fff; --secondary: #c9c9c9; --border: #939393; --link: #bfeafe; }}
}}
</style>
</head>
<body>
<a href="#results">Skip to startup matrices</a>
<header><h1>Startup time by setting</h1>
<p><a href="{REPO}">Repository and methodology</a> |
<a href="data.js" download>Download complete published history (data.js)</a> |
<a href="#profiles">Build profile guide</a> |
<a href="#rerun">How to rerun</a></p></header>
<main id="results">
<p>Spring Boot startup scenarios, by build profile and CPU limit. Each scenario shows its latest
published full run, not necessarily the current repository version. Follow its commit for the
exact source and dependency versions measured. Dates are publication times in UTC and may differ
between scenarios.</p>
<nav aria-label="Jump to scenario">{' '.join(links)}</nav>
<p>Rows are build profiles; columns are Docker CPU settings. <strong>Each bold time is the
started median in milliseconds (ms)</strong>, from Spring's startup log.
The smaller ratio compares that profile to plain in the same job; below 1 is faster.
Brackets are the original 95% bootstrap confidence intervals for the ratio, not the time.
Compare profiles within one scenario/run, not machines or dates.</p>
<p><strong>n/a</strong> means not published for this run; absolute publication is best effort.
Older absolute measurements are never filled into newer ratio results.
The full benchmark uses 30 cold starts per profile and CPU limit; this page displays the published
medians and ratios unchanged, without recalculating measurements.</p>
<p>Browse each scenario's published runs by date and benchmark commit below.
Smoke and manual Actions runs are not in published history; these records do not contain Actions run IDs.
The latest matrices stay visible; older published runs expand without JavaScript.</p>
{empty}
{chr(10).join(sections)}
<section id="profiles"><h2>Build profile guide</h2>
<dl>
<dt>plain</dt><dd>No build customization; ratio reference.</dd>
<dt>aot</dt><dd>Spring AOT.</dd>
<dt>cds</dt><dd>Class Data Sharing (CDS).</dd>
<dt>aot-cds</dt><dd>Spring AOT and CDS.</dd>
<dt>aot-caching</dt><dd>JVM AOT caching.</dd>
<dt>aot-aot-caching</dt><dd>Spring AOT and JVM AOT caching.</dd>
<dt>alpaquita</dt><dd>Alpaquita musl builder.</dd>
<dt>native</dt><dd>Native executable.</dd>
</dl>
<p>CPU headers show published setting IDs and Docker quotas, not JVM versions.
Follow each scenario's benchmark commit for the exact build/JVM configuration.
Expand its wall-time matrix for container start-to-exit medians, including Docker overhead.
No confidence interval for absolute medians is published; all displayed intervals belong to ratios.</p>
</section>
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
