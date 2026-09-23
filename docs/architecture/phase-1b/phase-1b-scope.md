# Phase 1B Scope — v0.1 (Phase 1B-0)

> Status: DESIGNED / SCOPE-ONLY. No Runtime, CLI, MCP, SDK, Policy Engine, or Evidence Engine implemented. No business code touched. This document defines how the Pilot (`pilot-selection.md`) will be investigated and evaluated, and what Phase 1B is/is not allowed to do.

## 1. Phase 1A Baseline — Confirmation

All six frozen Phase 1A documents were re-read in full during this phase: `protocol.md`, `state-model.md`, `routing.md`, `evidence.md`, `legacy-mapping.md`, `adr/adr.md`, `simulation.md`. Cross-checked against each other and against this phase's own real-project findings.

**Result: no internal contradiction, factual error, or violation of a frozen decision was found.** No `PHASE_1A_CONFLICT` is raised. Phase 1A remains FROZEN and unmodified.

## 2. Investigation Bound — Design (Section 4 of the governing instruction)

The governing instruction explicitly rejects settling for a single simplistic mechanism ("max 20 files," "max 5 minutes"). Five signals were analyzed for whether they should combine, and how:

### 2.1 The five signals

| Signal | What it measures | Alone, why insufficient |
|---|---|---|
| **Investigation Budget** | A rough ceiling on tool calls / files touched | Gameable both ways: an agent can burn the budget on irrelevant files and call it "done," or hit the ceiling before covering a Critical Boundary category and stop prematurely. Budget answers "how much effort was spent," never "was the investigation actually sufficient." |
| **Evidence Sufficiency** | Whether each relevant Boundary Discovery category (`protocol.md` §7: Scope/Data/Permission/Transaction-Irreversibility/Integration/Compatibility) has been addressed — resolved by Evidence, or explicitly determined not-applicable | This is the real "done" signal, but has no natural stopping rule on its own for categories that are ambiguous or where "sufficient" evidence is itself a judgment call — it needs a budget as a backstop against endless refinement. |
| **Information Gain / diminishing returns** | Whether the last few investigation steps produced any *new* fact relevant to a Boundary category | A genuinely useful heuristic (an agent re-reading files it already read, or wandering into unrelated code, should stop) — but currently **unproven** as a signal an agent can self-assess reliably; this Pilot is explicitly a chance to observe whether it's usable at all, not to enforce it as a rule yet. |
| **Scope boundary** | A fixed perimeter investigation should not cross (e.g., "frontend only, no backend/DB") | Answers "where," not "how much" or "when to stop" — necessary but not sufficient alone; an agent could stay perfectly in-scope and still investigate forever, or stop far too early. |
| **Escalation trigger** | Specific conditions that force a stop-and-ask regardless of budget/sufficiency state | The actual fail-closed backstop — without this, an ambiguous case (contradictory evidence, a genuine business unknown, unavailable tooling) has no defined exit besides "keep investigating," which contradicts Fail-Closed (`protocol.md` §9). |

**Conclusion**: no single signal above is sufficient alone, and the governing instruction's skepticism is correct. The five signals are not redundant — they answer different questions (how much / is it enough / is it still productive / where / when to stop-and-ask) and Phase 1B should combine them rather than pick one.

### 2.2 Phase 1B-minimal implementable scheme (not a full Investigation Engine)

This is a **working procedure the agent narrates and follows during the Pilot**, not code, consistent with the Phase Boundary (no Investigation Engine implementation permitted this phase):

1. **Scope boundary (hard, stated up front)**: for this Pilot, investigation stays within `vilims-admin` (frontend only). No backend Java/`vilims` service code, no DB schema investigation — HANDOFF.md itself already states no backend change was made ("未跑 `mvn compile`（无后端改动，纯前端功能）"); crossing this boundary is itself an Escalation Trigger (see #4).
2. **Evidence Sufficiency as the primary stop signal**: investigation is considered sufficient once each row of the Investigation Surface table (`pilot-selection.md` §C) has either (a) a cited real-Evidence answer, or (b) an explicit "not applicable, because ___" note — not merely "budget exhausted."
3. **Budget as a soft circuit-breaker only**: a generous, unenforced target — investigation should typically resolve within a small number of tool calls given the Pilot's narrow scope (this phase's own investigation of the *broader* project used roughly a dozen Read/Grep/Glob calls to find and fully characterize HANDOFF.md; the Pilot's own re-investigation, being narrower, should need fewer). If it runs far past that without reaching Evidence Sufficiency, that itself becomes an Escalation Trigger, not silent continued investigation.
4. **Escalation triggers (any one forces a stop-and-ask, not more investigation)**:
   - A Critical/business-decision unknown is found (per `protocol.md` §6 hard override) — always escalates, no amount of further investigation licenses inferring it.
   - Contradictory evidence is found (e.g., HANDOFF.md claims the orphan file is still pending, but `Glob` shows it absent) — escalates as a `Question`, is not silently resolved either direction. This exact situation already occurred during this phase's own investigation (see `pilot-selection.md` §1) and is the concrete, real precedent motivating this rule rather than a hypothetical one.
   - Required tooling is unavailable (this phase's own Bash rate-limit is the real precedent) — escalates/pauses rather than being silently skipped or worked around in a way that produces weaker Evidence than intended.
   - Investigation would cross the Scope boundary (#1).
5. **Information Gain tracking (observational only, not enforced)**: the Pilot should log, in its narration, whether each investigation step produced new Boundary-relevant information. This is explicitly a data-gathering exercise for Phase 1B to assess later — whether this is a usable self-assessed signal is `UNPROVEN` and not claimed otherwise here.

No numeric formula is defined anywhere in this scheme, consistent with `routing.md` §2's and ADR-004's rejection of fake scoring for a structurally similar problem (Complexity tiering) — the same reasoning applies here: a qualitative, evidence-cited procedure the agent must narrate, not a score.

## 3. Current Workflow vs. Target Workflow vs. Human Touchpoints (Section 7)

### 3.1 Current Workflow (what the human must do today)

Two real variants exist, both evidenced:

**(a) Generic Legacy 7-stage workflow** (per the governing instruction's own example chain, matching this repo's actual templates): 选择 Prompt → 判断走哪些 Stage → 提供需求/设计文档 → 审核 QA → 审核 Spec → 生成 Tasks → 授权实现 → 测试 → 审核结果. Every step requires active human judgment and action; nothing is inferred or investigated autonomously (Phase 0's confirmed finding: Requirement Intelligence and Adaptive Routing are both `MISSING` as agent behavior in Legacy).

**(b) This Pilot's actual evidenced current workflow** (real, per HANDOFF.md's own existence and closing line): user gives feedback/correction (e.g., a screenshot pointing out a wrong button position) → agent implements within a session → agent **writes a HANDOFF.md** summarizing state, decisions, and a pending-verification checklist, because the session is ending → HANDOFF.md ends with "建议现在执行 /clear" → the human must, in a **later, separate session**, manually re-read HANDOFF.md, manually decide what still needs checking, manually perform the 6-item browser walkthrough, manually judge whether the orphan file is truly safe to delete, and manually re-invoke the agent to continue. This is a real, already-practiced session-continuity pattern distinct from (but philosophically adjacent to) the Legacy 7-stage pipeline — and it is exactly the workload this Pilot's Target Workflow should be measured against.

### 3.2 Target Workflow (what the Protocol should let the Agent do autonomously)

Intent ("confirm this feature can be closed out") → Investigation (bounded, per §2.2 above — independently re-derive the Investigation Surface rather than being handed it) → Question generation (only for genuine unknowns — e.g., the orphan-file contradiction) → Routing (agent proposes MODERATE tier, proposes skipping Stage 1-4 ceremony, recommends keeping Stage 6-equivalent testing — see `pilot-selection.md` §E) → Execution (verification actions only: re-run eslint, check file existence/git history; no business-code change without a Human Gate, per Decision 3) → Testing (the 6-item walkthrough — see open sub-question in Decision 4 on whether this can be scripted) → Evidence (collected per item, tier stated) → Evaluation (non-test claims routed to Human per Decision 4) → a single consolidated report to the human, instead of the human having to reconstruct all of the above themselves from HANDOFF.md.

### 3.3 Human Touchpoints (explicit)

**Agent may do alone** (per `protocol.md` §8, unchanged): investigate, re-derive the Investigation Surface, run eslint, compare current repo state to HANDOFF.md's claims, draft Questions, propose a Complexity tier and routing recommendation, draft the final report.

**Must go to the human**: any actual code/file change (including the orphan-file deletion — already real-precedented as blocked, see `pilot-selection.md`); the final PASS/FAIL determination on every non-test Claim (Decision 4); resolution of the orphan-file contradiction if investigation alone cannot settle it; any Critical/business unknown; confirmation of the 6-item walkthrough itself, unless and until Decision 4's open sub-question (scripted substitute) is separately resolved.

## 4. UNPROVEN Labeling (Section 8, mandatory)

The following are explicitly **not** claimed as proven by this phase, and must remain labeled `UNPROVEN` until the Pilot actually runs and produces real data:

- That the Investigation Bound scheme in §2.2 actually produces a *sufficient* investigation in practice (vs. one that merely feels bounded on paper). `UNPROVEN`.
- That Information Gain/diminishing-returns is a usable self-assessed signal at all. `UNPROVEN` (explicitly named as observational-only in §2.2 for this reason).
- That routing non-test Claims to mandatory Human confirmation (Decision 4) meaningfully closes the ADR-003 gap rather than just relocating it. `UNPROVEN`.
- **Above all**: that this Protocol reduces the human's active workload of organizing the development process (the governing instruction's stated most-important validation goal, §7) — comparing §3.1(b) to §3.2 above is a plausible narrative, not evidence. No workload-reduction claim in this document or in `pilot-selection.md` may be read as proven. Collecting that evidence is Phase 1B's own goal, not a precondition already met.

## 5. Phase Boundary Recap (what this phase did and did not do)

**Did**: read and confirmed all 6 frozen Phase 1A documents (no conflict found); investigated real projects read-only (filesystem, IDE recent-project history, `git`-tracked docs, `Grep`/`Glob` across `vlims`); selected a real, non-fabricated Pilot; wrote 3 new files under `docs/architecture/phase-1b/`.

**Did not**: modify any Phase 1A file; modify any file in `vlims`/`vilims-admin` or any other real project; implement any Runtime/CLI/MCP/SDK/Policy Engine/Evidence Engine; introduce new Core Objects or refactor the existing 7; integrate OpenSpec/Multica/TypeSafe; rewrite the Legacy 7-stage templates; delete any Legacy risk control; add new architecture layers.

## 6. Final Gate Checklist (Section 10) — self-verification

| Item | Status |
|---|---|
| Phase 1A not rewritten | ✅ — 6 frozen files re-read only, zero Edit calls made to any of them this phase |
| No Runtime implemented | ✅ — no code, only 3 Markdown files written |
| No Auto-Test modification | ✅ — `auto-test` files were not opened or touched this phase |
| No business code modification | ✅ — `vlims`/`vilims-admin` files were only Read/Grep/Glob'd, never Edited or Written |
| Pilot from a real project | ✅ — `vlims`/`vilims-admin`, live client codebase, `pilot-selection.md` §1 |
| Pilot not fictional | ✅ — grounded in real `HANDOFF.md`, real `Glob`/`Grep` findings, real bug ledger search that came back empty for the brief's own hypothetical |
| Human Decisions made explicit | ✅ — 5 decisions in `human-decisions.md`, each with Decision/Recommended Default/Alternatives/Consequence/Why-Human-Authority-Required, none pre-decided by the agent |
| Investigation Bound has a concrete proposal | ✅ — §2 above, 5-signal combination + Phase-1B-minimal procedure, explicitly not a full engine |
| Human Touchpoints explicit | ✅ — §3.3 above |
| Workload reduction not falsely presented as proven | ✅ — §4 above, explicit `UNPROVEN` labels, no contrary claim made anywhere in this file set |
