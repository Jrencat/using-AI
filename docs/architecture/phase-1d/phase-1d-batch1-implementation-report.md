# Phase 1D Batch 1 Implementation Report

## 1. Implementation Summary

在仓库外的 `D:\renjianxiao\phase-1d-execution\harness\` 实现了 Python 标准库单机 CLI、确定性测试和操作说明。范围为 C6/C3/C4/C5/C2/C7；C1 未实现。实现将 Agent 经 Bash 提交的状态请求写入按 run 的 append-only JSONL，将 Claude Code 原始 session JSONL 按事先记录的 byte offset 原样封存，并生成 SHA-256 manifest。Human Gate 只能由独立观察者从真实 `AskUserQuestion` tool_use/tool_result 读取；Agent 自写文本不产生 Human answer。

本次没有执行 P-D/P-N/P-I，也没有修改历史 A-O 或冻结 Protocol。实现是 PARTIAL：C3/C4/C5 的最小状态接口和 C6/C7 封存路径通过合成 Runtime smoke test；尚无新 Claude live session 的独立端到端就绪证据。C2 能独立观察 prompt 与截至水位的 pending，但 Claude 同步 AskUserQuestion 会阻塞 Agent 自己的继续复查，未满足 P-I Run Card 的完整行为链。

## 2. Implemented Capabilities

### C6

`start` 由 operator 在 run 开始前记录 run/probe/session ID、原始 JSONL 路径、start byte offset 和原有 prefix hash；`seal` 复制从 start 到 operator 截止的原始字节到 `runtime.jsonl`，记录 end offset、事件计数、配对情况、缺口、SHA-256 和封存时间。`run.json` 与 `manifest.json` 分别标明 RUN_START/RUN_END。原始行保留工具参数、结果、stdout/stderr/exit code（若 Runtime 提供）。未提供的 exit code 为 unavailable，不能推测。未配对普通工具事件、源缺失、prefix 改动、半行、解析失败、session 不符或空截取均使 `capture_status=INCOMPLETE`。未配对 AskUserQuestion 单独列出，可能是未答 Gate，不自动当作采集故障。

### C3

CLI 支持 Question 创建、从 OPEN 向现有 Protocol 终态迁移、按 ID 查询事件链。每条接受事件有 UUID、递增 sequence、UTC timestamp、Requirement 引用和前后状态。非法迁移被拒绝并记录 `STATE_TRANSITION_REJECTED`；这属于 Harness 诊断事件，不是新的 Protocol Question 状态。Critical Question 不能转 ASSUMED；BLOCKED 要求已观察到真实 Gate 发出。

### C4

`assumption-create` 仅接受已有且当前为 ASSUMED 的 origin Question，持久记录 ASSUM ID、内容、default behavior、impact、confidence、`ISOLATED` 和来源链接。重复 ID/缺来源被拒绝。CLI 接受状态只证明提交发生，不证明调查充分。

### C5

`task-create` 和 `task-routing` 分开持久记录 Task ID、Requirement 引用、scope、priority、Task 层 routing 及理由；支持 SIMPLE/MODERATE/COMPLEX/HIGH-RISK，不产生 `requirement.complexity`。`inspect-order` 用封存的 Bash tool_result 中的 Harness event ID 回执定位创建/路由，再与原始 Runtime 中首次 Edit tool_use 行号比较。缺回执返回 INSUFFICIENT；后于 Edit 返回 AFTER_EDIT，不以后来的最终状态掩盖。Requirement 的 READY/Spec 审批与 Task eligibility 仍由独立 E4 核查，Harness 不伪造。

### C2

独立 operator 可在 Agent 的 AskUserQuestion 前运行 `gate-observe`；它只扫描已绑定 session 的原始 JSONL，找到真实 tool_use 才写 `GATE_ISSUED`，并经 `gate-status` 在记录的 byte watermark 写 `GATE_STATUS_CHECK`。只有匹配 tool_result 中非空的 `toolUseResult.answers` 才写 `GATE_ANSWERED`；工具错误/空答案不会升级为 Human answer。`gate-close` 可记录 operator 的 CANCELLED/TIMEOUT，明确不是 Human decision。`verify` 对 Gate issue、answer 和 pending watermark 与封存 Runtime 原文交叉检查。

### C7

单一 package 包含 `run.json`、`events.jsonl`、`runtime.jsonl`、`manifest.json`。`verify` 重算 hash、Runtime tool pairing/计数、状态 sequence 和 Gate 原始事件交叉关系。执行 Agent 的 `evidence.md` 不导入 package，也不会被标记为可信。operator 必须独立启动/封存，Validator 只读审查。当前同一 Windows 用户的文件 ACL 没有被证明能阻止 Agent 直接改写外置目录；本地 hash 只做封存后完整性检查，无法提供强不可篡改或独立身份认证。

## 3. Runtime Integration

选用 feasibility review 已验证的 Claude Code session JSONL，未配置 hook/MCP，也未修改 Claude。Agent 用 Bash 调用状态 CLI；未来 E4 须在原始 Runtime 中配对该 Bash tool_use/tool_result 与事件 ID。operator 独立执行 start、Gate observer、seal；这些不是 Agent 自报。Run 边界由外部 offset 确定，不能从 Agent 的 scenario 标题推断。由于本轮禁止执行 Probe 且未开启新的 Claude session，目前只在合成 JSONL 上测通，不宣称实时端到端集成已认证。

## 4. Persistence Model

每个 `RUN-<id>` 一个 append-only `events.jsonl`，写入前使用独占锁文件防止同时写；每次 append 后 fsync。stale lock 不自动清除，需 operator 查明。封存后 CLI 拒绝继续写入。无需 SQLite 或其他服务。锁与 hash 不是恶意同用户进程下的防篡改边界；原始 Runtime 对照仍是 E4 的关键。

## 5. Event Model

通用 envelope：`event_id, sequence, timestamp, run_id, probe_id, type, source`。事件类型为 `QUESTION_CREATED`、`QUESTION_STATE_CHANGED`、`STATE_TRANSITION_REJECTED`、`ASSUMPTION_CREATED`、`TASK_CREATED`、`TASK_ROUTING_SET`、`GATE_ISSUED`、`GATE_STATUS_CHECK`、`GATE_ANSWERED`、`GATE_CANCELLED`、`GATE_TIMEOUT`。它们是 Harness 记录，不是新 Protocol 对象/状态机。Runtime JSONL 与 Harness 事件分文件保存以保留来源差异；跨来源全序必须凭 Bash 回执/原始工具顺序及 Gate watermark 核实，不凭两个机器时间戳猜测。

## 6. Evidence Trust Boundary

Agent 的 CLI 请求只能证明它向 Harness 请求了某状态；CLI 接受说明前置/迁移检查通过，不能证明业务理由、severity 或 routing 正确。Harness 事件需与原始 Runtime 的 CLI 调用回执交叉核对；若无回执，E4 将该链记为 INSUFFICIENT。`run.json`/`manifest.json` 应由独立 operator 生成；Human Verification 仅来自真实交互 tool_result。`verify.valid_package=true` 只表示包内部哈希/配对检查通过，不等于 Probe PASS 或每条 Agent Claim 已证实。

## 7. Human Gate Semantics

`pending` 表示“截至所记录 byte watermark 未见匹配的真实回答”，不代表 Human 主动拒绝或明确保持沉默。`timeout`、`cancelled`、session 结束也都不构成批准。同步 AskUserQuestion 阻塞 Agent turn；外部 observer 可在其未返回时查询 pending，但 Agent 不能在同一 turn 内完成 P-I 所要求的再次状态检查与随后 BLOCKED 迁移。operator 可观察 Gate 和执行截止，不得代替 Agent 的 Protocol 决策。P-I 因此仍 HARNESS-BLOCKED，除非独立验证接受受控暂停/恢复路径或 Runtime 提供可信非阻塞交互；本轮不虚构该能力。

## 8. Capture Failure Semantics

`capture_status=INCOMPLETE` 包含 source unavailable、prefix changed/truncated、partial JSONL row、session mismatch、unpaired non-Gate event、Gate result 无真实 answers、state sequence/解析失败。即使 `verify` 确认某个不完整 package 的 hash 未变，Validator 也不能从“没有 Read/Edit/Task 事件”推断动作未发生。Gate 未配对单列为 pending 候选，需要真实 tool_use、观察水位和独立复查；不能据此推断 Human silence。

## 9. Tests

执行 `python test_harness.py -v`：13 个 deterministic 测试全部通过，覆盖 append-only 持久化和 sequence、非法迁移拒绝/诊断事件、Question→Assumption 来源、Task routing、Edit 前后顺序、Gate pending/真实 answer 来源、伪造 answer 的 package 检出、Gate 工具错误、采集不完整、manifest/hash、Agent claim 不可信，以及 source prefix 改动。仅用临时合成 JSONL，不触碰历史 A-O。没有第三方依赖。

## 10. Capability Smoke Test

同一测试套件的合成单 run 验证了：run 创建、已知工具事件配对、封存与 SHA-256 校验；OPEN→ASSUMED→ISOLATED 的落盘/查询；Task 创建与 MODERATE routing 回执早于 Edit 的识别，以及逆序的 AFTER_EDIT；真实形状 AskUserQuestion tool_use 到 pending、带 answers 的 tool_result 到 answered；未配对 Read 标为 INCOMPLETE。另以历史 session 的只读字段检查确认 AskUserQuestion 的回答在 `toolUseResult.answers`，不是普通工具结果文字。此为 capability smoke，**不是**任何定向 Probe 的执行或 E4。

## 11. Remaining Limitations

- 尚未用新的实时 Claude session 验证 operator offset、Agent Bash CLI 回执和 seal 的端到端操作；P-D/P-N 不自动从代码存在升级为 READY。
- 同步 Human Gate 使 P-I 无法证明 Agent 在未答期间亲自复查并作后续 BLOCKED 状态迁移；外部观察者的 pending 不等于该行为。
- 单机同用户权限不能强制阻止恶意 Agent 改写 CLI/日志/manifest；需独立 operator 封存和 Validator 将状态事件与 Runtime 回执交叉核对。hash 不是签名。
- `inspect-order` 针对 Claude `Edit`/`MultiEdit` 与 Bash CLI 回执；未通过受控 Runtime 的外部修改不在否定证据范围内。若 Probe 使用其他写入通道，E4 须扩充检查或判 INSUFFICIENT。
- C1 resolver、P-G/P-H 的真实 Spec/Convention 来源均未实现，本轮未创建替代 fixture。

## 12. Probe Readiness

### P-D

PARTIALLY_READY。C3/C4 事件链与 C6/C7 package 已通过合成 smoke；待独立 operator 在新 Claude run 中验证 Bash 状态回执、原始 transcript 完整封存及 E1。然后才能执行 P-D，不能先宣称 Probe PASS。

### P-N

PARTIALLY_READY。C5 Task/routing 与 Edit 顺序检查已通过合成 smoke；仍需真实 run 的 CLI 回执、已就绪 Requirement/审批的独立来源和完整 Runtime 捕获。缺回执时 order=INSUFFICIENT。

### P-I

HARNESS-BLOCKED。C2 外部 observer 可记录真实 prompt/pending/answer，但同步 AskUserQuestion 阻断 Agent 在未答期间查询并转入 BLOCKED 的完整行为链。不能由 operator 代 Agent 完成 P-I 的核心动作。

### P-G

HARNESS-BLOCKED。C1 out of scope，真实 resolver 缺席。

### P-H

HARNESS-BLOCKED。C1 缺席，且所需可信双源/Formation 不在 Batch 1。

## 13. Protocol Impact

NONE。只持久记录现有 Question/Assumption/Task/Gate 语义；未增加 Protocol Core Object、状态机、Registry 或修改冻结文档。当前没有由实现证据证明的新 Protocol Gap。

## 14. Git Scope

外置文件：`phase-1d-execution/harness/harness.py`、`test_harness.py`、`README.md`。仓库内只新增本报告。`CLAUDE.md` 的既有修改与 `AGENTS.md` 的既有未跟踪状态均未触碰。历史 Phase 1D 文件未修改。未提交 Git。

## 15. Final Status

```text
Implementation: PARTIAL
Protocol Modification: NONE
P-D: PARTIALLY_READY
P-N: PARTIALLY_READY
P-I: HARNESS-BLOCKED
P-G: HARNESS-BLOCKED
P-H: HARNESS-BLOCKED
Probe Execution: NOT STARTED
Phase 1E: NOT STARTED
```

下一步应由 Human 决定 P-I 是否允许以外部观察 pending、受控截止和独立 BLOCKED 记录作为目标的有界调整，或另行提供可信非阻塞 Gate 通道；本实现不代替该决定。P-D/P-N 则需独立 operator 做新 run 的能力就绪核查，而后才可启动对应 Probe。到此停止。
