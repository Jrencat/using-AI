# Phase 3 Step 4 — Differential Verification

```text
PHASE 3 STEP 4 GATE: PASS   (classifications pending Human confirmation at Closeout, E7)
Label: SAME_FAMILY_REVIEW   (NOT INDEPENDENT_VERIFICATION)
Contract / Validator / Old verifier / Expected / Corpus / Human digest: unmodified during this step
Fixes made: NONE   (no v2; only the v1 round exists; an identical re-run is kept separately)
```

## 1. Inputs and Hashes (verified unchanged before and after)

| Item | SHA-256 |
| --- | --- |
| New validator `D:\phase3-iso\validator.py` (v1) | `5fa40eccb4ebbc52aacfcde575f067c7e52a855ada5587e2eabb42ac3ceec856` |
| Old `harness/chain_verifier.py` | `8d134a1c3db1f9a6d07b247955fd1debd24d2dcfef837d18671e88bc7c6b4c42` |
| `verification-contract.md` | `e5139d68eb796f4829ce40d2da18140358735cc53723a35b4c9ccf15ee154aa4` |
| `external-digest-record.json` (Human) | `325cbbe89c38520520bad496a0ed642baa64d9b660f24383fe758c9aeacc14f3` |
| `expected.json` (pre-registered) | `f5bf2b10…` (matches `negative-corpus-record.json`) |

Corpus lock intact (85 files); the two Phase 2 packages still match the Human digest. Raw results: `phase-3-validation/differential-results-v1.json`; byte-identical re-run: `differential-results-v1-rerun.json` (both verifiers, all findings equal → reproducible). Runner: `phase-3-validation/run_differential.py`.

Execution notes: the old verifier takes `--claim ID=STATE` (equivalent input to Contract `--claims`) and has **no digest input**. For `NONE` cases the new validator was given a path to a non-existent digest record (the CLI requires the argument; absence is what the Contract's I1 defines). "TEST_FIXTURE_DIGEST" = digest generated for the mutated package (N07: Human record with one hash altered); it is never a Human anchor.

## 2. Matrix (18 cases)

Anchor = anchor status reported by the new validator. Integrity = I-rules; Semantic = E/S/R/C-rules.

| Case | Digest type | Anchor | Integrity result | Semantic result | Expected | Old | New | Classification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P01 | HUMAN | VERIFIED | pass | pass | PASS | PASS | PASS | AGREEMENT |
| P02 | HUMAN | VERIFIED | pass | S4 INSUFF | INSUFFICIENT | INSUFFICIENT | INSUFFICIENT | AGREEMENT |
| P03 | HUMAN | VERIFIED | pass | C1 holds | PASS | PASS | PASS | AGREEMENT |
| P04 | NONE | ABSENT | I1 INSUFF | pass | INSUFFICIENT | **PASS** | INSUFFICIENT | D1 |
| N01 | HUMAN | MISMATCH | I2, I3 FAIL | – | FAIL | FAIL | FAIL | AGREEMENT |
| N01b | HUMAN | MISMATCH | I2, I3 FAIL | S4 INSUFF | FAIL | FAIL | FAIL | AGREEMENT |
| N02a | FIXTURE | VERIFIED | pass | S2 FAIL, S5 FAIL | FAIL | FAIL | FAIL | AGREEMENT |
| N02b | FIXTURE | VERIFIED | pass | E1 FAIL | FAIL | FAIL | FAIL | AGREEMENT |
| N03 | FIXTURE | VERIFIED | pass | R1 INSUFF | INSUFFICIENT | **FAIL** | INSUFFICIENT | D2 |
| N04 | FIXTURE | VERIFIED | pass | R1 INSUFF | INSUFFICIENT | INSUFFICIENT | INSUFFICIENT | AGREEMENT |
| N05a | FIXTURE | VERIFIED | I3 FAIL | – | FAIL | FAIL | FAIL | AGREEMENT |
| N05b | FIXTURE | VERIFIED | I6 FAIL | – | FAIL | **PASS** | FAIL | D3 |
| N06a | HUMAN | MISMATCH | I2 FAIL | (would pass) | FAIL | **PASS** | FAIL | D1 |
| N06b | NONE | ABSENT | I1 INSUFF | (would pass) | INSUFFICIENT | **PASS** | INSUFFICIENT | D1 |
| N07 | FIXTURE (Human record, 1 hash altered) | MISMATCH | I2 FAIL | pass | FAIL | **PASS** | FAIL | D1 |
| N08 | HUMAN | VERIFIED | pass | C1 INVALID | INVALID_AGENT_RESULT | INVALID_AGENT_RESULT | INVALID_AGENT_RESULT | AGREEMENT |
| N09 | FIXTURE | VERIFIED | pass | S5 INSUFF | INSUFFICIENT | **FAIL** | INSUFFICIENT | D2 |
| N10 | FIXTURE | VERIFIED | pass | S3 FAIL | FAIL | **PASS** | FAIL | D4 |

Totals: **New = Expected on 18/18.** Old = Expected on 10/18. New ≠ Old on 8 cases (P04, N03, N05b, N06a, N06b, N07, N09, N10). No case failed to execute (`EXECUTION_ERROR`: 0). Old exits 1 on any non-PASS verdict (its convention); not a divergence.

Required checks: N01/N01b — external Human digest alone rejects a modified package (I2). N02a — with a fixture digest the anchor is VERIFIED and integrity passes, so the verdict comes from S2/S5 (not I2). N03/N04 — missing/unlinked receipts give `INSUFFICIENT`, not `FAIL`, in the new validator (R1). N06a — a fully self-consistent forgery is rejected only by the Human digest (I2): internal consistency ≠ anchored authenticity. N06b — same package without an anchor is `INSUFFICIENT`, not `PASS`. N08 — C1 gives `INVALID_AGENT_RESULT`; no higher-precedence FAIL present. N09 — S5 `INSUFFICIENT`. N10 — S3 `FAIL`.

## 3. Divergence Analysis

Order of judgment: Contract → evidence/input → Expected → old → new. In every divergence Contract = Expected = New; Old is the outlier.

**D1 — P04, N06a, N06b, N07: old `PASS`, contract `INSUFFICIENT`/`FAIL`.** The old verifier has no digest input, so it can neither report anchor `ABSENT` (I1) nor detect a digest mismatch (I2). It checks only hashes stored inside the package. For N06a that is exactly the self-consistent-forgery hole the Contract exists to close. *Classification:* `EXISTING_VERIFIER_BUG`, sub-type **capability gap** (`OLD_VERIFIER_CAPABILITY_GAP`): the old verifier predates the Contract's anchor requirement; it is not a defect against its own original design. Corpus/Expected not at fault.

**D2 — N03, N09: old `FAIL`, contract `INSUFFICIENT`.** Old also reports the contract's insufficiency (`no Runtime receipt…` / `no recorded ELIGIBLE rejection`) but additionally raises `sealed runtime differs from source slice`: it opens `run.json.source`, the live Claude session file, and compares. That input is outside Contract §2, which forbids opening it; with FAIL > INSUFFICIENT precedence, the extra check turns the verdict into `FAIL`. *Classification:* `EXISTING_VERIFIER_BUG` (sub-type: reads outside the Contract's input set). Not a Corpus error: the mutation is a real package rewrite that would legitimately differ from the live source. *Observation for Human (no change made):* the old check is stronger evidence (it catches resealed rewrites even without a digest). The Contract chose package-only inputs; whether to allow an optional source cross-check is a **Contract design decision**, not decided here.

**D3 — N05b: old `PASS`, contract `FAIL` (I6).** Old does not compare `manifest.runtime_inventory.row_count` with the Runtime rows. *Classification:* `EXISTING_VERIFIER_BUG`, capability gap (missing inventory-consistency check).

**D4 — N10: old `PASS`, contract `FAIL` (S3).** Old does not enforce "a Critical Question cannot be ASSUMED" (Protocol hard rule, state-model §1.1) when replaying the chain. *Classification:* `EXISTING_VERIFIER_BUG`, capability gap.

Claims: both support the equivalent input; N08 agrees. Old has no digest-related capability (covered by D1). No `NEW_VALIDATOR_BUG` found. No `TEST_CORPUS_ERROR`: each Expected equals the Contract-derived verdict and the new validator reached it from the Contract alone. No `EVIDENCE_AMBIGUITY` surfaced in the 18 cases.

## 4. Contract Gaps Reported by the Validator (not exercised by the 18 cases)

Contract not modified. Each judged against the text; none produced a divergence.

| # | Item | Does the Contract decide? | Classification |
| --- | --- | --- | --- |
| 1 | Extra files in package dir | §2 says "exactly the four files" but no verdict on violation; only the §3 catch-all (`INSUFFICIENT`). New: INSUFFICIENT (consistent with catch-all). | CONTRACT_GAP (minor; arguably should be FAIL) |
| 2 | Digest entry lacks a hash for one file | I1/I2 speak of missing *package* files, not missing *record* entries; catch-all applies. New: anchor ABSENT/INSUFFICIENT. | CONTRACT_GAP (minor) |
| 3 | Duplicate creation of the same object id | E4 covers references to non-existent objects only; catch-all. New: INSUFFICIENT. | CONTRACT_GAP (arguably FAIL) |
| 4 | Unknown event type | E3 decides: `INSUFFICIENT`. New complies. | Decided — no gap |
| 5 | S5 when Task was already `BLOCKED` before the rejection and never changes | S5 is internally inconsistent: "after it the recorded state is BLOCKED" (satisfied) vs "including no BLOCKED change is FAIL" (violated). New chose INSUFFICIENT, which matches neither literal reading. | CONTRACT_GAP (wording conflict) |
| 6 | R2 and Runtime rows without `sessionId` | I7 says such rows are never evidence; R2 says "no tool_use in Runtime evidence". Whether R2 scans them is unstated. New scans all rows (stricter). | CONTRACT_GAP / EVIDENCE_AMBIGUITY |

Gaps 1–3, 5, 6 are candidates for a Contract v2 decided by the Human. They did not affect any pre-registered case, so the Step 4 verdict does not depend on them; they are recorded as limits on how far "the Contract alone determines the verdict" has been shown.

## 5. Gate Conditions

| # | Condition | Result |
| --- | --- | --- |
| 1 | 18 cases executed | yes (0 execution errors) |
| 2 | Expected complete, hash unchanged | yes |
| 3 | Old and New both executed | yes |
| 4 | Every divergence classified | yes (D1–D4) |
| 5 | No unexplained divergence | yes |
| 6 | Contract not edited to remove a divergence | yes (hash unchanged) |
| 7 | New validator did not read old implementation | yes (Step 3 transcript check; static: stdlib imports only; no further sessions run) |
| 8 | Human digest unmodified | yes |
| 9 | Phase 2 packages unmodified | yes |
| 10 | Matrix complete | yes |

## 6. Limits

- Expected, Corpus and Contract share an author; New agreeing on 18/18 shows the Contract was sufficient *at these 18 points* for a context-isolated implementer, not that it is complete (§4).
- The isolated session saw its own outputs on the two real packages (Step 3 note).
- Same model family: `SAME_FAMILY_REVIEW` only.
- Not yet done (Closeout): Evaluation-shaped record (E6), Human Verification (E7), E8 diff check, final label ruling.
