# Phase 1C — Implementation Design Handoff

> Status: HANDOFF SNAPSHOT ONLY. No Protocol file (`protocol.md` / `state-model.md` / `evidence.md` / `routing.md`) has been modified as of this document. This file records design conclusions reached in conversation; it does not itself implement anything.

---

## A. FROZEN / APPROVED

The following design conclusions have been through their respective audit/consistency rounds and are not open for re-litigation without an explicit new governing instruction:

1. **Gap 1 — Decision Boundary**: Human-must-decide is evaluated as an independent first branch, ahead of Finding/affects-correctness checks, ahead of Existing-Spec-resolution checks, ahead of the §6 severity fallback.
2. **Finding semantics**: a Finding is distinct from a Question/Assumption; it does not by itself trigger Human Gate unless it affects correctness or crosses a Human-must-decide category.
3. **Human Gate scope**: the Human Gate mixin (`trigger, context, decision, authority, effect, audited_at`) attaches only to its four existing points — `requirement.questions[i]`, `assumption`, `task`, `evaluation` — no fifth attachment point has been added.
4. **Gap 1a — Convention Formation chain (frozen shape)**:
   ```text
   Historical Precedent → Evidence → Convention Candidate → Human Gate →
   Explicit Formation Confirmation → Convention semantic established
   ```
5. **Human Confirmation requirement**: a Convention cannot exist without an explicit Formation Confirmation recorded in a Human Gate's `decision` (with `authority` + `audited_at`).
6. **Convention Scope requirement**: Formation is invalid without an explicit, bounded Scope statement.
7. **Formation Evidence requirement**: Formation is invalid without re-locatable Evidence (an `Evidence.id` or equivalent re-checkable pointer) — an unlocatable narrative phrase does not qualify.
8. **`ANSWERED ≠ Convention`**: `Question.status = ANSWERED` is a Question lifecycle result only. The Convention semantic is sourced from `Question.human_gate.decision` containing an explicit Formation Confirmation, never from status alone.
9. **Safe Default vs Assumption — permanent separation**: `safe default → Evidence-backed Known` never routes through `Assumption`. `Assumption` creation is gated exclusively on `(created from an ASSUMED Question)` (`state-model.md` line 34); the Non-Critical/Convention-unavailable branch explicitly has "no Question created" (`protocol.md` line 158), which directly contradicts any Assumption-based fallback for this branch.
10. **Gap 2 — Complexity semantics**: Complexity (`SIMPLE/MODERATE/COMPLEX/HIGH-RISK`) is a per-Task property only, assigned at Task-creation time; a pre-Task Boundary Discovery hit becomes at most a "Complexity upgrade signal" (`protocol.md` §7 line 168), not a Complexity assignment itself.
11. **No new Convention Core Object / State Machine / Runtime Entity / Registry**: every Formation/Challenge/Discovery design produced so far reuses existing objects (`Question`, `Human Gate` mixin, `Evidence`, `Spec`) — no new object, state, or registry has been introduced or approved.
12. **Challenge — basic direction (frozen shape)**:
    ```text
    Contradicting Evidence → Evidence.DISPUTED → New Question
    (context cites the DISPUTED Evidence.id and the original
    Convention-confirming Question.id) → Human Gate → disposition
    (Keep / Narrow Scope / Invalidate)
    ```
    No `Convention.CHALLENGED` / `Convention.INVALIDATED` / `Convention.APPROVED` state exists or has been proposed as final.

---

## B. HUMAN-DEFINED RULES

The following are Human-Defined Rules layered on top of the existing Protocol object model. They are **not** Existing Protocol Rules — `protocol.md` / `state-model.md` / `evidence.md` / `routing.md` do not state them; they were established by explicit Human Authority decision and subsequent targeted design rounds in this conversation.

- Convention Formation requires Human Confirmation (Agent may discover a Candidate, collect/cite Evidence, and suggest Scope — Agent may never confirm a Convention, and may never unilaterally decide Keep / Narrow Scope / Invalidate on Challenge).
- Convention requires bounded Scope (no unscoped/global-by-default Convention).
- Convention Formation requires re-locatable Evidence (not an unlocatable narrative claim).
- Convention cannot override higher authority — the six-item Information Priority ordering (`Repository Evidence > Existing Spec > Project Convention > Existing Tests > Safe Assumption > Human Question`, `protocol.md` line 151) is unchanged; a Convention persisted into Spec is governed by Spec's own approval semantics from that point, not by Convention's own ranking.

---

## C. CURRENT STATUS

The single open issue not yet carried into formal Protocol Implementation:

```text
Convention Discoverability Gap
```

**Discoverability R2 has been completed** (design-only; no file modified). R2 confirmed:

1. `Requirement.questions[]` has no defined historical Discovery entry point — no Authoritative File states that a future Requirement Intelligence pass searches historical Requirement objects.
2. `Question` has no independent Discovery rule of its own — it inherits Requirement's (absent) persistence/discovery guarantees.
3. `Spec` is the strongest existing persistence candidate — but Spec-entry for `ANSWERED` content is stated as *eligible*, not *obligatory* (`protocol.md` §5.3), and Spec's stated authority ("referenced by `Task.scope` as the sole authority") is explicit only for Task scope, not for the Requirement Intelligence Convention-check step.
4. The `Existing Behavior / Architecture / Convention check` pipeline step (`protocol.md` line 139) already exists as a named step, but does not name a search target/location — connecting it to Spec is Direct Inference, not textual fact.
5. Two connective rules are currently missing (not missing objects):
   - Human-confirmed Convention content must enter the governing Spec.
   - The Convention-check step must read the governing Spec for previously-confirmed Conventions.

**Note**: R2 is a design conclusion only. No formal Protocol file has been modified to reflect it.

---

## D. DISCOVERABILITY R2 — FROZEN RESULT

**Final Result**: `DISCOVERABILITY R2 — MINIMAL PROTOCOL CLARIFICATION`

### Rule 1 — Convention → Spec

> When a Question's Human Gate records an explicit Convention Formation Confirmation, that Convention's Scope, Evidence references, and Human Confirmation record must enter the governing Spec's normative content.

Status: `Human-Defined / Proposed Protocol Rule` — **not yet written into `protocol.md`.**

### Rule 2 — Convention Check → Spec

> The `Existing Behavior / Architecture / Convention check` step of Requirement Intelligence should read the governing Spec for previously-confirmed Conventions.

Status: `Human-Defined / Proposed Protocol Rule` — **not yet written into `protocol.md`.**

### Important Open Safety Check (not yet performed)

Before either rule is written into a formal Protocol file, three questions remain open — this is an **Implementation Safety Check**, distinct from re-running Discoverability R2:

1. Does a determinate `governing Spec` exist for a Requirement at the point a Convention is confirmed?
2. Can `governing Spec` be fully expressed by reusing the existing Protocol Scope → Spec relationship, or does it require new definition?
3. Does Rule 1 actually guarantee a determinate persistence landing point for a Convention, or does it merely defer to "some future Spec update" without a firm trigger?

---

## E. Excluded — Historical Errors, Not Facts

The following must **not** be treated as established fact in any future session picking up this work:

```text
ANSWERED Question = Convention
Historical Precedent = Convention
Historical Precedent = Safe Default
Safe Default = Assumption
Requirement.questions[] = guaranteed global Convention Registry
Phase 1B precedent = Existing Protocol Rule
```

Each of these was explicitly raised, examined, and rejected/corrected during Phase 1C design rounds (Final Semantic Check, R1 Targeted Revision, R2 Discoverability).

---

## F. NEXT ACTION

```text
Phase 1C Implementation Safety Check
```

Scope — check only:
1. Whether `governing Spec` is already unambiguously defined by existing Protocol text.
2. Whether Convention can obtain a determinate Spec persistence landing point.
3. Whether only minimal Protocol text changes (not new objects/states) are required.

**If Safety Check PASSes**:
```text
Implementation → modify formal Protocol files → Regression A–F → Final Gate
```

**If Safety Check finds the existing model insufficient**:
```text
STOP
```
No self-directed creation of a Convention Registry, Convention Object, Convention State, Convention Index, or Database Table is permitted at that point either — the same Object Boundary constraint carried through every prior round remains in force.
