"""Deterministic capability checks; these are not Phase 1D Probe runs."""

import json
import tempfile
import unittest
from pathlib import Path

import harness


def use(name, uid, arguments=None):
    return {"type": "tool_use", "name": name, "id": uid, "input": arguments or {}}


def result(uid, content="ok", error=False):
    return {"type": "tool_result", "tool_use_id": uid, "content": content, "is_error": error}


def row(session, role, content, answers=None):
    output = {"type": "assistant" if role == "assistant" else "user", "sessionId": session,
              "timestamp": "2026-01-01T00:00:00Z", "message": {"role": role, "content": [content]}}
    if answers is not None:
        output["toolUseResult"] = {"answers": answers}
    return output


class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "runs"
        self.source = Path(self.tmp.name) / "session.jsonl"
        self.source.write_bytes(b"")
        harness.start(self.root, "smoke", "CAPABILITY", "session-1", self.source)
        self.path = harness.run_path(self.root, "smoke")

    def runtime(self, *rows):
        with self.source.open("ab") as output:
            for item in rows:
                output.write(harness.encoded(item))

    def question(self, qid="TECH-001", severity="Important"):
        return harness.append(self.path, "QUESTION_CREATED", {"question_id": qid, "requirement_ref": "R-1",
                                                               "severity": severity, "context": "bounded investigation", "previous_state": None,
                                                               "new_state": "OPEN"})

    def transition(self, qid="TECH-001", target="ASSUMED", severity="Important"):
        return harness.append(self.path, "QUESTION_STATE_CHANGED", {"question_id": qid,
                                                                       "requirement_ref": "R-1", "severity": severity,
                                                                       "new_state": target})

    def test_append_only_sequence_and_query(self):
        self.question()
        self.transition()
        records = harness.history(self.path)
        self.assertEqual([1, 2], [x["sequence"] for x in records])
        self.assertEqual("ASSUMED", harness.query(self.path, "question", "TECH-001")["state"])
        self.assertEqual("QUESTION_CREATED", records[0]["type"])

    def test_invalid_transition_rejected_and_recorded(self):
        self.question()
        self.transition()
        code = harness.cli(["--root", str(self.root), "question-transition", "--run-id", "smoke",
                            "--id", "TECH-001", "--state", "ANSWERED"])
        self.assertEqual(1, code)
        self.assertEqual("STATE_TRANSITION_REJECTED", harness.history(self.path)[-1]["type"])
        self.assertEqual("ASSUMED", harness.question_state(harness.history(self.path), "TECH-001"))

    def test_assumption_requires_assumed_question(self):
        self.question()
        fields = {"assumption_id": "ASSUM-001", "origin_question_id": "TECH-001", "content": "display only",
                  "default_behavior": "retain order", "impact": "one view", "confidence": "medium"}
        with self.assertRaises(ValueError):
            harness.append(self.path, "ASSUMPTION_CREATED", fields)
        self.transition()
        made = harness.append(self.path, "ASSUMPTION_CREATED", fields)
        self.assertEqual("ISOLATED", made["state"])
        self.assertEqual("TECH-001", harness.query(self.path, "assumption", "ASSUM-001")["history"][0]["origin_question_id"])

    def test_task_routing_and_order_evidence(self):
        created = harness.append(self.path, "TASK_CREATED", {"task_id": "N-TASK-001", "requirement_ref": "R-ready",
                                                                "scope": ["one.py"], "priority": "P1"})
        routed = harness.append(self.path, "TASK_ROUTING_SET", {"task_id": "N-TASK-001", "routing": "MODERATE",
                                                                   "reason": "two local call sites"})
        self.assertEqual("MODERATE", harness.query(self.path, "task", "N-TASK-001")["routing"])
        self.runtime(row("session-1", "assistant", use("Bash", "b1")),
                     row("session-1", "user", result("b1", created["event_id"])),
                     row("session-1", "assistant", use("Bash", "b2")),
                     row("session-1", "user", result("b2", routed["event_id"])),
                     row("session-1", "assistant", use("Edit", "e1", {"file_path": "one.py"})),
                     row("session-1", "user", result("e1")))
        harness.seal(self.path)
        self.assertEqual("BEFORE_EDIT", harness.inspect_order(self.path)["order"])

    def test_edit_before_task_is_visible(self):
        self.runtime(row("session-1", "assistant", use("Edit", "e1")), row("session-1", "user", result("e1")))
        created = harness.append(self.path, "TASK_CREATED", {"task_id": "T-1", "requirement_ref": "R", "scope": ["x"], "priority": "P1"})
        routed = harness.append(self.path, "TASK_ROUTING_SET", {"task_id": "T-1", "routing": "MODERATE", "reason": "local"})
        self.runtime(row("session-1", "assistant", use("Bash", "b1")), row("session-1", "user", result("b1", created["event_id"])),
                     row("session-1", "assistant", use("Bash", "b2")), row("session-1", "user", result("b2", routed["event_id"])))
        harness.seal(self.path)
        self.assertEqual("AFTER_EDIT", harness.inspect_order(self.path)["order"])

    def test_gate_pending_and_human_answer_provenance(self):
        self.question("PD-001", "Critical")
        self.runtime(row("session-1", "assistant", use("AskUserQuestion", "gate-1", {"questions": ["Approve?"]})))
        observation = harness.gate_observe(self.path, "PD-001", 0.1, 0.01)
        self.assertEqual("pending", observation["status"])
        self.transition("PD-001", "BLOCKED", "Critical")
        self.assertEqual("pending", harness.query(self.path, "gate", "gate-1")["state"])
        self.runtime(row("session-1", "user", result("gate-1", "Human selected No"), {"Approve?": "No"}))
        answered = harness.gate_status(self.path, "gate-1")
        self.assertEqual("GATE_ANSWERED", answered["type"])
        self.assertEqual("answered", harness.query(self.path, "gate", "gate-1")["state"])
        with self.assertRaises(ValueError):
            harness.append(self.path, "GATE_ANSWERED", {"gate_id": "gate-1", "answer": "Agent says yes"})

    def test_gate_cannot_be_agent_authored(self):
        self.question("PD-001", "Critical")
        with self.assertRaises(ValueError):
            harness.append(self.path, "GATE_ANSWERED", {"gate_id": "fake", "answer": "yes"})
        with self.assertRaises(TimeoutError):
            harness.gate_observe(self.path, "PD-001", 0, 0.01)

    def test_gate_tool_error_is_not_human_answer(self):
        self.question("PD-001", "Critical")
        self.runtime(row("session-1", "assistant", use("AskUserQuestion", "gate-err")))
        harness.gate_observe(self.path, "PD-001", 0.1, 0.01)
        self.runtime(row("session-1", "user", result("gate-err", "rate limit", True)))
        with self.assertRaises(RuntimeError):
            harness.gate_status(self.path, "gate-err")
        self.assertEqual("pending", harness.query(self.path, "gate", "gate-err")["state"])
        self.assertEqual("INCOMPLETE", harness.seal(self.path)["capture_status"])

    def test_unanswered_gate_can_be_sealed_without_inventing_answer(self):
        self.question("PD-001", "Critical")
        self.runtime(row("session-1", "assistant", use("AskUserQuestion", "gate-pending")))
        harness.gate_observe(self.path, "PD-001", 0.1, 0.01)
        manifest = harness.seal(self.path)
        self.assertEqual("COMPLETE_WITHIN_BOUNDARY", manifest["capture_status"])
        self.assertEqual(["gate-pending"], manifest["runtime_inventory"]["unmatched_gate_ids"])
        self.assertTrue(harness.verify(self.path)["valid_package"])

    def test_forged_answer_event_fails_independent_package_check(self):
        self.question("PD-001", "Critical")
        self.runtime(row("session-1", "assistant", use("AskUserQuestion", "gate-pending")))
        harness.gate_observe(self.path, "PD-001", 0.1, 0.01)
        harness.append(self.path, "GATE_ANSWERED", {"gate_id": "gate-pending", "answer": {"q": "agent says yes"},
                                                      "watermark": self.source.stat().st_size})
        harness.seal(self.path)
        self.assertFalse(harness.verify(self.path)["valid_package"])

    def test_capture_incomplete_and_hash(self):
        self.runtime(row("session-1", "assistant", use("Read", "missing-result")))
        manifest = harness.seal(self.path)
        self.assertEqual("INCOMPLETE", manifest["capture_status"])
        self.assertIn("missing-result", manifest["runtime_inventory"]["unmatched_other_ids"])
        self.assertTrue(harness.verify(self.path)["valid_package"])
        self.assertEqual(harness.sha((self.path / "runtime.jsonl").read_bytes()), manifest["runtime_sha256"])
        (self.path / "runtime.jsonl").write_bytes(b"changed")
        self.assertFalse(harness.verify(self.path)["valid_package"])

    def test_claim_is_not_trusted(self):
        self.runtime(row("session-1", "assistant", use("Read", "r1")), row("session-1", "user", result("r1")))
        harness.seal(self.path)
        (self.path / "evidence.md").write_text("PASS; Human approved", encoding="utf-8")
        self.assertFalse(harness.verify(self.path)["claim_is_trusted_evidence"])

    def test_source_prefix_mutation_marks_incomplete(self):
        self.source.write_bytes(harness.encoded(row("session-1", "assistant", use("Read", "before"))))
        other = self.root / "RUN-other"
        harness.start(self.root, "other", "CAPABILITY", "session-1", self.source)
        self.source.write_bytes(harness.encoded(row("session-1", "assistant", use("Edit", "changed"))))
        self.assertEqual("INCOMPLETE", harness.seal(other)["capture_status"])

    def test_metadata_regression_a_valid_session_event(self):
        self.runtime(row("session-1", "assistant", use("Read", "r1")), row("session-1", "user", result("r1")))
        self.assertEqual("COMPLETE_WITHIN_BOUNDARY", harness.seal(self.path)["capture_status"])

    def test_metadata_regression_b_sessionless_metadata_row_stays_complete(self):
        self.runtime({"type": "file-history-snapshot", "messageId": "m1", "snapshot": {}},
                     row("session-1", "assistant", use("Read", "r1")), row("session-1", "user", result("r1")),
                     {"type": "file-history-delta", "messageId": "m2"})
        manifest = harness.seal(self.path)
        self.assertEqual("COMPLETE_WITHIN_BOUNDARY", manifest["capture_status"])
        self.assertEqual(2, manifest["runtime_inventory"]["non_session_metadata_rows"])
        verdict = harness.verify(self.path)
        self.assertTrue(verdict["valid_package"])
        self.assertEqual([], verdict["issues"])

    def test_metadata_regression_c_wrong_session_still_fails(self):
        self.runtime(row("other-session", "assistant", use("Read", "r1")), row("other-session", "user", result("r1")))
        manifest = harness.seal(self.path)
        self.assertEqual("INCOMPLETE", manifest["capture_status"])
        self.assertTrue(any("session mismatch" in g for g in manifest["capture_gaps"]))

    def test_metadata_regression_d_unpaired_event_still_fails_beside_metadata(self):
        self.runtime({"type": "file-history-snapshot", "messageId": "m1"}, row("session-1", "assistant", use("Read", "r1")))
        self.assertEqual("INCOMPLETE", harness.seal(self.path)["capture_status"])

    def test_sessionless_non_allowlisted_or_tool_bearing_row_fails_closed(self):
        unknown = {"type": "mystery", "message": {"content": []}}
        sneaky = {"type": "file-history-snapshot", "message": {"content": [use("Bash", "x1")]}}
        no_session_assistant = {"type": "assistant", "message": {"content": [use("Read", "y1")]}}
        for item in (unknown, sneaky, no_session_assistant):
            rows = [item]
            self.assertTrue(any("unattributable" in g for g in harness.inventory(rows, "session-1")["gaps"]), item)

    def chain(self):
        self.question()
        self.transition()
        harness.append(self.path, "ASSUMPTION_CREATED", {"assumption_id": "AS-1", "origin_question_id": "TECH-001",
                                                         "content": "c", "default_behavior": "d", "impact": "i", "confidence": "m"})

    def task(self, tid="T-1", deps=(), priority="P1"):
        return harness.append(self.path, "TASK_CREATED", {"task_id": tid, "requirement_ref": "R-1", "scope": ["x"],
                                                          "priority": priority, "assumption_deps": list(deps)})

    def cli(self, *args):
        return harness.cli(["--root", str(self.root), *args])

    def test_chain_question_assumed_assumption_isolated(self):
        self.chain()
        self.assertEqual("ASSUMED", harness.query(self.path, "question", "TECH-001")["state"])
        self.assertEqual("ISOLATED", harness.query(self.path, "assumption", "AS-1")["state"])

    def test_task_without_isolated_dependency_can_be_eligible(self):
        self.task()
        done = harness.task_transition(self.path, "T-1", "ELIGIBLE")
        self.assertEqual("ELIGIBLE", done["new_state"])
        self.assertEqual("ELIGIBLE", harness.query(self.path, "task", "T-1")["state"])

    def test_isolated_dependency_rejects_eligible_and_blocks(self):
        self.chain()
        self.task(deps=["AS-1"])
        self.assertEqual(1, self.cli("task-transition", "--run-id", "smoke", "--id", "T-1", "--state", "ELIGIBLE"))
        items = harness.history(self.path)
        self.assertEqual("STATE_TRANSITION_REJECTED", items[-2]["type"])
        self.assertEqual("BLOCKED", harness.query(self.path, "task", "T-1")["state"])
        self.assertFalse(any(e["type"] == "TASK_STATE_CHANGED" and e["new_state"] == "ELIGIBLE" for e in items))

    def test_p2_task_cannot_be_eligible(self):
        self.task(priority="P2")
        with self.assertRaises(ValueError):
            harness.task_transition(self.path, "T-1", "ELIGIBLE")

    def test_unknown_assumption_dependency_rejected(self):
        with self.assertRaises(ValueError):
            self.task(deps=["AS-missing"])
        self.assertIsNone(harness.query(self.path, "task", "T-1")["state"])

    def test_blocked_task_cannot_become_eligible_later(self):
        self.chain()
        self.task(deps=["AS-1"])
        self.cli("task-transition", "--run-id", "smoke", "--id", "T-1", "--state", "ELIGIBLE")
        self.assertEqual(1, self.cli("task-transition", "--run-id", "smoke", "--id", "T-1", "--state", "ELIGIBLE"))
        self.assertEqual("BLOCKED", harness.query(self.path, "task", "T-1")["state"])

    def test_transition_of_absent_task_rejected(self):
        self.assertEqual(1, self.cli("task-transition", "--run-id", "smoke", "--id", "T-none", "--state", "ELIGIBLE"))
        self.assertEqual("STATE_TRANSITION_REJECTED", harness.history(self.path)[-1]["type"])

    def test_inspect_order_recognizes_powershell_receipts(self):
        created = self.task()
        routed = harness.append(self.path, "TASK_ROUTING_SET", {"task_id": "T-1", "routing": "MODERATE", "reason": "local"})
        self.runtime(row("session-1", "assistant", use("PowerShell", "p1")), row("session-1", "user", result("p1", created["event_id"])),
                     row("session-1", "assistant", use("PowerShell", "p2")), row("session-1", "user", result("p2", routed["event_id"])),
                     row("session-1", "assistant", use("Edit", "e1")), row("session-1", "user", result("e1")))
        harness.seal(self.path)
        self.assertEqual("BEFORE_EDIT", harness.inspect_order(self.path)["order"])

    def test_verify_tolerates_string_tool_use_result(self):
        self.runtime(row("session-1", "assistant", use("PowerShell", "p1")))
        failed = row("session-1", "user", result("p1", "exit 1", True))
        failed["toolUseResult"] = "Error: Exit code 1"
        self.runtime(failed)
        harness.seal(self.path)
        self.assertTrue(harness.verify(self.path)["valid_package"])


if __name__ == "__main__":
    unittest.main()
