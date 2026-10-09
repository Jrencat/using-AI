# Codex Receipt Mapping v2 — Investigation and Change Proposal (P5-1.1)

```text
STATUS:   PROPOSAL, kept as the design record. Later implemented as mapping v2 with one change: the structure-only probe showed
          T2 does not match the observed records (every token record has string ID leaves), so the Human approved the finite
          allow-list T3 instead. Sections 3.1, 4.1, 5, 6 and 8 below describe T2 and are superseded by codex-receipt-mapping-v2.md;
          see p5-1-1-closeout.md. Text below is otherwise unchanged.
SCOPE:    why mapping v1 yields INCOMPLETE on 34 of 112 local sessions; what the minimum v2 change could be
NOT:      P5-2 authorization, a real Codex run, an adapter change, a Protocol/Harness/Contract change, an evidence-tier ruling
UNCHANGED: mapping v1, CODEX-RECEIPT-LOCK-V1, CODEX-RECEIPT-PREREG-V1, v1 fixtures, adapter, Harness, Phase 4 artifacts
AUTHOR:   same author as P5-1 (this is not Independent Verification)
```

Labels used below: **FACT** (directly supported by a repo file, cited), **INFERENCE** (reasoned, evidence missing), **UNKNOWN** (no basis; not guessed).

## 1. Background and v1 limits

- FACT: v1 treats any top-level `type` outside `session_meta`, `turn_context`, `event_msg`, `world_state`, `response_item` as `UNKNOWN_RECORD_TYPE` (adapter `convert()`; mapping §4). Any gap makes the status `INCOMPLETE` and withholds `runtime.jsonl` (mapping §5).
- FACT (`p5-1-closeout.md` §4, counts only, content not kept): 112 local sessions → 78 `COMPLETE`, 34 `INCOMPLETE`. Drivers: `token_usage_record` (1673 records / 29 files), `compacted` (8 records / 7 files), plus 2 files with unanswered calls.
- FACT: closeout records neither the per-file gap breakdown nor the overlap between the three causes. 29 + 7 + 2 = 38 > 34, so the sets overlap, or the 2 unpaired files are not inside the 34 (the wording is ambiguous). Exact post-v2 COMPLETE count is therefore **UNKNOWN**.
- FACT: no repo file records the field-level shape of either record type. v1 §1 lists only the structure observed for the types it handles, and `phase-5-boundary-analysis.md` states "record *types* were observed … field-level schema … unknown".
- FACT: nothing in the repo describes Codex semantics for these two types. I did not read any session file for this task (sources limited to repo and docs, as instructed).
- Background recollection (INFERENCE, **not relied on**): public Codex sources use a compaction rollout item and token-count events whose names differ from `token_usage_record`. Names/versions here may differ; treat as unverified.

## 2. What the downstream consumers actually read

- FACT (`harness.py inventory()`): per row `sessionId`, and `tool_use` / `tool_result` blocks. A row without `sessionId` is a gap unless it is an allowlisted Claude metadata type. Unpaired non-Gate tool events → `capture_status = INCOMPLETE`. Nothing else in the transcript is inspected.
- FACT (`scope_checker.py`, Contract SC-E3/SC-E4): Checker needs `capture_status = COMPLETE_WITHIN_BOUNDARY`, empty `capture_gaps`, and ≥ 1 `tool_use` when a delta exists. Tool identity and everything else in the transcript are not examined.
- Consequence (FACT, already shown by case N01): the Harness is **blind to adapter-level omissions**. Dropping a record from `runtime.jsonl` is invisible downstream. Every relaxation in v2 is therefore a claim made only by the adapter and must be justified on its own.

## 3. Per-record investigation

### 3.1 `token_usage_record`

| | |
|---|---|
| FACT | Top-level type, 1673 records in 29 of 112 files (≈58 per affected file). Currently a gap. Not a `response_item`, so it is not a v1 tool call/output. |
| INFERENCE | Name suggests usage accounting. Per-file density suggests per-turn emission. Why 83 files have none (older CLI? no model calls?) is not established. |
| UNKNOWN | Payload keys and value types; whether any string/array content is present; whether it can appear between a call and its output; whether it carries a call/turn reference; Codex-version dependence. |
| Risk if ignored | A record that does carry tool-related information would be lost silently. Mitigated by the shape rule below. |
| Risk if kept as gap | Every session containing one is `INCOMPLETE`; a P5-2 run would very likely be unusable (v1 closeout §7 already says so). |
| Order / boundary impact | None under raw-line ordering (rows come from raw line order; unmapped lines do not shift it). Session boundary: no role in v1 (session id comes only from `session_meta`). |

**Why a content-agnostic rule is possible.** Under v1 a tool call needs a non-empty string `call_id` and `name`, and an output needs a string `call_id` and a string/list-of-text `output`. A record whose payload leaves are all numbers/booleans/null cannot carry any of those, whatever its name means. So a shape rule gives safety without knowing the semantics.

### 3.2 `compacted`

| | |
|---|---|
| FACT | Top-level type, 8 records in 7 of 112 files. Currently a gap. v1 §7 lists compaction as unsupported. Closeout §4: "may hide earlier tool calls". |
| INFERENCE | Name suggests context compaction (history summarized/replaced for the model). That alone does **not** say whether the session file still keeps the original records, or whether the record embeds a replacement history. |
| UNKNOWN | Payload shape; whether pre-compaction `function_call`/`*_output` lines remain in the same file; whether the record embeds copies of earlier items; whether later outputs can reference calls only present in the compacted region; whether it marks a context boundary only or also a session/turn boundary; frequency in short sessions. |
| Risk if ignored | A call/output removed from the file (or only present inside the record) would make `runtime.jsonl` look complete while being partial; Harness cannot detect it. This is the core integrity risk. |
| Risk if kept as gap | 7 of 112 local files stay `INCOMPLETE`. Low cost for P5-2 if the run is short (INFERENCE: compaction is tied to long contexts; unverified). |
| Why it cannot be proven benign offline | "No orphan outputs after the record" is a weak signal only: a dropped call-with-output pair leaves no trace. Absence of evidence does not establish completeness. |

### 3.3 Unanswered tool calls

| | |
|---|---|
| FACT | 2 local files have calls without a paired output; `UNPAIRED_CALL` is a gap and the Harness independently flags unpaired non-Gate events (N08 black box: `INCOMPLETE`). |
| INFERENCE (hypotheses, none established) | (a) session interrupted/aborted during a call; (b) file copied while a call was in flight; (c) the output exists only inside a compacted region; (d) an output form v1 does not recognise — weakened because an unrecognised type would have produced `UNKNOWN_RECORD_TYPE`, and the closeout names only the two types above. |
| UNKNOWN | Which hypothesis applies; whether the 2 files overlap with the `compacted` files; whether the unpaired call is the last tool record. |
| Risk if relaxed | A tool run with unknown outcome would count as complete evidence. Contradicts the Harness's own rule. |
| Verdict | Keep as gap. No v2 change. |

## 4. Candidate strategies

### 4.1 `token_usage_record`

| ID | Strategy | Safety | Value | Needs |
|---|---|---|---|---|
| T0 | Keep gap (v1) | Highest | Real sessions mostly unusable | nothing |
| T1 | Ignore and count by type name | Relies on unknown semantics | High | trust in the name |
| **T2** | **Ignore and count only if payload is an object whose leaves are all number/boolean/null; otherwise gap `TOKEN_USAGE_UNEXPECTED_SHAPE`** | Content-agnostic; cannot hide v1-recognisable tool data | High if real records are numeric-only; otherwise stays fail-closed and tells us | shape of real records (probe, see D1) improves fixtures but is not needed for safety |

### 4.2 `compacted`

| ID | Strategy | Safety | Value | Needs |
|---|---|---|---|---|
| C0 | Keep as `UNKNOWN_RECORD_TYPE` (v1) | High | none | nothing |
| **C1** | **Keep fail-closed, give it a dedicated gap code `COMPACTION_PRESENT`; record line numbers in the sidecar; no row ever mapped from its payload** | High (status unchanged) | Diagnostics; makes a later relaxation decision data-driven | small spec text + tests |
| C2 | Accept when all earlier calls are paired | Not provable (§3.2) | Medium | evidence on what the file retains |
| C3 | Ignore | Unsafe | — | — |

### 4.3 Unanswered calls
Only one real option: keep `UNPAIRED_CALL`.

## 5. Recommendation

- **Token: T2.** Smallest change that removes the dominant, evidenced blocker without relying on its semantics.
- **Compaction: C1** (fail-closed, dedicated code). If the Human prefers the smallest possible change, C0 (no change) is acceptable; C1 only improves diagnostics and does not change any status. C2 is not recommended until the §7 questions are answered with evidence, and may never be provable offline.
- **Unanswered calls: no change.**
- Net effect: v2 = one relaxation (T2) + one relabel (C1). Everything else in v1 §3–§5 is carried over unchanged.
- Residual risks of the recommendation:
  - T2: real records may contain string leaves → they would stay gaps (safe, no gain). A numeric-only record might carry information relevant to completeness that we ignore (e.g. a counter); it is not used as a cross-check.
  - C1: short sessions without compaction pass; long sessions do not. Accepted.
  - Both: the v2 adapter would still be adapter-derived, same `TOOL_GENERATED` classification as P5-1 (H1 unchanged).

## 6. Proposed v2 mapping rules (draft text for a new `codex-receipt-mapping-v2.md`)

| Rule | v1 | v2 |
|---|---|---|
| `mapping_version` | 1 | 2 (also in each `origin`) |
| `session_meta`, `function_call`, `custom_tool_call`, `*_output`, pairing, serialization, traceability, output files, exit codes | as v1 | **identical** |
| `token_usage_record` | `UNKNOWN_RECORD_TYPE` | If `payload` is an object and every leaf in it (recursively, through objects only; arrays or strings anywhere fail) is number/boolean/null → no row, counted in `ignored_counts["token_usage_record"]`. Otherwise gap `TOKEN_USAGE_UNEXPECTED_SHAPE` (covers missing/non-object payload), no row. |
| `compacted` | `UNKNOWN_RECORD_TYPE` | Gap `COMPACTION_PRESENT` (one per record, on its line); no row; payload is never parsed for tool data. |
| Unanswered call / orphan output | gap | unchanged |
| All other unknown types | gap | unchanged |
| New gap codes | — | `TOKEN_USAGE_UNEXPECTED_SHAPE`, `COMPACTION_PRESENT` (closed code set otherwise unchanged) |

Sidecar: unchanged fields; `mapping_version: 2`; `ignored_counts` gains the `token_usage_record` key. Individual ignored lines are traceable through the source hash and line count already in the sidecar; no per-line list is proposed (1673 entries would bloat it).

## 7. Open questions (not answerable from the repo)

1. Exact payload shape (keys, leaf types) of `token_usage_record` and `compacted`.
2. Do pre-compaction tool records remain in the same file? Does the record embed copies?
3. Can a token record sit between a call and its output? (T2 is safe either way; fixture realism only.)
4. For the 2 unpaired files: is the unpaired call last? Overlap with the `compacted` files?
5. Per-file gap breakdown behind the 34 (to estimate the real gain from T2).
6. Whether current Codex CLI versions still emit the same types (all data are from about 0.161.0).

Questions 1, 2, 4, 5 could be answered by a **structure-only probe** (key names, value types, relative line positions, counts; no content read into any file or report). That is the same method as the P5-1 structural check, but it reads local session files, which this task did not do. It needs your authorization (D1).

## 8. Proposed pre-registered cases for v2 (to be written and locked **before** any adapter change)

Fixtures would be synthetic. **Caveat:** payload shapes for these two types in synthetic fixtures are invented, not observed; this is why D1 is recommended before locking.

| ID | Case | Expected |
|---|---|---|
| Q01 | P01 plus one numeric-only `token_usage_record` between call and output | `COMPLETE`; rows equal P01; `ignored_counts` `{token_usage_record: 1}`; Harness black box `COMPLETE_WITHIN_BOUNDARY` |
| Q02 | Several token records at start / between / end, interleaved calls (P03 shape) | `COMPLETE`; row order = raw line order; count correct |
| Q03 | Nested numeric-only objects, booleans, nulls | `COMPLETE` (rule accepts them) |
| R01 | Token record with a string leaf | `INCOMPLETE`, `TOKEN_USAGE_UNEXPECTED_SHAPE` on its line; rows for the pair still in partial |
| R02 | Token record with an array leaf, and another with a string-valued `output` / `call_id` / `name` key | each a gap; no row is derived from them |
| R03 | Token record with missing / non-object payload | gap |
| R04 | `compacted` between a call and its output | `INCOMPLETE`, `COMPACTION_PRESENT`; partial rows present; Harness black box on the partial file is `COMPLETE_WITHIN_BOUNDARY` (demonstrates why `runtime.jsonl` is withheld) |
| R05 | `compacted` whose payload embeds `function_call`-shaped objects | only `COMPACTION_PRESENT`; **no** row from embedded content |
| R06 | `compacted` after an unanswered call | `UNPAIRED_CALL` + `COMPACTION_PRESENT` |
| R07 | Valid token records plus an unanswered call (N08 shape) | `INCOMPLETE`, `UNPAIRED_CALL` only (ignoring tokens must not mask it) |
| R08 | Token records plus an orphan output | `INCOMPLETE`, `UNPAIRED_OUTPUT` only |
| V-reg | All 26 v1 fixtures under v2 | same status, gaps and row projection as in the v1 registry (only `mapping_version` fields differ); under v1 they are byte-identical to today |

Acceptance conditions for a future implementation task:
- Registry and fixtures locked (new lock) before the adapter change; expectations never edited to match output.
- All v2 cases match; v1's 26 cases and 11 tests still pass unchanged; `test_locked_files_unchanged` for the v1 lock still passes.
- Determinism, CRLF equivalence, raw-line traceability and "no false COMPLETE" tests extended to the Q/R cases.
- No `COMPLETE` for any case containing `compacted`, an unanswered call, or a non-conforming token record.
- No new dependency, no network/clock/randomness, Harness unchanged.
- Optional, only if D1 is approved: a structure-only re-run on local sessions reporting counts (COMPLETE/INCOMPLETE and gap codes per file), explicitly labelled a structural smoke check, not run validation.

## 9. Impact on status and output gate

- `COMPLETE` is still "no gaps". `runtime.jsonl` is still written only when `COMPLETE`; `runtime.partial.jsonl` still only with `--emit-partial` on `INCOMPLETE`.
- Newly `COMPLETE`: sessions whose **only** v1 gap was numeric-only `token_usage_record`. Size: UNKNOWN (§1). Upper bound if every token record conforms: the 34 minus the files that also contain `compacted` (7) or unanswered calls (≤ 2); overlap unknown.
- Still `INCOMPLETE`: any `compacted`, unanswered call, non-conforming token record, or any v1 gap.
- COMPLETE ratio is not a goal; a lower ratio with an explained gap is preferable to a higher one with a silent drop.
- What v2 does not change: the Harness cannot see adapter omissions; `COMPLETE` still means only "every record was mapped, counted by a stated rule, or reported". It is not a statement that the Codex session was complete or authorised.

## 10. Migration requirements (nothing created now)

- New mapping file (proposed name `codex-receipt-mapping-v2.md`), new registry (proposed id `CODEX-RECEIPT-PREREG-V2`), new lock (proposed id `CODEX-RECEIPT-LOCK-V2`, adapter-not-yet-modified flag true), new fixtures in a separate directory. Names are proposals; formal ids are allocated only on approval.
- v1 mapping, registry, lock, fixtures: byte-unchanged.
- Adapter form (D5): add an opt-in `--mapping-version 2` with default 1 and v1 behaviour unchanged, or a separate module. Recommend the former only if the v1 regression gate above is mandatory; the latter if byte-level isolation of v1 is preferred (cost: ~230 duplicated lines).
- `make_lock.py` would need a parameter or a copy; that is a change to an existing tool, to be decided in the implementation task.
- Closeout for v2 follows the P5-1 pattern (facts / limits / what is not shown).

## 11. Decisions for the Human

| ID | Decision | Recommendation |
|---|---|---|
| D1 | Authorize a structure-only probe of local session files (key names, value types, relative positions, counts; no content kept) to answer §7 Q1, Q2, Q4, Q5 before fixtures are written? | Yes, limited to those questions |
| D2 | Token policy: T2 vs keep gap (T0) | T2 |
| D3 | Compaction: C1 vs C0 vs C2 | C1 (C0 acceptable); not C2 now |
| D4 | Unanswered calls | Keep gap |
| D5 | Adapter implementation form for v2 | Opt-in flag, v1 default |
| D6 | Authorize a separate implementation task for v2 (spec, registry, lock, fixtures, adapter, tests) | After D1–D5 |
| D7 | Whether v2 is worth doing at all before P5-2, or to go to P5-2 with v1 and accept `INCOMPLETE` on any session with token records | v2-T2 is worth it: token records are in ≈26% of local files and a real run likely contains them (INFERENCE) |

Still separate and untouched: H1 confirmation, H2 (P5-2 and quota), H3 (close Phase 4), H4 (P5-3/P5-4).

## 12. Out of scope

Implementing v2; new lock/registry ids; editing v1 or its lock; any real Codex run or quota use; P5-2/P5-3/P5-4; Independent Verification; a general adapter framework; Harness/Protocol/Contract/Corpus changes; evidence-tier rulings; support for streaming, multi-modal output, tool errors, approvals or sub-agents; committing any session content; Git commit/push.
