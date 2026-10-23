---
name: develop
description: 按复杂度与风险执行开发需求，完成必要的规划、实现、检查与交付。用于实现或修复任务；讨论和代码审查按用户原意处理。
---

# 自适应研发工作流

以当前对话中的明确需求为任务；没有任务时只询问需求。

读取并遵循本 Skill 目录内的 [references/develop.md](references/develop.md)。
相对路径基于本 SKILL.md 所在目录，不是业务仓库工作目录。
同一任务中已读取且未变化的规则不重复加载。

本入口采用可复用的 Agent Skills 结构；自动发现、目录及调用语法由宿主决定。
不支持原生 Skill 时，可将 references/develop.md 作为提示词或项目上下文提供给 AI，并附上需求。
该文件是 docs/workflow/develop.md 的生成分发副本，只维护权威源，不单独修改副本。

目标业务仓库的适用指引、规格及用户授权仍然适用。
安装 Skill 不表示授权提交、推送、发布或其他外部副作用。
