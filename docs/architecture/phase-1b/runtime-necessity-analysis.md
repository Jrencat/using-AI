# Phase 1B-2A Runtime Necessity Analysis

> Status: `ANALYSIS-ONLY`. No Runtime, CLI, MCP, SDK, Orchestrator, State Engine, Evidence Engine, or Policy Engine is implemented or designed in detail by this document. No Phase 1A `FROZEN` file is modified. No VILIMS/business path is accessed — the Phase 1B-1 VILIMS finding is cited only as an already-recorded `OBSERVED CASE`, never as proof that using-AI's own Runtime capability exists or has been validated.

---

## 1. Executive Summary

using-AI today is 100% Markdown: two Legacy prompt templates, a README, an example, and the `docs/architecture/**` design set. `Glob({pattern:"**/*"})` over the repository (excluding `.git`) confirms zero scripts, zero CLI, zero MCP/SDK code, zero test runner, zero persistence layer. The only "execution" that has ever happened against this design is one narrative, human-supervised walkthrough (`pilot-walkthrough.md`) that never reached Task `IN_PROGRESS` — it stayed `BLOCKED` on a Human Gate.

Applying the Four Necessity Conditions (§18) to every candidate control: several controls fail only Agent-reliability (Condition A) and Document-insufficiency (Condition B) in theory, but **none currently satisfy Condition D** — a real, in-scope, non-VILIMS occurrence, or an actual block on current usage. The VILIMS case is the one real failure ever observed, and it is explicitly excluded from counting toward using-AI's own necessity case per the governing instruction.

**Decision: `NO RUNTIME NEEDED YET`.** Several items (Evidence provenance, Task Resume, Retry-cap enforcement, true Human-Gate blocking) are real, honestly-documented theoretical gaps — they are recorded as `RUNTIME DEFERRED` candidates with explicit trigger conditions (§19), not dismissed. But none currently justify moving into Runtime design.

---

## 2. Current using-AI Capability Boundary

### 2.1 当前已经具备（文件证据）

- Protocol Object Model：7 Core Objects + 2 fold + 2 demote，完整定义（`protocol.md` §4，`adr.md` ADR-001/002）— `DESIGNED`
- State Model：8 个对象状态机 + 5 条 Cross-Object Invariants（`state-model.md`）— `DESIGNED`
- Requirement Intelligence 流水线 + Investigation Bound 五信号方案（`protocol.md` §6，`phase-1b-scope.md` §2）— `DESIGNED`，Investigation Bound 有一次真实叙事性应用（`pilot-walkthrough.md` §1）— `PARTIAL/OBSERVED`
- Adaptive Routing 四级分类法 + Complexity 4 tier（`routing.md`）— `DESIGNED`，一次真实应用（`pilot-walkthrough.md` §6-7）— `PARTIAL/OBSERVED`
- Evidence 5 级 Trust Tier + PASS 规则（`evidence.md` §2）— `DESIGNED`
- Human Gate 语义（Trigger/Context/Decision/Authority/Effect/Audit，`protocol.md` §8）— `DESIGNED`，一次真实克制应用（`pilot-walkthrough.md` §8）— `PARTIAL/OBSERVED`
- Legacy 7-stage → Protocol Primitive 映射，逐条真实行号引用（`legacy-mapping.md`）— `DESIGNED`；原模板文件本身未被修改 — `IMPLEMENTED`（就"文件未被破坏"这一事实而言）
- Evidence Self-Check Checklist（`docs/architecture/templates/evidence-self-check.md`）— `IMPLEMENTED`（文档制品本身存在），效果 `UNPROVEN`
- Proposed-changes 登记机制（`proposed-changes.md`）— `IMPLEMENTED`（文档制品本身存在）

### 2.2 当前没有（无代码/无工具证据）

- 任何形式的 Runtime / Harness / Orchestrator 代码
- Persistent execution state（Task/Attempt 的跨 session 持久化存储）
- Machine-enforced state transition（没有任何东西阻止 agent 自行声明 Task `DONE`）
- 独立认证的 Evidence provenance（"这条 Evidence 确实来自这次真实调用"目前无法被独立核实）
- Tool capability enforcement（Agent Contract 的 `forbidden` 字段是声明，不是强制）
- 自动 Retry / 自动 Resume
- 一个可查询的 Human Gate 登记表（`human-decisions.md` Decision 5 已承认此缺口）

这条边界与 Phase 1A `protocol.md` §15/§16（Explicit Non-Goals / Runtime-Harness Boundary）、`simulation.md` Architecture Attack #1/#3/#4/#8 完全一致，本文档未发现新矛盾。

---

## 3. Enforcement Classification

| 能力 | 分类 | Failure Mode（若仅靠该层） | 为什么当前仍可接受 |
|---|---|---|---|
| Requirement Intelligence / Investigation Bound | `AGENT_ENFORCED` | Agent 可能提前停止调查或无限调查而自称"已充分" | 唯一真实案例（`pilot-walkthrough.md` §1）自查通过，且 Scope 被限定在一次性、有人工复核的任务；`human-decisions.md` Decision 1 已明确接受此风险 |
| Routing / Complexity 判断 | `AGENT_ENFORCED` | Agent 可能误判复杂度、错误跳过必要 Stage | 唯一真实案例显示 Agent 选择了保守方向（升级为 COMPLEX，未跳过任何本该保留的环节）；错误方向的失败模式尚无真实样本 |
| Question 生成 / Spec 形成 | `AGENT_ENFORCED` | 遗漏关键问题、把 Critical 问题误判为非 Critical | `state-model.md` §1.1 有硬规则（Critical Question 不能直接 OPEN→ASSUMED），属于 `DOCUMENT_ENFORCED` 兜底，非纯 Agent 自律 |
| Evidence Self-Check（本轮新增） | `DOCUMENT_ENFORCED` | Agent 可以直接跳过 Checklist 不用 | Checklist 本身已明确声明"辅助模板、非强制执行"，不试图伪装成强制机制 |
| Agent Contract 的 `forbidden_actions` | `DOCUMENT_ENFORCED`（声明层）；真正的执行边界目前落在宿主编码 Agent 自身的工具权限系统（例如本会话所用编码 Agent 的 Bash 二次确认机制），不是 using-AI 自建的能力 | 如果 Agent 决心违反 Contract 且宿主工具没有拦截，Protocol 本身无法阻止 | 已有一次真实、正向的证据：`pilot-selection.md` §C 记录的 "Bash `rm` 被拒绝执行" 正是宿主工具权限系统实际拦截了一次危险操作，且这个能力**独立于 using-AI、已经存在** |
| Evidence Trust Tier 标注 | `AGENT_ENFORCED`（自报 Tier）+ `HUMAN_GATE`（非测试类 Claim 强制人工确认，`human-decisions.md` Decision 4） | 二阶自证问题（见 §5）：agent 既声称做了事，又自行给这份"证据"贴 Tier 标签 | 当前唯一真实案例从未产生过一条被滥用的 Evidence（Task 从未进入 EVALUATING）；且 Decision 4 已经把非测试 Claim 的最终判定权收回给人 |
| Task 状态声明（尤其 `DONE`） | `AGENT_ENFORCED`，理论上应受 `evidence.md` §2 PASS 门槛约束 | Agent 可以声明 `DONE` 而实际 Evidence 不足 | 同上，PASS 门槛 + Human Gate 双重兜底目前尚未被真实违反过 |
| Retry / `INVALID_AGENT_RESULT` | `DOCUMENT_ENFORCED`（规则定义完整，`state-model.md` §4），强制执行缺失 | 没有任何东西阻止 agent 无视 retry cap 继续尝试 | 从未有真实 Task 进入过 retry 循环，风险目前是理论性的 |
| Human Gate 的"真正阻断" | 名义上 `HUMAN_GATE`，但若无宿主强制，实质只是 `AGENT_ENFORCED`（agent 叙述"需要确认"后自行停止） | Agent 可能在叙述 Gate 之后仍然继续往下做 | 唯一真实案例（`pilot-walkthrough.md` §8）agent 确实停在了 Gate 前，未继续；`human-decisions.md` Decision 5 已明确接受"无独立查询机制"的风险 |
| Legacy 7-stage 映射 | `DOCUMENT_ENFORCED` | 无（这是纯映射文档，不涉及执行） | 不适用 |

---

## 4. Runtime Necessity Matrix

Priority 说明：`P0` 不解决则协议无法安全成立 / `P1` 明显影响可靠性、值得近期 Runtime 化 / `P2` 真实需求尚未证明，暂不实现 / `P3` 纯未来扩展。

| Control | 当前设计 | Failure Mode | 无 Runtime 是否可工作 | 是否已有真实证据 | 最小强制机制（若未来需要） | Enforcement | Priority |
|---|---|---|---|---|---|---|---|
| Evidence provenance（"这条证据真的来自这次调用"） | Agent 自行标注 Trust Tier | 二阶自证：Tier 标签本身可能是 `SELF_REPORT` | 可工作，但依赖人工复核（Decision 4） | 否（using-AI 自身无真实违反案例；VILIMS 案例不计入） | 由宿主环境而非 agent 生成的、带时间戳/参数的调用记录 | `HOST_RUNTIME_ENFORCED`（候选，未证实必要） | `P2` |
| Task Resume（跨 session 接续） | 未定义（`proposed-changes.md` Change 1） | 无法判断 Task 是否真的仍在执行、旧 Evidence 是否可信 | 可工作——因为目前没有真实场景需要跨 session 接续 | 否（using-AI 自身唯一 Task 从未进入 IN_PROGRESS） | Task 持久化 + Ownership 转移记录 + 旧 Evidence 强制复核 | `HOST_RUNTIME_ENFORCED`（候选） | `P2` |
| State transition 权威性（Agent 自称 `DONE`） | `evidence.md` PASS 规则 + Decision 4 人工确认 | Agent 可能在 Evidence 不足时仍声明 `DONE` | 可工作，因为非测试 Claim 已强制走人工 | 否 | 状态迁移前强制校验 Evidence 是否达到门槛 | `HOST_RUNTIME_ENFORCED`（候选） | `P2` |
| Retry cap 强制执行 | `state-model.md` §4 定义 cap 语义 | Agent 可能无视 cap 持续重试 | 可工作——目前从未有真实 Task 进入过 retry | 否 | 一个记录 attempt 计数并在超限时强制切 `FAILED` 的最小计数器 | `HOST_RUNTIME_ENFORCED`（候选，成本很低） | `P2` |
| Agent Contract 工具能力边界 | Protocol 声明 `forbidden_actions` | Agent 违反声明，Protocol 无法拦截 | **已经部分可工作** ——宿主编码 Agent 自身的工具权限系统（非 using-AI 自建）已提供真实拦截先例 | **是**——`pilot-selection.md` §C "Bash `rm` 被拒绝执行" 是真实、已发生的拦截案例 | 无需 using-AI 自建；建议文档层面明确"依赖宿主工具权限配置"作为已有的最小强制层 | 宿主已提供，非 using-AI 的 `HOST_RUNTIME_ENFORCED` 缺口 | `P3`（对 using-AI 而言几乎不需要额外投入） |
| Investigation Bound（防止无限调查） | 五信号方案，`phase-1b-scope.md` §2 | Agent 可能无限调查或过早停止 | 可工作——唯一真实案例自查通过，且规模很小 | 部分（一次真实、克制的正向案例，不是负面证据） | 调用次数/文件数的软上限记录 | `AGENT_ENFORCED`（现状已足够） | `P3` |
| Human Gate 真正阻断后续执行 | Agent 叙述后自行停止 | Agent 可能叙述 Gate 后仍继续 | 可工作——唯一真实案例中 agent 确实停住了 | 否 | 宿主强制在 Gate 触发时拒绝后续工具调用（类比 Agent Contract 边界已有的宿主拦截先例） | `HOST_RUNTIME_ENFORCED`（候选，但可能已被宿主工具权限系统部分覆盖，见上） | `P2` |

---

## 5. Evidence Trust Analysis

**当前设计**：`evidence.md` §2 五级 Tier（`SELF_REPORT < RUNTIME_GENERATED < TOOL_GENERATED < INDEPENDENT_VERIFICATION < HUMAN_VERIFICATION`），`PASS` 需要 ≥`RUNTIME_GENERATED`。

**核心问题（二阶自证）**：Agent 声称"我执行了命令"→"这是 RUNTIME_GENERATED 证据"，这个 Tier 标签本身也是由 agent 叙述赋予的，构成二阶自我认证——本文档确认这**确实构成一个真实、非假设性的逻辑缺口**，而不只是理论风险的重复表述。

逐项回答用户要求的十个问题：

1. **当前 Protocol 能否解决？** 不能——`evidence.md` 定义了 Tier 分级规则，但没有定义如何核实"标签是否属实"。
2. **Template 能否解决？** 不能——`evidence-self-check.md` 能提示 agent 自查，但无法强制其诚实标注。
3. **Agent Contract 能否解决？** 不能——Contract 约束"能做什么"，不约束"如何证明做过"。
4. **Human Gate 能否解决？** **部分可以**——`human-decisions.md` Decision 4 已经把非测试 Claim 的最终判定权收回给人，这实质上是用 Human Gate 替代了对 Trust Tier 标签本身的独立核验，是当前唯一已生效的缓解措施。
5. **是否必须有 Host/Runtime 提供 provenance？** 理论上是解决这个问题的唯一根本方案，但"必须现在做"不成立（见 Condition D 分析，§18）。
6. **Runtime 最小需要记录什么？**（仅作候选记录，不设计）：调用发生的时间戳、调用参数、调用来源，由宿主生成而非 agent 自行转述。
7. **是否必须现在实现？** 否——无真实违反案例。
8. **如果暂不实现，当前 Evidence 应如何表述？** 继续如实标注：非测试类 Claim 的 Trust Tier 本质上受限于"agent 自报"，最终判定必须经 `HUMAN_VERIFICATION`，不得把 agent 自报的 `RUNTIME_GENERATED` 当作已经等价于被独立核实。
9. **哪些场景可以接受 SELF_REPORT？** 低风险、可被人一眼复核的场景（例如本文档这类纯分析性产出，人工阅读即可验证）。
10. **哪些场景必须拒绝 SELF_REPORT？** 任何不可逆操作、任何业务代码变更 Claim、任何"测试通过"类 Claim——这些已经被 `evidence.md`/`protocol.md` §9 Fail-Closed 规则覆盖。

**结论**：这是一个真实的 Enforcement Boundary，且不可由 Agent 自律可靠解决（Condition A、B 成立）。但 Condition D（是否已经真实发生或阻碍当前使用）目前不成立——using-AI 自身从未产生过一条被验证是伪造的 Evidence。VILIMS 案例只能作为 `OBSERVED CASE / UNPROVEN AS SYSTEM CAPABILITY` 提及，不能作为 using-AI 自身 Evidence 机制失败的证据（那次矛盾恰恰是被人工叙事性投资发现的，不是被 using-AI 的 Runtime 或工具发现的）。**不设计 Evidence Engine**；记录为 `RUNTIME DEFERRED`，触发条件见 §19。

---

## 6. Task / Attempt / Resume Analysis

**同 Session Retry**：Agent 失败→修复→重试，属于 `state-model.md` §4 已定义的 `EVALUATING──(FAIL, attempts<cap)──>IN_PROGRESS` 转移，发生在同一次连续执行中，不需要持久化，也不需要 Runtime——整个循环可以在一次工具调用序列内完成，编码 Agent 本身的会话上下文就足够。**结论：同 Session Retry 不需要 Runtime。**

**Cross-session Resume**：Session A 中 Task `IN_PROGRESS`，Session 结束后 Session B 需要：上一次 Task 状态、Attempt 历史、Evidence、未完成 Question、Human Gate 状态、当前 Agent Contract、修改记录——这些若无持久化层，确实无法被可靠恢复，只能依赖 agent 重新阅读某种人工维护的交接文档（这正是 VILIMS 场景中 HANDOFF.md 试图扮演的角色，且已被 Phase 1B-1 证明"文档声称的状态可能与实际不符"）。

**是否已经证明 Runtime 必须存在？** 不成立。理由：(a) using-AI 自身从未有过一个真正进入 `IN_PROGRESS` 的 Task，因此没有真实的跨 session Resume 案例——唯一相关的观察（VILIMS/HANDOFF.md）发生在被排除的业务项目中，且描述的是那个项目自己的交接实践，不是 using-AI Protocol 被真实使用后失败的证据；(b) 即使把 VILIMS 案例当作"未来若发生会是什么样子"的参考，它恰恰说明的是**没有 Runtime 时人工 handoff 文档本身不可靠**，这是一个支持"若真的需要 Resume，document-only 方案不够"的论据，但不能替代"当前是否已经需要 Resume"这个前提判断。

**结论：`P2 / UNPROVEN`**，与 `proposed-changes.md` Change Proposal 1 的登记一致，本文档不提升其优先级。

---

## 7. State Transition Analysis

`state-model.md` 的 Requirement/Task 状态机均由 agent 在叙述中自行驱动迁移（例如宣布"Task 已经 DONE"）。问题：如果 Evidence 不完整、Required Question 未回答、Test 未执行、Human Gate 未通过，Protocol 能否阻止这种状态伪造？

**回答**：Protocol 本身（纯文本规则）不能物理阻止——它只能规定"不应该"这样迁移。但当前设计有两层真实存在的缓解：(1) `evidence.md` §2 的 PASS 门槛把"证据不足"标记为 `INSUFFICIENT`，理论上应阻止 `DONE`；(2) `human-decisions.md` Decision 4 把非测试 Claim 的最终判定权交给人工，形成一道 Human Gate 兜底。

**这只是理论风险，还是已经阻碍实际工作？** 目前是理论风险——using-AI 自身没有一次真实的"Task 被错误标记为 DONE"案例（因为从未有 Task 真正走到这一步）。**不建议现在实现 State Engine。** 记录为 `RUNTIME DEFERRED`，与 §5 Evidence Trust 共享同一触发条件（见 §19），因为二者本质是同一个"自报状态是否可信"问题的两个表现面，不应分别重复建设。

---

## 8. Retry / INVALID_AGENT_RESULT Analysis

**Agent 能否自己判断结果 INVALID、触发 Retry、判断次数、判断是否该进 Human Gate？** 目前完全依赖 agent——`state-model.md` §4 已经把 `INVALID_AGENT_RESULT` 与 `FAIL` 同等对待（都消耗 retry cap），这是 Policy Definition 层面已经解决的部分。但 Policy Enforcement（真正阻止 `Retry > N`）不存在——没有计数器，没有强制切换到 `FAILED` 的机制。

**是否可能出现 Agent 自称 PASS 而 Evidence 与 Claim 冲突？** 理论上可能，但目前无真实案例（using-AI 自身从未产生这类冲突；VILIMS 案例不计入）。

**是否需要 Runtime 强制？** 是否现在需要 —— 不需要。这是 Runtime Necessity Matrix（§4）中标注的 `P2` 项，且是所有候选中**实现成本最低**的一个（一个简单的 attempt 计数器，不需要完整状态引擎）——如果未来确实需要 Runtime，这可能是最小 Runtime 里最先该做的一项，但"成本低"不构成"现在就做"的理由（Condition D 仍不满足）。

---

## 9. Scope / Capability Boundary Analysis

**问题**：Agent Contract 声明"Forbidden: 修改数据库"，但如果 Agent 实际拥有数据库工具，谁能阻止 Agent 违反 Contract？

**回答**：Protocol 层面只能要求遵守，无法保证。但本文档发现一个**真实、已发生的正面证据**：`pilot-selection.md` §C 记录"Bash `rm` 被拒绝执行"——这次拦截发生在宿主编码 Agent 自身的工具权限系统层面（本会话所用编码 Agent 的危险命令二次确认机制），**不是 using-AI 自建的任何机制**，且早于 using-AI 的 Protocol 设计就已经存在。

**这对 using-AI 意味着什么**：真正可靠的能力边界（Tool-level permission / Host-level enforcement）已经由宿主编码 Agent 提供，using-AI 不需要重新发明一套。using-AI 的 Agent Contract 应该被理解为 **Protocol-level declaration**（写清楚"不应该做什么"，给 agent 和人一个可读的约定），真正的强制层是**外部现有基础设施**，不是 using-AI 需要建的 Runtime。

**是否已经需要 using-AI 自建这个能力？** 不需要——这是本次分析中唯一一个"Condition A/B 成立但已经有更便宜的现成替代方案"的例子，应明确标注 `P3`（对 using-AI 而言几乎不需要额外投入），而不是升级为 P0。

---

## 10. Investigation Bound Analysis

`phase-1b-scope.md` §2 已定义 Budget / Evidence Sufficiency / Information Gain / Scope / Escalation 五信号方案，`human-decisions.md` Decision 1 已经把"是否需要额外硬性数字上限"这一问题交给人工决定，且默认推荐是不加硬编码上限。

**Agent 是否可以无限调查？** 理论上可以。**Agent 自称"Evidence 已经 sufficient"是否可信？** 唯一真实案例（`pilot-walkthrough.md` §1）显示这次自查是克制、有据可查的，调查范围与规模都很小（一个功能点、约十几次工具调用）。

**是否需要 Runtime 限制调用次数/时间/token/文件数？** 不需要——当前唯一真实证据是正面的（自律有效），没有任何真实的"失控调查"案例。继续沿用 Protocol + Agent discipline（`AGENT_ENFORCED`），维持 Human Decision 1 已经做出的选择，不新增机制。

---

## 11. Human Gate Analysis

**Human Gate 是否只是 Agent 输出一句"需要用户确认"，还是真正能阻止后续 Task？** 诚实的回答：目前只是前者。`state-model.md`/`protocol.md` 没有任何机制在 Agent 叙述"需要确认"之后，物理阻止它继续调用工具——真正的阻止依赖 agent 自己"说到做到"。

**唯一真实案例的表现**：`pilot-walkthrough.md` §8 中，agent 确实在两个 Gate 处停住，没有继续往下做。这是一个正面样本，但样本量为 1，且发生在一个高度受控、人工全程在场的会话中。

**如果要真正阻止，是否必须由 Runtime 保存 Gate 状态并拒绝继续执行？** 理论上是——但 §9 已经发现，宿主编码 Agent 的工具权限系统已经提供了类似能力的一个真实先例（Bash `rm` 拦截）。这提示一个更便宜的路径：与其为 Human Gate 单独设计一套 Runtime 阻断机制，不如先确认"利用宿主已有的工具确认/权限模式，在 Gate 触发时的高风险动作（写文件、执行命令）上要求人工批准"是否已经足够——这仍然是候选思路，不在本轮设计范围内。

**当前是否已经有真实执行 Runtime，因此这个问题现在值得解决？** 没有。记录为 `P2 / RUNTIME DEFERRED`，与 Evidence Trust（§5）共享同一类触发条件。

---

## 12. Legacy 7-stage Analysis

本节刻意不把 Runtime 理解为"把 7 个 Stage 自动化"。逐条检查：

| Legacy Stage | 人类组织方式的部分 | 真正需要 Runtime Enforcement 的 Control Primitive（如果有） |
|---|---|---|
| 1 需求分析 & QA | 人工决定何时关闭问题 | 无——这是 Human Authority 范畴，不是执行边界 |
| 2 Spec 设计 | 人工 Review 通过 | 无 |
| 3 OpenSpec Change | 人工 Review | 无 |
| 4 Tasks 拆解 | 人工 Review Scope | 无 |
| 5 代码实现 | 人工授权高风险任务 | Agent Contract 边界执行（见 §9，已有宿主级先例，非 using-AI 需自建） |
| 6 测试生成 + 自愈 | —— | **Test Execution Evidence**（不是"Stage 6"本身）——这正是 `evidence.md` §4 ADR-003 已经标注的 GAP：非测试类 Claim 没有对应 `auto-test`-equivalent 工具，且明确不在本轮设计范围 |
| 7 最终审计 + 归档 | —— | **Evidence / Claim reconciliation**（不是"Stage 7"本身）——即 §5/§7 讨论的同一个"自报状态是否可信"问题 |

**结论**：Legacy 7 个 Stage 本身全部是"人类组织方式"，没有一个 Stage 编号本身需要 Runtime。真正可能需要机器保证的只有两类 Control Primitive（Test Evidence、Claim-Evidence Reconciliation），且二者已经在 Phase 1A（ADR-003 GAP）与本文档 §5/§7 中被识别，不是本节的新发现，**不建立 Stage Runtime 1-7**。

---

## 13. Auto-Test Boundary

`adr.md` ADR-003 已经限定：using-AI 对 `auto-test` 只做 **Semantic Reuse**（Claim vs Actual、`INVALID_AGENT_RESULT` 概念），不做 Code Reuse / Architecture Import。

**using-AI 是否真的需要 Auto-Test 已实现的那些能力（Resume、Run history 等）？** 需要区分 **Testing Evidence** 与 **General Software Engineering Evidence** 是两个不同问题：`auto-test` 解决的是"一次 Playwright 测试运行的证据链"，其 Resume/Run history 是为了应对测试执行本身可能中断重跑；using-AI 面对的是"一个开发任务从需求到交付的证据链"，跨度更长、涉及的 Claim 类型更广（不止测试通过与否）。**不能因为 Auto-Test 已经实现过 Resume，就假设 using-AI 现在也需要一份同构的 Resume 机制**——§6 已经独立论证 using-AI 自己的 Resume 需求目前是 `UNPROVEN`，不借用 Auto-Test 的既有实现作为理由。

**结论**：不修改 Auto-Test，不复制 Auto-Test 代码，不因为 Auto-Test 存在就提升 using-AI 任何 Runtime 候选项的优先级。

---

## 14. No-Runtime Walkthrough

**演练任务**（纯 using-AI 自身、无业务代码）：将 `claude研发流水线提示词模板.md` 变量表中 `{{REVIEW_DIR}}` 的示例值改为一个新值，并检查 `README.md` 变量表是否同步一致。

```
Requirement（intent：更新示例值并保持两处文档一致）
↓
RI（Grep 定位所有引用 {{REVIEW_DIR}} 的位置：模板文件 + README）
↓
Routing（SIMPLE：单字段文本编辑，无 schema、无不可逆操作）
↓
Task（T-1 编辑模板；T-2 核对 README）
↓
Agent Contract（允许：编辑这两个文件；禁止：改动其他变量）
↓
Execution（Edit 工具）
↓
Evidence（Edit 工具自身的成功回执 + 事后 Grep 确认无残留旧值，均为 RUNTIME_GENERATED）
↓
Evaluation（比对 Claim 与 Evidence：两处文件是否都显示新值）
↓
DONE
```

**哪些步骤完全不需要 Runtime？** 全部——因为宿主编码 Agent 的工具调用本身（Edit/Grep/Read 的成功或失败回执）已经提供了这个小任务所需的全部"执行证据"，不需要额外的持久化或状态引擎。这与 §9 的发现一致：现有编码 Agent 宿主环境已经提供了相当一部分本以为需要 Runtime 才能获得的保障。

**失败场景**：Agent 声称"Task DONE"，但实际上 README 的核对步骤被跳过、Evidence 缺失。

- **Protocol 能发现吗？** 不能自动发现——`evidence.md` PASS 规则要求 ≥`RUNTIME_GENERATED`，但没有强制"必须真的跑一次 Grep"。
- **Template（Evidence Self-Check）能发现吗？** 能提示，不能强制——agent 仍可以跳过勾选直接下结论。
- **Human Gate 能发现吗？** 只有当人工真的去复核 README 内容时才能发现——如果人工只读 agent 的文字总结而不亲自核对，就会重复 VILIMS/HANDOFF.md 同一类问题。
- **是否必须 Runtime？** 这正是 §5/§7 已经识别的同一个 Evidence Trust / State Transition 问题的又一次具体化，**不是新发现**，不升级任何优先级。

---

## 15. False Runtime Requirements

逐项检查，确认均不适用于当前阶段：

- **"Agent 可能犯错，所以需要 Runtime。"** 不成立——Agent 会犯错 ≠ Runtime 能解决；本文档全程以 Condition D（真实发生/阻碍当前使用）作为门槛，而非"理论上可能出错"。
- **"未来需要 Resume，所以现在实现 Resume。"** 不成立——§6 已确认无真实需求，维持 `proposed-changes.md` 的 `P2` 标注。
- **"Evidence 很重要，所以需要 Evidence Engine。"** 不成立——§5 已经把问题精确定位到"Trust Tier 标签的独立核验"这一具体 Enforcement Boundary，而非笼统地论证"Evidence 重要就该有 Engine"。
- **"State Model 有状态，所以需要 State Engine。"** 不成立——Protocol State（文档定义的状态语义）与 Runtime State Machine（机器强制执行）是两回事，§7 已明确区分。
- **"多 Agent 未来会需要，所以现在做 Orchestrator。"** 不适用——当前默认 Single Agent，本文档全程未发现任何多 Agent 并发场景的真实证据。
- **"Agent-Native 就必须有 Runtime。"** 不成立——Agent-Native 是工作模型（Protocol + Object + Routing），Runtime 是执行基础设施，本文档的核心结论正是二者不能划等号。

本文档未发现任何新的伪需求，也未发现以上六类论证在本轮分析中被实际使用来论证某个候选项。

---

## 16. User Workload Impact

using-AI 当前的核心卖点（`README.md` "依赖与适配"一节）是**模型无关、技术栈无关、不绑定任何工具链**——任何具备文件读写能力的编码 Agent 都可以直接使用两份 Markdown 模板。这个"零安装、零配置"的可移植性本身就是当前设计的一部分价值。

如果引入 Runtime：用户可能需要——配置额外的运行环境、学习新的 CLI 或状态查看方式、维护 Task/Run 持久化文件、处理 Runtime 自身可能出现的异常。如果 Runtime 只是把"原来 agent 自己顺手做的事"变成"用户必须额外维护的系统"，收益尚未证实（§5-§11 均显示 `UNPROVEN`/`P2`），成本却是确定会发生的（配置、学习、维护）。

**定性结论**：在收益尚未被证实的当前阶段，引入 Runtime 的确定成本大概率超过不确定收益，这进一步支持 §18 的 Decision A，而不是相反。

---

## 17. Runtime Boundary

当前不存在足够证据支持 Runtime Boundary。

（本节按用户要求，在 Decision = `NO RUNTIME NEEDED YET` 时仅需明确写出以上结论；候选的未来触发条件已分别记录在 §5/§6/§7/§8/§11 及 §19，不在本节展开设计。）

---

## 18. Decision

### Four Necessity Conditions 逐项汇总

| 候选能力 | A. Agent 不可靠 | B. Document 不足 | C. Human Gate 不合适 | D. 当前真的值得 | 结论 |
|---|---|---|---|---|---|
| Evidence provenance | 成立（理论） | 成立（理论） | 不完全——Decision 4 已部分缓解 | **不成立** | 不 Runtime 化 |
| Task Resume | 成立（理论） | 成立（理论） | 不适用（非决策类问题） | **不成立** | 不 Runtime 化 |
| State transition 权威性 | 成立（理论） | 部分——PASS 规则+Decision 4 已缓解 | 不完全 | **不成立** | 不 Runtime 化 |
| Retry cap 强制 | 成立（理论） | 成立（规则有，强制无） | 不适用 | **不成立** | 不 Runtime 化 |
| Agent Contract 工具边界 | 成立 | 成立 | 不适用 | **成立，但已有更便宜的现成替代**（宿主工具权限系统） | 不需要 using-AI 自建 |
| Investigation Bound | 部分成立（理论） | 部分——五信号方案已是 Document 层缓解 | 不适用 | **不成立**（唯一样本是正面的） | 不 Runtime 化 |
| Human Gate 真正阻断 | 成立（理论） | 成立（理论） | 本身就是 Human Gate 问题，不能自我替代 | **不成立** | 不 Runtime 化 |

**Decision: `NO RUNTIME NEEDED YET`**

理由：当前 Protocol + Template + Agent discipline + Human Gate 的组合，足以支撑 using-AI 进入下一阶段的验证工作。所有理论上成立的 Failure Mode（A、B 成立）均未通过 Condition D（真实发生 / 阻碍当前使用 / 必须机器保证的安全边界）的检验。VILIMS 案例被严格排除在 Condition D 的证据之外，因为它是另一个项目、由人工叙事性调查发现的问题，不是 using-AI 自身 Runtime 缺失导致的真实失败。

---

## 19. Open Questions

以下问题保持 `UNPROVEN`，作为未来重新评估 Runtime 必要性的触发条件（Trigger），而不是当前待办：

1. **Evidence provenance / 二阶自证问题**（§5）——Trigger：using-AI 自身（非 VILIMS）的一次真实使用中，出现被证实错误标注 Trust Tier 的 Evidence。
2. **Task Resume**（§6）——Trigger：一个真实 Task 确实跨 session 被接续，且因无 Resume 定义导致实际返工或风险。
3. **State transition 权威性 / Retry cap 强制**（§7、§8）——Trigger：一次真实案例中，Agent 自报 `DONE`/`PASS` 而 Evidence 实际不足，且未被人工及时发现。
4. **Human Gate 真正阻断**（§11）——Trigger：一次真实案例中，Agent 在叙述 Human Gate 之后仍然继续执行了本应被阻止的动作。
5. **宿主工具权限系统是否足以覆盖 Agent Contract 边界**（§9）——这不是一个"缺口"，而是一个待确认的假设：需要在下一次真实使用中观察，宿主的权限确认机制是否总能覆盖 Agent Contract 里声明的 `forbidden_actions`，还是存在两者不完全对齐的场景。

这些触发条件本身应当靠**真实、非 VILIMS 的 using-AI 使用**来验证，而不是靠推演或本文档进一步分析产生。

---

## 20. Phase 1B-3 Recommendation

**Next Recommended Phase: `STOP`**（本会话范围内）。

若未来需要继续，自然的下一步是 **Additional Evidence Collection**——即在 using-AI 自身范围内（非 VILIMS、非业务代码）积累第二个、第三个真实（哪怕是小规模的）使用案例，观察 §19 中列出的触发条件是否被真实命中。**不建议**直接进入 `1B-2B Minimal Runtime Design`——本文档没有发现任何满足全部四个 Necessity Condition 的能力，因此没有设计对象可以进入下一阶段设计。

---

```text
Phase: 1B-2A
Status: COMPLETE

Decision:
NO RUNTIME NEEDED YET

Runtime MUST:
（不适用——当前无满足四条件的候选能力）

Runtime SHOULD:
（不适用，同上；如需参考候选清单见 §4 Runtime Necessity Matrix 中标注 P2 的行）

Runtime MUST NOT:
- 不得现在实现 Evidence Engine / State Engine / Policy Engine / Orchestrator
- 不得为 Task Resume 现在设计跨 session 持久化机制
- 不得因为 Auto-Test 已有 Resume/Run history 就照搬到 using-AI
- 不得重新发明 Agent Contract 工具边界——应优先确认并依赖宿主编码 Agent 已有的工具权限系统

Current Blocking Reason:
无——当前 Protocol + Template + Agent discipline + Human Gate 组合已足以支撑下一阶段验证工作；未发现任何能力因缺少 Runtime 而无法可靠成立到"阻塞当前使用"的程度。

Next Recommended Phase:
STOP（若继续，应为 Additional Evidence Collection，而非 1B-2B Runtime 设计）

Artifact:
docs/architecture/phase-1b/runtime-necessity-analysis.md
```
