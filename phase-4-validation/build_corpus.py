"""C1 corpus builder: realises the abstract cases of a locked corpus as input files.

Reads ONLY the corpus JSON. It never reads expected verdicts, never imports the
checker and never runs it. For each case it writes, under OUT/<case_id>/:

    anchor-pre.json  baseline.json  post.json  package/{run,manifest}.json
    package/{events,runtime}.jsonl  anchor-post.json  [claims.json]

plus OUT/index.json mapping case_id -> argument paths for scope_checker.py.
A path in the index may point at a file that is intentionally absent (missing-evidence cases).

    python -I build_corpus.py --corpus c1-negative-corpus-v3.json --out DIR
"""
import argparse
import hashlib
import json
import os
import sys

RUN = "RUN-C1-CORPUS"
SESSION = "SESSION-C1-CORPUS"
T_BASE, T_START, T_SEAL, T_POST = ("2026-01-01T00:00:00Z", "2026-01-01T00:10:00Z",
                                    "2026-01-01T00:20:00Z", "2026-01-01T00:30:00Z")
BASE_FILES = ("README.txt", "src/a.py", "src/b.py", "src/c.py")
PACKAGE_FILES = ("run.json", "events.jsonl", "runtime.jsonl", "manifest.json")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fsha(tag, path):
    return sha(("%s:%s" % (tag, path)).encode("utf-8"))


def dumps(obj):
    return (json.dumps(obj, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")


def parse_task(spec):
    tid, prio, state, scope = spec.split("|", 3)
    return {"task_id": tid, "priority": prio, "expected_final_state": state,
            "scope": [s for s in scope.split(",") if s]}


def parse_op(text):
    name, _, rest = text.partition(":")
    return name, (rest.split("|") if rest else [])


def entries_of(mapping):
    return [{"path": p, "type": t, "sha256": h}
            for p, (t, h) in sorted(mapping.items(), key=lambda kv: kv[0].encode("utf-8", "surrogatepass"))]


def task_events(task, final_state=None):
    """Event rows (without ids/sequence) for a task ending in final_state (default: its expected state)."""
    st = task["expected_final_state"] if final_state is None else final_state
    rows = [{"type": "TASK_CREATED", "task_id": task["task_id"], "priority": task["priority"],
             "scope": list(task["scope"])}]
    if st == "BLOCKED":
        rows.append({"type": "STATE_TRANSITION_REJECTED", "task_id": task["task_id"], "requested_state": "ELIGIBLE",
                     "reason": "blocked"})
        rows.append({"type": "TASK_STATE_CHANGED", "task_id": task["task_id"], "previous_state": "DRAFT", "new_state": "BLOCKED"})
    elif st != "DRAFT":
        rows.append({"type": "TASK_STATE_CHANGED", "task_id": task["task_id"], "previous_state": "DRAFT", "new_state": st})
    return rows


def build_case(case, profiles):
    """Return {relative file name: bytes or None(absent)} and the claims bytes for one case."""
    c = case["construction"]
    tasks = [parse_task(t) for t in (c.get("tasks") if c.get("tasks") is not None else profiles[c["profile"]])]
    ops = [parse_op(o) for o in c.get("ops", [])]
    names = [n for n, _ in ops]

    def arg(name):
        return [a for n, a in ops if n == name]

    def has(name):
        return name in names

    # ---- workspace states ----
    base = {p: ("file", fsha("baseline", p)) for p in BASE_FILES}
    for n, a in ops:
        if n == "baseline.symlink":
            base[a[0]] = ("symlink", fsha("link", a[0]))
        elif n == "baseline.remove_path":
            base.pop(a[0], None)
        elif n == "manifest.both.raw_path":
            base[a[0]] = ("file", fsha("raw", a[0]))
    post = dict(base)
    for n, a in ops:
        if n == "post.modify":
            post[a[0]] = ("file", fsha("modified", a[0]))
        elif n == "post.add":
            post[a[0]] = ("file", fsha("added", a[0]))
        elif n == "post.delete":
            post.pop(a[0], None)
        elif n == "post.set_file":
            post[a[0]] = ("file", fsha("setfile", a[0]))
        elif n == "post.symlink":
            post[a[0]] = ("symlink", fsha("link-post", a[0]))
        elif n == "post.case_rename":
            post[a[1]] = post.pop(a[0])
        elif n == "manifest.post.casefold_pair":
            for p in a:
                post[p] = ("file", fsha("added", p))
        # post.rewrite_identical: identical bytes -> no change

    # ---- events ----
    rows = []
    finals = {t["task_id"]: t["expected_final_state"] for t in tasks}
    for n, a in ops:
        if n == "events.final_state":
            tid, s = a[0].split("=", 1)
            finals[tid] = s
    for t in tasks:
        rows.extend(task_events(t, finals[t["task_id"]]))
    for n, a in ops:
        if n == "events.scope":
            tid, s = a[0].split("=", 1)
            for r in rows:
                if r["type"] == "TASK_CREATED" and r["task_id"] == tid:
                    r["scope"] = [x for x in s.split(",") if x]
        elif n == "events.priority":
            tid, s = a[0].split("=", 1)
            for r in rows:
                if r["type"] == "TASK_CREATED" and r["task_id"] == tid:
                    r["priority"] = s
        elif n == "events.drop_created":
            rows = [r for r in rows if not (r["type"] == "TASK_CREATED" and r["task_id"] == a[0])]
        elif n == "events.add_task":
            tid, st, prio, scope = a
            rows.extend(task_events({"task_id": tid, "priority": prio, "expected_final_state": st,
                                     "scope": [x for x in scope.split(",") if x]}))
        elif n == "events.add_unknown_type":
            rows.append({"type": a[0]})
    if has("events.empty"):
        rows = []
    for i, r in enumerate(rows):
        r.update({"event_id": "EVT-%04d" % (i + 1), "sequence": i + 1, "run_id": RUN, "source": "harness_cli"})
    if has("events.sequence_gap"):
        for i in range(1, len(rows)):  # 1,3,4,... (a gap even when only two rows exist)
            rows[i]["sequence"] += 1
    if has("events.duplicate_event_id") and len(rows) > 1:
        rows[1]["event_id"] = rows[0]["event_id"]
    if has("events.source") and rows:
        rows[0]["source"] = arg("events.source")[0][0]
    if has("events.run_id") and rows:
        rows[0]["run_id"] = arg("events.run_id")[0][0]
    events_b = b"".join(dumps(r) for r in rows)

    # ---- runtime ----
    rt = [{"type": "user", "sessionId": SESSION, "message": {"role": "user", "content": "work"}}]
    if has("runtime.zero_tool_use"):
        rt.append({"type": "assistant", "sessionId": SESSION, "message": {"content": [{"type": "text", "text": "done"}]}})
    else:
        rt.append({"type": "assistant", "sessionId": SESSION, "message": {"content": [
            {"type": "tool_use", "id": "toolu_1", "name": "Edit", "input": {"file_path": "src/a.py"}}]}})
        rt.append({"type": "user", "sessionId": SESSION, "message": {"content": [
            {"type": "tool_result", "tool_use_id": "toolu_1", "content": "ok"}]}})
    runtime_b = b"".join(dumps(r) for r in rt)

    # ---- package manifest.json / run.json ----
    pm = {"boundary": "RUN_END", "run_id": RUN, "probe_id": "C1-CORPUS", "session_id": SESSION,
          "capture_status": "COMPLETE_WITHIN_BOUNDARY", "capture_gaps": [], "sealed_at": T_SEAL,
          "runtime_sha256": sha(runtime_b), "events_sha256": sha(events_b)}
    if has("capture.status"):
        pm["capture_status"] = arg("capture.status")[0][0]
        pm["capture_gaps"] = ["capture incomplete"]
    if has("capture.gaps"):
        pm["capture_gaps"] = ["gap"]
    if has("manifest_json.run_id"):
        pm["run_id"] = arg("manifest_json.run_id")[0][0]
    if has("manifest_json.session_id"):
        pm["session_id"] = arg("manifest_json.session_id")[0][0]
    if has("manifest_json.runtime_sha"):
        pm["runtime_sha256"] = sha(b"wrong-runtime")
    if has("manifest_json.events_sha"):
        pm["events_sha256"] = sha(b"wrong-events")
    manifest_b = dumps(pm)
    rj = {"run_id": RUN, "session_id": SESSION, "probe_id": "C1-CORPUS", "started_at": T_START, "boundary": "RUN_START"}
    if has("run_json.run_id"):
        rj["run_id"] = arg("run_json.run_id")[0][0]
    run_b = dumps(rj)

    # ---- baseline / post manifests ----
    bobj = {"manifest_version": 1, "kind": "BASELINE", "run_id": RUN, "workspace_root": "WORKSPACE",
            "entries": entries_of(base), "created_at": T_BASE}
    pobj = {"manifest_version": 1, "kind": "POST", "run_id": RUN, "workspace_root": "WORKSPACE",
            "entries": entries_of(post), "created_at": T_POST,
            "bound_to": {"manifest_sha256": sha(manifest_b), "events_sha256": sha(events_b), "session_id": SESSION}}
    if has("baseline.run_id"):
        bobj["run_id"] = arg("baseline.run_id")[0][0]
    if has("post.run_id"):
        pobj["run_id"] = arg("post.run_id")[0][0]
    if has("timestamps.post_before_seal"):
        pobj["created_at"] = "2026-01-01T00:15:00Z"
    bt = pobj["bound_to"]
    if has("post.bound_to.session_id"):
        bt["session_id"] = arg("post.bound_to.session_id")[0][0]
    if has("post.bound_to.manifest_sha"):
        bt["manifest_sha256"] = sha(b"wrong-bound-manifest")
    if has("post.bound_to.events_sha"):
        bt["events_sha256"] = sha(b"wrong-bound-events")
    if has("post.omit_bound_to"):
        del pobj["bound_to"]
    if has("manifest.baseline.add_bound_to"):
        bobj["bound_to"] = {"manifest_sha256": "0" * 64, "events_sha256": "0" * 64, "session_id": SESSION}
    if has("manifest.post.kind"):
        pobj["kind"] = arg("manifest.post.kind")[0][0]
    for a in arg("manifest.baseline.duplicate_path"):
        bobj["entries"].append(dict(next(e for e in bobj["entries"] if e["path"] == a[0])))
    for a in arg("manifest.post.bad_type"):
        next(e for e in pobj["entries"] if e["path"] == a[0])["type"] = "dir"
    for a in arg("manifest.post.bad_sha"):
        next(e for e in pobj["entries"] if e["path"] == a[0])["sha256"] = "zz"
    if has("manifest.post.unsorted"):
        pobj["entries"].reverse()
    baseline_b = dumps(bobj)
    post_honest_b = dumps(pobj)
    post_b = post_honest_b
    for a in arg("post.forge_hide"):
        forged = json.loads(post_honest_b.decode("utf-8"))
        for e in forged["entries"]:
            if e["path"] == a[0]:
                e["type"], e["sha256"] = base[a[0]]
        post_b = dumps(forged)
    if has("baseline.unparseable"):
        baseline_b = b"this is not json\n"
    if has("post.unparseable"):
        post_b = post_honest_b = b"this is not json\n"

    # ---- anchors (digests computed over the bytes as originally anchored) ----
    A = {"record_version": 1, "recorded_by": "Human", "recorded_at": "2026-01-01T00:00:00Z", "run_id": RUN,
         "workspace_root": "WORKSPACE", "observed_root": "WORKSPACE",
         "baseline_manifest": "baseline.json", "baseline_sha256": sha(baseline_b),
         "baseline_reproduced_identical": True,
         "tasks": [{"task_id": t["task_id"], "priority": t["priority"], "scope": list(t["scope"]),
                    "expected_final_state": t["expected_final_state"]} for t in tasks]}
    pkg_bytes = {"run.json": run_b, "events.jsonl": events_b, "runtime.jsonl": runtime_b, "manifest.json": manifest_b}
    Z = {"record_version": 1, "recorded_by": "Human", "recorded_at": "2026-01-01T00:40:00Z", "run_id": RUN,
         "session_id": SESSION, "post_manifest_sha256": sha(post_honest_b if has("post.forge_hide") else post_b),
         "package": {n: sha(b) for n, b in pkg_bytes.items()}}
    for a in arg("anchor.pre.run_id"):
        A["run_id"] = a[0]
    for a in arg("anchor.pre.recorded_by"):
        A["recorded_by"] = a[0]
    for a in arg("anchor.pre.reproduced"):
        if a[0] == "omit":
            del A["baseline_reproduced_identical"]
        else:
            A["baseline_reproduced_identical"] = (a[0] == "true")
    if has("anchor.pre.observed_root"):
        A["observed_root"] = "WORKSPACE-OTHER"
    for a in arg("anchor.pre.baseline_manifest_name"):
        A["baseline_manifest"] = a[0]
    for a in arg("anchor.post.run_id"):
        Z["run_id"] = a[0]
    for a in arg("anchor.post.session_id"):
        Z["session_id"] = a[0]
    for a in arg("anchor.post.recorded_by"):
        Z["recorded_by"] = a[0]
    if has("anchor.post.post_manifest_sha"):
        Z["post_manifest_sha256"] = sha(b"wrong-post")
    for a in arg("anchor.post.package_sha"):
        Z["package"][a[0]] = sha(b"wrong-package")
    for a in arg("anchor.post.package_omit"):
        Z["package"].pop(a[0], None)
    for a in arg("anchor.post.package_extra_key"):
        Z["package"][a[0]] = sha(b"extra")

    # ---- tamper after anchoring ----
    if has("stale.baseline_bytes"):
        baseline_b += b" "
    if has("stale.post_bytes"):
        post_b += b" "
    for a in arg("stale.package_file"):
        pkg_bytes[a[0]] += b" "

    files = {"baseline.json": baseline_b, "post.json": post_b,
             "anchor-pre.json": dumps(A), "anchor-post.json": dumps(Z)}
    for n, b in pkg_bytes.items():
        files["package/" + n] = b
    if has("anchor.pre.unreadable"):
        files["anchor-pre.json"] = b"{not json"
    if has("anchor.post.unreadable"):
        files["anchor-post.json"] = b"{not json"
    absent = set()
    if has("anchor.pre.drop"):
        absent.add("anchor-pre.json")
    if has("anchor.post.drop"):
        absent.add("anchor-post.json")
    if has("baseline.drop"):
        absent.add("baseline.json")
    if has("post.drop"):
        absent.add("post.json")
    for a in arg("package.drop"):
        absent.add("package/" + a[0])
    if has("package.drop_dir"):
        absent.update("package/" + n for n in PACKAGE_FILES)
    for k in absent:
        files.pop(k, None)
    for a in arg("package.add_extra_file"):
        files["package/" + a[0]] = b"extra content\n"
    if c.get("claims") is not None:
        files["claims.json"] = dumps(c["claims"])
    return files


def build_all(corpus, out):
    os.makedirs(out, exist_ok=True)
    index = {}
    for case in corpus["cases"]:
        files = build_case(case, corpus["profiles"])
        root = os.path.join(out, case["case_id"])
        for rel, data in files.items():
            path = os.path.join(root, *rel.split("/"))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "xb") as fh:
                fh.write(data)
        os.makedirs(root, exist_ok=True)
        entry = {"anchor_pre": os.path.join(root, "anchor-pre.json"), "baseline": os.path.join(root, "baseline.json"),
                 "post": os.path.join(root, "post.json"), "package": os.path.join(root, "package"),
                 "anchor_post": os.path.join(root, "anchor-post.json")}
        if "claims.json" in files:
            entry["claims"] = os.path.join(root, "claims.json")
        index[case["case_id"]] = entry
    return index


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--out", required=True, help="must not already exist")
    a = ap.parse_args(argv)
    if os.path.exists(a.out):
        print("refusing to write into existing " + a.out, file=sys.stderr)
        return 2
    with open(a.corpus, "rb") as fh:
        corpus = json.loads(fh.read().decode("utf-8"))
    index = build_all(corpus, a.out)
    with open(os.path.join(a.out, "index.json"), "xb") as fh:
        fh.write(dumps(index))
    print(json.dumps({"cases": len(index), "out": a.out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
