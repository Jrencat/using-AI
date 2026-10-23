# using-AI：安装 `$develop`，在自己的项目中开始开发

`$develop` 帮助 Codex 理解需求、按需多轮澄清、实现代码、执行必要验证并交付。简单需求直接执行；关键业务歧义未解决时先提问。无需了解本仓库的协议或七阶段模板。

## 快速安装（Codex / Windows）

先安装并配置好 Codex CLI，确保 `codex` 命令可用。在 **PowerShell 5.1 或更新版本**运行：

```powershell
& ([scriptblock]::Create((Invoke-RestMethod 'https://raw.githubusercontent.com/Jrencat/using-AI/main/scripts/install-develop.ps1')))
```

无需克隆仓库、Python、Git 或管理员权限。安装器只从 GitHub 下载 `skills/develop/` 的三个必需文件，安装到当前用户的 `~/.agents/skills/develop/`，并检查文件、入口引用和哈希。不会修改 Codex 配置或项目指引；同名未知来源或被修改的 Skill 会使安装停止。此命令执行本仓库 `main` 上的脚本；团队固定版本时，将命令中的 `main` 换成已审核提交，并在末尾加 `-Ref <同一提交>`。

### 开始使用

在自己的项目中启动新的 Codex 会话，输入：

```text
$develop 帮我实现某项需求
```

用户级安装可供其他项目使用，无需在每个项目复制规则。项目自己的 AGENTS.md、规格和授权仍然适用。若未发现 Skill，启动新会话并检查下方常见问题；文件安装检查不等于已验证 Codex 新会话发现。

### 更新

```powershell
& ([scriptblock]::Create((Invoke-RestMethod 'https://raw.githubusercontent.com/Jrencat/using-AI/main/scripts/install-develop.ps1'))) -Update
```

更新只替换本安装器管理的 `develop` Skill，先检查本地文件是否被修改，再下载同一 GitHub 提交下的完整包；旧版保留在 `~/.agents/using-ai-backups/`，不参与 Skill 发现。同版本不替换，重复安装提示使用更新命令。未知来源、个人定制或新增文件不会被静默覆盖：先将整个旧目录移到 skills 扫描目录之外备份，再重新安装；按需合并定制。更新后启动新会话。

### 卸载

```powershell
& ([scriptblock]::Create((Invoke-RestMethod 'https://raw.githubusercontent.com/Jrencat/using-AI/main/scripts/install-develop.ps1'))) -Uninstall
```

将受管理且未修改的 Skill 移到上述备份目录，不删除配置或备份。离线或已有个人修改时，也可手动将 `~/.agents/skills/develop/` 移到 skills 扫描目录之外，再启动新会话。

### 常见安装问题

| 情况 | 处理方式 |
| --- | --- |
| 找不到 `codex` | 先完成 Codex CLI 安装，确认命令在 PATH 中，重新打开 PowerShell |
| 下载失败、403、404、超时 | 检查 GitHub API 和 raw.githubusercontent.com 的网络 / 代理、API 限流及所选 ref；重试。首次下载脚本失败时安装器尚未运行 |
| 同名 Skill、未知来源或本地修改 | 按报错路径将旧目录移出所有 skills 扫描目录备份，再安装；不直接覆盖 |
| 权限不足或安装锁残留 | 检查报错目录权限；确认没有安装进程后才移除报错中的锁文件，不用管理员权限强行覆盖 |
| 安装成功但未发现 / 仍用旧规则 | 启动新会话；检查项目级 `.agents/skills/develop`、兼容目录 `~/.codex/skills/develop` 或 `$CODEX_HOME/skills/develop` 是否有另一份；也检查 Codex 是否禁用了该 Skill |
| macOS / Linux 或希望在 Codex 内安装 | 使用下方内置安装器请求；它需要 Python，不提供本脚本的受管理更新功能 |

```text
$skill-installer 从 https://github.com/Jrencat/using-AI/tree/main/skills/develop 安装 develop Skill
```

内置安装器可直接获取 GitHub 子目录，无需手动克隆，但目标已存在时会拒绝安装；使用它安装的副本需先移出扫描目录备份，再重新安装以更新。Claude、项目级安装、离线源码安装及维护者打包方式见[详细安装说明](./docs/workflow/README.md)。新会话发现及跨项目调用仍需在目标 Codex 环境确认，不以文件检查代替实际调用。

---

## 原有七阶段模板

一套面向 **规格驱动开发（Spec-Driven Development）** 的中文提示词模板，把「需求 → 交付」拆成 7 个互相隔离的阶段，每个阶段都有明确的输入、输出、禁止项和人工卡点。

核心特点是一条贯穿全流程的 **风险隔离主线**：需求里没确认的东西，绝不会悄悄变成代码。

- 📄 [`claude研发流水线提示词模板.md`](./claude研发流水线提示词模板.md) — Claude Code / Claude 网页版（可用 `/opsx:*` 等 slash command）
- 📄 [`codex研发流水线提示词模板.md`](./codex研发流水线提示词模板.md) — Codex 及其他通用编码 Agent（全程自然语言，不依赖 slash command）
- 📝 [`examples/填写示例.md`](./examples/填写示例.md) — 一份填好变量的完整样例

两份文件内容一一对应，只在「是否使用 slash command」上有差异，可按你的工具链任选其一。

> 本仓库还包含 Agent-Native Protocol / Harness 的设计与有限范围验证。想知道现在能用什么、不能用什么：见 [`docs/architecture/ADOPTION.md`](./docs/architecture/ADOPTION.md)。
> 项目第二阶段（Protocol / Harness 探索，含内部 Phase 1–5）的原有产品推进路线已收尾；局部工程成果保留，不代表完整研发工作流或成本收益已获证明。见[第二阶段收尾记录](./docs/architecture/stage-2-closeout.md)与[当前交接](./HANDOFF.md)。第三阶段将转向明确入口、按任务选流程及真实研发效率，以本页两套模板为对照基线。

---

## 第三阶段：直接开始开发

在本仓库目录启动 **Codex CLI，直接自然语言描述开发需求**；[AGENTS.md](./AGENTS.md) 指引接入[通用工作流](./docs/workflow/develop.md)。Claude Code 保留 `/develop 你的开发需求` 及自然语言入口，引用同一规则源。AI 按复杂度与风险选择必要流程，实施最小修改、执行相关检查并交付；简单任务不要求手选七个阶段。

在任意业务仓库中使用时，推荐安装标准 [develop Skill](./skills/develop/SKILL.md)：支持用户级或项目级安装，Codex 用 `$develop 需求`，Claude Code 用 `/develop 需求`。完整步骤与更新、卸载策略见[启动与安装方法](./docs/workflow/README.md)。保留旧版手工接入方式。Agent 新会话发现、实际调用和真实业务试点待验证，成本收益尚不可比较；[首次试点记录](./docs/workflow/pilot-001.md)保留原有试点记录。以下七阶段模板保持原样，继续作为独立方案与对照基线。

## 解决什么问题

用 AI 做需求到代码的全流程，最常见的三类翻车：

| 问题 | 本模板的应对 |
|------|-------------|
| AI 把没定的需求「自行脑补」成代码，后期返工 | 未确认问题降级为假设 → 熔断不拆任务 → 实现阶段强制阻断 |
| 一次对话干完 7 件事，中途跑偏无从追溯 | 每阶段单独 Prompt，严禁越界，产出物人工 Review 后才进入下一阶段 |
| 多轮迭代时 AI 覆盖掉历史 QA / 已确认结论 | 问题 ID 永不复用，增量维护，`✅ 已关闭` 的结论强制继承 |

---

## 七个阶段

| 阶段 | 角色 | 产出物 | 人工卡点 |
|------|------|--------|---------|
| 1 | 需求分析 & QA 生成 | `产品需求问题.md` / `技术问题.md` | 人工逐条关闭或追问 |
| 2 | Spec 设计 + 自我审查 | 唯一真相源 `Spec`、`spec-review.md` | Review 数据结构与接口 |
| 3 | OpenSpec Change 初始化 | `proposal.md` / `design.md` / `specs/**` | Review 提案与设计 |
| 4 | Tasks 拆解 | `tasks.md` | Review 任务与 Scope |
| 5 | 代码实现 | 代码（逐个 task） | 高风险任务需显式授权 |
| 6 | 测试生成 + 自愈闭环 | `test_cases.md` + 修复记录 | Review 用例后再自动推演 |
| 7 | 最终审计 + 归档 | `final-validation.md` | 结论为 ❌ 时拒绝归档 |

### 风险隔离主线

```
阶段1  问题未关闭（❌ 待确认 / 🔄 追问中）
  ↓
阶段2  降级为 ASSUM-XXX，隔离进 Spec 第9章（不进正文）
  ↓
阶段3  隔离进 proposal / design 的【未决风险与假设跟踪】章节
  ↓
阶段4  绝对熔断不拆任务；弱相关任务降级 P2 并标注 ASSUM
  ↓
阶段5  命中 P2 或 ASSUM 依赖 → 强制阻断，等待人工授权
  ↓
阶段6  相关用例标记 ⚠️ 风险挂起，禁止靠"自愈"发明业务逻辑
  ↓
阶段7  登记为【已知未决技术债】，合规隔离即可归档
```

**一句话**：不确定的需求会一路被标记、降级、熔断、阻断，最终以技术债的形式显式交付，而不是被 AI 猜着写进代码里。

---

## 怎么用

### 1. 复制模板

按你使用的工具，取 `claude研发流水线提示词模板.md` 或 `codex研发流水线提示词模板.md`。

### 2. 替换变量

每份文件顶部都有完整变量表，最少需要替换这几个：

| 变量 | 含义 | 示例 |
|------|------|------|
| `{{PROJECT}}` | 项目 / 系统名称 | 示例系统 |
| `{{MODULE}}` | 模块中文名 | 订单管理 |
| `{{MODULE_SLUG}}` | 模块英文短名 | order-management |
| `{{VERSION}}` | 迭代版本号 | v1 |
| `{{REQ_DOCS}}` | 原始需求文档路径 | docs/需求/order-management/需求说明.md |
| `{{DESIGN_DOCS}}` | 设计稿 / 原型路径（可选） | docs/design/order-management.html |
| `{{QA_DIR}}` | QA 看板目录 | docs/qa/order-management/v1 |
| `{{SPEC_FILE}}` | 唯一真相源 Spec | specs/order-management-v1.md |
| `{{REVIEW_DIR}}` | 审查报告目录 | docs/review |
| `{{CHANGE_NAME}}` | OpenSpec Change 名 | order-management-v1 |
| `{{CHANGE_DIR}}` | Change 目录 | openspec/changes/order-management-v1 |
| `{{TASK_PREFIX}}` | Task ID 前缀 | OM |
| `{{BACKEND_LAYERS}}` | 后端分层顺序 | 数据库/DDL → 实体与 DTO → 数据访问层 → 业务逻辑层 → 接口层 |
| `{{FRONTEND_LAYERS}}` | 前端分层顺序 | API 定义 → 通用组件 → 页面与路由集成 |

完整取值样例见 [`examples/填写示例.md`](./examples/填写示例.md)。

### 3. 逐阶段执行

一次只粘贴一个阶段的代码块。等 AI 输出完、你 Review 通过后，再粘贴下一阶段。

**不要把多个阶段合并成一次对话** —— 阶段隔离是这套模板生效的前提。

---

## 约定速查

**问题状态机**

```
❌ 待确认  →  🔄 追问中  →  ✅ 已关闭
```

只有 `✅ 已关闭` 的结论才能写进 Spec 正文。

**严重级别**：`BLOCKER`（阻塞）/ `MAJOR`（重要）/ `MINOR`（次要）

**ID 体系**

| 前缀 | 含义 | 产生阶段 |
|------|------|---------|
| `PD-XXX` | 产品需求问题 | 阶段1 |
| `TECH-XXX` | 技术问题 | 阶段1 |
| `ASSUM-XXX` | 未决假设 | 阶段2 |
| `{{TASK_PREFIX}}-XXX` | 开发任务 | 阶段4 |
| `TD-XXX` | 未决技术债 | 阶段7 |

---

## 依赖与适配

- **OpenSpec**：阶段 3/4/7 基于 [OpenSpec](https://github.com/Fission-AI/OpenSpec) 的 Change 目录结构。没有用 OpenSpec 也可以照常使用，把 `{{CHANGE_DIR}}` 换成任意自定义目录即可，文件语义不变。
- **技术栈无关**：模板不绑定任何语言或框架，前后端分层顺序通过 `{{BACKEND_LAYERS}}` / `{{FRONTEND_LAYERS}}` 变量配置。
- **模型无关**：不绑定具体模型版本，任何具备文件读写能力的编码 Agent 都可使用。

---

## 常见问题

**Q：必须走完 7 个阶段吗？**
小改动可以只用阶段 1、2、5。但阶段 2（唯一真相源 Spec）建议保留 —— 它是后续所有阶段的锚点，去掉后风险隔离链条就断了。

**Q：为什么阶段 5 遇到 P2 任务就停下来不干活？**
这是设计意图。P2 意味着该任务依赖尚未敲定的假设，此时写出来的代码大概率要返工。停下来问一句，比返工便宜。确认逻辑后把它升级为 P0/P1 再继续即可。

**Q：多轮迭代时旧的 QA 会被覆盖吗？**
不会。阶段 1 内置【增量状态维护规则】，要求先读取历史 QA 文件、继承已关闭问题的 ID 与结论，只允许增量追加。

**Q：中文文件名在 GitHub 上有问题吗？**
没有，GitHub 完整支持 UTF-8 文件名。若你的工具链对中文路径敏感，可自行重命名为 `claude.md` / `codex.md`，记得同步修改 README 中的链接。

---

## License

[MIT](./LICENSE) — 可自由使用、修改、商用。
