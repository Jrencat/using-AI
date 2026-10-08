# Phase 2 Boundary Analysis

```text
STATUS: ANALYSIS ONLY — no implementation, no Probe, no Protocol change
PROTOCOL: FROZEN (protocol.md, state-model.md unmodified)
PHASE 1D: CLOSED, not reopened
INPUTS: phase-1d-handoff.md, phase-1d-closeout.md, phase-1d-batch1-implementation-report.md,
        protocol.md, state-model.md, evidence.md, phase-1c/implementation-design-handoff.md
```

## 1. Phase 1 → Phase 2 Transition

- Phase 1A–1C answered: *is the Protocol coherent, closed, and cross-agent consistent?* (design/semantic questions).
- Phase 1D asked a different question: *can a real Agent's protocol-relevant behavior be independently verified?* Answer: **not yet — INSUFFICIENT**, with attribution `Harness=YES, Evidence=YES, Environment=YES, Protocol=NO, Agent Error=NOT PROVEN`.
- Therefore the project's bottleneck moved from **"is the Protocol right?"** to **"can anything the Protocol demands be observed without trusting the Agent?"** Phase 2 is the first phase whose output is *capability*, not documentation.
- Phase 2 is **not** "Phase 1D, retried". New scope, new run namespace, new success criteria (§12).

## 2. What Phase 1 Proved

- Protocol is internally consistent after 1C clarifications (Governing Spec Resolution as Harness capability; Convention persistence via Spec; no new objects).
- Real Agent (Claude) behaviors that are locally verifiable from raw Runtime JSONL: investigation via Read/Grep (A/B/K/L/O, P-D-04 Investigation VERIFIED).
- Human Authority boundary held in observed runs: no fabricated Human answers (P-D-04 Human Authority PASS).
- Raw Claude session JSONL is a usable, sealable evidence source (byte-offset slice + SHA-256 + tool_use/tool_result pairing worked; fixture hashes matched).
- Batch 1 harness exists (13 synthetic deterministic tests): append-only event log, Question/Assumption/Task CLI, gate observer, seal/verify.
- **Meta-finding:** Agent self-report ≠ evidence (G/H/I narratives contradicted by the tool trace). This validates Protocol Evidence tiers empirically — it is a *proof of the Protocol's premise*, not a Protocol failure.

## 3. What Phase 1 Did Not Prove

- Any end-to-end persisted chain `Question → ASSUMED → Assumption(ISOLATED) → Task` produced by a **real** Agent and verified against raw Runtime.
- That an Agent, given a *discoverable and working* state interface, actually uses it (P-D-04's CLI was never offered a usable path — untested, not failed).
- Task absence / routing-before-first-Edit under COMPLETE capture.
- Human Gate pending/answered as an independently queryable state (sync `AskUserQuestion` blocks the Agent turn).
- Real Governing Spec / Convention resolution (P-G/P-H used substitutes).
- That the Protocol's **value proposition** holds: that these gates materially prevent unconfirmed decisions from becoming code, versus the 7-stage prompts.

## 4. Current Unknowns

| # | Unknown | Type |
| --- | --- | --- |
| U1 | Does the Harness's capture/verify path work live (not synthetic) with COMPLETE status? | Empirical, cheap |
| U2 | Will a real Agent call the state CLI when it is discoverable and instructed? Does state match its narrative? | Empirical, needs real run |
| U3 | Can invariants (e.g., "no ELIGIBLE Task with ISOLATED dep") be **enforced by Harness** rather than merely audited? | Engineering, deterministic |
| U4 | Is a Human Gate observable without blocking Agent? | Runtime-dependent, may be unanswerable on Claude Code |
| U5 | Is a Governing Spec Resolver needed at all for the core value claim? | Architectural (answerable by analysis: no) |
| U6 | Does the Protocol beat the legacy pipeline in practice (cost/benefit)? | Long-horizon; not Phase 2 |
| U7 | Can independent validation be trusted without a second model family? | Process, partly unanswerable now |

**Largest unknown that gates everything else: U1+U2** — if the evidence chain cannot be captured and verified live, every later behavioral claim stays `INSUFFICIENT` regardless of Agent quality.

## 5. Phase 1D Harness Gaps Reassessment

| Gap | Blocks core-hypothesis validation? | Needs real implementation to learn? | Verdict |
| --- | --- | --- | --- |
| **H4** Runtime capture/evidence boundary (incl. no-`sessionId` metadata row bug) | **YES** — root cause of INCOMPLETE | Small fix + live qualification | **IN Phase 2** |
| **H2** Question/Assumption/Task state | **YES** — the throughline (unconfirmed ≠ code) lives here | Batch 1 CLI exists; needs Agent-reachable + live receipts | **IN Phase 2** |
| **H3** Human Gate queryability | Partly — but Claude sync `AskUserQuestion` makes full P-I chain unprovable | Runtime limit, not our code | **Reduced**: record Human decisions via *operator-side* write only; defer async query |
| **H5** Independent validation boundary | Limits trust, doesn't block building evidence | Process/permission design | **Partial**: separate operator/Agent/validator roles + read-only validator; no Multi-Agent runtime |
| **H1** Governing Spec Resolver | **NO** for core slice; needed only for Convention (P-G/P-H) | Engineering completeness | **DEFERRED** |

Principle: implement only what changes **whether U1/U2/U3 are answerable**. H1 and full H3 are engineering completeness, not hypothesis validation.

## 6. Protocol / Harness / Runtime Boundary

| Layer | Owns | Phase 2 stance |
| --- | --- | --- |
| **Protocol** | Objects, states, invariants, evidence tiers, Human Authority | **FROZEN.** No contradiction found; every Phase 1D gap is attributable below Protocol. |
| **Harness** | State persistence + transition enforcement, run start/seal, verify, gate observation | Phase 2 work lives here. Enforces invariants deterministically (e.g., reject `ELIGIBLE` with `ISOLATED` dep). |
| **Runtime** (Claude Code) | Tool execution, session JSONL, permissions | Treated as external, read-only evidence source. No hooks/MCP modification. |
| **Agent** | Investigation, Question/Assumption/Task *requests* | Requests only; Harness accepts/rejects. Agent claims never promoted to state. |
| **Evidence/Validation infra** | Sealing, cross-checking receipts vs Runtime | Deterministic verifier = `TOOL_GENERATED`; not Agent-authored. |

Protocol-change test (per brief): *Existing rule → contradiction/missing semantics → unsolvable by Harness/Runtime → Protocol change.* Fails at step 3 for every gap. **Protocol stays FROZEN.**

## 7. Candidate Phase 2 Directions

| ID | Direction | Assessment |
| --- | --- | --- |
| **A** | Implement all H1–H5 (full Harness) | **Rejected.** Pure engineering expansion; violates the minimality brief; H1/H3 don't test the core hypothesis. |
| **B** | Resume probes (P-N/P-I/P-G/P-H) on existing harness | **Rejected.** Reopens 1D by another name; harness not qualified; P-I/P-G/P-H are HARNESS-BLOCKED. |
| **C** | More architecture/Protocol analysis only | **Rejected.** U1–U3 cannot be answered by analysis; diminishing returns. |
| **D** | **Harness Qualification + one Verifiable State-Chain vertical slice** | **Recommended.** Smallest step that converts INSUFFICIENT into an answerable question. |
| **E** | Wait for GPT-6/Codex, then do independent validation | **Rejected as plan**, retained as optional later uplift (§11). Blocking on quota stalls the project. |

## 8. Minimum Viable Phase 2

**Name: Harness Qualification + Verifiable State Chain (VSC) slice.**

Two sequential stages, each with a Human gate:

**Stage 2.1 — Harness Qualification (no Agent behavior judged)**
- Move/adopt the minimal harness into the repo (location = Human decision) so it is version-controlled and reviewable.
- Fix capture-metadata handling: Runtime rows without `sessionId` (e.g., `file-history-snapshot`) are not session mismatches. Add deterministic regression test.
- Run a **live scripted session** (Human- or script-driven Bash calls, not an Agent probe) → operator start → CLI calls → seal → verify → require `capture_status=COMPLETE` and receipts matching raw Runtime. This answers **U1** without asking whether the Agent behaves well.
- Make the CLI invocation path **discoverable** in the Agent's execution environment (absolute path/env var in the run instruction; permission allow-rule for that one command) — closing the P-D-02/04 environment gap.

**Stage 2.2 — VSC slice (one scenario, one run)**
```text
Requirement (1 sentence, fixture with one Important unknown)
  → Agent investigates (Read/Grep)
  → Question created   [CLI receipt, persisted]
  → Question ASSUMED   [CLI receipt]
  → Assumption ISOLATED [CLI receipt, origin_question_id]
  → Task created with assumption_dep → Harness REFUSES ELIGIBLE (deterministic invariant)
  → Operator/Human records a gate decision out-of-band (never Agent)
  → Seal → verify → independent read-only evaluation
```
- Covers H2 + H4 + a deterministic slice of H3/H5. One object chain, no Spec/Evaluation/Evidence-object persistence, no Convention.
- Success = every state claim in the final report is backed by a CLI receipt **and** the matching raw Runtime tool_use/tool_result **and** Harness-enforced invariant behavior.
- Failure to use the CLI under a *discoverable* interface is itself a valid, attributable Phase 2 finding (Agent Execution vs Environment now separable).

## 9. Deferred Work

```text
H1 Governing Spec Resolver          → Phase 3 candidate (needed for Convention/Spec persistence only)
Async Human Gate query / P-I        → blocked by Claude sync AskUserQuestion; revisit only with a Runtime that supports it
P-G, P-H (Convention probes)        → depends on H1
Evaluation/Evidence object storage  → not needed for slice
Cross-model independent validation  → when GPT-6/Codex available
Tamper-proof sealing (signing/ACL)  → hash-only accepted; document limitation
MCP / SDK / Registry / Plugin / Orchestrator / UI / DB / Cloud / full CLI / Event Bus → all remain Deferred
Protocol vs legacy value comparison (U6) → long-horizon
```

## 10. Claude-Only Execution Constraints

- Only Claude Sonnet 5.5 is available. Be explicit about four distinct activities:

| Activity | Claude-only feasible? | Note |
| --- | --- | --- |
| Implementation (harness fix, CLI path, tests) | **Yes** | Standard engineering. |
| Self-Validation (Claude runs its own tests/reviews its own code) | Yes, but **evidence tier ≤ `RUNTIME_GENERATED`/`TOOL_GENERATED`** | Deterministic tests are fine; Claude's judgment of its own work is not independent. |
| Independent Validation | **Not fully** | See §11. |
| Human Verification | Yes | Highest tier; the real independence available today. |

- Claude must **not** be both the Agent under test and the sole validator of that run. Claude-the-implementer ≠ independent of Claude-the-harness-author.
- Never describe a Claude self-review as `INDEPENDENT_VERIFICATION`.

## 11. Independent Validation Strategy

Honest tiering for Phase 2 without GPT-6:

1. **Deterministic verifier** (hash recompute, tool pairing, receipt↔Runtime cross-check, invariant refusal tests) → `TOOL_GENERATED`. Does the heavy lifting and is model-independent.
2. **Fresh-context Claude validator**: separate session, read-only, given only the sealed package + the Protocol, no implementation context. Label **`SAME-FAMILY REVIEW`** — a distinct process but correlated blind spots; it **cannot** alone upgrade a result to PASS.
3. **Human Verification** of the few load-bearing facts (raw JSONL spot check of receipts, fixture hash). Required before any Phase 2 gate PASS.
4. **Optional uplift**: when GPT-6/Codex quota returns, re-review the *already sealed* Stage 2.2 package (no rerun). Result recorded as an addendum, not a prerequisite.

Rule: Phase 2 final gate may be `PASS` only if tiers 1 + 3 both hold; tier 2 is supporting. If only tier 2 exists, gate = `PASS WITH GAPS (same-family only)`.

## 12. Phase 2 Exit Criteria

```text
E-1  Stage 2.1: live scripted session seals as capture_status=COMPLETE; regression test for sessionId-less rows passes.
E-2  Stage 2.2: Question→Assumption→Task chain has persisted CLI receipts, each matched to a raw Runtime Bash tool_use/tool_result.
E-3  Harness refuses Task ELIGIBLE with an ISOLATED assumption_dep (deterministic test + live demonstration).
E-4  No Agent claim appears as state without a receipt; no fabricated Human decision.
E-5  Human spot-verification of receipts recorded.
E-6  Protocol files unmodified (git diff empty for protocol.md/state-model.md), or a Protocol Change Request satisfying §6's test.
E-7  Deferred list (§9) unchanged or consciously amended by Human.
```
Gate vocabulary: `PASS / PASS WITH GAPS / INSUFFICIENT / STOP`.

## 13. Recommended Next Step

```text
RECOMMENDATION:
Phase 2 = "Harness Qualification + Verifiable State Chain slice":
make one real Question→Assumption→Task-gate chain capturable, enforceable, and
independently re-checkable under COMPLETE capture. Protocol stays FROZEN.
```

- **Why now?** Phase 1 exhausted what design analysis can establish; the only remaining blocker (INSUFFICIENT) is an evidence-capability problem that only live implementation can resolve. Delaying for GPT-6 blocks the project without need.
- **Why this scope?** Q→A→T-gate is the Protocol's throughline ("unconfirmed ≠ code"); it exercises H2+H4 and a deterministic piece of H3/H5, and tests U1–U3 — the unknowns gating everything else.
- **Why not the other gaps?** H1 only serves Convention probes (not core value). Async Human Gate is a Claude Runtime limitation, not fixable by our code. Full independent-validation infra is Multi-Agent expansion with no minimal-loop dependency.
- **Smallest useful implementation:** (a) sessionId-less-row fix + test; (b) harness under version control; (c) discoverable/allow-listed CLI path; (d) CLI refusal of ELIGIBLE Task with ISOLATED dep; (e) one live scripted qualification run; (f) one fixture-based Agent run.
- **Evidence Phase 2 produces:** sealed COMPLETE packages (2.1 scripted, 2.2 Agent), receipt↔Runtime cross-check report, invariant-refusal tests, Human spot-check record, attribution of any Agent non-use of the CLI (now separable from Environment).
- **What stops Phase 2:**
  - Stage 2.1 cannot reach COMPLETE capture after bounded effort (→ Runtime evidence source unsuitable; reconsider source, not Agent).
  - A genuine Protocol contradiction proven by the §6 test (→ stop, raise Protocol Change Request).
  - Pressure to add a Deferred item (MCP, registry, orchestrator…) to proceed (→ stop, Human decides).
  - Stage 2.2 fails twice for the same Harness reason (→ no PASS-chasing; close as INSUFFICIENT, same discipline as 1D).

**Open Human decisions before Stage 2.1:** (1) repo location for the harness (currently outside repo at `D:\renjianxiao\phase-1d-execution\harness\`); (2) permission allow-rule scope for the CLI command; (3) naming/run namespace to keep Phase 2 runs visibly separate from 1D (suggest `PH2-` prefix).
