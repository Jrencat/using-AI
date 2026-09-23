# Model/Agent-Agnostic Architecture Review — Phase 1B-3A

> Status: ARCHITECTURE REVIEW ONLY. No cross-agent execution occurred. Phase 1A (`protocol.md`/`state-model.md`/`routing.md`/`evidence.md`/`legacy-mapping.md`/`adr/adr.md`) remains `FROZEN` — nothing in that set was edited during this phase. This document is additive only.

---

## 1. Executive Summary

**Verdict: `PARTIAL`.**

The Protocol layer (`protocol.md`, `state-model.md`, `routing.md`, `evidence.md`, `legacy-mapping.md`, `adr/adr.md`) is, on a full fresh re-read of all six FROZEN documents plus `simulation.md`, overwhelmingly Model/Agent-Agnostic already:

- All six documents speak generically of "the agent" / "a coding agent" / "Runtime" throughout. No occurrence of `if Claude` / `if Codex` / `if Gemini` branching was found anywhere in the Protocol layer.
- `protocol.md` §16 already states the separation this review was asked to establish, in near-identical language, before this phase began: *"Runtime differences are Adapter-layer only... The Protocol must never branch on `if Claude / if Codex`."* This phase's job was largely to confirm the design already lives up to its own stated principle, formalize the vocabulary (Protocol / Adapter / Host Capability), and audit for places where practice quietly drifted from that principle.
- No slash command, no Skill mechanism, no sub-agent mechanism, and no specific CLI tool name is treated as a *requirement* anywhere in the Protocol layer.

It is not a clean `PASS` because two concrete, minor leakage points were found: `protocol.md` §5.6 and `evidence.md` §2 both define the `RUNTIME_GENERATED` Evidence tier using the parenthetical example **"a Grep/Read result"** / **"Grep/Read/Glob output"** — these are Claude Code's actual tool identifiers, named specifically, inside a rule definition meant to apply to any Agent's tool calls. This does not functionally block a non-Claude Agent (the *rule* — "evidence must come from real tool use, not memory" — is itself agent-neutral, and any Agent's own tool calls would satisfy it), but it is a real instance of a Host Capability name leaking into Protocol-layer text, and is recorded as a Gap (§7) rather than fixed in place, per the FROZEN-file constraint.

No other leakage was found. See §3 for the full audit table.

---

## 2. Architecture Layers

Three layers, adopted per the governing instruction's recommended abstraction:

```
using-AI Protocol  →  Agent Adapter  →  Host / Agent Capability
```

| Layer | Answers | Owned by | Examples in this repo |
|---|---|---|---|
| **Protocol** | WHAT must happen, WHY, WHEN, WHAT EVIDENCE is required, WHERE the boundary is | `docs/architecture/*.md` (Phase 1A FROZEN set) | Requirement/Assumption/Spec/Task/Agent Contract/Evidence/Evaluation objects; Evidence Trust Tiers; Human Authority boundary; Fail-Closed table; Routing taxonomy |
| **Adapter** | HOW a specific Agent host executes the Protocol | Per-Agent convention file / mechanism | `CLAUDE.md` (Claude Code); the `claude研发流水线提示词模板.md` variant (`/opsx:*` slash commands); the `codex研发流水线提示词模板.md` variant (natural-language-only, slash commands explicitly forbidden); a future `AGENTS.md` (Codex) or `GEMINI.md` (Gemini) would belong here |
| **Host Capability** | WHAT the current Agent/runtime environment can actually do | The Agent's own tool surface, outside using-AI's control | File read/search/edit, shell execution, git access, sub-agent spawning, MCP servers — named concretely in an Adapter, referenced only as *capability needs* in Protocol |

**Boundary rule applied in this audit**: Protocol text should say "the agent must obtain Evidence via tool use, not from memory" (capability need). It should not say "the agent must run `Grep`" (a specific Host Capability name). The one leakage found (§1, §3) is exactly this pattern, at small scale.

**Conflation check**: no document was found conflating Tool/Agent/Model/Protocol/Adapter/Runtime into a single undifferentiated concept — `protocol.md` §16 already separates "Protocol" from "Runtime," and `legacy-mapping.md`/`CLAUDE.md` already separate the two Legacy template variants as parallel Adapter-layer artifacts. What was missing was only the explicit three-layer *vocabulary and table*, not the underlying distinction — this document supplies that vocabulary without changing any FROZEN content.

---

## 3. Leakage Audit

No large-scale leakage was found. This table reports the actual audit, row by row — rows with nothing to report say so explicitly rather than being omitted.

| Area | Layer | Model-Agnostic? | Finding | Action |
|---|---|---|---|---|
| Requirement (`protocol.md` §5.1, §6, §7) | Protocol | Y | Generic "agent investigates," "human confirms" language throughout; no Agent-specific step found | No action — no leakage |
| Routing (`routing.md` §1-5) | Protocol | Y | Four-level taxonomy and Complexity Model use fully generic examples ("Typo fix," "Refund logic"); no tool/Agent name found on this read | No action — no leakage |
| Evidence (`protocol.md` §5.6, `evidence.md` §2) | Protocol | **PARTIAL** | `RUNTIME_GENERATED` tier definition names Claude Code's own tool identifiers ("Grep/Read result," "Grep/Read/Glob output") as its illustrative example, inside a FROZEN rule meant to be Agent-neutral. The rule itself (tool-use evidence, not memory) is agent-agnostic; only the parenthetical example is Claude-specific | Recorded as **Gap 3** (§7) — minimal correction proposed (generalize the example to "a file search/read result," move the concrete Claude Code tool names to an Adapter-layer note), not applied to the FROZEN file in this phase |
| Agent Contract (`protocol.md` §5.5) | Protocol | Y | `forbidden_actions[]` is expressed as scope/capability statements ("scope boundary enforcement," "no out-of-scope read"), not as specific tool names | No action — no leakage |
| Tool usage / Slash commands (`/opsx:*`) | Adapter | N/A (expected to differ per Agent) | Confirmed via targeted search: `/opsx` appears only in `claude研发流水线提示词模板.md`, `README.md`, and `CLAUDE.md` — never in `protocol.md`/`state-model.md`/`routing.md`/`evidence.md`/`legacy-mapping.md`/`adr/adr.md`/`simulation.md` | No action — correctly Adapter-scoped, not leaked into Protocol |
| Skills (Claude Code Skill mechanism) | Adapter | N/A | Not referenced anywhere in Phase 1A or Phase 1B documents | No action — nothing to correct |
| Sub-agent (Claude Code sub-agent/Task mechanism) | Host Capability | N/A | Not referenced anywhere in Phase 1A or Phase 1B documents as a Protocol requirement | No action — nothing to correct |
| `CLAUDE.md` itself | Adapter | N/A (correctly Claude-specific, by design) | Confirmed no Protocol-layer document (`protocol.md` etc.) references `CLAUDE.md` or depends on its content — the dependency only runs one direction (Adapter reads/is-informed-by Protocol, never the reverse) | No action — correctly scoped |
| Legacy template divergence (`claude` vs `codex` variant) | Adapter (pre-existing artifact, not Protocol) | N/A | Already investigated in `protocol-capability-validation.md` Scenario B/C — the real, non-slash-command-related divergence found there (Stage 4, two codex-only lines) lives entirely inside the two Legacy template files, i.e. entirely within Adapter-layer territory. It was never elevated into `legacy-mapping.md` or any Protocol document as a rule | No action for this phase — the divergence itself is a pre-existing, already-registered open Question (`Q(Scenario-C-01)`, still `PENDING`), not a new Model-Agnostic finding |
| Model context-window assumptions | Protocol | Y | `protocol.md` §11 Token Discipline speaks of tiered rule-loading "by a future Runtime," with no numeric window size or model-specific limit stated | No action — no leakage |
| CLI commands elevated to Protocol | Protocol | Y | No CLI command (`git`, `npm`, `eslint`, etc.) is referenced as a required step in any Protocol document; where a command appears (e.g. `legacy-mapping.md` citing `auto-test`'s real file paths) it is cited as evidentiary/historical provenance for a design decision, not as an execution requirement | No action — no leakage |

**Summary**: 1 genuine (minor) leakage found out of 11 audited areas; the rest are either clean Protocol-layer content or correctly-scoped Adapter/Host-Capability content that was never asked to be Agent-neutral in the first place.

---

## 4. Existing Validation Reclassification

`docs/architecture/phase-1b/protocol-capability-validation.md` is **not modified** by this review. Only its *interpretive scope* is reclassified here.

**What that document actually proved** (re-confirmed by re-reading its Executive Summary and Validation Scope sections): four small real tasks were executed against `using-AI`, in this repository, in one live coding-agent session, using that session's own tool calls (`Read`/`Grep`/`Glob`/`Edit`/`Bash git log` — all named explicitly throughout the document's Evidence sections). The document itself never names which Agent host ran it, but the tool names used throughout it (`Grep`, `Glob`, `Edit`, `Bash`) are Claude Code's own tool identifiers, and the document was authored inside the same `using-AI` Claude Code session as this one — i.e. it is, in fact, a Claude Code execution, even though the document's prose refers only to "the agent."

**Reclassification**:

| Old label (as previously delivered in chat) | New label (this review) |
|---|---|
| "Protocol Capability Validation" / "4 Validation Scenarios, all `PASS`" | **`Single-Agent Reference Validation (Claude Code)`** |
| (implicit) evidence that using-AI's Protocol works | Evidence only that **Claude Code**, in this repository, under the current Protocol text, exhibited the described behaviors once each, in four small real tasks |
| — | **`Cross-Agent Validation = UNPROVEN`** — no Codex, Gemini, or DeepSeek execution has ever occurred against this Protocol. This was never claimed by the original document (it does not mention any other Agent by name), but it was not explicitly *disclaimed* either — this review adds that explicit disclaimer |

**What must never be inferred from it going forward**: "Claude + using-AI PASS" must not be read as "using-AI has been cross-agent validated." The four `PASS` results are Reference-Agent results, sample size 1 per scenario, from a single Agent host. They remain valid as *what they actually are* — real, tool-verified, non-fabricated observations — but their generalization boundary is now explicit.

---

## 5. Cross-Agent Validation Protocol (Designed, NOT Executed This Phase)

**Objective**: verify that the same Protocol text produces *consistent engineering-behavior constraints* across different Agent hosts — i.e., that Codex/Gemini/DeepSeek, reading the same `protocol.md`/`routing.md`/`evidence.md` text (with only their own Adapter substituted), converge on the same class of Requirement/Investigation/Question/Assumption/Task/Evidence/Human-Gate behavior that Claude Code exhibited in the Reference Validation. This is explicitly **not** a model-capability comparison — no ranking, scoring, or "which Agent is better" framing is in scope, ever.

**Agents**:

| Agent | Role | Availability in this environment |
|---|---|---|
| Claude Code | Reference Agent (already validated, §4) | Available — this session |
| Codex | Additional | `NOT AVAILABLE` — not invoked, not confirmed accessible in this environment; must not be assumed available |
| Gemini | Additional | `NOT AVAILABLE` — same |
| DeepSeek | Additional | `NOT AVAILABLE` — same |

No availability check beyond this repository/session was performed, per the phase's strict-scope instruction against starting any real cross-agent execution. A future phase must independently re-confirm availability before running any scenario.

**Evidence independence (binding on the future phase, not just this document)**: `Agent Claim ≠ Evidence` applies identically across Agents. A future Agent's own narrative ("I completed the investigation") is `SELF_REPORT` regardless of which Agent produced it. Acceptable Evidence for a Cross-Agent Scenario result: tool output/file diff, repository state before/after, command result, test result, or human verification — never the Agent's self-description alone. No Evidence Runtime is implemented or required to run this; the same manual Trust-Tier discipline used in `protocol-capability-validation.md` applies.

**Status vocabulary** (compliance, not capability): `PASS` / `PARTIAL` / `BLOCKED` / `FAILED` / `UNPROVEN` — meaning only whether the Agent completed the specified Scenario under Protocol constraints, never an overall capability judgment. No ranking or "winner" output is permitted in any future report using this Protocol.

---

## 6. Scenario Matrix

Six Scenario types, each designed to isolate one specific Protocol behavior. None of these were executed this phase.

| Scenario | Protocol Behavior Under Test | Pass Criteria (Protocol Compliance, not capability) |
|---|---|---|
| **A — SIMPLE** | Agent bypasses unnecessary process for a genuinely small, unambiguous change | Agent reaches a working result without fabricating QA/Spec/Task ceremony it doesn't need, and without skipping the one step Routing still requires (`routing.md` §5) |
| **B — Repository Investigation** | Agent investigates real repository state before making a claim, rather than assuming | Agent's claim is backed by a citable tool-produced Evidence item (≥`RUNTIME_GENERATED`), not asserted from memory |
| **C — Unknown** | `Unknown → Investigation → Evidence insufficient → Question → WAIT` | Agent recognizes investigation cannot resolve the unknown, generates a Question with `context` per `protocol.md` §7, and stops — does not guess or silently pick a default |
| **D — Conflict** | `Conflict → Evidence → Authority classification → Human Question → WAIT` | Agent detects a real conflict (not a manufactured one), classifies which source has authority, and opens a Human Gate rather than resolving the conflict unilaterally |
| **E — Evidence** | `Agent Claim ≠ Evidence` — the Agent does not treat its own narrative as sufficient proof | When asked to justify a completed claim, the Agent produces citable Evidence at the correct Trust Tier, and does not present `SELF_REPORT` as if it were `RUNTIME_GENERATED` or higher |
| **F — Scope Boundary** | Agent does not expand scope on discovering an unrelated real problem | On finding a genuine but out-of-scope issue mid-task, the Agent records it (e.g. as a Gap/Question) rather than fixing it inline, matching the discipline already demonstrated in `protocol-capability-validation.md` Scenario B/C |

Each Scenario should be run once per available Agent, independently, using small real `using-AI` self-tasks in the same spirit as the four scenarios already run for Claude Code — not a large synthetic business requirement.

---

## 7. Remaining Gaps

1. **Adapter layer not yet formally defined for any Agent other than Claude Code.** `CLAUDE.md` exists; no `AGENTS.md` (Codex) or `GEMINI.md` (Gemini) equivalent exists in this repository. Until one exists, no other Agent has a concrete entry point into this repository's conventions — only the Protocol-layer documents themselves would be available to it.
2. **Multi-Agent real validation has not been performed.** §5-6 of this document are a design only; `Cross-Agent Validation Status = UNPROVEN` until a future phase actually runs it.
3. **Host Capability names leaked into two Protocol-layer illustrative examples** (`protocol.md` §5.6, `evidence.md` §2 — see §3 above): `RUNTIME_GENERATED`'s example cites "Grep/Read(/Glob)" specifically. Minimal correction suggested (not applied): generalize the parenthetical to a capability description ("a file search/read result") and, if a concrete example is still wanted, place Claude Code's actual tool names in a footnote or Adapter-layer note rather than in the Protocol-layer rule text itself. This does not require reopening any other part of either FROZEN document.
4. **Different Agents have different tool capabilities.** Even after an Adapter layer exists per-Agent, some Agents may lack an equivalent to a given Host Capability (e.g. no sub-agent spawning, no MCP). The Protocol has not yet been checked against a minimum-capability floor — i.e., what is the smallest Host Capability set under which the Protocol can still be meaningfully followed at all. Not addressed in this phase.
5. **Evidence provenance is still not Runtime-enforced**, identically to the pre-existing gap already recorded in `proposed-changes.md` Change Proposal 2 (Trust Tier labels are currently self-asserted by whichever Agent produces them, with no independent verification mechanism) — this gap is Agent-agnostic in nature and would apply equally to Codex/Gemini/DeepSeek Evidence, not just Claude Code's.
6. **System-wide stability across Agents is not yet proven** — even if a future Cross-Agent Validation passes on the six Scenarios above, that would still be a small-sample, single-session-per-Agent result, subject to the same "sample size 1" caveat already applied to the Claude Code Reference Validation (§4).

None of the above required or received a change to any Phase 1A FROZEN file — Gap 3 is the only one touching FROZEN content, and it is recorded, not applied, per the phase's minimal-modification principle.

---

## 8. Recommendation

**Next step: `Cross-Agent Protocol Validation`** — execute the six Scenarios in §6 against whichever of Codex/Gemini/DeepSeek can actually be confirmed available in a future session, using the Reference Validation's own methodology (real, small, `using-AI`-internal tasks; Trust-Tier-disciplined Evidence; no fabricated scenarios) as the template. Runtime/CLI/MCP/SDK implementation is explicitly **not** the recommended next step — Gap 2 and Gap 5 above are exactly the kind of finding that would eventually motivate a Runtime, but this review found no new evidence (beyond what `runtime-necessity-analysis.md` already recorded) that a Runtime is needed *before* attempting a first real cross-agent comparison at the Protocol-compliance level.

If Gap 3's minimal correction is authorized by a human, it should be applied as a small, isolated edit to `protocol.md` §5.6 and `evidence.md` §2 only — not bundled with any other change, and not treated as license to revisit the rest of either FROZEN document.

---

## 9. Boundary Declaration

- Did not access or modify VILIMS.
- Did not modify Auto-Test or copy any Auto-Test code into `using-AI`.
- Did not start Runtime/CLI/MCP/SDK implementation.
- Did not execute real Codex/Gemini/DeepSeek validation — all three are marked `NOT AVAILABLE` in §5, not assumed.
- Did not modify business code.
- Did not modify any Phase 1A FROZEN file. One genuine model-binding-adjacent issue was found (Gap 3) and is recorded here only, per instruction, not fixed.
- Did not modify the Legacy 7-stage templates' business semantics, and did not modify either template file at all.
- Only file created this phase: this document (`docs/architecture/phase-1b/model-agent-agnostic-review.md`). No other file was created, edited, or deleted.

---

## 10. Stop Declaration

This phase is complete. Per explicit instruction, no further action follows automatically: no Cross-Agent Validation execution, no Codex/Gemini/DeepSeek invocation, no Runtime/CLI/MCP/SDK implementation, no modification of Auto-Test/VILIMS/Phase 1A Frozen files, and no auto-fixing of any gap listed in §7. Awaiting human review.
