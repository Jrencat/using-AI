# Phase 1B Human Decisions — v0.1 (Phase 1B-0)

> These are business/authority decisions, not technical ones. Technical recommendations are offered below, but each Decision line is left for the human to actually make. None of these have been decided by the agent. Numbering matches the 5 items restated in the governing Phase 1B-0 instruction.

---

## Decision 1 — How to define Requirement Intelligence's investigation bound

**Decision**: Which combination of Investigation Budget / Evidence Sufficiency / Information-Gain / Scope boundary / Escalation trigger (detailed in `phase-1b-scope.md` §Investigation Bound) should govern the Pilot's investigation, and whether a hard numeric safety cap should also be imposed for this first real run.

**Recommended Default**: Adopt the qualitative multi-signal scheme in `phase-1b-scope.md` §Investigation Bound — Budget as a soft circuit-breaker only (not the primary stop signal), Evidence Sufficiency against the 6 Boundary Discovery categories as the actual "done" signal, Scope boundary fixed to `vilims-admin` frontend only (no backend/DB investigation), and 3 concrete Escalation triggers (Critical/business unknown found; contradictory evidence found; tooling unavailable, as already happened this phase with the Bash rate-limit). Track Information-Gain/diminishing-returns narratively as an experimental signal, not yet an enforced rule.

**Alternatives**:
- (a) A single simplistic hard cap ("max 20 files" / "max 5 minutes") — rejected by the governing brief itself as too simplistic, and not evidence-driven (it would stop investigation at an arbitrary point regardless of whether the relevant Boundary categories were actually covered).
- (b) No bound at all, fully open-ended investigation — rejected: contradicts the already-frozen Fail-Closed principle (`protocol.md` §3.6) and Token Discipline intent (`protocol.md` §11).

**Consequence**: Accepting the Recommended Default means the first real Pilot run has no enforced stop mechanism beyond the agent's own narrated discipline — a real, honest limitation (see Attack #1 in `simulation.md`, which already flagged that nothing today prevents an agent from ignoring the design). If the human instead wants a hard numeric safety cap for this first run specifically (even though it's philosophically weaker), that should be stated now, since it changes how the Pilot is briefed before execution.

**Why Human Authority Is Required**: This sets an actual operational safety boundary — how much unsupervised investigation an agent may do against a real client codebase — which is a risk/policy decision, not something ADR-004's precedent (which only rejected numeric scoring for *risk-tiering*, a different question) already settled.

---

## Decision 2 — When to move from document-only validation to a Minimal Runtime

**Decision**: Whether the Phase 1B Pilot executes purely narratively (the agent applies the Protocol's rules by discipline within a normal session, self-reporting compliance, with the human as the actual enforcement backstop) or whether some minimal scaffolding (even something as small as a checklist/state-tracking file) should exist first.

**Recommended Default**: Run the Pilot narratively, with **no Runtime code written** — consistent with this phase's own Phase Boundary (no Runtime/CLI/MCP/SDK/Policy Engine/Evidence Engine implementation permitted). Reassess only after the Pilot surfaces concrete friction that a document-only approach cannot address — and treat that reassessment as a separate, later decision point, not something to pre-build now.

**Alternatives**:
- (a) Build a minimal Runtime now (even a small script or state file) before running the Pilot, so enforcement isn't purely self-discipline — rejected for Phase 1B-0/1B by the explicit Phase Boundary, and premature before even one real Pilot data point exists to justify what shape a Runtime should take.
- (b) Never build a Runtime, validate only through repeated narrative pilots indefinitely — risks reproducing the exact "prose-only enforcement" gap Phase 0 already found in the Legacy templates, without ever closing it.

**Consequence**: Narrative-only execution means the Pilot's own compliance-with-the-Protocol claims are themselves largely `SELF_REPORT`-tier evidence (the agent narrating "I followed the Investigation Bound") — which, by the Protocol's own Evidence rule (`protocol.md` §5.6), would not be sufficient to `PASS` an Evaluation of the Protocol's own effectiveness. This tension is real and is being named explicitly here, not hidden.

**Why Human Authority Is Required**: This is a resourcing/timeline/prioritization decision — how much infrastructure to build before spending effort validating a design — with real cost tradeoffs the agent should not decide unilaterally.

---

## Decision 3 — Whether to use a real project for Pilot first

**Decision**: Confirm using the real, live `vlims`/`vilims-admin` client codebase (specifically the already-documented HANDOFF.md task — see `pilot-selection.md`) as the Phase 1B Pilot target, versus an isolated sandbox/toy repo.

**Recommended Default**: Yes, use the real codebase — but scope the Pilot itself to investigation/verification and, at most, one already-precedented low-risk cleanup action (the orphan-file deletion, itself already gated once by tooling policy), with an explicit rule that **no other business code is touched** without a separate, later human authorization. This is an extra safety margin beyond what Phase 1B-0's Phase Boundary already forbids.

**Alternatives**:
- (a) Create an isolated toy/sandbox repository instead, to avoid any risk to a real client project — rejected: it would require fabricating a requirement to validate against, which the governing instruction explicitly forbids ("必须根据真实项目证据选择").
- (b) Use a different real client project instead (`yhoa`/`ytl`/`lims` were also found as real evidence during this phase's investigation) — rejected for this Pilot specifically: no artifact of HANDOFF.md's quality/completeness (a fully-documented, bounded, already-decided real task with a concrete open verification checklist) was found in those projects during this phase's search.

**Consequence**: A real-project Pilot yields materially stronger Evidence quality (a genuine investigation surface, a genuine Human Gate precedent already encountered — the blocked `rm`) but carries genuine operational stakes: any mistake touches a live client's production-adjacent codebase, not a disposable sandbox.

**Why Human Authority Is Required**: Accepting risk against a real client's codebase — even read-mostly — is itself the kind of decision `protocol.md` §8 reserves to Human Authority (irreversible/high-risk action authorization), applied here at the meta-level of "should this validation exercise touch this codebase at all."

---

## Decision 4 — Who/what temporarily owns Evaluation for non-test Claims

**Decision**: For the Pilot's non-test Claims (e.g., "the 6-item browser walkthrough passed," "the orphan file is genuinely gone," "HANDOFF.md's scope was correctly understood") — where no `auto-test`-equivalent tool exists (the ADR-003 GAP, `adr/adr.md`) — who or what performs the Evaluation reconciliation?

**Recommended Default**: The human (the user) is the temporary Evaluation owner for all non-test Claims during this Pilot. The agent may self-collect supporting Evidence at `RUNTIME_GENERATED`/`TOOL_GENERATED` tiers (Glob/Grep/eslint output), but may not self-Evaluate those claims to `PASS` — every non-test Claim requires explicit human confirmation (`HUMAN_VERIFICATION`) before being treated as closed. One open sub-question worth the human's input: whether a scripted/automated browser check (e.g. Playwright) could substitute for a literal manual click-through for the walkthrough items specifically, which would raise that particular Evidence to `INDEPENDENT_VERIFICATION` tier instead of requiring `HUMAN_VERIFICATION` — this is a testing-methodology choice, not decided here.

**Alternatives**:
- (a) Let the agent self-Evaluate non-test claims using only trust-tier discipline (cite ≥`RUNTIME_GENERATED` evidence, no human step) — rejected: this is exactly the unresolved gap ADR-003 flagged, and self-evaluation with no external check re-introduces the "agent grades its own homework" risk Phase 0 already raised as a concern.
- (b) Defer any non-test Claim entirely until a real Evaluation mechanism is designed — rejected: too restrictive, would prevent the Pilot from validating anything beyond the eslint-shaped Claims, defeating the purpose of choosing a Pilot with real non-test verification work in it.

**Consequence**: Routing all non-test Claims through explicit human confirmation increases the human's review load *during the Pilot itself* — an accepted, bounded cost for the sake of getting real data on a currently-unsolved gap, not a permanent arrangement.

**Why Human Authority Is Required**: This assigns responsibility for judging correctness in a domain with zero automated backing today — `protocol.md` §8 already reserves "Insufficient-Evidence resolution" to Human Authority; this Decision is a direct instance of that reserved category, made concrete for this Pilot.

---

## Decision 5 — Whether it's acceptable that Human-Gate query capability doesn't yet exist

**Decision**: Confirm that, for the duration of this Pilot, the absence of a queryable "list all currently open Human Gates" registry (the accepted cost from `adr/adr.md` ADR-002) is acceptable — i.e., the human must rely on the agent explicitly narrating every Human-Gate-triggering condition as it fires, with no independent cross-check mechanism.

**Recommended Default**: Accept the cost at this Pilot's scale — a single Requirement with a small, bounded set of possible gate triggers (orphan-file deletion, walkthrough failures, non-test Claim sign-off). Revisit only if a later, larger pilot or real usage grows to multiple concurrent Requirements/Tasks, where a missed gate becomes a materially higher real risk.

**Alternatives**:
- (a) Build a minimal gate-registry file now (e.g. a markdown table the agent appends an entry to whenever a gate fires) — rejected as unnecessary infrastructure for a single-Task pilot under this phase's Phase Boundary, though flagged as a cheap, low-risk future addition if scale grows.
- (b) Refuse to proceed with any Pilot until a query mechanism exists — rejected as overly cautious relative to the Pilot's actual size and stakes.

**Consequence**: If a Human Gate condition is ever silently missed due to a narration gap, there is currently no independent mechanism to catch it besides the human's own attentiveness while reading the agent's report — an accepted, bounded risk given the Pilot's small scale.

**Why Human Authority Is Required**: This re-confirms, at a concrete operational scale, a tradeoff ADR-002 already accepted in the abstract. Accepting a design tradeoff in principle and accepting its real consequence for a specific real-codebase Pilot are two different decisions — the second one belongs to whoever bears the operational risk, i.e., the human.
