"""Offline tests for Codex receipt mapping v2 (P5-1.1). No network, no Codex process, no real session files.

Run from the repo root:  python -I -m unittest discover -s phase-5-validation/codex_receipt -p "test_*.py"
Expectations come from the locked v2 registry; they are never edited to match the adapter.
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
LOCK = ROOT / "docs/architecture/phase-5/codex-receipt-lock-v2.json"
REGISTRY = ROOT / "docs/architecture/phase-5/codex-receipt-preregistration-v2.json"
V1_REGISTRY = ROOT / "docs/architecture/phase-5/codex-receipt-preregistration.json"
FIXTURES = HERE / "fixtures_v2"
V1_FIXTURES = HERE / "fixtures"
V2 = ("--mapping-version", "2")

sys.path.insert(0, str(HERE))
import codex_receipt_adapter as adapter  # noqa: E402


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_bytes())


REG = load(REGISTRY)
CASES = REG["cases"]
V1_CASES = load(V1_REGISTRY)["cases"]


def fixture_bytes(case, directory=FIXTURES):
    raw = (directory / case["fixture"]).read_bytes()
    if case.get("derived") == "LF_TO_CRLF":
        raw = raw.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    return raw


def project(row):
    block = row["message"]["content"][0]
    if block["type"] == "tool_use":
        return ["use", row["origin"]["raw_line"], block["id"], block["name"], block["input"]]
    return ["res", row["origin"]["raw_line"], block["tool_use_id"], block["content"]]


def gaps_of(result):
    return [[g["code"], g["line"]] for g in result["gaps"]]


def rows_of(result):
    return [project(r) for r in result["rows"]] if result["session_id"] else []


def run_cli(raw, tmp, name, *flags):
    src = Path(tmp) / (name + ".jsonl")
    src.write_bytes(raw)
    out = Path(tmp) / (name + "-out")
    proc = subprocess.run([sys.executable, "-I", str(ADAPTER), "--input", str(src), "--out-dir", str(out), *flags],
                          capture_output=True, text=True)
    return proc, out


class LockV2Tests(unittest.TestCase):
    def test_locked_files_unchanged(self):
        lock = load(LOCK)
        self.assertEqual(lock["lock_id"], "CODEX-RECEIPT-LOCK-V2")
        self.assertFalse(lock["adapter_v2_present_at_lock"])
        for rel, expected in lock["files"].items():
            data = (ROOT / rel).read_bytes().replace(b"\r\n", b"\n")
            self.assertEqual(sha(data), expected, rel)

    def test_lock_covers_only_v2_files_and_every_fixture(self):
        files = load(LOCK)["files"]
        self.assertTrue(all("fixtures/" not in k or "/fixtures_v2/" in k for k in files))
        self.assertNotIn("docs/architecture/phase-5/codex-receipt-mapping.md", files)
        on_disk = {"phase-5-validation/codex_receipt/fixtures_v2/" + p.name for p in FIXTURES.glob("*.jsonl")}
        self.assertEqual({k for k in files if "/fixtures_v2/" in k}, on_disk)
        used = {c["fixture"] for c in CASES} | {c["fixture"] for c in REG["default_version_cases"]}
        self.assertEqual(used, {Path(p).name for p in on_disk})
        self.assertEqual(len(CASES), 32)
        self.assertEqual(len(V1_CASES), 26)


class PreRegisteredV2Tests(unittest.TestCase):
    def test_cases_match_registry(self):
        for case in CASES:
            with self.subTest(case=case["id"]):
                result = adapter.convert(fixture_bytes(case), case["fixture"], 2)
                exp = case["expected"]
                self.assertEqual(result["status"], exp["adapter_status"])
                self.assertEqual(gaps_of(result), exp["gaps"])
                self.assertEqual(rows_of(result), exp["runtime_rows"])
                self.assertEqual(result["ignored_counts"], exp["ignored_counts"])
                for row in result["rows"]:
                    self.assertEqual(row["origin"]["mapping_version"], 2)

    def test_cli_exit_codes_and_withholding(self):
        with tempfile.TemporaryDirectory() as tmp:
            for case in CASES:
                with self.subTest(case=case["id"]):
                    exp = case["expected"]
                    proc, out = run_cli(fixture_bytes(case), tmp, case["id"], *V2)
                    self.assertEqual(proc.returncode, exp["exit_code"], proc.stderr)
                    self.assertEqual((out / "runtime.jsonl").exists(), exp["adapter_status"] == "COMPLETE")
                    self.assertFalse((out / "runtime.partial.jsonl").exists())
                    side = load(out / "provenance.json")
                    self.assertEqual((side["mapping_version"], side["adapter_version"]), (2, "2"))
                    partial_proc, partial_out = run_cli(fixture_bytes(case), tmp, case["id"] + "p", *V2, "--emit-partial")
                    self.assertEqual(partial_proc.returncode, exp["exit_code"])
                    wrote = (partial_out / "runtime.partial.jsonl").exists()
                    self.assertEqual(wrote, exp["adapter_status"] == "INCOMPLETE" and exp["partial_output_allowed"])
                    self.assertEqual((partial_out / "runtime.jsonl").exists(), exp["adapter_status"] == "COMPLETE")

    def test_crlf_variant_matches_lf_output(self):
        by_id = {c["id"]: c for c in CASES}
        lf = adapter.convert(fixture_bytes(by_id["Q01"]), "x.jsonl", 2)
        crlf = adapter.convert(fixture_bytes(by_id["Q06"]), "x.jsonl", 2)
        self.assertIn(b"\r\n", fixture_bytes(by_id["Q06"]))
        self.assertEqual(lf["runtime_bytes"], crlf["runtime_bytes"])

    def test_no_complete_with_compaction_unpaired_or_bad_token(self):
        for case in CASES:
            raw = fixture_bytes(case)
            risky = b'"type":"compacted"' in raw or case["id"].startswith(("T", "C"))
            if case["kind"] == "negative" or risky:
                with self.subTest(case=case["id"]):
                    result = adapter.convert(raw, "x.jsonl", 2)
                    self.assertEqual(result["status"], "INCOMPLETE")
                    with tempfile.TemporaryDirectory() as tmp:
                        _, out = run_cli(raw, tmp, "n", *V2)
                        self.assertFalse((out / "runtime.jsonl").exists())


class PropertyV2Tests(unittest.TestCase):
    def test_deterministic_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            for case in CASES:
                with self.subTest(case=case["id"]):
                    raw = fixture_bytes(case)
                    a = run_cli(raw, tmp, case["id"] + "a", *V2, "--emit-partial")[1]
                    b = run_cli(raw, tmp, case["id"] + "b", *V2, "--emit-partial")[1]
                    names = sorted(p.name for p in a.iterdir())
                    self.assertEqual(names, sorted(p.name for p in b.iterdir()))
                    for name in names:
                        a_bytes, b_bytes = (a / name).read_bytes(), (b / name).read_bytes()
                        if name == "provenance.json":
                            a_bytes = a_bytes.replace(case["id"].encode() + b"a.jsonl", b"X")
                            b_bytes = b_bytes.replace(case["id"].encode() + b"b.jsonl", b"X")
                        self.assertEqual(a_bytes, b_bytes, name)

    def test_traceability_to_raw_lines(self):
        for case in CASES:
            with self.subTest(case=case["id"]):
                raw = fixture_bytes(case)
                raw_lines = [x[:-1] if x.endswith(b"\r") else x for x in raw.split(b"\n")]
                result = adapter.convert(raw, "x.jsonl", 2)
                self.assertEqual(len(result["rows"]), len(result["sidecar_rows"]))
                for row, side in zip(result["rows"], result["sidecar_rows"]):
                    line = row["origin"]["raw_line"]
                    self.assertEqual(row["origin"]["raw_line_sha256"], sha(raw_lines[line - 1]))
                    self.assertEqual(side["raw_line_sha256"], sha(raw_lines[line - 1]))
                    self.assertEqual(side["row_sha256"], sha(adapter.dump(row)))

    def test_ignored_and_gapped_records_never_become_rows(self):
        for case in CASES:
            with self.subTest(case=case["id"]):
                raw = fixture_bytes(case)
                raw_lines = [x[:-1] if x.endswith(b"\r") else x for x in raw.split(b"\n")]
                for row in adapter.convert(raw, "x.jsonl", 2)["rows"]:
                    record = json.loads(raw_lines[row["origin"]["raw_line"] - 1])
                    self.assertEqual(record["type"], "response_item")

    def test_input_not_modified(self):
        before = {p.name: p.read_bytes() for p in FIXTURES.glob("*.jsonl")}
        for case in CASES:
            adapter.convert(fixture_bytes(case), case["fixture"], 2)
        self.assertEqual(before, {p.name: p.read_bytes() for p in FIXTURES.glob("*.jsonl")})

    def test_unsupported_mapping_version_rejected(self):
        with self.assertRaises(ValueError):
            adapter.convert(b"{}\n", "x.jsonl", 3)


class V1UnchangedTests(unittest.TestCase):
    def test_all_v1_cases_give_same_result_under_v2(self):
        for case in V1_CASES:
            with self.subTest(case=case["id"]):
                raw = fixture_bytes(case, V1_FIXTURES)
                result = adapter.convert(raw, case["fixture"], 2)
                exp = case["expected"]
                self.assertEqual(result["status"], exp["adapter_status"])
                self.assertEqual(gaps_of(result), exp["gaps"])
                self.assertEqual(rows_of(result), exp["runtime_rows"])
                if "ignored_counts" in exp:
                    self.assertEqual(result["ignored_counts"], exp["ignored_counts"])

    def test_default_and_explicit_v1_outputs_are_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            for case in V1_CASES:
                with self.subTest(case=case["id"]):
                    raw = fixture_bytes(case, V1_FIXTURES)
                    default_proc, default_out = run_cli(raw, tmp, case["id"] + "d", "--emit-partial")
                    explicit_proc, explicit_out = run_cli(raw, tmp, case["id"] + "e", "--mapping-version", "1", "--emit-partial")
                    self.assertEqual(default_proc.returncode, explicit_proc.returncode)
                    names = sorted(p.name for p in default_out.iterdir())
                    self.assertEqual(names, sorted(p.name for p in explicit_out.iterdir()))
                    for name in names:
                        d, e = (default_out / name).read_bytes(), (explicit_out / name).read_bytes()
                        if name == "provenance.json":
                            d = d.replace(case["id"].encode() + b"d.jsonl", b"X")
                            e = e.replace(case["id"].encode() + b"e.jsonl", b"X")
                        self.assertEqual(d, e, name)
                    side = load(default_out / "provenance.json")
                    self.assertEqual((side["mapping_version"], side["adapter_version"]), (1, "1"))

    def test_default_version_cases_select_v1(self):
        with tempfile.TemporaryDirectory() as tmp:
            for case in REG["default_version_cases"]:
                with self.subTest(case=case["id"]):
                    exp = case["expected"]
                    raw = (FIXTURES / case["fixture"]).read_bytes()
                    proc, out = run_cli(raw, tmp, case["id"], "--emit-partial")
                    self.assertEqual(proc.returncode, exp["exit_code"])
                    side = load(out / "provenance.json")
                    self.assertEqual(side["mapping_version"], exp["mapping_version_in_provenance"])
                    self.assertEqual(side["status"], exp["adapter_status"])
                    self.assertEqual([[g["code"], g["line"]] for g in side["gaps"]], exp["gaps"])
                    self.assertFalse((out / "runtime.jsonl").exists())
                    rows = [json.loads(x) for x in (out / "runtime.partial.jsonl").read_bytes().splitlines()]
                    self.assertEqual([project(r) for r in rows], exp["runtime_rows"])
                    self.assertTrue(all(r["origin"]["mapping_version"] == 1 for r in rows))


def harness(root, *args):
    proc = subprocess.run([sys.executable, "-I", str(HARNESS), "--root", str(root), *args], capture_output=True, text=True)
    return proc.returncode, proc.stdout


class HarnessBlackBoxV2Tests(unittest.TestCase):
    """Run the unchanged Harness start/seal/verify in a temp root. No Agent, no network, no repo state change."""

    def test_registered_blackbox_expectations(self):
        checked = 0
        with tempfile.TemporaryDirectory() as tmp:
            for case in CASES:
                bb = case.get("harness_blackbox")
                if not bb:
                    continue
                with self.subTest(case=case["id"]):
                    proc, out = run_cli(fixture_bytes(case), tmp, case["id"], *V2, "--emit-partial")
                    runtime = out / bb["input"]
                    self.assertTrue(runtime.exists())
                    session = load(out / "provenance.json")["session_id"]
                    root = Path(tmp) / "runs"
                    source = Path(tmp) / (case["id"] + "-harness-source.jsonl")
                    source.write_bytes(b"")
                    run_id = "P52" + case["id"]
                    code, _ = harness(root, "start", "--run-id", run_id, "--probe-id", "P5-OFFLINE-V2", "--session-id", session,
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
        self.assertEqual(checked, 8)


if __name__ == "__main__":
    unittest.main()
