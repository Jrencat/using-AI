# Legacy 7-Stage → Protocol Primitive Mapping — v0.1 (Phase 1A Design)

> Every citation below was re-verified directly against the repo files during this phase (not carried over unchecked from Phase 0). Line numbers refer to `claude研发流水线提示词模板.md` unless noted; the `codex` variant is structurally identical per the CLAUDE.md claim, independently spot-checked in Phase 0.

## 1. Mapping Table

| Legacy Stage | Protocol Primitive(s) | Preserved Risk Control | Citation |
|---|---|---|---|
| 1. 需求分析 & QA 生成 | `Requirement` + embedded `Question[]` | QA status machine `❌待确认→🔄追问中→✅已关闭`; permanent, never-reused/renumbered IDs; incremental-merge-not-overwrite rule | L31 (state machine), L52-53 (increment rule + "问题 ID 一经分配永不复用、永不重排") |
| 2. Spec 设计 + 自我审查 | `Spec` (chapters 1-8) + `Assumption` (chapter 9 origin) | Only `✅已关闭` content becomes normative; open items downgrade to `ASSUM-XXX` with mandatory `default_behavior`; Spec = Single Source of Truth for all downstream stages | L149-151 (QA 状态过滤规则), L192-198 (假设格式, mandatory 默认行为字段), L147-148/L158-160 (SSOT declaration) |
| 3. OpenSpec Change 初始化 | `Spec → (external adapter, out of Protocol core)` | Chapter 9 assumptions carried into a dedicated Pending Assumptions section; never turned into buildable specs | L247-249 (未决假设拦截规则: "严禁将其作为正式功能进行任务拆分") |
| 4. Tasks 拆解 | `Task` (creation-time circuit-break + priority/dependency fields) | Absolute circuit-break for pending-only features (no Task created at all); P2 downgrade + explicit `ASSUM-XXX` dependency tag for weakly-dependent tasks | L316-318 (绝对熔断 + 风险标记与降级规则) |
| 5. 代码实现 | `Task` state machine (`ELIGIBLE`/`BLOCKED`) + `Agent Contract` (Execution Contract instance) | Green-light/red-light check before any code; P2 or `ASSUM-XXX` dependency → hard block + exact warning string + wait for explicit human authorization; Scope boundary enforcement; one-task-at-a-time | L390-391 (scope lock), L395-397 (red/green light rule, verbatim warning string), L442-446 (禁止事项: no multi-task, no out-of-scope read, no refactor, no "顺手优化") |
| 6. 测试生成 + 自愈闭环 | `Evaluation` (per test_case) + `Evidence` (test artifacts) | Pruning: no tests for circuit-broken features; expected-result adapts to Assumption's `default_behavior` for P2 tasks; self-heal boundary hard-isolated (assumption-caused failures → `⚠️风险挂起`, never "fixed" by inventing business logic); bounded self-heal (max 2 fix attempts) | L485-488 (风险自适应规则三条), L532-534 (自愈边界硬隔离 + 2次上限规则) |
| 7. 最终审计 + 归档 | `Evaluation` (final compliance check) + Pending Tech Debt ledger (`TD-XXX`) | Unauthorized P2/`ASSUM` implementation → forced `❌ BLOCKER`, archive refused; compliant risk-isolation (known unimplemented/risk-pending items) → `⚠️` verdict, archive allowed; known tech debt is explicitly NOT counted as a defect | L587-589 (隔离合规性审计规则, both branches verbatim), L640-641 (final verdict definitions: ⚠️ vs ❌) |

## 2. Verbatim-Preserved Mechanisms (must not be weakened by the Protocol)

These are named explicitly because Phase 1A's brief treats them as non-negotiable inherited behavior, not merely "inspiration":

1. **ID permanence**: `PD-XXX`/`TECH-XXX`/`ASSUM-XXX`/`{{TASK_PREFIX}}-XXX`/`TD-XXX` — assigned once, never renumbered, never reused, even across Requirement re-opens. Encoded in `Requirement.questions[].id` / `Assumption.id` / `Task.id` / tech-debt ledger entries.
2. **Mandatory default behavior on every Assumption** — Legacy forbids an Assumption without a stated fallback (L197: `【默认行为】` is a required field, not optional). Encoded in `Assumption.default_behavior` as a required field (`protocol.md` §5.2).
3. **The exact P2/ASSUM red-light block** — Legacy's block condition (`priority==P2 OR any ASSUM-XXX dependency`) is reproduced exactly as `Task.status = BLOCKED` precondition in `state-model.md` §4, not loosened to a softer "warn but proceed" behavior.
4. **The exact final-audit fork** — "unauthorized P2/ASSUM implementation ⇒ BLOCKER, refuse archive" vs. "compliant risk-isolation ⇒ ⚠️, allow archive" is reproduced exactly in `Evaluation` decision logic for the final audit case (no third, softer path was invented).
5. **Self-heal boundary** — a test failure traced to an unresolved Assumption must never be "fixed" by inventing business logic (Legacy L543: "禁止基于「经验」通过自愈去补全或发明未定义/未决的业务逻辑"). Encoded as: `Evaluation` on a `RISK_PENDING`-linked Task must not silently flip to `PASS` by generating new Evidence that wasn't actually observed.
6. **Stage isolation as a first-class rule, not a convenience** — every Legacy stage prompt opens with an explicit "你只能执行阶段N的任务" boundary (L46, L146, L244, L314, L391, L483, L585). The Protocol's Agent Contract `forbidden_actions[]` field (`protocol.md` §5.5) exists specifically to carry this forward in a structured (not just prose) form.

## 3. What Changed (and why it's not a weakening)

| Change | Reason | Safeguard against regression |
|---|---|---|
| Fixed 7-prompt sequence → Requirement/Task-driven object model with Routing | Legacy forces every change through the same stage count regardless of size (Phase 0 finding: `Adaptive Routing = MISSING`) | Routing's SIMPLE tier still never skips the Spec-equivalent step (`routing.md` §5), matching the one exception the Legacy FAQ itself already carves out |
| Single continuous QA doc → `Requirement.questions[]` embedded, still ID-stable | Structural fit for object model | ID permanence rule (§2.1 above) is carried forward unchanged, not merely "inspired by" |
| Stage-numbered gating → condition-triggered gating (`BLOCKED` state, Human Gate mixin) | Enables Routing (a SIMPLE task shouldn't need "stage 3" to not apply) without losing the human checkpoint | Every condition-triggered gate maps 1:1 to a real Legacy trigger condition (P2, ASSUM dependency, unresolved Critical question) — no new looser condition was invented |

## 4. Explicitly Not Re-litigated

Per the brief's instruction, Phase 0's confirmed findings (Adaptive Routing = MISSING as agent behavior; Requirement Intelligence = MISSING as agent behavior; the two templates are structurally mirrored; OpenSpec is optional) are treated as the settled factual baseline for this mapping and are not re-audited here.
