# 第三阶段：最小研发入口

状态：Codex 自然语言入口和 Claude Code 命令入口均已接入同一规则源，另提供自包含的标准 Skill 分发包。当前会话使用 Codex；本机已检测到 Claude Code，Skill 新会话调用、真实业务试点与效率收益仍未验证。项目第三阶段与第二阶段内部 Phase 3 无关。

## 启动

**Codex CLI**：在 using-AI 仓库目录启动 Codex，直接输入自然语言需求即可。项目 [AGENTS.md](../../AGENTS.md) 指引读取 [通用规则 develop.md](develop.md)，不使用 Claude 的 `/develop`。新会话会获取项目指引；已有会话可显式要求“按 docs/workflow/develop.md 执行以下需求”。

**Claude Code**：在 using-AI 仓库目录启动 Claude Code，输入：

```text
/develop 你的实际开发需求，可附范围和验收标准
```

也可以直接用自然语言提出开发需求；本仓库的 CLAUDE.md 指引读取同一份通用规则。无参数且没有当前任务时只询问需求，不自动修改仓库。无需填写原模板变量或手选七个阶段。

Claude 入口保留原生项目级 custom slash command：[.claude/commands/develop.md](../../.claude/commands/develop.md)，只传递任务并引用通用文件。`docs/workflow/develop.md` 是行为规则的主要维护源；AGENTS.md / CLAUDE.md 只负责接入。不安装依赖、不启动子 Agent、不创建常驻服务。

## 安装标准 Skill

**普通 Codex 用户**：优先使用根目录 [README 的快速安装、更新与卸载命令](../../README.md)，无需克隆或运行 Python。`scripts/install-develop.ps1` 使用系统 PowerShell 和 HTTPS，解析 GitHub ref 为提交后只下载三个 Skill 文件；校验后再安装。来源及文件哈希保存在 Skill 内的 `.using-ai-install.json`，更新 / 卸载只接受本安装器管理且未修改的目录，旧版移到 `~/.agents/using-ai-backups/`。不修改项目规则或 Codex 配置；检查兼容用户目录中的同名冲突，但不扫描每个业务项目。

以下 Python 命令面向**维护者、已有源码用户或 Claude / 项目级安装**，不是普通用户的安装前置条件。PowerShell 入口与内置 skill-installer、旧 Python 安装器产生的安装不自动互相接管；迁移时先将旧目录整体备份到 skills 扫描范围外。

维护分发时，先通过打包一致性检查及 `powershell -NoProfile -File scripts/test_install_develop.ps1` 的隔离安装检查，再按项目授权发布源码。README 的远程命令只有在对应 ref 已包含 `scripts/install-develop.ps1` 时才可用；本地文件修改不代表远端已发布。测试脚本只模拟网络并写隔离临时目录，不证明目标环境的联网安装或 Codex 新会话发现成功。

分发目录为 `skills/develop/`，包含标准 `SKILL.md`、完整的 `references/develop.md` 和 MIT `LICENSE`。安装后不依赖 using-AI 的路径。规则仍只编辑 `docs/workflow/develop.md`，运行 `python scripts/package_develop.py` 生成分发副本；`python scripts/package_develop.py --check` 必须通过。不要直接编辑生成副本。

| Agent | 用户级目录 | 项目级目录 | 显式调用 |
| --- | --- | --- | --- |
| Codex CLI | `~/.agents/skills/develop/` | `<项目>/.agents/skills/develop/` | `$develop 需求` |
| Claude Code | `~/.claude/skills/develop/` | `<项目>/.claude/skills/develop/` | `/develop 需求` |

`~` 由 Python `Path.home()` 按当前用户环境解析，不硬编码用户名、盘符。Claude 用户级目录设置了 `CLAUDE_CONFIG_DIR` 时使用该目录下的 `skills/develop/`。Codex 还兼容 `$CODEX_HOME/skills`（未设置时通常为 `~/.codex/skills`）；本地安装脚本统一选择跨 Agent 标准的 `.agents/skills`，不同时安装两份。Skill 自动匹配由 Agent 决定；显式调用更易核对。安装后启动新会话，确认 Skill 已发现。

先克隆本仓库，或下载 GitHub 源码归档并解压，在 using-AI 根目录运行（需要 Python 3.9+，仅标准库）：

```powershell
git clone https://github.com/Jrencat/using-AI.git
cd using-AI
python scripts/package_develop.py --check
# 用户级：二选一
python scripts/install_develop.py --agent codex --user
python scripts/install_develop.py --agent claude --user
# 项目级：替换为已有业务仓库的实际路径
python scripts/install_develop.py --agent codex --project 'D:\work\my-app'
python scripts/install_develop.py --agent claude --project 'D:\work\my-app'
```

安装器不会修改 AGENTS.md / CLAUDE.md 或安装旧 command；已有目标目录时失败且保留原内容，重复执行不会追加配置。同范围存在 `.claude/commands/develop.md` 时拒绝安装同名 Skill，先人工确认如何迁移。其他范围也不要保留同名入口，避免优先级遮蔽。本仓库保留原 command，因此不要在本仓库安装同名 Claude 项目 Skill。

**复用现有安装工具**：Codex 的内置 `$skill-installer` 可安装 GitHub 子目录。向其提出“从 Jrencat/using-AI 的 skills/develop 安装 Skill”，或使用其 `install-skill-from-github.py --repo Jrencat/using-AI --path skills/develop --ref <已审核提交> --dest <目标skills父目录>`。脚本位置随安装而异，不硬编码本机路径。已检查该工具支持 `--dest` 且目标存在时拒绝覆盖；它不负责更新、卸载或 Claude 同名 command 检查。只有 Codex 环境才保证提供该工具；本地小脚本补足独立 Claude 环境和范围选择，不引入完整 CLI 或第三方依赖。

**更新**：在源码目录 `git pull --ff-only`，运行打包检查；查看新旧 Skill 差异，将目标 `develop` 目录整体移到 skills 扫描目录之外的备份位置（包括个人定制），再执行原安装命令。确认新会话能调用后，按需手工合并定制。更新失败时移走未完成的新目录，再将备份放回原处。不要强制覆盖，不自动删除备份。正式团队分发建议固定已审核的 commit；目前沿用 GitHub 源码分发，没有新增自动发布服务。

**卸载**：确认目标绝对路径和内容后，将相应 `develop` 目录移到 skills 扫描目录之外；需要彻底删除时自行清理该备份。新会话确认已不再发现此 Skill。项目级目录如已提交，按业务仓库流程提交移除。无需清理 AGENTS.md / CLAUDE.md，因为安装器从未修改它们。源码安装中断可能留下部分目录，检查后同样先移出备份再重试。

官方依据：[Claude Skills](https://code.claude.com/docs/en/skills) 已读取，确认标准格式、两级目录、`/skill-name` 和旧 commands 兼容性。[Codex Skills](https://developers.openai.com/codex/skills/) 本次访问受 308 / Forbidden 限制；Codex 的 `SKILL.md`、`$name`、`.agents/skills` 与兼容 `.codex/skills` 另结合当前会话的 Skill 目录和内置 skill-creator / skill-installer 指引核对，不能视为本次成功读取官方网页。

验证边界：本机检测到 Codex CLI 0.163.0 与 Claude Code 2.1.293。可执行文件存在及版本输出不证明 Skill 调用成功；两种 Agent 的新会话发现、真实任务调用与真实用户级安装均待验证。仅在隔离临时目录验证安装行为，不向真实用户配置写入。真实业务试点和效率收益仍未验证。

## 旧版手工接入（继续兼容）

1. 将通用文件复制到目标项目的 `docs/workflow/develop.md`；已有同名文件先比较，不覆盖。目标项目决定实际业务规范、测试命令和提交授权。
2. **Codex**：在目标项目 `AGENTS.md` 中追加下面的接入指引，保留原有规则，然后在该项目目录启动新 Codex 会话，直接描述需求。不要复制整个 using-AI 的 AGENTS.md。
3. **Claude Code**：另复制 `.claude/commands/develop.md`，保留相同相对目录，重启后使用 `/develop 实际需求`。需要自然语言入口时，将下面的指引追加到目标项目 CLAUDE.md。不要复制整个 using-AI 的 CLAUDE.md、HANDOFF 或架构历史。

```text
当用户提出开发需求时，读取并遵循 docs/workflow/develop.md，以当前需求为任务。
遵守本项目既有规格和权限；说明、讨论、审查请求按原意处理，不自动进入实现。
```

旧版 Codex 接入是一份通用文件加一段 AGENTS.md 指引；Claude 命令接入是通用文件加命令文件。AGENTS.md 是 Codex 项目指引入口，引用的通用文件由 Agent 按指令读取，并非 Codex 自动导入任意 Markdown。此前在已有 Codex 会话中读取并应用通用规则完成入口维护，未启动新会话验证自动发现，也不能当作 Claude Code 调用成功。官方支持方式参见 [OpenAI AGENTS.md 指南](https://developers.openai.com/codex/guides/agents-md/)；此前联网读取该页面受重定向 / 403 限制，未将未读取的页面作为实测证据，入口依据会话实际提供的 AGENTS.md 指引。

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
