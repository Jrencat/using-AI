# Phase 5 P5-1 Closeout — Codex Receipt Adapter (offline)

```text
P5-1:            ACCEPTED — OFFLINE SCOPE   (accepted by the Human)
PHASE 5:         NOT complete. P5-2 / P5-3 / P5-4 not authorized or started.
REAL CODEX RUN:  NOT EXECUTED (no Codex quota at the time). Offline results are not a real-run result.
PROTOCOL / HARNESS / PHASE 4 ARTIFACTS: unchanged
```

Source analysis: `phase-5-boundary-analysis.md` (P5-1 recommended there). Phase 4 formal closure remains a separate Human Gate decision.

## 1. Deliverables

| Item | Path |
|---|---|
| Mapping contract v1 (locked) | `docs/architecture/phase-5/codex-receipt-mapping.md` |
| Pre-registered expectations: 26 cases (5 positive, 21 negative), written before the adapter | `docs/architecture/phase-5/codex-receipt-preregistration.json` |
| Lock (hashes of spec, registry, 25 fixtures; `adapter_present_at_lock: false`) | `docs/architecture/phase-5/codex-receipt-lock.json` |
| Adapter, lock tool, tests, fixtures | `phase-5-validation/codex_receipt/` |

Locked hashes (SHA-256 over bytes with CRLF normalized to LF), as recorded in the lock file:

```text
codex-receipt-mapping.md              cb7c2f8fbfdd710f2ef5093c0042f7381e0b7885be29790aab2eff5911e229e1
codex-receipt-preregistration.json    f6bb395f6c6433883418e0d6369b644ec353a4ab583257e6ec1b2535b8b77f25
fixtures (25): see codex-receipt-lock.json
```

Do not edit the locked files. A change needs a new lock id, a new registry id and a Human decision.

## 2. Adapter in one paragraph

`python -I phase-5-validation/codex_receipt/codex_receipt_adapter.py --input SESSION.jsonl --out-dir DIR [--emit-partial]`. Reads one Codex session JSONL read-only; writes `provenance.json` always, `runtime.jsonl` only when status is `COMPLETE`, and `runtime.partial.jsonl` only with `--emit-partial` on an `INCOMPLETE` result whose session id is determined. Exit `0` COMPLETE, `2` INCOMPLETE, `1` usage/I-O error. Standalone (no import of `harness.py`); no network, clock or randomness; output is byte-deterministic. Each emitted row carries `origin.raw_line` and `origin.raw_line_sha256`; the sidecar adds a per-row SHA-256. Gaps are a closed code set in the mapping spec section 4.

## 3. Test and acceptance record (as reported by the Human-accepted execution; not re-run for this archive)

- Command: `python -I -m unittest discover -s phase-5-validation/codex_receipt -p "test_*.py"` — 11 tests, all passed.
- Covered: lock integrity; 26/26 pre-registered cases; CLI exit codes and withholding of `runtime.jsonl`; byte determinism; traceability to raw-line hashes; CRLF/LF equivalence; input not modified; no network-related imports; Harness black box (`start`, `seal`, `verify` in a temporary root, no Agent) on 7 registered cases.

| Check | Result | Limit |
|---|---|---|
| Mapping contract explicit and limited | PASS | fields from structural observation only |
| Negatives registered and locked before the adapter | PASS | same author |
| Adapter independent, Harness unchanged | PASS | |
| Same input -> identical bytes | PASS | also 112/112 on local real sessions (structural check) |
| Call/output pairing, gaps explicit | PASS | |
| Source traceability, unsafe input handled | PASS | |
| Negatives match; Harness black box accepts | PASS, limited | synthetic fixtures only; no real Codex run |

## 4. Findings and limits

- The Harness cannot see adapter-level gaps (an unknown record is simply absent from the rows), so a gapped `runtime.jsonl` could be sealed as `COMPLETE_WITHIN_BOUNDARY`. Hence `runtime.jsonl` is withheld on any gap (demonstrated by case N01).
- Structural check of 112 local Codex sessions (counts only, no content kept): 78 `COMPLETE`, 34 `INCOMPLETE`, driven by top-level record types not covered by mapping v1 — `token_usage_record` (1673 records, 29 files) and `compacted` (8 records, 7 files) — plus 2 files with unanswered calls. Mapping v1 was **not** loosened to fit; whether these records are benign is unresolved (`compacted` may hide earlier tool calls).
- Compatibility is limited to the record structure observed locally (Codex CLI about 0.161.0). `is_error`, streaming and multi-modal output are unsupported.
- Not shown: any real Codex run, that a real Codex run passes the C1 chain, Independent Verification, FX-BLOCKED, repeat runs.

## 5. H1: local classification of adapter output (recommended for P5-1 products only)

- The raw Codex session file and the adapter's normalized output are different evidence objects. The normalized output is a tool-derived artifact: it must be read together with its source hash, adapter version and mapping version (all in `provenance.json`).
- Being shaped like `runtime.jsonl` does not make it Codex-native Runtime output.
- Recommended tier for adapter output: **`TOOL_GENERATED`** (an external deterministic tool, `protocol.md` section 5.6), explicitly **not** `RUNTIME_GENERATED`.
- Scope: this classifies P5-1 products only. It is not a change to the Protocol or to any Contract, and not a global evidence-classification ruling. No conflict with the frozen text was found (`TOOL_GENERATED` is already defined as tool-produced evidence). Whether such rows may support a C1 run claim is decided before P5-2 is judged.

## 6. Adapter principles (kept here, not copied into other rule files)

1. A converted artifact must not pose as native Runtime evidence.
2. A converter keeps source hash, converter version and mapping version.
3. Negatives are registered and locked before the converter is written; expectations are not edited to match results.
4. Unknown records and unpaired calls or outputs are never dropped silently.
5. Incomplete input must not yield an artifact that looks complete.
6. Offline compatibility tests are not real-Agent verification.
7. A frozen contract or locked expectation is not changed to make a test pass.
8. Reports separate verified facts, reasonable inference and unverified assumptions.

These were not added to `docs/ai-collaboration/CHATGPT_COLLABORATION_RULES.md` (its scope is how ChatGPT chooses tasks and reviews results; items 6 and 8 are already covered by its sections 2 and 5) and not to `CLAUDE.md`/`AGENTS.md` (template and environment rules).

## 7. Open items and next step

- Decide whether a **mapping v2** (new version, new lock, no edit to v1) is worth doing before any real run: classify `token_usage_record`, investigate `compacted`.
- Human rulings still pending: H1 confirmation, H2 (authorize P5-2 and Codex quota), H3 (formally close Phase 4), H4 (P5-3 / P5-4).
- P5-2 (one real Codex FX-ELIGIBLE run) is **not authorized**. Under mapping v1 a current real session would likely be `INCOMPLETE`, so authorizing it first is not recommended.
