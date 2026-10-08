# Phase 3 Boundary Analysis

```text
STATUS:   ANALYSIS ONLY — no implementation, no Run, no Harness change
PROTOCOL: FROZEN (protocol.md, state-model.md unmodified)
PHASE 1D: INSUFFICIENT — CLOSED, not reopened
PHASE 2:  FINAL PASS / CLOSED, not reopened
PHASE 3:  NOT STARTED (this document does not start it)
INPUTS:   HANDOFF.md, protocol.md, state-model.md, phase-1d-closeout.md, phase-1d-handoff.md,
          phase-2-boundary-analysis.md, phase-2-1-*, phase-2-2-*, phase-2-closeout.md,
          harness/chain_verifier.py (read for verifier scope only)
```

## 1. Question

Not "what can the Harness add next?" but:

> What is the smallest, non-substitutable next piece of evidence that keeps the Protocol/Harness architecture *falsifiable*?

## 2. Capability / Evidence Matrix (Phase 1 → Phase 2)

Evidence levels used here (descriptive only, no new Protocol vocabulary):
`DESIGN` = analysis/simulation only · `SYNTH` = deterministic synthetic tests · `LIVE-1` = one real Claude run · `HV` = Human Verification done · `SELF` = Agent self-report only.

| # | Capability | Phase | Proven | Level | Not proven (≠ "should build") |
| --- | --- | --- | --- | --- | --- |
| 1 | Protocol semantic integrity | 1A–1C, 2 | Internally consistent after 1C; cross-agent review PASS WITH GAPS; two live Harness slices found no contradiction | DESIGN + LIVE-1 | Most semantics never executed: Spec states, Evaluation, Evidence DISPUTED, Routing, most Task/Assumption edges |
| 2 | Requirement Intelligence | 1D | Investigation via Read/Grep VERIFIED from raw JSONL (A/B/K/L/O, P-D-04) | LIVE (1D, partial) | "Ask only what investigation cannot resolve"; Critical-vs-assume judgment by an Agent; value vs legacy pipeline (U6). Phase 2.2 *told* the Agent what to do — it did not test judgment |
| 3 | Question state | 2.2 | `OPEN→ASSUMED` persisted, receipted; Critical→ASSUMED rejected (SYNTH, `validate`) | LIVE-1 + SYNTH | `ANSWERED / BLOCKED / INVALID` live; BLOCKED↔Human Gate loop |
| 4 | Assumption state | 2.2 | Created `ISOLATED` from an ASSUMED Question, `origin_question_id` carried | LIVE-1 | `CHALLENGED / PROMOTED / REJECTED` — harness comment: "promotion needs a Human Gate and is out of scope" |
| 5 | Task state | 2.2 | `DRAFT→BLOCKED` on ISOLATED dep / P2; ELIGIBLE refused (exit 1); BLOCKED cannot be re-eligibilized via CLI | LIVE-1 + SYNTH | Whole positive path (`ELIGIBLE→IN_PROGRESS→EVALUATING→DONE/FAILED/RISK_PENDING`); Scope enforcement; absolute circuit-break at creation |
| 6 | Runtime capture | 2.1, 2.2 | start→capture→seal→verify, `COMPLETE_WITHIN_BOUNDARY`, byte-equal slice, hashes match; two runs | LIVE-1 ×2 + HV | Interactive sessions; sessionId-less rows live (SYNTH only); any non-Claude transcript format |
| 7 | State/runtime correlation | 2.2 | All 6 state `event_id`s found in Runtime `tool_result` receipts (PowerShell and Bash) | LIVE-1 + HV | Receipts are string-matched; no adversarial Agent tested |
| 8 | Fail-closed enforcement | 2.2 | Missing receipt/rejection→INSUFFICIENT; claim conflict→INVALID_AGENT_RESULT; forged ELIGIBLE→FAIL; direct edit detected | SYNTH (8 verifier tests) | Only for the single VSC chain shape; only what the same author thought of |
| 9 | Seal / verify | 2.1, 2.2 | Package integrity via hashes | LIVE-1 + SYNTH | Hashes are package-internal: a self-consistent rewrite (events + manifest recomputed) is not detectable; no signing/ACL/external anchor |
| 10 | Human Verification | 2.1, 2.2 | Done on both runs by inspecting raw transcripts | HV | Not a scalable mechanism; not recorded as a Protocol object |
| 11 | Independent Verification | 2.2 | **Nothing.** `chain_verifier.py` is `TOOL_GENERATED`, same-author | — | The tier `INDEPENDENT_VERIFICATION` has never been reached by any run |
| 12 | Governing Spec | 1C | Resolver mandated as Harness capability; Convention persistence obligation | DESIGN | No resolver; P-G/P-H used substitutes |
| 13 | Human Gate | 1D, 2 | Sync `AskUserQuestion` observed; gate-observe code exists | SYNTH + 1D partial | Async/pending queryability (Claude limit); promotion/authorization loop; *who may write the decision* |
| 14 | Convention | 1C | Only via explicit Human Confirmation; persisted via Spec | DESIGN | Everything (depends on #12) |
| 15 | Evidence / Evaluation | 1A, 2.2 | Trust tiers used as vocabulary; verifier emits PASS/FAIL/INSUFFICIENT/INVALID_AGENT_RESULT as CLI JSON | DESIGN + SYNTH | No Evidence or Evaluation record is ever instantiated; verdict has no `collected_by`/`trust_tier`/`evidence_refs` |

Reading the matrix: Phase 2 proved the **negative/blocking branch** of the throughline ("unconfirmed ≠ code") with a trustworthy capture chain. Rows 9–11 and 15 are the weak spine: *how much the verdict itself can be trusted.*

## 3. Facts about the current verifier (basis for §6)

From `harness/chain_verifier.py` and Phase 2 docs:

- Verdict logic exists only as code; there is **no written contract** saying what a verifier must check or when it must answer INSUFFICIENT.
- It is specific to one chain shape (`next(TASK_CREATED with assumption_deps)`); "no such Task" → INSUFFICIENT.
- Package integrity compares against hashes **stored inside the package**; no digest held outside the Agent's write domain.
- Agent claims are `--claim` values transcribed by the operator.
- Same author as `harness.py`; shares no code, shares all assumptions.
- Phase 2.1 §11: the `Bash(...)` allow rule did not bound execution (Agent used PowerShell). Runtime permission rules are therefore **not** a reliable enforcement boundary; post-hoc transcript inspection is.

## 4. Candidate Comparison

Dimensions: (1) real unproven capability, (2) what semantic stays unprovable without it, (3) tiny slice possible, (4) Protocol change, (5) State Model change, (6) new Runtime capability, (7) real Claude execution, (8) Human Verification, (9) Independent Verification, (10) scope-bloat risk, (11) crisp exit criteria.

| | A Governing Spec Resolver | B Human Gate / Authority loop | C Independent Validator boundary | D Evidence/Evaluation persistence | E Multi-Agent / Model-Agnostic | F Fuller Runtime event system | G Claim ingestion |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | #12, #14 | #4 promotion, #13 | #9, #11, #15 (trust in the verdict) | #15 | Model-Agnostic headline | #5 positive path, Scope | Agent claim→verifier is manual |
| 2 | Convention discovery/persistence | Invariant 2 ("no PROMOTED without Human decision+authority"); BLOCKED→ELIGIBLE | Whether any evidence tier ≥ TOOL_GENERATED can exist; whether verdicts are reproducible by someone else | Core rule "PASS needs Evidence ≥ RUNTIME_GENERATED, cited" as objects | That the Protocol survives a second Runtime | Task Boundary (INSUFFICIENT in 1D), Evaluation→DONE/RISK_PENDING | INVALID_AGENT_RESULT on free-text claims |
| 3 | Yes, but only after choosing storage/identity/cardinality (Harness design decisions) | Code: trivial. Proof: not tiny (see §5-B) | **Yes** | Yes | No (needs transcript adapter) | No (many sub-slices) | No (NL extraction = model judgment) |
| 4 | N | N | **N** | N | N | N | N |
| 5 | N | N | N | N | N | N | N |
| 6 | N | Likely (principal separation) | **N** | N | **Y** (non-Claude capture parser) | **Y** (Edit/scope capture) | N |
| 7 | Y (P-G/P-H) | Y | **No** for Agent run; only a validator-authoring session | N | Y (Codex) | Y | Y |
| 8 | Y | Y (essential) | **Y** | Optional | Y | Y | Y |
| 9 | N | Helpful | **IS the subject** | N | Natural fit | N | N |
| 10 | High | High (auth/identity creep) | **Low–Medium** | Medium (generic evidence engine — a Protocol §15 non-goal) | High (adapter framework) | High (full runtime) | High |
| 11 | Possible, proves little of core claim | Hard: same-OS-account Agent cannot be shown unable to call a command | **Possible** | Possible | Blocked by quota/format | Diffuse | Unclear |

## 5. Candidate Notes

**A — Resolver.** Phase 2 §5 already concluded it serves Convention only; the core throughline (Q→ASSUMED→Assumption→Task gate) never needed it. Proving it first forces storage/identity/cardinality decisions the Protocol deliberately left open (§16). Defer.

**B — Human Gate / Authority loop.** Highest *semantic* importance (Human Authority is "non-negotiable"), but not provable yet. Phase 2 enforcement works because the invariant is a function of **state alone** (dep ISOLATED → refuse). "Only a Human may promote" is a function of **caller identity**, and Agent and operator share one OS account and one CLI; Phase 2.1 showed Runtime permission rules do not bound the Agent. Adding `assumption-promote` would be a command the Agent could also call, so "Harness rejects Agent promotion" cannot be demonstrated without inventing a principal/authority channel — i.e. the start of an auth system. B is blocked on a prerequisite it does not itself contain: *a role boundary whose violation is detectable.* C produces exactly that learning at lower cost, because a validator needs read isolation, not write authority.

**C — Independent Validator boundary.** See §6.

**D — Evidence/Evaluation persistence.** Real gap (#15), but a store is the wrong unit: a general Evidence/Evaluation engine is a Protocol non-goal and bloats. The minimal, *necessary* piece — one Evaluation-shaped verdict record carrying `collected_by`, trust-tier label and `evidence_refs` — falls out of C and needs no store. Absorb that fragment into C; reject D as a standalone target.

**E — Multi-Agent / Model-Agnostic.** Important for the project's headline, premature as a first step. `harness.py` capture is Claude-JSONL-specific (`sessionId`, `toolUseResult`); a second Runtime means a transcript adapter (model adapter framework risk) and depends on quota. Dependency argument: E becomes cheap only if verification is defined against an **abstract receipt** (tool call + result + event_id) rather than Claude row shape. C's contract forces that abstraction. So C reduces E's later cost; E first would not help C.

**F — Fuller event system.** The positive path and Scope enforcement are the *next-most* valuable thing after the verification spine is trustworthy (1D's Task Boundary was INSUFFICIENT). Today it would be built on a verifier only its author has ever checked. Defer; plausible Phase 4 candidate.

**G — Claim ingestion (added).** Automating Agent-claim extraction needs model judgment, reintroducing the non-determinism the Harness exists to remove. Rejected; the contract in C only fixes the *input format* of claims.

**H — Seal hardening (signing/ACL) (added).** Real limit (#9) but crypto/ACL infrastructure. Only a minimal piece is taken into C: an **externally supplied package digest**. Signing/ACL stays deferred.

## 6. Independent Validator Boundary — Analysis

### 6.1 What it is

- **Protocol side (already present):** tier `INDEPENDENT_VERIFICATION` = "produced by a separate agent/process not the one making the Claim". A validator is an **Agent Contract instance** (`applies_to = Evaluation`; allowed: read; forbidden: write state, import implementation) that produces Evidence/Evaluation. It is **not** a new core object and needs no new object.
- **Harness side (missing):** the mechanism and the *recording of independence attributes*. That is a Harness capability.
- Protocol-change test (per Phase 2 §6): existing rule → missing semantics? No. The fields needed already exist (`collected_by`, `trust_tier`, `source`, `evidence_refs`, `decision`). **Protocol stays frozen.**

### 6.2 "Independent of what?" — an ambiguity to document, not to patch in the Protocol

The Protocol text reads independence relative to the **Claim-maker**. Phase 2 applied a stricter reading (independent of the **implementer/family**). These differ. Handled as a **labeling policy** in Harness-level docs, with five axes:

| Axis | Meaning | `chain_verifier.py` today |
| --- | --- | --- |
| Data | Input is the sealed package + externally held digest only | Partial (digest is package-internal) |
| Code | No shared code or source access with the thing verified | Yes (no shared code) |
| Context | Author has no implementation context | **No** |
| Family | Different model family | **No** |
| Authority | Human decision | Separate (HV exists) |

Policy proposed (for Human decision, not a Protocol edit): the label `INDEPENDENT_VERIFICATION` requires Data + Code + Context + Family. A Claude-only run can legitimately reach Data + Code + Context, which keeps Phase 2 §11's name **`SAME-FAMILY REVIEW`** (context-isolated). It must never be reported as `INDEPENDENT_VERIFICATION`.

### 6.3 Is a second model required in Phase 3?

- To **prove the boundary** (inputs, isolation, reproducibility, record): **No.**
- To **earn the tier label**: **Yes** (Family axis). That is an additive uplift on already-sealed inputs, not a Phase 3 prerequisite, and GPT-6/Codex quota should not gate the phase.
- Fallback honesty: two Claude implementations can share a blind spot; the slice does not claim otherwise.

### 6.4 What a Claude-only, deterministic-first proof can show

Property to prove: **the verdict is a function of (sealed package, externally held digest, written contract) — not of the implementer's private knowledge.** Method — contract + blind re-implementation + differential check:

1. Write a **Verification Contract** from the Protocol (what must be checked; when INSUFFICIENT; when INVALID_AGENT_RESULT; input formats; no code detail).
2. A **context-isolated Claude session** implements a validator from the contract + package file format only, without access to `harness.py`/`chain_verifier.py`. Its session is itself captured with the existing Phase 2.1 mechanism so non-access is checked **post-hoc from the transcript**, not by trusting permission rules (the PowerShell lesson).
3. **Differential run:** new validator vs `chain_verifier.py` on the real sealed packages and on a **pre-registered negative corpus** (mutations on copies; expected verdicts hashed before the validator runs).
4. Divergences are findings: contract ambiguity, validator bug, or `chain_verifier` bug — resolved by Human, never by editing to match.
5. Include the known hole as a test: a self-consistent forgery must not yield unqualified PASS without an external digest.

This tests the boundary and the contract's sufficiency. It does **not** test Agent behavior and needs no new Agent run.

## 7. Rejected Directions

MCP, SDK, Plugin, Registry, Orchestrator, Event Bus, Database, Web UI, cloud, multi-agent framework, full CLI, model adapter framework, general runtime: **none unavoidable.** The recommended slice introduces no new framework: one document, one standalone script, one corpus, one record file.

Considered and rejected: **`NO IMPLEMENTATION YET`.** Reason: a Protocol tier (`INDEPENDENT_VERIFICATION`) is unreachable by any current run, the verdict logic has no written contract, and a cheap, non-expanding slice exists. Choose `NO IMPLEMENTATION YET` instead if the Human judges the Claude-only differential check not worth its cost *and* will wait for a second-family reviewer.

## 8. Recommendation

```text
Phase 3 Recommended Target:
Independent Validation Boundary (Claude-only, context-isolated): prove that the verdict on a
sealed run is reproducible from (package + external digest + written contract) by a
validator that had no access to the original verifier's code or context.

Why:
- Every later claim (Human Gate, positive path, second Runtime) will be judged by the same
  verifier whose only reviewer is its author. Row 11 (tier unreachable) and row 15 (verdict is
  not an Evaluation record) are the weak spine of the architecture.
- Cheapest candidate with a sharp pass/fail; needs no Protocol change, no new Runtime
  capability, no new Agent run.
- It forces the Runtime-neutral "receipt" abstraction (reduces future cost of E) and teaches
  what a detectable role boundary is (prerequisite learning for B).

Minimal Slice:
1. Verification Contract document (inputs, checks as properties, verdict conditions, limits).
2. Human records an external digest of sealed PH2-VSC-01 and PH2-QUAL-01 before work starts.
3. Context-isolated Claude session writes a standalone validator from the contract only;
   session captured and sealed with the existing Phase 2.1 mechanism.
4. Pre-registered negative corpus (mutated copies; expected verdicts hashed first).
5. Differential run: new validator vs chain_verifier.py on 2 real packages + corpus.
6. Verdict written as one Evaluation-shaped record outside the sealed package.

Protocol Change:
NONE. (Watch item: the "independent of Claim-maker vs implementer/family" ambiguity is handled
as a Harness labeling policy; revisit only if Human wants a Protocol clarification.)

Harness Change:
None to harness.py or chain_verifier.py. New, separate artifacts only: contract doc, standalone
validator, corpus + expected-verdict manifest, one record file. No shared imports.

Runtime Change:
None. Reuses existing capture to record the validator-authoring session.

Human Verification:
Required: record external digests; inspect validator-authoring transcript for forbidden reads;
review the corpus and pre-registered expectations; adjudicate divergences; rule on the label.

Independent Verification:
NOT CLAIMED. Family axis unmet. Optional additive addendum: GPT-6/Codex re-derives the verdict
from the same sealed inputs + contract when available (no rerun, not an exit criterion).

Exit Criteria:
E1 Verification Contract exists, states INSUFFICIENT / INVALID_AGENT_RESULT / FAIL conditions
   and its own known limits, and uses only the existing verdict vocabulary.
E2 Validator-authoring transcript (captured, sealed, verify clean) shows zero reads of
   harness.py / chain_verifier.py / their tests, and the validator imports neither.
E3 Positive controls: validator and chain_verifier agree on PH2-VSC-01 (PASS) and
   PH2-QUAL-01 (INSUFFICIENT, no applicable chain), run on copies; originals byte-identical.
E4 Negative corpus: validator verdict equals the pre-registered verdict on every mutation,
   covering FAIL, INSUFFICIENT and INVALID_AGENT_RESULT; every divergence from chain_verifier
   is classified and Human-resolved.
E5 Known hole stated, not hidden: a self-consistent forgery does not yield unqualified PASS
   without an external digest; with a wrong digest it yields FAIL.
E6 Verdict stored as an Evaluation-shaped record (claim, evidence_refs, decision, collected_by,
   trust-tier label) outside the package; label is not INDEPENDENT_VERIFICATION unless the
   Human explicitly rules the policy met.
E7 Human Verification recorded for E2, E4 corpus, and label.
E8 git diff empty for protocol.md, state-model.md, harness.py, chain_verifier.py; no Phase 2
   package modified.
Stop rule (Phase 1D discipline): E2 or the same divergence class failing twice → close as
INSUFFICIENT; do not chase PASS.

Deferred:
A Governing Spec Resolver · B Human Gate promotion / authority channel · D Evidence/Evaluation
store · E second Runtime / Codex execution (addendum only) · F positive Task path and Scope
enforcement (likely Phase 4 candidate) · G claim ingestion · H signing/ACL · async Human Gate ·
MCP, SDK, Plugin, Registry, Orchestrator, Event Bus, DB, UI, cloud, multi-agent framework,
full CLI, model adapter framework, general runtime.
```

## 9. Limits of This Analysis

- Based on documents and a read of `chain_verifier.py`; no new experiment was run.
- The recommended slice rests on a Claude-only differential check, which can miss shared misreadings; it strengthens the verification boundary, it does not make it independent in the Protocol's strongest sense.
- Whether E (second Runtime) or F (positive path) ranks second is a Human judgment after Phase 3.
