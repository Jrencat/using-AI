# 第三阶段：最小研发入口

状态：Codex 自然语言入口和 Claude Code 命令入口均已接入同一规则源。当前环境使用 Codex，Claude Code 暂不可用；Claude 命令实跑、真实业务试点与效率收益均未验证。项目第三阶段与第二阶段内部 Phase 3 无关。

## 启动

**Codex CLI**：在 using-AI 仓库目录启动 Codex，直接输入自然语言需求即可。项目 [AGENTS.md](../../AGENTS.md) 指引读取 [通用规则 develop.md](develop.md)，不使用 Claude 的 `/develop`。新会话会获取项目指引；已有会话可显式要求“按 docs/workflow/develop.md 执行以下需求”。

**Claude Code**：在 using-AI 仓库目录启动 Claude Code，输入：

```text
/develop 你的实际开发需求，可附范围和验收标准
```

也可以直接用自然语言提出开发需求；本仓库的 CLAUDE.md 指引读取同一份通用规则。无参数且没有当前任务时只询问需求，不自动修改仓库。无需填写原模板变量或手选七个阶段。

Claude 入口保留原生项目级 custom slash command：[.claude/commands/develop.md](../../.claude/commands/develop.md)，只传递任务并引用通用文件。`docs/workflow/develop.md` 是行为规则的主要维护源；AGENTS.md / CLAUDE.md 只负责接入。不安装依赖、不启动子 Agent、不创建常驻服务。

## 用在实际代码仓库

1. 将通用文件复制到目标项目的 `docs/workflow/develop.md`；已有同名文件先比较，不覆盖。目标项目决定实际业务规范、测试命令和提交授权。
2. **Codex**：在目标项目 `AGENTS.md` 中追加下面的接入指引，保留原有规则，然后在该项目目录启动新 Codex 会话，直接描述需求。不要复制整个 using-AI 的 AGENTS.md。
3. **Claude Code**：另复制 `.claude/commands/develop.md`，保留相同相对目录，重启后使用 `/develop 实际需求`。需要自然语言入口时，将下面的指引追加到目标项目 CLAUDE.md。不要复制整个 using-AI 的 CLAUDE.md、HANDOFF 或架构历史。

```text
当用户提出开发需求时，读取并遵循 docs/workflow/develop.md，以当前需求为任务。
遵守本项目既有规格和权限；说明、讨论、审查请求按原意处理，不自动进入实现。
```

Codex 安装是一份通用文件加一段 AGENTS.md 指引；Claude 命令安装是通用文件加命令文件。AGENTS.md 是 Codex 项目指引入口，引用的通用文件由 Agent 按指令读取，并非 Codex 自动导入任意 Markdown。本次在已有 Codex 会话中读取并应用通用规则完成入口维护，未启动新会话验证自动发现，也不能当作 Claude Code 调用成功。官方支持方式参见 [OpenAI AGENTS.md 指南](https://developers.openai.com/codex/guides/agents-md/)；本次联网读取该页面受重定向 / 403 限制，未将未读取的页面作为实测证据，入口依据当前会话实际提供的 AGENTS.md 指引。

## 从需求到交付

需求 → 有界定位实现与约束 → 报告级别 / 范围 / 验收 → 最小实现 → 相关检查 → diff、结果与未解决事项。

SIMPLE 用对话中的目标和验收替代额外文档；MODERATE 增加简短方案和相关测试；COMPLEX 明确规格、边界及依赖，按项目约定分批交付；HIGH-RISK 在受影响工作前确认。发现风险可升级，资金、数据安全、权限和不可逆操作不因改动小而降级。已有业务答案不重复询问，已授权工作不反复请求开始。

只读取当前任务相关规范，复用已读上下文；只有新修改、失败或新风险才重复验证。无需默认读取第二阶段 Protocol 或运行旧验证链。完整行为规则见 [develop.md](develop.md)，不在各入口复制。

## 与既有资产的边界

两套七阶段模板保持原样，作为现有用法和成本对照基线；它们的阶段隔离规则仍适用于主动选择模板的任务。新入口是独立候选工作流，不声称实现冻结 Protocol 或提供机器强制执行。

借鉴第二阶段的复杂度词汇、未决需求隔离和人类授权原则，但**低风险任务不再因路由推荐而额外等待人工确认**。这不同于冻结 [routing.md](../architecture/routing.md) 的 Agent-selected 人工确认设计，是第三阶段候选的产品选择；未修改旧规范。若未来要声称兼容该 Protocol，须另行提出兼容性决策，不能借本入口解除冻结。

## 试点与成本

首次代码试点的当前状态见 [pilot-001.md](pilot-001.md)。在真实需求缺失前，不改历史 fixture，不为完成试点制造功能。

轻量记录一行即可：任务 / 起始提交 / 组别 / 模型与工具版本、路由理由、完整任务 Token 及缓存口径、人工介入次数与分钟、重复分析 / 检查、验收结果、7 天返工。未知项明确留空说明；使用量不可读取时不推算降幅。失败、重试及收尾也计入总成本。

后续以第一阶段现有用法（包含其允许的小改动路径）作 A 组，新入口作 B 组；同起点独立副本与会话、相同模型 / 权限 / 验收，避免共享实现结果。本次不启动完整多任务实验。初步目标仍为总 Token 降低至少 20%、至少 2/3 对照任务 Token 更低、人工操作及重复验证减少、同标准质量不明显下降；单次运行或更短的提示词均不能证明收益。完整对照边界继承 [第二阶段收尾计划](../architecture/stage-2-closeout.md)。
