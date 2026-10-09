"""Write the pre-registration lock for the Codex receipt mapping (P5-1).

Hashes the mapping spec, the pre-registered expectations and every fixture, and refuses to overwrite an
existing lock. SHA-256 is taken over the bytes with CRLF normalized to LF so that an autocrlf checkout
does not change the recorded values. Run once, before the adapter exists.
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "docs/architecture/phase-5/codex-receipt-mapping.md"
REGISTRY = ROOT / "docs/architecture/phase-5/codex-receipt-preregistration.json"
LOCK = ROOT / "docs/architecture/phase-5/codex-receipt-lock.json"
FIXTURES = ROOT / "phase-5-validation/codex_receipt/fixtures"
ADAPTER = ROOT / "phase-5-validation/codex_receipt/codex_receipt_adapter.py"


def digest(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def rel(path):
    return path.relative_to(ROOT).as_posix()


def build():
    return {
        "lock_id": "CODEX-RECEIPT-LOCK-V1",
        "mapping_version": 1,
        "hash_rule": "SHA-256 over file bytes with CRLF normalized to LF",
        "adapter_present_at_lock": ADAPTER.exists(),
        "locked_at": datetime.now(timezone.utc).isoformat(),
        "rule": "Changing a locked file after the adapter exists requires a new lock id, a new registry id and a Human decision.",
        "files": {rel(p): digest(p) for p in [SPEC, REGISTRY, *sorted(FIXTURES.glob("*.jsonl"))]},
    }


def main():
    if LOCK.exists():
        print("lock already exists; refusing to overwrite", file=sys.stderr)
        return 1
    LOCK.write_bytes((json.dumps(build(), indent=2) + "\n").encode())
    print("wrote", rel(LOCK))
    return 0


if __name__ == "__main__":
    sys.exit(main())
