"""Human-run: record the Phase 3 External Digest Record (Contract Appendix B).

Run by the Human from the repo root, BEFORE any validator work exists:
    python -I phase-3-validation/record_digests.py
Refuses to overwrite an existing record. Cross-check the printed values with
`certutil -hashfile <file> SHA256` or `sha256sum` yourself.
"""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RUNS = ["PH2-VSC-01", "PH2-QUAL-01"]
FILES = ["run.json", "events.jsonl", "runtime.jsonl", "manifest.json"]
OUT = Path("docs/architecture/phase-3/external-digest-record.json")

if OUT.exists():
    sys.exit(f"refusing to overwrite {OUT}")
record = {"record_version": 1, "recorded_by": "Human",
          "recorded_at": datetime.now(timezone.utc).isoformat(), "packages": {}}
for run in RUNS:
    record["packages"][run] = {
        f: hashlib.sha256(Path("harness/runs", f"RUN-{run}", f).read_bytes()).hexdigest() for f in FILES}
OUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
print(json.dumps(record, indent=2))
