# HANDOFF — using-AI (canonical, compressed)

Read this first, then the closeout docs named below. This is a state index, not a log. Formal definitions live in `docs/architecture/`.

## A. Project

**using-AI** = a Model-Agnostic / Agent-Native Software Engineering Protocol / Harness. It is not a CLI, SDK, MCP server or agent framework.

```text
Protocol = what must be true (objects, states, invariants, evidence, human authority)
Harness  = how execution is organized, recorded, enforced, verified
Runtime  = execution capabilities (Claude Code, Codex, ...)
Agent    = protocol participant, not evidence authority; requests state changes, never grants them
```

The repo also holds the legacy 7-stage Chinese prompt templates (see `CLAUDE.md`, `legacy-mapping.md`); they are preserved, not replaced.

## B. Architecture core (authoritative: `docs/architecture/protocol.md`, `state-model.md`, `evidence.md`, `routing.md`)

- Objects: Requirement, Assumption, Spec, Task, Agent Contract, Evidence, Evaluation (Question is embedded in Requirement; Human Gate is a mixin).
- Requirement Intelligence: investigate first; ask only what investigation cannot resolve.
- Question: `OPEN → ANSWERED | ASSUMED | BLOCKED | INVALID`. An Assumption exists only from an `ASSUMED` Question and starts `ISOLATED`. A Critical business Question cannot be ASSUMED.
- Evidence trust tiers: SELF_REPORT < RUNTIME_GENERATED < TOOL_GENERATED < INDEPENDENT_VERIFICATION < HUMAN_VERIFICATION. A Claim is not a Fact; Claim vs Evidence conflict → `INVALID_AGENT_RESULT`; no evidence → `INSUFFICIENT`.
- Fail closed; Human Authority is non-negotiable. Governing Spec Resolver is a Harness capability.
- **Protocol is FROZEN** (`protocol.md`, `state-model.md` unchanged through Phase 3). Change only with a proven contradiction that Harness/Runtime cannot solve.

## C. Phase status

```text
Phase 1: PASS / CLOSED   (1A COMPLETE | 1B COMPLETE | 1C PASS WITH GAPS, Protocol frozen | 1D INSUFFICIENT — CLOSED;
                          do NOT reopen 1D; do NOT re-run A–O, P-D, P-D-04, or create P-D-05)
Phase 2: PASS / CLOSED   (2.1 PASS | 2.2 PASS; do not re-run; do not create PH2 runs)
Phase 3: PASS / CLOSED   (Trust Label: SAME_FAMILY_REVIEW)
Phase 4: NOT STARTED     (not designed, not executed)
```

Docs: `phase-1d/phase-1d-closeout.md`; `phase-2/phase-2-closeout.md` (+ 2-boundary, 2-1, 2-2); `phase-3/phase-3-closeout.md` (+ boundary analysis, contract, differential).

## D. What Phase 2 proved (state chain + capture)

```text
Requirement → Question → ASSUMED → Assumption (ISOLATED) → Task(assumption_dep)
 → Agent requests ELIGIBLE → Harness rejects (exit 1) → Task BLOCKED
```

Real Claude Code capture start→capture→seal→verify (`COMPLETE_WITHIN_BOUNDARY`); every state event_id correlated to a Runtime `tool_result` receipt; fail-closed paths tested; Human Verification done for `PH2-QUAL-01`, `PH2-VSC-01`.

## E. Phase 3 — Independent Validation Boundary

```text
PHASE 3 FINAL GATE: PASS
Trust Label: SAME_FAMILY_REVIEW        (NOT INDEPENDENT_VERIFICATION)

Protocol Modified: NO         Contract Modified: NO        Phase 2 Modified: NO
External Digest Modified: NO  New Validator Fixed: NO
Differential Verification: PASS      Human Verification: PASS
E6 Evaluation Record: DONE           E8 Integrity Check: PASS
```

**Core proof (within Verification Contract v1 only):** a Context-Isolated Claude (session `9de7fed0-154d-4741-8ac5-59858ccc14b3`, captured as run `PH3-AUTH-01`) received only `verification-contract.md`, the package format, two sealed package copies and the Human digest record — never the old verifier, its tests, the Expected or the Negative Corpus — and wrote a standalone `validator.py`.

- Verification Contract v1 is the sole normative source; verdicts: `PASS | FAIL | INSUFFICIENT | INVALID_AGENT_RESULT`; precedence `FAIL > INVALID_AGENT_RESULT > INSUFFICIENT > PASS`.
- External Human digest (created by the Human before any validator work) is the integrity anchor; no digest → never an unqualified PASS.
- 18 pre-registered, hash-locked scenarios (P01–P04, N01–N10 incl. N06a self-consistent forgery).
- **New Validator = Expected 18/18. Old `chain_verifier.py` = Expected 10/18.** Re-run byte-identical.
- 8 divergences (D1–D4) classified, all the old verifier deviating from the Contract: D1 no external digest input (P04, N06a, N06b, N07); D2 reads `run.json.source` outside the Contract input set (N03, N09; `EXISTING_VERIFIER_BUG / READS_OUTSIDE_CONTRACT_INPUT_SET`); D3 no inventory `row_count` check (N05b); D4 no Critical→ASSUMED rule (N10).
- No `NEW_VALIDATOR_BUG`, no `TEST_CORPUS_ERROR`, no fix/v2 of the validator.

### Phase 3 artifacts (actual paths)

```text
docs/architecture/phase-3/phase-3-boundary-analysis.md
docs/architecture/phase-3/verification-contract.md        (normative v1, unmodified)
docs/architecture/phase-3/external-digest-record.json     (Human anchor, read-only)
docs/architecture/phase-3/negative-corpus-record.json     (corpus + expected hash lock)
docs/architecture/phase-3/differential-verification.md
docs/architecture/phase-3/phase-3-evaluation.json         (EVAL-PH3-001, Evaluation-shaped, SAME_FAMILY_REVIEW)
docs/architecture/phase-3/phase-3-closeout.md
phase-3-validation/differential-results-v1.json
phase-3-validation/differential-results-v1-rerun.json    (byte-identical to v1)
phase-3-validation/run_differential.py, record_digests.py
```

Not in the repo (referenced by path/hash): `D:\phase3-iso\validator.py` (+ `NOTES.md`), `D:\phase3-pre-registered\` (corpus, `expected.json`, builder), `harness/runs/RUN-PH3-AUTH-01/` (gitignored, raw transcript). Copying them into the repo is a Human decision.

### Phase 3 known limits (keep stated)

1. No cross-model Independent Verification; GPT-6/Codex review NOT PERFORMED (additive, optional).
2. Contract v1 has 5 deferred `CONTRACT_V2_CANDIDATE`s: extra package files; digest record missing a file hash; duplicate object id; S5 wording conflict; R2 scope for sessionId-less rows. No Contract v2.
3. Validator completeness not proven; Expected/Corpus/Contract share one author; the isolated session saw its own self-test output on the real packages.
4. Old `chain_verifier.py` has the capability gaps D1–D4 above; it was deliberately not fixed.
5. Phase 3 does not make the Harness production-grade. One chain shape only; sealing is hash-based (no signing/ACL); external digest proves anchored bytes, not how the package formed before anchoring.

## F. Harness (`harness/`, unchanged since Phase 2)

`harness.py`, `test_harness.py` (27 tests), `chain_verifier.py`, `test_chain_verifier.py` (8 tests), `README.md`, `.gitignore`. Run from repo root: `python harness/harness.py ...`. Run packages go to `harness/runs/` (gitignored, local-only; raw transcripts). Run-ID prefixes: `PH2-` (Phase 2), `PH3-` (Phase 3). Capture token `COMPLETE_WITHIN_BOUNDARY`.

## G. Deferred (capabilities, not failures)

Governing Spec Resolver; async/queryable Human Gate and Assumption promotion; Evidence/Evaluation store; Task positive path and Scope enforcement; second Runtime / model-agnostic execution; signing/ACL; Contract v2; optional source-integrity cross-check; MCP, SDK, Registry, Orchestrator, Event Bus, UI, DB/cloud, production CLI.

## H. Git notes

- Branch `main`, remote `origin` (github.com/Jrencat/using-AI). Last commit: `5068b95 chore: checkpoint phase 2 and compress handoff`.
- `CLAUDE.md` (modified) and `AGENTS.md` (untracked) are pre-existing user workspace state, not part of any checkpoint; do not commit or revert without the user's say-so.
- Phase 3 files (`docs/architecture/phase-3/`, `phase-3-validation/`) and this HANDOFF update are uncommitted until the user asks.
- Never `git add .` / `-A`; never force-push. Global rules in the user's CLAUDE.md apply (concise output, no project-wide formatting, no push/force/`--no-verify` unless asked).

## I. NEXT STEP

```text
Phase 4: NOT STARTED — not designed, not executed.

Next: Phase 4 Boundary Analysis (analysis only, no implementation).
Decide the minimal Phase 4 proof target before building anything.

Until that analysis is done:
- no Phase 4 implementation, no new runs
- no Harness / Contract / Validator / chain_verifier changes
- no Protocol change (frozen)
- never describe SAME_FAMILY_REVIEW as INDEPENDENT_VERIFICATION
```
