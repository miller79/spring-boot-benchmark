#!/usr/bin/env python3
"""Text-level guard rails for the workflows (stdlib only, no YAML parser): the publish-error gate, the
alert step and the permission scopes must not regress unnoticed. Usage: python3 ci/test_workflows.py"""
import os
import re
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PUBLISH_GUARD = ("!cancelled() && github.event_name == 'push' && "
                 "github.ref == format('refs/heads/{0}', github.event.repository.default_branch) && "
                 "needs.plan.outputs.mode == 'full' && needs.bench.result != 'skipped'")


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


def guard(body):
    m = re.search(r"^    if: >-\n(.*?)(?=^    [a-z-]+:)", body, re.S | re.M)
    return " ".join(m.group(1).split()) if m else ""


def check_publish_guard(publish):
    """Exact (whitespace-normalised) guard: an && flipped to || or a dropped clause is caught."""
    return [] if guard(publish) == PUBLISH_GUARD else [f"publish guard changed: {guard(publish)!r}"]


def check_data_file(text):
    """`landed` reads DATA_FILE; it must be where the action writes: <benchmark-data-dir-path>/data.js."""
    publish = job(text, "publish")
    action = step(publish, "Publish history")
    m = re.search(r"benchmark-data-dir-path: '([^']*)'", action)
    want = "data.js" if m and m.group(1) == "." else f"{m.group(1) if m else 'dev/bench'}/data.js"
    got = re.search(r"DATA_FILE: (\S+)", step(publish, "Verify the history push landed"))
    return [] if got and got.group(1) == want else [f"landed DATA_FILE {got and got.group(1)!r} != {want!r}"]


def check_pinned(name, text):
    return [f"{name}: unpinned action {m}" for m in re.findall(r"(?m)^\s*(?:- )?uses: (\S+)", text)
            if not re.fullmatch(r"[\w.-]+/[\w./-]+@[0-9a-f]{40}", m)]


class BenchmarkWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.text = read("benchmark.yml")
        self.publish = job(self.text, "publish")

    def test_publish_guard_is_exact_and_flips_are_caught(self):
        self.assertEqual(check_publish_guard(self.publish), [])
        for old, new in (("github.event_name == 'push' &&", "github.event_name == 'push' ||"),
                         ("needs.plan.outputs.mode == 'full' &&", "needs.plan.outputs.mode == 'full' ||"),
                         ("!cancelled() &&", "!cancelled() ||"),
                         ("needs.bench.result != 'skipped'", "true")):
            with self.subTest(old=old):
                self.assertIn(old, self.publish)
                self.assertNotEqual(check_publish_guard(self.publish.replace(old, new, 1)), [])

    def test_landed_reads_the_file_the_action_writes(self):
        self.assertEqual(check_data_file(self.text), [])
        self.assertNotEqual(check_data_file(self.text.replace("DATA_FILE: dev/bench/data.js", "DATA_FILE: data.js")), [])
        with_dir = self.text.replace("          gh-pages-branch: bench-data\n", "          gh-pages-branch: bench-data\n          benchmark-data-dir-path: '.'\n", 1)
        self.assertNotEqual(check_data_file(with_dir), [])  # dir changed, DATA_FILE not
        self.assertEqual(check_data_file(with_dir.replace("DATA_FILE: dev/bench/data.js", "DATA_FILE: data.js")), [])

    def test_all_actions_are_pinned_to_a_full_sha(self):
        names = sorted(n for n in os.listdir(os.path.join(ROOT, ".github", "workflows")) if n.endswith(".yml"))
        self.assertIn("benchmark.yml", names)
        for n in names:
            self.assertEqual(check_pinned(n, read(n)), [])
        self.assertNotEqual(check_pinned("x", "      - uses: actions/checkout@v4\n"), [])
        self.assertNotEqual(check_pinned("x", "        uses: a/b@3d3c42e\n"), [])

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
