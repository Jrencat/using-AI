# Evidence / Evaluation Design — v0.1 (Phase 1A Design)

> Status: DESIGNED, NOT IMPLEMENTED. See `protocol.md` §5.6-5.7 for object field definitions.

## 1. Claim vs Evidence vs Evaluation vs Decision — strict separation

| Term | Definition | Who produces it | Can it be trusted alone? |
|---|---|---|---|
| **Claim** | An assertion an agent (or human) makes about the state of the world ("this test passes," "the requirement is fully understood") | Agent or human | No — a Claim is not a Fact |
| **Evidence** | A citable, sourced record collected via investigation/tooling/human confirmation | Tooling, investigation, or human | Only at `HUMAN_VERIFICATION` / `INDEPENDENT_VERIFICATION` tiers alone; lower tiers require corroboration |
| **Evaluation** | The reconciliation process that checks a Claim against Evidence | The Evaluation mechanism (agent-run, evidence-gated) | N/A — it is the process, not a fact |
| **Decision** | The output of an Evaluation: `PASS / FAIL / INSUFFICIENT / INVALID_AGENT_RESULT / BLOCKED` | Evaluation | This is the only thing downstream objects (Task, Human Gate) may act on |

This separation is the direct analog of `auto-test`'s real internal architecture, where `checkClaim()` (in `core/verify.mjs`) never accepts a self-reported PASS without reconciling it against stored evidence, and `finalize.mjs`'s `decide()` runs a strict short-circuit hierarchy (`INVALID → BLOCKED → FINALIZED_FAIL → INCONCLUSIVE → FLAKY → FINALIZED_PASS`) rather than trusting the last-reported status.

## 2. Evidence Trust Tiers (5, ordered lowest→highest)

1. `SELF_REPORT` — the agent's own narrative ("I checked and it works"). Necessary for traceability, insufficient alone.
2. `RUNTIME_GENERATED` — produced by the agent's own tool calls (a file search/read result, a file diff). Verifiable by re-running the same tool.
3. `TOOL_GENERATED` — produced by a deterministic external tool (test runner, linter, type-checker, build).
4. `INDEPENDENT_VERIFICATION` — produced by a separate agent/process that did not make the original Claim.
5. `HUMAN_VERIFICATION` — a human directly confirmed it.

**Rule**: `Evaluation.decision = PASS` requires at least one Evidence item at tier ≥ `RUNTIME_GENERATED`. An Evaluation resting solely on `SELF_REPORT` evidence caps at `INSUFFICIENT`, never `PASS`, no matter how confident the Claim's language is.

## 3. INVALID_AGENT_RESULT Semantics (conceptual inheritance, not code reuse)

Inherited concept from `auto-test`'s real `finalize.mjs` (function name and short-circuit ordering observed directly in the local clone at `Auto-Test Skill / core/finalize.mjs` during Phase 0): when a Claim says one thing and higher-or-equal-trust Evidence says another, the Evaluation does not average, defer to the Claim, or silently pick a side — it produces a distinct terminal state (`INVALID_AGENT_RESULT`) that is neither PASS nor FAIL. This is deliberately distinct from `FAIL`: `FAIL` means the work genuinely didn't meet the bar; `INVALID_AGENT_RESULT` means the agent's own report cannot be trusted as an account of what happened, which is a different (and in this Protocol's judgment, more serious) problem — it should trigger re-doing the Evaluation, not just re-doing the Task.

**What is reused**: the concept (Claim≠Evidence produces a distinct non-PASS/non-FAIL terminal), the short-circuit-hierarchy pattern (some conditions override others regardless of order encountered), and the trust-tier framing.

**What is NOT reused**: no function, module, schema, or package from `auto-test` is imported, copied, or referenced at runtime. `using-AI`'s Evaluation object is defined independently in `protocol.md` §5.7 and is not required to match `auto-test`'s `Verdict` type shape field-for-field.

## 4. Auto-Test Boundary — explicit reuse vs. explicit gap

**Reused (semantic only)**:
- Claim/Evidence/Decision separation (`core/verify.mjs::checkClaim`)
- Short-circuit decision hierarchy (`core/finalize.mjs::decide`)
- SHA256-style evidence identity/immutability idea (`core/evidence-store.mjs`) — informed the "Evidence is COLLECTED then only DISPUTED/superseded, never edited in place" rule in `state-model.md` §6
- Retry/flake policy shape (`core/policy.mjs::shouldRetry`) — informed the Task retry-cap rule in `state-model.md` §4, without adopting its actual retry thresholds

**Genuine GAP, not glossed over**: `auto-test`'s Evidence/Evaluation model is scoped entirely to **test-execution verdicts** — a Claim in its system is always "this test case passed/failed," and its Evidence is always test-run artifacts (logs, screenshots, traces, DB assertions per Phase 0's Fork B findings on `core/case-store.mjs`/`evidence-store.mjs`). `using-AI`'s Evaluation object must also judge **non-test claims**: "the requirement is correctly understood," "the implementation matches Spec scope," "the Assumption's default behavior is still valid." `auto-test` has no existing mechanism for these — they are not a natural extension of its Assertion Gate, they are a different claim domain entirely. This is flagged here as an open design gap (`Human Decisions Required` list in the closing report), not force-generalized into a shared abstraction that doesn't actually exist in the real code.

**No dependency formed**: `using-AI` does not import, call, or vendor any `auto-test` module. If real test execution is eventually required, `auto-test` would be invoked as an external Testing Adapter behind the Evidence/Evaluation contract — out of scope for Phase 1A.

## 5. Requirement Intelligence Worked Trace (uses the brief's supplied hypothetical sentence)

Input intent (task-supplied, hypothetical — **not** drawn from real repo history): "修复实验页面刷新后左侧菜单与专题不匹配的问题" ("Fix: after refreshing the experiment page, the left-side menu doesn't match the topic").

Walking the pipeline from `protocol.md` §6:

1. **Repository Investigation** (bounded): would start from files plausibly named around "实验页面" / "左侧菜单" / "专题" (e.g. an experiment-page component, a menu/sidebar component, a topic-selection store/context). **This step cannot actually run in this design exercise** — there is no real target codebase in this repo to investigate (using-AI is a prompt-template repo with no such application code). Classification: `DESIGNED / NOT EXECUTABLE` for this specific sentence, in this specific repo.
2. **Existing Behavior check**: would compare current menu-state derivation logic against the topic/page state on refresh — same caveat, not executable here.
3. **Conflict Detection**: the sentence itself already states a conflict (menu vs. topic mismatch after refresh) — this much is derivable from the sentence alone, no investigation needed: a `Non-Critical`/`Important` factual question ("is the mismatch reproducible on every topic, or only some?") could be raised without investigation.
4. **Boundary Discovery** (`protocol.md` §7): `Scope` (which component owns menu-state derivation) and possibly `Compatibility` (does the fix affect other pages using the same menu component) are the plausible touched categories — this is a structural judgment, not a claim about the real code, since no real code was investigated.
5. **Question Generation**: at minimum one `Important` question is generated without needing investigation — "should the fix re-derive menu state from the topic on every refresh, or only cache-invalidate on topic change?" — because this is a genuine design-trade-off question a repo scan alone would not resolve even if the repo existed.

**Overall classification for this simulation**: `PARTIAL`. The parts of the pipeline that reason from the sentence alone (Conflict Detection, a plausible Question) are `DESIGNED` and can be narrated; the parts that require real repository investigation are honestly marked `NOT EXECUTABLE` in this context, per the brief's explicit instruction not to fabricate investigation results.

## 6. Fail-Closed Evidence Rules (restated from `protocol.md` §9 for this document's completeness)

| Situation | Decision |
|---|---|
| No Evidence cited for a PASS claim | `INSUFFICIENT` |
| Evidence exists but is all `SELF_REPORT` tier | `INSUFFICIENT` |
| Evidence contradicts Claim | `INVALID_AGENT_RESULT` |
| Evidence genuinely shows failure (no Claim/Evidence mismatch) | `FAIL` |
| Evaluation touches an irreversible/high-risk action | `BLOCKED` pending Human Gate, regardless of Evidence quality |
