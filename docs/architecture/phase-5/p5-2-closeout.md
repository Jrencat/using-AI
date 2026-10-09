# Phase 5 P5-2 Closeout — one real Codex run (attempt closed as INSUFFICIENT)

```text
P5-2 RESULT:      INSUFFICIENT   (this verification attempt is closed by the Human; it is NOT retried)
CHECKER:          NOT RUN. No Checker verdict exists for this run. Nothing here is a PASS.
RECEIPT -> v2:    COMPLETE, 0 gaps (one real session; tool-generated)
HARNESS CAPTURE:  COMPLETE_WITHIN_BOUNDARY, valid_package = true (capture only; started AFTER the run, "Plan D")
CODEX TASK:       NOT completed by Codex (last write attempt failed; src/calc.py was edited by the operator)
PHASE 5:          NOT complete. P5-3 / P5-4 not authorized or started.
PROTOCOL / HARNESS / CHECKER / MAPPING v1+v2 / REGISTRIES / FIXTURES / ADAPTER: unchanged
```

Plan: `p5-2-minimal-validation-plan.md` (planned verdict classes: `PASS` / `FAIL` / `INCOMPLETE` / `INSUFFICIENT` / `BLOCKED`). Predecessors: `p5-1-closeout.md`, `p5-1-1-closeout.md`.

## 1. What P5-2 was to show

One real Codex FX-ELIGIBLE run, converted by the v2 adapter, accepted by the unchanged Harness and C1 Checker (Checker `PASS`, capture `COMPLETE_WITHIN_BOUNDARY`). It would not have shown that Codex behaves like Claude.

## 2. What happened

Sources are labelled: **[tool]** produced by a repo tool in this closing work, **[manual]** checked by hand against files/timestamps, **[operator]** stated by the operator and not independently verified.

- Workspace `D:\c1-live\PH5-P52-LIVE-01\workspace` was created as a copy of `phase-4-validation/fixture/workspace/`; its 5 files matched the source SHA-256 at creation **[tool]**. No baseline manifest and no anchor A were made before the run.
- Two earlier Codex sessions were started in the wrong working directory and stopped before reading files **[operator]**. They were not examined.
- The session in the correct workspace read `src/calc.py` and tried to write `subtract(a, b)`; the write failed and Codex stopped **[operator]**. The raw session shows 3 tool calls (a custom tool named `exec`) with 3 outputs, the third containing the word "failed" **[tool/manual, content not quoted]**.
- Codex ran no code or tests and changed no other file **[operator]**. The file-attribute/ACL check by the operator found no cause for the write failure **[operator]**. The cause of the failure is **UNKNOWN**.
- The operator then replaced the TODO in `src/calc.py` by hand with `subtract(a, b): return a - b` **[operator]**. The file's modification time is 09:21:44 UTC, after Codex's last tool call (09:19:48 UTC) and before the session's last record (09:22:40 UTC) **[manual]**. **The final content of `src/calc.py` is not Codex's work and is not evidence of Codex success.**
- The session shows two `task_started` / `task_complete` pairs and two `turn_context` records **[tool]**. Why there are two turns is **UNKNOWN**; the plan expected one prompt. Message content was not read.

## 3. Results

| Step | Result | Source |
|---|---|---|
| Session identification | One new rollout file after the workspace was created; its `session_meta` `cwd` equals the workspace path; session ID `01a11ff5-d025-7222-b57d-514be6296fe7`. Names/metadata only; the raw log was not copied or quoted. Source SHA-256 `f4d49bc3…480ffd` (50 lines), unchanged before and after the adapter run | [tool] + [manual] |
| Adapter, `--mapping-version 2` | `COMPLETE`, 0 gaps, exit 0, 6 rows (3 `tool_use` + 3 `tool_result`, all `sessionId` = the ID above); `runtime.jsonl` SHA-256 `42f85ab3…524a61`; `mapping_version` 2, `adapter_version` "2" | [tool] |
| Ignored (counted) records | `event_msg` 22, `response_item:message` 9, `response_item:reasoning` 4, `token_usage_record` 5, `turn_context` 2, `world_state` 1. No `compacted`, no unanswered call | [tool] |
| Harness capture (run id `PH5-P52-CAPTURE-ONLY-01`, package in git-ignored `harness/runs/`) | `COMPLETE_WITHIN_BOUNDARY`, no gaps, 3 `tool_use` / 3 `tool_result`, `verify` `valid_package = true`; `started_at` 09:26:07 UTC (after the session ended), `sealed_at` 09:26:07 UTC. No Task events were created | [tool] |
| Manifest / anchors / Checker | **Not done.** No pre-run baseline or anchor A; a baseline cannot be recreated after the manual edit without being a reconstruction | — |

## 4. Positive technical finding (single observation only)

- The v2 adapter accepted a real Codex 0.161.0 session with no gap, and the Harness sealed its output as `COMPLETE_WITHIN_BOUNDARY`.
- Rule T3 passed 5 real `token_usage_record` payloads. This is one observation on one session and one CLI version. It is **not** general compatibility, not cross-version evidence, and does not say whether T3's allow-list holds in other sessions.
- Real Codex 0.161.0 tool calls appear as a custom tool named `exec`, not as the `shell` / `apply_patch` names the plan and the synthetic fixtures assumed. The adapter does not interpret tool identity, so this did not matter here.

## 5. Why the verdict is INSUFFICIENT

- There is no Checker verdict: the chain was not completed (no pre-run baseline, no anchor A, no Task events before the task).
- The filesystem delta that a Checker would have judged was made by the operator, not by Codex, so even a mechanical `PASS` would not support the P5-2 claim.
- Plan D only: the Harness was started after the run, so its timestamps give no ordering evidence about Codex's activity. Neither plan lets the Harness observe Codex; the raw Codex file cannot be a Harness source (rows carry no top-level `sessionId`).
- Not `FAIL` (no Checker `FAIL`), not `INCOMPLETE` (the adapter was complete), not `BLOCKED` (nothing waited for Human input).

## 6. Evidence tier

The adapter output remains **`TOOL_GENERATED`**. It is not raised to `RUNTIME_GENERATED`; H1 is still pending. No claim is made that the Checker passed, and no Independent Verification exists. The Harness's `COMPLETE_WITHIN_BOUNDARY` shows only that the converted rows were complete and session-consistent inside the Harness's view, not that the session was authorised, complete or successful.

## 7. Not verified

- Codex completing the task; the cause of the write failure; why the session has two turns; the claims marked [operator].
- Any Checker verdict; any time ordering between the Harness and Codex's activity.
- Cross-version behaviour; other sessions; real symlink behaviour; repeat runs; FX-BLOCKED.

## 8. Not done, by decision

- No retry of Codex. Any further run is a new run needing the Human's fresh authorization of quota (the plan allows a second run only for an environment reason before any edit, never to chase `PASS`).
- No change to adapter, mapping, registries, fixtures, Harness, Checker or Protocol. No P5-3 / P5-4.

## 9. Open items

- Human rulings: H1 (tier of adapter-derived rows), H2 (whether to authorize another run and quota), H3 (close Phase 4), H4 (P5-3 / P5-4).
- If another run is ever authorized: do baseline ×2 and anchor A first, and learn the cause of the write failure (environment) before spending quota; the write failure may repeat.
