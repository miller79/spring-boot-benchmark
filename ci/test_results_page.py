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
        self.module = None
        self.details_depth = 0
        self.matrices = {}
        self.matrix_disclosed = {}
        self.matrix_rows = None
        self.stamps = {}
        self.stamp = None
        self.stamp_key = None
        self.ids = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "section":
            self.module = attrs.get("id")
        elif tag == "details":
            self.details_depth += 1
        elif tag == "p" and attrs.get("class") == "publication":
            self.stamp = ""
            self.stamp_key = attrs.get("data-run", self.module)
        elif tag == "table":
            self.tables += 1
            self.matrix_rows = []
        elif tag == "caption":
            anchor, metric = attrs["id"].rsplit("-", 1)
            self.matrices[(anchor, metric)] = self.matrix_rows
            self.matrix_disclosed[(anchor, metric)] = self.details_depth > 0
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
        if self.stamp is not None:
            self.stamp += data

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.cell is not None:
            self.row.append(self.cell)
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.matrix_rows.append(self.row)
            self.row = None
        elif tag == "table":
            self.matrix_rows = None
        elif tag == "p" and self.stamp is not None:
            self.stamps[self.stamp_key] = self.stamp
            self.stamp = None
        elif tag == "details":
            self.details_depth -= 1
        elif tag == "section":
            self.module = None


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


def matrix_cell(parsed, module, profile, cpu, metric="started"):
    rows = parsed.matrices[(module, metric)]
    column = rows[0].index(f"{cpu} CPU")
    row = next(row for row in rows[1:] if row[0] == profile)
    median, ratio = row[column].split(" Ratio: ")
    return [median.removesuffix(" ms"), ratio]


class PublicationTests(unittest.TestCase):
    def test_real_published_staging_path(self):
        self.assertEqual(hashlib.sha256(FIXTURE.read_bytes()).hexdigest(), FIXTURE_SHA256)
        result, html, output_data, raw, files = staged(fixture())
        self.assertEqual(result.returncode, 0, result.stderr)
        parsed = table(html)
        self.assertEqual(parsed.tables, 12, "expected six startup matrices and six disclosed wall matrices")
        modules = ("original", "tomcat", "data-jpa", "data-rest", "activemq", "all")
        profiles = ["plain", "aot", "cds", "aot-cds", "aot-caching",
                    "aot-aot-caching", "alpaquita", "native"]
        for module in modules:
            for metric in ("started", "wall"):
                rows = parsed.matrices[(module, metric)]
                self.assertEqual(rows[0], ["Build profile", "p06 / 0.6 CPU", "p10 / 1.0 CPU", "p20 / 2.0 CPU"])
                self.assertEqual([row[0] for row in rows[1:]], profiles)
                self.assertTrue(all(len(row) == 4 for row in rows))
                self.assertTrue(all(" ms Ratio: " in cell for row in rows[1:] for cell in row[1:]))
                self.assertEqual(parsed.matrix_disclosed[(module, metric)], metric == "wall")
            self.assertIn("2026-10-11", parsed.stamps[module])
            self.assertIn("6694569", parsed.stamps[module])
        self.assertEqual(matrix_cell(parsed, "original", "plain", "p06 / 0.6"),
                         ["6401.5", "1 (reference)"])
        self.assertEqual(matrix_cell(parsed, "original", "plain", "p06 / 0.6", "wall"),
                         ["9832", "1 (reference)"])
        self.assertEqual(matrix_cell(parsed, "original", "aot", "p06 / 0.6"),
                         ["5101.5", "0.7969 [0.768, 0.824]"])
        self.assertEqual(matrix_cell(parsed, "original", "aot", "p06 / 0.6", "wall"),
                         ["8827.1", "0.8978 [0.837, 0.935]"])
        self.assertEqual(output_data, raw)
        self.assertEqual(files, ["data.js", "index.html"])
        self.assertEqual(parsed.scripts, 0)
        self.assertIn("data.js", parsed.links)
        self.assertIn("How to rerun", html)
        self.assertIn("./measure-runtime.sh 5", html)
        self.assertIn("manual runs do not publish", html)
        self.assertIn("95% bootstrap", html)
        cpus = {"p06": "p06 / 0.6", "p10": "p10 / 1.0", "p20": "p20 / 2.0"}
        checked = 0
        for group, entries in fixture()["entries"].items():
            absolute = group.endswith("-absolute")
            for bench in entries[0]["benches"]:
                module, profile, cp, metric = bench["name"].split(" / ")
                cell = matrix_cell(parsed, module, profile, cpus[cp], metric.split()[0])
                expected = str(bench["value"])
                if not absolute:
                    expected += " " + bench["range"]
                self.assertEqual(cell[0 if absolute else 1], expected, bench["name"])
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
        parsed = table(html)
        original = matrix_cell(parsed, "original", "aot", "p06 / 0.6")
        self.assertEqual(original[0], "n/a")  # absolute publication is still old
        self.assertEqual(matrix_cell(parsed, "original", "aot", "p06 / 0.6", "wall")[0], "n/a")
        self.assertTrue(original[1].startswith("0.1234 "))
        self.assertIn("2026-10-12", parsed.stamps["original"])
        self.assertEqual(matrix_cell(parsed, "tomcat", "plain", "p06 / 0.6")[0], "9903.5")
        self.assertIn("2026-10-11", parsed.stamps["tomcat"])

    def test_same_commit_rerun_does_not_reuse_old_absolutes(self):
        data = fixture()
        key = "spring-boot-benchmark-original"
        newer = copy.deepcopy(data["entries"][key][0])
        newer["date"] += 86400000
        data["entries"][key].append(newer)
        result, html, *_ = staged(data)
        self.assertEqual(result.returncode, 0, result.stderr)
        parsed = table(html)
        for metric in ("started", "wall"):
            self.assertEqual(matrix_cell(parsed, "original", "aot", "p06 / 0.6", metric)[0], "n/a")

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
                if expected == "absolute only":
                    parsed = table(html)
                    self.assertEqual(matrix_cell(parsed, "original", "aot", "p06 / 0.6"),
                                     ["5101.5", "n/a"])
                    self.assertEqual(matrix_cell(parsed, "original", "plain", "p06 / 0.6"),
                                     ["6401.5", "1 (reference)"])

    def test_equal_date_last_rerun_wins_and_missing_cells_stay_missing(self):
        data = fixture()
        key = "spring-boot-benchmark-original"
        newer = copy.deepcopy(data["entries"][key][0])
        newer["benches"] = newer["benches"][:1]
        newer["benches"][0]["value"] = 0.4321
        data["entries"][key].append(newer)
        result, html, *_ = staged(data)
        self.assertEqual(result.returncode, 0, result.stderr)
        parsed = table(html)
        self.assertTrue(matrix_cell(parsed, "original", "aot", "p06 / 0.6")[1].startswith("0.4321 "))
        self.assertEqual(matrix_cell(parsed, "original", "aot", "p06 / 0.6", "wall")[1], "n/a")


class HistoryTests(unittest.TestCase):
    def test_real_single_run_index_is_honest(self):
        result, html, output_data, raw, files = staged(fixture())
        self.assertEqual(result.returncode, 0, result.stderr)
        parsed = table(html)
        for module in ("original", "tomcat", "data-jpa", "data-rest", "activemq", "all"):
            self.assertIn(f"#{module}-run-0", parsed.links)
        self.assertEqual(html.count("No earlier published run"), 6)
        self.assertIn("Smoke and manual Actions runs are not in published history", html)
        self.assertEqual(len(parsed.ids), len(set(parsed.ids)))
        self.assertEqual(output_data, raw)
        self.assertEqual(files, ["data.js", "index.html"])
        self.assertEqual(parsed.scripts, 0)

    def test_specific_older_run_is_linked_and_keeps_its_values(self):
        data = fixture()
        group = "spring-boot-benchmark-original"
        newer = copy.deepcopy(data["entries"][group][0])
        newer["date"] += 86400000
        newer["commit"]["id"] = "a" * 40
        newer["benches"][0]["value"] = 0.1234
        newer_absolute = copy.deepcopy(data["entries"][group + "-absolute"][0])
        newer_absolute["date"] += 86400000
        newer_absolute["commit"]["id"] = "a" * 40
        newer_absolute["benches"][2]["value"] = 2500
        data["entries"][group].append(newer)
        data["entries"][group + "-absolute"].append(newer_absolute)
        result, html, *_ = staged(data)
        self.assertEqual(result.returncode, 0, result.stderr)
        parsed = table(html)
        links = [link for link in parsed.links if link.startswith("#original-run-")]
        self.assertEqual(links, ["#original-run-1", "#original-run-0"])
        self.assertEqual(matrix_cell(parsed, "original", "aot", "p06 / 0.6"),
                         ["2500", "0.1234 [0.768, 0.824]"])
        self.assertEqual(matrix_cell(parsed, "original-run-0", "aot", "p06 / 0.6"),
                         ["5101.5", "0.7969 [0.768, 0.824]"])
        self.assertIn("2026-10-12", parsed.stamps["original"])
        self.assertIn("2026-10-11", parsed.stamps["original-run-0"])
        self.assertTrue(parsed.matrix_disclosed[("original-run-0", "started")])
        self.assertFalse(parsed.matrix_disclosed[("original", "started")])
        self.assertEqual(len(parsed.ids), len(set(parsed.ids)))

    def test_older_same_sha_run_cannot_borrow_later_absolute_publication(self):
        for offset in (86400000, 0):
            with self.subTest(offset=offset):
                data = fixture()
                group = "spring-boot-benchmark-original"
                newer = copy.deepcopy(data["entries"][group][0])
                newer["date"] += offset
                data["entries"][group].append(newer)
                absolute = copy.deepcopy(data["entries"][group + "-absolute"][0])
                absolute["date"] += offset
                absolute["benches"][2]["value"] = 1111
                data["entries"][group + "-absolute"] = [absolute]
                result, html, *_ = staged(data)
                self.assertEqual(result.returncode, 0, result.stderr)
                parsed = table(html)
                self.assertEqual(matrix_cell(parsed, "original", "aot", "p06 / 0.6")[0], "1111")
                for metric in ("started", "wall"):
                    self.assertEqual(matrix_cell(parsed, "original-run-0", "aot", "p06 / 0.6", metric)[0],
                                     "n/a")


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

    def test_ci_runner_includes_new_tests_without_permission_changes(self):
        current = (ROOT / ".github/workflows/ci-tests.yml").read_text()
        self.assertIn("ci/test_results_page.py", current)
        self.assertNotIn("secrets.", current)
        self.assertNotIn(": write", current)


if __name__ == "__main__":
    unittest.main(verbosity=2)
