"""Local tests of anchor_tool.py. Not a verification run: no Agent, no live run, fake package contents.

    python -I phase-4-validation/test_anchor.py
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import anchor_tool  # noqa: E402
import manifest_tool  # noqa: E402
import scope_checker  # noqa: E402

FIXTURE = os.path.join(HERE, "fixture")
FX_JSON = os.path.join(FIXTURE, "fixture.json")


class AnchorTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="c1-an-")
        self.ws = os.path.join(self.d, "workspace")
        shutil.copytree(os.path.join(FIXTURE, "workspace"), self.ws)
        self.human = os.path.join(self.d, "human")
        os.makedirs(self.human)
        self.pkg = os.path.join(self.d, "pkg")
        os.makedirs(self.pkg)
        for n in anchor_tool.PACKAGE_FILES:
            with open(os.path.join(self.pkg, n), "wb") as fh:
                fh.write(("fake " + n).encode())
        self.b1, self.b2, self.post = (os.path.join(self.human, n) for n in ("b1.json", "b2.json", "post.json"))
        base = manifest_tool.serialize(manifest_tool.build_manifest(self.ws, "BASELINE", "R1", "W", "2026-01-01T00:00:00Z"))
        for p in (self.b1, self.b2):
            with open(p, "wb") as fh:
                fh.write(base)
        bound = {"manifest_sha256": "0" * 64, "events_sha256": "0" * 64, "session_id": "S1"}
        with open(self.post, "wb") as fh:
            fh.write(manifest_tool.serialize(manifest_tool.build_manifest(self.ws, "POST", "R1", "W", "2026-01-01T00:00:00Z", bound)))

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def pre(self, out="A.json", scenario="FX-ELIGIBLE", b2=None, ws=None):
        return anchor_tool.main(["pre", "--run-id", "R1", "--workspace-root", ws or self.ws, "--baseline", self.b1,
                                 "--baseline-repeat", b2 or self.b2, "--fixture", FX_JSON, "--scenario", scenario,
                                 "--out", os.path.join(self.human, out)])

    def post_args(self, out="Z.json", pkg=None):
        return ["post", "--run-id", "R1", "--session-id", "S1", "--post", self.post, "--package", pkg or self.pkg,
                "--out", os.path.join(self.human, out)]

    def load(self, name):
        return json.load(open(os.path.join(self.human, name), encoding="utf-8"))

    def test_pre_anchor_content(self):
        self.assertEqual(self.pre(), 0)
        A = self.load("A.json")
        self.assertEqual(A["recorded_by"], "Human")
        self.assertEqual(A["baseline_manifest"], "b1.json")
        self.assertEqual(A["baseline_sha256"], anchor_tool.sha(open(self.b1, "rb").read()))
        self.assertIs(A["baseline_reproduced_identical"], True)
        self.assertEqual([(t["task_id"], t["priority"], t["scope"], t["expected_final_state"]) for t in A["tasks"]],
                         [("T-CALC", "P0", ["src/calc.py"], "ELIGIBLE"), ("T-REPORT", "P2", ["src/report.py"], "BLOCKED")])
        self.assertEqual(A["workspace_root"], A["observed_root"])

    def test_post_anchor_content(self):
        self.assertEqual(anchor_tool.main(self.post_args()), 0)
        Z = self.load("Z.json")
        self.assertEqual(Z["post_manifest_sha256"], anchor_tool.sha(open(self.post, "rb").read()))
        self.assertEqual(set(Z["package"]), set(anchor_tool.PACKAGE_FILES))
        self.assertEqual(Z["package"]["run.json"], anchor_tool.sha(b"fake run.json"))

    def test_checker_accepts_anchors_on_anchor_rules(self):
        self.assertEqual(self.pre(), 0)
        self.assertEqual(anchor_tool.main(self.post_args()), 0)
        res = scope_checker.check(os.path.join(self.human, "A.json"), self.b1, self.post, self.pkg,
                                  os.path.join(self.human, "Z.json"))
        anchor_rules = ("SC-P", "SC-E2", "SC-D1", "SC-D2", "SC-D3")
        bad = [f for f in res["findings"] if f["rule"].startswith(anchor_rules) or
               (f["rule"] in ("SC-E1", "SC-E5") and "anchor" in f["detail"])]
        self.assertEqual(bad, [])  # other findings are expected: the package here is fake

    def test_pre_refusals(self):
        self.assertEqual(self.pre(), 0)
        self.assertEqual(self.pre(), 2)  # overwrite
        with open(self.b2, "ab") as fh:
            fh.write(b" ")
        self.assertEqual(self.pre(out="A2.json"), 2)  # baselines differ
        self.assertFalse(os.path.exists(os.path.join(self.human, "A2.json")))
        with open(self.b2, "wb") as fh:
            fh.write(open(self.b1, "rb").read())
        self.assertEqual(self.pre(out="A3.json", scenario="NOPE"), 2)
        self.assertEqual(self.pre(out=os.path.join(self.ws, "A.json")), 2)  # out inside workspace
        self.assertEqual(self.pre(out="A4.json", b2=os.path.join(self.d, "missing.json")), 2)

    def test_baseline_inside_workspace_refused(self):
        inside = os.path.join(self.ws, "b.json")
        shutil.copy(self.b1, inside)
        self.b1 = inside
        self.assertEqual(self.pre(), 2)

    def test_post_refusals(self):
        self.assertEqual(anchor_tool.main(self.post_args()), 0)
        self.assertEqual(anchor_tool.main(self.post_args()), 2)  # overwrite
        os.remove(os.path.join(self.pkg, "events.jsonl"))
        self.assertEqual(anchor_tool.main(self.post_args(out="Z2.json")), 2)  # missing package file
        self.assertEqual(anchor_tool.main(self.post_args(out=os.path.join(self.pkg, "Z.json"))), 2)  # out inside package


if __name__ == "__main__":
    unittest.main(verbosity=1)
