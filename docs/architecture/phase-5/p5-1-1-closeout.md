# Phase 5 P5-1.1 Closeout — Codex Receipt Mapping v2 (offline)

```text
P5-1.1:          ACCEPTED — OFFLINE SCOPE   (closeout prepared after the closing checks in section 8)
PHASE 5:         NOT complete. P5-2 / P5-3 / P5-4 not authorized or started.
REAL CODEX RUN:  NOT EXECUTED. Offline results are not a real-run result. No Independent Verification.
PROTOCOL / HARNESS / CONTRACT / CORPUS / PHASE 4 ARTIFACTS / MAPPING V1: unchanged
```

This is not a Protocol, Harness or Contract change, and it does not mean Phase 5 is complete. Predecessor: `p5-1-closeout.md`. Design record: `mapping-v2-proposal.md`.

## 1. Goal and scope

Question: can `token_usage_record` get an explicit ignore rule without losing the fail-closed boundary, so that mapping v2 can be offered next to v1? Scope: Codex receipt adapter only. Mapping v2 is selected explicitly with `--mapping-version 2`; with no flag the adapter uses v1.

## 2. Files and how they relate

| Item | Path |
|---|---|
| Mapping v2 (locked) | `docs/architecture/phase-5/codex-receipt-mapping-v2.md` |
| Pre-registration `CODEX-RECEIPT-PREREG-V2` (32 cases + v1 regression rule + 2 default-version cases; locked) | `docs/architecture/phase-5/codex-receipt-preregistration-v2.json` |
| Lock `CODEX-RECEIPT-LOCK-V2` (33 files: spec, registry, 31 fixtures; `adapter_v2_present_at_lock: false`; records the pre-change adapter hash `15709ddd…5025e`, equal to the `HEAD` blob of the adapter) | `docs/architecture/phase-5/codex-receipt-lock-v2.json` |
| Synthetic fixtures (31) | `phase-5-validation/codex_receipt/fixtures_v2/` |
| Adapter (`--mapping-version {1,2}`, default 1) | `phase-5-validation/codex_receipt/codex_receipt_adapter.py` |
| v2 tests | `phase-5-validation/codex_receipt/test_codex_receipt_v2.py` |
| Design record, T2 text superseded by T3 | `docs/architecture/phase-5/mapping-v2-proposal.md` |

Order kept: v2 spec, fixtures and registry were written and hash-locked **before** any adapter change; expectations were not edited afterwards. Before locking, the unchanged v1 adapter was used only to check that the fixtures parse. The v2 files are CRLF-normalized SHA-256 as in the v1 lock. Generator and lock scripts were run from a temporary directory and are not in the repo.

## 3. v2 rules (summary)

- `token_usage_record`: ignored and counted iff `payload` is an object, has no array at any depth, string values appear only under the top-level keys `response_id`, `root_turn_id`, `session_id`, `thread_id`, `turn_id` (each, if present, must be a string), and all other leaves are number, boolean or null. Otherwise gap `TOKEN_USAGE_UNEXPECTED_SHAPE`.
- `compacted`: always gap `COMPACTION_PRESENT`; the payload is never parsed and no row is derived from it.
- Unanswered calls (`UNPAIRED_CALL`), orphan outputs, unknown types: unchanged gaps.
- `runtime.jsonl` only when `COMPLETE`; `runtime.partial.jsonl` only with `--emit-partial` on `INCOMPLETE`.

## 4. Basis and limit of T3

- The proposal's T2 (numeric-only leaves) was tested by a structure-only, in-memory probe of the local sessions (key paths, value types, counts; no content kept). Result: 0 of 1673 `token_usage_record` payloads conformed; all had string leaves under exactly the five ID keys above, other leaves were integers, no arrays, and no tool-call/tool-output key appeared. The Human then approved T3 (this allow-list), no `session_id` consistency check, `compacted` fail-closed, unanswered calls fail-closed.
- For `compacted` the probe showed pre-compaction tool records are present in those files, but that cannot prove the history is complete, and 5 of 8 records embed objects carrying a `call_id`. Hence fail-closed.
- **T3 is a finite allow-list for the structure observed locally (Codex CLI about 0.161.0). It is not a Codex schema and is not claimed to hold for other versions.** A different structure fails closed (becomes a gap).
- The probe counts are not re-run for this closeout. The probe was a structural smoke check, not a run validation.

## 5. Results (executed during this work; the final run is in section 8)

| Item | Result |
|---|---|
| Pre-registered v2 cases | **32** cases: Q01–Q06 (6 positive), T01–T19 (19 negative), C01–C07 (7 negative); all match the locked expectations |
| Default-version cases | 2 (D01, D02): no flag selects v1 (`mapping_version` 1, token and compacted are `UNKNOWN_RECORD_TYPE`) |
| v1 regression | all **26** v1 pre-registered cases give the same status, gaps, rows and ignored counts under v2; default and explicit `--mapping-version 1` outputs are byte-identical on all 26 v1 fixtures |
| Test suites | v1 file `test_codex_receipt.py` (**11** tests, unchanged) + v2 file `test_codex_receipt_v2.py` (**15** tests) = **26** tests, all passed |
| Harness black box | **8** registered cases (Q01, Q04, Q05, Q06, T01, T18, C01, C04) through the unchanged `start`/`seal`/`verify` in a temporary root, no Agent: all as registered |
| Also covered | lock integrity, exit codes and `runtime.jsonl` withholding for all 32 cases, byte determinism, CRLF/LF equivalence (Q06 vs Q01), raw-line hash traceability, no row from non-`response_item` records, input not modified, unsupported mapping version rejected |

Counts of cases (32 + 2 + 26 v1 re-run) and counts of tests (26) are different things: the 26 tests iterate over those cases.

## 6. Finding: partial output looks complete to the Harness

The unchanged Harness sealed `runtime.partial.jsonl` of T01 (invalid token payload) and C01 (compacted between a call and its output) as `COMPLETE_WITHIN_BOUNDARY`, because it only sees `tool_use`/`tool_result` rows and cannot see an adapter-level omission. (T18 and C04, which contain an unanswered call, are sealed `INCOMPLETE` by the Harness itself.) This is why `runtime.jsonl` is withheld on any gap, and why a partial file must never be used as complete run evidence.

## 7. Not verified / known limits

- No real Codex run was made; no Codex quota was used. Offline tests on synthetic fixtures are not real-Agent verification.
- No Independent Verification; author of spec, fixtures, adapter and tests is the same.
- Cross-version applicability of T3 is unknown. Synthetic token and compacted fixtures follow the locally observed structure, not real session content.
- `compacted` and unanswered calls stay `INCOMPLETE`; real sessions containing them cannot yield `runtime.jsonl`. The share of local sessions that become `COMPLETE` under v2 was not computed.
- No check that a token record's `session_id` equals the `session_meta` id (Human decision: not added).
- `COMPLETE` means every record was mapped, counted by a stated rule or reported as a gap; it does not mean the Codex session was complete, authorised or error-free. `is_error`, streaming and multi-modal output remain unsupported.

## 8. Evidence classification and closing checks

- Adapter output stays recommended as **`TOOL_GENERATED`**, explicitly not `RUNTIME_GENERATED`; v2 does not raise it. This is the local P5-1 recommendation only (H1 still pending).
- Closing checks before this closeout (no architecture re-audit): v1 mapping, registry, lock and fixtures show no diff against `HEAD`; the v2 lock hashes match the files; the lock's recorded adapter hash equals the pre-change `HEAD` adapter; the full unittest run (26 tests) was repeated and passed. The final run is recorded in the commit report, not edited into this file.

## 9. Open items

- Human rulings still pending: H1 (classification confirmation), H2 (authorize P5-2 and Codex quota), H3 (formally close Phase 4), H4 (P5-3 / P5-4).
- Whether to run P5-2 now: a real session containing `compacted` or an unanswered call would still be `INCOMPLETE`; a short run without them is expected, not shown, to pass. P5-2 is **not** started.
