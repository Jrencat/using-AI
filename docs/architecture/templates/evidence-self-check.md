# Evidence Self-Check Checklist

> **辅助模板，非强制执行引擎。** 本清单不具备任何自动校验能力，完成勾选**不等于** `VERIFIED` / `PASS`。它只是帮助 agent（或复核者）在宣称一个 Task/Claim 完成前，用结构化问题逼自己区分"我描述过做了什么"和"我有什么可核实的证据"——最终判定仍须遵循 `evidence.md`（`FROZEN`）中已定义的 Trust Tier 与 Fail-Closed 规则。

适用场景：任何 Task 在进入 `EVALUATING` 之前，或任何 Claim 准备被写作"已完成"之前，逐项自查。

---

## Checklist

1. **Claim 是什么？**
   用一句话写清楚具体声称了什么（例如"eslint 无新增报错"，不要写"功能已完成"这种笼统说法）。

2. **Actual Evidence 是什么？**
   实际存在的、可以被别人看到的产物是什么（工具输出、文件内容、日志、截图等）？如果答案是"没有，只是我这么说"，Evidence 为空。

3. **Evidence 来源是什么？**
   这份 Evidence 是由哪次具体的工具调用/命令/观察产生的？能否指出具体的调用或文件路径？

4. **Trust Tier 是什么？**
   按 `evidence.md` §2 的五级分层标注：`SELF_REPORT` / `RUNTIME_GENERATED` / `TOOL_GENERATED` / `INDEPENDENT_VERIFICATION` / `HUMAN_VERIFICATION`。

5. **是否存在独立生成来源？**
   这份 Evidence 是否由 agent 自身叙述之外的来源产生（例如宿主环境记录的调用日志、人类确认），还是完全依赖 agent 自己的转述？

6. **是否只是 Agent 自己声称执行过？**
   如果去掉所有 agent 的文字描述，Evidence 是否仍然存在？如果答案是"不存在"，这条 Claim 实质上只是 `SELF_REPORT`，无论标签写了什么。

7. **如果缺少足够 Evidence，是否应该标记 `INSUFFICIENT`？**
   按 `evidence.md` §2 规则，`PASS` 需要 ≥`RUNTIME_GENERATED`。不满足则应如实标记 `INSUFFICIENT`，不得因为"看起来应该没问题"而放行。

8. **是否存在 Claim 与 Evidence 冲突？**
   Evidence 内容是否与 Claim 所声称的结果完全一致？是否存在部分矛盾、部分未覆盖的情况？

9. **是否应该进入 `INVALID_AGENT_RESULT`？**
   如果 Claim 与 Evidence 明显冲突，或 Evidence 被发现是伪造/张冠李戴，应按 `evidence.md` §3 的 `INVALID_AGENT_RESULT` 语义处理，而不是继续尝试让它"看起来通过"。

---

## 使用限制

- 本清单本身不产生 Evidence，也不提升任何一条 Claim 的 Trust Tier。
- 勾完全部 9 项，结论仍然只是"自查已完成"，不代表 `evidence.md` 定义的 `PASS`/`VERIFIED` 判定已经成立。
- 最终判定权仍按 `protocol.md` §8 / `evidence.md` 的既有规则执行（多数非测试类 Claim 目前仍需 `HUMAN_VERIFICATION`）。
