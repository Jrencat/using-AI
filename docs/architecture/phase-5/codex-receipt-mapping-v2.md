# Codex Receipt Mapping v2 (Phase 5, P5-1.1)

```text
STATUS:    mapping contract for an OFFLINE adapter. Locked (see codex-receipt-lock-v2.json) before the v2 adapter code was written.
SCOPE:     Codex session JSONL  ->  Harness-compatible runtime.jsonl  +  provenance sidecar
BASE:      mapping v1 (codex-receipt-mapping.md), which stays locked and unchanged and remains the default
NOT:       a real Codex run, a Protocol/Harness/Contract change, a general Runtime-adapter framework, an evidence-tier ruling,
           a cross-version Codex schema
MAPPING:   mapping_version = 2   (selected explicitly with --mapping-version 2; without the flag the adapter uses mapping v1)
```

## 1. What v2 changes

Everything in v1 sections 1-7 applies unchanged (input, output contract, mapping rules, pairing, serialization, traceability, gap codes, output files, status, exit codes, guarantees) except the three points below. `origin.mapping_version` and `provenance.json` carry `2`.

| Record | v1 | v2 |
|---|---|---|
| `token_usage_record` | gap `UNKNOWN_RECORD_TYPE` | counted and ignored when it satisfies rule T3 (section 2); otherwise gap `TOKEN_USAGE_UNEXPECTED_SHAPE` |
| `compacted` | gap `UNKNOWN_RECORD_TYPE` | gap `COMPACTION_PRESENT` (section 3) |
| all other records, unanswered calls, orphan outputs | per v1 | per v1, unchanged |

New gap codes (closed set otherwise unchanged): `TOKEN_USAGE_UNEXPECTED_SHAPE`, `COMPACTION_PRESENT`.

## 2. Rule T3 for `token_usage_record`

Basis: a structural check of local Codex sessions (CLI about 0.161.0) found every `token_usage_record` to be a top-level record with `payload` an object whose string leaves sit only under five top-level keys and whose other leaves are integers. No tool-call or tool-output key (`call_id`, `name`, `arguments`, `input`, `output`, `content`, `text`, `message`) was present. **T3 is a finite allow-list for that observed structure. It is not a Codex schema and is not claimed to hold for other versions.**

A `token_usage_record` is ignored (no row; counted in `ignored_counts["token_usage_record"]`) if and only if all hold:

1. `payload` is present and is a JSON object (not null, array, string, number or boolean).
2. No array occurs anywhere in `payload`, at any depth, including empty arrays.
3. For the five ID keys `response_id`, `root_turn_id`, `session_id`, `thread_id`, `turn_id` **at the top level of `payload`**: if present, the value is a string. (Absent is allowed.)
4. Every other leaf, at any depth (including a key with an ID key's name below the top level), is a number, boolean or null. No string leaf is allowed there.
5. Objects may nest. An empty object is valid.

Otherwise: one gap `TOKEN_USAGE_UNEXPECTED_SHAPE` for the record's line, no row, not counted as ignored. Failing records are never silently dropped; status becomes `INCOMPLETE`.

Properties: no row is ever derived from a token record, whatever its content. Its position between a call and its output does not affect pairing. The value of the ID strings, including `session_id`, is not inspected; **no consistency check between a token record's `session_id` and the `session_meta` id is made** (not in scope for v2).

## 3. `compacted`

Each `compacted` record produces one gap `COMPACTION_PRESENT` on its line, whatever its payload (including no payload). The payload is never parsed and no row is ever derived from it; objects embedded in it (for example tool-call-shaped objects) do not pair with real calls or outputs. Reason: nothing available proves that the tool history before the record is fully retained in the session file, and the record may embed copies of tool objects. Compaction therefore makes the adapter status `INCOMPLETE`, and `runtime.jsonl` is withheld (v1 section 5).

## 4. Unchanged and still fail-closed

Unanswered calls (`UNPAIRED_CALL`), orphan outputs, duplicate ids, unknown record types and all other v1 gaps stay gaps. `runtime.jsonl` is written only when status is `COMPLETE`; with `--emit-partial` an `INCOMPLETE` result with a determined session id writes `runtime.partial.jsonl` only.

## 5. Guarantees and non-guarantees

As v1 section 6. In addition: v2 `COMPLETE` means every record was mapped, counted by a stated rule, or reported as a gap. It does not mean the Codex session was complete, authorised or error-free. The output is adapter-derived (recommended tier `TOOL_GENERATED`, not `RUNTIME_GENERATED`); this mapping assigns no evidence tier.

## 6. Version selection

`--mapping-version 2` selects this mapping. No flag, or `--mapping-version 1`, selects mapping v1 with v1's exact output bytes. No mapping is ever chosen from the input's content.
