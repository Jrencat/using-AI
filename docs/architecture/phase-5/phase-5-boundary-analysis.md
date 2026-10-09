# Phase 5 Boundary Analysis (DRAFT)

```text
STATUS:   ANALYSIS ONLY — not a Phase 5 Spec. No implementation, no Run, no test.
PROTOCOL: FROZEN (protocol.md, state-model.md unmodified)
PHASE 1–3: CLOSED   PHASE 4 C1: Gate PASS (BOUNDED), Human spot check ACCEPTED WITH BOUNDED SCOPE,
           committed at 4c65d10. Phase 4 formal closure is a Human Gate decision, not made here.
INPUTS:   HANDOFF.md, phase-4-closeout.md, scope-conformance-evaluation.json (EVAL-PH4-C1-001),
          phase-4-boundary-analysis.md, scope-conformance-contract.md (§8–10, App. A), protocol.md (§5.4, 5.6–5.7, 8, 15, 16),
          phase-3-boundary-analysis.md (§5-B, candidate table), harness/harness.py (read only), local Codex install (structure only)
```

## 1. Question

> After C1, which single next piece of work removes the largest remaining *unevidenced* part of the project's stated identity, at the smallest cost, without opening Protocol/Harness construction?

## 2. Current state and its basis

| Fact | Basis |
|---|---|
| C1 chain proven for one Claude FX-ELIGIBLE run + 143-case synthetic corpus, bounded | `phase-4-closeout.md` §2–3; EVAL-PH4-C1-001 |
| Trust claimed: `TOOL_GENERATED + HUMAN_VERIFICATION` (bounded); Independent Verification NOT DONE | closeout §3, §5 |
| Not verified: FX-BLOCKED real run, repeat runs, real symlinks, byte-level content | closeout §5 |
| Project identity is "Model-Agnostic / Agent-Native"; every real run so far is Claude Code | HANDOFF §A, §D, §E; `phase-2-boundary-analysis.md` ("Claude JSONL only") |
| The C1 Checker's only Runtime-specific input is `runtime.jsonl` `message.content[].type = "tool_use"` count (SC-E4, tool identity not examined) plus `manifest.capture_status`. Everything else is filesystem manifests, Human anchors and `harness_cli` events | Contract §9–10, App. A |
| The Harness capture/seal code is Claude-JSONL-shaped (`message.content` `tool_use`/`tool_result`, `sessionId`) | `harness/harness.py` ~lines 204–243, 308–311 |
| Task `BLOCKED→ELIGIBLE`, `IN_PROGRESS…DONE` have no Harness path; `TASK_STATE_CHANGED` accepts only `DRAFT→ELIGIBLE|BLOCKED` | `harness.py` ~141–150 |
| Codex CLI 0.161.0 is installed; `~/.codex/sessions` holds 112 session files, 92 containing tool-call records (`function_call`, `custom_tool_call` with matching `*_output`). Observed by record **type counts only**; contents not read, schema stability across versions unknown, quota unknown | local structural check, this analysis |

## 3. Candidates

| ID | Problem | Layer | Depends on C1? | Prerequisite | If not done | Verdict |
|---|---|---|---|---|---|---|
| **A. Second-Runtime receipt (C3)** | "Model-agnostic" has zero evidence; C1 gave a nearly Runtime-neutral Checker | Runtime adapter + verification evidence | Yes (receipt content is defined by C1 App. A / SC-E3–E4) | Codex session format (now observed to exist); no Contract change if normalized at adapter layer | Headline claim stays unevidenced | **Recommended** |
| B. Human Authority channel (C2) | Agents must not promote Assumptions or un-block Tasks (Protocol §8) | Harness + Protocol | No | A detectable role boundary: Agent and operator still share one OS account and one CLI (Phase 3 §5-B, unchanged) | Release path for BLOCKED work is undefined, but nothing currently depends on it | Defer; reconsider only if a principal separation can be shown without inventing an auth system |
| C. Independent Verification of C1 (Codex re-derives verdicts from the Contract alone) | Contract, Corpus, Checker share one author — the top recorded limit | Verification evidence | Yes | Codex access | Trust label stays `TOOL_GENERATED + HUMAN_VERIFICATION`; no downstream work depends on a higher label | Additive and optional (Phase 3 precedent); run after A reuses the same Codex access |
| D. FX-BLOCKED real run / repeat run | Closes C1 limits | Agent execution | Yes | Human authorization (already required) | Limits stay stated; corpus already covers BLOCKED-only synthetically and the live run kept `src/report.py` unchanged | C1 hardening, not a new boundary; not first |
| E. Task lifecycle positive path + Evaluation→DONE/RISK_PENDING | Core lifecycle is DESIGNED only | Harness | Partly | Harness state-machine and Evaluation-store decisions | Lifecycle unproven | Harness construction; creep risk; defer |
| F. Resolver, Evidence/Evaluation store, signing/ACL, Contract v2, MCP/SDK/CLI/UI | — | — | — | — | — | Excluded again for the reasons in Phase 4 analysis §3 |

## 4. Recommendation: Phase 5 first work item P5-1

**P5-1 — Codex receipt adapter, offline.** Show that a Codex session can be turned into a Harness-compatible `runtime.jsonl` that the *unchanged* C1 chain can consume, before spending any live Codex run.

Why first:

1. It is the only candidate that addresses an unevidenced core claim and whose main prerequisite (a Codex session format) is available locally now.
2. The C1 Checker is already close to Runtime-neutral, so the gap is a thin receipt layer, not a new verification system. Protocol §16 already states Runtime differences are adapter-layer only.
3. Offline work needs no Codex quota or live run; the live Codex run (P5-2) becomes a small, well-defined follow-up instead of an exploration.
4. It does not alter Protocol, Harness, Contract v1, C1 Contract or any Phase 1–4 artifact.

Why not B: its prerequisite (a detectable Agent/operator boundary) is still absent; it would end `BLOCKED`. Why not C or D first: they raise the label or close limits of C1 but open no new boundary, and no later work waits on them.

### Scope

In scope:

- A receipt mapping from Codex record types to the fields C1 and Harness capture actually read (App. A; capture-gap logic), written as a short spec before code.
- A standalone adapter (new directory `phase-5-validation/`, no import of `harness.py` or `chain_verifier.py`) that reads a Codex session JSONL slice and emits (a) a normalized `runtime.jsonl` in the shape the existing capture reads, and (b) a provenance sidecar: source file hash, per-row raw-line hash, mapping version.
- A small pre-registered negative set written and hash-locked **before** adapter code (Phase 3/4 method).
- Offline tests on synthetic fixtures and on structure-only checks against recorded local Codex sessions.

Out of scope:

- Any live Codex run (P5-2, separate authorization); Independent Verification; FX-BLOCKED.
- Changes to `harness.py`, `chain_verifier.py`, Verification Contract v1, C1 Contract, Corpus, Protocol.
- A general Runtime-adapter framework, plugin system, MCP/SDK/CLI, a second Runtime beyond Codex, or support for Codex features not needed by App. A.
- Committing any content of the user's recorded Codex sessions.

### Acceptance (all must hold)

| # | Condition |
|---|---|
| A1 | Adapter output is deterministic: same input → byte-identical `runtime.jsonl` and sidecar on rerun |
| A2 | Every tool call has a paired output row, or the pair is recorded in `capture_gaps`; nothing is dropped silently |
| A3 | Unknown record types, missing session id, truncated line, duplicate call id and unpaired call each produce the pre-registered gap/`INCOMPLETE` outcome, never `COMPLETE_WITHIN_BOUNDARY` |
| A4 | Each normalized row is traceable to a raw Codex line by hash |
| A5 | Pre-registered negative set (locked before code) matches 100%; mismatches are reported, not edited away |
| A6 | Using the Harness CLI as a black box (`start`, `seal`, `verify`) on a synthetic run, a normalized file is accepted by the same capture analysis used for Claude |
| A7 | `git diff` shows no change to the frozen artifacts listed above |

Failure/limit handling: a Codex format that cannot satisfy A2–A4 is recorded as a Harness/Evidence Gap finding for P5-1, not worked around by guessing; the same failure class twice closes P5-1 as `INSUFFICIENT` (Phase 1D stop rule).

### Responsibility boundary

| Layer | In P5-1 |
|---|---|
| Protocol | Unchanged. No `if Claude / if Codex` branching (§16) |
| Harness | Unchanged. Used only as a black box in A6 |
| Runtime (Codex) | Source of raw rows only; not an evidence authority |
| Adapter | New, standalone; produces *derived* rows plus provenance |
| Agent | Not run in P5-1 |
| Verification | C1 Checker reused unchanged in P5-2, not in P5-1 |

## 5. Risks and dependencies

- **Derived evidence.** Normalized rows are an adapter's transformation of raw rows, not the raw Runtime log. Mitigation: raw hashes and mapping version in the sidecar, fail-closed gaps. Whether such derived rows may carry the `RUNTIME_GENERATED` tier is a Human ruling (H1).
- **Format drift.** Only record *types* were observed (CLI 0.161.0, 112 local files); field-level schema and stability are unknown. P5-1 must read real field shapes itself and record what it finds.
- **Quota/availability.** Does not affect P5-1; affects P5-2.
- **Same-author tooling.** Adapter, mapping and negative set would share one author; label stays `TOOL_GENERATED` at most.
- **Scope creep** toward a universal Runtime framework — blocked by the out-of-scope list.

## 6. Proposed order

```text
P5-1  Codex receipt adapter, offline (this analysis recommends starting here)
P5-2  One live Codex FX-ELIGIBLE run through the unchanged C1 chain   [needs Human authorization + quota]
P5-3  Optional: Independent Verification of C1 by Codex (context-isolated)   [additive]
P5-4  Optional: C1 hardening (FX-BLOCKED, repeat run, real symlink)   [each needs authorization]
Deferred: Human Authority channel, Task lifecycle path, Resolver, store, signing, Contract v2
```

P5-2 would show only that the C1 chain accepts one Codex run's evidence; it would not show Codex behaves like Claude, nor general model-agnosticism.

## 7. Who decides

Execution Agent, under existing rules: directory and file names, the mapping details, negative-case design inside A1–A7, test layout, and recording Gaps.

Human decides:

- **H1** whether adapter-normalized rows may be treated as `RUNTIME_GENERATED` evidence, or whether a Runtime-neutral receipt (a new contract / Harness change) is required instead. P5-1 proceeds under the adapter approach by default; the answer is needed before P5-2 is judged.
- **H2** authorizing P5-2 and its Codex quota/use.
- **H3** whether to formally close Phase 4 (C1 is bounded PASS; this analysis does not depend on that closure).
- **H4** whether P5-3 / P5-4 are wanted.

## 8. Next task

Executor: **Claude Sonnet 5.5 / Claude Code**, working in `D:\renjianxiao\using-AI`.

Goal: P5-1 up to a locked pre-registration — write the receipt mapping spec and the negative set, lock their hashes, then implement the adapter and offline tests against A1–A7, report with evidence, and stop. No live Codex run, no Git write unless separately authorized.

## 9. Limits of this analysis

- Codex format knowledge is structural (record type counts); no content or field schema was read.
- Candidate B and E judgments rest on Phase 3/4 records and a read of `harness.py`, not on new experiments.
- Nothing here changes any Phase 4 conclusion or the HANDOFF; HANDOFF was not edited.
