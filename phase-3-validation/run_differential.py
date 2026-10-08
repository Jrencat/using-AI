"""Phase 3 Step 4 runner: executes old chain_verifier and new validator on the locked corpus.

Records raw results only; classification is done separately. Read-only with respect to all inputs.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(r"D:\renjianxiao\using-AI")
EXPECTED = Path(r"D:\phase3-pre-registered\expected\expected.json")
OLD = REPO / "harness/chain_verifier.py"
NEW = Path(r"D:\phase3-iso\validator.py")
LOCK = REPO / "docs/architecture/phase-3/negative-corpus-record.json"
OUT = REPO / "phase-3-validation" / (sys.argv[1] if len(sys.argv) > 1 else "differential-results-v1.json")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


lock = json.loads(LOCK.read_text(encoding="utf-8"))
assert sha(EXPECTED) == lock["expected_sha256"], "expected.json changed"
cases = json.loads(EXPECTED.read_text(encoding="utf-8"))["cases"]
real = str(REPO / "docs/architecture/phase-3/external-digest-record.json")


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    try:
        out = json.loads(p.stdout)
    except Exception:
        out = None
    return {"exit": p.returncode, "json": out, "stdout": p.stdout[-1500:] if out is None else None,
            "stderr": p.stderr[-800:]}


results = []
for c in cases:
    claims = json.loads(Path(c["claims"]).read_text()) if c["claims"] else {}
    old_cmd = [sys.executable, "-I", str(OLD), c["package"]]
    for k, v in claims.items():
        old_cmd += ["--claim", f"{k}={v}"]
    new_cmd = [sys.executable, "-I", str(NEW), "--package", c["package"]]
    if c["digest_record"]:
        new_cmd += ["--digest-record", c["digest_record"]]
    else:
        new_cmd += ["--digest-record", str(Path(r"D:\phase3-pre-registered") / "no-such-digest-record.json")]
    if c["claims"]:
        new_cmd += ["--claims", c["claims"]]
    digest_type = ("NONE" if not c["digest_record"] else "HUMAN_ANCHORED_DIGEST" if c["digest_record"] == real
                   else "TEST_FIXTURE_DIGEST")
    results.append({"case": c["case"], "digest_type": digest_type, "expected": c["expected"],
                    "old": run(old_cmd), "new": run(new_cmd)})

OUT.write_text(json.dumps({"validator_sha256": sha(NEW), "old_verifier_sha256": sha(OLD),
                           "expected_sha256": sha(EXPECTED), "results": results}, indent=1) + "\n", encoding="utf-8")
for r in results:
    o = (r["old"]["json"] or {}).get("verdict", "ERR")
    n = (r["new"]["json"] or {}).get("verdict", "ERR")
    print(f'{r["case"]:5} {r["digest_type"]:22} exp={r["expected"]:21} old={o:21} new={n}')
