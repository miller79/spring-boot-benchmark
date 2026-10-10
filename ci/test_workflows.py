#!/usr/bin/env python3
"""Guard rails for the workflows (stdlib only, no YAML parser): the publish-error gate, the alert
step, the guards and the permission scopes must not regress unnoticed. Each check is a function over
the workflow text, so the tests can run it on the real file (no problems) and on deliberately broken
copies (a problem must be reported: the negative tests). Usage: python3 ci/test_workflows.py"""
import os
import re
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DEFAULT_REF = "github.ref == format('refs/heads/{0}', github.event.repository.default_branch)"


def read(name):
    with open(os.path.join(ROOT, ".github", "workflows", name)) as f:
        return f.read()


def job(text, name):
    """Body of the top-level job `name` (2-space indented key under jobs:), or '' if absent."""
    m = re.search(r"^  %s:\n(.*?)(?=^  [A-Za-z0-9_-]+:\n|\Z)" % re.escape(name), text, re.S | re.M)
    return m.group(1) if m else ""


def steps(body):
    parts = re.split(r"^      - ", body, flags=re.M)[1:]
    return {re.match(r"name: (.*)", p).group(1): p for p in parts if p.startswith("name: ")}


def step(body, prefix):
    found = [v for k, v in steps(body).items() if k.startswith(prefix)]
    return found[0] if len(found) == 1 else ""


def guard(body):
    m = re.search(r"^    if: >-\n(.*?)(?=^    [a-z-]+:)", body, re.S | re.M)
    return m.group(1) if m else ""


def check_benchmark(text):
    problems = []
    publish = job(text, "publish")
    g = guard(publish)
    for clause in ("github.event_name == 'push'", DEFAULT_REF, "needs.plan.outputs.mode == 'full'"):
        if clause not in g:
            problems.append(f"publish guard lost: {clause}")
    if not re.search(r"(?m)^permissions:\n  contents: read\n", text):
        problems.append("workflow-level permissions must be contents: read")
    for name in ("plan", "bench"):
        if re.search(r"(?m)^\s+(contents: write|issues: write|pages:|id-token:)", job(text, name)):
            problems.append(f"job {name} must not have write scopes")
    if "contents: write" not in publish or "issues: write" not in publish:
        problems.append("publish needs contents: write and issues: write")
    if re.search(r"(?m)^\s+(pages|id-token):", text):
        problems.append("benchmark.yml must not hold pages/id-token scopes (the Pages deploy lives in pages.yml)")
    if job(text, "deploy-pages"):
        problems.append("deploy-pages must not be a job of benchmark.yml")

    landed = step(publish, "Verify the history push landed")
    for needle, why in (("run: bash ci/landed.sh", "landed must run ci/landed.sh"),
                        ("if: steps.series.outputs.has_series == 'true'", "landed must run whenever a series was published"),
                        ("BEFORE_SHA: ${{ steps.before.outputs.sha }}", "landed needs the head from before the publish"),
                        ("DATA_FILE:", "landed needs DATA_FILE"), ("BENCH_NAME:", "landed needs BENCH_NAME")):
        if needle not in landed:
            problems.append(why)
    if not landed or "always()" in landed or "continue-on-error" in landed:
        problems.append("landed must exist, without always() or continue-on-error")

    names = list(steps(publish))
    idx = {p: next((i for i, n in enumerate(names) if n.startswith(p)), -1)
           for p in ("Publish history", "Verify the history push", "Open or update the alert issue")}
    if not 0 <= idx["Publish history"] < idx["Verify the history push"] < idx["Open or update the alert issue"]:
        problems.append("step order must be publish, landed, alert issue")

    action = step(publish, "Publish history")
    for needle in ("continue-on-error: true", "fail-on-alert: true"):
        if needle not in action:
            problems.append(f"publish action must keep {needle}")
    alert = step(publish, "Open or update the alert issue")
    if "if: steps.bench.outcome == 'failure'" not in alert or "always()" in alert or "continue-on-error" in alert \
            or "for attempt in 1 2 3" not in alert:
        problems.append("alert step: gate on steps.bench.outcome only (no always()), retried, not continue-on-error")
    if "--require-nonempty" not in step(publish, "Build ratio series"):
        problems.append("the ratio series step must be strict (--require-nonempty)")
    return problems


def check_pages(text):
    problems = []
    if not re.search(r"(?m)^permissions: \{\}\n", text):
        problems.append("workflow-level permissions must be {}")
    if not re.search(r"(?m)^on:\n  workflow_run:\n    workflows: \[benchmark\]\n    types: \[completed\]\n    branches: \[main\]\n  workflow_dispatch:\n", text):
        problems.append("triggers must be exactly workflow_run (benchmark, completed, main) and workflow_dispatch")
    if re.search(r"(?m)^  (push|pull_request|pull_request_target|schedule):", text):
        problems.append("no push/pull_request/schedule trigger allowed")
    deploy = job(text, "deploy")
    g = guard(deploy)
    for clause in ("github.event_name == 'workflow_dispatch'", DEFAULT_REF, "github.event_name == 'workflow_run'",
                   "github.event.workflow_run.event == 'push'",
                   "github.event.workflow_run.head_branch == github.event.repository.default_branch"):
        if clause not in g:
            problems.append(f"deploy guard lost: {clause}")
    if len(re.findall(r"(?m)^\s+pages: write$", text)) != 1 or len(re.findall(r"(?m)^\s+id-token: write$", text)) != 1 \
            or "pages: write" not in deploy or "id-token: write" not in deploy:
        problems.append("pages: write and id-token: write exactly once, on the deploy job")
    if re.search(r"(?m)^\s+(contents|issues|actions|pull-requests): write", text):
        problems.append("no other write scope allowed")
    if "name: github-pages" not in deploy:
        problems.append("deploy must use the github-pages environment")
    if not re.search(r"(?m)^\s+path: _site$", deploy) or re.search(r"(?m)^\s+path: site$", step_text(deploy, "upload-pages-artifact")):
        problems.append("the artifact path must be the allowlisted _site")
    if "run: bash ci/pages-probe.sh" not in deploy:
        problems.append("the strict probe script must be used")
    if "always()" in text or "continue-on-error" in text:
        problems.append("no always() or continue-on-error in pages.yml")
    stage = step(deploy, "Stage the allowlisted site files")
    if "for f in index.html data.js; do" not in stage or "cp -r" in stage or "cp -R" in stage:
        problems.append("staging must copy exactly index.html and data.js")
    return problems


def step_text(body, uses_fragment):
    parts = re.split(r"^      - ", body, flags=re.M)[1:]
    return next((p for p in parts if uses_fragment in p), "")


def check_absolute(text):
    problems = []
    step_ = step(job(text, "publish"), "Publish absolute times")
    if "steps.absolute.outputs.has_absolute == 'true'" not in step_ or "continue-on-error: true" not in step_:
        problems.append("the absolute publish must stay best effort and conditional on has_absolute")
    for forbidden in ("fail-on-alert", "comment-on-alert", "alert-threshold"):
        if forbidden in step_:
            problems.append(f"the absolute publish must not use {forbidden}")
    return problems


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.bench, self.pages = read("benchmark.yml"), read("pages.yml")

    def mutate(self, text, old, new):
        self.assertIn(old, text, "mutation target missing: the test needs updating")
        return text.replace(old, new, 1)

    def test_real_workflows_pass(self):
        self.assertEqual(check_benchmark(self.bench), [])
        self.assertEqual(check_pages(self.pages), [])
        self.assertEqual(check_absolute(self.bench), [])

    def test_benchmark_negative_cases(self):
        for old, new in (
                ("github.event_name == 'push' &&", "true &&"),
                ("needs.plan.outputs.mode == 'full' &&", "true &&"),
                ("      issues: write\n", "      issues: write\n      pages: write\n"),
                ("run: bash ci/landed.sh", "run: echo skipped"),
                ("          BEFORE_SHA: ${{ steps.before.outputs.sha }}\n", ""),
                ("        id: landed\n        if: steps.series.outputs.has_series == 'true'\n",
                 "        id: landed\n        if: always()\n"),
                ("if: steps.bench.outcome == 'failure'", "if: always()"),
                ("fail-on-alert: true", "fail-on-alert: false"),
                ("--require-nonempty > ratios.json", "> ratios.json")):
            with self.subTest(old=old):
                self.assertNotEqual(check_benchmark(self.mutate(self.bench, old, new)), [])

    def test_pages_negative_cases(self):
        for old, new in (
                ("permissions: {}", "permissions: write-all"),
                ("github.event.workflow_run.event == 'push' &&", "true &&"),
                ("github.event.workflow_run.head_branch == github.event.repository.default_branch)",
                 "true)"),
                ("github.ref == format('refs/heads/{0}', github.event.repository.default_branch)) ||", "true) ||"),
                ("  workflow_dispatch:\n", "  workflow_dispatch:\n  push:\n"),
                ("      contents: read\n      pages: write", "      contents: write\n      pages: write"),
                ("          path: _site", "          path: site"),
                ("for f in index.html data.js; do", "for f in index.html data.js README.md; do cp -r site/. _site/; done; for f in x; do"),
                ("run: bash ci/pages-probe.sh", "run: gh api repos/x --silent || true"),
                ("      name: github-pages", "      name: other")):
            with self.subTest(old=old):
                self.assertNotEqual(check_pages(self.mutate(self.pages, old, new)), [])

    def test_pages_scopes_only_in_pages_workflow(self):
        self.assertNotEqual(check_benchmark(self.mutate(
            self.bench, "  publish:\n", "  deploy-pages:\n    permissions:\n      pages: write\n      id-token: write\n  publish:\n")), [])

    def test_absolute_negative_cases(self):
        for old, new in (("          output-file-path: absolute.json\n", "          output-file-path: absolute.json\n          fail-on-alert: true\n"),
                         ("        id: bench_abs\n        if: steps.series.outputs.has_series == 'true' && steps.absolute.outputs.has_absolute == 'true'\n        continue-on-error: true\n",
                          "        id: bench_abs\n        if: steps.series.outputs.has_series == 'true'\n")):
            with self.subTest(old=old):
                self.assertNotEqual(check_absolute(self.mutate(self.bench, old, new)), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
