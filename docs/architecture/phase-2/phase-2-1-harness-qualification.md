# Phase 2.1 — Harness Qualification

```text
PHASE 2.1 FINAL GATE: PASS
Human Verification: DONE (§10)
Protocol Modified: NO
```

## 1. Objective

Answer **U1**: does `Runtime → Start → Capture → Seal → Verify` reach `capture_status=COMPLETE` on a real Claude Code session? Agent behavior is not judged.

## 2. Baseline

- Source: `D:\renjianxiao\phase-1d-execution\harness\` (`harness.py` 475 lines, `test_harness.py`, `README.md`).
- Copied unmodified into the repo first: **13/13 PASS** before any change.
- Git at start: `M CLAUDE.md`, `?? AGENTS.md`, `?? docs/architecture/phase-2/` (untouched by this phase except the new doc).

## 3. Harness Repository Location

`harness/` (`harness.py`, `test_harness.py`, `README.md`, `.gitignore`). Only these three source files were migrated; no fixtures, recovered evidence, or Phase 1D runs. Default run root changed from `../runs` to `harness/runs/` (gitignored — sealed packages contain raw transcript slices; archiving them is a Human decision). Entry point: `python harness/harness.py ...` from the repo root.

## 4. Changes Made

- `harness.py`: `inventory()` session handling (§5); new `non_session_metadata_rows` inventory field; default `--root`.
- `test_harness.py`: +5 tests.
- `harness/.gitignore`: `runs/`, `__pycache__/`.
- No change to `README.md` content (still describes Phase 1D wording and `../runs`; stale, not fixed to avoid scope growth).

## 5. Capture Metadata Fix

Old: any row lacking `sessionId` → `session mismatch`. New, per row:

| Row | Result |
| --- | --- |
| `sessionId == bound` | normal |
| `sessionId != bound` | gap `session mismatch` (unchanged) |
| no `sessionId`, `type ∈ {file-history-snapshot, file-history-delta}` **and** no tool blocks | counted as `non_session_metadata_rows`, not a gap |
| no `sessionId`, any other type, or metadata type carrying tool blocks | gap `unattributable row without sessionId` (fail closed) |

The allowlist was derived from observed real transcripts (only those two types lack `sessionId`).

## 6. Regression Tests

`python harness/test_harness.py` → **18/18 PASS** (13 baseline + 5 new).
- A valid session event → COMPLETE_WITHIN_BOUNDARY
- B valid event + sessionId-less metadata rows → COMPLETE, `verify` valid, `issues=[]`
- C wrong sessionId → INCOMPLETE (`session mismatch`)
- D unpaired event beside metadata → INCOMPLETE
- E unknown type / tool-bearing metadata / sessionId-less assistant row → `unattributable` gap

## 7. PH2-QUAL-01

- New session `42795500-6df5-4dd9-9a5d-143192aea5d8`, cwd = repo, created by `claude -p --session-id` (one no-tool turn), then `start` at a complete-row boundary (offset 168805).
- Live turn (same session via `--resume`): the Agent was told to run two exact harness CLI commands (`question-create`, `query`). Agent text is not evidence.
- Operator ran `seal` then `verify`.

## 8. Runtime Evidence

- Slice `[168805, 183758)`, 13 rows, 2 tool_use / 2 tool_result, all paired, no gaps.
- State log: 1 event (`QUESTION_CREATED`, `c85db43d-…`); that event_id appears in the raw Runtime slice (receipt).
- **Independent re-check** (separate script, not the harness): `end_offset == source size`; source slice byte-equal to `runtime.jsonl`; SHA-256 of slice and prefix both match manifest/run.json.

## 9. Seal / Verify Result

```text
capture_status = COMPLETE_WITHIN_BOUNDARY   (the harness's existing token for COMPLETE; not renamed to keep 13 baseline tests)
valid_package  = true
issues         = []
```

## 10. Human Verification

**DONE (Human).** The Human inspected `harness/runs/RUN-PH2-QUAL-01/runtime.jsonl` and confirmed:

- Runtime spot-check: PASS — two real `tool_use` and two matching `tool_result` rows.
- Harness CLI tool receipts: PASS — the Harness CLI was actually executed.
- `QUESTION_CREATED` receipt: PASS — event_id `c85db43d-3ca0-4e0b-871f-ff7137d92d3f` appears in the Runtime receipt.
- Query receipt: PASS — returns the same event_id, `TECH-001 = OPEN`.
- Event_id correlation: PASS.
- Independent byte/hash verification (§8): PASS.

Evidence tiers: `TOOL_GENERATED` + `HUMAN_VERIFICATION`. No `INDEPENDENT_VERIFICATION` is claimed.

## 11. Known Limitations

- **The live run contained no sessionId-less row** (`non_session_metadata_rows = 0`), so the fix is proven by synthetic tests, not live. U1 (COMPLETE live) is answered; the specific bug path is not live-demonstrated.
- Token is `COMPLETE_WITHIN_BOUNDARY`, not literally `COMPLETE`.
- Agent invoked the **PowerShell** tool, not Bash, despite the `Bash(python harness/harness.py *)` allow rule. The command succeeded, so the rule's scope was **not** shown to be enforced or minimal. Also `inspect_order` only matches `Bash` tool results → will miss PowerShell receipts (Phase 2.2 issue).
- Headless `claude -p` session, not an interactive one.
- Hashes detect later change only; no signing/ACL (deferred). Operator and Agent share a user account.
- Stale `harness/README.md`; sealed package lives in gitignored `harness/runs/`.

## 12. Attribution

```text
Protocol Gap: NO     Harness Gap: fixed (metadata)     Environment: permission/tool-name mismatch noted
Agent Execution Error: not assessed (out of scope)
```

## 13. Phase 2.1 Gate

**PASS** (final). 18/18 tests, `COMPLETE_WITHIN_BOUNDARY` capture, `valid_package=true`, `issues=[]`, independent byte/hash re-check, Human Verification DONE, Protocol unchanged. The agent's earlier `PASS WITH GAPS` was upgraded only after §10. The limitations in §11 are non-blocking and retained.

Closeout notes: `harness/README.md` was refreshed after the initial report; `harness/runs/` stays gitignored (raw transcripts are not repo fixtures).

## 14. Phase 2.2 Readiness

**YES**, by Human decision. Inputs carried to Phase 2.2 (not fixed here):

- **PowerShell vs Bash:** PH2-QUAL-01 ran through the `PowerShell` tool, not the requested `Bash`. `inspect_order` only recognizes `Bash` tool results, and the `Bash(...)` allow rule was not shown to bound execution.
- Live capture did not include a sessionId-less metadata row (covered by regression tests only).
- Headless `claude -p` session, not interactive; non-blocking for U1.

PHASE 2.1 CLOSED — PASS
