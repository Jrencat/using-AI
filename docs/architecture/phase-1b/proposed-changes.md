# Proposed Changes (Phase 1B — Gap Registration Only)

> Status: `PROPOSAL / NOT APPLIED`. This document registers design gaps found in `using-ai-status-review.md`. It does **not** modify any Phase 1A `FROZEN` file (`protocol.md` / `state-model.md` / `routing.md` / `evidence.md` / `legacy-mapping.md` / `adr/adr.md`) or the Legacy 7-stage templates. Nothing here is applied until a human explicitly confirms and a separate change is made to the frozen file itself.

---

## Change Proposal 1 — Task Resume

**建议优先级**：`P2`（默认）

**当前缺口**：`state-model.md` §4 的 Task 状态机只定义了 `ELIGIBLE`/`BLOCKED`/`IN_PROGRESS`/`EVALUATING`/`DONE`/`FAILED`/`RISK_PENDING`，以及 retry-on-`FAIL`/`INVALID_AGENT_RESULT` 的转移。没有任何"Resume"（跨 session 接续一个未完成 Task）相关的状态、字段或转移规则。

**为什么现有 Task / Attempt 模型不足以表达跨 session Resume**：Attempt（`protocol.md` §5.4 `attempts[]`）表达的是"同一次尝试内的重试"，前提是执行连续、上下文未丢失。跨 session Resume 是不同的问题：执行被打断后，(a) 无法从状态机本身判断一个 `IN_PROGRESS` Task 是"仍在真实执行"还是"执行者已经离开、状态只是没被更新"；(b) 没有定义谁有权接手、是否需要所有权转移记录；(c) 没有定义中断前产生的 Evidence 在恢复后是否仍然可信，还是必须重新验证。

**Resume 至少需要解决的语义问题**：
1. 中断检测——如何区分"真实执行中"与"执行者已消失但状态未更新"。
2. 所有权/身份——同一 agent/session 续做，还是允许不同 agent/session 接手；是否需要显式转移记录。
3. 旧 Evidence 的可信度——中断前收集的 Evidence，Resume 后是直接复用还是必须重新核验。
4. 是否消耗 Attempt——Resume 算作同一次 Attempt 的延续，还是开启新的 Attempt（影响 retry cap 计数）。
5. 触发条件——人工手动重新打开、下一次 session 自动检测、还是依赖一份显式的 handoff 记录。

**当前推荐的最小解决方向**：不新增顶层对象。建议探讨在 Task 的 `IN_PROGRESS` 状态下追加一个可选的中断标志/字段（例如 `resumable` + 一个指向最后一次可信 Evidence 的引用），并规定 Resume 时必须重新声明/复核这些旧 Evidence 是否仍然可信，而不是默认直接信任。这只是方向性建议，不是最终设计。

**哪些内容必须等 Runtime / 真实执行后才能确定**：中断检测本身依赖真实的 session 生命周期信号，这类信号在纯文档层面无法定义，需要 Runtime 存在后才能观察；Ownership 转移的实际触发方式，以及"旧 Evidence 复核"规则的具体粒度，都需要真实场景数据支撑，本轮不作进一步结论。

**何时才值得改冻结 state-model.md**：仅凭本次文档审查不构成修改冻结文件的理由。建议等到出现第二个真实场景（例如一次真实 Pilot 中，某个 Task 确实跨 session 被接续，且因为当前缺少 Resume 定义而导致了实际风险、返工或人工困惑）之后，才启动对 `state-model.md` 的正式变更评审。在此之前，本 Proposal 保持 `P2` / 待观察状态。

---

## Change Proposal 2 — Evidence Trust（独立可信来源问题）

**当前 Evidence Trust Tier 的设计**：`evidence.md` §2 定义 5 级信任分层 `SELF_REPORT < RUNTIME_GENERATED < TOOL_GENERATED < INDEPENDENT_VERIFICATION < HUMAN_VERIFICATION`，并规定 `PASS` 判定至少需要 `≥RUNTIME_GENERATED` 的证据，`SELF_REPORT`-only 只能停在 `INSUFFICIENT`。

**SELF_REPORT 与 RUNTIME_GENERATED 的边界**：`SELF_REPORT` 是 agent 的纯文字描述（"我做了 X"），没有可核实的产物；`RUNTIME_GENERATED` 要求存在一个真实运行动作产生的输出（工具调用返回值、文件读取结果等）。但这个边界的可靠性完全取决于"这份输出确实来自被声称的那次执行"——目前协议没有定义如何核实这一点。

**为什么 Agent 自己声明 `RUNTIME_GENERATED` 不能作为可信证明**：Trust Tier 标签目前是由 agent 在叙述中自行赋予的（"这是 RUNTIME_GENERATED 证据"），协议里没有任何独立机制核实该标签是否属实。这是自证问题的二阶版本：不仅 Claim 本身可能只是 `SELF_REPORT`，连"这条证据属于哪个 Tier"这件事本身也可能只是 agent 的自我认定。

**需要什么"独立来源"才能证明 Trust Tier**：需要一个不受 agent 自身叙述控制的、独立记录工具调用/执行过程的来源——例如由宿主环境（而非 agent 自行生成）附带时间戳与调用参数的调用日志，使"这条证据确实来自一次真实调用"可以被第三方核对，而不是依赖 agent 自己贴的标签。

**哪些部分属于 Protocol 问题**：Trust Tier 的分级逻辑本身、`PASS` 判定门槛、不同 Claim 类型对应的最低 Tier 要求——这些是 Protocol 层的规则定义，已经在 `evidence.md` 中规定，属于"已设计"范畴，本 Proposal 不改动这部分。

**哪些部分可能属于未来 Runtime / Tooling 问题**：如何独立记录、核验"一次工具调用确实发生过"（调用日志生成、来源认证）——这类"证据的证据"机制需要脱离纯文档叙述、由某种执行环境记录，属于 Runtime/Tooling 范畴，明确不在本轮设计范围内，本文档只记录问题本身。

**哪些问题目前仍然 UNPROVEN**：Trust Tier 标签是否会被 agent 系统性错误标注（乐观偏差或伪造）尚无真实数据；即便设计出"独立来源"机制，它在实践中能否真正提升可信度也未验证。两者都需要 Runtime 存在并积累真实执行数据后才能回答，本轮不作进一步结论。

---

## 本文档的边界声明

- 不修改 `protocol.md` / `state-model.md` / `routing.md` / `evidence.md` / `legacy-mapping.md` / `adr/adr.md`。
- 不修改 Legacy 7 阶段 Prompt 模板。
- 不新增 Core Object。
- 不设计 Runtime / CLI / MCP / SDK。
- 两个 Proposal 均为待人工确认的登记项，非已批准变更。
