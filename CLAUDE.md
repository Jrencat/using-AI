# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

This is not a software project — there is no source code, build, lint, or test tooling. It is a collection of **Chinese-language prompt templates** for running a 7-stage "Spec-Driven Development" pipeline with a coding AI agent (Claude Code or Codex). The deliverable is the templates themselves; changes here are edits to prompt text, not code.

## File map

- `claude研发流水线提示词模板.md` — the Claude Code / Claude web variant. Uses `/opsx:*` slash commands for OpenSpec operations (stage 3 change init, stage 7 archive).
- `codex研发流水线提示词模板.md` — the Codex / generic-agent variant. Functionally identical, but forbids slash commands — OpenSpec change creation and archiving must be spelled out in natural language instead.
- `examples/填写示例.md` — a fully filled-in example (虚构的"订单管理" module) showing variable substitution and the resulting output file tree.
- `README.md` — project overview, the risk-isolation pipeline diagram, and the variable reference table.

**These two template files are structurally parallel: each has the same 7 stage sections in the same order.** When editing one, check whether the same change (rule tweak, wording fix, output-format change) needs to be mirrored in the other. The *only* intentional divergence between them is slash-command usage.

## Architecture: the 7-stage pipeline

Each stage is a **self-contained prompt block** meant to be pasted into a fresh AI conversation turn, one stage at a time, with human review gating progress to the next stage. The stages are not meant to run in one continuous session.

1. **需求分析 & QA 生成** — reads requirement/design docs, produces `产品需求问题.md` + `技术问题.md` (a QA board with a status machine `❌ 待确认 → 🔄 追问中 → ✅ 已关闭`). IDs (`PD-XXX`, `TECH-XXX`) are permanent, never reused or renumbered. Re-running this stage must incrementally merge into existing QA files, never overwrite them.
2. **Spec 设计 + 自我审查** — produces the **single source of truth** Spec (`{{SPEC_FILE}}`) plus a self-review report. Only `✅ 已关闭` QA items become normative spec content (chapters 1-8); anything still open is downgraded into Spec chapter 9 (`假设与待确认列表`) as an `ASSUM-XXX` with an explicit default/fallback behavior.
3. **OpenSpec Change 初始化** — turns Spec chapters 1-8 into an OpenSpec change (`proposal.md`, `design.md`, `specs/*`). Chapter 9 assumptions are carried into a dedicated "Pending Assumptions" section and must never be turned into buildable specs.
4. **Tasks 拆解** — produces `tasks.md`. Any task tied to a pending assumption is downgraded to `P2` and explicitly tagged with its `ASSUM-XXX` dependency. Features living only in the Pending Assumptions section get no tasks at all (absolute circuit-break).
5. **代码实现** — implements one task at a time, strictly within that task's declared file Scope. A task that is `P2` or carries an `ASSUM-XXX` dependency must be blocked with an explicit warning and wait for human authorization before any code is written.
6. **测试生成 + 自愈闭环** — produces `test_cases.md`, then runs tests one at a time with a bounded self-heal loop (max 2 fix attempts per case). Failures traced to an unresolved assumption become `⚠️ 风险挂起` (risk-pending), not a failure — self-heal must never invent business logic to make these pass.
7. **最终审计 + 归档** — final audit against the Spec, produces a Pending Tech Debt ledger for anything left in `⚠️ 风险挂起`/`ASSUM-XXX` limbo, and only archives when there's no unauthorized implementation of pending/P2 logic.

**The throughline**: anything not explicitly confirmed by a human in stage 1 is never allowed to quietly become working code. It gets tagged, demoted, isolated into its own document section, and blocked at each subsequent stage until a human closes the loop.

## Variable convention

Every template starts with a substitution table (`{{PROJECT}}`, `{{MODULE}}`, `{{MODULE_SLUG}}`, `{{VERSION}}`, `{{REQ_DOCS}}`, `{{DESIGN_DOCS}}`, `{{QA_DIR}}`, `{{SPEC_FILE}}`, `{{REVIEW_DIR}}`, `{{CHANGE_NAME}}`, `{{CHANGE_DIR}}`, `{{TASK_PREFIX}}`, `{{BACKEND_LAYERS}}`, `{{FRONTEND_LAYERS}}`). When adding a new variable to a stage prompt, add it to the substitution table at the top of *both* template files and to the table in `README.md`, and add an example value to `examples/填写示例.md`.

## Editing conventions specific to this repo

- Keep the two template files structurally mirrored — same section headers, same stage numbering, same ID prefixes (`PD-`, `TECH-`, `ASSUM-`, `{{TASK_PREFIX}}-`, `TD-`).
- Don't collapse the per-stage prompt blocks or merge stages — stage isolation (one prompt, one human review gate, then the next) is the entire point of the design; see README's 常见问题 section for the rationale.
- The "全局强制规则" (global mandatory rules) block at the top of each stage prompt is what prevents scope creep into other stages — treat it as load-bearing, not boilerplate, when revising a stage.
- Status/severity vocab is fixed and used verbatim throughout: problem status `❌ 待确认 / 🔄 追问中 / ✅ 已关闭`; severity `BLOCKER / MAJOR / MINOR`; task priority `P0 / P1 / P2`; test result `✅ 通过 / ❌ 失败 / ⚠️ 风险挂起`; final verdict `✅ / ⚠️ / ❌`. Don't introduce new status vocabulary without updating it everywhere it's referenced across both templates and the README.
