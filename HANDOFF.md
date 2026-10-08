# HANDOFF — using-AI (canonical, compressed)

Read this first, then the closeout docs named below. This is a state index, not a log. Formal definitions live in `docs/architecture/`.

## A. Project

**using-AI** = a Model-Agnostic / Agent-Native Software Engineering Protocol / Harness. It is not a CLI, SDK, MCP server or agent framework.

```text
Protocol = what must be true (objects, states, invariants, evidence, human authority)
Harness  = how execution is organized, recorded, enforced, verified
Runtime  = execution capabilities (Claude Code, Codex, ...)
Agent    = follows the Protocol; requests state changes, never grants them
```

The repo also holds the legacy 7-stage Chinese prompt templates (see `CLAUDE.md`, `legacy-mapping.md`); they are preserved, not replaced.

## B. Architecture core (authoritative: `docs/architecture/protocol.md`, `state-model.md`, `evidence.md`, `routing.md`)

- Objects: Requirement, Assumption, Spec, Task, Agent Contract, Evidence, Evaluation (Question is embedded in Requirement; Human Gate is a mixin).
- Requirement Intelligence: investigate first; ask only what investigation cannot resolve.
- Question: `OPEN → ANSWERED | ASSUMED | BLOCKED | INVALID`. An Assumption exists only from an `ASSUMED` Question and starts `ISOLATED`. A Critical business Question cannot be ASSUMED.
- Complexity belongs to Task only.
- Evidence trust tiers: SELF_REPORT < RUNTIME_GENERATED < TOOL_GENERATED < INDEPENDENT_VERIFICATION < HUMAN_VERIFICATION. A Claim is not a Fact; Claim vs Evidence conflict → `INVALID_AGENT_RESULT`; no evidence → `INSUFFICIENT`.
- Fail closed; Human Authority is non-negotiable. A Convention exists only via explicit Human Confirmation.
- Governing Spec Resolver is a Harness capability; the Protocol fixes no registry, path or storage.
- **Protocol is FROZEN** (`protocol.md`, `state-model.md` unchanged through Phase 2). Change only with a proven contradiction that Harness/Runtime cannot solve.

## C. Phase status

```text
Phase 1  1A COMPLETE | 1B COMPLETE | 1C PASS WITH GAPS (Protocol frozen)
         1D INSUFFICIENT — CLOSED  (do NOT reopen; do NOT re-run A–O, P-D, P-D-04, or create P-D-05)
Phase 2  2.1 PASS | 2.2 PASS | FINAL PASS  (no Phase 2.3 needed)
Phase 3  NOT STARTED
```

Phase 2 completed the minimal verifiable Harness slice. Docs: `docs/architecture/phase-1d/phase-1d-closeout.md`, `phase-2/phase-2-boundary-analysis.md`, `phase-2-1-harness-qualification.md`, `phase-2-2-verifiable-state-chain.md`, `phase-2-closeout.md`.

## D. What Phase 2 proved

```text
Requirement → Question → ASSUMED → Assumption (ISOLATED) → Task(assumption_dep)
 → Agent requests ELIGIBLE → Harness rejects (exit 1) → Task BLOCKED
```

- Runtime capture on a real Claude Code session: start → capture → seal → verify, `capture_status=COMPLETE_WITHIN_BOUNDARY`, `valid_package=true`, `issues=[]`; sealed slice byte-equal to source, SHA-256 and prefix hash match.
- Persistent append-only state events for Question/Assumption/Task; every state event_id correlated to a Runtime `tool_result` receipt (PowerShell and Bash both recognized).
- Fail-closed paths: missing receipt/rejection → INSUFFICIENT; claim/state conflict → INVALID_AGENT_RESULT; forged ELIGIBLE → FAIL; direct state edit → detected.
- Human Verification completed for both runs (`PH2-QUAL-01`, `PH2-VSC-01`).
- Real-run Harness bugs found and fixed (not Protocol gaps): sessionId-less metadata rows (2.1); `verify` crash on string `toolUseResult` (2.2).

## E. Evidence-level limits (keep stated)

```text
chain_verifier.py ≠ Independent Verification   (read-only, shares no code with harness.py, but written by the same Claude)
GPT-6 / Codex independent review = NOT PERFORMED
```

This is the current verification boundary, not a Phase 2 failure. Never describe Claude self-review as `INDEPENDENT_VERIFICATION`.

## F. Harness (`harness/`)

`harness.py`, `test_harness.py` (27 tests), `chain_verifier.py`, `test_chain_verifier.py` (8 tests), `README.md`, `.gitignore`. All pass at Phase 2 close. Run from the repo root: `python harness/harness.py ...`; tests from `harness/`: `python test_harness.py`, `python test_chain_verifier.py`. Run packages go to `harness/runs/` (gitignored, local-only; contain raw transcripts). Run IDs use the `PH2-` prefix. Capture token is `COMPLETE_WITHIN_BOUNDARY` (not renamed).

## G. Deferred / known limits (capabilities, not Phase 2 failures)

- Governing Spec Resolver not implemented.
- Question/Assumption/Task state is a minimal slice, not a full Runtime; no Assumption promotion via Human Gate.
- Async Human Gate not implemented (Claude `AskUserQuestion` is synchronous).
- Full Evaluation/Evidence persistence not implemented.
- Independent Validator boundary not implemented; tamper-proof sealing/signing/ACL not implemented (hash + heuristics only).
- Only single headless `claude -p` runs; sessionId-less metadata not covered live; Agent→verifier claims are operator-supplied.
- MCP, SDK, Registry, Orchestrator, Event Bus, UI, DB/cloud, production CLI: all deferred.

## H. Git notes

- Branch `main`, remote `origin` (github.com/Jrencat/using-AI).
- `CLAUDE.md` (modified) and `AGENTS.md` (untracked) are pre-existing user workspace state. They are **not** part of the Phase 2 checkpoint and must not be committed or reverted without the user's say-so.
- Never `git add .` / `-A`; never force-push.
- Global rules in the user's CLAUDE.md apply: concise output, no project-wide formatting, no push/force/`--no-verify` unless asked.

## I. NEXT STEP

```text
Do NOT start Phase 3 implementation.

Next: Phase 3 Boundary Analysis.
Goal: decide the minimum capability Phase 3 must prove,
not keep piling on Harness / Runtime / CLI / MCP / SDK / Orchestrator features.

Until that analysis is done:
- no Phase 3 implementation
- no Harness expansion
- no MCP / SDK / Registry / Orchestrator
- no Protocol change
```
