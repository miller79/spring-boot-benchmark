#!/usr/bin/env python3
"""Tests for verify_published.py. Usage: python3 ci/test_verify_published.py"""
import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verify_published as vp  # noqa: E402

NAME, SHA = "spring-boot-benchmark-tomcat", "a" * 40


def data(entries):
    return vp.PREFIX + json.dumps({"lastUpdate": 1, "repoUrl": "x", "entries": entries}, indent=2)


def entry(sha):
    return {"commit": {"id": sha}, "date": 1, "tool": "customSmallerIsBetter", "benches": []}


class HasEntryTests(unittest.TestCase):
    def test_present(self):
        self.assertTrue(vp.has_entry(data({NAME: [entry("b" * 40), entry(SHA)]}), NAME, SHA))

    def test_other_commit_only(self):
        self.assertFalse(vp.has_entry(data({NAME: [entry("b" * 40)]}), NAME, SHA))

    def test_other_module_group_only(self):
        self.assertFalse(vp.has_entry(data({NAME + "-x": [entry(SHA)]}), NAME, SHA))

    def test_no_entries_or_empty_file(self):
        self.assertFalse(vp.has_entry(data({}), NAME, SHA))
        self.assertFalse(vp.has_entry("", NAME, SHA))

    def test_malformed(self):
        for text in (vp.PREFIX + "{nope", "[]", vp.PREFIX + "[1]", vp.PREFIX + '{"entries": []}',
                     data({NAME: "x"}), data({NAME: [1, {"commit": 1}, {"commit": {}}]})):
            self.assertFalse(vp.has_entry(text, NAME, SHA), text)

    def run_cli(self, stdin, *args):
        return subprocess.run([sys.executable, os.path.join(HERE, "verify_published.py"), *args],
                              input=stdin, capture_output=True, text=True)

    def test_cli_exit_codes(self):
        ok = self.run_cli(data({NAME: [entry(SHA)]}), "--name", NAME, "--sha", SHA)
        self.assertEqual(ok.returncode, 0, ok.stderr)
        missing = self.run_cli(data({NAME: [entry("b" * 40)]}), "--name", NAME, "--sha", SHA)
        self.assertEqual(missing.returncode, 1)
        self.assertIn("no " + NAME, missing.stderr)
        self.assertNotEqual(self.run_cli("", "--name", NAME).returncode, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
