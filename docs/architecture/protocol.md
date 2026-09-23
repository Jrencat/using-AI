# using-AI Protocol — v0.1 (Phase 1A Design)

> Status of this document: **DESIGNED, NOT IMPLEMENTED.** Nothing described here executes today. It defines the contract that a future Harness/Runtime (Phase 1B+) would implement. See `simulation.md` §Architecture Attack for an honest audit of the gap between "designed" and "executable."

## 1. Purpose

Define the smallest set of objects, states, and rules that let a coding agent go from a one-sentence human intent to a verified, human-authorized change, while:

- never letting an unconfirmed business decision quietly become shipped behavior (the property the existing 7-stage prompts already provide — see `legacy-mapping.md`), and
- not forcing every task through the same fixed-length process regardless of risk (the property the existing prompts lack — see Phase 0 audit, `Adaptive Routing = MISSING`).

## 2. Scope

In scope: object definitions, state machines, preconditions/postconditions, evidence requirements, human-authority boundaries, routing rules, failure/fail-closed rules, traceability minimum, legacy/auto-test/OpenSpec boundaries.

Out of scope (explicit non-goals, see §14): any Runtime, CLI, MCP, SDK, Policy engine, generic Evidence engine, multi-agent orchestration, or modification of `auto-test`.

## 3. Core Principles (inherited from Phase 0, not re-litigated here)

1. Correctness over speed.
2. Self-investigation over interrupting the human.
3. Autonomy scales with evidence and risk; high risk cannot be routed around a Human Gate.
4. Legacy risk-isolation primitives are the default for high-risk paths, preserved not replaced.
5. Evidence First — a Claim is not a Fact until Evaluated.
6. Fail Closed on: unresolved Critical Question, low-confidence Assumption with business impact, insufficient Evidence, unexplained failure, irreversible/high-risk action, Claim-Evidence contradiction.

## 4. Core Objects (7, top-level)

| # | Object | Why it is independent (not folded into another object) |
|---|---|---|
| 1 | **Requirement** | Owns intent, investigation state, and the Question sub-entities it produces. No other object originates Questions. |
| 2 | **Assumption** | Distinct 5-stage lifecycle (create→isolate→circuit-break→human-gate→audit) inherited verbatim from Legacy `ASSUM-XXX`; not a Question (has a default behavior), not Evidence (is a placeholder for a missing decision). |
| 3 | **Spec** | The durable, versioned single-source-of-truth artifact. Requirement is the discovery *process*; Spec is what survives it. Legacy explicitly treats these as separate (README: "阶段2……建议保留——它是后续所有阶段的锚点"). |
| 4 | **Task** | A unit of Scope-bounded work with its own eligibility/circuit-breaker check, independent of Spec's normative content. |
| 5 | **Agent Contract** | Reusable capability-boundary definition (allowed/forbidden/preconditions/evidence-required) applied to *multiple* objects' execution (Requirement investigation, Task execution, Evaluation) — not owned by any single one of them. |
| 6 | **Evidence** | A fact record with its own identity/trust-level/source, referenced many-to-many by Assumptions, Evaluations, and Human Gates. Reusability across unrelated parents is why it cannot be folded into Evaluation (mirrors `auto-test`'s real separation of `evidence-store.mjs` from `verify.mjs`). |
| 7 | **Evaluation** | The judgment process that reconciles a Claim against Evidence and produces a Decision (incl. `INVALID_AGENT_RESULT`). Distinct from Evidence: one Evidence record can feed multiple Evaluations; an Evaluation without Evidence is `INSUFFICIENT`, not `PASS`. |

### 4.1 Deliberately folded (not top-level, with reason)

- **Question** → folded into **Requirement** as a child list (`requirement.questions[]`). A Question has no existence or reuse outside the Requirement that raised it (1:1 composition, unlike Evidence's many:many). This mirrors how Legacy's QA board is inseparable from Stage 1.
- **Run/Attempt** → folded into **Task** as a child list (`task.attempts[]`). Per §20 of the brief: no evidence in this repo shows an execution attempt needs an identity independent of its Task. Revisit only if a future real case shows concurrent or cross-Task-shared attempts.

### 4.2 Deliberately NOT top-level objects (cross-cutting mechanisms instead)

- **Human Gate** — modeled as a **shared embedded structure** (mixin), not a standalone object, and attached to whichever object raises it: `requirement.questions[i].human_gate`, `assumption.human_gate`, `task.human_gate`, `evaluation.human_gate`. Reason: a gate instance has no identity or reuse outside the object that raised it (1:1), unlike Evidence. This is different from simply merging it away — the schema (§9) is defined once and reused, but it is not an independent registry.
- **Policy** — modeled as a **rule table** (`condition → action → enforcement_level`), not a stateful object. It has no per-instance lifecycle of its own; it configures *when* Assumption circuit-breakers, Task eligibility checks, Routing decisions, and Human Gates fire. Per the brief's §22 instruction, Phase 1A does not implement a Policy engine — the rule table is documentation, referenced by the objects above.
- **Routing / Complexity** — a decision function over Requirement + Task + Evidence + Policy, recorded as an attribute (`task.routing = {level, evidence, reasoning}`), not an object with its own identity.

This resolves the ≤7 constraint honestly: two folds are justified by 1:1-composition (Question, Run), two demotions are justified by "no independent identity/reuse" (Human Gate, Policy) — not by merging things the brief explicitly warned against merging (Evidence+Evaluation+HumanGate+Policy stay four separately-reasoned concepts; only two of the four keep top-level object status).

## 5. Object Definitions

### 5.1 Requirement

- **Purpose**: capture intent, drive investigation, own Questions, feed Spec once ready.
- **Key fields**: `intent` (free text, may be one sentence), `desired_outcome`, `known[]` (Evidence-backed facts), `unknown[]` → materializes as `questions[]`, `authority` (who owns the business decision), `scope_hint`.
- **State**: `DRAFT → INVESTIGATING → (READY | BLOCKED)`. `READY` requires all `Critical` questions `ANSWERED`; `BLOCKED` while any `Critical` question is unresolved.
- **Relationships**: produces `Question[]` (embedded); produces `Assumption` when a question is downgraded; feeds `Spec`.
- **Preconditions**: none (a bare sentence is a valid input — see §6).
- **Failure conditions**: investigation exceeds scope bound (§13 Token Discipline) without resolving Critical questions → escalate to Human Gate rather than silently guessing.
- **Upgrade conditions**: discovery of a new Critical unknown at any later stage re-opens `Requirement.status = BLOCKED`.

**Question** (embedded in Requirement):
- **Fields**: `id` (`PD-XXX` / `TECH-XXX`, legacy-compatible prefixes, permanent, never renumbered), `text`, `severity` (`Critical | Important | Non-Critical`), `context` (what was investigated, what was found, options + impact — required before escalating to a human, per §10), `status`.
- **State**: `OPEN → (ANSWERED | ASSUMED | BLOCKED | INVALID)`. `BLOCKED` = Critical, unanswered, Human Gate open. `ASSUMED` = downgraded, spawns an `Assumption`. `INVALID` = further investigation showed the question no longer applies (kept as a state — not deleted — for traceability).

### 5.2 Assumption

Lifecycle preserved verbatim from Legacy `ASSUM-XXX` (see `legacy-mapping.md` for full citation trail):

```
create → isolate → (circuit-break on referencing Task) → human gate → audit
```

- **Purpose**: let low/medium-risk work proceed under an explicit, falsifiable default instead of blocking on every open question.
- **Key fields**: `id` (`ASSUM-XXX`), `origin_question_id`, `content`, `impact_scope`, `default_behavior` (mandatory — no Assumption without a stated fallback), `confidence`, `follow_up_suggestion`.
- **State**: `ISOLATED → CHALLENGED (optional, when new Evidence contradicts it) → (PROMOTED | REJECTED)`. `PROMOTED` = Human confirmed it as a real decision → becomes normative Requirement/Spec content. `REJECTED` = Human overturned the default → Requirement re-opens.
- **What it can do**: unblock Non-Critical/Important-severity work at low confidence-risk, with a recorded default and an explicit follow-up.
- **What it cannot do**: stand in for a business decision that is Critical-severity, irreversible, or involves data/money/permissions — those must be a blocking `Question`, not an `Assumption` (hard rule, §12/§10).
- **Evidence that can promote/reject it**: a Human decision record (Human Gate `decision`), or new Evidence that directly contradicts `default_behavior` (triggers `CHALLENGED`, does not auto-resolve).

### 5.3 Spec

- **Purpose**: single normative source of truth; only `ANSWERED` Requirement content and `PROMOTED` Assumptions become normative chapters; everything else lives in a dedicated Pending-Assumptions section (Legacy Ch.9, preserved).
- **Key fields**: `chapters[1..8]` (normative), `chapter9_pending_assumptions[]` (references `Assumption.id`, never buildable).
- **State**: `DRAFT → REVIEWED → APPROVED` (Human Gate on `REVIEWED → APPROVED`).
- **Relationships**: derived from `Requirement`; referenced by `Task.scope` as the sole authority. Governing Spec identification for a given `Requirement` is a Harness-provided capability, not a Protocol-defined field — see §16.
- **Convention persistence** (Phase 1C addition): a Convention — established only when a `Question.human_gate.decision` contains an explicit Formation Confirmation, never from `Question.status = ANSWERED` alone — must be represented in the normative content of its Governing Spec. This adds an obligation on top of, and does not alter, the `ANSWERED`/`PROMOTED` eligibility rule stated above.

### 5.4 Task

- **Purpose**: a Scope-bounded unit of work with an eligibility check before any code is written.
- **Key fields**: `id` (`{{TASK_PREFIX}}-XXX`), `priority` (`P0|P1|P2`), `scope[]` (file/module list, hard boundary), `depends_on[]`, `assumption_deps[]`, `acceptance_criteria[]`, `attempts[]` (folded Run/attempt history: `{n, started_at, ended_at, outcome, evidence_refs[]}`).
- **State**: `DRAFT → (ELIGIBLE | BLOCKED) → IN_PROGRESS → EVALUATING → (DONE | FAILED | RISK_PENDING)`.
  - `ELIGIBLE`: `priority ∈ {P0,P1}` AND no `assumption_deps` in `ISOLATED` state (green-light, Legacy §5 verbatim).
  - `BLOCKED`: `priority = P2` OR any `assumption_deps` still `ISOLATED` (red-light, Legacy §5 verbatim) → Human Gate required to move to `ELIGIBLE`.
  - Absolute circuit-break (Legacy §4): a feature whose scope exists *only* inside `chapter9_pending_assumptions` never gets a Task created at all — this happens at Task-creation time, before the eligibility check.
  - `RISK_PENDING`: Evaluation attributes failure to an unresolved Assumption — not a `FAILED` verdict (Legacy §6 preserved).
- **Failure conditions**: attempt count exceeds Agent Contract's retry cap → `FAILED`, escalate.

### 5.5 Agent Contract

- **Purpose**: the machine-checkable shape of what Legacy calls "全局强制规则" — not a persona.
- **Required fields (Phase 1 minimum)**: `applies_to` (Requirement-investigation | Task-execution | Evaluation), `preconditions[]`, `allowed_actions[]`, `forbidden_actions[]`, `evidence_required[]`, `human_gate_conditions[]`, `capability_boundary` (e.g. file Scope).
- **Deferred fields (may be added later, not required now)**: `expected_output_schema`, `versioning`.
- **State**: mostly static/versioned, not per-instance stateful. One Contract instance is referenced by many Task/Requirement executions.
- **Example instance (Execution Contract, mirrors Legacy Stage 5 verbatim, claude模板 L390-397)**: `forbidden_actions = [需求分析, Spec修改, tasks拆解, 测试生成, 归档]`; `human_gate_conditions = [priority==P2, any assumption_dep.status==ISOLATED]`.

### 5.6 Evidence

- **Purpose**: an independently-citable fact record, reusable across Assumptions, Evaluations, and Human Gates.
- **Key fields**: `id` (`EVID-XXX`), `source` (path/section/command/tool), `trust_tier` (see §11 below), `content` (short, citable), `collected_at`, `collected_by`.
- **Trust tiers** (from lowest to highest trust; §16 of the brief):
  1. `SELF_REPORT` — the agent's own narrative claim. Never sufficient alone to close a Question, promote an Assumption, or produce `PASS`.
  2. `RUNTIME_GENERATED` — produced by the agent's tool use (e.g. a file search/read result), not asserted from memory.
  3. `TOOL_GENERATED` — produced by an external deterministic tool (test runner, linter, build).
  4. `INDEPENDENT_VERIFICATION` — produced by a separate agent/process not the one making the Claim.
  5. `HUMAN_VERIFICATION` — a human directly confirmed it.
- **Rule**: an Evaluation may reach `PASS` only if at least one `trust_tier ≥ RUNTIME_GENERATED` Evidence item supports the Claim; `SELF_REPORT`-only evidence caps the Evaluation at `INSUFFICIENT`.
- **State**: `COLLECTED` (effectively immutable once recorded) → optionally flagged `DISPUTED` if a later, higher-trust-tier Evidence item contradicts it.

### 5.7 Evaluation

- **Purpose**: reconcile a Claim ("test passed," "requirement understood," "scope matches Spec") against Evidence and produce a Decision.
- **Key fields**: `claim`, `evidence_refs[]`, `decision`, `human_gate` (embedded, only present if triggered).
- **Decision values**: `PASS | FAIL | CONTRADICTED→INVALID_AGENT_RESULT | INSUFFICIENT | BLOCKED (human gate open)`.
- **State**: `PENDING → EVALUATED`.
- **Core rule (INVALID_AGENT_RESULT, inherits `auto-test`'s `checkClaim()`/`decide()` semantic shape — not its code, see `evidence.md`)**: if `claim = PASS` but a required Evidence item shows `FAIL`/contradiction → `decision = INVALID_AGENT_RESULT`, regardless of what the agent asserts. The Claim never overrides the Evidence.

## 6. Requirement Intelligence (P0 capability, lightweight)

See `evidence.md` §Requirement Intelligence Simulation and `simulation.md` for a worked walkthrough. Summary contract:

```
User Intent (one sentence is valid input)
    ↓
Repository Investigation (scope-limited: start at files/paths plausibly related to the intent; expand only if still ambiguous — bounded, not a full-repo scan)
    ↓
Existing Behavior / Architecture / Convention check
    ↓
Existing Tests check
    ↓
Conflict Detection (does investigation output contradict the stated intent?)
    ↓
Question Generation (only for what investigation could not resolve)
    ↓
Requirement Model populated
```

**Convention check** (Phase 1C addition, clarifies the `Existing Behavior / Architecture / Convention check` pipeline step above): for the current Requirement, use the Harness-provided Governing Spec Resolution capability (§16) to identify the Governing Spec, then inspect that Spec for previously confirmed Conventions applicable to the current Requirement. The Governing Spec is the sole Discovery Target — no Convention Registry, Convention object, or additional state machine is introduced. A discovered Convention feeds into this pipeline's existing Non-Critical/Safe-Default handling below like any other Evidence-backed Known fact — it does not bypass or outrank Human Authority, Business Rule, an explicit Protocol Rule, or Existing Spec content (the Information Priority ordering below is unchanged).

**Information priority** (default, overridable by Human Authority — see next line):
`Repository Evidence > Existing Spec > Project Convention > Existing Tests > Safe Assumption > Human Question`.

**Hard override**: if the unknown is a business rule, business trade-off, irreversible decision, permission/authorization, or policy exception, existing repo behavior is *not* sufficient to infer current intent — this always routes to a `Critical` Question, never a `Safe Assumption`, even if the repository shows a clear existing pattern (§10 of the brief). Example: Case B in `simulation.md` — an existing refund code pattern, if one existed, would still not license assuming the current desired policy.

**When to investigate vs. ask** (severity rule, §4.2 of the brief):
- `Critical` (changes business semantics/data/security/permissions/irreversible/large rework) → must become a `Question`, cannot be resolved by investigation alone if it is a business decision.
- `Important` → keep investigating first; only becomes a `Question` if investigation is exhausted within the scope bound.
- `Non-Critical` → resolved via convention/safe default, recorded as `Evidence`-backed `Known`, no `Question` created.

**Status of this mechanism**: `DESIGNED`. `NOT IMPLEMENTED` — no tooling exists to perform or bound "repository investigation"; this remains dependent on whatever investigation capability the Runtime (e.g. Claude Code's own file tools) already provides, and on the operating agent actually following this contract. See Architecture Attack #3.

## 7. Boundary Discovery

Not an exhaustive checklist (the brief explicitly forbids mechanical enumeration). Minimum structured categories, only when relevant to the Requirement at hand:

`Scope | Data | Permission | Transaction/Irreversibility | Integration | Compatibility`.

Routing rule: any Boundary category flagged as touched becomes either (a) an `Evidence` item if investigation resolves it, (b) a `Question` if it can't be resolved and materially changes correctness, or (c) a `Complexity` upgrade signal if it changes risk level without needing a new Question (e.g. discovering cross-service impact — see `routing.md` Scenario 2).

## 8. Human Authority (non-negotiable boundary)

**Agent may**: investigate, discover, analyze, recommend, generate Questions/Assumptions, execute within an `ELIGIBLE` Task's Scope, produce Evidence, run an Evaluation.

**Agent may not**: resolve a `Critical` Question by inference, promote/reject an `Assumption`, mark a `BLOCKED` Task `ELIGIBLE`, override an `INVALID_AGENT_RESULT` decision, or treat a business-authority question as a technical one (§19 of the brief — the agent must not "将 Human Authority 问题伪装成技术执行问题").

**Human must decide**: Business Ambiguity, Irreversible Action authorization, High-Risk Change authorization, Insufficient-Evidence resolution, Policy Exception, explicit red-light authorization.

**Human Gate schema** (mixin, embedded wherever triggered — §4.2, §19): `trigger`, `context` (what was investigated, what was found, options A/B/C + impact of each — required, per §10 of the brief: "提问必须带 Context"), `decision`, `authority` (who decided), `effect`, `audited_at`.

## 9. Fail Closed (P0)

| Condition | Result |
|---|---|
| Evidence missing for a Claim | `Evaluation.decision = INSUFFICIENT`, not `PASS` |
| Required (`Critical`) Question unanswered | `Requirement.status = BLOCKED`, dependent `Task`s cannot become `ELIGIBLE` |
| Claim contradicts Evidence | `Evaluation.decision = INVALID_AGENT_RESULT` |
| High-risk action without Human authorization | `Task.status` stays `BLOCKED` |
| Attempt count exceeds Agent Contract retry cap | `Task.status = FAILED`, escalate, do not retry silently |

## 10. Traceability (minimum, file/ID-level — no database)

Preserved ID chain (Legacy, unchanged): `PD-/TECH-XXX → ASSUM-XXX → {{TASK_PREFIX}}-XXX → TD-XXX`.
New IDs added: `EVID-XXX` (Evidence), `EVAL-XXX` (Evaluation, optional — may be embedded in the Task/Requirement it belongs to rather than separately numbered).
Every `Evaluation.decision ≠ PASS` must cite at least one `Evidence.id`. Every `Task.attempts[]` entry should reference the `Evidence` it produced or consumed. No new database or graph store — Markdown/JSON/file-path citation is sufficient for Phase 1, matching Phase 0's own audit method.

## 11. Token Discipline (P2, documented now, not engineered now)

Rule tiers, to be loaded selectively rather than all at once by a future Runtime:
- **Core Rules** (always loaded): Fail Closed table (§9), Human Authority boundary (§8), Assumption hard rule (§10 override).
- **Contextual Rules** (loaded once Routing level is known): the specific Complexity tier's Assessment/Evidence/Decision rules (`routing.md`).
- **Task-specific Rules**: the one Agent Contract instance that applies to the current Task type.
- **Evidence-specific Rules**: Evidence trust-tier table (§5.6), only needed at Evaluation time.

No context engine is implemented in Phase 1A; this is a load-order specification for a future Harness.

## 12. Legacy Compatibility

See `legacy-mapping.md` for the full Stage→Primitive table and citation trail. Summary: nothing is deleted; every Legacy risk-control primitive (QA state machine, ASSUM lifecycle, P2 circuit breaker, red-light Human Gate, final compliance audit, Pending Tech Debt ledger) is preserved as a condition-triggered rule inside the objects above, rather than a stage-number-triggered rule.

## 13. Auto-Test Boundary

`using-AI` Protocol reuses **semantics only** from `auto-test` (`Auto-Test Skill / core/{verify,finalize,policy,evidence-store}.mjs`) — the claim-vs-evidence separation, the `INVALID_AGENT_RESULT` short-circuit concept, and the trust-tier framing. No code, package, or release-cycle dependency. A genuine gap was found, not glossed over: `auto-test`'s Evaluation model is scoped to test-execution verdicts; `using-AI`'s Evaluation must also judge non-testing claims (e.g. "requirement understood," "scope matches Spec"), which `auto-test` does not cover. See `evidence.md` for detail. When real test execution is eventually needed, `auto-test` is invoked as a Testing Adapter (future, not Phase 1A).

## 14. OpenSpec / Multica / TypeSafe Boundary

- **OpenSpec**: Optional. Stage 3/4/7's existing optional dependency is preserved unchanged. A future OpenSpec Adapter may exist; OpenSpec is not the Protocol's foundation (README.md L124 already documents this as swappable).
- **Multica**: not merged. Multica owns WHO/WHERE/WHEN; this Protocol owns HOW/RULE/EVIDENCE/GOVERNANCE.
- **TypeSafe**: reference-only for the Decision/Confidence vocabulary; no dependency formed.

## 15. Explicit Non-Goals (Phase 1A)

No CLI, MCP, SDK, Web UI, Runtime, multi-agent orchestration, plugin system, registry, Policy engine, generic Evidence engine, `auto-test` modification/copy/refactor, OpenSpec/Multica/TypeSafe integration, large Prompt rewrite, deletion of the 7-stage templates, large directory restructuring, or business code changes.

## 16. Runtime/Harness Boundary (reference)

- **Protocol** (this document): what must be true — objects, states, preconditions, evidence requirements, human authority, routing constraints, traceability.
- **Harness** (not designed here beyond this boundary statement): who organizes execution of the Protocol's objects across a session/task. Out of scope for Phase 1A.
- **Runtime** (not designed here): Claude Code, Codex, or any other coding agent that actually reads files and writes code. The Protocol must never branch on `if Claude / if Codex` — Runtime differences are Adapter-layer only, exactly as the existing Claude/Codex template pair already demonstrates (`EXISTS (doc-level)` per Phase 0).
- **Governing Spec Resolution capability** (Phase 1C addition): for a given `Requirement`, the Harness MUST provide a deterministic mechanism to resolve its Governing Spec. Protocol requires only that this capability exists and is deterministic; it does not define the mechanism itself — storage, identity (e.g. a naming convention), file path, cardinality, and Spec creation timing are Harness/Runtime concerns unless a future Protocol revision states otherwise.
