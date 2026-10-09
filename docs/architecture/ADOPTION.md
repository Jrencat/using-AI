# ADOPTION — what a developer can use today

Scope: a short entry point. It states what is usable now and what is not. Normative definitions stay in `protocol.md`, `state-model.md`, `evidence.md`, `routing.md`. Phase status lives in `HANDOFF.md`.

## 1. Usable today (verified within stated limits)

| Capability | How to use | Evidence level |
| --- | --- | --- |
| 7-stage prompt templates (human-gated spec-driven flow) | Paste stage prompts from `claude研发流水线提示词模板.md` / `codex研发流水线提示词模板.md` | Prompt text only; no machine enforcement |
| Protocol vocabulary (Question → Assumption → Task, trust tiers) | Read `protocol.md`, `state-model.md`; use `templates/evidence-self-check.md` | Frozen; design-level |
| Harness state CLI + capture/seal/verify (Claude Code) | `python harness/harness.py ...` (see `harness/README.md`) | 27 + 8 local tests pass; one chain shape; hash-sealed, no signing |
| Scope Conformance Checker (C1) | `phase-4-validation/` tools + `fixture/README.md` | C1 Gate `PASS`, bounded (`phase-4/phase-4-closeout.md`): Corpus v3 143/143 + one FX-ELIGIBLE Live Run + bounded Human spot check. Same-author; `TOOL_GENERATED + HUMAN_VERIFICATION` ceiling; Phase 4 itself not formally closed |
| Codex receipt adapter | `phase-5-validation/codex_receipt/` (mapping v2 is opt-in: `--mapping-version 2`) | P5-1 / P5-1.1 `ACCEPTED — OFFLINE SCOPE`; output stays `TOOL_GENERATED`. P5-2 (one real run) `INSUFFICIENT — CLOSED`: no Checker verdict, not a PASS |

## 2. Minimal adoption path (no new tooling)

1. Run the 7-stage templates with human review at each gate.
2. Where a Question cannot be answered, mark it `ASSUMED` and isolate it as an Assumption; do not let it reach code.
3. A Task tied to an `ISOLATED` Assumption, or `P2`, must not become `ELIGIBLE`. The Harness CLI refuses such a request (`task-transition` exits 1, records a rejection, Task becomes `BLOCKED`). It only judges requests submitted to it; it does not stop an Agent that never uses it.
4. Treat agent output as a Claim. Promote to Fact only with evidence at the right tier (`evidence.md`).
5. Before accepting a code change, compare the changed files with the Task's declared Scope. Manually this is a diff review; the C1 Checker does it mechanically only for a run set up as in `phase-4-validation/fixture/README.md` (baseline, anchors, sealed Claude Code capture).

## 3. Not available (do not assume)

- No production CLI, SDK, MCP server, or runtime. The Harness is a local aid.
- No model-agnostic end-to-end proof: Codex path ended `INSUFFICIENT`; no Checker verdict on a non-Claude run.
- No Independent Verification is claimed anywhere. Phase 3 is `SAME_FAMILY_REVIEW`; Phase 2, 4 and 5 closeouts state it was not done. Best claimed tier is `TOOL_GENERATED + HUMAN_VERIFICATION`, bounded.
- Scope checking is detection only (blind spots: `scope-conformance-contract.md` §7). Agent-submitted state events and other scenarios (e.g. FX-BLOCKED) are untested.
- Governing Spec Resolver, async Human Gate, evidence store, signing: deferred (`HANDOFF.md` §G).

## 4. Where it blocks real use (ranked)

1. Operator-heavy setup: each captured run needs baseline, anchors, and Task events done by hand (`phase-4-validation/fixture/README.md`).
2. Only Claude Code capture is proven end to end.
3. No packaged way to run the Checker on a user's own repo; the Fixture is synthetic.

Any step that closes 1–3 (a runtime, a CLI, a real-Codex re-run) needs a separate Human decision (H2, H4 in `HANDOFF.md`).
