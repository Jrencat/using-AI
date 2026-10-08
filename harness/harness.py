"""Phase 1D single-machine validation harness; Agent claims are never evidence."""

import argparse
import contextlib
import hashlib
import json
import os
import re
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

QUESTION_TARGETS = {"ANSWERED", "ASSUMED", "BLOCKED", "INVALID"}
ROUTING = {"SIMPLE", "MODERATE", "COMPLEX", "HIGH-RISK"}
ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$")


def stamp():
    return datetime.now(timezone.utc).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(obj):
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True) + "\n").encode()


def jsonl(data):
    if data and not data.endswith(b"\n"):
        raise ValueError("partial JSONL row")
    return [json.loads(line) for line in data.splitlines()]


def read(path):
    return json.loads(path.read_bytes())


def run_path(root, run_id):
    if not ID.fullmatch(run_id):
        raise ValueError("invalid run ID")
    return Path(root).resolve() / ("RUN-" + run_id)


@contextlib.contextmanager
def writer(path):
    lock = path / ".writer.lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise RuntimeError("writer busy or stale lock; operator review required") from exc
    try:
        yield
    finally:
        os.close(fd)
        lock.unlink()


def history(path):
    return jsonl((path / "events.jsonl").read_bytes())


def last(items, kind, key, value):
    return next((x for x in reversed(items) if x["type"] == kind and x.get(key) == value), None)


def question_state(items, qid):
    change = last(items, "QUESTION_STATE_CHANGED", "question_id", qid)
    if change:
        return change["new_state"]
    return "OPEN" if last(items, "QUESTION_CREATED", "question_id", qid) else None


def task_state(items, tid):
    change = last(items, "TASK_STATE_CHANGED", "task_id", tid)
    if change:
        return change["new_state"]
    return "DRAFT" if last(items, "TASK_CREATED", "task_id", tid) else None


def assumption_state(items, aid):
    # Only creation (ISOLATED) is implemented; promotion needs a Human Gate and is out of scope.
    return "ISOLATED" if last(items, "ASSUMPTION_CREATED", "assumption_id", aid) else None


def eligibility_violations(items, task):
    """Protocol state-model invariants: P2 or any ISOLATED/CHALLENGED assumption_dep blocks ELIGIBLE."""
    reasons = []
    if task["priority"] == "P2":
        reasons.append("priority is P2")
    for dep in task.get("assumption_deps", []):
        if assumption_state(items, dep) in {"ISOLATED", "CHALLENGED"}:
            reasons.append(f"assumption_dep {dep} is ISOLATED")
    return reasons


def gate_state(items, gid):
    for kind, state in (("GATE_ANSWERED", "answered"), ("GATE_CANCELLED", "cancelled"), ("GATE_TIMEOUT", "timeout")):
        if last(items, kind, "gate_id", gid):
            return state
    return "pending" if last(items, "GATE_ISSUED", "gate_id", gid) else None


def validate(event, items):
    kind = event["type"]
    qid = event.get("question_id")
    for key in ("question_id", "assumption_id", "task_id"):
        if key in event and not ID.fullmatch(event[key]):
            raise ValueError(f"invalid {key}")
    if kind == "QUESTION_CREATED":
        if question_state(items, qid) or event["new_state"] != "OPEN" or not event["requirement_ref"]:
            raise ValueError("Question must be new, linked, and OPEN")
    elif kind == "QUESTION_STATE_CHANGED":
        if question_state(items, qid) != "OPEN" or event["new_state"] not in QUESTION_TARGETS:
            raise ValueError("invalid Question transition")
        if event["new_state"] == "ASSUMED" and event["severity"] == "Critical":
            raise ValueError("Critical Question cannot be ASSUMED")
        if event["new_state"] == "BLOCKED" and (event["severity"] != "Critical" or not any(
            e["type"] == "GATE_ISSUED" and e.get("question_id") == qid for e in items)):
            raise ValueError("BLOCKED requires Critical Question and issued Gate")
        event["previous_state"] = "OPEN"
    elif kind == "ASSUMPTION_CREATED":
        if last(items, kind, "assumption_id", event["assumption_id"]):
            raise ValueError("duplicate Assumption")
        if question_state(items, event["origin_question_id"]) != "ASSUMED":
            raise ValueError("origin Question must already be ASSUMED")
        if not all(event.get(k) for k in ("content", "default_behavior", "impact", "confidence")):
            raise ValueError("Assumption fields missing")
        event["state"] = "ISOLATED"
    elif kind == "TASK_CREATED":
        if last(items, kind, "task_id", event["task_id"]) or not event["requirement_ref"] or not event["scope"]:
            raise ValueError("Task duplicate or missing requirement/scope")
        if event["priority"] not in {"P0", "P1", "P2"}:
            raise ValueError("invalid priority")
        for dep in event.get("assumption_deps", []):
            if not ID.fullmatch(dep) or not assumption_state(items, dep):
                raise ValueError(f"unknown assumption dependency {dep}")
    elif kind == "TASK_STATE_CHANGED":
        task = last(items, "TASK_CREATED", "task_id", event["task_id"])
        if not task or task_state(items, event["task_id"]) != "DRAFT" or event["new_state"] not in {"ELIGIBLE", "BLOCKED"}:
            raise ValueError("invalid Task transition")
        reasons = eligibility_violations(items, task)
        if event["new_state"] == "ELIGIBLE" and reasons:
            raise ValueError("Task cannot be ELIGIBLE: " + "; ".join(reasons))
        if event["new_state"] == "BLOCKED" and not reasons:
            raise ValueError("Task has no blocking condition")
        event["previous_state"] = "DRAFT"
    elif kind == "TASK_ROUTING_SET":
        if not last(items, "TASK_CREATED", "task_id", event["task_id"]):
            raise ValueError("Task not created")
        if last(items, kind, "task_id", event["task_id"]) or event["routing"] not in ROUTING or not event["reason"]:
            raise ValueError("invalid Task routing")
    elif kind == "GATE_ISSUED":
        if question_state(items, qid) != "OPEN" or last(items, kind, "gate_id", event["gate_id"]):
            raise ValueError("Gate needs a new ID and OPEN Question")
    elif kind in {"GATE_STATUS_CHECK", "GATE_ANSWERED", "GATE_CANCELLED", "GATE_TIMEOUT"}:
        state = gate_state(items, event["gate_id"])
        if not state or (kind != "GATE_STATUS_CHECK" and state != "pending"):
            raise ValueError("invalid Gate event")


def append(path, kind, fields):
    with writer(path):
        if (path / "manifest.json").exists():
            raise RuntimeError("sealed run")
        run = read(path / "run.json")
        items = history(path)
        record = {"event_id": str(uuid.uuid4()), "sequence": len(items) + 1,
                  "timestamp": stamp(), "run_id": run["run_id"], "probe_id": run["probe_id"],
                  "type": kind, "source": "runtime_observer" if kind.startswith("GATE_") else "harness_cli", **fields}
        validate(record, items)
        with (path / "events.jsonl").open("ab", buffering=0) as output:
            output.write(encoded(record))
            os.fsync(output.fileno())
        return record


def start(root, run_id, probe_id, session_id, source):
    path = run_path(root, run_id)
    if not ID.fullmatch(probe_id) or not session_id:
        raise ValueError("invalid probe/session ID")
    source = Path(source).resolve(strict=True)
    raw = source.read_bytes()
    jsonl(raw)  # start only on a complete row boundary
    path.mkdir(parents=True, exist_ok=False)
    data = {"run_id": run_id, "probe_id": probe_id, "session_id": session_id,
            "source": str(source), "start_offset": len(raw), "prefix_sha256": sha(raw), "started_at": stamp()}
    data["boundary"] = "RUN_START"
    (path / "run.json").write_bytes(encoded(data))
    (path / "events.jsonl").write_bytes(b"")
    return data


def tool_answers(row):
    # toolUseResult is a dict for most tools but a plain string for errors/refusals
    outcome = row.get("toolUseResult")
    return outcome.get("answers") if isinstance(outcome, dict) else None


def blocks(row):
    return [x for x in ((row.get("message") or {}).get("content") or [])
            if isinstance(x, dict) and x.get("type") in {"tool_use", "tool_result"}]


# Claude Code rows known to carry no sessionId and no tool events.
NON_SESSION_METADATA_TYPES = {"file-history-snapshot", "file-history-delta"}


def inventory(rows, session_id):
    uses, results, gaps = {}, {}, []
    metadata_rows = 0
    for index, row in enumerate(rows, 1):
        row_session = row.get("sessionId", row.get("session_id"))
        if row_session is None:
            # Fail closed: only an allowlisted metadata type without tool blocks is exempt.
            if row.get("type") in NON_SESSION_METADATA_TYPES and not blocks(row):
                metadata_rows += 1
                continue
            gaps.append(f"unattributable row without sessionId at row {index}")
        elif row_session != session_id:
            gaps.append(f"session mismatch at row {index}")
        for item in blocks(row):
            key = item.get("id") if item["type"] == "tool_use" else item.get("tool_use_id")
            collection = uses if item["type"] == "tool_use" else results
            if not key or key in collection:
                gaps.append(f"missing/duplicate tool ID at row {index}")
            else:
                collection[key] = item.get("name") if collection is uses else index
    unmatched = set(uses) - set(results)
    orphan = set(results) - set(uses)
    ordinary = sorted(x for x in unmatched if uses[x] != "AskUserQuestion")
    if ordinary or orphan:
        gaps.append("unpaired non-Gate tool events")
    for row in rows:
        for item in blocks(row):
            if item["type"] == "tool_result" and uses.get(item.get("tool_use_id")) == "AskUserQuestion":
                answers = tool_answers(row)
                if item.get("is_error") or not isinstance(answers, dict) or not answers:
                    gaps.append("Gate tool result lacks verified human answers")
    return {"row_count": len(rows), "non_session_metadata_rows": metadata_rows, "tool_use_count": len(uses), "tool_result_count": len(results),
            "unmatched_gate_ids": sorted(x for x in unmatched if uses[x] == "AskUserQuestion"),
            "unmatched_other_ids": ordinary, "orphan_result_ids": sorted(orphan), "gaps": gaps}


def seal(path):
    with writer(path):
        return _seal_locked(path)


def _seal_locked(path):
    if (path / "manifest.json").exists():
        raise RuntimeError("already sealed")
    run = read(path / "run.json")
    source = Path(run["source"])
    gaps = []
    if not source.exists():
        raw = b""
        gaps.append("source unavailable")
    else:
        raw = source.read_bytes()
    offset = run["start_offset"]
    if len(raw) < offset or sha(raw[:offset]) != run["prefix_sha256"]:
        gaps.append("source prefix changed or truncated")
    excerpt = raw[offset:] if len(raw) >= offset else b""
    if not excerpt:
        gaps.append("no runtime events captured")
    try:
        counts = inventory(jsonl(excerpt), run["session_id"])
        gaps.extend(counts["gaps"])
    except (ValueError, json.JSONDecodeError) as exc:
        counts = None
        gaps.append(f"runtime parse failure: {exc}")
    state = (path / "events.jsonl").read_bytes()
    try:
        events = jsonl(state)
        if [e.get("sequence") for e in events] != list(range(1, len(events) + 1)):
            gaps.append("state sequence broken")
    except (ValueError, json.JSONDecodeError):
        events = []
        gaps.append("state event parse failure")
    (path / "runtime.jsonl").write_bytes(excerpt)
    manifest = {"boundary": "RUN_END", "run_id": run["run_id"], "probe_id": run["probe_id"], "session_id": run["session_id"],
                "source": run["source"], "start_offset": offset, "end_offset": len(raw),
                "runtime_sha256": sha(excerpt), "events_sha256": sha(state),
                "source_prefix_sha256": run["prefix_sha256"], "runtime_inventory": counts,
                "state_event_count": len(events), "capture_status": "INCOMPLETE" if gaps else "COMPLETE_WITHIN_BOUNDARY",
                "capture_gaps": gaps, "sealed_at": stamp(), "claim_is_trusted_evidence": False,
                "exit_code_policy": "preserve raw value when Runtime provides it; otherwise unavailable"}
    (path / "manifest.json").write_bytes(encoded(manifest))
    return manifest


def scan(path, gate_id=None):
    run = read(path / "run.json")
    raw = Path(run["source"]).read_bytes()
    offset = run["start_offset"]
    if len(raw) < offset or sha(raw[:offset]) != run["prefix_sha256"]:
        raise RuntimeError("runtime source prefix changed")
    excerpt = raw[offset:]
    if excerpt and not excerpt.endswith(b"\n"):
        excerpt = excerpt[:excerpt.rfind(b"\n") + 1] if b"\n" in excerpt else b""
    uses, results = {}, {}
    for row in jsonl(excerpt):
        for item in blocks(row):
            if item["type"] == "tool_use" and item.get("name") == "AskUserQuestion":
                uses[item["id"]] = (item, row)
            elif item["type"] == "tool_result":
                results[item.get("tool_use_id")] = (item, row)
    if gate_id is None:
        known = {e["gate_id"] for e in history(path) if e["type"] == "GATE_ISSUED"}
        gate_id = next((x for x in uses if x not in known), None)
    return gate_id, uses.get(gate_id), results.get(gate_id), offset + len(excerpt)


def gate_status(path, gate_id):
    if not last(history(path), "GATE_ISSUED", "gate_id", gate_id):
        raise ValueError("Gate not observed")
    _, use, result, watermark = scan(path, gate_id)
    if not use:
        raise RuntimeError("Gate invocation missing from runtime")
    current = gate_state(history(path), gate_id)
    if result and current == "pending":
        answers = tool_answers(result[1])
        if result[0].get("is_error") or not isinstance(answers, dict) or not answers:
            raise RuntimeError("matching Gate result has no verified human answers")
        return append(path, "GATE_ANSWERED", {"gate_id": gate_id, "answer": answers,
                                              "runtime_tool_result_id": gate_id, "watermark": watermark})
    return append(path, "GATE_STATUS_CHECK", {"gate_id": gate_id, "status": current,
                                               "watermark": watermark, "matching_result": bool(result)})


def gate_observe(path, question_id, duration, poll):
    if question_state(history(path), question_id) != "OPEN":
        raise ValueError("Question must be OPEN before observation")
    end = time.monotonic() + duration
    while time.monotonic() <= end:
        gate_id, use, _, watermark = scan(path)
        if use:
            append(path, "GATE_ISSUED", {"gate_id": gate_id, "question_id": question_id,
                                         "runtime_tool_use_id": gate_id, "runtime_prompt": use[0].get("input"),
                                         "runtime_timestamp": use[1].get("timestamp"), "watermark": watermark})
            return gate_status(path, gate_id)
        time.sleep(poll)
    raise TimeoutError("no real AskUserQuestion observed; Gate not issued")


def query(path, kind, identity):
    items = history(path)
    key = {"question": "question_id", "assumption": "assumption_id", "task": "task_id", "gate": "gate_id"}[kind]
    subset = [x for x in items if x.get(key) == identity]
    state = (question_state(items, identity) if kind == "question" else
             gate_state(items, identity) if kind == "gate" else
             task_state(items, identity) if kind == "task" else
             assumption_state(items, identity))
    route = last(items, "TASK_ROUTING_SET", "task_id", identity) if kind == "task" else None
    return {"id": identity, "state": state, "routing": route["routing"] if route else None, "history": subset}


def verify(path):
    manifest = read(path / "manifest.json")
    runtime = (path / "runtime.jsonl").read_bytes()
    events = (path / "events.jsonl").read_bytes()
    issues = []
    if sha(runtime) != manifest["runtime_sha256"]:
        issues.append("runtime hash mismatch")
    if sha(events) != manifest["events_sha256"]:
        issues.append("events hash mismatch")
    try:
        runtime_rows = jsonl(runtime)
        if inventory(runtime_rows, manifest["session_id"]) != manifest["runtime_inventory"]:
            issues.append("runtime inventory mismatch")
        rows = jsonl(events)
        if len(rows) != manifest["state_event_count"] or [x.get("sequence") for x in rows] != list(range(1, len(rows) + 1)):
            issues.append("state event sequence/count mismatch")
        invocations, answers = {}, {}
        for row in runtime_rows:
            for block in blocks(row):
                if block["type"] == "tool_use" and block.get("name") == "AskUserQuestion":
                    invocations[block["id"]] = block.get("input")
                elif block["type"] == "tool_result":
                    answers[block.get("tool_use_id")] = tool_answers(row)
        for event in rows:
            gid = event.get("gate_id")
            if event["type"] == "GATE_ISSUED" and (gid not in invocations or event.get("runtime_prompt") != invocations[gid]):
                issues.append("Gate issue has no matching runtime invocation")
            if event["type"] == "GATE_ANSWERED" and (gid not in answers or event.get("answer") != answers[gid]):
                issues.append("Gate answer has no matching human runtime result")
            if event["type"] in {"GATE_ISSUED", "GATE_STATUS_CHECK", "GATE_ANSWERED"}:
                watermark = event.get("watermark")
                within = watermark - manifest["start_offset"] if isinstance(watermark, int) else -1
                if within < 0 or within > len(runtime):
                    issues.append("Gate watermark outside sealed runtime range")
                    continue
                try:
                    prefix_rows = jsonl(runtime[:within])
                except (ValueError, json.JSONDecodeError):
                    issues.append("Gate watermark is not a complete JSONL boundary")
                    continue
                seen_use = any(b["type"] == "tool_use" and b.get("id") == gid and b.get("name") == "AskUserQuestion"
                               for r in prefix_rows for b in blocks(r))
                seen_result = any(b["type"] == "tool_result" and b.get("tool_use_id") == gid
                                  for r in prefix_rows for b in blocks(r))
                if not seen_use or (event["type"] == "GATE_STATUS_CHECK" and event.get("status") == "pending" and seen_result):
                    issues.append("Gate event disagrees with runtime at observation watermark")
    except (ValueError, json.JSONDecodeError):
        issues.append("invalid package JSONL")
    return {"valid_package": not issues, "capture_status": manifest["capture_status"],
            "issues": issues, "claim_is_trusted_evidence": False}


def inspect_order(path):
    """Compare persisted Task event receipts with the first raw Edit tool call."""
    rows = jsonl((path / "runtime.jsonl").read_bytes())
    items = history(path)
    use_names = {}
    receipts = {}
    edits = []
    for index, row in enumerate(rows, 1):
        for item in blocks(row):
            if item["type"] == "tool_use":
                use_names[item.get("id")] = item.get("name")
                if item.get("name") in {"Edit", "MultiEdit"}:
                    edits.append(index)
            elif use_names.get(item.get("tool_use_id")) in {"Bash", "PowerShell"}:
                content = json.dumps(item, ensure_ascii=False)
                for event in items:
                    if event["event_id"] in content:
                        receipts[event["event_id"]] = index
    task = next((e for e in items if e["type"] == "TASK_CREATED"), None)
    routing = next((e for e in items if e["type"] == "TASK_ROUTING_SET" and task and e["task_id"] == task["task_id"]), None)
    first_edit = min(edits) if edits else None
    create_row = receipts.get(task["event_id"]) if task else None
    routing_row = receipts.get(routing["event_id"]) if routing else None
    status = "INSUFFICIENT"
    if first_edit and create_row and routing_row:
        status = "BEFORE_EDIT" if create_row <= routing_row < first_edit else "AFTER_EDIT"
    return {"task_created_result_row": create_row, "routing_result_row": routing_row,
            "first_edit_row": first_edit, "order": status,
            "note": "Receipt matching and raw runtime order do not judge Task eligibility or routing correctness"}


def task_transition(path, task_id, state):
    """Request a Task transition. A refused request is recorded, printed with its receipt, then raised (fail closed)."""
    try:
        if not last(history(path), "TASK_CREATED", "task_id", task_id):
            raise ValueError("Task absent")
        return append(path, "TASK_STATE_CHANGED", {"task_id": task_id, "new_state": state})
    except ValueError as exc:
        refused = [append(path, "STATE_TRANSITION_REJECTED", {"task_id": task_id, "requested_state": state, "reason": str(exc)})]
        if state == "ELIGIBLE" and task_state(history(path), task_id) == "DRAFT":
            # state-model: a DRAFT Task with a blocking condition becomes BLOCKED, never ELIGIBLE
            refused.append(append(path, "TASK_STATE_CHANGED", {"task_id": task_id, "new_state": "BLOCKED"}))
        print(json.dumps(refused, ensure_ascii=False, indent=2))
        raise


def cli(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", default=str(Path(__file__).resolve().parent / "runs"))
    sub = p.add_subparsers(dest="cmd", required=True)
    def command(name, *fields):
        s = sub.add_parser(name)
        for field in fields:
            s.add_argument("--" + field.replace("_", "-"), required=True)
        return s
    command("start", "run_id", "probe_id", "session_id", "source")
    for name in ("seal", "verify", "inspect-order"):
        command(name, "run_id")
    s = command("query", "run_id")
    s.add_argument("kind", choices=("question", "assumption", "task", "gate"))
    s.add_argument("id")
    s = command("question-create", "run_id", "id", "requirement_ref", "severity")
    s.add_argument("--context", default="")
    command("question-transition", "run_id", "id", "state")
    command("assumption-create", "run_id", "id", "origin_question_id", "content", "default_behavior", "impact", "confidence")
    s = command("task-create", "run_id", "id", "requirement_ref", "priority")
    s.add_argument("--scope", nargs="+", required=True)
    s.add_argument("--assumption-dep", nargs="*", default=[])
    command("task-routing", "run_id", "id", "routing", "reason")
    command("task-transition", "run_id", "id", "state")
    s = command("gate-observe", "run_id", "question_id")
    s.add_argument("--duration", type=float, default=30)
    s.add_argument("--poll", type=float, default=0.2)
    command("gate-status", "run_id", "gate_id")
    s = command("gate-close", "run_id", "gate_id", "reason")
    s.add_argument("--state", choices=("cancelled", "timeout"), required=True)
    args = p.parse_args(argv)
    try:
        if args.cmd == "start":
            result = start(args.root, args.run_id, args.probe_id, args.session_id, args.source)
        else:
            path = run_path(args.root, args.run_id)
            if args.cmd == "seal":
                result = seal(path)
            elif args.cmd == "verify":
                result = verify(path)
            elif args.cmd == "inspect-order":
                result = inspect_order(path)
            elif args.cmd == "query":
                result = query(path, args.kind, args.id)
            elif args.cmd == "question-create":
                if args.severity not in {"Critical", "Important", "Non-Critical"}:
                    raise ValueError("invalid severity")
                result = append(path, "QUESTION_CREATED", {"question_id": args.id, "requirement_ref": args.requirement_ref,
                                                             "severity": args.severity, "context": args.context, "new_state": "OPEN", "previous_state": None})
            elif args.cmd == "question-transition":
                created = last(history(path), "QUESTION_CREATED", "question_id", args.id)
                if not created:
                    append(path, "STATE_TRANSITION_REJECTED", {"question_id": args.id, "requested_state": args.state, "reason": "Question absent"})
                    raise ValueError("Question absent")
                try:
                    result = append(path, "QUESTION_STATE_CHANGED", {"question_id": args.id, "requirement_ref": created["requirement_ref"],
                                                                       "severity": created["severity"], "new_state": args.state})
                except ValueError as exc:
                    append(path, "STATE_TRANSITION_REJECTED", {"question_id": args.id, "requested_state": args.state, "reason": str(exc)})
                    raise
            elif args.cmd == "assumption-create":
                result = append(path, "ASSUMPTION_CREATED", {"assumption_id": args.id, "origin_question_id": args.origin_question_id,
                                                              "content": args.content, "default_behavior": args.default_behavior,
                                                              "impact": args.impact, "confidence": args.confidence})
            elif args.cmd == "task-create":
                result = append(path, "TASK_CREATED", {"task_id": args.id, "requirement_ref": args.requirement_ref,
                                                        "scope": args.scope, "priority": args.priority,
                                                        "assumption_deps": args.assumption_dep})
            elif args.cmd == "task-transition":
                result = task_transition(path, args.id, args.state)
            elif args.cmd == "task-routing":
                result = append(path, "TASK_ROUTING_SET", {"task_id": args.id, "routing": args.routing, "reason": args.reason})
            elif args.cmd == "gate-observe":
                result = gate_observe(path, args.question_id, args.duration, args.poll)
            elif args.cmd == "gate-close":
                gate_status(path, args.gate_id)
                result = append(path, "GATE_CANCELLED" if args.state == "cancelled" else "GATE_TIMEOUT",
                                {"gate_id": args.gate_id, "reason": args.reason,
                                 "watermark": Path(read(path / "run.json")["source"]).stat().st_size,
                                 "note": "Operator cutoff, never a Human decision"})
            else:
                result = gate_status(path, args.gate_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, RuntimeError, TimeoutError, FileNotFoundError, KeyError) as exc:
        print(f"harness error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(cli())
