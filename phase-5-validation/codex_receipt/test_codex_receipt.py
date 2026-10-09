"""Offline tests for the Codex receipt adapter (P5-1). No network, no Codex process, no real session files.

Run from the repo root:  python -I -m unittest discover -s phase-5-validation/codex_receipt -p "test_*.py"
"""

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ADAPTER = HERE / "codex_receipt_adapter.py"
HARNESS = ROOT / "harness" / "harness.py"
LOCK = ROOT / "docs/architecture/phase-5/codex-receipt-lock.json"
REGISTRY = ROOT / "docs/architecture/phase-5/codex-receipt-preregistration.json"
FIXTURES = HERE / "fixtures"

sys.path.insert(0, str(HERE))
import codex_receipt_adapter as adapter  # noqa: E402


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_bytes())


CASES = load(REGISTRY)["cases"]


def fixture_bytes(case):
    raw = (FIXTURES / case["fixture"]).read_bytes()
    if case.get("derived") == "LF_TO_CRLF":
        raw = raw.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    return raw


def project(row):
    block = row["message"]["content"][0]
    if block["type"] == "tool_use":
        return ["use", row["origin"]["raw_line"], block["id"], block["name"], block["input"]]
    return ["res", row["origin"]["raw_line"], block["tool_use_id"], block["content"]]


def run_cli(raw, tmp, name, *flags):
    src = Path(tmp) / (name + ".jsonl")
    src.write_bytes(raw)
    out = Path(tmp) / (name + "-out")
    proc = subprocess.run([sys.executable, "-I", str(ADAPTER), "--input", str(src), "--out-dir", str(out), *flags],
                          capture_output=True, text=True)
    return proc, out


class LockTests(unittest.TestCase):
    def test_locked_files_unchanged(self):
        lock = load(LOCK)
        self.assertFalse(lock["adapter_present_at_lock"])
        for rel, expected in lock["files"].items():
            data = (ROOT / rel).read_bytes().replace(b"\r\n", b"\n")
            self.assertEqual(sha(data), expected, rel)

    def test_lock_covers_every_fixture_and_registry_case(self):
        lock = load(LOCK)["files"]
        on_disk = {"phase-5-validation/codex_receipt/fixtures/" + p.name for p in FIXTURES.glob("*.jsonl")}
        self.assertEqual({k for k in lock if "/fixtures/" in k}, on_disk)
        self.assertEqual({c["fixture"] for c in CASES}, {Path(p).name for p in on_disk})
        self.assertEqual(len(CASES), 26)


class PreRegisteredCaseTests(unittest.TestCase):
    def test_cases_match_registry(self):
        for case in CASES:
            with self.subTest(case=case["id"]):
                result = adapter.convert(fixture_bytes(case), case["fixture"])
                exp = case["expected"]
                self.assertEqual(result["status"], exp["adapter_status"])
                self.assertEqual([[g["code"], g["line"]] for g in result["gaps"]], exp["gaps"])
                self.assertEqual([project(r) for r in result["rows"]] if result["session_id"] else [],
                                 exp["runtime_rows"])
                if "ignored_counts" in exp:
                    self.assertEqual(result["ignored_counts"], exp["ignored_counts"])

    def test_cli_exit_codes_and_withholding(self):
        with tempfile.TemporaryDirectory() as tmp:
            for case in CASES:
                with self.subTest(case=case["id"]):
                    exp = case["expected"]
                    proc, out = run_cli(fixture_bytes(case), tmp, case["id"])
                    self.assertEqual(proc.returncode, exp["exit_code"], proc.stderr)
                    self.assertTrue((out / "provenance.json").exists())
                    self.assertEqual((out / "runtime.jsonl").exists(), exp["adapter_status"] == "COMPLETE")
                    self.assertFalse((out / "runtime.partial.jsonl").exists())
                    partial_proc, partial_out = run_cli(fixture_bytes(case), tmp, case["id"] + "p", "--emit-partial")
                    self.assertEqual(partial_proc.returncode, exp["exit_code"])
                    wrote = (partial_out / "runtime.partial.jsonl").exists()
                    self.assertEqual(wrote, exp["adapter_status"] == "INCOMPLETE" and exp["partial_output_allowed"])
                    self.assertEqual((partial_out / "runtime.jsonl").exists(), exp["adapter_status"] == "COMPLETE")

    def test_crlf_variant_matches_lf_output(self):
        by_id = {c["id"]: c for c in CASES}
        lf = adapter.convert(fixture_bytes(by_id["P01"]), "x.jsonl")
        crlf = adapter.convert(fixture_bytes(by_id["P05"]), "x.jsonl")
        self.assertIn(b"\r\n", fixture_bytes(by_id["P05"]))
        self.assertEqual(lf["runtime_bytes"], crlf["runtime_bytes"])


class PropertyTests(unittest.TestCase):
    def test_deterministic_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            for case in CASES:
                with self.subTest(case=case["id"]):
                    raw = fixture_bytes(case)
                    a = run_cli(raw, tmp, case["id"] + "a", "--emit-partial")[1]
                    b = run_cli(raw, tmp, case["id"] + "b", "--emit-partial")[1]
                    names = sorted(p.name for p in a.iterdir())
                    self.assertEqual(names, sorted(p.name for p in b.iterdir()))
                    for name in names:
                        a_bytes, b_bytes = (a / name).read_bytes(), (b / name).read_bytes()
                        if name == "provenance.json":  # only the input file name differs between the two runs
                            a_bytes = a_bytes.replace(case["id"].encode() + b"a.jsonl", b"X")
                            b_bytes = b_bytes.replace(case["id"].encode() + b"b.jsonl", b"X")
                        self.assertEqual(a_bytes, b_bytes, name)

    def test_traceability_to_raw_lines(self):
        for case in CASES:
            with self.subTest(case=case["id"]):
                raw = fixture_bytes(case)
                raw_lines = [x[:-1] if x.endswith(b"\r") else x for x in raw.split(b"\n")]
                result = adapter.convert(raw, "x.jsonl")
                self.assertEqual(len(result["rows"]), len(result["sidecar_rows"]))
                for row, side in zip(result["rows"], result["sidecar_rows"]):
                    line = row["origin"]["raw_line"]
                    self.assertEqual(row["origin"]["raw_line_sha256"], sha(raw_lines[line - 1]))
                    self.assertEqual(side["raw_line_sha256"], sha(raw_lines[line - 1]))
                    self.assertEqual(side["row_sha256"], sha(adapter.dump(row)))

    def test_no_false_complete_status(self):
        for case in CASES:
            if case["kind"] == "negative":
                with self.subTest(case=case["id"]):
                    self.assertEqual(adapter.convert(fixture_bytes(case), "x.jsonl")["status"], "INCOMPLETE")

    def test_input_not_modified_and_no_network_imports(self):
        before = {p.name: p.read_bytes() for p in FIXTURES.glob("*.jsonl")}
        for case in CASES:
            adapter.convert(fixture_bytes(case), case["fixture"])
        self.assertEqual(before, {p.name: p.read_bytes() for p in FIXTURES.glob("*.jsonl")})
        source = ADAPTER.read_text(encoding="utf-8")
        for banned in ("socket", "urllib", "http", "requests", "subprocess", "datetime", "random", "uuid", "time"):
            self.assertNotIn("import " + banned, source)
        self.assertNotIn("harness", source.replace("Harness", "").replace("harness.py", ""))

    def test_refuses_non_empty_output_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc, out = run_cli(fixture_bytes(CASES[0]), tmp, "first")
            self.assertEqual(proc.returncode, 0)
            again = subprocess.run([sys.executable, "-I", str(ADAPTER), "--input", str(Path(tmp) / "first.jsonl"),
                                    "--out-dir", str(out)], capture_output=True, text=True)
            self.assertEqual(again.returncode, 1)


def harness(root, *args):
    proc = subprocess.run([sys.executable, "-I", str(HARNESS), "--root", str(root), *args], capture_output=True, text=True)
    return proc.returncode, proc.stdout


class HarnessBlackBoxTests(unittest.TestCase):
    """Run the unchanged Harness start/seal/verify in a temp root. No Agent, no network, no repo state change."""

    def test_registered_blackbox_expectations(self):
        checked = 0
        with tempfile.TemporaryDirectory() as tmp:
            for case in CASES:
                bb = case.get("harness_blackbox")
                if not bb:
                    continue
                with self.subTest(case=case["id"]):
                    proc, out = run_cli(fixture_bytes(case), tmp, case["id"], "--emit-partial")
                    runtime = out / bb["input"]
                    self.assertTrue(runtime.exists())
                    session = load(out / "provenance.json")["session_id"]
                    root = Path(tmp) / "runs"
                    source = Path(tmp) / (case["id"] + "-harness-source.jsonl")
                    source.write_bytes(b"")
                    run_id = "P5" + case["id"]
                    code, _ = harness(root, "start", "--run-id", run_id, "--probe-id", "P5-OFFLINE", "--session-id", session,
                                      "--source", str(source))
                    self.assertEqual(code, 0)
                    source.write_bytes(runtime.read_bytes())
                    code, text = harness(root, "seal", "--run-id", run_id)
                    self.assertEqual(code, 0, text)
                    self.assertEqual(json.loads(text)["capture_status"], bb["capture_status"])
                    code, text = harness(root, "verify", "--run-id", run_id)
                    self.assertEqual(code, 0, text)
                    self.assertEqual(json.loads(text)["valid_package"], bb["valid_package"])
                    checked += 1
        self.assertEqual(checked, 7)


if __name__ == "__main__":
    unittest.main()
