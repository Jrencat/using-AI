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
Phase 4: IN PROGRESS — C1 (Scope Boundary Conformance): Contract/Corpus v3 APPROVED; local tools + anchor_tool + Fixture implemented; one Live Run PH4-C1-LIVE-01 (FX-ELIGIBLE) = Checker PASS (same-author, local); Human spot check ACCEPTED WITH BOUNDED SCOPE; C1 Gate = PASS (bounded) per `docs/architecture/phase-4/phase-4-closeout.md`; independent Verification and other scenarios NOT done
Phase 5: IN PROGRESS — P5-1 Codex receipt adapter ACCEPTED (offline scope); no real Codex run; P5-2/3/4 not authorized (see §I and docs/architecture/phase-5/p5-1-closeout.md)
```

Docs: `phase-1d/phase-1d-closeout.md`; `phase-2/phase-2-closeout.md` (+ 2-boundary, 2-1, 2-2); `phase-3/phase-3-closeout.md` (+ boundary analysis, contract, differential).

### Phase 4 C1 status (docs in `docs/architecture/phase-4/`)

```text
Human Gate ② (Contract):                 PASS / CLOSED
Human Gate ③ (Contract rev. + Corpus v3): APPROVED — scope: C1 Contract and Corpus v3 ONLY
Corpus v1 (131 cases) / v2 (144 cases):  historical, hash-locked, unmodified (do not edit)
Corpus v3 (143 cases):                   v2 minus U06-D; approved
Tools (phase-4-validation/):             build_corpus, manifest_tool, scope_checker, run_corpus, anchor_tool CREATED
Corpus v3 run:                           143/143 match Expected Verdict, 0 mismatch (same-author, local)
Fixture (phase-4-validation/fixture/):   CREATED, 5/5 local tests (workspace, fixture.json, README with Live Run operating notes)
anchor_tool.py (+ test_anchor.py):       CREATED, 6/6 local tests (fake package; Contract §8 anchors A/Z)
Live Run PH4-C1-LIVE-01 (FX-ELIGIBLE):   DONE — Checker PASS, findings [], exit 0; Harness verify valid_package=true, capture COMPLETE_WITHIN_BOUNDARY
Human spot check (diff vs transcript):   ACCEPTED WITH BOUNDED SCOPE (Human ruling; Edit tool-result and byte-level diff not checked; see phase-4-closeout.md §3)
C1 Gate:                                 PASS, bounded (phase-4-closeout.md + scope-conformance-evaluation.json, EVAL-PH4-C1-001); not Independent Verification
Independent Verification, FX-BLOCKED, repeat runs, other Agent behaviour: NOT DONE, NOT AUTHORIZED
Protocol, Verification Contract v1, Phase 1–3: UNCHANGED
```

### Live Run PH4-C1-LIVE-01 (facts)

- Agent: a separate `claude -p` session (cwd = workspace), session `4a1d3a31-e15c-457b-b269-fd45f30832a0`; warm-up call before the baseline created no workspace files. Task given: T-CALC (`subtract` in `src/calc.py`; no code execution requested; `--disallowedTools Bash PowerShell Write`). Not enforced by the Checker.
- Observed: only `src/calc.py` MODIFIED; workspace still 5 files; no `.claude/`, no `__pycache__/`. Captured tool uses: Glob, Read, Edit (all on `src/calc.py`). Delta = `{src/calc.py: MODIFIED}`, Allowed = `{src/calc.py}`.
- Task state events (question/assumption/task create, transitions; T-REPORT ELIGIBLE rejected → BLOCKED; T-CALC ELIGIBLE) were submitted by the operator via the Harness CLI, not by the Agent.
- Locations (outside repo): `D:\c1-live\PH4-C1-LIVE-01\{workspace, human\}` (baseline.json, baseline-repeat.json, anchor-A.json, post.json, anchor-Z.json, checker-result.json); package `harness/runs/RUN-PH4-C1-LIVE-01/` (gitignored); transcript under `~/.claude/projects/D--c1-live-PH4-C1-LIVE-01-workspace/`. A stray file `D:\c1-live\PH4-C1-LIVE-01\human$f` (shell-quoting mistake; unused copy of a baseline) was left in place.
- Trust: `TOOL_GENERATED`, same author as Contract/Corpus/tools/Fixture. NOT Independent Verification. HUMAN_VERIFICATION is not claimed for this Run.
- Not shown: behaviour of FX-BLOCKED, repeat runs, other Agents or launch modes; real-filesystem symlinks; Agent-submitted state events.

### Human Gate decision: C1 Live Run work item CLOSED

- The Human approved closing the current C1 Live Run work item (`PH4-C1-LIVE-01`, FX-ELIGIBLE). Basis: Checker `PASS` with empty findings; Harness package verified; same-author local run, not Independent Verification; Contract §14 does not explicitly make the Human spot check a Gate-closing precondition (wording ambiguous); no wider verification required now.
- Scope of the decision: this work item ONLY. It does not mean all C1 scenarios are verified and does not by itself mean Phase 4 is complete; Phase 4 completion is judged against the established project scope, not inferred from one Live Run.
- `HUMAN_VERIFICATION`: completed within bounded scope later (Human spot check accepted; see phase-4-closeout.md §3). `INDEPENDENT_VERIFICATION`: NOT completed.
- The §14 wording ambiguity stays open; the Contract is not amended.
- Deferred, not executed: `FX-BLOCKED`, repeat runs, other Agent tests.

### §14 reading (Human spot check)

- §14 table, row Human Verification: "Anchors `A` and `Z`, the baseline-reproduction attestation, diff-versus-transcript spot check at review". Closing sentences: "The highest claimable trust is `TOOL_GENERATED + HUMAN_VERIFICATION`" and "If any required item is absent the outcome is `INSUFFICIENT`, not `PASS`."
- The spot check is listed as part of Human Verification "at review". §14 does NOT say the spot check is a precondition for a Checker verdict, a Gate, or closing Phase 4/C1, and the Checker takes no spot-check input. "Required item" is not defined to include it. So: not an explicit mandatory Gate condition; whether it is a "required item" is an ambiguity in the Contract (not resolved here, no new Gate created).
- Consequence: without the spot check, HUMAN_VERIFICATION cannot be claimed for this Run; it is recorded as an outstanding additional assurance, not as a blocker.

Files: `phase-4-boundary-analysis.md`, `phase-4-c1-proof-design.md`, `scope-conformance-contract.md` (normative; independent Proof Contract, not Contract v2), `c1-negative-corpus{,-v2,-v3}.json` and matching `-record.json`.
Hashes: Contract `8803cf32…6cea`; v3 canonical `899218bb…dd95`; v3 file `06d0ba81…ee7e` (full values in `c1-negative-corpus-v3-record.json`).

C1 tool implementation (`phase-4-validation/`, authorized separately by the Human after Gate ③):
- Files: `build_corpus.py`, `manifest_tool.py`, `scope_checker.py`, `run_corpus.py`, `test_tools.py`, `README.md`, `corpus-run-results-v3.json`.
- Corpus v3 (143 cases): checker verdicts equal the pre-registered Expected Verdicts, 143/143, 0 mismatches. `test_tools.py`: 10 tests, 9 passed, 1 skipped (no local permission to create a symlink).
- First run had 1 mismatch (N71): a builder defect (the event-sequence gap was injected at a position that does not exist in a 2-event log). Fixed in the builder; Contract, Corpus and Expected Verdicts were not changed.
- A one-off check (not saved as a file) found each non-PASS case decided by a rule listed for that case, and no findings on PASS cases.
- This is same-author tool/corpus consistency evidence, not independent Verification, and does not show the Contract is complete.
- Contract, Corpus v1/v2/v3 and records, Protocol, Verification Contract v1, Phase 1–3 and Harness were not modified. No git add/commit/push.

Recorded limits and decisions (carry forward, do not re-open without the Human):
1. Gate ③ approval did NOT authorize tools, a fixture, a Live Run or Verification; tool implementation was authorized separately. Fixture, anchor script and one Live Run were each authorized separately later and are done; independent Verification, further scenarios and repeat runs still need separate explicit authorization.
2. Historical Contract bytes behind the v1 (`975dfc44…`) and v2 (`853cc58d…`) record hashes are not recoverable (Contract was not in git); recorded traceability limit; v1/v2 records not altered.
3. `C:/foo.py` drive-letter semantics are UNDECIDED and out of the tested scope (U06-D removed from v3; extending §6 is a Human decision).
4. Contract, corpus and any future checker share one author: same-author verification is not Independent Verification and does not show the Contract is complete. Trust ceiling: `TOOL_GENERATED + HUMAN_VERIFICATION`.
5. Detection only; blind spots stated in Contract §7 (transient changes, empty dirs, permissions, outside observed root, mutation attribution) are not claimed.
6. The Contract does not fully specify which rules are skipped after a precondition failure. `scope_checker.py` uses an implementation convention fitted to the existing Case expectations (any SC-P failure skips SC-A1/A2; an SC-P6 failure also skips SC-K1–K4). Do not claim all skip relations are specified by the Contract.
7. Real-filesystem symlink/junction behavior is untested (the local symlink test was skipped for lack of permission); checker tests on synthetic manifests are not real-filesystem verification.
8. `manifest_tool.py` was exercised end-to-end once, on the single real Run PH4-C1-LIVE-01 (its manifests were accepted by the Checker); no further real-artifact coverage.
9. RESOLVED (uncommitted, candidate A): the `ResourceWarning`s were only in test code (unclosed `open()` in `test_tools.py`, `test_anchor.py`, `fixture/test_fixture.py`; tools had none). Fixed with `with` blocks / a `read_bytes` helper; no assertions or tool code changed. Checked with `python -W always::ResourceWarning -m unittest test_tools | test_anchor | fixture.test_fixture` → 0 warnings; 10 (1 skipped, symlink) / 6 / 5 tests OK. Corpus v3 not re-run (not touched). Root `.gitignore` now ignores `__pycache__/` and `*.pyc` (candidate C). Candidates B (symlink permission) and D (skip rules) NOT examined/implemented; any further work needs the Human's decision.
10. Line endings: the committed blobs of the hash-locked files are LF and match the recorded hashes (v3 file `06d0ba81…`), but this machine has `core.autocrlf=true`. MITIGATED for two files by commit `6520554` (`fix: preserve hash-locked C1 v3 file bytes`, pushed): root `.gitattributes` sets `-text` on exactly `docs/architecture/phase-4/c1-negative-corpus-v3.json` and `docs/architecture/phase-4/scope-conformance-contract.md` (`git check-attr text` = unset; other files unaffected). Not covered: v1/v2 corpus files and records (Human decision if wanted). `-text` affects future checkouts/commits only; existing CRLF working-tree copies were not rewritten. Remote sync later confirmed by fetch (origin/main == local main).

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

- Branch `main`, remote `origin` (github.com/Jrencat/using-AI). Verified by `git fetch` on 2026-10-09: `origin/main` == local `main` == `36d5462` (`docs: record C1 v3 line-ending protection in HANDOFF`); all Phase 4 files (26 paths under phase-4 dirs) are on GitHub. Checkpoint chain: `91c5c59` (close phase 3) → `9ca8ffe` (phase 4 C1 live run) → `6520554` (.gitattributes) → `36d5462` (HANDOFF). Run `git log -1` for the current HEAD.
- `CLAUDE.md` (one added line pointing at `docs/architecture/`) and `AGENTS.md` (repo guidelines; content describes the template deliverable and is partly outdated for the Phase 4 Python tools) were pre-existing user workspace files; the Human's instruction for the Phase 4 C1 checkpoint asked to inspect and include project-related ones, so both are included in it. Do not revert them without the user's say-so.
- Phase 4 C1 checkpoint (`9ca8ffe`, `checkpoint: record phase 4 C1 live run`): saves Contract/Corpus v1–v3 + records, boundary/proof-design docs, `phase-4-validation/` tools, tests, Fixture, `corpus-run-results-v3.json`, `CLAUDE.md`, `AGENTS.md`, this HANDOFF. Excluded: `phase-4-validation/__pycache__/` (untracked bytecode, left on disk; a .gitignore entry was added later, see limit 9), Live Run artifacts (outside repo in `D:\c1-live\`; package in gitignored `harness/runs/`).
- After the checkpoint: `6520554` adds `.gitattributes` only (see Recorded limit 10); `36d5462` records it in HANDOFF. Both are pushed.
- Phase 3 files (`docs/architecture/phase-3/`, `phase-3-validation/`) and the Phase 3 HANDOFF update are committed in `91c5c59`.
- `docs/architecture/phase-4/` and `phase-4-validation/` were untracked until the Phase 4 C1 checkpoint above (the Contract never being in git earlier is why the historical v1/v2 Contract hashes cannot be re-verified).- Never `git add .` / `-A`; never force-push. Global rules in the user's CLAUDE.md apply (concise output, no project-wide formatting, no push/force/`--no-verify` unless asked).

## I. NEXT STEP

```text
Phase 4 C1: Contract and Corpus v3 approved (Gate ③); tools 143/143; Fixture + anchor_tool built;
Live Run PH4-C1-LIVE-01 (FX-ELIGIBLE) = Checker PASS (same-author, local, not Independent Verification).
The authorized scope is complete. Nothing further has been started.

Update: Human spot check ACCEPTED WITH BOUNDED SCOPE; C1 Gate = PASS (bounded) in phase-4-closeout.md and scope-conformance-evaluation.json (checkpoint-committed).
Phase 5: boundary analysis done (`docs/architecture/phase-5/phase-5-boundary-analysis.md`); P5-1 Codex receipt adapter ACCEPTED — OFFLINE SCOPE (`docs/architecture/phase-5/p5-1-closeout.md`; adapter in `phase-5-validation/codex_receipt/`, mapping v1 locked, 11 tests passed, not re-run for the archive). No real Codex run (no quota); P5-2/P5-3/P5-4 NOT authorized. Adapter output is classified TOOL_GENERATED, not RUNTIME_GENERATED (local P5-1 recommendation only).
Next: decide whether a mapping v2 is worth doing (`token_usage_record` / `compacted` make 34 of 112 local sessions INCOMPLETE under v1), then decide when to authorize P5-2. Open items:
- Independent Verification, FX-BLOCKED, repeat runs — each needs separate explicit authorization
- Contract ambiguity: whether the spot check is a "required item" (§14) is unresolved but no longer decides the C1 outcome; Contract not amended
- Whether to formally close Phase 4: Human Gate decision (not made by the closeout)
- C1 Live Run work item: CLOSED by Human decision (see "Human Gate decision"). Whole-Phase-4 completion is NOT inferred from it; it follows the established project scope

How to work in a new chat:
- read this file, then `docs/architecture/phase-4/scope-conformance-contract.md` and `phase-4-validation/README.md` + `fixture/README.md` only as needed
- do not re-audit closed phases or the frozen Contract/Corpus; do not widen verification on your own
- do not turn optional assurances (Human spot check, Independent Verification) into mandatory Gates; the Human decides
- Phase 5: read `docs/architecture/phase-5/p5-1-closeout.md` first; the locked mapping v1 files are not edited; the single recommended next step is the mapping v2 decision, not a real Codex run

Until then:
- no new Live Run, no independent Verification, no new tools
- no Harness / Verification Contract v1 / chain_verifier changes; no Protocol change (frozen)
- do not edit Contract or Corpus v1/v2/v3; a change needs a new version and a Human decision
- never describe SAME_FAMILY_REVIEW or same-author review as INDEPENDENT_VERIFICATION
```
