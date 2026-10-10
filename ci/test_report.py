#!/usr/bin/env python3
"""Tests for report.py result validation and series building. Usage: python3 ci/test_report.py"""
import copy
import json
import math
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import report  # noqa: E402


def good(module="tomcat"):
    samples = []
    for profile, base in (("plain", 2.0), ("aot", 1.0)):
        for i in range(6):
            samples.append({"ok": True, "repeat": 1, "cpu_profile": "p06", "iteration": i, "side": "head",
                            "profile": profile, "started_s": base + i / 100, "wall_s": base + 0.5 + i / 100,
                            "nr_periods": 10, "nr_throttled": 1, "mem_peak_bytes": 1000})
    return {"schema": 1, "module": module, "iterations": 6, "repeats": 1, "cpuset": "2,3", "memory": "1g",
            "variants": [{"side": "head", "profile": "plain"}, {"side": "head", "profile": "aot"}],
            "samples": samples}


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, res, name=None, raw=None):
        module = res.get("module", "x") if isinstance(res, dict) else "x"
        sub = os.path.join(self.dir, "artifact")
        os.makedirs(sub, exist_ok=True)
        path = os.path.join(sub, name or ("results-%s.json" % module).replace("/", "_").replace("\n", "_"))
        with open(path, "w") as f:
            f.write(raw if raw is not None else json.dumps(res))
        return path

    def series(self, **kw):
        return json.loads(report.series(self.dir, **kw))

    def rejected(self, res, **kw):
        self.write(res)
        with self.assertRaises(ValueError):
            report.series(self.dir, **kw)

    def mutated(self, fn):
        res = copy.deepcopy(good())
        fn(res)
        return res

    def test_good_result_yields_series(self):
        self.write(good())
        items = self.series()
        self.assertEqual(len(items), 2)  # aot: started + wall
        for it in items:
            self.assertTrue(it["name"].startswith("tomcat / aot / p06 / "))
            self.assertTrue(math.isfinite(it["value"]) and 0 < it["value"] < 100)

    def test_module_filter(self):
        self.write(good("tomcat"))
        self.write(good("original"))
        items = self.series(module="original")
        self.assertEqual(len(items), 2)
        self.assertTrue(all(i["name"].startswith("original") for i in items))

    def test_malicious_module_name(self):
        self.rejected(self.mutated(lambda r: r.update(module="x\n[click](http://evil) @everyone")))

    def test_module_not_allowlisted(self):
        self.rejected(self.mutated(lambda r: r.update(module="evil")))

    def test_malicious_sample_profile(self):
        def f(r):
            for s in r["samples"]:
                if s["profile"] == "aot":
                    s["profile"] = "aot](http://evil)"
        self.rejected(self.mutated(f))

    def test_malicious_variant_profile(self):
        self.rejected(self.mutated(lambda r: r["variants"].append({"side": "head", "profile": "<img src=x>"})))

    def test_malicious_cpu_profile(self):
        def f(r):
            for s in r["samples"]:
                s["cpu_profile"] = "p06 @admin"
        self.rejected(self.mutated(f))

    def test_bad_side(self):
        self.rejected(self.mutated(lambda r: r["samples"][0].update(side="../x")))

    def test_nan_infinity_constants(self):
        for token in ("NaN", "Infinity", "-Infinity"):
            raw = json.dumps(good()).replace('"started_s": 2.0,', f'"started_s": {token},', 1)
            self.assertIn(token, raw)
            self.write(good(), raw=raw)
            with self.assertRaises(ValueError, msg=token):
                report.series(self.dir)

    def test_overflow_to_infinity(self):
        raw = json.dumps(good()).replace('"started_s": 2.0,', '"started_s": 1e999,', 1)
        self.write(good(), raw=raw)
        with self.assertRaises(ValueError):
            report.series(self.dir)

    def test_huge_integer_overflow_fails_closed(self):
        raw = json.dumps(good()).replace('"started_s": 2.0,', '"started_s": 1' + "0" * 400 + ",", 1)
        self.write(good(), raw=raw)
        with self.assertRaises(ValueError):
            report.series(self.dir)
        self.assertEqual(report.load(self.dir, strict=False), [])

    def test_series_requires_matching_file_for_module(self):
        self.write(good("tomcat"))
        with self.assertRaises(ValueError):
            report.series(self.dir, module="original")
        self.assertTrue(json.loads(report.series(self.dir, module="tomcat")))

    def test_non_numeric_bool_and_non_positive_metrics(self):
        for bad in ("fast", True, [1], {"a": 1}, -1, 0):
            self.rejected(self.mutated(lambda r, b=bad: r["samples"][0].update(started_s=b)))

    def test_ratio_out_of_range(self):
        def f(r):
            for s in r["samples"]:
                if s["profile"] == "aot":
                    s["started_s"] = 1e6
        self.rejected(self.mutated(f))

    def test_file_name_must_match_module(self):
        self.write(good("tomcat"), name="results-original.json")
        with self.assertRaises(ValueError):
            report.series(self.dir)

    def test_module_filter_mismatch(self):
        self.write(good("original"), name="results-tomcat.json")
        with self.assertRaises(ValueError):
            report.series(self.dir, module="tomcat")

    def test_module_filter_without_file_fails_closed(self):
        self.write(good("tomcat"))
        with self.assertRaises(ValueError):
            self.series(module="original")

    def test_not_json_and_not_object(self):
        for raw in ("{nope", "[1,2]"):
            self.write({"module": "tomcat"}, raw=raw)
            with self.assertRaises(ValueError, msg=raw):
                report.series(self.dir)

    def test_summary_skips_invalid_but_keeps_valid(self):
        self.write(good("tomcat"))
        bad = good("original")
        bad["samples"][0]["profile"] = "evil"
        self.write(bad)
        out = report.summary(self.dir)
        self.assertIn("## tomcat", out)
        self.assertNotIn("## original", out)

    def test_cli_fails_closed(self):
        bad = good()
        bad["module"] = "evil](x)"
        self.write(bad)
        p = subprocess.run([sys.executable, os.path.join(HERE, "report.py"), "series", self.dir],
                           capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(p.stdout, "")

    def test_cli_good(self):
        self.write(good())
        p = subprocess.run([sys.executable, os.path.join(HERE, "report.py"), "series", self.dir, "--module", "tomcat"],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(len(json.loads(p.stdout)), 2)

    def test_min_samples_is_shared_with_bench(self):
        import bench
        self.assertIs(report.MIN_OK_SAMPLES, bench.MIN_OK_SAMPLES)

    def _drop_ok(self, keep):
        res = good()
        seen = {"aot": 0, "plain": 0}
        for s in res["samples"]:
            seen[s["profile"]] += 1
            if s["profile"] == "aot" and seen["aot"] > keep:
                s["ok"] = False
        return res

    def test_series_needs_exactly_the_shared_minimum(self):
        self.write(self._drop_ok(report.MIN_OK_SAMPLES))
        self.assertEqual(len(self.series()), 2)
        self.write(self._drop_ok(report.MIN_OK_SAMPLES - 1))
        self.assertEqual(self.series(), [])

    def test_require_nonempty_raises_on_empty_series(self):
        self.write(self._drop_ok(report.MIN_OK_SAMPLES - 1))
        with self.assertRaises(ValueError):
            report.series(self.dir, module="tomcat", require_nonempty=True)
        self.write(good())
        self.assertEqual(len(json.loads(report.series(self.dir, module="tomcat", require_nonempty=True))), 2)

    def test_cli_require_nonempty_fails_on_empty_series(self):
        self.write(self._drop_ok(0))
        cmd = [sys.executable, os.path.join(HERE, "report.py"), "series", self.dir, "--module", "tomcat"]
        p = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual((p.returncode, json.loads(p.stdout)), (0, []))
        p = subprocess.run(cmd + ["--require-nonempty"], capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(p.stdout, "")
        self.assertIn("empty ratio series", p.stderr)

    def test_cli_require_nonempty_rejected_for_summary(self):
        p = subprocess.run([sys.executable, os.path.join(HERE, "report.py"), "summary", self.dir, "--require-nonempty"],
                           capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
