# Architecture Decision Records — Phase 1A

> Only genuinely contentious decisions are recorded here (per brief §35 — not every design choice warrants an ADR). Four decisions met the bar: each had a real, defensible alternative that was rejected for a stated reason, not a decision with only one reasonable answer.

---

## ADR-001: Fold Question into Requirement, fold Run/Attempt into Task

**Status**: Accepted

**Context**: The ≤7 top-level Core Object constraint requires either genuinely fewer concepts or an honest fold — the brief explicitly forbids dodging the limit via superficial "super object" merging.

**Decision**: `Question` is a child list on `Requirement`; `Run`/`Attempt` is a child list on `Task`. Neither gets independent top-level identity.

**Alternative considered**: Keep `Question` and `Run` as independent top-level objects (9 total), citing that Legacy treats QA as its own file artifact and that `auto-test` treats a Run as an independently-identified, resumable entity (`run-store.mjs`'s `createRun`/`resumeRun`).

**Why rejected**: In this Protocol's usage, a Question has no existence or reuse outside the Requirement that raised it (no cross-Requirement Question references exist anywhere in Legacy or the worked example), and no evidence in this repo shows a Task attempt needs identity independent of its Task (unlike `auto-test`'s Run, which genuinely is resumable/independent because it models live test execution — a different domain). This is a **fold justified by real 1:1-composition**, not a merge to hit a number.

**Consequence**: If a future real case shows concurrent or cross-Task-shared attempts (unlikely given Legacy's explicit "一次只处理一个 task" rule, L394), this decision should be revisited.

---

## ADR-002: Demote Human Gate and Policy from top-level objects to cross-cutting mechanisms

**Status**: Accepted

**Context**: Same ≤7 constraint; Human Gate and Policy are both structurally important (referenced throughout) but reasoning was needed on whether they deserve independent object status.

**Decision**: `Human Gate` is a shared *schema* (mixin) embedded wherever it's triggered (`Requirement.questions[].human_gate`, `Assumption.human_gate`, `Task.human_gate`, `Evaluation.human_gate`) — not a standalone registry. `Policy` is a static condition→action rule table, not a stateful instance object.

**Alternative considered**: A standalone `HumanGate` object with its own ID and lifecycle, referenced by whichever object triggers it (many-to-one), enabling a unified "all open gates" query; a standalone `Policy` object with versioned instances.

**Why rejected**: A Human Gate instance genuinely has no identity or reuse outside its triggering object — no case in Legacy or the worked example shows two different objects sharing *the same* gate instance (unlike Evidence, which is legitimately many-to-many: one Evidence item can support multiple Evaluations). A standalone Policy *object* would imply per-instance state that doesn't exist — Policy is configuration, evaluated fresh each time, matching the brief's own explicit instruction (§22) not to build a Policy engine in Phase 1A.

**Consequence**: A future Harness wanting a unified "list all currently open Human Gates across objects" view must query across objects (Requirement, Assumption, Task, Evaluation) rather than a single table — an accepted cost, not a hidden one.

---

## ADR-003: Auto-Test Boundary — semantic reuse only, explicit GAP declared rather than forced generalization

**Status**: Accepted

**Context**: `auto-test`'s Evidence/Evaluation code (`core/verify.mjs`, `finalize.mjs`) is real, tested, and structurally close to what this Protocol needs for its Evidence/Evaluation objects.

**Decision**: Reuse only the *concepts* (Claim/Evidence/Decision separation, INVALID_AGENT_RESULT-style short-circuit hierarchy, trust-tier framing) as documented in `evidence.md`. No code, package, or shared module. The scope mismatch (auto-test = test-execution claims only; using-AI = broader claim types including "requirement understood," "scope matches Spec") is recorded as an open **GAP**, not resolved by assuming auto-test's model generalizes.

**Alternative considered**: Treat `auto-test`'s `core/` as a shared library and have Evaluation call into it directly for all claim types, since the code already exists and works.

**Why rejected**: This would import test-execution-specific concerns (Playwright run artifacts, screenshot/trace evidence, `case-store.mjs`'s Assertion Gate) into a Protocol that also needs to evaluate claims with no test-execution shape at all (e.g., "did the agent correctly investigate the repository"). Forcing this dependency would either bloat `auto-test`'s scope or produce a leaky abstraction pretending to be general when it isn't — exactly what the brief's §23 warns against ("any real insufficiency in auto-test's model must be flagged as a GAP rather than forced to generalize").

**Consequence**: A future Evaluation implementation for non-test claims has no existing tooling to build on and must be designed from scratch — listed explicitly in the closing report's Human Decisions Required / Gap List.

---

## ADR-004: Routing reaches "Agent-selected," explicitly stops short of claiming "System-enforced"

**Status**: Accepted

**Context**: The brief requires Adaptive Routing to reach at least "Agent-selected" design level while being honest that "System-enforced" is DESIGNED-only.

**Decision**: `routing.md` defines a qualitative Complexity Model and upgrade/downgrade rules that an agent can apply and *recommend* against, with mandatory human confirmation — no numeric auto-routing, no claim that any Runtime currently enforces the routing decision mechanically.

**Alternative considered**: Define a numeric complexity score (e.g. weighted sum of files touched, schema changes, risk flags) that could plausibly be computed by a future Runtime without human involvement, positioning the design closer to "System-enforced."

**Why rejected**: The brief explicitly prohibits fake scoring, and no real evidence in this repo (Legacy prompts, worked example, auto-test) suggests a scoring formula would track actual risk better than the qualitative Boundary-Discovery-driven judgment already used in `evidence.md`/`protocol.md` §7. Claiming a numeric score would overstate rigor that doesn't exist.

**Consequence**: Routing recommendations remain qualitative and require a human-legible `reasoning` field (`protocol.md` §4.2, `task.routing.reasoning`) rather than a machine-comparable score — accepted as the honest tradeoff.
