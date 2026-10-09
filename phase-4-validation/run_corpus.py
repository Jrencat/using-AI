"""C1 corpus runner: builds the cases of a locked corpus, runs scope_checker.py on each,
and compares the checker's verdict with the corpus's pre-registered expected verdict.

It never edits expected verdicts. It refuses to run if the corpus no longer matches
the canonical hash in its record. Exit code: 0 all cases match, 1 any mismatch/error,
2 usage or lock failure.

    python -I run_corpus.py [--corpus FILE] [--record FILE] [--results FILE] [--keep DIR]
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PHASE4 = os.path.join(REPO, "docs", "architecture", "phase-4")
sys.path.insert(0, HERE)
import build_corpus  # noqa: E402  (same directory; builder does not import the checker)


def canonical_sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")).hexdigest()


def run_checker(entry):
    cmd = [sys.executable, "-I", os.path.join(HERE, "scope_checker.py"),
           "--anchor-pre", entry["anchor_pre"], "--baseline", entry["baseline"], "--post", entry["post"],
           "--package", entry["package"], "--anchor-post", entry["anchor_post"]]
    if "claims" in entry:
        cmd += ["--claims", entry["claims"]]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if p.returncode != 0:
        return None, "checker exit %d: %s" % (p.returncode, p.stderr.strip()[-300:])
    try:
        return json.loads(p.stdout), None
    except ValueError:
        return None, "checker output is not JSON"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--corpus", default=os.path.join(PHASE4, "c1-negative-corpus-v3.json"))
    ap.add_argument("--record", default=os.path.join(PHASE4, "c1-negative-corpus-v3-record.json"))
    ap.add_argument("--results", help="write a deterministic results JSON here")
    ap.add_argument("--keep", help="build the case inputs in this (new) directory and keep them")
    a = ap.parse_args(argv)

    with open(a.corpus, "rb") as fh:
        corpus = json.loads(fh.read().decode("utf-8"))
    with open(a.record, "rb") as fh:
        record = json.loads(fh.read().decode("utf-8"))
    got = canonical_sha(corpus)
    if got != record["corpus_canonical_sha256"] or len(corpus["cases"]) != record["case_count"]:
        print("LOCK FAILURE: corpus does not match its record (%s)" % got, file=sys.stderr)
        return 2

    work = a.keep or tempfile.mkdtemp(prefix="c1-corpus-")
    if a.keep and os.path.exists(a.keep):
        print("refusing to write into existing " + a.keep, file=sys.stderr)
        return 2
    try:
        index = build_corpus.build_all(corpus, os.path.join(work, "cases") if not a.keep else a.keep)
        rows, bad = [], 0
        for case in corpus["cases"]:
            res, err = run_checker(index[case["case_id"]])
            actual = res["verdict"] if res else "ERROR"
            ok = actual == case["expected_verdict"]
            bad += not ok
            rows.append({"case_id": case["case_id"], "expected": case["expected_verdict"], "actual": actual,
                         "match": ok, "rules": sorted({f["rule"] + ":" + f["outcome"] for f in (res or {}).get("findings", [])}),
                         "error": err})
        summary = {"corpus_id": corpus["corpus_id"], "corpus_canonical_sha256": got, "cases": len(rows),
                   "matched": len(rows) - bad, "mismatched": bad, "results": rows}
        if a.results:
            with open(a.results, "wb") as fh:
                fh.write((json.dumps(summary, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("utf-8"))
        for r in rows:
            if not r["match"]:
                print("MISMATCH %-6s expected=%-20s actual=%-20s %s %s" % (r["case_id"], r["expected"], r["actual"], r["rules"], r["error"] or ""))
        print("%s: %d/%d match, %d mismatch" % (corpus["corpus_id"], len(rows) - bad, len(rows), bad))
        return 0 if bad == 0 else 1
    finally:
        if not a.keep:
            shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
