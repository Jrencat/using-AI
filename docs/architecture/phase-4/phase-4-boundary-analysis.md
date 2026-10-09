# Phase 4 Boundary Analysis (DRAFT)

```text
STATUS:   ANALYSIS ONLY — not a Phase 4 Spec. No implementation, no Run, no test.
PROTOCOL: FROZEN (protocol.md, state-model.md unmodified)
PHASE 1D: INSUFFICIENT — CLOSED   PHASE 2: PASS / CLOSED   PHASE 3: PASS / CLOSED (SAME_FAMILY_REVIEW)
PHASE 4:  NOT STARTED (this document does not start it)
INPUTS:   HANDOFF.md, protocol.md, state-model.md, evidence.md, routing.md,
          phase-1d-closeout.md, phase-2-closeout.md, phase-3-closeout.md,
          phase-3-boundary-analysis.md, verification-contract.md, phase-3-evaluation.json,
          harness/harness.py (read for state-machine facts only)
```

Not read / not present: root `MEMORY.md` (does not exist; not created). `docs/architecture/phase-4/` did not exist before this document.

## 1. Question

> What is the smallest, non-substitutable boundary that no Phase 1–3 evidence covers, and that can be proven without turning Phase 4 into Harness/Runtime construction?

## 2. A. Proof boundary of Phase 1–3

Vocabulary (descriptive only, no new Protocol terms):
`DESIGNED` = specified in docs · `EXECUTABLE` = code path exists · `VALIDATED` = deterministic/synthetic tests or corpus pass · `PROVEN` = observed in a real captured run and verified, within a stated boundary · `DEFERRED` = explicitly not done.

| Capability | Level | Basis / what is NOT shown |
| --- | --- | --- |
| Protocol objects, states, invariants | DESIGNED (frozen) | Most edges never executed (Spec states, Evaluation store, Evidence DISPUTED, Routing) |
| Requirement investigation via tools | PROVEN (partial, 1D: A/B/K/L/O, P-D-04 Read) | Agent *judgment* (ask vs investigate, Critical-vs-assume) not proven; Phase 2.2 told the Agent what to do |
| Question `OPEN→ASSUMED` → Assumption `ISOLATED` → gated Task → ELIGIBLE refused → `BLOCKED` | PROVEN (one chain, `PH2-VSC-01`, one live run) + VALIDATED (27 + 8 tests) | One chain shape; one headless run; operator-supplied claims |
| Runtime capture (start→capture→seal→verify) | PROVEN ×2 (`PH2-QUAL-01`, `PH2-VSC-01`) | Claude JSONL only; headless only; sessionId-less rows live: SYNTH only |
| State-event ↔ Runtime receipt correlation | PROVEN (6/6 event_ids in `tool_result`) | String match; no adversarial Agent |
| Fail-closed verifier verdicts | VALIDATED | Same-author tests |
| Verdict reproducible from (package + Human digest + Contract v1) | PROVEN within v1 / 18 cases, `SAME_FAMILY_REVIEW` | Not general correctness; Contract completeness unproven; 5 `CONTRACT_V2_CANDIDATE`s open |
| External Human digest as integrity anchor | PROVEN (N06a self-consistent forgery rejected) | Anchors bytes, not how the package formed |
| Human Gate (sync `AskUserQuestion` observe) | EXECUTABLE + VALIDATED (SYNTH); 1D partial | Async/queryable gate, promotion/authorization loop, *who may write the decision* |
| Task `DRAFT→ELIGIBLE|BLOCKED` | EXECUTABLE (`harness.py:141-150`); BLOCKED branch PROVEN | ELIGIBLE branch never observed live |
| Task `ELIGIBLE→IN_PROGRESS→EVALUATING→DONE/FAILED/RISK_PENDING` | DESIGNED only | No code, no run |
| **Scope enforcement / Task Boundary** | **DESIGNED only** | `scope` is required non-empty at creation (`harness.py:134`) and compared with nothing. 1D Task Boundary = INSUFFICIENT; no later phase revisited it |
| Assumption promotion/rejection | DESIGNED (harness comment: out of scope) | — |
| Evaluation / Evidence record | One hand-authored Evaluation-shaped file (`EVAL-PH3-001`) | No store, no generation |
| `INDEPENDENT_VERIFICATION` tier | DEFERRED — never reached | Highest label reached: `SAME_FAMILY_REVIEW` |
| Governing Spec Resolver, second Runtime, signing/ACL, Contract v2, source-integrity check, MCP/SDK/Registry/Orchestrator/Event Bus/UI/DB/CLI | DEFERRED | — |

Phase-by-phase, one line each:

- **Phase 1**: design + attack; behavior probes mostly `INSUFFICIENT` (1D). Proved the Protocol is not contradicted; proved little about execution.
- **Phase 2**: a minimal Harness can capture a real Agent and enforce the **blocking branch** of the throughline.
- **Phase 3**: the verdict on a sealed run is a function of (package, Human digest, Contract), not of the implementer's private knowledge.

**Observation (fact, not a decision):** harness events `TASK_ROUTING_SET` and `GATE_*` are not in Contract v1 Appendix A; per E3 any package containing them is `INSUFFICIENT` under v1. Current verification cannot judge Human-Gate or routing runs.

## 3. B. Largest unverified boundary

The throughline is *"unconfirmed ≠ working code."* Phases 2–3 proved only the half where the Harness **refuses a state change**. Nothing has ever verified the other half: **what an Agent actually changed in the workspace versus what the Task authorized.** Contract R2 only rejects any `Edit/Write` tool in the chain run; it is not a scope check, and tool-name matching is bypassable (Phase 2.1: the Agent used `PowerShell`, and Runtime permission rules did not bound it).

Deferred items considered, and why each is or is not Phase 4 material:

| Deferred item | Verdict |
| --- | --- |
| Task positive path + Scope enforcement | **Candidate** — the only unproven half of the core throughline |
| Human Gate / authority channel | **Candidate** — high importance, but see C2 risk |
| Second Runtime | **Candidate** — but premature, see C3 |
| Governing Spec Resolver | Not a candidate: Phase 2/3 analyses showed the core throughline never needed it; forces storage/identity decisions the Protocol left open (§16). Serves Convention only |
| Evidence/Evaluation store | Not a candidate: generic Evidence engine is a Protocol §15 non-goal; the needed fragment (one Evaluation-shaped record) already exists |
| Signing/ACL | Not a candidate: crypto/ACL infrastructure; the Human digest already covers the minimal need |
| Contract v2 / source-integrity cross-check | Not a candidate: maintenance of Phase 3 (reopens its proof target) |
| GPT-6/Codex review of Phase 3 | **Rejected** — see §8 |

## 4. C. Candidates (max 3)

### C1 — Scope Boundary Conformance

| Field | Content |
| --- | --- |
| Boundary | Task authorization (state + `scope`) → what the Agent actually changed in the workspace |
| Why now | The throughline's second half is unproven; Phase 3 produced the reusable pattern (Human-held external digest + deterministic Contract-style verdict + pre-registered negatives); 1D's Task Boundary `INSUFFICIENT` was caused by lack of a baseline, which is solvable without new Protocol |
| Would prove | For an `ELIGIBLE` Task with declared scope S and an anchored baseline B: files changed (added/modified/deleted) ⊆ S. For a `BLOCKED` Task (P2 or ISOLATED dep): no file in its scope changed. Violation → verdict `FAIL`; missing evidence → `INSUFFICIENT`; Agent claim ≠ diff → `INVALID_AGENT_RESULT` |
| Would NOT prove | Prevention (this is detection, not enforcement at write time); Agent judgment or code quality; the full Task positive path / `DONE`; Evaluation→`DONE/RISK_PENDING`; writes outside the observed root; Independent Verification |
| Required inputs | Fixture workspace; a Task event with `scope` and state; Harness/tool-produced baseline and post manifests (path → SHA-256); Runtime capture of the Agent run; Human-held baseline digest; (optional) Agent claim |
| Required evidence | See §7 |
| Minimal experiment | 1 real Claude run on a small fixture with an `ELIGIBLE` P0/P1 Task, scope = 1 file, Agent edits it → in-scope diff, verdict `PASS`. Same run also has a `BLOCKED` Task whose scope file must stay unchanged. Negative cases via a pre-registered mutated corpus (Phase 3 method): out-of-scope modify/add/delete, change under a `BLOCKED` Task, missing post manifest, baseline mismatch vs Human digest, claim mismatch |
| Expected gate | PASS if live positive verdict + 100% pre-registered negatives match; else INSUFFICIENT (Phase 1D stop rule) |
| Dependencies | Manifest capture (baseline/post) — a new artifact, preferably standalone as in Phase 3, not a `harness.py` change; a scope-matching rule (file/prefix semantics) decided by the Human; a verification contract for this chain shape (a *new* document; Contract v1 stays unmodified) |
| Risk | Scope creep into a full Task state machine / write-time enforcement (mitigated by OUT OF SCOPE list); scope-match semantics for "module" granularity; live Agent may not edit as expected (Environment/Fixture) |
| Size vs alternatives | Smaller than C2 and C3: needs no principal/identity model and no second transcript format. The filesystem diff does not depend on parsing tool names |

### C2 — Human Authority Channel (Assumption promotion)

| Field | Content |
| --- | --- |
| Boundary | A state change that only a Human may cause (`PROMOTED`, `BLOCKED→ELIGIBLE`) → proof the Agent could not have caused it |
| Why now | Human Authority is "non-negotiable"; Phase 3 gave an anchor pattern; `gate-observe` already exists |
| Would prove | A promotion event is accepted only when correlated with an observed Human answer in the Runtime, and an Agent-originated promotion is rejected |
| Would NOT prove | Identity/authentication of the Human; async queue; tamper-proof authority |
| Required inputs | Interactive Claude session (headless `claude -p` cannot answer `AskUserQuestion`); promotion command; Contract for Gate events (v1 yields `INSUFFICIENT` on them) |
| Minimal experiment | Live interactive run: Agent asks, Human answers, Harness records promotion; negative: Agent calls promotion directly |
| Expected gate | PASS only if "Agent cannot call it" is demonstrable — Phase 3 analysis §5-B: Agent and operator share one OS account and one CLI, so this is not currently demonstrable without inventing a principal/auth channel |
| Dependencies | New Harness command; role boundary whose violation is detectable (not yet defined); interactive session |
| Risk | High: auth-system creep; Environment-dependent; likely ends `BLOCKED`/`INSUFFICIENT` |
| Size vs alternatives | Larger than C1 (needs a prerequisite C1 does not) |

### C3 — Second Runtime receipt abstraction

| Field | Content |
| --- | --- |
| Boundary | Protocol/Harness verdicts → a non-Claude Runtime transcript |
| Why now | "Model-agnostic" is the project headline and has zero evidence |
| Would prove | Capture + verify works for one Codex session using a Runtime-neutral receipt (tool call, result, event_id) |
| Would NOT prove | Anything about Scope, Gate, or the throughline; Independent Verification of Phase 3 |
| Required inputs | Codex session transcript format; adapter; quota |
| Minimal experiment | One Codex run, adapter, sealed package, verifier verdict |
| Expected gate | Likely `INSUFFICIENT`/`BLOCKED` (quota, format unknown) |
| Dependencies | Transcript adapter (adapter-framework risk); Contract Appendix A is currently Claude-row-shaped, so neutral receipts need a contract change |
| Risk | High; format and quota unknowns |
| Size vs alternatives | Larger than C1: adds a format adapter and does not advance the core throughline. Becomes cheaper after C1 clarifies what a receipt must contain |

## 5. D. Recommended minimal Proof Target

```text
Phase 4 Proof Target (recommended): C1 — Scope Boundary Conformance
Property: the workspace change set of a run is verifiably a subset of what the Task's
state and scope authorized — as a function of (anchored baseline, post manifest, Task
events, Runtime capture), not of the Agent's account.
```

1. **Why this boundary.** It is the only unproven half of the core throughline; deterministic; needs no Protocol change; no identity model; reuses the Phase 3 pattern as a *method* without redoing Phase 3's proof; independent of Claude-specific tool naming.
2. **Why not the others (for now).** C2: prerequisite (a detectable role boundary) is missing; its likely outcome is `BLOCKED`. C3: format adapter plus quota, does not advance the throughline. Resolver, store, signing, Contract v2, GPT/Codex review: see §3 and §8.
3. **Success conditions.** (a) live positive run: in-scope change → `PASS`; `BLOCKED`-Task scope unchanged; (b) every pre-registered negative returns its pre-registered verdict (FAIL / INSUFFICIENT / INVALID_AGENT_RESULT); (c) no PASS without anchored baseline and post manifest; (d) Human Verification recorded; (e) Protocol/Harness/Phase 1–3 artifacts unchanged.
4. **Failure conditions.** A confirmed counterexample: an out-of-scope or unauthorized change that yields PASS, or PASS issued with missing evidence. Gate then is `FAIL` for the checker/design, not for the Agent.
5. **Harness Gap**: the Harness/tooling cannot produce a baseline/post manifest or cannot bind it to a run (expected and acceptable as a finding; it does not itself downgrade the Protocol).
6. **Protocol Gap**: only if a case exists where frozen Protocol rules (Task scope as hard boundary §5.4; Fail Closed §9) give contradictory or no answer *and* Harness/Runtime cannot resolve it. Presumption: NO; Phase 4 must not edit Protocol.
7. **Evidence Gap**: capture `INCOMPLETE`, manifest absent, unanchored baseline, transcript lacks the needed events. Verdict `INSUFFICIENT`, never PASS.
8. **Environment / Fixture Problem**: fixture mis-set (scope file missing, cwd mismatch as in P-D-04), permission denial blocks the Agent before it edits, session/binding errors.
9. **Agent Execution Error**: only when the Agent demonstrably had the capability and instructions and did something contrary (e.g. edited outside scope). Per 1D discipline, absent proof → `NOT PROVEN`. An out-of-scope edit is a *valid positive finding for the checker*, not a failure of the phase.

## 6. E. Scope

**IN SCOPE**
- A Scope Conformance verification contract for one chain shape (new document; Contract v1 untouched).
- Baseline/post file-hash manifests of a fixture, Human-anchored baseline digest.
- A deterministic conformance checker (standalone artifact, no import of `harness.py`/`chain_verifier.py`).
- One live Claude run with an `ELIGIBLE` and a `BLOCKED` Task; a pre-registered negative corpus; one Evaluation-shaped record outside the package; Human Verification.

**OUT OF SCOPE**
- Any change to Protocol, `harness.py`, `chain_verifier.py`, Contract v1, Phase 1–3 artifacts, `PH2-*`/`PH3-*` runs.
- Write-time enforcement/sandboxing; Task `IN_PROGRESS→DONE` machine; Evaluation→DONE/RISK_PENDING.
- CLI, MCP, SDK, Registry, Orchestrator, Event Bus, UI, DB/cloud, production Runtime.
- Re-running or extending Phase 3 proofs (E6/E8, differential, Contract v2).

**DEFERRED**
Human Authority channel (C2) · second Runtime (C3) · Governing Spec Resolver · Assumption promotion · Evidence/Evaluation store · signing/ACL · GPT-6/Codex family review · source-integrity check · Contract v2 · writes outside the observed root.

**Open decisions for the Human (not decided here):** scope-match semantics (exact path vs prefix/glob; treatment of created/deleted files; "module" granularity); whether the checker is standalone or an extension of `chain_verifier.py`; whether a context-isolated authoring session is wanted (otherwise label stays `TOOL_GENERATED` + `HUMAN_VERIFICATION`, not an independence claim).

## 7. F. Proof Architecture (future, not implemented)

```text
Human Authority      anchors baseline digest + scope-match rule before the run
      ↓
Input                fixture workspace + Task events (scope, state: ELIGIBLE / BLOCKED)
      ↓
Agent / Runtime      real Claude edits the fixture (captured by existing Phase 2.1 capture)
      ↓
Harness Boundary     baseline manifest (start) / post manifest (seal), bound to the run
      ↓
Evidence             manifests + diff + Runtime transcript + Agent claim (as claim only)
      ↓
Independent Verif.   deterministic checker per the new contract (NOT claimed independent)
      ↓
Evaluation           one Evaluation-shaped record outside the package
      ↓
Gate                 PASS / FAIL / BLOCKED / INSUFFICIENT
```

## 8. H. Anti-scope-creep checks

1. **Phase 3.1?** Rejected. Any step that edits Contract v1, fixes the old verifier, re-runs the 18 cases, or re-judges `PH2-*` packages is Phase 3.1. C1 has a different subject (workspace change vs authorization), a different chain shape, and a new contract.
2. **GPT-6/Codex review as Phase 4?** Not automatic, and not recommended. Phase 3 closeout labels it additive/optional on the *same* sealed inputs and Contract: same proof target, only a stronger trust label. It uplifts Phase 3 (an addendum), and does not open a new boundary. It may be run any time as an addendum without a Phase 4.
3. **Full Harness because it is weak?** Rejected. The checker is a standalone artifact; Harness gaps are recorded as findings.
4. **Contract v2 because candidates exist?** Rejected. The new contract is a separate document for a different chain; the five v1 candidates stay deferred.
5. **Designed ≠ proven.** Scope enforcement is DESIGNED; nothing here upgrades it until a live run + verification exist.

Residual risk: C1 is detection after the fact; an Agent can still write outside the observed root, and tamper-resistance remains hash-based (no signing/ACL).

## 9. G. Evidence design

| Class | Content for C1 | Needed for PASS? |
| --- | --- | --- |
| Agent Claim | Agent's list of files touched / "stayed in scope" | No. Used only to detect `INVALID_AGENT_RESULT`; never sufficient |
| Runtime Evidence (`RUNTIME_GENERATED`) | Captured transcript, `COMPLETE_WITHIN_BOUNDARY`, paired tool_use/tool_result, event receipts | **Yes** (capture complete; otherwise `INSUFFICIENT`) |
| Tool Evidence (`TOOL_GENERATED`) | Baseline and post manifests (path → SHA-256), deterministic diff, Task events with scope/state | **Yes** (both manifests, bound to the run) |
| Independent Verification | A different agent/process re-deriving the verdict | No — not required, not claimed. A same-family re-derivation would be `SAME_FAMILY_REVIEW` at most |
| Human Verification | Human-held baseline digest recorded before the run; spot-check of diff against transcript | **Yes** (anchor absent → at best `INSUFFICIENT`) |

Rule: absent any "Yes" item → `INSUFFICIENT`, never PASS. Highest label claimable: `TOOL_GENERATED` + `HUMAN_VERIFICATION`; never `INDEPENDENT_VERIFICATION`.

## 10. Proposed Phase 4 gate (for Human approval)

| Gate | Meaning |
| --- | --- |
| PASS | §5.3 (a)–(e) all hold; evidence per §9 complete |
| FAIL | Counterexample to the property (false PASS on out-of-scope/unauthorized change or on missing evidence) |
| BLOCKED | A Human decision/authority is required and missing (scope-match rule, baseline anchor, label ruling); no inference, work stops |
| INSUFFICIENT | Run/evidence incomplete (capture INCOMPLETE, no post manifest, no live run, only synthetic evidence). Stop rule (1D discipline): the same failure class twice → close as INSUFFICIENT; do not chase PASS |

## 11. Limits of this analysis

- Based on documents and a read of `harness.py` state logic; no experiment run.
- C2/C3 feasibility judgments rest on Phase 1D–3 records; not re-tested.
- HANDOFF §H still says last commit `5068b95` and Phase 3 uncommitted; HEAD is `91c5c59` (stale, not edited here).
- The recommendation is a draft for Human decision; it is not a Phase 4 Spec.
