#!/usr/bin/env python3
"""Tests for bench.py: docker error handling in run_once and the per-cell sample checkpoint.
Docker is mocked; nothing here needs a daemon. Usage: python3 ci/test_bench.py"""
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bench  # noqa: E402

STARTED = "Started Application in 1.5 seconds (process running for 1.7)"


def cp(stdout="", stderr="", rc=0):
    return subprocess.CompletedProcess([], rc, stdout, stderr)


class FakeDocker:
    """Dispatches on the docker sub-command; `fail` maps a sub-command to an exception to raise."""

    def __init__(self, exit_code="0 false", logs=STARTED, fail=None):
        self.exit_code, self.logs, self.fail, self.calls = exit_code, logs, fail or {}, []

    def __call__(self, args, **kw):
        self.calls.append(args[1])
        if args[1] in self.fail:
            raise self.fail[args[1]]
        if args[1] == "create":
            return cp("cid123\n")
        if args[1] == "inspect":
            return cp(self.exit_code + "\n")
        if args[1] == "logs":
            return cp(self.logs)
        return cp()


def run(fake):
    with mock.patch.object(bench.subprocess, "run", fake):
        return bench.run_once("img", "0.6", "", None, 5)


def err(cmd, stderr="boom"):
    # sh() uses text=True (str stderr); docker wait does not (pass bytes)
    return subprocess.CalledProcessError(1, cmd, stderr=stderr)


class RunOnceTests(unittest.TestCase):
    def test_happy_path_is_ok(self):
        fake = FakeDocker()
        rec = run(fake)
        self.assertTrue(rec["ok"])
        self.assertEqual((rec["exit_code"], rec["started_s"]), (0, 1.5))
        self.assertEqual(fake.calls[-1], "rm")

    def test_wait_error_is_not_ok_with_reason(self):
        fake = FakeDocker(fail={"wait": err("wait", b"daemon gone")})
        rec = run(fake)
        self.assertFalse(rec["ok"])
        self.assertIn("docker wait failed: daemon gone", rec["log_tail"][0])
        self.assertNotIn("inspect", fake.calls)
        self.assertEqual(fake.calls[-1], "rm")  # container still removed

    def test_wait_oserror_is_not_ok(self):
        rec = run(FakeDocker(fail={"wait": OSError("no docker")}))
        self.assertFalse(rec["ok"])
        self.assertIn("docker wait failed: no docker", rec["log_tail"][0])

    def test_inspect_error_is_not_ok_with_reason(self):
        fake = FakeDocker(fail={"inspect": err("inspect", "no such container")})
        rec = run(fake)
        self.assertFalse(rec["ok"])
        self.assertIsNone(rec["exit_code"])
        self.assertIn("docker inspect failed: no such container", rec["log_tail"][0])
        self.assertEqual(fake.calls[-1], "rm")

    def test_inspect_garbage_is_not_ok(self):
        for out in ("", "0", "abc true"):
            rec = run(FakeDocker(exit_code=out))
            self.assertFalse(rec["ok"], out)
            self.assertIn("docker inspect failed", rec["log_tail"][0])

    def test_nonzero_exit_is_not_ok(self):
        rec = run(FakeDocker(exit_code="1 false"))
        self.assertFalse(rec["ok"])
        self.assertEqual(rec["exit_code"], 1)

    def test_missing_started_line_is_not_ok(self):
        self.assertFalse(run(FakeDocker(logs="nothing here"))["ok"])

    def test_timeout_is_recorded_and_not_ok(self):
        fake = FakeDocker(fail={"wait": subprocess.TimeoutExpired("wait", 5)})
        rec = run(fake)
        self.assertTrue(rec["timed_out"])
        self.assertFalse(rec["ok"])
        self.assertIn("kill", fake.calls)

    def test_create_and_start_errors_still_handled(self):
        for sub in ("create", "start"):
            rec = run(FakeDocker(fail={sub: err(sub)}))
            self.assertFalse(rec["ok"], sub)
            self.assertIn(f"docker {sub} failed", rec["log_tail"][0])


def result(iterations, repeats, oks, cpu_profiles=("p06",), sides=("head",), profiles=("plain", "aot")):
    """`oks` maps (side, profile, cpu_profile) to the number of ok samples; others get all ok."""
    variants = [{"side": s, "profile": p} for p in profiles for s in sides]
    samples = []
    for cpn in cpu_profiles:
        for v in variants:
            n = iterations * repeats
            good = oks.get((v["side"], v["profile"], cpn), n)
            samples += [{"ok": i < good, "cpu_profile": cpn, "side": v["side"], "profile": v["profile"]}
                        for i in range(n)]
    return {"iterations": iterations, "repeats": repeats, "variants": variants, "samples": samples}


class CheckpointTests(unittest.TestCase):
    def bad(self, res, cps=("p06",)):
        return bench.insufficient_cells(res, list(cps))

    def test_all_ok_passes(self):
        self.assertEqual(self.bad(result(30, 1, {}, ("p06", "p10", "p20")), ("p06", "p10", "p20")), [])

    def test_one_below_minimum_fails_and_exact_minimum_passes(self):
        n = bench.MIN_OK_SAMPLES
        self.assertEqual(self.bad(result(30, 1, {("head", "aot", "p06"): n})), [])
        bad = self.bad(result(30, 1, {("head", "aot", "p06"): n - 1}))
        self.assertEqual(bad, [f"head/aot/p06: {n - 1} ok"])

    def test_empty_cell_fails(self):
        self.assertEqual(self.bad(result(30, 1, {("head", "plain", "p06"): 0})), ["head/plain/p06: 0 ok"])

    def test_old_check_would_have_passed_a_single_ok_sample(self):
        res = result(30, 1, {("head", "aot", "p06"): 1})
        self.assertTrue(any(s["ok"] for s in res["samples"] if s["profile"] == "aot"))
        self.assertTrue(self.bad(res))

    def test_cell_is_per_cpu_profile_not_pooled(self):
        res = result(30, 1, {("head", "aot", "p10"): 0}, ("p06", "p10"))
        self.assertEqual(self.bad(res, ("p06", "p10")), ["head/aot/p10: 0 ok"])

    def test_base_side_is_checked_too(self):
        res = result(10, 1, {("base", "aot", "p06"): 2}, sides=("head", "base"))
        self.assertEqual(self.bad(res), ["base/aot/p06: 2 ok"])

    def test_smoke_mode_10_iterations_is_satisfiable(self):
        self.assertGreaterEqual(10, bench.MIN_OK_SAMPLES)
        self.assertEqual(self.bad(result(10, 1, {("head", "aot", "p06"): bench.MIN_OK_SAMPLES})), [])
        self.assertEqual(self.bad(result(10, 1, {}, sides=("head", "base"))), [])

    def test_repeats_are_pooled_within_a_cell(self):
        self.assertEqual(self.bad(result(3, 2, {("head", "aot", "p06"): 5})), [])
        self.assertTrue(self.bad(result(3, 2, {("head", "aot", "p06"): 4})))

    def test_fewer_runs_than_minimum_need_all_of_them(self):
        self.assertEqual(bench.needed_samples(3, 1), 3)
        self.assertEqual(bench.needed_samples(1, 1), 1)
        self.assertEqual(bench.needed_samples(30, 3), bench.MIN_OK_SAMPLES)
        self.assertEqual(self.bad(result(3, 1, {})), [])
        self.assertTrue(self.bad(result(3, 1, {("head", "aot", "p06"): 2})))


class CmdRunTests(unittest.TestCase):
    def run_cmd(self, ok_for):
        """Run cmd_run with run_once mocked; `ok_for(profile, call_no)` decides each sample."""
        counter = {}

        def fake_run_once(image, *a):
            profile = image.split("benchmark-tomcat-")[1].split(":")[0]
            counter[profile] = counter.get(profile, 0) + 1
            ok = ok_for(profile, counter[profile])
            return {"ok": ok, "exit_code": 0 if ok else 1, "timed_out": False}

        with tempfile.TemporaryDirectory() as out, \
                mock.patch.object(bench, "run_once", fake_run_once), \
                mock.patch.object(bench, "try_out", lambda *a, **k: "sha256:x"):
            args = bench.argparse.Namespace(
                module="tomcat", profiles="plain,aot", sides="head", cpu_profiles="p06", iterations=10,
                repeats=1, cpuset="", timeout=5, seed=1, out=out)
            bench.cmd_run(args)

    def test_run_passes_when_every_cell_has_enough(self):
        self.run_cmd(lambda p, n: True)

    def test_run_fails_when_a_cell_has_too_few_ok_samples(self):
        # warm-up is call 1; samples are calls 2..11. Only 2 of the 10 aot samples are ok.
        with self.assertRaises(SystemExit) as cm:
            self.run_cmd(lambda p, n: p == "plain" or n in (2, 3))
        self.assertIn("head/aot/p06: 2 ok", str(cm.exception))

    def test_run_fails_when_a_cell_is_empty(self):
        with self.assertRaises(SystemExit):
            self.run_cmd(lambda p, n: p == "plain")


class RealSubprocessTests(unittest.TestCase):
    """No mocks: a stub `docker` executable on PATH, so the exception types are the real ones."""

    def run_with_stub(self, wait_rc):
        with tempfile.TemporaryDirectory() as d:
            stub = os.path.join(d, "docker")
            with open(stub, "w") as f:
                f.write('#!/bin/sh\ncase "$1" in\n'
                        '  create) echo cid1;;\n'
                        '  wait) echo "daemon went away" >&2; exit %d;;\n'
                        '  inspect) echo "0 false";;\n'
                        '  logs) echo "Started Application in 1.5 seconds";;\n'
                        'esac\n' % wait_rc)
            os.chmod(stub, 0o755)
            with mock.patch.dict(os.environ, {"PATH": d + os.pathsep + os.environ["PATH"]}):
                return bench.run_once("img", "0.6", "", None, 5)

    def test_real_wait_failure_is_not_ok_with_reason(self):
        rec = self.run_with_stub(1)
        self.assertFalse(rec["ok"])
        self.assertIn("docker wait failed: daemon went away", rec["log_tail"][0])

    def test_err_text_decodes_bytes(self):
        self.assertEqual(bench._err_text(err("x", b"caf\xc3\xa9 \xff")), "caf\u00e9 \ufffd")


if __name__ == "__main__":
    unittest.main(verbosity=2)
