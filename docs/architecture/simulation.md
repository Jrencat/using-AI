# Real Case Simulation & Architecture Attack — v0.1 (Phase 1A Design)

> Paper-only. No code executed, no files outside `docs/architecture/` written. Every simulation result is classified `DESIGNED / NOT EXECUTABLE / PARTIAL / UNPROVEN` per the brief's required vocabulary, and separately tagged `REAL EVIDENCE / DESIGN DECISION / UNVERIFIED`.

## 1. Source Material

The repo's only real worked example is `examples/填写示例.md` — a fictional "订单管理" (order-management) module. It is the sole source for Case A and Case B below. It is fictional (no real target codebase exists behind it), which caps every simulation at `PARTIAL` for any sub-step that would require real repository investigation — flagged explicitly at each such point rather than glossed over.

---

## 2. Case A — SIMPLE (real repo evidence: `examples/填写示例.md` PD-001)

**Source**: PD-001 "订单列表是否支持批量取消" (does the order list support bulk cancel), status `✅ 已关闭` in the example (L70 of `examples/填写示例.md`).

**Trace through the Protocol**:

| Step | Object/Transition | Result | Classification |
|---|---|---|---|
| Requirement created | `Requirement.intent` = "订单列表批量取消" | `DRAFT → INVESTIGATING` | `DESIGNED` (mechanical, structural mapping of real content) |
| Repository Investigation | Would check existing order-list component/API for a batch-action pattern | Cannot actually run — order-management is fictional, no real codebase | `NOT EXECUTABLE` |
| Question resolution | PD-001 already `✅已关闭` in the source material — maps to `Question.status = ANSWERED` | direct 1:1 mapping from real example content | `DESIGNED`, `REAL EVIDENCE` (the closed status itself is real example content) |
| Complexity tiering | Single list-page feature addition, no schema/permission/irreversibility flag raised in the example | `SIMPLE` per `routing.md` §2 | `DESIGNED`, `DESIGN DECISION` (tiering rule applied to real content, but the tier itself wasn't independently verified against a real codebase) |
| Routing recommendation | SIMPLE tier → lightweight path (skip full OpenSpec ceremony, keep Spec-equivalent step) | per `routing.md` §5 | `DESIGNED`, `UNVERIFIED` (no execution occurred) |
| Task creation | `Task` for the bulk-cancel endpoint, `priority = P0/P1`, no `assumption_deps` | `ELIGIBLE` immediately | `DESIGNED` |
| Execution | Not performed (Phase 1A is document-only; no code written) | — | `NOT EXECUTABLE` (by design/prohibition, not by limitation) |

**Overall Case A classification**: `PARTIAL`. The object/state mapping is `DESIGNED` and grounded in real example content; the investigation and execution sub-steps are honestly `NOT EXECUTABLE` in this phase.

---

## 3. Case B — HIGH-RISK (real repo evidence: `examples/填写示例.md` PD-002/ASSUM-001/OM-007/TD-001)

**Source**: PD-002 "已发货订单的退款规则未定义" (refund rule for shipped orders is undefined), `❌ 待确认` → downgraded to `ASSUM-001` in Spec chapter 9 (L93-98) with mandatory `default_behavior` ("未确认前，已发货订单点击退款仅创建「待退货」单据，不触发实际退款"), driving `Task OM-007` (L102-116, `priority = P2`, `Scope = RefundController/RefundService`), whose Stage-5 output is the exact block (L120-127) ending in `⚠️ 已阻断挂起 —— 等待人工显式授权`, and finally `TD-001` (L131-139) in the Stage-7 tech-debt ledger with verdict `⚠️ 可使用`.

**Trace through the Protocol**:

| Step | Object/Transition | Result | Classification |
|---|---|---|---|
| Requirement created | `Requirement.intent` = "已发货订单退款流程" | `DRAFT → INVESTIGATING` | `DESIGNED` |
| Question raised | PD-002, severity assessed | This is a business-authority matter (financial/inventory reconciliation) → per `protocol.md` §6 hard override, **must** be `Critical`, cannot resolve via repo investigation alone even if a pattern existed | `DESIGNED`, `REAL EVIDENCE` (the example itself treats it as MAJOR/blocking, L71) |
| Question downgrade | PD-002 `OPEN → ASSUMED` with mandatory `default_behavior` stated | Spawns `Assumption ASSUM-001`, `status = ISOLATED` | `DESIGNED`, `REAL EVIDENCE` (default_behavior text copied faithfully from L96) |
| Complexity tiering | Money + inventory + irreversibility-adjacent (refund) → `HIGH-RISK` per `routing.md` §2, **regardless of** the fact the example downgraded it to a mere P2 Task rather than fully blocking Requirement | `HIGH-RISK` | `DESIGNED`, `DESIGN DECISION` — note: this is a genuine judgment call the Protocol makes that Legacy's own worked example doesn't explicitly label as "high risk," it only encodes the *effect* (P2 + circuit-break) without naming a risk tier. Flagged honestly as this Protocol's own added structure, not something Legacy literally states. |
| Task creation | `Task OM-007`, `scope = [RefundController, RefundService]`, `assumption_deps = [ASSUM-001]` | Creation-time check: scope is not *exclusively* inside chapter-9-only content (a real Refund endpoint IS a legitimate Task, just a blocked one) → not absolute-circuit-broken, correctly falls to `BLOCKED` state instead | `DESIGNED`, `REAL EVIDENCE` (matches Legacy's actual behavior of creating OM-007 as P2, not refusing to create it) |
| Task eligibility check | `priority == P2 OR assumption_dep ISOLATED` → both true | `Task.status = BLOCKED`, Human Gate opens | `DESIGNED`, `REAL EVIDENCE` (matches the real red-light block text verbatim, L121 "⚠️ 告警：当前任务依赖未决假设...") |
| Execution attempt | None occurs — Task stays `BLOCKED` | matches real example's `⚠️ 已阻断挂起 —— 等待人工显式授权` (L126) exactly | `DESIGNED`, `REAL EVIDENCE` |
| Final audit | Task never executed without authorization → compliant isolation, not a defect | `Evaluation.decision` for the audit-level claim = `PASS` (compliance claim, not a feature-works claim); `RISK_PENDING`/tech-debt ledger entry `TD-001` created | `DESIGNED`, `REAL EVIDENCE` (matches L131-139 exactly, including the `⚠️ 可使用` verdict, not `❌`) |

**Overall Case B classification**: `PARTIAL` — same investigation/execution caveats as Case A, but the risk-isolation chain itself (Question→Assumption→BLOCKED Task→Human Gate→Tech Debt) maps to real, cited example content essentially line-for-line, giving this case the strongest evidentiary grounding of any simulation in this document.

---

## 4. Routing Simulation — 3 Scenarios

### Scenario 1: Reduce-steps (grounded in real evidence)
Basis: README.md L132-133 FAQ. A SIMPLE-tier Task (Case A pattern) is recommended to skip full OpenSpec ceremony while keeping the Spec-equivalent step. **Classification: `DESIGNED / PARTIAL`** — grounded in real repo text, but no mechanism exists that actually computes or enforces this today.

### Scenario 2: Mid-execution escalate (hypothetical)
A MODERATE-tier Task (e.g., "add a filter param to the order list API") discovers mid-implementation that the filter needs to query a separate reporting service, introducing cross-service coupling. Per `routing.md` §3 (upgrade always allowed), the Task immediately re-tiers to `COMPLEX`, and any skipped stages (e.g. full Spec review) reopen. No such case exists in the repo's real content. **Classification: `DESIGNED / UNPROVEN`.**

### Scenario 3: Complex-to-downgrade candidate (hypothetical)
A COMPLEX-tier Task (e.g., a full new module scaffold) turns out, during implementation, to require far less code than expected. Downgrade is evaluated against the three-condition rule (`routing.md` §3): no new contradicting Evidence exists (the domain risk — e.g. a new module touching shared auth — is unchanged by code volume), so downgrade is **rejected**, demonstrating the rule prevents "it was easy so it must have been low-risk" reasoning. No matching real repo case. **Classification: `DESIGNED / UNPROVEN`.**

---

## 5. Requirement Intelligence Simulation

Full trace already written in `evidence.md` §5, using the brief-supplied hypothetical sentence ("修复实验页面刷新后左侧菜单与专题不匹配的问题"). Summary result: **`PARTIAL`** — sentence-only reasoning steps (Conflict Detection, one plausible Question) are `DESIGNED`; steps requiring real repository investigation are `NOT EXECUTABLE` because no real target codebase exists in this repo. Not duplicated here; see `evidence.md` §5 for the full walkthrough.

---

## 6. Architecture Attack (10 items, adversarial)

| # | Attack | Verdict | Reasoning |
|---|---|---|---|
| 1 | "An agent could mark a Critical Question `ASSUMED` instead of `BLOCKED` to avoid stopping for a human, since nothing enforces the state machine." | `PARTIAL` | Correct — this Protocol is a document, not running code. The hard override rule (`protocol.md` §6) forbids this in the design, but nothing today prevents an agent from ignoring the document. This is an honest limitation, not a flaw unique to this design: the same gap exists in Legacy's prose-only enforcement (Phase 0 finding). Mitigation is future Runtime/Harness enforcement — explicitly out of scope for Phase 1A. |
| 2 | "PROMOTED Assumptions never get re-checked — what stops a stale default_behavior from silently staying normative forever?" | `FIXED` | Real gap found: `PROMOTED` was originally terminal with no re-entry path. Fixed in `state-model.md` §2 by adding `PROMOTED → CHALLENGED` on new contradicting Evidence (with a corresponding Spec chapter revert). Still `NOT IMPLEMENTED` — the fix is a design correction, not running code. |
| 3 | "Requirement Intelligence claims a 'bounded' repository investigation, but no bound is actually specified — an agent could investigate forever or investigate nothing and call it done." | `PARTIAL` | Correct gap: `protocol.md` §6 says "bounded, not a full-repo scan" but does not define the bound numerically or structurally beyond deferring to Token Discipline (§11), which is itself undesigned in detail. Listed as a Human Decision Required item. |
| 4 | "Evidence trust tiers can be gamed — an agent could wrap a SELF_REPORT claim as if it were RUNTIME_GENERATED by citing a tool call that didn't actually verify the claim." | `PARTIAL` | The design assumes good-faith tier self-labeling; nothing structurally prevents mislabeling. `evidence.md` §2's rule (PASS requires ≥RUNTIME_GENERATED) reduces but doesn't eliminate this risk. A future Runtime could require Evidence records to embed the actual tool-call transcript for independent spot-check — deferred, not designed here. |
| 5 | "The ≤7 Core Object limit was hit by folding Question and Run — isn't this exactly the 'dodge' the brief prohibited?" | `PASS` | Addressed directly in ADR-001: the fold is justified by genuine 1:1-composition evidence (no cross-Requirement Question reuse, no cross-Task Run reuse observed anywhere in Legacy or the example), not by arbitrary merging. The brief's prohibition was on *dishonest* super-object merging; this fold's reasoning is written out and falsifiable. |
| 6 | "Human Gate being a mixin instead of an object means there's no single place to query 'all currently open gates' — a real operational need." | `PASS` | Acknowledged directly as a stated consequence in ADR-002, not hidden. This is a real cost accepted deliberately, with the reasoning for why (no independent identity/reuse) laid out — the attack doesn't surface a new unconsidered flaw. |
| 7 | "Complexity tiering has no numeric score, so two agents (or the same agent twice) could tier the same Task differently with no way to detect disagreement." | `PASS` | Correctly anticipated and accepted in `routing.md` §2 and ADR-004: the qualitative approach requires a human-legible `reasoning` field precisely because tiering isn't claimed to be deterministic; disagreement is expected to be resolved by a human reading the reasoning, not by algorithmic consensus. Not a hidden flaw — an accepted tradeoff against fake scoring. |
| 8 | "Case A and Case B are both drawn from the same fictional example — the Protocol has never been checked against a real, non-fictional codebase at all." | `PARTIAL` | True, and already flagged throughout §2-§5 as `NOT EXECUTABLE`/`PARTIAL` for investigation-dependent steps. This is the single largest evidentiary weakness of this phase's simulation work, explicitly surfaced rather than minimized. |
| 9 | "The auto-test Evidence GAP (test-only vs. broader claims) is declared but not solved — doesn't that mean Evaluation for non-test claims is effectively undesigned?" | `PASS` | Correct, and intentionally left that way per ADR-003 and the brief's own instruction (§23) to flag GAPs rather than force generalization. The attack confirms the gap was accurately self-identified, not that it was missed. |
| 10 | "INVALID_AGENT_RESULT retries the Task (state-model.md §4: `IN_PROGRESS`) — but what stops an infinite retry loop if the agent keeps misreporting?" | `FIXED` | Real gap found: `INVALID_AGENT_RESULT` did not originally count against the retry cap. Fixed in `state-model.md` §4: `INVALID_AGENT_RESULT` now consumes an attempt slot identically to `FAIL` and routes to `FAILED` once the cap is exceeded. |

**Attack summary**: 4 clean `PASS` (5, 6, 7, 9), 2 `FIXED` during this phase (2, 10 — state-model.md was corrected in response), 4 `PARTIAL` (1, 3, 4, 8) each with an honestly stated, still-open gap. No item was rated a full failure requiring the whole design to be scrapped. Items 1, 3, 4, and 8 are carried into the closing report's Gap List / Human Decisions Required as still-open.

---

## 7. Why Document-Only Validation Is Sufficient For Phase 1A (required self-check)

Per the brief's escape-hatch instruction: a prototype would only be necessary if paper-based simulation could not surface the design's real weaknesses. §6 above shows paper simulation *did* surface concrete gaps (items 2, 3, 10) purely through adversarial reading, without executing anything — demonstrating document-only review is doing real work here, not rubber-stamping. No prototype is judged necessary for Phase 1A; this assessment should be revisited once real (non-fictional) target-codebase cases become available, since §8 of this document is the acknowledged limit of what paper simulation against a fictional example can validate.
