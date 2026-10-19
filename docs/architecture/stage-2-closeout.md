# Phase 2 Closeout — Protocol / Harness Experiment

日期：2026-10-19。性质：项目第二阶段的产品方向收尾与第三阶段交接基线。

## 1. 决策与命名边界

项目第一阶段是根目录两套七阶段研发流水线提示模板；项目第二阶段是 Protocol / Harness 探索，包含内部 Phase 1–5；项目第三阶段将以实际研发效率为目标。本文件使用“项目第二阶段 / 第三阶段”区分产品阶段与内部 Phase 编号。

**第二阶段原有产品推进路线至此结束：这是一次未达到预期产品目标的工程实验收尾。** 不再以完成内部 Phase 4、Phase 5 或增加验证器作为默认路线。此决策来自本次用户的方向调整指令，不是新的技术 Gate，也不把未完成的 Phase 改判为 PASS / CLOSED。

内部 [Phase 2 Closeout](phase-2/phase-2-closeout.md) 的 Harness 局部验证 PASS 保持原义；内部 [Phase 3 Closeout](phase-3/phase-3-closeout.md) 也不是项目第三阶段的完成记录。历史文档中的“下一步”“未开始”和提交状态均按其记录时点理解；当前产品方向以本文件及 [HANDOFF](../../HANDOFF.md) 为准。

## 2. 原定目标及证据口径

第二阶段探索模型无关的研发协议：定义需求、假设、规格、任务、证据及人工权限边界，通过 Harness 组织执行、记录状态、约束未确认需求，并验证执行记录。设计依据：[Protocol](protocol.md)、[State Model](state-model.md)、[Evidence](evidence.md)、[Routing](routing.md)、[ADRs](adr/adr.md)。这些是设计及局部实现的依据，不等于日常研发产品已经交付。

本次区分四类陈述：

- **已证实的事实**：当前仓库文件及已接受阶段记录所载结果，引用其范围和限制；本次没有重跑历史实验或重新计算历史证据。
- **基于证据的判断**：由局部成果、使用障碍及缺失的对照数据形成的产品判断，不扩大历史 Gate 的含义。
- **尚未验证的假设**：需要第三阶段真实任务检验的收益或原因推测。
- **第三阶段计划**：下一阶段拟执行的工作与验收标准，尚无执行结果。

## 3. 已完成的工程探索与历史状态（事实，按记录限定）

| 内部阶段 | 已有结果及来源 | 必须保留的边界 |
| --- | --- | --- |
| Phase 1 | [1B 状态记录](phase-1b/using-ai-status-review.md)；[1C 收尾](phase-1c/phase-1c-closeout.md) 为 PASS WITH GAPS，Protocol 冻结；[1D 收尾](phase-1d/phase-1d-closeout.md) 为 INSUFFICIENT — CLOSED。HANDOFF 汇总 Phase 1 为 PASS / CLOSED，1A、1B COMPLETE | 汇总不抹去 1D 的不足或历史证据矛盾；不重开 A–O、P-D 或创建 P-D-05。1C 的跨 Agent 静态解释结论不提升后续执行证据的信任等级 |
| Phase 2 | [收尾](phase-2/phase-2-closeout.md)：2.1 / 2.2 PASS；真实 Claude Code capture/seal/verify、append-only 状态事件、Question→Assumption→Task 阻断链；记录 27 + 8 项测试 | 单一状态链、有限真实运行、hash 封存而非签名；不代表完整 Harness 或完整研发交付工作流 |
| Phase 3 | [收尾](phase-3/phase-3-closeout.md)：PASS，SAME_FAMILY_REVIEW；独立上下文 validator 在 18 个预注册案例上与 Expected 一致；旧 verifier 10/18，8 处分歧归为 D1–D4 | 不是 INDEPENDENT_VERIFICATION，不证明 Contract 完备；旧 verifier 未修复，Contract v2 的 5 个候选缺口延期 |
| Phase 4 | [C1 收尾](phase-4/phase-4-closeout.md)：Corpus v3 143/143；一次 FX-ELIGIBLE Live Run Checker PASS；人工抽查 ACCEPTED WITH BOUNDED SCOPE；C1 Gate PASS，bounded | 整个 Phase 4 **未正式关闭**（HANDOFF H3）；同作者结果，非独立验证；详见下一节 |
| Phase 5 | [P5-1](phase-5/p5-1-closeout.md) / [P5-1.1](phase-5/p5-1-1-closeout.md)：ACCEPTED — OFFLINE SCOPE；Codex receipt adapter、版本化 mapping、预注册负例及 provenance；[P5-2](phase-5/p5-2-closeout.md)：INSUFFICIENT — CLOSED | 整个 Phase 5 未完成；没有非 Claude 路径的 Checker PASS；模型无关端到端能力未获证明 |

工程资产包括 `harness/` 的状态 CLI 和封存工具、`phase-3-validation/` 的差分驱动及结果、`phase-4-validation/` 的 manifest / anchor / scope checker 和 fixture、`phase-5-validation/codex_receipt/` 的离线适配器。Phase 3 的 standalone validator、部分原始包及真实运行材料位于仓库外或 gitignored 目录；引用路径不保证下一会话能够取得它们，不把仓库当成完整可重放证据包。

## 4. Phase 4 / Phase 5 未完成与未验证事项（事实）

Phase 4 保留 C1 的有限范围成功和 H3“整体未正式关闭”的裁决。未做：FX-BLOCKED 真实运行、重复运行、其他 Agent / 启动模式、真实文件系统 symlink/junction 行为、Independent Verification。人工抽查未逐字节比较内容，未单独检查 Edit tool-result。Contract §14 的 required-item 歧义、预条件失败后的 skip-rule 规范不足和 detection-only 盲区仍保留；本次不修改 Contract、Corpus 或冻结 Protocol。

Phase 5 的 v1 默认、v2 显式 opt-in 及锁定文件保留。P5-2 的一次真实 session 经 v2 转换 COMPLETE、0 gaps，Harness 在运行后 capture-only 封存成功；但缺少运行前 baseline、anchor A、任务事件，Checker 未运行。Codex 写入失败原因 UNKNOWN，最终代码由操作者修改，不能作为 Codex 成功证据。H1 已裁决适配产物保持 TOOL_GENERATED，不是 RUNTIME_GENERATED。跨版本适配、真实 Codex 完成任务及 C1 全链成功均未验证；`compacted`、未配对调用继续 fail-closed。

P5-3 / P5-4 未授权、未开始。H2（另一次 P5-2 与额度）、H4（P5-3 / P5-4）保留为历史待决事项，因本次产品路线结束而不再驱动下一项工作；不隐含新授权。停止推进不等于将未测事项判失败，也不等于补齐了它们。

## 5. 未达到的产品目标与停止理由

**事实依据**：[ADOPTION](ADOPTION.md) 记录操作者需手工建立 baseline、anchors、Task events，缺少直接在用户仓库上运行 Checker 的封装入口；[Harness README](../../harness/README.md) 需要显式绑定 session 和封存边界；现有完成记录集中在状态链、证据、checker 和适配器。尚未形成开发者可直接从真实需求走到合格交付的完整日常工作流。Routing 有短路径设计，但没有交付可自动执行的系统路由。

**产品判断**：这些局部验证不能支撑第二阶段已经实现易用入口或完整工作流的产品主张。当前记录没有足够的第一阶段对照数据，无法证明总 Token、人工介入下降且质量保持。继续按原路线补验证，很可能继续推迟对真实研发收益的检验；因此停止原有产品推进路线，保留资产并改变下一阶段的验收对象。

**未验证假设**：重复加载规则、封存准备、复核与修复验证链可能增加 Token 和人工成本；选择性加载和按风险裁剪流程可能降低成本。两者都缺少同类真实任务的对照，不能写成“已证明第二阶段更贵”或“第三阶段一定更省”。

## 6. 技术资产处置建议（后续按需采用）

| 资产 | 建议 | 适用边界 |
| --- | --- | --- |
| 两套七阶段模板及示例 | 保留并作为对照基线 | 本次不改模板、变量、阶段或全局强制规则；第三阶段候选流程另行设计 |
| Question / Assumption 隔离、人工权限、Claim 与 Evidence 区分 | 复用必要原则 | 按真实任务需要引用最小规则，不要求每次加载全部架构文档 |
| Routing 四级复杂度与升降级依据 | 改造成可用入口中的简短任务分流说明 | 仍属计划；不得宣称现有系统自动强制执行。与冻结规范发生冲突时先记录问题、影响和待决策项 |
| Harness、C1 checker、manifest / anchor | 保留为可选专项工具 | 仅在风险和证据需求值得其成本时使用，不作为日常任务默认前置条件；旧 verifier 的已知 D1–D4 不忽略 |
| Codex receipt adapter、mapping、负例、provenance | 保留版本及锁定记录，按需参考适配方法 | 离线范围和单 session 观察不提升为普遍兼容；当前无需继续 Codex 运行 |
| Contract v2、独立验证、FX-BLOCKED / repeat / symlink 扩展、store / signing / Resolver | 暂时搁置 | 不是第三阶段 backlog 的默认承诺；有具体产品需求及证据后再决策 |

## 7. 第三阶段目标、范围与成功标准（计划）

目标：让开发者从真实研发任务开始，用一个明确入口选择必要流程，完成修改、适量验证和交付，并测量相对第一阶段的收益。先交付 Claude Code 可使用的入口文档 / 提示词及最小工作流；GPT-6 / Codex CLI 当前不可用时，优先安排 Claude Code 可完成的工作，不等待跨模型验证。

不预设 CLI、MCP、SDK、Runtime、Orchestrator 或新基础设施。产品范围不包括补完旧 Phase 4 / 5、增加通用验证器或解冻 Protocol。若未来设计确实与冻结规范冲突，先提出原因、具体条款、影响及待决策项，不能自行解除冻结。

| 维度 | 最小成功标准（未来试点的验收约定，尚未达成） |
| --- | --- |
| 低摩擦入口 | 一份稳定入口能说明输入、启动方式和完成条件；新会话只需任务描述、仓库位置及必要约束，最多一次启动提示，无需人工选择多个阶段或配置验证链 |
| 真实交付 | 至少 3 个有实际使用需求的任务，各自从任务描述完成到可审查 diff、相关验证结果和交接；fixture 或仅文档化设计不计真实开发完成 |
| 适应复杂度 / 风险 | 样本覆盖小型可逆修改、已有行为 bug、跨模块功能；每项记录选择了哪些必要步骤及理由，发现数据 / 权限 / 不可逆风险时升级确认 |
| 人工与验证成本 | 与基线成对比较，累计人工介入次数、主动操作分钟数及无新增信息的重复验证次数均下降；业务决策和高风险授权保留，不以跳过它们凑降幅 |
| 总 Token | 同口径累计 input + output（含重试、重复上下文、缓存输入和收尾），至少 2/3 任务更低，三对任务总量至少降低 20%；这是试点目标，不是已证实收益 |
| 质量 | 每对采用同一预定验收、相关回归和 diff review；无新增 BLOCKER / MAJOR、越权实现或范围外改动；完成后观察 7 天的返工与缺陷，不能用明显质量下降换成本收益 |

## 8. 最小对照评估（计划，不在本次执行）

1. 先从真实项目待办挑选上述 3 类任务，固定起始 commit、需求、验收和相关回归；指定检查者，先冻结验收再看候选结果。首个任务选择小型可逆、无接口 / schema / 权限变化的实际修改；没有合适任务时先选任务，不用合成 fixture 替代。
2. A 组使用当前第一阶段 Claude 模板的现有用法，包括 README 已允许的小改动路径；B 组使用第三阶段候选入口。两组使用独立同起点副本和新会话、相同 Claude Code / 模型版本、工具权限、上下文资料及 Token 统计口径；同一任务不共享生成结果。交替 A/B 执行顺序，记录可能的操作者学习效应。复杂或风险任务保留基线要求的人工 Gate。
3. 每次只记录一行轻量数据：任务 / 起点 / 组别 / 模型版本、路由理由、总 input/output Token 与缓存口径、耗时、人工介入次数及分钟、验证与重复次数、验收 / 回归结果、7 天返工。记录失败、中断、重试和人工补写，全部计入本任务成本，不能只比较成功尾段。质量检查者按同一验收检查两组 diff，尽可能隐藏组别。
4. 优先用工具可得用量；缺任一组同口径总 Token，标注不可比较，不从费用或耗时反推已证实的 Token 降幅。用量收集不引入新 runtime 或通用证据系统。
5. 汇总成对差值及三对总量，按第 7 节验收。样本仅支持有限试点结论；未达标则记录具体瓶颈并缩小或调整候选，不通过增加验证层追求表面完整。只在新证据需要时扩样，不在本次收尾运行完整套件。

## 9. 交接与版本基线

检查时：`main` / HEAD `3c84e5b18d5fcdedda8c893ff2f6e3bf643229a0`；`git fetch origin` 后与 `origin/main` 相等，暂存区为空；仅有用户已有未跟踪 `.claude/`，保留且不提交。现有本地 Tag `v0.1.0`；GitHub 公开 Releases 页面列有 `v0.1.0`（API 限流，`gh` 未安装，改查公开页面；不声明已检查私有草稿）。

建议 Tag `v0.2.0-phase2-closeout`，建议标题及完整说明见 [Release 草案](../releases/phase-2-closeout.md)。本任务仅准备草案与收尾提交，不创建 Tag、不发布 Release；拟发布目标应为包含本文件的最终收尾提交，发布前重新核对远程与 Tag 冲突。

下一工程任务：设计第三阶段的 Claude Code 单入口与最小工作流，先选定第一个真实小改动及验收，再完成可直接启动的提示词和一次实际交付；逐步补齐另外两类对照样本。交付物应包含流程选择、必要上下文、停止条件和轻量用量记录，不是新的验证器。
