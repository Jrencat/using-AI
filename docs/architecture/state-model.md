# State Model — v0.1 (Phase 1A Design)

> Status: DESIGNED, NOT IMPLEMENTED. See `protocol.md` §4-5 for object definitions this document assumes.

## 1. Requirement

```
DRAFT ──(investigation started)──> INVESTIGATING ──(all Critical questions resolved)──> READY
                                         │
                                         └──(a Critical question remains OPEN/BLOCKED)──> BLOCKED
BLOCKED ──(question ANSWERED or ASSUMED)──> INVESTIGATING (re-check)
READY ──(new Critical unknown discovered downstream)──> BLOCKED  [reopen]
```

- Entry precondition: none (`intent` alone is sufficient to create).
- Exit postcondition for `READY`: every `Critical` question is `ANSWERED`; `Important`/`Non-Critical` questions may remain `ASSUMED` or `OPEN` (non-blocking).
- `READY` is not terminal — a Spec revision or new Evidence can reopen it (see §12 Legacy Compatibility: this mirrors Legacy's incremental QA re-run rule).

### 1.1 Question (embedded)

```
OPEN ──(investigation resolves it)──> ANSWERED
OPEN ──(Critical/Important, downgraded with a stated default)──> ASSUMED  [spawns Assumption]
OPEN ──(Critical, cannot be resolved by investigation)──> BLOCKED  [opens Human Gate]
BLOCKED ──(Human decision recorded)──> ANSWERED
OPEN ──(further investigation shows it no longer applies)──> INVALID  [kept, not deleted]
```

- Hard rule (protocol.md §6): a `Critical` question can never transition `OPEN → ASSUMED` directly for business/irreversible/permission matters — only `OPEN → BLOCKED → ANSWERED`.

## 2. Assumption

```
(created from an ASSUMED Question) ──> ISOLATED
ISOLATED ──(new Evidence contradicts default_behavior)──> CHALLENGED
CHALLENGED ──(Human reviews, confirms default was fine)──> ISOLATED
ISOLATED / CHALLENGED ──(Human Gate decision: confirm)──> PROMOTED   [becomes normative Spec content]
ISOLATED / CHALLENGED ──(Human Gate decision: reject)──> REJECTED    [terminal, Requirement reopens]
PROMOTED ──(new Evidence contradicts the now-normative content)──> CHALLENGED  [re-opens; Spec must also revert that chapter to DRAFT]
```

`PROMOTED` is **not** fully terminal: it is the normal resting state, but new contradicting Evidence can still re-open it into `CHALLENGED`. Without this edge, a stale default could sit as normative forever with no re-check path — caught during Architecture Attack #2 (`simulation.md` §6) and fixed here rather than left as a silent gap.

- `ISOLATED` is the only state in which a dependent Task may be `BLOCKED`-created (never `ELIGIBLE`).
- No transition exists directly from `ISOLATED` to any state that allows unauthorized code — `PROMOTED` requires a Human Gate decision, full stop (Legacy §5/§7 preserved verbatim).

## 3. Spec

```
DRAFT ──(chapters 1-8 populated from READY Requirement content + PROMOTED Assumptions)──> REVIEWED
REVIEWED ──(Human approves)──> APPROVED
REVIEWED ──(Human requests changes)──> DRAFT
APPROVED ──(Requirement reopens / new PROMOTED Assumption / new Critical Question)──> DRAFT  [versioned re-entry, not a silent overwrite]
```

- Chapter 9 (`chapter9_pending_assumptions[]`) is populated continuously as Assumptions are created — it is not gated by Spec state.

## 4. Task

```
DRAFT ──(created; if scope touches ONLY chapter9_pending_assumptions content ⇒ creation itself is refused — absolute circuit-break)──>
DRAFT ──(priority ∈ {P0,P1} AND no assumption_deps in ISOLATED)──> ELIGIBLE
DRAFT ──(priority == P2 OR any assumption_dep in ISOLATED)──> BLOCKED
BLOCKED ──(all assumption_deps leave ISOLATED via PROMOTED, AND priority manually re-set to P0/P1 by Human)──> ELIGIBLE
ELIGIBLE ──(agent starts work)──> IN_PROGRESS
IN_PROGRESS ──(attempt completed)──> EVALUATING
EVALUATING ──(Evaluation.decision == PASS)──> DONE
EVALUATING ──(Evaluation.decision == FAIL, attempts < contract retry cap)──> IN_PROGRESS  [retry]
EVALUATING ──(Evaluation.decision == FAIL, attempts >= retry cap)──> FAILED
EVALUATING ──(Evaluation attributes failure to unresolved Assumption)──> RISK_PENDING  [not a FAILED verdict]
EVALUATING ──(Evaluation.decision == INVALID_AGENT_RESULT, attempts < contract retry cap)──> IN_PROGRESS  [claim rejected, redo — never silently accepted]
EVALUATING ──(Evaluation.decision == INVALID_AGENT_RESULT, attempts >= retry cap)──> FAILED  [an agent that keeps misreporting must not retry forever]
```

`INVALID_AGENT_RESULT` consumes a retry-cap attempt identically to `FAIL` — caught during Architecture Attack #10 (`simulation.md` §6), where an unbounded-retry gap was identified and closed here.

- `RISK_PENDING` is terminal for this Task instance in the current cycle — it surfaces as a `TD-XXX` Pending Tech Debt entry (Legacy §7 preserved), not a defect.
- A Task never self-transitions `BLOCKED → ELIGIBLE`; only a Human Gate decision does, matching Legacy's "等待人工显式授权" (Legacy L397).

## 5. Agent Contract

```
DRAFT ──(authored)──> ACTIVE
ACTIVE ──(revised)──> ACTIVE (new version)
ACTIVE ──(deprecated)──> RETIRED
```

- Mostly reference data, not a per-task instance; included for completeness since the brief requires every Core Object to have a state model, however trivial.

## 6. Evidence

```
(collected via tool/investigation/human)──> COLLECTED
COLLECTED ──(a later, higher-or-equal-trust-tier Evidence item contradicts it)──> DISPUTED
DISPUTED ──(Human or independent verification resolves conflict)──> COLLECTED (superseded_by recorded) | DISPUTED (unresolved, blocks dependent Evaluation)
```

- `COLLECTED` Evidence is otherwise immutable — no in-place edits, only supersession, to keep the citation trail honest.

## 7. Evaluation

```
PENDING ──(Evidence sufficient, Claim matches)──> EVALUATED (decision = PASS)
PENDING ──(Evidence insufficient)──> EVALUATED (decision = INSUFFICIENT)
PENDING ──(Evidence contradicts Claim)──> EVALUATED (decision = INVALID_AGENT_RESULT)
PENDING ──(Evidence shows genuine failure, not a Claim/Evidence mismatch)──> EVALUATED (decision = FAIL)
PENDING ──(high-risk/irreversible action pending authorization)──> EVALUATED (decision = BLOCKED, human_gate open)
```

- `EVALUATED` is terminal for that Evaluation instance; a retried Task attempt produces a *new* Evaluation, not a mutated one (append-only, matching the Traceability requirement in `protocol.md` §10).

## 8. Cross-Object Invariants (must hold in every reachable state)

1. No `Task` is ever `ELIGIBLE` while any of its `assumption_deps` is `ISOLATED` or `CHALLENGED`.
2. No `Assumption` reaches `PROMOTED`/`REJECTED` without a recorded Human Gate `decision` + `authority`.
3. No `Evaluation` reaches `PASS` citing only `SELF_REPORT`-tier Evidence.
4. No `Spec` chapter 1-8 content originates from a Question that is not `ANSWERED`, nor from an Assumption that is not `PROMOTED`.
5. `chapter9_pending_assumptions[]` never contains a `PROMOTED` or `REJECTED` Assumption (it is removed/migrated on transition out of `ISOLATED`/`CHALLENGED`).
