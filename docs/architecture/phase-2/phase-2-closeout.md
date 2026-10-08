# Phase 2 Closeout

```text
PHASE 2 FINAL GATE: PASS
Phase 2.1 (Harness Qualification):   PASS
Phase 2.2 (Verifiable State Chain):  PASS
Protocol Modified:                   NO
Phase 2.3:                           NOT REQUIRED
Phase 3:                             NOT STARTED
```

Sources: `phase-2-boundary-analysis.md`, `phase-2-1-harness-qualification.md`, `phase-2-2-verifiable-state-chain.md`. Phase 1D remains `INSUFFICIENT — CLOSED` and was not reopened.

## 1. Goal

Phase 2 was not meant to build a complete Harness. It set out to show that a minimal Harness can capture a real Agent Runtime in a verifiable way, and can record and enforce a Requirement State Chain on that Agent. The unknowns it targeted were U1 (live capture), U2 (does a real Agent use the state CLI), and U3 (can the Harness enforce Protocol invariants).

## 2. What Phase 2 Proved

### A. Runtime Capture (Phase 2.1, run `PH2-QUAL-01`)
- A run boundary is established on a real Claude Code session, and the Runtime JSONL is captured and sealed as a source slice with a manifest.
- `verify` passes, and an independent script confirms the sealed slice is byte-equal to the source and that the SHA-256 and prefix hashes match.
- Rows without `sessionId` are exempt only if they are known metadata types (`file-history-snapshot`, `file-history-delta`) carrying no tool blocks. Any other such row is a capture gap, and a wrong `sessionId` still fails.
- A clean capture reports `COMPLETE_WITHIN_BOUNDARY`, with `valid_package=true` and `issues=[]`.

### B. Persistent State Events
The Harness records and queries Question, Assumption and Task state as append-only events with `event_id`, sequence and source. Tasks carry `assumption_deps`.

### C. Verifiable State Chain (Phase 2.2, run `PH2-VSC-01`)
```text
Question OPEN → ASSUMED → Assumption ISOLATED → Task(assumption_dep) →
Agent requests ELIGIBLE → Harness rejects (exit 1) → Task BLOCKED
```
- A real Agent (session `91d39881-1418-4163-a596-0ba648faaa42`) made every state change through the Harness CLI.
- Each of the six events has its `event_id` in a Runtime `tool_result`.
- The Agent's claim cannot bypass the Harness invariant.

### D. Fail-Closed Behavior (deterministic tests)
- Missing Question, Assumption or Task receipt → `INSUFFICIENT`.
- Missing ELIGIBLE rejection → `INSUFFICIENT`.
- Claim/state conflict → `INVALID_AGENT_RESULT`.
- Forged ELIGIBLE event → `FAIL`.
- Direct state edit → detected.
- ISOLATED dependency, P2 priority, or an unknown dependency → ELIGIBLE or creation rejected.

Tests: `test_harness.py` 27/27, `test_chain_verifier.py` 8/8.

## 3. Evidence and Verification Tiers

| Tier | Status |
| --- | --- |
| Runtime-generated evidence | Present |
| Tool-generated evidence (Harness, deterministic verifier) | Present |
| Human Verification | Done (2.1 spot-check; 2.2 transcript inspection) |
| Independent Agent Validator (e.g. GPT-6/Codex) | **Not performed** |

`chain_verifier.py` is read-only and shares no code with `harness.py`, but the same Claude implemented both. It is therefore **not** Independent Verification. This limitation is retained.

## 4. Protocol Integrity

```text
docs/architecture/protocol.md    = unchanged
docs/architecture/state-model.md = unchanged
```

The Harness implemented and verified existing semantics (state-model §4 and invariant 1). No contradiction was found, so Protocol Gap = NO.

## 5. Findings from Real Runs

| Phase | Finding | Class | Resolution |
| --- | --- | --- | --- |
| 2.1 | Runtime rows without `sessionId` were treated as session mismatches | Harness Gap | Explicit allowlist rule with fail-closed default, plus regression tests. It did not occur in the live run, so the branch is covered by tests only. |
| 2.1 / 2.2 | The Agent used `PowerShell`, not `Bash` | Environment | `inspect_order` accepts both; the verifier accepts both |
| 2.2 | `verify` raised `AttributeError` when `toolUseResult` was a string (an error or refusal result) | Harness Gap | Fixed with `tool_answers()` and a deterministic regression test. The sealed `PH2-VSC-01` was not modified and the experiment was not re-run. |

None of these is a Protocol Gap.

## 6. Deferred / Out of Scope (not Phase 2 failures)

1. Governing Spec Resolver
2. Requirement-level intelligence persistence/query beyond the current state slice
3. Complete async/queryable Human Gate
4. Assumption promotion through a Human Gate
5. Independent validator boundary
6. Stronger tamper-proof sealing (signing, ACL)
7. Multi-agent orchestration
8. MCP
9. SDK
10. Registry
11. Event Bus
12. UI
13. Database / cloud persistence
14. Full production CLI

Their absence does not downgrade the Phase 2 gate.

## 7. Known Limitations Carried Forward

- Single live run per stage, both headless `claude -p`.
- sessionId-less metadata not covered live.
- Tamper resistance is heuristic.
- The Agent claim → verifier comparison uses operator-supplied claims.
- Run packages are gitignored, so the raw evidence is local-only.
- No GPT-6/Codex review has been done on the sealed packages.

## 8. Boundary Conclusion

Phase 2 deliberately stopped after proving Harness Qualification and one Verifiable State Chain slice.

No Phase 2.3 is required merely to remove the deferred capability gaps.

## 9. Working Tree (fact only, at closeout)

```text
 M CLAUDE.md          (pre-existing, not touched by Phase 2)
?? AGENTS.md          (pre-existing, not touched by Phase 2)
?? docs/architecture/phase-2/
?? harness/
```

Nothing is committed.
