# 通用研发工作流与宿主接入

[develop.md](develop.md) 是开发行为规则的唯一权威源；[Skill 入口](../../skills/develop/SKILL.md) 只负责定位生成的规则副本。安装器负责获取、冲突保护和宿主路径，不定义另一套流程。模型开放，宿主按能力接入，不为每个模型维护规则。

## 接入方式与证据边界

| 层次 | 含义与边界 |
| --- | --- |
| 协议兼容 | 不依赖 GPT、Claude、Gemini、Grok、DeepSeek、MiMo 或其他特定模型；名单开放 |
| 手动可用 | 将规则全文作为提示词或上下文；未证明产品自动加载或完整执行 |
| 已实现适配 | Codex Skill、Claude Code Skill 与本仓库 Claude command 已有入口 |
| 已验证接入 | 必须有真实会话加载和关键工作流执行证据；安装模拟不属于此级别 |
| 不支持或受限 | 缺少项目文件、命令、权限等能力时，只能完成相应部分，需用户补充真实结果 |

2026-10-27 已用 Codex 0.164.0 原生 `skills/list` 验证标准 CLI 安装的项目 Skill 被发现且启用、无解析错误；这不等于新会话 `$develop` 已执行工作流。隔离个人目录的原生发现仍为 UNVERIFIED。固定 CLI、网络安装、更新及卸载证据见 [Skills CLI 验证记录](skills-cli-validation.md)。2026-10-23 尝试以临时工作目录、隔离 `CLAUDE_CONFIG_DIR`、禁用会话持久化，向 Claude Code 非交互会话提供规则全文；CLI 返回退出码 1，提示 `Not logged in /login`。为避免修改真实用户全局配置，未登录或复制凭证，因此未取得真实加载和执行证据。其他具体产品未验证；不能把模型 API 可用或能读 SKILL.md 当作开发执行能力。

## 安装、更新和卸载

新安装统一使用首页的 [npx 安装命令](../../README.md#通过-npx-安装)，由用户在交互中选择 Project 或 Global。查看、更新和卸载按原安装范围执行，命令与共享目录限制见[首页](../../README.md#查看与更新)。标准 CLI 更新可覆盖本地修改，卸载不备份；`check` 是更新别名，不能用于只读预览。`remove --agent codex` 可能保留共享目录却报告成功；要彻底移除所选范围内各宿主的同名 Skill，使用首页不带 `--agent` 的卸载命令，并核对实际目录。

### 旧版安装的维护与迁移

以下保留旧安装器的兼容维护说明，不是另一条新用户安装入口。不要用 npx 直接覆盖旧安装器管理的目录。迁移到 npx 前，先确认项目 / 全局同名入口及本地定制；用原安装器卸载，或将完整旧目录移到技能发现范围之外备份，再按首页安装。仅在 `skills/` 内改名仍可能被发现。不要让两个安装器轮流管理同一目录。

旧 PowerShell 安装器的引导命令保留在此供维护验证使用；下面以 Codex 为目标，维护旧副本时追加 `-Update` 或 `-Uninstall`。命令会以当前用户权限执行 GitHub `main` 上的远程脚本，可先下载审阅；固定版本时须同时固定脚本 URL 和 `-Ref`，仅指定 `-Ref` 不会固定引导脚本。

```powershell
& ([scriptblock]::Create((Invoke-WebRequest -UseBasicParsing -Uri 'https://raw.githubusercontent.com/Jrencat/using-AI/main/scripts/install-develop.ps1' -TimeoutSec 30 -ErrorAction Stop).Content)) -Target codex
```

PowerShell 默认 `-Target manual`，可选 `codex` 或 `claude`，不检测或要求任一 CLI。未知目标在写文件前被拒绝。只为所选目标安装，不自动安装所有工具。Claude 用户目录遵循 `CLAUDE_CONFIG_DIR`，Codex 兼容目录冲突检查仅用于 Codex 目标。

更新和卸载使用相同 `-Target`、`-UserDirectory` 和环境变量。安装器保存提交与逐文件哈希；未知内容、修改、新增文件或链接拒绝替换。旧内容保留在所选根下 `using-ai-backups/`。不自动接管 Python 安装器或其他工具的副本。迁移时先把整个旧目录移出发现范围备份，再安装；手动合并个人定制。下载失败不替换现有包。卸载不删除备份，不改 AGENTS.md、CLAUDE.md 或其他配置。

#### 旧版跨平台与源码副本维护

本小节仅供已有手工或源码安装副本的兼容维护、重建及迁移使用。新用户统一使用首页的 [npx / Skills CLI 安装方式](../../README.md#通过-npx-安装)，不将下述方式作为并列的新安装入口。

PowerShell 卸载也支持无 manifest 的可识别旧版：检查 `SKILL.md` 的 `develop` 名称、规则引用及规则的特征段落后，将整个目录原样移到 `using-ai-backups/` 并报告路径，保留个人文件。安装、更新不接受该识别结果；存在但无效的 manifest 不按旧版处理，链接、异常路径或未知内容拒绝移动。无法识别时请人工审阅并整体移到技能发现目录之外备份。Python 安装器没有自动卸载功能，继续采用本节的人工备份方式，不会因本次修复放宽覆盖限制。

维护既有手工副本时，可从 GitHub 获取 `skills/develop/SKILL.md`、`references/develop.md`、`LICENSE`，保持相对路径，在完整旧目录备份并移出发现范围后重建到原宿主已确认的 skills 目录；通用手动使用只需规则全文。不确定宿主机制时，提供上下文即可，不猜测其专有路径。

已有源码用户维护旧版副本时，可用 Python 3.9+ 标准库核对分发包，并在完整旧目录备份并移出发现范围后按原宿主和范围重建副本，不要求宿主 CLI：

```powershell
python scripts/package_develop.py --check
python scripts/install_develop.py --agent manual --project 'D:\work\my-app'
python scripts/install_develop.py --agent codex --user
python scripts/install_develop.py --agent claude --project 'D:\work\my-app'
```

上述命令应保持旧副本原有的宿主与范围。`--user` 使用当前用户主目录，`--project` 要求现有项目。manual 对应 `.using-ai/workflows/develop`，codex 对应 `.agents/skills/develop`，claude 对应 `.claude/skills/develop`；Claude 用户级支持 `CLAUDE_CONFIG_DIR`。未知宿主拒绝，不退回 Codex。Python 安装拒绝已有同名目录；更新、卸载需先将旧目录整体移出发现范围备份，再安装或保留移出状态，不提供受管理的自动更新。

Skill 格式和目录依据：[Claude Code Skills](https://code.claude.com/docs/en/skills)、[Codex Skills](https://developers.openai.com/codex/skills/)。这些链接是机制参考，不是本次真实会话验证证据。其他宿主只承诺手动提供规则，不宣称其支持相同格式、目录或语法。

## 本仓库入口

AGENTS.md 与 CLAUDE.md 都指向权威规则，直接描述需求即可；Claude 还保留 `.claude/commands/develop.md` 的 `/develop` 薄入口，只传递任务和引用规则。分发 Skill 在其他项目自包含，不依赖本仓库路径。command 与 Skill 是宿主历史入口差异，规则没有分叉；同范围有同名 command 时安装器拒绝新增 Skill，需人工选择迁移。本仓库因此不安装同名 Claude 项目 Skill。

没有原生技能的宿主可直接使用以下提示：

```text
请读取我提供的通用研发规则，并按规则处理以下需求：……
遵守目标项目既有指引、规格和权限；能力不足时明确说明，不把建议当作执行结果。
```

可把规则保存在目标项目的 `docs/workflow/develop.md`，再在宿主实际支持的项目指引中添加引用；已有文件先比较，不覆盖，也不要复制本仓库整份 AGENTS.md / CLAUDE.md。

## 维护与验证

规则只编辑 `docs/workflow/develop.md`，运行 `python scripts/package_develop.py` 生成分发副本和许可证；`--check` 检查逐字节一致性。入口不复制流程。不增加 Runtime、依赖或后台服务。

以下是本工作流与安装分发工具的维护检查，不是普通业务任务的必跑清单。仅修改规则正文时执行打包、同步检查和 `git diff --check`；修改安装器或相关分发逻辑时执行对应安装测试。业务任务的检查范围按[权威规则](develop.md#实现与必要检查)及目标项目明确适用的强制要求选择。

```powershell
python scripts/package_develop.py --check
python scripts/test_install_develop.py -v
powershell -NoProfile -File scripts/test_install_develop.ps1
git diff --check
```

安装测试使用临时目录和模拟下载，验证安装、更新、卸载及冲突保护，不写真实全局配置，也不证明网络安装或真实宿主会话成功。真实业务试点与成本收益仍未验证。

## 从需求到交付

需求 → 有界定位实现与约束 → 报告级别 / 范围 / 验收 → 最小实现 → 相关检查 → diff、结果与未解决事项。

真实业务任务均保留可追溯锚点；SIMPLE 优先复用现有需求单或规格，以极简记录保留目标、结果和验证，不增加独立计划或长报告。MODERATE 增加简短方案和相关测试；COMPLEX 明确规格、边界及依赖，按项目约定分批交付；HIGH-RISK 在受影响工作前确认。跨会话查找及续写、证据分类和反馈规则见[权威规则](develop.md#业务任务追踪)。发现风险可升级，资金、数据安全、权限和不可逆操作不因改动小而降级。已有业务答案不重复询问，已授权工作不反复请求开始。

只读取当前任务相关规范，复用已读上下文及验证证据；失败本身不是重跑理由，重试须满足[权威规则](develop.md#实现与必要检查)的条件，已成功的检查仅因新的相关变化或证据才补充。验证范围、日志成本及临时产物收尾均遵循该规则，不在各入口复制。无需默认读取第二阶段 Protocol 或运行旧验证链。

## 与既有资产的边界

两套七阶段模板保持原样，作为现有用法和成本对照基线；它们的阶段隔离规则仍适用于主动选择模板的任务。新入口是独立候选工作流，不声称实现冻结 Protocol 或提供机器强制执行。

借鉴第二阶段的复杂度词汇、未决需求隔离和人类授权原则，但**低风险任务不再因路由推荐而额外等待人工确认**。这不同于冻结 [routing.md](../architecture/routing.md) 的 Agent-selected 人工确认设计，是第三阶段候选的产品选择；未修改旧规范。若未来要声称兼容该 Protocol，须另行提出兼容性决策，不能借本入口解除冻结。

## 试点与成本

首次代码试点的当前状态见 [pilot-001.md](pilot-001.md)。在真实需求缺失前，不改历史 fixture，不为完成试点制造功能。

轻量记录一行即可：任务 / 起始提交 / 组别 / 模型与工具版本、路由理由、完整任务 Token 及缓存口径、人工介入次数与分钟、重复分析 / 检查、验收结果、7 天返工。未知项明确留空说明；使用量不可读取时不推算降幅。失败、重试及收尾也计入总成本。

后续以第一阶段现有用法（包含其允许的小改动路径）作 A 组，新入口作 B 组；同起点独立副本与会话、相同模型 / 权限 / 验收，避免共享实现结果。本次不启动完整多任务实验。初步目标仍为总 Token 降低至少 20%、至少 2/3 对照任务 Token 更低、人工操作及重复验证减少、同标准质量不明显下降；单次运行或更短的提示词均不能证明收益。完整对照边界继承 [第二阶段收尾计划](../architecture/stage-2-closeout.md)。
