# Codex Receipt Mapping v1 (Phase 5, P5-1)

```text
STATUS:    mapping contract for an OFFLINE adapter. Locked (see codex-receipt-lock.json) before the adapter was written.
SCOPE:     Codex session JSONL  ->  Harness-compatible runtime.jsonl  +  provenance sidecar
NOT:       a real Codex run, a Protocol/Harness/Contract change, a general Runtime-adapter framework, an evidence-tier ruling
MAPPING:   mapping_version = 1
```

## 1. Input and its source

- One Codex CLI session file (`~/.codex/sessions/**/rollout-*.jsonl` layout), one JSON object per physical line, UTF-8.
- Fields below were observed **structurally** on local session files (key names and value types only; 112 files, CLI around 0.161.0). Contents were not copied. Field semantics beyond what is stated here are **not** assumed.
- Observed, and relied on:
  - top level: `type` (str), `payload` (object), `timestamp`, `ordinal`.
  - `session_meta.payload`: `session_id` (str), `id` (str).
  - `response_item.payload.type` in `function_call` (`call_id`, `name`, `arguments` = JSON string), `custom_tool_call` (`call_id`, `name`, `input` = string), `function_call_output` / `custom_tool_call_output` (`call_id`, `output` = string **or** list of objects with a string `text`).
- Observed and ignored (counted, never silently dropped): `turn_context`, `event_msg`, `world_state`, and `response_item` payload types `message`, `reasoning`, `web_search_call`.

## 2. Output contract (what the existing Harness reads)

`harness.py inventory()` reads, per row: `sessionId` (or `session_id`), and `message.content[]` blocks of type `tool_use` (`id`, `name`) and `tool_result` (`tool_use_id`). The Harness hashes the whole file. The adapter therefore emits Claude-shaped rows and adds an `origin` key (unknown keys are ignored by the Harness and by C1 Contract Appendix A).

```text
tool_use row:    {"message":{"content":[{"id":CALL_ID,"input":{...},"name":NAME,"type":"tool_use"}],"role":"assistant"},
                  "origin":{...},"sessionId":SESSION,"type":"assistant"}
tool_result row: {"message":{"content":[{"content":OUTPUT,"tool_use_id":CALL_ID,"type":"tool_result"}],"role":"user"},
                  "origin":{...},"sessionId":SESSION,"type":"user"}
origin:          {"adapter":"codex_receipt","mapping_version":1,"raw_line":N,"raw_line_sha256":HEX,"raw_record_type":T}
```

Serialization: `json.dumps(obj, sort_keys=True, ensure_ascii=True)` + `"\n"`, UTF-8, LF only.

## 3. Mapping rules

| Codex record | Rule |
|---|---|
| `session_meta` | Source of the session id: `payload.session_id`, else `payload.id`. Exactly one `session_meta` is required. |
| `function_call` | `tool_use`; `id` = `call_id`; `name` = `name`; `input` = `json.loads(arguments)` and must be an object. |
| `custom_tool_call` | `tool_use`; `input` = `{"input": <input string>}`. |
| `*_output` | `tool_result`; `tool_use_id` = `call_id`; `content` = `output` verbatim (string, or list of objects each with a string `text`). `is_error` is **not** derivable and is never emitted. |

Pairing: an output pairs with the earlier, still-unanswered call of the same `call_id`. Row order = raw line order (outputs may interleave across calls). Tool identity is carried through but not interpreted.

Session id, call id, order, time: session id comes only from `session_meta`. Call ids are taken verbatim. Output order is raw line order. Codex timestamps and `ordinal` are not copied into rows (the Harness and C1 Checker do not read them); the adapter never reads the clock.

Traceability: each row carries `origin.raw_line` (1-based physical line) and `origin.raw_line_sha256` = SHA-256 of that raw line's bytes without the line terminator (`\n` or `\r\n`). The sidecar repeats this per row and adds the row's own SHA-256.

## 4. Gaps (fail closed)

Any gap makes the adapter status `INCOMPLETE`. Gap record: `{code, line, detail}` (`line` = 1-based raw line or `null`). Codes are closed:

| Code | Condition | Row for the offending record |
|---|---|---|
| `EMPTY_INPUT` | zero bytes | — (processing stops) |
| `CORRUPT_LINE` | terminated line that is not valid UTF-8, not valid JSON, not a JSON object, or blank | none |
| `TRUNCATED_FINAL_LINE` | final line has no line terminator | none (line not processed) |
| `MALFORMED_RECORD` | object without a string `type`, a `response_item` without an object `payload` with string `type`, or a tool call without a non-empty string `name` | none |
| `UNKNOWN_RECORD_TYPE` | top-level `type` or `response_item` payload type not listed in section 1 | none |
| `NO_SESSION_ID` | no `session_meta`, or it has neither `session_id` nor `id` as a non-empty string | — |
| `AMBIGUOUS_SESSION_ID` | `session_id` and `id` both present and different | — |
| `DUPLICATE_SESSION_META` | more than one `session_meta` (reported on each extra one) | — |
| `MISSING_CALL_ID` | tool call or output without a non-empty string `call_id` | none |
| `DUPLICATE_CALL_ID` | second call with an already-seen `call_id` | none (first wins) |
| `DUPLICATE_OUTPUT_ID` | second output for an already-answered `call_id` | none (first wins) |
| `UNPAIRED_CALL` | call never answered (reported on the call's line) | emitted |
| `UNPAIRED_OUTPUT` | output with no earlier unanswered call | none |
| `UNPARSEABLE_ARGUMENTS` | `arguments` not a JSON-object string, or `custom_tool_call.input` not a string | emitted with `input` = `{"_unparsed_arguments": <raw value>}` |
| `UNSUPPORTED_OUTPUT_SHAPE` | `output` neither a string nor a list of objects with string `text` | none (the call stays unpaired) |

Gaps are listed sorted by (`line` with `null` first, `code`). A gap on session identity (`NO_SESSION_ID`, `AMBIGUOUS_SESSION_ID`, `DUPLICATE_SESSION_META`) means rows cannot be attributed: no rows are emitted at all.

## 5. Output files and status

- `provenance.json` is **always** written.
- `runtime.jsonl` is written **only when status is `COMPLETE`**. The Harness cannot see adapter-level gaps (an unknown record is simply absent from the rows), so a gapped `runtime.jsonl` could be sealed as `COMPLETE_WITHIN_BOUNDARY`. Withholding it is the fail-closed guard.
- With `--emit-partial` and status `INCOMPLETE` (and a determined session id), rows are written to `runtime.partial.jsonl`, a name the Harness flow never consumes by default. Not written when session identity is gapped.
- Exit code: `0` COMPLETE, `2` INCOMPLETE, `1` usage or I/O error. The output directory must not exist or must be empty.
- Zero tool rows with no gaps is `COMPLETE` with an empty `runtime.jsonl`; the Harness itself then reports `no runtime events captured`.

## 6. Guarantees and non-guarantees

Guaranteed: determinism (same bytes, same mapping_version, same file name -> identical output bytes); no silent drop (each non-mapped record is either counted in `ignored_counts` or a gap); each emitted row is traceable by line and hash; no network, no clock, no randomness, input opened read-only.

Not guaranteed: that the Codex record semantics are what this mapping assumes beyond section 1; stability across other Codex versions (older or newer formats are only handled to the extent their records match section 1, otherwise they produce gaps); that tool results are complete or error-free (`is_error` is unsupported); that the session was a real, complete or authorised run; that the output is native Runtime evidence. **The output is adapter-derived.** No evidence tier is assigned here; whether such rows may count as `RUNTIME_GENERATED` is a pending Human ruling (Phase 5 analysis H1).

## 7. Unsupported

Streaming/partial tool output, multi-modal outputs beyond `text`, tool errors, approvals, sub-agents, compaction, and any record type not in section 1.
