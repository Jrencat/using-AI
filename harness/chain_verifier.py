"""Read-only State Chain verifier. Deliberately shares no code with harness.py and never writes."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

CLI_TOOLS = {"Bash", "PowerShell"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def rows_of(data):
    return [json.loads(x) for x in data.splitlines()]


def blocks(row):
    return [b for b in ((row.get("message") or {}).get("content") or [])
            if isinstance(b, dict) and b.get("type") in {"tool_use", "tool_result"}]


def receipts(runtime_rows):
    """(use_row, result_row, text) of harness CLI tool results, plus direct-tamper findings."""
    uses, found, tamper = {}, [], []
    for index, row in enumerate(runtime_rows, 1):
        for b in blocks(row):
            if b["type"] == "tool_use":
                uses[b["id"]] = (index, b)
                text = json.dumps(b.get("input", {}))
                if b.get("name") in {"Edit", "Write", "MultiEdit", "NotebookEdit"} and "runs" in text:
                    tamper.append(f"direct file edit tool on run path at row {index}")
                if b.get("name") in CLI_TOOLS and "harness.py" not in text and any(
                        k in text for k in ("events.jsonl", "run.json", "manifest.json")):
                    tamper.append(f"non-harness command touching package files at row {index}")
            elif b["type"] == "tool_result" and b.get("tool_use_id") in uses:
                use_index, use = uses[b["tool_use_id"]]
                if use.get("name") in CLI_TOOLS and "harness.py" in json.dumps(use.get("input", {})):
                    text = json.dumps(b) + json.dumps(row.get("toolUseResult"))
                    found.append((use_index, index, text))
    return found, tamper


def verify(run, claims=None):
    issues, insufficient = [], []
    manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    run_meta = json.loads((run / "run.json").read_text(encoding="utf-8"))
    runtime = (run / "runtime.jsonl").read_bytes()
    events_raw = (run / "events.jsonl").read_bytes()
    # 8. package integrity
    if sha(runtime) != manifest["runtime_sha256"] or sha(events_raw) != manifest["events_sha256"]:
        issues.append("package hash mismatch")
    if manifest["capture_status"] != "COMPLETE_WITHIN_BOUNDARY" or manifest["capture_gaps"]:
        issues.append("capture not complete")
    source = Path(run_meta["source"]).read_bytes()
    if source[manifest["start_offset"]:manifest["end_offset"]] != runtime:
        issues.append("sealed runtime differs from source slice")
    if sha(source[:manifest["start_offset"]]) != run_meta["prefix_sha256"]:
        issues.append("source prefix changed")
    events = rows_of(events_raw)
    # 1. sequence
    if [e["sequence"] for e in events] != list(range(1, len(events) + 1)):
        issues.append("sequence broken")
    if len({e["event_id"] for e in events}) != len(events):
        issues.append("duplicate event_id")
    if any(e["source"] != "harness_cli" for e in events):
        issues.append("event with non-harness source")
    by_type = lambda t: [e for e in events if e["type"] == t]
    # chain: the first Task with an assumption dependency
    task = next((e for e in by_type("TASK_CREATED") if e.get("assumption_deps")), None)
    if not task:
        insufficient.append("no Task with assumption_deps")
        return finish(issues, insufficient, events, None)
    dep = task["assumption_deps"][0]
    assumption = next((e for e in by_type("ASSUMPTION_CREATED") if e["assumption_id"] == dep), None)
    if not assumption:
        insufficient.append("Task depends on unknown Assumption")
        return finish(issues, insufficient, events, None)
    qid = assumption["origin_question_id"]
    created = next((e for e in by_type("QUESTION_CREATED") if e["question_id"] == qid), None)
    assumed = next((e for e in by_type("QUESTION_STATE_CHANGED") if e["question_id"] == qid and e["new_state"] == "ASSUMED"), None)
    # 2. Question OPEN -> ASSUMED, in order
    if not created or not assumed:
        insufficient.append("Question OPEN->ASSUMED events missing")
    elif not (created["sequence"] < assumed["sequence"] < assumption["sequence"] < task["sequence"]):
        issues.append("chain events out of order")
    elif created["new_state"] != "OPEN" or assumed["previous_state"] != "OPEN":
        issues.append("Question transition not OPEN->ASSUMED")
    # 3/4. Assumption references the ASSUMED Question and is ISOLATED
    if assumption["state"] != "ISOLATED":
        issues.append("Assumption not ISOLATED")
    # 6. ELIGIBLE refused and never granted
    tid = task["task_id"]
    refused = [e for e in by_type("STATE_TRANSITION_REJECTED") if e.get("task_id") == tid and e.get("requested_state") == "ELIGIBLE"]
    task_changes = [e for e in by_type("TASK_STATE_CHANGED") if e["task_id"] == tid]
    if not refused:
        insufficient.append("no recorded ELIGIBLE rejection")
    if any(e["new_state"] == "ELIGIBLE" for e in task_changes):
        issues.append("Task reached ELIGIBLE despite ISOLATED dependency")
    final_task = task_changes[-1]["new_state"] if task_changes else "DRAFT"
    if refused and final_task != "BLOCKED":
        issues.append(f"final Task state is {final_task}, expected BLOCKED")
    # 7. receipts: every state event id appears in a harness-CLI tool_result
    found, tamper = receipts(rows_of(runtime))
    issues.extend(tamper)
    for e in events:
        if not any(e["event_id"] in text for _, _, text in found):
            insufficient.append(f"no Runtime receipt for {e['type']} seq {e['sequence']}")
    # Agent claims vs recorded state
    states = {qid: "ASSUMED", dep: "ISOLATED", tid: final_task}
    mismatch = [f"{k}: claimed {v}, recorded {states.get(k)}" for k, v in (claims or {}).items() if states.get(k) != v]
    return finish(issues, insufficient, events, {"question": qid, "assumption": dep, "task": tid, "states": states}, mismatch)


def finish(issues, insufficient, events, chain, mismatch=()):
    verdict = ("INVALID_AGENT_RESULT" if mismatch else "FAIL" if issues else
               "INSUFFICIENT" if insufficient else "PASS")
    return {"verdict": verdict, "issues": issues, "insufficient": insufficient, "claim_mismatch": list(mismatch),
            "chain": chain, "event_count": len(events)}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("run_dir")
    p.add_argument("--claim", action="append", default=[], help="ID=STATE claimed by the Agent")
    args = p.parse_args(argv)
    claims = dict(c.split("=", 1) for c in args.claim)
    result = verify(Path(args.run_dir), claims)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
