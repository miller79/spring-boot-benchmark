#!/usr/bin/env python3
"""Text-level guard rails for the workflows (stdlib only, no YAML parser): the publish-error gate, the
alert step and the permission scopes must not regress unnoticed. Usage: python3 ci/test_workflows.py"""
import os
import re
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def read(name):
    with open(os.path.join(ROOT, ".github", "workflows", name)) as f:
        return f.read()


def job(text, name):
    """Body of the top-level job `name` (2-space indented key under jobs:)."""
    m = re.search(r"^  %s:\n(.*?)(?=^  [A-Za-z0-9_-]+:\n|\Z)" % re.escape(name), text, re.S | re.M)
    assert m, f"job {name} not found"
    return m.group(1)


def steps(body):
    parts = re.split(r"^      - ", body, flags=re.M)[1:]
    return {re.match(r"name: (.*)", p).group(1): p for p in parts if p.startswith("name: ")}


def step(body, prefix):
    found = [v for k, v in steps(body).items() if k.startswith(prefix)]
    assert len(found) == 1, f"step {prefix!r}: {len(found)} found"
    return found[0]


class BenchmarkWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.text = read("benchmark.yml")
        self.publish = job(self.text, "publish")

    def test_publish_guard_keeps_its_clauses(self):
        guard = self.publish.split("if: >-", 1)[1].split("name:", 1)[0]
        for clause in ("github.event_name == 'push'", "github.ref == format('refs/heads/{0}', github.event.repository.default_branch)",
                       "needs.plan.outputs.mode == 'full'"):
            self.assertIn(clause, guard)

    def test_only_publish_can_write(self):
        self.assertRegex(self.text, r"(?m)^permissions:\n  contents: read\n")
        for name in ("plan", "bench"):
            self.assertNotRegex(job(self.text, name), r"(?m)^\s+(contents: write|issues: write|pages:|id-token:)")
        self.assertIn("contents: write", self.publish)
        self.assertIn("issues: write", self.publish)
        self.assertNotRegex(self.text, r"(?m)^\s+(pages|id-token):")

    def test_landed_gate_is_unconditional_and_runs_the_script(self):
        s = step(self.publish, "Verify the history push landed")
        self.assertIn("run: bash ci/landed.sh", s)
        self.assertIn("if: steps.series.outputs.has_series == 'true'", s)
        self.assertNotIn("always()", s)
        self.assertNotIn("continue-on-error", s)
        for var in ("BEFORE_SHA: ${{ steps.before.outputs.sha }}", "DATA_FILE:", "BENCH_NAME:"):
            self.assertIn(var, s)

    def test_landed_runs_after_the_publish_action_and_before_the_alert(self):
        names = list(steps(self.publish))
        i_bench = names.index(next(n for n in names if n.startswith("Publish history")))
        i_landed = names.index(next(n for n in names if n.startswith("Verify the history push")))
        i_alert = names.index(next(n for n in names if n.startswith("Open or update the alert issue")))
        self.assertLess(i_bench, i_landed)
        self.assertLess(i_landed, i_alert)

    def test_publish_action_may_fail_but_alerts_on_regression(self):
        s = step(self.publish, "Publish history")
        self.assertIn("continue-on-error: true", s)
        self.assertIn("fail-on-alert: true", s)

    def test_alert_step_gates_on_the_action_outcome_only(self):
        s = step(self.publish, "Open or update the alert issue")
        self.assertIn("if: steps.bench.outcome == 'failure'", s)  # no always(): skipped when `landed` failed
        self.assertNotIn("always()", s)
        self.assertNotIn("continue-on-error", s)
        self.assertRegex(s, r"for attempt in 1 2 3")

    def test_series_step_is_strict(self):
        self.assertIn("--require-nonempty", step(self.publish, "Build ratio series"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
