# using-AI 架构状态审查 — v0.1

> 范围：仅审查 `using-AI` 工作区当前实际文件。不访问、不调查任何业务项目（含 VILIMS）。Phase 1A（`protocol.md`/`state-model.md`/`routing.md`/`evidence.md`/`legacy-mapping.md`/`adr/adr.md`）保持 `FROZEN`，本文档不修改其中任何一份，仅在发现问题时提出"建议变更"。真实 Pilot 不在本轮范围内；所有需要真实执行才能回答的问题，只登记进 §B 待验证清单。

---

## 1. 当前架构是否真的已经从 Prompt Workflow 演进为 Agent-Native Workflow？

**结论**：设计文档层面已从"固定 Stage 顺序"转向"对象 + 状态机 + 路由"模型；但这只是文档设计，没有任何 Runtime/Harness 真正执行这套状态机。原 7 阶段 Prompt 模板文件本身未被修改、未被替换，仍是可独立使用的产物——二者是并存关系，不是替代关系。
**状态**：`DESIGNED`（协议/状态机/路由）
**证据**：`protocol.md` 文首 "DESIGNED, NOT IMPLEMENTED"；`routing.md` §1 四级表格中 Agent-selected/System-enforced 均标注 `DESIGNED` only；本轮 `Glob` 确认 `claude研发流水线提示词模板.md`/`codex研发流水线提示词模板.md` 仍完整存在。
**缺口**：唯一一次尝试真实套用这套模型的案例（VILIMS Pilot）已按上一轮指令中止，未产出任何完整端到端执行结果——本轮不得继续调查，仅登记为待验证。

---

## 2. Core Objects 是否足够，并且是否存在过度抽象？

**结论**：7 个顶层对象 + 2 个 fold（Question→Requirement、Run/Attempt→Task）+ 2 个 demote（Human Gate、Policy）均有 ADR 逐条论证"无独立身份/复用场景"，不是硬凑数字。目前没有发现新的过度抽象信号，但也没有一次真实案例完整用到全部 7 个对象——`pilot-walkthrough.md` 实例化了 Requirement/Question/Task/Agent Contract，Evidence/Evaluation 仅在叙述层面引用，Spec 从未被实例化过。
**状态**：`DESIGNED`（对象定义）/ `PARTIAL`（实际使用覆盖度）
**证据**：`protocol.md` §4/4.1/4.2；`adr.md` ADR-001/ADR-002；`pilot-walkthrough.md` §3/§9/§10。
**缺口**：Spec 对象完全没有真实实例；Evidence/Evaluation 从未产生过一条真正的 `EVALUATED` 记录。7 个对象"是否刚好够用"目前证据不足以判断。

---

## 3. Requirement Intelligence 是否已经具有明确、可执行的边界？

**结论**：`protocol.md` §6 给出完整流水线顺序，并明确自评 `NOT IMPLEMENTED`。`phase-1b-scope.md` §2 补充了五信号 Investigation Bound（Budget/Evidence Sufficiency/Information Gain/Scope/Escalation），是目前唯一具体到"何时停止"的规则，但仍是叙事性、依赖 agent 自觉遵守，非机械强制。`pilot-walkthrough.md` §1 是唯一一次真实套用并完成自评的案例。
**状态**：`DESIGNED`（流水线本身）+ `PARTIAL`（Investigation Bound，已有一次真实应用）
**证据**：`protocol.md` §6（L130-160）；`phase-1b-scope.md` §2.1-2.2；`pilot-walkthrough.md` §1 "Investigation Bound self-check"。
**缺口**：没有机制能独立检测 agent 是否诚实遵守了这个边界；`human-decisions.md` Decision 1 已明确承认"无强制止步机制"是真实局限，尚未解决。

---

## 4. Adaptive Routing 是否真正允许 Agent 根据任务情况选择路径，而不是人工选择固定阶段？

**结论**：`routing.md` 明确四级分类法，目前只到"Agent-selected"（推荐+人工确认）。`pilot-walkthrough.md` §7 是第一个真实案例：Agent 逐 stage 给出跳过/不跳过的理由，最关键的一点是 Stage 5 因 Critical Question `BLOCKED` 被 Agent **自己判断**为"不能进入"，而非被动等待人工指定阶段——这验证了"Agent 能做出路径判断"，而不只是执行预设分支。
**状态**：`DESIGNED`（机制）+ `PARTIAL`（一次真实案例，仍是叙事性推荐、无强制）
**证据**：`routing.md` §1；`pilot-walkthrough.md` §6（COMPLEX 升级判定）、§7（逐 stage 路由表）。
**缺口**：唯一真实案例的结果是"全部阻塞在 Human Gate 之前"；还没有一次案例展示 Agent 选择了更短路径并真的走完到 `DONE`。

---

## 5. Human Gate 是否只用于真正需要人的决策？

**结论**：`protocol.md` §8 明确界定 Agent/Human 各自权限边界，并专门警告不得"将 Human Authority 问题伪装成技术执行问题"。`pilot-walkthrough.md` §8 显示唯一真实案例只开了 2 个 Gate（真正的业务根因未知 + 待定的最终签字确认），没有为"文件是否存在"这类可自证事实开 Gate——是一个克制的正面信号。
**状态**：`DESIGNED`（规则）+ `PARTIAL`（一次真实、克制的应用，样本量为 1）
**证据**：`protocol.md` §8（L170-178）；`pilot-walkthrough.md` §8 及其末尾 "No gate was manufactured for a fact the agent could determine itself"。
**缺口**：样本量为 1，无法判断这条克制规则在更复杂/多 Requirement 并发场景下是否仍然成立。

---

## 6. Evidence / Evaluation 是否已经避免"Agent 自报完成"？

**结论**：`evidence.md` 明确规定 `PASS` 需要 ≥`RUNTIME_GENERATED` 证据，`SELF_REPORT`-only 只能停在 `INSUFFICIENT`。VILIMS Pilot 案例证明了"HANDOFF.md 的 Claim ≠ 实际证据"这类矛盾确实可以被检测出来，但这只是一次由 Agent 手动叙述执行的检测过程，using-AI 自身没有任何工具/机制强制执行这条规则——按本轮约束，该案例只能标记为观察案例，不构成系统能力证明。
**状态**：`DESIGNED`（规则）+ `OBSERVED CASE / UNPROVEN AS SYSTEM CAPABILITY`（唯一相关真实案例）
**证据**：`evidence.md` §2 Rule；`pilot-walkthrough.md` §16 Final Classification Summary。
**缺口**：没有任何代码/工具强制执行"PASS 需要 ≥RUNTIME_GENERATED"——`simulation.md` Architecture Attack #4 已承认此风险，至今未解决。

---

## 7. Task / Attempt / Retry / Resume 是否定义清楚？

**结论**：`state-model.md` §4 给出完整 Task 状态机（`ELIGIBLE`/`BLOCKED`/`IN_PROGRESS`/`EVALUATING`/`DONE`/`FAILED`/`RISK_PENDING`），retry cap 规则明确（`FAIL` 与 `INVALID_AGENT_RESULT` 均消耗重试次数，Attack #10 修复过一次真实 gap）。Attempt 已 fold 进 `Task.attempts[]` 并有字段定义。但"Resume"（跨 session 接续未完成 Task）从未被专门定义——`pilot-walkthrough.md` 中唯一真实 Task 从未进入 `IN_PROGRESS`，Resume 语义完全未被触及。
**状态**：`DESIGNED`（Task/Attempt/Retry 完整）/ 缺口明确（Resume 未定义）
**证据**：`state-model.md` §4 全文；`protocol.md` §5.4 `attempts[]` 字段定义。
**缺口**：无 Resume 状态转移规则。这是本次审查中唯一建议纳入"建议变更"的具体设计空白（见 §C）。

---

## 8. Legacy 7-stage 是否已经从固定流程转化为风险控制机制？

**结论**：`legacy-mapping.md` 给出完整 Stage→Primitive 映射表，逐条附真实模板行号引用，并列出 6 条"必须保留、不得弱化"的机制。原 7 阶段模板文件本身未被删除、重写或弱化——本轮 `Glob` 确认两份模板文件仍完整存在，本阶段及此前各阶段均无 `Edit` 记录。风险控制语义已被抽出并重组为条件触发（而非阶段号触发），但原始 Prompt 与新协议是并存关系。
**状态**：`DESIGNED`（映射论证完整）+ `IMPLEMENTED`（"原模板未被破坏"这一事实本身可核实）
**证据**：`legacy-mapping.md` §1/§2 全文；`Glob` 确认两份模板文件存在且未被 `Edit`。
**缺口**：没有一次真实执行并行对比"条件触发版"与"阶段号触发版"对同一真实任务的风险拦截效果——目前只是文档层面的映射论证。

---

## 9. 简单任务是否已经存在明确的短路径？

**结论**：`routing.md` §2 明确定义 SIMPLE tier 的默认路径（需求轻量→实现→验证，跳过完整 Spec/OpenSpec 仪式），并在 §5 指出这直接对应 Legacy README 自身 FAQ（小改动可只走 1/2/5 阶段，但 Spec 步骤不可跳过）。短路径的**设计**是明确的。但唯一的真实案例（VILIMS Pilot）被判定为 `COMPLEX`，从未真正走过一次 SIMPLE 短路径；`simulation.md` Case A 虽然是 SIMPLE tier，但基于虚构示例，调查步骤本身标注 `NOT EXECUTABLE`。
**状态**：`DESIGNED`（短路径规则明确）+ `UNPROVEN`（真实场景下的效果）
**证据**：`routing.md` §2/§5；`simulation.md` §2 Case A。
**缺口**：没有一个真实、非虚构的 SIMPLE 任务被完整走过一次短路径（从 Requirement 到 Task `DONE`）。

---

## 10. 当前哪些能力只是 DESIGNED，哪些已经 IMPLEMENTED，哪些仍然 UNPROVEN？

**结论**：目前"IMPLEMENTED"严格来说只适用于文档制品本身——Phase 1A/1B-0/1B-1 的 Markdown 文件确实存在、内容确实完整、Legacy 模板确实未被破坏。所有机制性能力（对象状态机、Routing、Investigation Bound、Evidence 强制、Human Gate 触发）仍是 `DESIGNED`（有完整设计文本，无强制执行手段）。"这套设计是否真的减少人工工作量、是否能被稳定遵守"仍是 `UNPROVEN`——详见 §A/§B。
**状态**：见下方 §A/§B 分类。
**证据**：见下方 §A/§B。
**缺口**：见下方 §A/§B。

---

## A. 已确认能力（当前工作区有实际文件证据支持）

- 7 Core Objects + 2 fold + 2 demote 的定义与理由完整存在（`protocol.md` §4，`adr.md` ADR-001/002）。
- 8 个对象的完整状态机 + 5 条 Cross-Object Invariants（`state-model.md`）。
- Evidence 5 级信任分层 + `PASS` 判定规则明确定义（`evidence.md` §2）。
- Adaptive Routing 四级分类法 + Complexity 4 tier + 升降级三条件规则（`routing.md` §1-3）。
- Legacy 7 阶段→Protocol 映射表，逐条真实行号引用，原模板文件确认未被修改（`legacy-mapping.md` + `Glob` 事实）。
- Investigation Bound 五信号方案存在，且已有一次真实（非虚构）应用案例可查（`phase-1b-scope.md` §2 + `pilot-walkthrough.md` §1）。
- 至少一次真实（非虚构）端到端 Requirement Intelligence 叙事性执行案例存在，产出 Requirement/Question/Complexity/Routing/Task/Agent Contract 的完整实例（`pilot-walkthrough.md`），即便该 Task 最终停在 `BLOCKED`。
- 一次真实案例显示 Human Gate 未被滥用于可自证事实（`pilot-walkthrough.md` §8）。

## B. 未验证能力（必须真实执行 / Runtime / 真实项目 Pilot 才能证明，本轮不展开）

- Investigation Bound 五信号能否被 agent 稳定、诚实地自我遵守（而非仅此一次被认真执行）。
- Adaptive Routing 短路径（SIMPLE/MODERATE tier）在真实、非虚构任务上从 Requirement 走到 Task `DONE` 的完整案例。
- Evidence trust tier 规则能否防止"agent 把 SELF_REPORT 包装成更高信任等级"（Architecture Attack #4，仍未解决）。
- Task 的 `IN_PROGRESS`/`EVALUATING`/`DONE`/`FAILED`/`RISK_PENDING` 状态从未被真实触发过一次。
- Task 的 Resume 语义（跨 session 接续）完全未定义，也未被验证。
- "using-AI 相比 Legacy 7 阶段真的减少了人工组织开发流程的工作量"——目前只有一个 `OBSERVED CASE`（HANDOFF.md 与实际代码不符被 Agent 发现），已被明确标记为 `UNPROVEN AS SYSTEM CAPABILITY`，不得泛化为系统能力证明。
- Human Gate 在更复杂/多 Requirement 并发场景下是否仍保持克制（当前样本量为 1）。

## C. 最小下一步

1. **新增 `docs/architecture/phase-1b/proposed-changes.md`**：登记本轮发现的建议变更（Task Resume 状态机缺失 — 见 §7；Evidence trust-tier 缺乏防伪造机制的后续设计方向 — 见 §6；Human Gate 无统一查询登记表，是 ADR-002 已知成本的真实体现 — 见 §5）。仅作为待人工确认的提案，不直接修改 `state-model.md`/`protocol.md`/`evidence.md` 任何一份冻结文件。
2. **新增一份 Evidence 自查 Checklist 模板**（建议路径：`docs/architecture/templates/evidence-self-check.md`）：把 `evidence.md` §2 的"`PASS` 需要 ≥`RUNTIME_GENERATED` 证据"规则转化为一份可操作的核对清单，供未来任何 Requirement/Task 在自报完成前逐项自查，直接回应 §6 的缺口，且不修改 `evidence.md` 本身。

第三项评估后认为无必要：`NO FURTHER CHANGE REQUIRED IN THIS STEP`（除上述 2 项外，本轮未发现其他必须在 using-AI 仓内立即处理的文档/Prompt/Template/Checklist/Contract 缺口）。
