"""Local tool tests for the C1 tools. Not a verification run: no Agent, no fixture, no live run.

    python -I phase-4-validation/test_tools.py
"""
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import manifest_tool  # noqa: E402
import run_corpus  # noqa: E402
import scope_checker  # noqa: E402

PHASE4 = os.path.join(os.path.dirname(HERE), "docs", "architecture", "phase-4")


class ManifestToolTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="c1-mt-")
        for rel, data in (("b.txt", b"b"), ("a/z.py", b"z"), ("a/y.py", b"y"), ("__pycache__/x.pyc", b"x")):
            p = os.path.join(self.root, *rel.split("/"))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "wb") as fh:
                fh.write(data)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_entries_sorted_hashed_and_no_ignore_list(self):
        e = manifest_tool.collect(self.root)
        self.assertEqual([x["path"] for x in e], ["__pycache__/x.pyc", "a/y.py", "a/z.py", "b.txt"])
        self.assertEqual(e[2]["sha256"], hashlib.sha256(b"z").hexdigest())
        self.assertTrue(all(set(x) == {"path", "type", "sha256"} and x["type"] == "file" for x in e))

    def test_deterministic_bytes(self):
        a = manifest_tool.serialize(manifest_tool.build_manifest(self.root, "BASELINE", "R", "W", "2026-01-01T00:00:00Z"))
        b = manifest_tool.serialize(manifest_tool.build_manifest(self.root, "BASELINE", "R", "W", "2026-01-01T00:00:00Z"))
        self.assertEqual(a, b)

    def test_symlink_recorded_not_followed(self):
        link = os.path.join(self.root, "link.txt")
        try:
            os.symlink(os.path.join(self.root, "b.txt"), link)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation not permitted here")
        e = {x["path"]: x for x in manifest_tool.collect(self.root)}
        self.assertEqual(e["link.txt"]["type"], "symlink")

    def test_post_requires_bound_to(self):
        with self.assertRaises(ValueError):
            manifest_tool.build_manifest(self.root, "POST", "R", "W", "2026-01-01T00:00:00Z")

    def test_output_is_well_formed_for_the_checker(self):
        rep = scope_checker.Report()
        obj = manifest_tool.build_manifest(self.root, "BASELINE", "R", "W", "2026-01-01T00:00:00Z")
        self.assertIsNotNone(scope_checker.check_manifest("baseline", "BASELINE", obj, rep))
        self.assertEqual(rep.findings, [])

    def test_refuses_overwrite(self):
        out = os.path.join(self.root, "..", "c1-mt-out.json")
        open(out, "wb").close()
        try:
            self.assertEqual(manifest_tool.main(["--root", self.root, "--kind", "BASELINE", "--run-id", "R", "--out", out]), 2)
        finally:
            os.remove(out)


class GrammarTests(unittest.TestCase):
    def test_scope_paths(self):
        ok = ["src/a.py", "README.txt", "a-b_c.d/e"]
        bad = ["", "/a", "a/", "a//b", "./a", "a/./b", "../a", "a/../b", "a\\b", "C:/a", "//s/a", "a b", "a~1", "\u00e9",
               "a*", "a.", "src/NUL.txt", "com1", "a:stream"]
        for p in ok:
            self.assertTrue(scope_checker.scope_path_valid(p), p)
        for p in bad:
            self.assertFalse(scope_checker.scope_path_valid(p), p)

    def test_manifest_path_form_is_not_scope_grammar(self):
        for p in ["docs/read me.txt", "src/\u00e9.py", "C:/foo.py"]:
            self.assertTrue(scope_checker.manifest_path_ok(p), p)
        for p in ["src\\foo.py", "../foo.py", "/foo.py", "a//b", "a/./b", ""]:
            self.assertFalse(scope_checker.manifest_path_ok(p), p)


class RunnerTests(unittest.TestCase):
    def test_builder_does_not_import_checker_or_expected(self):
        src = open(os.path.join(HERE, "build_corpus.py"), encoding="utf-8").read()
        self.assertNotIn("import scope_checker", src)
        self.assertNotIn("expected_verdict", src)

    def test_runner_refuses_a_modified_corpus(self):
        d = tempfile.mkdtemp(prefix="c1-rc-")
        try:
            corpus = json.load(open(os.path.join(PHASE4, "c1-negative-corpus-v3.json"), encoding="utf-8"))
            corpus["cases"][0]["expected_verdict"] = "PASS" if corpus["cases"][0]["expected_verdict"] != "PASS" else "FAIL"
            p = os.path.join(d, "tampered.json")
            with open(p, "w", encoding="utf-8") as fh:
                json.dump(corpus, fh)
            self.assertEqual(run_corpus.main(["--corpus", p]), 2)
        finally:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=1)
