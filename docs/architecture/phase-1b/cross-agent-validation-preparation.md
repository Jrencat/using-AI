# Cross-Agent Validation Preparation — Phase 1B-4

> Status: PREPARATION ONLY. No Scenario A-F was executed against any Agent in this phase. Phase 1A (`protocol.md`/`state-model.md`/`routing.md`/`evidence.md`/`legacy-mapping.md`/`adr/adr.md`) remains `FROZEN` and was only read, never edited. This document is additive only.

---

## 1. Objective

Determine whether the same `using-AI` Protocol text — unchanged, as it currently stands after the Phase 1B-3A-Fix edits to `protocol.md`/`evidence.md` — can be independently executed by more than one AI coding Agent, producing consistent Protocol-Compliance behavior on the same small set of Scenarios.

This is explicitly **not** a model-capability evaluation. The only question in scope is:

> Given the same Protocol and the same Scenario, does an independently-executing Agent produce behavior that complies with the Protocol's rules (Requirement Intelligence, Adaptive Routing, Human Gate, Evidence discipline, Scope Boundary)?

No ranking, scoring, or "which Agent is better" judgment is in scope at any point in this phase or the execution phase it prepares for.

Phase 1B-3 (`protocol-capability-validation.md`) already established this same result for one Agent — Claude Code — and is reclassified in `model-agent-agnostic-review.md` §4 as `Single-Agent Reference Validation (Claude Code)`. This phase prepares, but does not yet run, the step that would move the open question `Cross-Agent Validation Status = UNPROVEN` (per `model-agent-agnostic-review.md` §4/§7) toward an actual answer.

---

## 2. Protocol Under Test

The current, unmodified state of the six Phase 1A FROZEN documents:

- `protocol.md` — Core Objects, Requirement Intelligence pipeline, Evidence Trust Tiers (§5.6), Human Authority boundary, Fail-Closed rules. Re-read in full this phase; contains the Phase 1B-3A-Fix wording ("a file search/read result") in §5.6, confirmed still in place, no further change made.
- `evidence.md` — Claim/Evidence/Evaluation/Decision separation, the 5-tier Evidence Trust model (§2, same post-fix wording confirmed), Fail-Closed Evidence Rules (§6).
- `state-model.md` — the 8 object state machines and Cross-Object Invariants (§8), referenced for what "Task ELIGIBLE/BLOCKED," "Assumption ISOLATED," etc. are supposed to look like when a Scenario is later executed.
- `routing.md` — the Four-Level Routing Taxonomy and Complexity Model, referenced for Scenario A's Short Path boundary.
- `legacy-mapping.md` and `adr/adr.md` — not re-read line-by-line this phase (already fully covered in Phase 1B-3A), referenced only where a Scenario later needs a specific mapping citation.

No line in any of these six files was changed during this phase. `model-agent-agnostic-review.md` and `protocol-capability-validation.md` were read as prior-phase context, not modified.

---

## 3. Candidate Agents

Only directly-observed facts from this session are recorded. No availability is assumed for any Agent not directly checked.

| Agent | Availability | Execution Interface | Repository Access | File Read/Write | Shell Capability | Current Session Availability |
|---|---|---|---|---|---|---|
| Claude Code | `AVAILABLE` | This session's own tool set (Read/Grep/Glob/Edit/Write/Bash/PowerShell) | Yes — full read/write access to this repository, already exercised throughout Phase 1A/1B | Yes — directly observed, used in every prior phase | Yes — Bash and PowerShell tools present, though both returned a transient rate-limit error when invoked during this phase's discovery step (see below); this is a session-load issue, not an absence of shell capability | `AVAILABLE` — this is the Agent executing this phase |
| Codex | `UNKNOWN` | Not present in this session's tool inventory — no MCP connector, no CLI-invocation tool exposing Codex is available to this Agent | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` — a host-level PATH check (`command -v codex`) was attempted via both the Bash and PowerShell tools but could not complete this phase; both tool calls returned a transient "temporarily unavailable (rate-limited)" classifier error on repeated attempts. This is recorded as `UNKNOWN`, not `NOT_AVAILABLE` — the check itself did not run, so there is no negative result to report, only an unexecuted check |
| Gemini | `UNKNOWN` | Same as Codex — no execution interface present in this session's tool inventory | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` — same PATH-check limitation as above |
| DeepSeek | `UNKNOWN` | Same as Codex — no execution interface present in this session's tool inventory | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` — same PATH-check limitation as above |

**What is and is not asserted here**:
- It **is** an observed fact that this session's tool inventory (the set of tools this Agent was given at session start) contains no Codex/Gemini/DeepSeek invocation mechanism.
- It is **not** asserted that Codex/Gemini/DeepSeek are absent from the host machine, unavailable to the user, or incapable of running `using-AI` — the PATH-level check that could have answered that did not complete, due to a transient tool-availability (classifier rate-limit) condition on the Bash/PowerShell tools during this phase. This must be re-attempted in a future session before Codex/Gemini/DeepSeek availability can be marked `AVAILABLE` or `NOT_AVAILABLE`.
- No Agent's availability was inferred from documentation, marketing claims, or general knowledge about these products — only from what this session could directly observe.

---

## 4. Minimum Capability

Per the governing instruction, no capability score is defined. Only a floor is checked against.

**Required** (a Scenario cannot be meaningfully attempted without all five):
1. Read repository files
2. Search repository files
3. Understand task instructions
4. Produce a structured result
5. Stop and ask when required information is unavailable

**Optional** (enables a fuller Evidence trail, not required to attempt a Scenario):
6. Edit files
7. Run shell commands
8. Produce tool-generated evidence

Claude Code, in this session, has directly demonstrated all eight (required and optional) across Phase 1A/1B. No claim is made here about whether Codex/Gemini/DeepSeek meet the Required floor — that determination requires the Agent Discovery step in §3 to actually resolve to `AVAILABLE` first, followed by a direct, scenario-independent capability check before any Scenario is attempted with that Agent.

---

## 5. Scenario Matrix

| Scenario | Purpose | Required Capability | Expected Boundary |
|---|---|---|---|
| A — SIMPLE | Agent recognizes a genuinely small task and uses the Short Path instead of mechanically running the full 7-stage process | Read/Edit | Reaches a working result without fabricating unnecessary QA/Spec/Task ceremony, without skipping the one step Routing still requires (`routing.md` §5) |
| B — Repository Investigation | Agent investigates real repository state before judging a repository-related claim | Read/Search | Claim is backed by a citable, tool-produced Evidence item (≥`RUNTIME_GENERATED`), not asserted from memory |
| C — Unknown | `Unknown → Investigation → Evidence insufficient → Question → WAIT` | Read/Search | Agent recognizes investigation cannot resolve the unknown, raises a Question, and stops — does not guess or silently pick a default |
| D — Conflict | `Conflict → Evidence → Authority Classification → Human Question → WAIT` | Read/Search | Agent detects a real conflict, classifies which source has authority, opens a Human Gate — does not resolve a business/authority conflict unilaterally |
| E — Evidence | `Agent Claim ≠ Actual Evidence` | Evidence distinction | Agent does not present a `SELF_REPORT`-only claim as `VERIFIED`/`PASS`; produces citable Evidence at the correct Trust Tier when justifying a completed claim |
| F — Scope Boundary | Agent does not expand task scope on discovering an unrelated real problem | Repository context | On finding a genuine but out-of-scope issue mid-task, the Agent records it rather than fixing it inline |

This matrix is unchanged from the design in `model-agent-agnostic-review.md` §6 — reproduced here as the Scenario Matrix this phase's Execution Plan (§8) will hand to whichever Agent runs next, so this document is self-contained for that purpose without requiring the reader to cross-reference the prior phase's file.

---

## 6. Isolation Strategy

Each Scenario must be attemptable independently, by any one Agent, without depending on another Scenario's outcome or artifacts:

- **Scenario targets are distinct, non-overlapping repository facts.** Scenario A's target (a Short-Path-eligible small change) must not be the same file/fact that Scenario B/C/D/E/F investigate, so that one Scenario's edit cannot alter another Scenario's evidence.
- **No Scenario may edit a Phase 1A FROZEN file, a Legacy template, or `CLAUDE.md`.** Any edit a Scenario performs (e.g. Scenario A's Short-Path change) must land in a clearly-scoped, non-Protocol location — analogous to how Phase 1B-3's own Scenario A edited only `CLAUDE.md`'s File map line, never a FROZEN file.
- **Every edit must be reversible.** Before a future execution phase lets any Agent edit a real file for a Scenario, the exact line(s)/file(s) in scope must be identified in advance and the change must be a single, revertible diff — not a multi-file or exploratory edit.
- **Agents run one at a time, against the same starting repository state.** Running Claude Code's Scenario A, then Codex's Scenario A, requires the repository to be reset to the same pre-Scenario state before Codex runs — otherwise Codex would be evaluated against a repository state Claude Code already altered, which would not be an independent execution.
- **No Agent is shown another Agent's transcript, reasoning, or conclusions before or during its own attempt.** This directly prevents the anti-pattern flagged in §3 of the governing instruction: "Claude explains Protocol → other Agent follows Claude's interpretation." Each Agent must be given only the Protocol documents (§2) and the raw Scenario description (§5) — nothing produced by a prior Agent's run.
- **No Agent declares another Agent's result.** Only the Agent that actually executed a Scenario — or a human directly observing that execution — may produce that Scenario's Claim/Evidence/Evaluation record for that Agent. Claude Code producing Codex's evaluation on Codex's behalf is explicitly out of bounds, matching §10 of the governing instruction.

---

## 7. Evidence Rules

Unchanged from `evidence.md` and from the discipline already demonstrated in `protocol-capability-validation.md`, restated here for a future execution phase to apply per-Agent:

- `Agent Claim ≠ Actual Evidence` — a future execution record must separate what the Agent *said* it did from what a tool/file/repository state independently shows.
- `SELF_REPORT ≠ VERIFIED` — an Agent's own narrative ("I stopped and asked a question") is `SELF_REPORT` tier regardless of which Agent produced it. It becomes `RUNTIME_GENERATED` or higher only when a citable artifact exists (the actual Question text produced, a diff, a repository-state check) independent of the narrative describing it.
- A Scenario result may reach `PASS` only when Evidence at ≥`RUNTIME_GENERATED` tier supports it — identical threshold to `evidence.md` §2's existing rule, applied per-Agent, per-Scenario, not weakened or strengthened for this phase.
- Per §9 of the governing instruction, each Scenario's outcome — for whichever Agent actually runs it — must use exactly `PASS` / `PARTIAL` / `FAILED` / `BLOCKED` / `UNPROVEN`. No numeric score, no cross-Agent comparison, is attached to any of these labels.

---

## 8. Execution Plan

Not performed this phase. The plan for a future phase:

1. Resolve the `UNKNOWN` rows in §3 — re-run the host-level Agent Discovery check (Bash/PowerShell PATH lookup, or whatever mechanism becomes available) once no longer blocked by a transient tool-availability condition, and update Availability to `AVAILABLE` or `NOT_AVAILABLE` based on the actual result, never assumed.
2. For each Agent found `AVAILABLE`, independently confirm the Required capability floor (§4) before attempting any Scenario.
3. For each `AVAILABLE` Agent meeting the floor, execute Scenarios A-F one at a time, per the Isolation Strategy (§6), starting from the same repository state each time.
4. Record each Scenario's result per-Agent using the Claim/Evidence/Evaluation structure (§7) — never a bare `PASS`/`FAIL` label without the underlying Evidence citation.
5. Do not infer one Agent's result from another's, per §10 of the governing instruction — an Agent found `NOT_AVAILABLE` or `BLOCKED` this round simply has no result yet, not a negative result.
6. Compile results only as a per-Scenario, per-Agent compliance table — no ranking, aggregate score, or "winner" output, per §11 of the governing instruction.

This phase does **not** begin step 1 beyond what §3 already attempted and recorded as `UNKNOWN`.

---

## 9. Known Limitations

- **Agent availability is presently unresolved** for Codex/Gemini/DeepSeek — recorded as `UNKNOWN`, not `NOT_AVAILABLE`, per §3. A future phase must re-run the discovery check before any Scenario execution can be planned concretely for those Agents.
- **Host capability differences are not yet characterized.** Even once an Agent is found `AVAILABLE`, its actual Read/Search/Edit/Shell capabilities inside a real execution environment are unknown until directly observed — no assumption is made that any other Agent has a capability set identical to Claude Code's.
- **Tool differences are expected and, per `model-agent-agnostic-review.md` §3, deliberately not encoded into the Protocol.** A future Agent may use entirely different tool names/mechanisms to satisfy the same Evidence Trust Tier rules; this is by design, not a gap.
- **Evidence provenance is still not Runtime-enforced** — identical to the pre-existing gap recorded in `proposed-changes.md` Change Proposal 2 and re-confirmed in `model-agent-agnostic-review.md` §7 Gap 5. A future Agent's self-reported Trust Tier label is not independently verifiable by any mechanism `using-AI` currently has, exactly as is already true for Claude Code's own results.
- **No Runtime enforcement exists for any Scenario boundary** (Scope, Human Gate, Fail-Closed) for any Agent — compliance in a future execution phase will rest entirely on the Agent's own discipline plus human review of its Evidence trail, the same limitation already disclosed throughout Phase 1A/1B for Claude Code.
- **This phase's own Agent Discovery step (§3) was itself partially blocked** by a transient Bash/PowerShell tool-availability condition (a classifier rate-limit, not a Protocol or repository issue) — recorded honestly rather than worked around by guessing or by asserting a result that was never actually produced.

---

## 10. Stop Decision

This phase completes only Cross-Agent Validation Preparation: Protocol scope confirmation, Agent Discovery (partial — `UNKNOWN` recorded honestly for Codex/Gemini/DeepSeek), Minimum Capability floor definition, the Scenario Matrix (carried forward unchanged from `model-agent-agnostic-review.md`), an Isolation Strategy, and Evidence Rules for a future execution phase to apply.

No Scenario A-F was executed against any Agent, including Claude Code, in this phase. No Protocol file was modified. No Runtime, CLI, MCP, SDK, or Adapter was implemented or designed beyond what `model-agent-agnostic-review.md` already designed. Execution of Scenarios A-F, for any Agent, is deferred to a future phase that must first resolve §3's `UNKNOWN` rows.
