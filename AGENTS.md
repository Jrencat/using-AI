# Repository Guidelines

## Project Structure & Module Organization

This repository contains Chinese-language prompt templates for a seven-stage, spec-driven AI development workflow; it is not an executable application.

- The two root-level `*研发流水线提示词模板.md` files are the primary deliverables: one for Claude/OpenSpec slash commands and one for Codex or generic agents.
- `examples/填写示例.md` shows a completed variable substitution and expected artifact layout.
- `docs/architecture/` contains the separate Agent-Native Protocol design, ADRs, evidence, routing, and phase records.
- `README.md` explains the template workflow and shared variables. `CLAUDE.md` records repository-specific editing constraints.

## Build, Test, and Development Commands

There is no package manifest, build system, linter, or automated test suite. Validate documentation changes by reviewing Markdown rendering and cross-file consistency:

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
