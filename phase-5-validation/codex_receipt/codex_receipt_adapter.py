"""Offline Codex session -> Harness-compatible runtime.jsonl adapter (Phase 5, P5-1).

Implements docs/architecture/phase-5/codex-receipt-mapping.md (mapping_version 1, the default) and, only when
selected with --mapping-version 2, docs/architecture/phase-5/codex-receipt-mapping-v2.md (mapping_version 2).
Standalone: does not import harness.py or chain_verifier.py, never reads the clock, never touches the network,
opens the input read-only. The output is adapter-derived, not native Runtime evidence.

Usage: python -I codex_receipt_adapter.py --input SESSION.jsonl --out-dir DIR [--emit-partial] [--mapping-version {1,2}]
Exit:  0 COMPLETE, 2 INCOMPLETE, 1 usage or I/O error.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

ADAPTER_VERSION = "1"
MAPPING_VERSION = 1
ADAPTER_VERSIONS = {1: "1", 2: "2"}
TOKEN_ID_KEYS = {"response_id", "root_turn_id", "session_id", "thread_id", "turn_id"}
IGNORED_TOP = {"turn_context", "event_msg", "world_state"}
IGNORED_ITEM = {"message", "reasoning", "web_search_call"}
CALLS = {"function_call", "custom_tool_call"}
OUTPUTS = {"function_call_output", "custom_tool_call_output"}
NOTE = ("Derived from Codex session records by codex_receipt; not native Runtime output. "
        "No evidence tier is assigned here (Human ruling pending).")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def dump(obj):
    return (json.dumps(obj, sort_keys=True, ensure_ascii=True) + "\n").encode()


def nonempty(value):
    return isinstance(value, str) and value != ""


def output_ok(output):
    if isinstance(output, str):
        return True
    return isinstance(output, list) and all(isinstance(x, dict) and isinstance(x.get("text"), str) for x in output)


def leaf_ok(value):
    """Mapping v2 rule T3: below the allowed ID keys only number, boolean, null and objects of them; no strings, no arrays."""
    if isinstance(value, dict):
        return all(leaf_ok(x) for x in value.values())
    return value is None or (isinstance(value, (bool, int, float)))


def token_payload_ok(payload):
    """Mapping v2 rule T3 (finite allow-list for the observed structure, not a Codex schema)."""
    if not isinstance(payload, dict):
        return False
    for key, value in payload.items():
        if key in TOKEN_ID_KEYS:
            if not isinstance(value, str):
                return False
        elif not leaf_ok(value):
            return False
    return True


def split_lines(raw):
    """Return (terminated lines, unterminated final line or None), each without its terminator."""
    parts = raw.split(b"\n")
    final = parts.pop()  # b"" when raw ends with a newline
    lines = [p[:-1] if p.endswith(b"\r") else p for p in parts]
    return lines, (final if final else None)


def convert(raw, source_name, mapping_version=1):
    if mapping_version not in ADAPTER_VERSIONS:
        raise ValueError("unsupported mapping version")
    gaps, ignored, records = [], {}, []

    def gap(code, line, detail):
        gaps.append({"code": code, "line": line, "detail": detail})

    lines, final = split_lines(raw)
    if not raw:
        gap("EMPTY_INPUT", None, "zero-byte input")
        return finish(raw, source_name, 0, gaps, ignored, None, [], mapping_version)
    line_count = len(lines) + (1 if final is not None else 0)
    for number, line in enumerate(lines, 1):
        try:
            obj = json.loads(line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            gap("CORRUPT_LINE", number, "not valid UTF-8 JSON")
            continue
        if not isinstance(obj, dict):
            gap("CORRUPT_LINE", number, "JSON value is not an object")
            continue
        records.append((number, sha(line), obj))
    if final is not None:
        gap("TRUNCATED_FINAL_LINE", line_count, "final line has no line terminator")

    metas = [(n, o) for n, _, o in records if o.get("type") == "session_meta"]
    session = None
    if not metas:
        gap("NO_SESSION_ID", None, "no session_meta record")
    elif len(metas) > 1:
        for number, _ in metas[1:]:
            gap("DUPLICATE_SESSION_META", number, "more than one session_meta record")
    else:
        number, meta = metas[0]
        payload = meta.get("payload") if isinstance(meta.get("payload"), dict) else {}
        first, second = payload.get("session_id"), payload.get("id")
        if nonempty(first) and nonempty(second) and first != second:
            gap("AMBIGUOUS_SESSION_ID", number, "session_id and id differ")
        elif nonempty(first) or nonempty(second):
            session = first if nonempty(first) else second
        else:
            gap("NO_SESSION_ID", number, "session_meta has neither session_id nor id")

    calls, rows = {}, []

    def emit(kind, number, digest, record_type, block, call_id):
        rows.append({"kind": kind, "line": number, "hash": digest, "call_id": call_id, "record_type": record_type, "block": block})

    for number, digest, obj in records:
        top = obj.get("type")
        if not nonempty(top):
            gap("MALFORMED_RECORD", number, "record has no string type")
            continue
        if top == "session_meta":
            continue
        if mapping_version == 2 and top == "token_usage_record":
            if token_payload_ok(obj.get("payload")):
                ignored[top] = ignored.get(top, 0) + 1
            else:
                gap("TOKEN_USAGE_UNEXPECTED_SHAPE", number, "token_usage_record payload outside the allowed shape")
            continue
        if mapping_version == 2 and top == "compacted":
            gap("COMPACTION_PRESENT", number, "compacted record; earlier tool history cannot be shown complete")
            continue
        if top in IGNORED_TOP:
            ignored[top] = ignored.get(top, 0) + 1
            continue
        if top != "response_item":
            gap("UNKNOWN_RECORD_TYPE", number, "top-level type " + top)
            continue
        payload = obj.get("payload")
        kind = payload.get("type") if isinstance(payload, dict) else None
        if not nonempty(kind):
            gap("MALFORMED_RECORD", number, "response_item without payload type")
            continue
        if kind in IGNORED_ITEM:
            key = "response_item:" + kind
            ignored[key] = ignored.get(key, 0) + 1
        elif kind in CALLS:
            call_id = payload.get("call_id")
            if not nonempty(call_id):
                gap("MISSING_CALL_ID", number, "tool call without call_id")
            elif not nonempty(payload.get("name")):
                gap("MALFORMED_RECORD", number, "tool call without name")
            elif call_id in calls:
                gap("DUPLICATE_CALL_ID", number, "call_id already used at line %d" % calls[call_id]["line"])
            else:
                if kind == "function_call":
                    args, tool_input = payload.get("arguments"), None
                    if isinstance(args, str):
                        try:
                            parsed = json.loads(args)
                            tool_input = parsed if isinstance(parsed, dict) else None
                        except json.JSONDecodeError:
                            tool_input = None
                else:
                    args = payload.get("input")
                    tool_input = {"input": args} if isinstance(args, str) else None
                if tool_input is None:
                    gap("UNPARSEABLE_ARGUMENTS", number, "arguments are not usable")
                    tool_input = {"_unparsed_arguments": args}
                calls[call_id] = {"line": number, "answered": False}
                emit("tool_use", number, digest, kind,
                     {"id": call_id, "input": tool_input, "name": payload["name"], "type": "tool_use"}, call_id)
        elif kind in OUTPUTS:
            call_id = payload.get("call_id")
            if not nonempty(call_id):
                gap("MISSING_CALL_ID", number, "tool output without call_id")
            elif call_id not in calls:
                gap("UNPAIRED_OUTPUT", number, "no earlier call for this call_id")
            elif calls[call_id]["answered"]:
                gap("DUPLICATE_OUTPUT_ID", number, "call_id already answered")
            elif not output_ok(payload.get("output")):
                gap("UNSUPPORTED_OUTPUT_SHAPE", number, "output is not a string or a list of text objects")
            else:
                calls[call_id]["answered"] = True
                emit("tool_result", number, digest, kind,
                     {"content": payload["output"], "tool_use_id": call_id, "type": "tool_result"}, call_id)
        else:
            gap("UNKNOWN_RECORD_TYPE", number, "response_item type " + kind)
    for call_id, info in calls.items():
        if not info["answered"]:
            gap("UNPAIRED_CALL", info["line"], "call never answered")
    return finish(raw, source_name, line_count, gaps, ignored, session, rows, mapping_version)


def finish(raw, source_name, line_count, gaps, ignored, session, rows, mapping_version=1):
    gaps.sort(key=lambda g: (-1 if g["line"] is None else g["line"], g["code"]))
    out_rows, sidecar_rows, data = [], [], b""
    if session is not None:
        for index, row in enumerate(rows, 1):
            role = "assistant" if row["kind"] == "tool_use" else "user"
            obj = {"message": {"content": [row["block"]], "role": role},
                   "origin": {"adapter": "codex_receipt", "mapping_version": mapping_version, "raw_line": row["line"],
                              "raw_line_sha256": row["hash"], "raw_record_type": row["record_type"]},
                   "sessionId": session, "type": role}
            encoded = dump(obj)
            out_rows.append(obj)
            data += encoded
            sidecar_rows.append({"row": index, "kind": row["kind"], "call_id": row["call_id"], "raw_line": row["line"],
                                 "raw_line_sha256": row["hash"], "row_sha256": sha(encoded)})
    return {"status": "INCOMPLETE" if gaps else "COMPLETE", "mapping_version": mapping_version, "gaps": gaps, "ignored_counts": dict(sorted(ignored.items())),
            "session_id": session, "rows": out_rows, "runtime_bytes": data, "sidecar_rows": sidecar_rows,
            "source": {"name": source_name, "sha256": sha(raw), "bytes": len(raw), "line_count": line_count}}


def write_outputs(result, out_dir, emit_partial):
    out_dir = Path(out_dir)
    if out_dir.exists() and any(out_dir.iterdir()):
        raise FileExistsError("output directory is not empty")
    out_dir.mkdir(parents=True, exist_ok=True)
    name = None
    if result["status"] == "COMPLETE":
        name = "runtime.jsonl"
    elif emit_partial and result["session_id"] is not None:
        name = "runtime.partial.jsonl"
    if name:
        (out_dir / name).write_bytes(result["runtime_bytes"])
    version = result["mapping_version"]
    sidecar = {"adapter": "codex_receipt", "adapter_version": ADAPTER_VERSIONS[version], "mapping_version": version,
               "status": result["status"], "session_id": result["session_id"], "source": result["source"],
               "gaps": result["gaps"], "ignored_counts": result["ignored_counts"],
               "runtime": {"file": name, "row_count": len(result["rows"]),
                           "sha256": sha(result["runtime_bytes"]) if name else None},
               "rows": result["sidecar_rows"], "note": NOTE}
    (out_dir / "provenance.json").write_bytes((json.dumps(sidecar, sort_keys=True, indent=2) + "\n").encode())
    return name


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--emit-partial", action="store_true")
    parser.add_argument("--mapping-version", type=int, choices=sorted(ADAPTER_VERSIONS), default=1)
    args = parser.parse_args(argv)
    try:
        path = Path(args.input)
        with open(path, "rb") as handle:
            raw = handle.read()
        result = convert(raw, path.name, args.mapping_version)
        write_outputs(result, args.out_dir, args.emit_partial)
    except OSError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1
    print(json.dumps({"status": result["status"], "gap_count": len(result["gaps"]), "row_count": len(result["rows"])}))
    return 0 if result["status"] == "COMPLETE" else 2


if __name__ == "__main__":
    sys.exit(main())
