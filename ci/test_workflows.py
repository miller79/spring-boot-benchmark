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
PUBLISH_GUARD = ("!cancelled() && github.event_name == 'push' && " + DEFAULT_REF +
                 " && needs.plan.outputs.mode == 'full' && needs.bench.result != 'skipped'")
PAGES_GUARD = ("(github.event_name == 'workflow_dispatch' && " + DEFAULT_REF + ") || "
               "(github.event_name == 'workflow_run' && github.event.workflow_run.event == 'push' && "
               "github.event.workflow_run.head_branch == github.event.repository.default_branch)")


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


def check_pinned(name, text):
    return [f"{name}: unpinned action {m}" for m in re.findall(r"(?m)^\s*(?:- )?uses: (\S+)", text)
            if not re.fullmatch(r"[\w.-]+/[\w./-]+@[0-9a-f]{40}", m)]


def check_checkouts(name, text):
    n_checkout = len(re.findall(r"uses: actions/checkout@", text))
    n_safe = len(re.findall(r"persist-credentials: false", text))
    return [] if n_checkout and n_checkout == n_safe else [f"{name}: every checkout needs persist-credentials: false"]


def check_data_file(text):
    """`landed` reads DATA_FILE; it must be where the action writes: <benchmark-data-dir-path>/data.js."""
    publish = job(text, "publish")
    m = re.search(r"benchmark-data-dir-path: '([^']*)'", step(publish, "Publish history"))
    want = "data.js" if m and m.group(1) == "." else f"{m.group(1) if m else 'dev/bench'}/data.js"
    got = re.search(r"DATA_FILE: (\S+)", step(publish, "Verify the history push landed"))
    return [] if got and got.group(1) == want else [f"landed DATA_FILE {got and got.group(1)!r} != {want!r}"]


def check_benchmark(text):
    problems = []
    publish = job(text, "publish")
    if " ".join(guard(publish).split()) != PUBLISH_GUARD:  # exact: a flipped && or a dropped clause is caught
        problems.append("publish guard changed")
    problems += check_data_file(text)
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
    if " ".join(guard(deploy).split()) != PAGES_GUARD:
        problems.append("deploy guard changed")
    if not re.search(r"(?m)^    concurrency:\n      group: pages\n      cancel-in-progress: false\n", deploy):
        problems.append("deploy must serialise on concurrency group pages without cancelling")
    problems += check_checkouts("pages.yml", text)
    problems += check_pinned("pages.yml", text)
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
    if "run: bash ci/stage-pages.sh site _site" not in stage or "if: steps.probe.outputs.present == 'true'" not in stage:
        problems.append("staging must run ci/stage-pages.sh (non-empty, no symlinks, two files) when bench-data exists")
    order = [deploy.find(x) for x in ("path: site", "Stage the allowlisted", "upload-pages-artifact", "deploy-pages")]
    if -1 in order or order != sorted(order):
        problems.append("order must be checkout bench-data, stage, upload, deploy")
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
                ("github.event_name == 'push' &&", "github.event_name == 'push' ||"),
                ("!cancelled() &&", "!cancelled() ||"),
                ("DATA_FILE: data.js", "DATA_FILE: dev/bench/data.js"),
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
                ("run: bash ci/stage-pages.sh site _site", "run: cp -r site _site"),
                ("      group: pages\n      cancel-in-progress: false", "      group: pages\n      cancel-in-progress: true"),
                ("      group: pages\n", "      group: other\n"),
                ("          persist-credentials: false\n      - name: Check", "      - name: Check"),
                ("actions/deploy-pages@368f82528645a54fb793d4d04e342629a3f51346", "actions/deploy-pages@v5"),
                ("github.event.workflow_run.event == 'push' &&", "github.event.workflow_run.event == 'push' ||"),
                ("(github.event_name == 'workflow_run' &&", "(github.event_name == 'workflow_run' ||"),
                ("default_branch)) ||", "default_branch)) &&"),
                ("run: bash ci/pages-probe.sh", "run: gh api repos/x --silent || true"),
                ("      name: github-pages", "      name: other")):
            with self.subTest(old=old):
                self.assertNotEqual(check_pages(self.mutate(self.pages, old, new)), [])

    def test_all_actions_pinned_and_checkouts_keep_no_credentials(self):
        names = sorted(n for n in os.listdir(os.path.join(ROOT, ".github", "workflows")) if n.endswith(".yml"))
        for n in names:
            self.assertEqual(check_pinned(n, read(n)), [], n)
        for n in ("pages.yml", "ci-tests.yml"):
            self.assertEqual(check_checkouts(n, read(n)), [], n)
        self.assertNotEqual(check_pinned("x", "      - uses: actions/checkout@v4\n"), [])
        self.assertNotEqual(check_pinned("x", "        uses: a/b@3d3c42e\n"), [])
        self.assertNotEqual(check_checkouts("x", "uses: actions/checkout@" + "a" * 40 + "\n"), [])

    def test_ci_tests_is_read_only(self):
        text = read("ci-tests.yml")
        self.assertRegex(text, r"(?m)^permissions:\n  contents: read\n")
        self.assertNotRegex(text, r"(?m)^\s+[a-z-]+: write")
        self.assertNotIn("secrets.", text)
        self.assertIn("command -v shellcheck", text)

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
