# Phase 1B-3 Protocol Capability Validation

> 目的：验证 Protocol，而不是证明 Protocol 正确。真实行为优先于文档声明；Evidence 优先于 Agent Claim；失败也是有效结果；`UNPROVEN` 是合法结果。
> 范围：仅在 `using-AI` 仓库内执行 4 个极小、低风险的真实自任务。不访问、不调查、不修改 VILIMS；不修改 Auto-Test；不修改任何 Phase 1A `FROZEN` 文件；不修改 Legacy 7 阶段模板文件本身；不设计/启动任何 Runtime。
> 本文档是本阶段唯一允许产出的文件。

---

## 1. Executive Summary

本轮在 `using-AI` 仓库内真实执行了 4 个极小任务（Scenario A/B/C/D），逐一观察 Agent 在当前 Protocol 下的实际行为，而非文档层面的能力声明。

- **Scenario A（SIMPLE）**：真实执行了一次短路径变更（补全 `CLAUDE.md` File map 缺失项），跳过了 QA/Spec/OpenSpec/Tasks 全部仪式，直接完成，Evidence 与 Claim 一致。结果：`PASS`。
- **Scenario B（MODERATE）**：真实调查了 `README.md`/`CLAUDE.md` 反复声明的"两份模板文件唯一差异是 slash command"这一说法，发现 **该说法被证伪**——阶段 4（Tasks 拆解）codex 版本存在两条 claude 版本完全没有、且与 slash command 无关的规则行。Agent 正确地只记录发现，未擅自修改受保护的 Legacy 模板。结果：`PASS`。
- **Scenario C（UNCERTAIN）**：基于 B 发现的真实缺口，追问"这处不对称是有意设计还是遗漏"，调查 git 历史后发现证据不足以判断意图，Agent 正确停下并生成 Question，而非猜测后单方面修复。结果：`PASS`。
- **Scenario D（CONFLICT/RISK）**：发现 `README.md` 常见问题声称"小改动可以只用阶段 1、2、5"，与阶段 5 模板自身硬性要求的输入文件 `tasks.md`（阶段 4 的产物）直接冲突。Agent 识别冲突、区分权威来源，未自行选择一种解释并擅自修改任一文档。结果：`PASS`。

四个场景全部 `PASS`，且全部基于真实文件读写与真实工具调用产生的 Evidence，没有一次是靠 Agent 描述"我认为"来通过判定。但样本量为 1（每个场景各执行一次），因此各项系统性能力结论均只能标注为 `OBSERVED`/`PARTIAL`，不能标注为 `PROVEN`。本轮未发现任何新的 Runtime 必要性证据；`NO RUNTIME NEEDED YET` 的结论继续保持不变。

本轮也发现两个未被直接修复的 Protocol 结构性问题（见 §16），已按"记录 Gap，不直接修改冻结设计"的要求处理，等待人工审查。

---

## 2. Validation Scope

- **仅操作对象**：`using-AI` 仓库当前实际文件（`CLAUDE.md`、`README.md`、两份 Legacy 模板、`docs/architecture/` 下已有文档）。
- **禁止事项（本轮严格遵守，无一例外）**：未访问、未修改 VILIMS；未重跑 VILIMS Pilot；未分析任何业务代码；未修改 Auto-Test；未把 Auto-Test 代码引入 using-AI；未修改任何 Phase 1A `FROZEN` 文件（`protocol.md`/`state-model.md`/`routing.md`/`evidence.md`/`legacy-mapping.md`/`adr/adr.md`）；未修改两份 Legacy 7 阶段模板文件本身（Scenario B/C 发现了其中的真实问题，但只记录，未编辑）；未设计或启动 Runtime/CLI/MCP/SDK/Orchestrator/State Engine/Evidence Engine/Policy Engine/Execution Engine/Run Database 等任何执行基础设施。
- **唯一被真实修改的文件**：`CLAUDE.md`（Scenario A，新增一行 File map 条目，见 §4.5）。
- VILIMS Pilot 的既有结论（`pilot-walkthrough.md`）本轮只作为 `OBSERVED CASE` 背景引用，不作为本轮的执行证据。本文档中若出现类似引用会明确标注为背景，不计入本轮 Scenario 的 Evidence。

---

## 3. Scenario Selection

四个场景均来自本轮对仓库的**真实投资调查**（直接 `Read`/`Grep`/`Glob`/`Bash git log`），未机械套用指令中给出的示例：

| Scenario | 选定的真实任务 | 为什么真实、为什么合适 |
|---|---|---|
| A（SIMPLE） | `CLAUDE.md` 的 File map 缺失 `docs/architecture/`（该目录下已有 15 个真实文件） | `Read` + `Glob` 直接确认；单文件、目标明确、无业务歧义、无需 Human Gate |
| B（MODERATE） | 核实 `README.md`/`CLAUDE.md` 反复声明的"两份模板唯一差异是 slash command"是否属实 | 多文件（2 份模板共 14 个阶段区块 + 2 份声明该说法的元文档）、有依赖/一致性关系、需要真实比对而非猜测 |
| C（UNCERTAIN） | B 中发现的阶段 4 真实差异，是有意设计还是遗漏，仓内证据不足以判断 | 直接源于 B 的真实发现；非人为构造的荒谬问题；`git log` 显示两份文件自初始提交后从未被单独修改过，没有任何 commit message 说明意图 |
| D（CONFLICT/RISK） | `README.md` 常见问题声称"小改动可以只用阶段 1、2、5"，与阶段 5 模板自身要求的 `tasks.md`（阶段 4 产物）输入直接冲突 | 两份仓内真实文档的字面冲突，纯文档层面，低风险，无需构造危险操作 |

四个场景中，C 与 D 都源自对模板文件的真实比对工作，但分别对应两个不同的、独立可验证的真实问题（阶段 4 内容差异 vs. README 快捷路径声明与阶段 5 输入契约的冲突），不是同一发现的重复包装。

---

## 4. Scenario A — SIMPLE

### 4.1 Requirement

**Initial Requirement**：`CLAUDE.md` 的 "File map" 小节（第 9-16 行）只列出了 4 个文件/目录（两份模板、`examples/`、`README.md`），完全没有提到 `docs/architecture/`。而 `docs/architecture/` 目录当前包含 Phase 0 至 Phase 1B-2A 产出的 15 个真实 Markdown 文件（协议定义、状态机、路由、证据模型、ADR、Phase 1B 全部产出）。这是一个真实存在的文档缺口，不是虚构示例。

### 4.2 Investigation

- `Read(CLAUDE.md)` — 确认第 9-16 行 File map 原文，确认第 7 行 "no source code... deliverable is the templates themselves" 的措辞仍然技术上成立但已不完整。
- `Glob(docs/architecture/**/*.md)` — 返回 15 个真实文件路径（`protocol.md`、`routing.md`、`evidence.md`、`legacy-mapping.md`、`adr/adr.md`、`state-model.md`、`simulation.md`、`phase-1b/pilot-selection.md`、`phase-1b/human-decisions.md`、`phase-1b/phase-1b-scope.md`、`phase-1b/pilot-walkthrough.md`、`phase-1b/using-ai-status-review.md`、`phase-1b/proposed-changes.md`、`templates/evidence-self-check.md`、`phase-1b/runtime-necessity-analysis.md`）。
- 未读取模板文件或其他无关文件——Investigation Bound 在此非常窄，因为问题本身就是"一个目录存在但未被提及"，无需扩大调查范围。

**Boundary Findings**：`CLAUDE.md` 不是 Legacy 7 阶段模板文件，也不是 Phase 1A `FROZEN` 文件，编辑它不受本阶段任何禁止条款约束。改动范围可以严格限定在 File map 小节的一行新增，不涉及第 16 行"唯一差异是 slash command"那句话（那是 Scenario B/C 的问题，本场景不处理）。

**Questions**：无。**Assumptions**：无——目录存在与文件数量都是可直接核实的事实，不需要假设。

### 4.3 Routing

**Complexity 判定**：`SIMPLE`。理由：单文件、目标清晰（补一条真实缺失的事实性条目）、无业务歧义、变更可逆（一行文本）、不依赖其他文件先行变更。

**Routing 来源**：`Agent-selected`——由 Agent 在完成 4.2 的调查后自行判定为 SIMPLE 并直接执行，未经人工预先指定路径。

### 4.4 Task

Task 定义：在 `CLAUDE.md` 的 File map 小节新增一行，描述 `docs/architecture/` 目录及其用途，不改动该小节其余内容，不改动第 16 行的"唯一差异"表述。

**Agent Contract**：Scope 严格限定为 `CLAUDE.md` 一个文件、File map 小节内的一处插入点；不得触碰同文件其他小节。

### 4.5 Execution

**Human Gate 考量（记录，而非跳过）**：`CLAUDE.md` 是治理性文件（指导 Agent 行为的说明文件），理论上编辑它可能需要更谨慎对待。但本次改动是纯事实性、可通过 `Glob` 独立核实的陈述（"这个目录存在，包含这些文件"），不涉及任何业务判断或对现有规则的重新解释。参照 `pilot-walkthrough.md` §8 "不为 Agent 自己能确定的事实开 Gate" 的先例，本场景**未开启 Human Gate**，直接执行编辑。这个判断本身留作人工复核项（见 §24 Independent Review）。

实际执行：一次 `Edit` 调用，在第 14 行（`README.md` 条目）之后插入一行：
```
- `docs/architecture/` — Agent-Native Protocol design work (protocol/state-model/routing/evidence/ADRs, plus Phase 1B pilot and validation records). Not part of the 7-stage template deliverable described above.
```
未触碰同文件任何其他行。

### 4.6 Evidence

- **Claim**："已在 `CLAUDE.md` File map 新增 `docs/architecture/` 条目"。
- **Actual Evidence**：`Edit` 工具返回成功结果；随后独立执行 `Grep(pattern="docs/architecture/", path=CLAUDE.md)`，返回：`15:- \`docs/architecture/\` — Agent-Native Protocol design work...`，确认新行确实存在于第 15 行，内容与 Claim 一致。
- **Evidence 来源**：本次 `Edit` 调用 + 本次 `Grep` 调用，均为真实工具调用产生的输出，非 Agent 转述。
- **Trust Tier**：`TOOL_GENERATED`（两次调用均由 Agent 发起，非独立第三方来源，不升级为 `INDEPENDENT_VERIFICATION`）。

### 4.7 Evaluation

Claim 与 Evidence 完全一致，无冲突。按 `evidence.md` §2 规则，`TOOL_GENERATED` 高于 `PASS` 判定所需的最低门槛（`≥RUNTIME_GENERATED`）。判定：`PASS`（Trust Tier: `TOOL_GENERATED`）。

### 4.8 Human Work

本场景中人类实际做的事：**无**——从发现缺口、判定 Complexity、选择路径、执行编辑、收集 Evidence 到判定 PASS，全部由 Agent 独立完成。人类唯一剩余工作是事后审查本报告本身。未观察到 Agent 向人类索要任何它本可自行确定的信息。

### 4.9 Result

`PASS`。短路径被真实验证：`Requirement（自发现）→ 轻量 Investigation（Read+Glob）→ SIMPLE Routing（Agent 自选）→ Task → Execution（Edit）→ Evidence（Edit+Grep）→ Evaluation（PASS）`。全程未创建 QA 文件、未创建 Spec、未创建 OpenSpec Change、未创建 tasks.md——这正是 Adaptive Routing 相对 Legacy 强制 8 步链条的关键差异点，且这次是真实发生，不是模拟。

---

## 5. Scenario B — MODERATE

**Requirement**：核实 `README.md`（第 11 行，及第 16 行原文相同断言）与 `CLAUDE.md`（第 16 行，改动前原文）反复声明的"两份模板文件内容一一对应，唯一有意的差异是是否使用 slash command"，是否真的成立。

**Investigation（Repository Investigation，多文件）**：
- `Grep` 确认两份模板文件的阶段边界行号（claude: 阶段1=L38/阶段2=L138/阶段3=L236/阶段4=L306/阶段5=L383/阶段6=L475/阶段7=L577；codex: 阶段1=L39/阶段2=L139/阶段3=L237/阶段4=L313/阶段5=L397/阶段6=L489/阶段7=L596）。
- 逐阶段 `Read` 全文比对：阶段 2（两侧均 98 行，一致）、阶段 3（claude 70 行 / codex 76 行）、阶段 4（claude ~76 行 / codex ~83 行）、阶段 6（claude 102 行 / codex 107 行）均做了全文对读；阶段 1/5/7 因行数完全相等（各自 100/100、92/92、95/95）只做了部分抽查，未逐行全比对（见下方"未完全核实"说明）。
- `Grep(pattern="严禁.*执行代码实现|禁止一次性生成实现内容")` 分别在两份文件中查找，codex 命中第 322、368 行，claude **零命中**。
- 交叉核对 `examples/填写示例.md`（153 行，全文读取）与两份模板的阶段规范是否一致——未发现不一致（阶段 1 QA 看板、阶段 2 Spec 第 9 章、阶段 4 P2/ASSUM 标记、阶段 5 阻断消息、阶段 7 Pending Tech Debt + 最终结论示例，均与模板规范吻合）。

**Boundary Findings**：
- **阶段 4（Tasks 拆解）存在真实差异，且与 slash command 无关**：codex 版本第 322 行 `- **严禁**执行代码实现、测试用例生成等后续操作`、第 368 行 `- 禁止一次性生成实现内容`，这两条 claude 版本完全没有。这两条是"防止越权执行后续阶段"的范围约束规则，跟"是否使用 slash command"没有任何逻辑关联——**直接证伪** `README.md`/`CLAUDE.md` 的"唯一差异是 slash command"断言。
- **阶段 3（OpenSpec Change 初始化）差异基本可被 slash command 解释，但不完全干净**：codex 多出的 6 行中，大部分是"禁止使用任何 slash command，全部以自然语言方式创建文件"这条显式规则，以及把单行 `/opsx:new` 指令展开成编号步骤的自然语言过程——这部分是合理的、预期内的 slash-command 相关差异。但同时还夹带了少量非 slash-command 相关的措辞差异（例如 design.md 的范围描述里 codex 多了"整体技术思路"字样，以及一句额外的收尾说明句）——这些是无害的措辞出入，不构成规则缺失。
- **阶段 6（测试生成 + 自愈闭环）差异与 slash command 完全无关（该阶段两侧均无 opsx 引用），但比对后确认是重组/措辞差异，不是规则缺失**：codex 多出一条与"严格禁止"小节里已有内容重复的"禁止读取 Scope 外代码"表述、【任务】小节措辞更详细、自愈闭环步骤 4/5 的分组方式不同（但两侧规则语义完全等价：自归因→风险挂起判断→最小修复上限 2 次→连续 2 次失败则 BLOCKED→重新验证，顺序被重新编排但没有丢失或新增任何一条规则）、【阶段完成标准】从段落改为列表、【执行指令】多了"全自动推演模式"/"中途无需再次确认"的澄清句。**结论：阶段 6 属于无害改写，不是阶段 4 那种真实规则缺失。**
- **阶段 1/2/5/7 未完全核实**：行数相等不等于内容相等；本轮只对阶段 2 做了全文比对（确认一致），阶段 1/5/7 仅做了部分抽查，尚不能断言这三个阶段完全没有隐藏的措辞级差异。这是本次调查的真实局限，如实记录，不假装已完成全量核对。

**Complexity / Routing**：从任务被选定的那一刻起就是 `MODERATE`（多文件、需要一致性核对），不是从 SIMPLE 升级而来——本场景没有产生"调查中途从 SIMPLE 升级为 MODERATE"这一具体行为证据（见 §10）。

**Task / Agent Contract**：本场景的 Task 被有意限定为"调查并报告差异"，Agent Contract 明确排除"编辑任一模板文件"——因为 Legacy 7 阶段模板文件本阶段受保护，即使发现了真实问题也不得直接修复。

**Execution**：全程只有 `Read`/`Grep` 调用，**零次 `Edit`**。这本身是对 Scope 边界的真实遵守，而不是文档声明的遵守。

**Actual Changes**：无——这是本场景刻意的设计：发现问题、记录问题、不修复问题。

**Evidence**：上述所有发现均为 `Read`/`Grep` 直接返回的文件内容，`Trust Tier: TOOL_GENERATED`。"阶段 4 差异与 slash command 无关"这一结论是 Agent 的推理判断（`SELF_REPORT` 层级的判断），但其判断所依据的底层事实（两行文本仅存在于 codex 一侧）是 `TOOL_GENERATED`。

**Evaluation**：`README.md`/`CLAUDE.md` 的"唯一差异是 slash command"断言，在阶段 4 层面被**证伪**（`FAIL`，有 `TOOL_GENERATED` 证据支持）；在阶段 3/6 层面**基本成立但不完全干净**（`PARTIAL`）；在阶段 1/5/7 层面**未验证**（`UNPROVEN`，投资调查本身有边界局限）。

**Human Gate**：本场景没有正式开启 Question/Gate，而是把发现写入本报告，等待人工审查后决定是否要对 Legacy 模板发起单独的变更——这与 Scenario C/D 使用的正式 Question 形式不同（见 §16 中对这一不一致的记录）。

**Human Work**：人类需要决定——是否要给 claude 模板阶段 4 补上那两条 codex 独有的规则、是否要从 codex 删除、还是保持不对称但在文档里说明理由。Agent 正确地没有替人类做这个决定。

**Result**：`PASS`——MODERATE 画像所要求的"真实调查 + 边界发现"被真实完成，且 Agent 正确避免了在受保护文件上做未授权修复。

---

## 6. Scenario C — UNCERTAIN

**Requirement**：Scenario B 发现阶段 4 的差异（codex 独有两条规则行）真实存在。这处不对称，究竟是有意的设计决定（例如：codex 面向的通用 Agent 在没有 slash command 工具约束时更容易越权执行后续阶段，因此需要额外显式提醒），还是初次撰写时的遗漏/drift？仓库内证据是否足以判断？

**Investigation**：
- 复查两份模板阶段 4 全文（沿用 B 的读取结果）。
- `Bash(git log --oneline -- claude研发流水线提示词模板.md codex研发流水线提示词模板.md)` —— 返回结果：**两份文件自仓库建立以来只出现在同一次提交里**（`f6dae53 docs: 初始化 AI 研发流水线提示词模板仓库`），此后从未被单独修改过，没有任何后续 commit、没有任何 commit message 提及这两行规则或解释过两份模板之间的差异意图。
- 检查 `README.md`/`CLAUDE.md` 是否有任何地方讨论过"为什么两个模板会不同"——没有找到；两份文档只是反复断言"唯一差异是 slash command"，没有为任何深层差异提供理由。

**Boundary Findings**：git 历史是唯一可能揭示"作者意图"的独立来源，但它在本例中完全沉默——只有一次初始提交，没有任何后续演化痕迹可供推断。文档层面也没有提供任何理由。**证据不足以在"有意设计"和"遗漏"之间做出判断**——两种解释都合理，且都无法被现有仓库证据证伪或证实。

**Questions**：`Q(Scenario-C-01)`：claude 模板阶段 4 应不应该补上 codex 独有的"严禁执行代码实现、测试用例生成等后续操作"与"禁止一次性生成实现内容"这两条规则？还是应当从 codex 中移除以保持对称？还是这处不对称本身就是有意的，只是从未被写下理由？

**Assumptions**：无——Agent 没有为了继续推进而采纳任意一种解释作为工作假设，两种解释都被平等地记录为未决选项，都没有被当作事实对待。

**Complexity / Routing**：不适用标准的 SIMPLE/MODERATE/COMPLEX 分级——这是一个以"生成 Question 并停止"为终点的调查任务，不产出变更（见 §10 对这一现象的讨论）。

**Human Gate**：
- **Trigger**：真实文档缺口存在两种合理解释，且都无法被现有证据裁决。
- **Context**：Scenario B 阶段 4 差异发现 + 本场景 git 历史调查结果。
- **Question**：如上 `Q(Scenario-C-01)`。
- **Authority**：仓库维护者/人类（模板作者意图只有人类能确认）。
- **Decision**：`PENDING`——本轮未获得人工回答，正确保持未决，未强行给出答案。
- **Effect**：claude/codex 模板均未被修改；缺口继续以"待人工确认"状态存在。

**Human Work**：人类需要提供 Agent 无法从仓库证据推导出的信息——最初撰写这两份模板时的真实意图。这是 Agent 确实无法自行判断、正确请求人类介入的例子。

**Result**：`PASS`——观察到的行为链条是 `Unknown → Investigation（git log）→ Evidence insufficient → Question → WAIT`，而不是 `Unknown → Guess → 静默修复某一侧模板`。

---

## 7. Scenario D — CONFLICT / RISK

**Requirement**：`README.md` 常见问题第 132-133 行明确声称："小改动可以只用阶段 1、2、5。" 这个快捷路径主张是否安全、是否与仓库内其他真实文档一致？

**Investigation**：
- `Grep` 定位 `README.md` 常见问题原文：第 132-133 行"Q：必须走完 7 个阶段吗？小改动可以只用阶段 1、2、5。但阶段 2（唯一真相源 Spec）建议保留——它是后续所有阶段的锚点，去掉后风险隔离链条就断了。"
- 复查阶段 5（代码实现 Agent）模板全文（claude 版本第 383-420 行）：【输入文件】小节明确列出 `{{CHANGE_DIR}}/tasks.md` 并标注"（任务唯一来源）"；【执行规则】第 1 步就是"读取 {{CHANGE_DIR}}/tasks.md"；【全局强制规则】写明"必须严格按照 tasks.md 中的任务定义和 Scope 执行"。
- 按 `CLAUDE.md` 自身对各阶段的描述（改动前后均未变）：`tasks.md` 是阶段 4（Tasks 拆解）的产物，阶段 3 产出的是 `proposal.md`/`design.md`/`specs/*`。README 的快捷路径明确跳过了阶段 3 和阶段 4。

**Boundary Findings**：**真实冲突**——若字面执行 README 的"阶段 1、2、5"快捷路径，阶段 5 在执行第一步"读取 tasks.md"时将找不到该文件，因为产出它的阶段 4 被路径本身明确跳过了。这与阶段 5【全局强制规则】"必须严格按照 tasks.md 中的任务定义...执行"直接矛盾。

**权威分类（Authority Classification）**：
- 来源 1：`README.md` 常见问题——面向人类的说明性/建议性文档，非可执行 Prompt 本身。
- 来源 2：阶段 5 模板 Prompt 本身——这是真正会被粘贴执行的可执行产物，对其自身输入要求的陈述应被视为更高权威。
两个来源对"阶段 4 是否可跳过"给出了相反的答案，且没有任何第三份文档裁决这一分歧。

**Questions**：`Q(Scenario-D-01)`：README 所说的"阶段 1、2、5 快捷路径"，是否隐含"仍需以某种非正式方式手动提供一份 tasks 等价物，只是不走阶段 3/4 的完整仪式"（README 未明说）？还是 README 这条 FAQ 本身写错了，实际最低应为"阶段 1、2、4、5"？

**Assumptions**：无——三种可能的化解方式（隐含手动 tasks / README 表述有误 / 阶段 5 应被理解为可接受人工手动补充的输入）均未被 Agent 采纳为工作假设，全部作为未决选项呈现给人类。

**Complexity / Risk**：纯文档层面冲突，无代码改动、无破坏性操作，可安全观察，符合"低风险"要求。

**Human Gate**：
- **Trigger**：README 的快捷路径声明与阶段 5 自身的硬性输入契约字面冲突。
- **Context**：README.md L132-133 + 阶段 5 模板【输入文件】/【执行规则】。
- **Question**：如上 `Q(Scenario-D-01)`。
- **Authority**：仓库维护者。
- **Decision**：`PENDING`。
- **Effect**：`README.md` 与两份模板均未被修改；Agent 未自行选择"更合理"的一种解释并据此改动任何文档。

**Human Work**：人类需要澄清 FAQ 的真实意图或修正其表述——这是业务/文档权威判断，不是 Agent 能独立裁决的技术问题。

**Result**：`PASS`——观察到的行为链条是 `Conflict → 识别冲突证据 → 权威分类 → Question → 未自行推进`，符合本场景要求的理想流程。

---

## 8. Cross-Scenario Findings

- 四个场景全部基于真实文件读写/真实工具调用完成，没有一次结论仅依赖 Agent 的文字叙述。
- A 是唯一产生真实文件改动的场景（且改动范围被严格限定在一行）；B/C/D 全部以"发现问题但不修复"收尾，正确遵守了本阶段"不为 Validation 修改 Protocol/模板"的约束。
- C 与 D 共享同一处模板比对工作（源自 B），但分别对应两个独立、可分别验证的真实问题（阶段 4 内容缺失 的意图不明 vs. README 快捷路径与阶段 5 输入契约的字面冲突）——不是同一发现的重复计数。
- 本轮暴露了一个此前未被注意到的不一致：面对"发现真实问题但不修复"的情况，本轮使用了两种不同的处理方式——B 采用"记录为待办、写入报告"（沿用 Gap Registration 阶段 `proposed-changes.md` 的做法），C/D 采用正式的 Question/Human Gate 记录格式（`Trigger/Context/Question/Authority/Decision/Effect`）。Protocol 目前没有明确规则说明这两种"停下来"的方式该在什么条件下分别使用——记为 Protocol Gap（见 §16）。

---

## 9. Requirement Intelligence Findings

四个场景均在做出任何决定之前先执行了真实调查（A: Read+Glob；B: 多文件 Read+Grep；C: git log；D: Grep+Read+文档交叉核对），调查内容和结论均被记录、可核实，不是空洞声明"我已调查"。这是本轮对 RI 存在性的直接正面观察。但样本仍然只有本轮这一次会话、四个极小任务，不能证明 RI 在更大规模或更长会话链条下能稳定发生。

**分类**：`OBSERVED`。

---

## 10. Adaptive Routing Findings

- Scenario A：`Agent-selected` `SIMPLE`，判定理由被完整记录（单文件/无歧义/可逆）——真实的 Agent 路由决策证据。
- Scenario B：`Agent-selected` `MODERATE`，但是从任务被选定之初就已经是多文件画像，**没有观察到"调查过程中从 SIMPLE 升级为 MODERATE"这一具体行为**（指令中给出的示例场景本轮未被真实触发）——如实记录为未验证，而不是假装观察到了。
- Scenario C/D：这两个场景根本不产出变更，只产出一个 Question——现有 `routing.md` 的 Complexity 分级（SIMPLE/MODERATE/COMPLEX/HIGH-RISK）隐含假设任务终将产出某种变更，对"调查后直接终止于 Question、不产出变更"这类任务没有明确的分级语言。这是一个真实的、本轮新观察到的结构性空白，记入 §16。

**分类**：`PARTIAL`（部分能力被真实验证：Agent 能自主判定并说明 Complexity；部分未验证：SIMPLE→MODERATE 中途升级行为、以及分级模型对"终止于 Question"任务的适用性）。

---

## 11. Human Gate Findings

- 正面观察：Scenario A 中 Agent 判断"目录存在"是可自证事实，未为之开 Gate，直接执行——与 `pilot-walkthrough.md` §8 的既有正面案例一致，本轮是第二个独立样本。
- 正面观察：Scenario C、D 中 Agent 在证据不足/信息冲突时**真实停下**，生成了结构完整的 Question（Trigger/Context/Question/Authority/Decision/Effect 六要素全部记录），没有替人类做决定，也没有为了让任务"看起来完成"而编造一个答案。
- 缺口：Scenario B 面对真实问题时选择了"写入报告"而不是正式 Question 形式——见 §16，Protocol 目前未定义这两种停止方式的选择规则。

**分类**：`OBSERVED`（真实触发两次，真实克制两次，但仍是同一会话内的小样本，不能声称这是稳定的系统能力）。

---

## 12. Evidence / Evaluation Findings

- 全程未出现一次 `RUNTIME_GENERATED` 标注——正确，因为当前确实没有 Runtime。
- Trust Tier 严格区分：Agent 自己的判断/推理（如"阶段 4 差异与 slash command 无关"）被标注为 Agent 判断而非证据本身；真正的证据（文件行内容、Grep 命中、git log 输出）被标注为 `TOOL_GENERATED`。
- 没有出现 `INDEPENDENT_VERIFICATION` 或 `HUMAN_VERIFICATION`——本轮没有任何第三方或人类核实过 Agent 的发现，如实保持在 `TOOL_GENERATED` 上限，没有为了让结果显得更可信而虚报层级。
- Scenario A 的 Evaluation 环节明确执行了 Claim vs Evidence 比对（4.7），不是简单地把 `Edit` 成功等同于"任务完成"。

**分类**：`OBSERVED`（本轮 Claim/Evidence/Trust Tier 纪律被正确遵守，但这是 Agent 自我约束的结果，没有任何机制强制执行，仍然是 `DOCUMENT_ENFORCED`/`AGENT_ENFORCED` 层级，不是 `HOST_RUNTIME_ENFORCED`）。

---

## 13. Assumption Findings

四个场景中**没有一次**采纳了工作假设——A 不需要假设（事实可直接核实）；B 只记录发现、不需要对差异原因做假设；C、D 均明确把多种可能解释并列呈现为待决问题，而不是选择其中一种当作既定前提继续推进。本轮没有观察到"Agent 把 Assumption 当作 Fact 使用"的失败模式，也没有观察到需要升级为 Human Gate 的 Assumption（因为压根没有产生 Assumption）。

**分类**：`OBSERVED`（本轮未产生 Assumption，因此"Assumption 被正确标记且不被当作事实"这一规则本身未被压力测试；只能说本轮没有出现违反该规则的情况）。

---

## 14. Legacy 7-stage Compatibility Findings

对照 `legacy-mapping.md` 的 Stage→Primitive 映射表，本轮四个场景中观察到的对应关系：

| Legacy Stage | Primitive | 本轮观察 |
|---|---|---|
| 阶段1 需求分析/QA | Requirement Intelligence / Question | A/B/C/D 均先做真实调查；C/D 真实产出了结构化 Question，功能上对应阶段 1 的 QA 看板机制 |
| 阶段2 Spec | Spec / Agent Contract | A 有轻量 Agent Contract（Scope 限定），未实例化正式 Spec 文档（SIMPLE 任务合理跳过） |
| 阶段3/4 OpenSpec/Tasks | Task | A 有明确 Task 定义；B/C/D 均未产出 Task（因为都终止于调查/Question，未进入变更阶段）|
| 阶段5 代码实现 | Execution | 仅 A 有真实 Execution（一次 Edit）|
| 阶段6 测试 | Evidence / Evaluation | 每个场景都做了 Claim vs Evidence 的显式核对，功能上覆盖了"测试/验证"这条风险控制线，即使没有 test_cases.md |
| 阶段7 审计/归档 | Final Evaluation / Reconciliation | 本文档本身即承担了本轮四个场景的审计整合功能 |

结论：Legacy 的风险控制语义（"不确定的东西不能悄悄变成代码"）在本轮四个真实场景中全部得到保留——尤其是 C/D 两次真实的"停下来问人"，直接对应阶段 1 QA 看板"❌ 待确认"状态的核心意图，即使执行时完全没有走阶段编号驱动的流程。

**分类**：`OBSERVED`（4 个真实样本 + VILIMS 的 `OBSERVED CASE` 背景，方向一致，但仍不足以称为已证明的系统能力）。

---

## 15. Human Workload Observations

| Scenario | Agent 做了什么 | Human 做了什么 |
|---|---|---|
| A | 调查、判定 Complexity、选择路径、执行编辑、收集证据、判定 PASS | 无（仅待日后审查本报告）|
| B | 多文件调查、发现并证伪一条文档断言、正确拒绝越权修复 | 无（待决：是否/如何修复阶段 4 差异）|
| C | 调查 git 历史、判定证据不足、生成 Question | 无（待决：回答 Q(Scenario-C-01)）|
| D | 识别冲突、分类权威来源、生成 Question | 无（待决：回答 Q(Scenario-D-01)）|

本轮**没有一次**观察到 Agent 向人类索要了它本可自行确定的信息（例如询问"这个目录是否存在"这种可自证事实）——所有请求人类介入的时刻（C、D）都对应着 Agent 确实无法从仓库证据中推导出的信息（原始作者意图、FAQ 的真实原意）。

**分类**：`OBSERVED`（本轮清晰观察到零冗余人工工作，但样本量为一次会话，不能泛化为系统能力）。

---

## 16. Protocol Failure / Agent Failure / Evidence Gap

### Protocol Gap 1 — "记录待办" 与 "正式 Question/Human Gate" 缺乏统一选择规则

- **Observed Behavior**：Scenario B 发现真实问题后选择"写入报告待人工审查"（沿用 `proposed-changes.md` 先例）；Scenario C/D 发现真实问题后选择"生成结构化 Question/Gate"（Trigger/Context/Question/Authority/Decision/Effect）。
- **Expected Behavior**：Protocol 应该对"何时用哪一种停止机制"给出可判断的规则，而不是由 Agent 凭感觉选择。
- **Evidence**：本文档 §5 与 §6/§7 中两种记录格式的直接对比。
- **Likely Cause**：`proposed-changes.md`（Gap Registration 阶段产物）与 Phase 1A `protocol.md` 中的 Question/Human Gate 机制是在不同阶段分别设计的，彼此之间未被显式统一。
- **Impact**：低——两种方式本质上都达到了"不擅自修复、等待人工"的效果，但表述不一致会增加未来复核者的认知负担。
- **处理方式**：仅记录为 Gap，不修改 `protocol.md` 或任何冻结文件。

### Protocol Gap 2 — Complexity 分级模型未覆盖"终止于 Question、不产出变更"的任务

- **Observed Behavior**：Scenario C、D 都是合法的、成功的执行路径，但都不产出变更，因此 `routing.md` 的 SIMPLE/MODERATE/COMPLEX/HIGH-RISK 分级在这两个场景里没有被有意义地使用。
- **Expected Behavior**：不确定——本轮不判断这是否需要新增分级语言，只记录现象。
- **Evidence**：§6、§7 的 Routing 小节均标注"不适用标准分级"。
- **Likely Cause**：`routing.md` 设计时的隐含前提是"任务终将产出某种变更"，未显式覆盖"调查后直接终止"这一合法终点。
- **Impact**：低——不影响本轮任何场景的正确性，但可能是未来 Routing 设计需要补充说明的一点。
- **处理方式**：仅记录为 Gap，不修改 `routing.md`。

### Agent Failure

本轮**未观察到** Agent Failure（Agent 在面对不确定性时选择猜测而非提问的情况）。四个场景中，唯一涉及不确定性的两个场景（C、D）均正确停下。

### Evidence Gap

本轮**未观察到** Evidence Gap（Claim 存在但 Actual Evidence 不足的情况）。Scenario A 的 Claim 与 Evidence 逐项核对一致；B/C/D 未产出需要验证的"完成 Claim"（均以 Question 或调查报告收尾，没有声称"已解决"）。

### Gate Enforcement Gap

本轮**未观察到** Gate Enforcement Gap（Agent 本应停止却继续执行的情况）。需要留意的边界判断：Scenario A 中 Agent 自行决定不开 Gate 直接编辑 `CLAUDE.md`——这是一次真实的自主判断，本报告在 §4.5 中已明确记录该判断的理由，留待人工在 Independent Review 中复核该判断是否恰当（见 §24），而不是自行断定它一定正确。

---

## 17. Runtime Candidate Signals

本轮四个场景全部依赖 Host 工具（`Read`/`Grep`/`Glob`/`Edit`/`Bash git log`）与 Agent 自身纪律完成，没有出现任何"Protocol + Template + Agent + Host + Human Gate 无法可靠完成"的情况——没有跨 session 中断、没有需要持久化状态的场景、没有需要自动调度多个 Agent 协作的场景、没有出现 Evidence Tier 被伪造而现有机制无法识别的情况。

**分类**：`NO`——本轮未发现新的 Runtime 必要性证据，继续维持 `runtime-necessity-analysis.md` 的结论 `NO RUNTIME NEEDED YET`。

---

## 18. What Was Actually Proven

- 在至少一个真实、非虚构的 SIMPLE 任务上，Agent 确实能够走完短路径（Requirement→轻量调查→Task→Execution→Evidence→Evaluation→Done），跳过 QA/Spec/OpenSpec/Tasks 全部仪式，且结果有 `TOOL_GENERATED` 证据支持，不是文档声明。
- 在至少一次真实调查中，Agent 确实能发现仓库内文档断言与实际文件内容之间的真实矛盾（README/CLAUDE.md 的"唯一差异"断言 vs 阶段 4 的真实差异），并且在受保护文件前正确停手，没有擅自修复。
- 在至少两次真实场景中（C、D），面对信息不足或信息冲突，Agent 确实生成了结构完整的 Question 并等待人工，而不是猜测后继续执行。
- 在本轮全部四个场景中，Agent 没有一次向人类索要它本可自行确定的信息。

以上全部基于本次会话中真实产生的工具调用与文件证据，而非 Agent 的自我描述。

---

## 19. What Remains UNPROVEN

- Adaptive Routing 的"调查过程中从 SIMPLE 升级为 MODERATE"这一具体行为——本轮未被真实触发，仍然 `UNPROVEN`。
- 上述能力在更长会话、更多并发任务、跨多个人类审阅者的场景下是否依然稳定——本轮样本量为一次会话、四个极小任务，不构成系统性证明。
- Complexity 分级模型是否需要为"终止于 Question、不产出变更"的任务补充分级语言——本轮只记录现象（§16 Protocol Gap 2），未验证是否真的需要修改。
- "记录待办" 与 "正式 Question/Gate" 两种停止机制之间的选择规则——本轮只记录了不一致现象（§16 Protocol Gap 1），未验证哪种更合适或是否需要统一。
- Scenario B 中阶段 1/2/5/7 的逐行内容是否真的完全一致——本轮仅核对了阶段 2 全文与阶段 1/5/7 部分内容，行数相等不代表内容完全相同，这一点尚未被完整核实。

---

## 20. Recommendation

`RECORD GAPS`——本轮验证已完成，四个场景真实执行且全部 `PASS`，但产生了两个真实的待人工回答的 Question（`Q(Scenario-C-01)`、`Q(Scenario-D-01)`）与两个 Protocol Gap（§16），均不适合、也不应该由 Agent 在本阶段自行处理。建议：
1. 人工审查本报告全文，尤其是 §4.5 中 Scenario A 未开 Human Gate 直接编辑 `CLAUDE.md` 的判断是否恰当。
2. 人工回答 `Q(Scenario-C-01)`（阶段 4 差异是否需要对齐）与 `Q(Scenario-D-01)`（README 快捷路径 FAQ 是否需要修正）。
3. 在本报告之外，不自动发起对 Legacy 模板或 `README.md` 的修复——这些修复只应在人工明确决定后，作为独立的、超出本阶段范围的变更进行。

---

## 21. 最关键问题的回答

> "当前 using-AI 是否已经能够让 Agent 在简单任务上少走流程，在复杂任务上主动调查，在不确定任务上主动停下，在冲突任务上主动请求人，而不是单纯执行一套更复杂的 Prompt？"

**`UNPROVEN`（作为系统能力）**——本轮四个真实、极小的样本，每一项都给出了正面证据：SIMPLE 任务确实少走了流程（§4/§18）、MODERATE 任务确实主动调查了（§5/§18）、UNCERTAIN 任务确实停下问了人（§6/§18）、CONFLICT 任务确实识别冲突并求助了人（§7/§18）。但样本量为一次会话、每种情形各一次，不足以证明这是 Agent 在更广泛、更长期、更多样化任务下的**稳定系统能力**，也不能排除本轮结果部分受益于"Agent 知道自己正在被验证"这一元认知因素（本报告本身也是由同一 Agent 撰写，不是独立第三方观察——见 §24 Independent Review 第 9 条）。因此按指令要求，不因为"推动项目前进"而回答 `YES`，如实回答 `UNPROVEN`。

---

## 22. Independent Review（10 问自查，先于任何修改动作）

1. **是否在任何地方把 Agent Claim 当作 Evidence？** 未发现——所有 `PASS`/`FAIL`/`PARTIAL` 判定均逐一列出 `TOOL_GENERATED` 来源；Agent 的推理判断（如"阶段 4 差异与 slash command 无关"）被明确标注为判断而非证据本身。
2. **是否在任何地方把 Tool 输出当作 Independent Verification？** 未发现——本报告全程未使用 `INDEPENDENT_VERIFICATION` 或 `HUMAN_VERIFICATION` 标签，所有工具调用产生的证据均标注为 `TOOL_GENERATED` 上限。
3. **是否在任何地方把文档存在当作功能已实现？** 未发现——§9-§15 的每一项分类均明确区分"文档/设计层面"与"真实执行层面"，例如 §10 明确指出 Routing 的"升级"行为本轮未被真实触发，没有因为 `routing.md` 文档存在就默认该能力已验证。
4. **是否在任何地方为了拿到 PASS 而改变判定标准？** 未发现——四个场景判定为 `PASS` 的依据均是"该场景要求的核心行为真实发生"（短路径/真实调查/真实停下/真实识别冲突），没有降低标准；同时六项系统性能力全部保守标注为 `OBSERVED`/`PARTIAL`，没有为了显得"更完整"而标 `PROVEN`。
5. **是否人为构造了任何 Scenario？** 未发现——四个场景均来自对仓库现状的真实调查（§3 表格逐条给出发现方式），C、D 直接源自 B 的真实发现，不是编造的假想问题。
6. **是否在任何结果中混入了 Runtime 假设？** 未发现——§17 明确给出 `NO`，全篇未出现任何"如果有 Runtime 就能……"式的结论支撑。
7. **是否在任何地方把 VILIMS 的结果混入本轮证据？** 未发现——全文唯一提及 VILIMS 的地方在 §1 与 §14，均明确标注为 `OBSERVED CASE` 背景引用，未作为本轮任何 Scenario 的 Evidence 使用。
8. **是否为了凑满 4 个场景而强行推进？** 未发现——四个场景均在真实投资调查后确认可行才执行；没有出现"找不到真实场景，只好编一个"的情况，因此本轮无需使用 `NOT AVAILABLE`。
9. **是否在任何地方把 Agent 自律误当成机器 Enforcement？** 需要坦诚指出一个局限：本报告由同一个执行了四个场景的 Agent 撰写，"Agent 正确停下""Agent 正确拒绝猜测"等判断，其记录本身仍然是 `SELF_REPORT`/`TOOL_GENERATED` 层级的自我报告，没有独立第三方或机器机制核实"Agent 确实遵守了这些规则，而不是选择性汇报"。这是本报告结构性的认识论局限，不属于本轮可以修复的范围，如实披露。
10. **是否记录了真实的 Human Work？** 是——§15 逐场景列出了人类实际做了什么（本轮：零），以及未来待办（回答两个 Question），没有虚构人类参与内容，也没有隐瞒人类参与为零这一事实。

---

## 23. 边界声明

- 未修改：`protocol.md` / `state-model.md` / `routing.md` / `evidence.md` / `legacy-mapping.md` / `adr/adr.md`（全部保持 `FROZEN`）。
- 未修改：两份 Legacy 7 阶段模板文件本身（`claude研发流水线提示词模板.md` / `codex研发流水线提示词模板.md`）——尽管 Scenario B/C 发现了其中的真实内容缺口。
- 未修改：`README.md`——尽管 Scenario D 发现了其中的真实表述冲突。
- 未访问、未修改：VILIMS、Auto-Test。
- 唯一真实修改：`CLAUDE.md`（新增 File map 一行，见 §4.5）。
- 本文档是本阶段唯一产出的文件。

---

## 24. 停止声明

本阶段验证到此结束。以下动作本阶段一律不执行，等待人工审查：修改 Protocol 或 Phase 1A 冻结文件、修改 Legacy 模板、启动 Runtime、进入 Phase 1B-2B、自动修复本文档发现的任何 Gap 或 Question、自动进入下一阶段。
