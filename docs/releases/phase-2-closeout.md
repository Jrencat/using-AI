# Phase 2 Closeout — Protocol / Harness Experiment

建议 Tag：`v0.2.0-phase2-closeout`。这是待发布草案；本任务不创建 Tag 或 Release。现有 Tag / 公开 Release 为 `v0.1.0`，发布前再次确认名称未占用及目标收尾提交。

以下为可直接用于 GitHub Release 的说明正文。

---

这是 using-AI **项目第二阶段**（Protocol / Harness 探索，包含内部 Phase 1–5）的阶段性工程实验收尾。第二阶段没有达到预期产品目标：缺少明确、易用的日常开发入口，尚未形成开发者可直接使用的完整研发工作流，也没有充分对照证据证明相较第一阶段能够降低总 Token、减少人工介入并保持交付质量。因此结束原有产品推进路线，保留技术成果，转向第三阶段的实际研发效率。

## 已完成的成果

- 保留第一阶段两套七阶段中文提示模板及填写示例，继续可独立使用，并作为下一阶段对照基线。
- 形成 Protocol、状态模型、证据分层、人工权限边界和按复杂度路由的设计；冻结规范保持不变。
- 内部 Phase 1 的历史结论保留，包括 Phase 1C PASS WITH GAPS 和 Phase 1D INSUFFICIENT — CLOSED。
- 内部 Phase 2 的有限目标已 PASS：Claude Code capture/seal/verify、持久化状态链和假设依赖任务阻断；不代表完整 Harness 或完整研发交付流程。
- 内部 Phase 3 PASS，信任标签为 SAME_FAMILY_REVIEW：隔离上下文 validator 在 18 个预注册案例上与 Expected 一致，并记录旧 verifier 的 D1–D4 差异；不声称 INDEPENDENT_VERIFICATION。
- C1 Scope Conformance 工具、manifest / anchor、fixture 及 Codex receipt 离线适配器成为可按需复用的工程资产。

## Phase 4 / Phase 5 的实际状态

- **Phase 4 未正式关闭。** C1 Gate 为有限范围 PASS：Corpus v3 143/143、一次 FX-ELIGIBLE Live Run Checker PASS、有限范围人工抽查。FX-BLOCKED 真实运行、重复运行、真实 symlink/junction、其他 Agent / 启动模式和 Independent Verification 未完成；不将单次 C1 成功等同于整个 Phase 4 完成。
- **Phase 5 未完成。** P5-1、P5-1.1 为 ACCEPTED — OFFLINE SCOPE；mapping v1 默认、v2 opt-in。P5-2 一次真实 Codex 尝试以 **INSUFFICIENT — CLOSED** 收口：receipt 转换 COMPLETE、0 gaps，事后 capture-only 封存成功，但无运行前 baseline / anchor A / Task events，Checker 未运行。Codex 写入失败原因未知，最终代码由操作者修改，不能算 Codex 交付成功。
- 适配产物保持 TOOL_GENERATED。P5-3 / P5-4 未授权、未开始；不声称非 Claude 路径端到端 PASS 或模型无关能力已获证明。

## 未实现的产品目标

手工 baseline、anchors、状态事件和封存操作仍增加使用门槛；现有局部工程验证不足以构成低摩擦日常入口。尚无同类真实任务的第一阶段对照数据支持 Token / 人工成本收益；也不将“可能增加负担”写成已证明的成本上升。技术实验有可复用价值，产品目标未达成的结论与局部 Gate PASS 并不冲突。

## 第三阶段方向

先建立 Claude Code 可用的明确入口与最小工作流，从真实研发任务开始，按复杂度和风险选择必要步骤，减少重复上下文和无效验证。GPT-6 / Codex CLI 不可用时，优先完成 Claude Code 可执行的工作。

以第一阶段模板为基线，对小型可逆修改、已有行为 bug、跨模块功能至少 3 个真实任务做同条件成对比较，统计完整任务的总 Token（含重试与缓存输入）、人工介入、重复验证和交付质量。试点目标：至少 2/3 任务 Token 更低、三对总量降低至少 20%，累计人工操作和重复验证下降，同时通过相同验收 / 回归，无新增 BLOCKER / MAJOR 或越权改动，并观察 7 天返工。缺同口径数据时不宣布收益。

不预设 CLI、MCP、SDK、Runtime 或 Orchestrator；仅在实际需求与证据支持时考虑。Phase 4 / 5 不再是默认下一步；历史结论、锁定资产及冻结规范不改写。

完整决策、资产边界及评估方案见 [项目第二阶段收尾记录](../architecture/stage-2-closeout.md)，当前交接见 [HANDOFF](../../HANDOFF.md)。
