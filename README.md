# using-AI

using-AI 是一套模型无关的 AI 软件研发工作流。你在自己的项目里用自然语言提出需求，AI 会沿着相关代码查清影响范围，完成修改，并说明怎样验证结果。遇到需要取舍的业务规则时，由你决定。

## 快速开始

### 通过 npx 安装

以下命令已在 Windows PowerShell 验证。准备好 Node.js、npm 和 Git，确认可以访问 npm 和 GitHub。在**你打算试用的代码项目根目录**打开 PowerShell，按所用工具选择一条命令安装 `develop` Skill。

**Codex CLI**

```powershell
npx.cmd --yes skills@1.7.4 add Jrencat/using-AI --skill develop --agent codex --copy
```

**Claude Code**

```powershell
npx.cmd --yes skills@1.7.4 add Jrencat/using-AI --skill develop --agent claude-code --copy
```

第一次试用建议选择 **Project**，让 `develop` 只对当前项目生效。如果希望在自己的所有项目中使用，选择 **Global**。

### 提出第一个需求

在同一个项目中开启新的 AI 会话，把下面的示例换成你手头的一项小改动。

| 工具 | 示例 |
| --- | --- |
| Codex CLI | `$develop 给任务列表增加按状态筛选的功能` |
| Claude Code | `/develop 给任务列表增加按状态筛选的功能` |

## 其他 AI 工具如何使用

打开[通用研发规则](docs/workflow/develop.md)，将全文作为项目上下文提供给 AI，再附上你的需求。工具无法读取本地项目时，提供相关文件或代码即可开始分析。能否直接修改文件、执行终端命令和运行测试，取决于宿主提供的工具与权限。

[查看与更新](#查看与更新) · [卸载](#卸载) · [MIT 许可证](LICENSE)

<details>
<summary>已安装 develop：查看、更新和卸载</summary>

### 查看与更新

按原安装范围选择命令。项目级命令在原项目根目录运行，全局命令使用安装时的系统用户与环境。以下为 Codex 清单命令，Claude Code 将 `--agent codex` 换成 `--agent claude-code`。

```powershell
# 查看项目级安装
npx.cmd --yes skills@1.7.4 list --agent codex
# 查看全局安装
npx.cmd --yes skills@1.7.4 list --agent codex --global
```

更新前先将本地定制备份到 Skill 目录之外。更新可能覆盖本地文件，也可能为其他已检测到的宿主写入入口。`check` 是 `update` 的别名，查看本地清单请用上面的 `list`。

```powershell
# 更新项目级安装
npx.cmd --yes skills@1.7.4 update develop --project --yes
# 更新全局安装
npx.cmd --yes skills@1.7.4 update develop --global --yes
```

### 卸载

以下命令会删除所选范围内各宿主的同名 `develop` 入口。先确认其他宿主也可以移除该 Skill，并备份本地定制，再按原范围选择一条命令。

```powershell
# 卸载项目级安装
npx.cmd --yes skills@1.7.4 remove develop --yes
# 卸载全局安装
npx.cmd --yes skills@1.7.4 remove develop --global --yes
```

卸载后查看同范围的清单，并核对安装目录。仅指定 `--agent codex` 时，CLI 可能报告成功但保留共享目录。Codex 可按原范围选用以下命令，预期返回 `False`。

```powershell
# 项目级
Test-Path -LiteralPath '.agents/skills/develop'
# 全局
Test-Path -LiteralPath (Join-Path $HOME '.agents/skills/develop')
```

Claude Code 对应目录为项目的 `.claude/skills/develop/` 或用户的 `~/.claude/skills/develop/`。设置了 `CLAUDE_CONFIG_DIR` 时，全局目录位于该配置目录下的 `skills/develop/`。

</details>
