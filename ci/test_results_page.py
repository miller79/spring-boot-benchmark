#!/usr/bin/env python3
"""Offline tests of published history -> real staging -> readable HTML.

Fixture: bench-data/data.js at 251390431dff5856ea4540d837372269180ee14c,
captured read-only on 2026-11-25. Only author/commit metadata was removed;
all 540 measurements, publication dates and benchmark SHAs are unchanged.
"""
import copy
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FIXTURE = HERE / "fixtures" / "published-results.json"
FIXTURE_SHA256 = "45646c83773dd88dabb8fab5e2c041074d29cdd978ffe650b971ecbc37a89cdd"


class Table(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.row = None
        self.cell = None
        self.tables = 0
        self.links = []
        self.scripts = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "table":
            self.tables += 1
        elif tag == "tr":
            self.row = []
        elif tag in ("td", "th"):
            self.cell = ""
        elif tag == "a":
            self.links.append(attrs.get("href"))
        elif tag == "script":
            self.scripts += 1

    def handle_data(self, data):
        if self.cell is not None:
            self.cell += data

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.cell is not None:
            self.row.append(self.cell)
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None


def fixture():
    return json.loads(FIXTURE.read_text())


def staged(data, tail=""):
    with tempfile.TemporaryDirectory() as work:
        work = Path(work)
        src, dst = work / "site", work / "_site"
        src.mkdir()
        (src / "index.html").write_text("<html><canvas>legacy chart template</canvas></html>")
        raw = ("window.BENCHMARK_DATA = " + json.dumps(data) + ";" + tail).encode()
        (src / "data.js").write_bytes(raw)
        result = subprocess.run(
            ["bash", str(HERE / "stage-pages.sh"), str(src), str(dst)],
            capture_output=True, text=True, check=False,
        )
        html = (dst / "index.html").read_text() if (dst / "index.html").exists() else ""
        output_data = (dst / "data.js").read_bytes() if (dst / "data.js").exists() else None
        return result, html, output_data, raw, sorted(p.name for p in dst.iterdir())


def table(html):
    parsed = Table()
    parsed.feed(html)
    return parsed


class PublicationTests(unittest.TestCase):
    def test_real_published_staging_path(self):
        self.assertEqual(hashlib.sha256(FIXTURE.read_bytes()).hexdigest(), FIXTURE_SHA256)
        result, html, output_data, raw, files = staged(fixture())
        self.assertEqual(result.returncode, 0, result.stderr)
        parsed = table(html)
        self.assertEqual(parsed.tables, 1, "base chart publish has no readable results table")
        self.assertEqual(len(parsed.rows), 145)  # header + six modules x eight profiles x three CPUs
        self.assertTrue(all(len(row) == 8 for row in parsed.rows))
        original_plain = next(r for r in parsed.rows if r[:3] == ["WebFlux (Netty)", "plain", "0.6"])
        self.assertEqual(original_plain[3:7], ["6401.5", "9832", "1 (reference)", "1 (reference)"])
        original_aot = next(r for r in parsed.rows if r[:3] == ["WebFlux (Netty)", "aot", "0.6"])
        self.assertEqual(original_aot[5:7], ["0.7969 [0.768, 0.824]", "0.8978 [0.837, 0.935]"])
        self.assertIn("2026-10-11", original_aot[7])
        self.assertIn("6694569", original_aot[7])
        self.assertEqual(output_data, raw)
        self.assertEqual(files, ["data.js", "index.html"])
        self.assertEqual(parsed.scripts, 0)
        self.assertIn("data.js", parsed.links)
        self.assertIn("How to rerun", html)
        self.assertIn("./measure-runtime.sh 5", html)
        self.assertIn("manual runs do not publish", html)
        self.assertIn("95% bootstrap", html)
        labels = {
            "original": "WebFlux (Netty)", "tomcat": "Spring MVC (Tomcat)", "data-jpa": "Data JPA",
            "data-rest": "Data REST", "activemq": "ActiveMQ", "all": "All dependencies",
        }
        cpus = {"p06": "0.6", "p10": "1.0", "p20": "2.0"}
        rows = {tuple(row[:3]): row for row in parsed.rows[1:]}
        checked = 0
        for group, entries in fixture()["entries"].items():
            absolute = group.endswith("-absolute")
            for bench in entries[0]["benches"]:
                module, profile, cp, metric = bench["name"].split(" / ")
                row = rows[(labels[module], profile, cpus[cp])]
                column = (3 if absolute else 5) + (1 if metric.startswith("wall") else 0)
                expected = str(bench["value"])
                if not absolute:
                    expected += " " + bench["range"]
                self.assertEqual(row[column], expected, bench["name"])
                checked += 1
        self.assertEqual(checked, 540)

    def test_readme_discovery(self):
        readme = (ROOT / "README.md").read_text()
        self.assertIn("https://miller79.github.io/spring-boot-benchmark/", readme.splitlines()[2])
        self.assertIn("Latest benchmark results", readme.splitlines()[2])
        self.assertNotIn("Not there yet", readme)
        for module in ("original", "tomcat", "data-jpa", "data-rest", "activemq", "all"):
            self.assertIn(f"](spring-boot-benchmark-{module}/)", readme)
        self.assertNotIn("Charts of the published history:", readme)


class LatestPublicationTests(unittest.TestCase):
    def test_latest_per_module_not_array_order_or_global_commit(self):
        data = fixture()
        key = "spring-boot-benchmark-original"
        newer = copy.deepcopy(data["entries"][key][0])
        newer["date"] += 86400000
        newer["commit"]["id"] = "a" * 40
        newer["benches"][0]["value"] = 0.1234
        data["entries"][key].insert(0, newer)
        result, html, *_ = staged(data)
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = table(html).rows
        original = next(r for r in rows if r[:3] == ["WebFlux (Netty)", "aot", "0.6"])
        self.assertEqual(original[3:5], ["n/a", "n/a"])  # absolute publication is still old
        self.assertTrue(original[5].startswith("0.1234 "))
        self.assertIn("2026-10-12", original[7])
        tomcat = next(r for r in rows if r[:3] == ["Spring MVC (Tomcat)", "plain", "0.6"])
        self.assertEqual(tomcat[3], "9903.5")
        self.assertIn("2026-10-11", tomcat[7])

    def test_same_commit_rerun_does_not_reuse_old_absolutes(self):
        data = fixture()
        key = "spring-boot-benchmark-original"
        newer = copy.deepcopy(data["entries"][key][0])
        newer["date"] += 86400000
        data["entries"][key].append(newer)
        result, html, *_ = staged(data)
        self.assertEqual(result.returncode, 0, result.stderr)
        row = next(r for r in table(html).rows if r[:3] == ["WebFlux (Netty)", "aot", "0.6"])
        self.assertEqual(row[3:5], ["n/a", "n/a"])

    def test_empty_and_absolute_only_are_explicit(self):
        for data, expected in (
            ({"entries": {}}, "No published results"),
            ({"entries": {"spring-boot-benchmark-original-absolute":
                          fixture()["entries"]["spring-boot-benchmark-original-absolute"]}},
             "absolute only"),
        ):
            with self.subTest(expected=expected):
                result, html, *_ = staged(data)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(expected, html)
                self.assertIn("Not yet published", html)

    def test_equal_date_last_rerun_wins_and_missing_cells_stay_missing(self):
        data = fixture()
        key = "spring-boot-benchmark-original"
        newer = copy.deepcopy(data["entries"][key][0])
        newer["benches"] = newer["benches"][:1]
        newer["benches"][0]["value"] = 0.4321
        data["entries"][key].append(newer)
        result, html, *_ = staged(data)
        self.assertEqual(result.returncode, 0, result.stderr)
        row = next(r for r in table(html).rows if r[:3] == ["WebFlux (Netty)", "aot", "0.6"])
        self.assertTrue(row[5].startswith("0.4321 "))
        self.assertEqual(row[6], "n/a")


class ControlTests(unittest.TestCase):
    def test_ignore_unneeded_metadata_and_never_execute_javascript(self):
        data = fixture()
        entry = data["entries"]["spring-boot-benchmark-original"][0]
        entry["commit"]["message"] = "<script>do-not-render</script>"
        entry["commit"]["url"] = "javascript:do-not-render"
        entry["commit"]["author"] = {"email": "do-not-render"}
        entry["benches"][0]["extra"] = "<img src=x onerror=do-not-render>"
        result, html, *_ = staged(data)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("do-not-render", html)
        result, _, *_ = staged(data, "throw new Error('do-not-execute')")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ValueError", result.stderr)
        self.assertNotIn("do-not-execute", result.stderr)

    def test_malformed_display_fields_fail_without_echoing_payload(self):
        for field, value in (("name", "<script>bad-payload</script>"),
                             ("value", float("nan")), ("value", True),
                             ("range", "<img src=bad-payload>"), ("unit", "bad-payload")):
            with self.subTest(field=field, value=value):
                data = fixture()
                data["entries"]["spring-boot-benchmark-original"][0]["benches"][0][field] = value
                result, _, *_ = staged(data)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("ValueError", result.stderr)
                self.assertNotIn("bad-payload", result.stderr)
        data = fixture()
        data["entries"]["spring-boot-benchmark-original"][0]["commit"]["id"] = "javascript:bad-payload"
        result, _, *_ = staged(data)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("bad-payload", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
