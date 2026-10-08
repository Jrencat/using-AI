# Phase 2.2 — Verifiable State Chain

```text
PHASE 2.2 FINAL GATE: PASS
Human Verification: PASS (§11)
Independent Verification: NOT PERFORMED (no independent Agent/Validator)
Protocol Modified: NO
```

## 1. Phase 2.2 Goal

Answer **U2 + U3**: can a real Agent form a traceable `Question → Assumption → Task` chain through the Harness CLI, and does the Harness deterministically refuse `ELIGIBLE` for a Task that depends on an `ISOLATED` Assumption?

## 2. Protocol Status

`protocol.md` and `state-model.md` untouched. The implemented invariants restate existing rules: state-model §4 (DRAFT→BLOCKED when `assumption_dep` is ISOLATED or priority is P2) and §8 invariant 1. No contradiction found.

## 3. Harness Changes

`harness/harness.py`:
- `task-create --assumption-dep <ids...>`; each dep must be an existing Assumption, otherwise the Task is rejected.
- New `task-transition` (`TASK_STATE_CHANGED`): `ELIGIBLE` is refused when priority is P2 or any dep is ISOLATED. The refusal is recorded (`STATE_TRANSITION_REJECTED`) and printed with its event_id, then the Task goes `BLOCKED` (state-model DRAFT→BLOCKED). A BLOCKED Task cannot be made ELIGIBLE through the CLI.
- `query task` and `query assumption` now report state (`task_state`, `assumption_state` helpers).
- `inspect_order` accepts `PowerShell` as well as `Bash` receipts (minimal change, no tool registry).
- **Harness Gap found live:** `verify` crashed with `AttributeError` when a Runtime `toolUseResult` was a string (the refused command's error result). Fixed with a `tool_answers()` helper. The sealed run was not modified or re-run; `verify` was simply re-executed after the fix.

New `harness/chain_verifier.py`: read-only, shares no code with `harness.py`.

## 4. Deterministic Tests

- `test_harness.py`: **27/27** (18 prior + 9 new: Question→ASSUMED→Assumption ISOLATED; Task without dep → ELIGIBLE allowed; ISOLATED dep → ELIGIBLE rejected and BLOCKED; P2 rejected; unknown dependency rejected; BLOCKED Task cannot become ELIGIBLE later; absent Task rejected; PowerShell receipts in `inspect_order`; string `toolUseResult`).
- `test_chain_verifier.py`: **8/8** (complete chain PASS; Bash receipts; missing Question/Assumption/Task receipt → INSUFFICIENT; missing rejection → INSUFFICIENT; claim conflict → INVALID_AGENT_RESULT; forged ELIGIBLE event → FAIL; direct state edit flagged; verifier is read-only).

## 5. Run ID / Claude Session ID

- Run: `PH2-VSC-01` (package in gitignored `harness/runs/RUN-PH2-VSC-01/`).
- Session: `91d39881-1418-4163-a596-0ba648faaa42`, headless `claude -p`, cwd = repo. Agent given semantic instructions and the README (no literal commands); Edit/Write tools denied; allow-rules for the harness CLI only.

## 6. Question / Assumption / Task State Chain

| seq | Event | Receipt (tool_result row) |
| --- | --- | --- |
| 1 | `QUESTION_CREATED` Q-VSC-01 (OPEN) `3b90e695` | PowerShell, row 7 |
| 2 | `QUESTION_STATE_CHANGED` OPEN→ASSUMED `b5eeffe5` | PowerShell, row 9 |
| 3 | `ASSUMPTION_CREATED` AS-VSC-01 ISOLATED, origin Q-VSC-01 `d28196e2` | PowerShell, row 11 |
| 4 | `TASK_CREATED` T-VSC-01, `assumption_deps=[AS-VSC-01]` `95fc50d0` | PowerShell, row 13 |
| 5 | `STATE_TRANSITION_REJECTED` ELIGIBLE `91cfd80e` | PowerShell, row 20 (`is_error=true`) |
| 6 | `TASK_STATE_CHANGED` DRAFT→BLOCKED `eae8297f` | PowerShell, row 20 |

Final query (row 23) lists all six event_ids. Assumption ISOLATED is automatic on creation; there is no separate "mark ISOLATED" step in the Protocol or Harness.

## 7. ELIGIBLE Rejection

Refused with exit 1: `Task cannot be ELIGIBLE: assumption_dep AS-VSC-01 is ISOLATED`. No `TASK_STATE_CHANGED → ELIGIBLE` exists for T-VSC-01; final state BLOCKED. Enforced by the Harness, not by Agent choice (the Agent attempted ELIGIBLE as instructed).

## 8. Runtime Evidence / Event ID Correlation

All 6 state event_ids appear in `tool_result` rows of `PowerShell` tool calls whose command is `python harness/harness.py ...`. The event_ids are generated at append time and cannot appear in the Agent's command text. 7 tool_use / 7 tool_result (1 Read of the README, 6 harness calls), all paired. No Edit/Write, no command touching package files.

## 9. Seal / Verify

```text
capture_status = COMPLETE_WITHIN_BOUNDARY   non_session_metadata_rows = 0   capture_gaps = []
valid_package  = true                        issues = []                     (after the string-toolUseResult fix)
slice [168806, 223183) byte-equal to source; SHA-256 and prefix hash match (independent re-check)
```

## 10. Independent Verifier

`chain_verifier.py harness/runs/RUN-PH2-VSC-01 --claim Q-VSC-01=ASSUMED --claim AS-VSC-01=ISOLATED --claim T-VSC-01=BLOCKED` → **verdict PASS**, no issues, no claim mismatch. It re-derived: sequence, Question OPEN→ASSUMED order, Assumption→ASSUMED Question, ISOLATED, Task dependency, ELIGIBLE refusal and absence of any grant, receipt per event, package integrity. Tier: `TOOL_GENERATED` / `RUNTIME_GENERATED`. Written by the same Claude that wrote the Harness, so it is not independent of the implementer; GPT-6/Codex re-review of the sealed package remains possible later.

## 11. Human Verification

**DONE — PASS.** The Human inspected the real Runtime transcript (`harness/runs/RUN-PH2-VSC-01/runtime.jsonl`) and confirmed:

1. The six state operations were made by the Agent through the `PowerShell` tool calling the Harness CLI.
2. Each state event_id corresponds to the matching Runtime `tool_result`.
3. The `ELIGIBLE` request was rejected by the Harness: `Task cannot be ELIGIBLE: assumption_dep AS-VSC-01 is ISOLATED`.
4. After the rejection T-VSC-01 became BLOCKED; the Harness was not bypassed.
5. No Edit/Write or direct modification of Harness state/package files was found.
6. Final query: `Q-VSC-01 = ASSUMED`, `AS-VSC-01 = ISOLATED`, `T-VSC-01 = BLOCKED`.

Evidence tiers: `TOOL_GENERATED` + `RUNTIME_GENERATED` + `HUMAN_VERIFICATION`. This is **not** `INDEPENDENT_VERIFICATION`: `chain_verifier.py` is read-only and shares no code with `harness.py`, but it was written by the same Claude that implemented the Harness. GPT-6/Codex review of the sealed package has not been performed.

## 12. Known Gaps (non-blocking, retained)

- Single run; headless `claude -p`, not an interactive session.
- The Agent used `PowerShell`, not `Bash` (both receipts are now supported).
- No sessionId-less metadata row occurred live (regression-tested only).
- Assumption promotion / Human Gate promotion path is not implemented; any Task with an Assumption dependency stays non-ELIGIBLE in this Harness.
- Tamper resistance is heuristic (package hashes, edit-tool and command scan); no signing/ACL.
- Agent claim → verifier comparison uses operator-supplied `--claim` values transcribed from the Agent's report.
- The package is gitignored; the raw evidence is local-only.
- GPT-6/Codex independent review has not been performed.

## 13. Attribution

```text
Protocol Gap: NO
Harness Gap: YES — fixed during Phase 2.2 (string toolUseResult crash in verify; Task dependency/eligibility not implemented before this phase)
Agent Execution Error: NO observed
Environment / Fixture Problem: PowerShell vs Bash — handled
```

## 14. Phase 2.2 Gate

```text
PHASE 2.2 FINAL GATE: PASS
E1–E10: PASS
Protocol Modified: NO
```

E9 (Human Verification) was completed after the initial report, which had recorded `PASS WITH GAPS — pending Human Verification`. The §12 gaps are capability boundaries, not failures. PH2-VSC-01 was not re-run.

## 15. Phase 3 Readiness

Not assessed here. Phase 2.2 closed; Phase 2.3/3 not started.
