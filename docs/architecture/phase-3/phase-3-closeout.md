# Phase 3 Closeout — Independent Validation Boundary

```text
PHASE 3 FINAL GATE: PASS
Trust Label:        SAME_FAMILY_REVIEW      (NOT INDEPENDENT_VERIFICATION)
Protocol Modified:  NO     Contract Modified: NO     Phase 2 Modified: NO
External Digest Modified: NO     New Validator Fixed: NO     Contract v2: NO
Commit: NO     Push: NO
```

## 1. Goal

Prove that **sealed package + external Human digest + normative Verification Contract** can be re-judged by a Context-Isolated, standalone Validator, i.e. the verdict is a function of those three inputs and not of the original implementer's private knowledge. Proof target and rationale: `phase-3-boundary-analysis.md`.

## 2. Step 2 — Human External Digest: PASS

The Human ran `phase-3-validation/record_digests.py` and created `external-digest-record.json` (SHA-256 of the four files of `PH2-VSC-01` and `PH2-QUAL-01`), before any validator work existed, and cross-checked the two `runtime.jsonl` hashes with `certutil`. The record is outside every package and outside the validator's write scope; it was never regenerated or edited.

## 3. Step 3 — Context-Isolated Validator: PASS

- Session `9de7fed0-154d-4741-8ac5-59858ccc14b3`, run `PH3-AUTH-01`, captured with the existing Harness: `COMPLETE_WITHIN_BOUNDARY`, 5 tool_use / 5 tool_result paired, `verify` valid, no issues.
- Workspace `D:\phase3-iso\`: the Contract, the digest record copy, two package copies. The negative corpus and Expected were built and hash-locked first (18 cases, 85 files, `validator_workspace_existed: false`) in `D:\phase3-pre-registered\`, never provided to the session.
- Transcript inspection: tool calls were Read (Contract), Glob (workspace), Write ×2 (`validator.py`, `NOTES.md`), PowerShell (self-test). No occurrence of `chain_verifier`, `test_harness`, `negative-corpus`, `pre-registered`, repo path, or git. `validator.py` imports stdlib only (`argparse, hashlib, json, os, sys`), no subprocess, no hardcoded run ids or verdicts.
- Label: **SAME_FAMILY_REVIEW**.

## 4. Step 4 — Differential Verification: PASS

Detail: `differential-verification.md`. Raw: `phase-3-validation/differential-results-v1.json` (and a byte-identical re-run).

- 18/18 cases executed; **New = Expected 18/18**; **Old = Expected 10/18**.
- 8 divergences (P04, N03, N05b, N06a, N06b, N07, N09, N10), grouped D1–D4, **all** the old verifier deviating from the Contract.
- No `NEW_VALIDATOR_BUG`, no `TEST_CORPUS_ERROR`, no `EXECUTION_ERROR`, no ambiguity surfaced in the 18 cases. No fix, no v2.

## 5. D1 — External digest capability gap (P04, N06a, N06b, N07)

Old verifier has no external digest input, so it returns `PASS` where the Contract requires `INSUFFICIENT` (anchor absent) or `FAIL` (anchor mismatch). N06a is the self-consistent forgery: only the Human digest rejects it. `EXISTING_VERIFIER_BUG`, sub-type capability gap (the verifier predates the anchor requirement).

## 6. D2 — Old verifier reads outside the Contract input set (N03, N09)

```text
EXISTING_VERIFIER_BUG
subtype = READS_OUTSIDE_CONTRACT_INPUT_SET
```

The old verifier opens `run.json.source` (the live Claude session file), which Contract §2 forbids, and its extra `sealed runtime differs from source slice` finding lifts `INSUFFICIENT` to `FAIL` by precedence. Human confirmed this classification. The Contract is **not** modified and the `source` cross-check is **not** added to v1. That check may give stronger source-integrity evidence; it belongs to a possible future, optional Runtime/source-integrity capability. The Phase 3 Validator stays within package + external digest + contract.

## 7. D3 — Manifest inventory (N05b)

Old verifier does not compare `manifest.runtime_inventory.row_count` with the Runtime rows (Contract I6). Capability gap; Contract says `FAIL`, old says `PASS`.

## 8. D4 — Critical Question → ASSUMED (N10)

Old verifier does not enforce the rule that a `Critical` Question cannot be `ASSUMED` (Contract S3, Protocol hard rule). Capability gap; Contract says `FAIL`, old says `PASS`.

## 9. Contract v2 candidates — DEFERRED (no Contract edit)

`CONTRACT_V2_CANDIDATE`, none exercised by the 18 cases, none changes the Step 4 outcome:

1. Extra files in the package directory (only the §3 catch-all applies).
2. Digest record lacks a hash for one of the four files.
3. Duplicate creation of the same object id.
4. S5 wording conflict (Task already `BLOCKED` before the rejection and unchanged): "recorded state is BLOCKED" vs "no BLOCKED change is FAIL". The validator chose INSUFFICIENT, which matches neither literal reading.
5. R2 scope for Runtime rows without `sessionId` (I7 vs R2).

Unknown event type is decided by E3 (`INSUFFICIENT`) and is not a gap.

## 10. Evaluation Record (E6): DONE

`docs/architecture/phase-3/phase-3-evaluation.json` (`EVAL-PH3-001`), outside all packages: claim, evidence_refs with hashes, decision `PASS`, `collected_by`, `trust_tier: SAME_FAMILY_REVIEW`, and sources. It is an Evaluation-shaped record only: no new trust tier, no new Protocol Core Object, no Evaluation store; `protocol.md` and `state-model.md` untouched. Its decision is scoped to Contract v1 and the 18 cases.

## 11. Human Verification (E7)

**Machine / Agent verified** (reproducible commands, not Human evidence):

- 18 cases executed; New = Expected 18/18; Old = Expected 10/18; 8 divergences classified.
- Re-run is byte-identical to the first round (both `sha256 58b606bd…`).
- Hashes of Contract, validator, old verifier, digest record, expected.json and the 85-file corpus lock unchanged; Phase 2 packages equal the Human digest.

**Human verified** — Human-confirmed in this review (no timestamp, identity or signature is recorded here; none is invented):

1. The Step 2 External Digest was created by the Human.
2. The two key `runtime.jsonl` SHA-256 values were checked by the Human with `certutil`.
3. The Step 3 Context-Isolated Validator did not read forbidden implementation, Expected or Corpus.
4. The Step 4 matrix and divergence analysis were reviewed.
5. D2 stays `EXISTING_VERIFIER_BUG` (`READS_OUTSIDE_CONTRACT_INPUT_SET`).
6. The five Contract v2 candidates are not edited now.
7. The highest trust label is `SAME_FAMILY_REVIEW`.

## 12. Integrity / Diff (E8): PASS

Read-only check at closeout:

| Item | Result |
| --- | --- |
| `protocol.md`, `state-model.md`, `HANDOFF.md` | `git diff` empty |
| `harness.py`, `chain_verifier.py`, `test_harness.py`, `test_chain_verifier.py`, `harness/README.md` | `git diff` empty |
| `PH2-VSC-01`, `PH2-QUAL-01` packages | match Human digest |
| `external-digest-record.json`, `verification-contract.md`, `validator.py`, `chain_verifier.py` | hashes equal pre-Step-4 values |
| `expected.json`, corpus (85 files) | lock intact |
| `differential-results-v1.json` vs `-rerun.json` | byte-identical |
| `git status` | `M CLAUDE.md`, `?? AGENTS.md` (pre-existing); new: `docs/architecture/phase-3/`, `phase-3-validation/` |

Not in the repo (by design): `D:\phase3-iso\` (validator, `NOTES.md`), `D:\phase3-pre-registered\` (corpus, expected, builder), `harness/runs/RUN-PH3-AUTH-01/` (gitignored). They are referenced by path and hash; copying them into the repo is a Human decision.

## 13. Known Limitations

- Expected, Corpus and Contract share one author; agreement shows the Contract sufficed at these 18 points, not that it is complete.
- The isolated session saw its own self-test outputs on the two real packages; it saw no Expected or Corpus, but may have been steered by those outputs.
- Only same-family review; the model-family axis is unmet. No GPT-6/Codex review was performed.
- Contract v1 retains five open candidate gaps (§9).
- Runtime transcript authenticity rests on the current Harness sealing (hash and heuristics, no signing/ACL).
- The external digest proves the Human-anchored bytes; it does not prove how the package was formed before anchoring.
- One chain shape only (Question → Assumption → gated Task); Spec, Evaluation store, Human Gate and the Task positive path are out of scope.
- Three of the four divergence groups are capability gaps of a verifier written before the Contract.

## 14. What the PASS Proves — and Does Not

**Proves:** within Verification Contract v1, a Claude that read neither the old validator implementation nor the Expected/Negative Corpus, and received only the Contract, the package format, two sealed packages and the Human digest, implemented a validator whose results on the 18 pre-registered scenarios equal the Contract-derived Expected exactly. Differential Verification also found and explained 8 points where the old verifier deviates from the Contract.

**Does not prove:** Independent Verification; that the Validator is correct in general; that the Contract is complete; that the Protocol is complete.

## 15. Final Gate

```text
PHASE 3 FINAL GATE: PASS
Trust Label: SAME_FAMILY_REVIEW
```

Deferred and not started: Contract v2, optional source-integrity capability, GPT-6/Codex family review (additive, on the same sealed inputs and Contract), Governing Spec Resolver, Human Gate/authority channel, Task positive path, signing/ACL, and Phase 4.
