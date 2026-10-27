# 标准 Skills CLI 安装验证

验证日期：2026-10-27。Windows PowerShell，`npx.cmd --yes skills@1.7.4`，Codex 0.164.0。命令面向当前 GitHub 默认分支，不表示固定了 using-AI 提交。未改动核心 Skill、流程规则或保护式安装器。

## 来源与隔离

- 仓库仅有 `skills/develop/SKILL.md` 一个 Skill；固定版 `add Jrencat/using-AI --list` 实际报告 `Found 1 skill`。
- 元数据为 `name: develop` 和非空 description；相对引用 `references/develop.md`，安装不依赖仓库外的规则文件。
- 误在源码仓库执行的首次安装产物，经时间、安装日志、锁记录和三个文件的逐字节比较核验后，移到仓库外临时目录，没有直接删除。后续安装、更新和卸载均只操作临时副本。
- 隔离根目录：`%TEMP%/using-ai-skills-174-bf183222019a440c81c226bf9f63f4e7/`。Node 的 `os.homedir()` 已确认指向临时 `user/`；只对子进程设置 `USERPROFILE`、`CODEX_HOME`、`CLAUDE_CONFIG_DIR`，未修改真实环境或配置。
- 来源不明的 `.claude/settings.local.json` 仅检查 Git 状态、元数据与校验值，未读取正文；未跟踪且被用户级 Git ignore 忽略，按用户数据保留。

## 真实网络安装与移除

下面命令均带 `npx.cmd --yes skills@1.7.4` 前缀；项目命令在临时项目根目录执行，个人命令在隔离用户环境中执行。表中安装、列举和卸载均退出 0。

| 场景 | 安装参数 | 实际目录 | 完整性 / 卸载 |
| --- | --- | --- | --- |
| Codex 项目 | `add Jrencat/using-AI --skill develop --agent codex --copy --yes --json` | `project/.agents/skills/develop/` | 三文件一致；`remove develop --agent codex --yes` 后目录消失 |
| Codex 个人 | 同上，加 `--global` | `user/.agents/skills/develop/` | 三文件一致；同范围 `remove` 后目录消失 |
| Claude Code 项目 | 将 Agent 改为 `claude-code` | `claude/.claude/skills/develop/` | 三文件一致；同 Agent、同范围 `remove` 后目录消失 |
| Claude Code 个人 | `--agent claude-code --global` | `user/.claude/skills/develop/` | 三文件一致；同 Agent、同范围 `remove` 成功 |

三文件为 `SKILL.md`、`references/develop.md`、`LICENSE`，分别与本地分发包逐字节相同；分发规则与许可证另由 `package_develop.py --check` 检查。`list --agent codex --json`、其 `--global` 变体，以及 Claude 项目 `list --agent claude-code --json` 均识别到安装。通用目录的清单可能返回空 `agents` 数组，这不是 Codex 未发现的证据。

## 更新、检查与本地修改

| 操作 | 真实结果与限制 |
| --- | --- |
| `update develop --project --yes`，锁记录与上游一致 | 退出 0、报告最新；手动修改的入口仍存在。这是跳过重装，不是修改保护 |
| 同命令，将临时 `computedHash` 改为全零以触发更新 | 退出 0、更新 1 项；修改的入口和新增 `personal.txt` 都被清除。此用例模拟陈旧锁记录，未修改 GitHub 上游 |
| `update develop --global --yes` | 退出 0、报告最新；GitHub API 不可用时 CLI 自动用 Git clone 检查成功。未制造真实远端版本发布或验证个人范围的实际版本切换 |
| `check` | 实际进入更新流程；固定版源码也把 `check`、`update`、`upgrade` 路由到同一个函数 |
| `check develop --project --yes`，临时锁记录设为全零 | 退出 0、更新 1 项，新增个人文件被删除；不能把 `check` 当成只读预览 |
| 项目 `remove`，入口已手动修改且有新增文件 | 退出 0，整个目录消失，没有修改保护或备份 |
| 个人 `remove`，有新增文件 | 退出 0，整个目录消失，没有备份 |

固定版帮助实际列出 `update [skills...]`、`--project`、`--global`、`--yes`；更新不支持按 Agent 过滤，内部重新安装也不传递首次的 `--copy`。本次只在所需路径验证，不据此承诺所有 Agent 的更新布局。源码中的复制安装会先清理目标目录；标准 CLI 不遵守本项目 `.using-ai-install.json` 的保护约定。

项目 `skills-lock.json` 记录 `source`、`sourceType`、`skillPath`、`computedHash`；本次来源为 `Jrencat/using-AI`、`skills/develop/SKILL.md`。项目更新读取此记录，卸载同步移除对应条目。记录远端内容哈希不等于检查已安装文件是否有个人修改；默认分支记录也不等于不可变提交。个人管理记录位于隔离用户的 `.agents/.skill-lock.json`。团队有意共享项目 Skill 时可审阅提交锁文件及相关 Skill 文件，本任务的测试产物不提交。实验性锁文件恢复未验证。

## 原生宿主证据与 UNVERIFIED

- Codex 0.164.0：以隔离 `CODEX_HOME` 启动真实 `app-server --stdio`，完成 `initialize` 后调用 `skills/list`，指定临时 `host-project` 并 `forceReload: true`。返回临时项目的 `develop`，`scope: repo`、`enabled: true`、无 Skill 解析错误。未调用模型、未复制凭证。
- 首次宿主启动因隔离 `CODEX_HOME` 目录不存在而退出；创建该临时目录后检查通过。
- Windows 原生 Codex 用户目录未随 Node 的临时 `USERPROFILE` 改变，列表还包含真实用户原有的 `develop`。没有修改它，也不把它计为本次个人安装验证。**隔离个人安装的原生发现：UNVERIFIED**。
- `name: develop` 保持不变，原生发现已确认项目入口，官方说明使用 `$` 提及 Skill；**新会话输入 `$develop` 后实际执行工作流：UNVERIFIED**。没有以能读文件或 CLI 清单代替实际调用证据。
- Claude Code：**安装与目录布局已验证；真实宿主加载、`/develop` 调用：UNVERIFIED**。本次未登录、未更改真实宿主配置，既往登录受限记录见[详细接入说明](README.md)。
- 官方 Codex 机制参考：[Skills](https://developers.openai.com/codex/skills/)（本次实际获取）；机制文档不代替以上执行证据。

隔离日志保留在上述临时根目录：`results.json`、各操作 `.log`、`codex-skills-list.json` 及 `codex-server-stderr.log`。它们用于复核此次边界，不是仓库需要分发的测试工具。

## 文档与回归检查

- `python scripts/package_develop.py --check`：退出 0，分发包同步。
- `python scripts/test_install_develop.py -v`：退出 0，7 个测试通过。
- `powershell -NoProfile -File scripts/test_install_develop.ps1`：退出 0，50 项隔离检查通过，网络为模拟；这些测试不代替前面的真实网络安装。
- 上述三个报告均未出现 warning 行；测试工具未提供独立的结构化告警计数。
- 三份改动文档的本地相对链接检查无缺失，PowerShell 示例静态解析无错误；这只是文档检查，不作为安装成功证据。
- 已审阅 Markdown 标题、表格、代码块及完整差异；`git diff --check` 通过。
- 本任务工具及本地汇总报告移到隔离根目录的 `local-task-tools/`，保留原有用户临时报告。`.claude/settings.local.json` 的内容校验值、长度及时间与恢复前一致；未提交、未推送。
