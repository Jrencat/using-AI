# Adaptive Routing & Complexity Model — v0.1 (Phase 1A Design)

> Status: DESIGNED, NOT IMPLEMENTED. Phase 0 finding this section responds to: Legacy has **no** Adaptive Routing — README.md L132-133 is a human-facing FAQ suggestion ("小改动可以只用阶段 1、2、5"), not agent-driven behavior. This document specifies what a routing mechanism *would* look like; it does not claim one runs today.

## 1. Four-Level Routing Taxonomy

| Level | Who decides which stages/steps run | Status in this design |
|---|---|---|
| Human-selected | A human explicitly tells the agent which stages to run (already possible today, informally, per README FAQ) | `EXISTS` (informal, human-driven, not agent behavior) |
| Prompt-selected | The stage prompt text itself hard-codes what runs (Legacy's current model — every stage prompt is fixed) | `EXISTS` (this is literally what the 7 templates do) |
| **Agent-selected** | The agent evaluates a Requirement/Task against the Complexity Model (§2) and **recommends** a routing decision for human confirmation | `DESIGNED` in this document — not implemented |
| System-enforced | A Runtime/Harness mechanically enforces the routing decision (e.g. refuses to skip a Human Gate) | `DESIGNED` only, explicitly **NOT** claimed as implementable without a Runtime — no such Runtime is in scope for Phase 1A |

Honesty check (per brief §7's requirement not to inflate this): reaching "Agent-selected" means the Protocol defines the *decision procedure* an agent should follow and the *evidence* it must cite when recommending a shortened or expanded path. It does not mean any code exists that runs this procedure automatically — an operator must still read the agent's recommendation and confirm it, same as every other Human Gate in this design. "System-enforced" is listed only to be explicit that this design does not claim it.

## 2. Complexity Model

Four tiers, assigned per-Task (not per-Requirement, since a single Requirement can spawn Tasks of different tiers):

| Tier | Definition | Default stage set | Example |
|---|---|---|---|
| **SIMPLE** | Single file/module, no schema/interface/permission change, fully reversible, no cross-service impact | 需求(轻量) → 实现 → 验证 (skip full Spec/OpenSpec ceremony) | Typo fix, adding a log line, a pure UI label change |
| **MODERATE** | Multi-file within one module, may add a field/endpoint, reversible, no cross-service impact | 需求 → Spec → 实现 → 测试 | Adding a filter to an existing list endpoint |
| **COMPLEX** | Cross-module or cross-layer change, schema change, or new integration | Full 7-stage pipeline | New module (e.g. order-management from `examples/`) |
| **HIGH-RISK** | Irreversible action, money/data/permission impact, or depends on an unresolved Assumption | Full 7-stage pipeline **+ mandatory Human Gate before Task execution**, regardless of tier-default | Refund logic (Case B, `simulation.md`) |

No numeric scoring formula is defined — per the brief's explicit prohibition on "fake scoring." Tier assignment is a qualitative, evidence-cited judgment call the agent must justify in `task.routing.reasoning`, citing the specific Boundary Discovery category (`protocol.md` §7) that drove the tier.

## 3. Upgrade / Downgrade Rules

- **Upgrade: always allowed, at any point.** New Evidence showing higher risk (e.g. discovering the "simple" field change actually feeds a billing calculation) immediately re-tiers the Task upward, re-opens any skipped stage, and re-evaluates eligibility. No confirmation needed to become *more* careful.
- **Downgrade: only with evidence, and never after a Human Gate has already fired or an irreversible effect has already occurred.** A Task cannot be silently downgraded from HIGH-RISK to MODERATE just because implementation turned out to be simple — the risk classification is about the *domain* (money/data/permission/irreversibility), not the size of the diff. Downgrade requires:
  1. explicit new Evidence contradicting the original risk classification (not a re-assessment of the same facts), and
  2. no Human Gate decision has already been recorded for that Task, and
  3. no irreversible effect (e.g. a migration, an external side effect) has already been produced.
- If any of the three conditions fails, the Task stays at its assigned tier or higher — this is the fail-closed default for routing itself.

## 4. Routing Simulation Scenarios (see `simulation.md` for full worked traces)

1. **Reduce-steps**: a SIMPLE-tier Task is recommended to skip full OpenSpec ceremony. Grounded in real repo content (README FAQ). Classified `DESIGNED / PARTIAL` — the recommendation logic is designed, but nothing currently produces or enforces it automatically.
2. **Mid-execution escalate**: a MODERATE-tier Task discovers, mid-implementation, that its change touches a cross-service integration → immediately upgrades to COMPLEX and reopens stages. No matching real repo case exists; classified `DESIGNED / UNPROVEN`.
3. **Complex-to-downgrade candidate**: a COMPLEX-tier Task's implementation turns out trivial; downgrade is evaluated against the three-condition rule above and **rejected** (domain risk unchanged) — used specifically to demonstrate the rule is not just decorative. Classified `DESIGNED / UNPROVEN` (hypothetical, no real repo case).

## 5. Relationship to Legacy README FAQ

The existing "Q：必须走完7个阶段吗？" FAQ answer (README.md L132-133) is the closest real precedent — it already identifies stages 1/2/5 as sufficient for "小改动" (small changes) while insisting stage 2 (Spec) is never skippable, because it is the anchor for the whole risk-isolation chain (L133: "阶段 2……建议保留——它是后续所有阶段的锚点，去掉后风险隔离链条就断了"). This Complexity Model formalizes that same judgment (SIMPLE never skips the Spec-equivalent step) rather than inventing a new philosophy.
