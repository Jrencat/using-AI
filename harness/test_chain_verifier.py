"""Deterministic checks of the read-only State Chain verifier on synthetic packages."""

import json
import tempfile
import unittest
from pathlib import Path

import chain_verifier
import harness
from test_harness import result, row, use


class ChainVerifierTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "runs"
        self.source = Path(self.tmp.name) / "s.jsonl"
        self.source.write_bytes(b"")
        harness.start(self.root, "vsc", "VSC", "s1", self.source)
        self.path = harness.run_path(self.root, "vsc")
        self.n = 0

    def call(self, kind, fields, tool=None, receipt=True, command="python harness/harness.py x"):
        tool = tool or getattr(self, "tool", "PowerShell")
        record = harness.append(self.path, kind, fields)
        self.n += 1
        if receipt:
            uid = f"u{self.n}"
            with self.source.open("ab") as out:
                out.write(harness.encoded(row("s1", "assistant", use(tool, uid, {"command": command}))))
                out.write(harness.encoded(row("s1", "user", result(uid, record["event_id"]))))
        return record

    def build(self, skip_receipt=None, eligible_attempt=True):
        def go(kind, fields, **kw):
            return self.call(kind, fields, receipt=kw.pop("receipt", True), **kw)
        go("QUESTION_CREATED", {"question_id": "Q1", "requirement_ref": "R", "severity": "Important", "context": "", "previous_state": None, "new_state": "OPEN"},
           receipt=skip_receipt != "question")
        go("QUESTION_STATE_CHANGED", {"question_id": "Q1", "requirement_ref": "R", "severity": "Important", "new_state": "ASSUMED"})
        go("ASSUMPTION_CREATED", {"assumption_id": "A1", "origin_question_id": "Q1", "content": "c", "default_behavior": "d", "impact": "i", "confidence": "m"},
           receipt=skip_receipt != "assumption")
        go("TASK_CREATED", {"task_id": "T1", "requirement_ref": "R", "scope": ["x"], "priority": "P1", "assumption_deps": ["A1"]},
           receipt=skip_receipt != "task")
        if eligible_attempt:
            go("STATE_TRANSITION_REJECTED", {"task_id": "T1", "requested_state": "ELIGIBLE", "reason": "assumption_dep A1 is ISOLATED"})
            go("TASK_STATE_CHANGED", {"task_id": "T1", "new_state": "BLOCKED"})
        return harness.seal(self.path)

    def verdict(self, **kw):
        return chain_verifier.verify(self.path, **kw)

    def test_complete_chain_passes(self):
        self.build()
        self.assertEqual("PASS", self.verdict()["verdict"])

    def test_bash_receipts_accepted(self):
        self.tool = "Bash"
        self.build()
        self.assertEqual("PASS", self.verdict()["verdict"])

    def test_missing_receipt_is_insufficient(self):
        for which in ("question", "assumption", "task"):
            with self.subTest(which=which):
                self.setUp()
                self.build(skip_receipt=which)
                out = self.verdict()
                self.assertEqual("INSUFFICIENT", out["verdict"])

    def test_missing_eligible_rejection_is_insufficient(self):
        self.build(eligible_attempt=False)
        self.assertEqual("INSUFFICIENT", self.verdict()["verdict"])

    def test_claim_conflict_is_invalid_agent_result(self):
        self.build()
        self.assertEqual("INVALID_AGENT_RESULT", self.verdict(claims={"T1": "ELIGIBLE"})["verdict"])
        self.assertEqual("PASS", self.verdict(claims={"T1": "BLOCKED", "A1": "ISOLATED", "Q1": "ASSUMED"})["verdict"])

    def test_forged_eligible_event_fails(self):
        self.build()
        with (self.path / "events.jsonl").open("ab") as out:
            out.write(harness.encoded({"event_id": "forged", "sequence": 99, "type": "TASK_STATE_CHANGED", "task_id": "T1",
                                       "new_state": "ELIGIBLE", "source": "harness_cli"}))
        self.assertEqual("FAIL", self.verdict()["verdict"])

    def test_direct_state_edit_is_flagged(self):
        self.call("QUESTION_CREATED", {"question_id": "Q1", "requirement_ref": "R", "severity": "Important", "context": "", "previous_state": None, "new_state": "OPEN"},
                  command="Add-Content harness/runs/RUN-vsc/events.jsonl x")
        with self.source.open("ab") as out:
            out.write(harness.encoded(row("s1", "assistant", use("Edit", "ed", {"file_path": "harness/runs/RUN-vsc/events.jsonl"}))))
        harness.seal(self.path)
        out = self.verdict()
        self.assertTrue(any("direct file edit" in i or "non-harness" in i for i in out["issues"]) or out["verdict"] != "PASS")

    def test_verifier_is_read_only(self):
        self.build()
        before = {p.name: p.read_bytes() for p in self.path.iterdir()}
        self.verdict()
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.path.iterdir()})


if __name__ == "__main__":
    unittest.main()
