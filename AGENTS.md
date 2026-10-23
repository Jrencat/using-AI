# Repository Guidelines

## Stage 3 Development Entry

For a natural-language request to implement or fix something, read and follow [docs/workflow/develop.md](docs/workflow/develop.md) once using the current request as the task. This is the model-independent workflow source; host discovery and commands are adapters, not protocol requirements. Discussion and review requests retain their original intent. Follow user instructions and applicable repository constraints; do not reload unchanged rules each turn.

The seven-stage structure and variable rules below govern the original templates when editing or explicitly using them, not every Stage 3 task. Preserve frozen Stage 2 assets and historical conclusions; do not resume Phase 4/5 or load architecture history for ordinary development. The real business pilot is waiting for an actual task; see `docs/workflow/pilot-001.md` only when working on that pilot.

## Project Structure & Module Organization

This repository contains Stage 1 prompt templates, Stage 2 historical Protocol / Harness tools, and the Stage 3 shared development workflow; it is not a business application.

- The two root-level `*研发流水线提示词模板.md` files are the primary deliverables: one for Claude/OpenSpec slash commands and one for Codex or generic agents.
- `examples/填写示例.md` shows a completed variable substitution and expected artifact layout.
- `docs/architecture/` contains the separate Agent-Native Protocol design, ADRs, evidence, routing, and phase records.
- `README.md` explains the template workflow and shared variables. `CLAUDE.md` records repository-specific editing constraints.

## Build, Test, and Development Commands

There is no repo-wide package manifest, build, lint or test command. Historical Python tools have their own tests; do not run those for unrelated workflow documentation changes. Validate documentation changes by reviewing Markdown rendering and cross-file consistency:

```powershell
rg "{{NEW_VARIABLE}}" README.md examples *.md
git diff --check
git diff -- AGENTS.md
```

Use `rg` to find every occurrence of a rule, status, variable, or stage label before changing it. `git diff --check` catches whitespace errors; inspect the complete diff before committing.

## Writing Style & Naming Conventions

Keep content in Markdown and preserve UTF-8 Chinese filenames and terminology. Match nearby heading depth, tables, fenced blocks, and concise instructional tone. Do not rename files merely to make paths ASCII-friendly.

The two main templates must stay structurally parallel: preserve identical stage order, identifiers (`PD-`, `TECH-`, `ASSUM-`, task-prefix IDs, and `TD-`), and output shapes. The only intended difference is OpenSpec slash-command usage. Treat each stage's global mandatory-rules block as load-bearing. Do not invent alternative status, severity, priority, or verdict vocabulary.

When adding a `{{VARIABLE}}`, update both templates, the variable table in `README.md`, and the filled example. Changes to protocol design should cite or update the relevant document under `docs/architecture/` rather than silently changing the legacy template contract.

## Testing Guidelines

Use review-based validation. Confirm links and relative paths exist, variable names are spelled consistently, and mirrored edits appear in both templates. For changes to an architecture decision, check its related ADR, evidence, simulation, or phase record for contradictions.

## Commit & Pull Request Guidelines

Recent history uses concise Conventional Commit-style subjects, for example `docs: 添加 CLAUDE.md 项目说明`. Prefer scoped, imperative messages such as `docs: clarify stage 5 authorization gate`.

Keep pull requests focused. Describe the workflow behavior changed, list every mirrored file updated, and explain any deliberate template divergence. Link related issues or ADRs where applicable. Include rendered Markdown screenshots only when tables, diagrams, or layout changed materially.
