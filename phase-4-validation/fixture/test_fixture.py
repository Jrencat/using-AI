"""Local consistency tests for the C1 fixture. Not a verification run: no Agent, no live run.

    python -I phase-4-validation/fixture/test_fixture.py
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import manifest_tool  # noqa: E402
import scope_checker  # noqa: E402

WS = os.path.join(HERE, "workspace")
FX = json.load(open(os.path.join(HERE, "fixture.json"), encoding="utf-8"))


def manifest(root, kind="BASELINE"):
    return manifest_tool.build_manifest(root, kind, "R", "W", "2026-01-01T00:00:00Z")


def entries(root):
    return {e["path"]: e["sha256"] for e in manifest_tool.collect(root)}


class FixtureTests(unittest.TestCase):
    def test_workspace_has_no_symlink_and_no_stray_files(self):
        got = manifest_tool.collect(WS)
        self.assertTrue(all(e["type"] == "file" for e in got))
        self.assertEqual([e["path"] for e in got],
                         ["README.txt", "docs/notes.txt", "src/calc.py", "src/report.py", "src/util.py"])

    def test_baseline_is_reproducible_and_checker_well_formed(self):
        a = manifest_tool.serialize(manifest(WS))
        b = manifest_tool.serialize(manifest(WS))
        self.assertEqual(a, b)
        rep = scope_checker.Report()
        self.assertIsNotNone(scope_checker.check_manifest("baseline", "BASELINE", manifest(WS), rep))
        self.assertEqual(rep.findings, [])

    def test_task_scopes_satisfy_contract_preconditions(self):
        paths = set(entries(WS))
        seen = []
        for tid, t in FX["tasks"].items():
            self.assertTrue(t["scope"], tid)
            for p in t["scope"]:
                self.assertTrue(scope_checker.scope_path_valid(p), p)
                self.assertIn(p, paths)  # names an existing file; no file ancestor (SC-P8)
                self.assertNotIn(p.casefold(), [s.casefold() for s in seen])  # disjoint, no casefold clash
                seen.append(p)
            self.assertIn(t["priority"], ("P0", "P1", "P2"))

    def test_scenarios_satisfy_single_eligible_rule(self):
        for name, sc in FX["scenarios"].items():
            states = [t["expected_final_state"] for t in sc["anchor_tasks"]]
            self.assertLessEqual(states.count("ELIGIBLE"), 1, name)
            for t in sc["anchor_tasks"]:
                task = FX["tasks"][t["task_id"]]
                if t["expected_final_state"] == "ELIGIBLE":
                    self.assertIn(task["priority"], ("P0", "P1"), name)  # SC-P6
                else:
                    self.assertTrue(task["priority"] == "P2" and task.get("assumption_dep"), name)
            allowed = {p for t in sc["anchor_tasks"] if t["expected_final_state"] == "ELIGIBLE"
                       for p in FX["tasks"][t["task_id"]]["scope"]}
            self.assertEqual(set(sc["admissible_delta"]), allowed, name)  # SC-A1: Allowed is never a union

    def test_in_scope_edit_vs_decoy_edit_on_a_copy(self):
        d = tempfile.mkdtemp(prefix="c1-fx-")
        try:
            base = entries(WS)
            root = os.path.join(d, "w")
            shutil.copytree(WS, root)
            with open(os.path.join(root, "src", "calc.py"), "ab") as fh:
                fh.write(b"\ndef subtract(a, b):\n    return a - b\n")
            after = entries(root)
            changed = {p for p in set(base) | set(after) if base.get(p) != after.get(p)}
            self.assertEqual(changed, {"src/calc.py"})
            with open(os.path.join(root, "src", "util.py"), "ab") as fh:
                fh.write(b"# x\n")
            changed = {p for p in set(base) | set(entries(root)) if base.get(p) != entries(root).get(p)}
            self.assertEqual(changed - set(FX["scenarios"]["FX-ELIGIBLE"]["admissible_delta"]), {"src/util.py"})
        finally:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=1)
