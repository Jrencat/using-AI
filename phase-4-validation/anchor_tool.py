"""C1 anchor script (Scope Conformance Contract section 8).

Run by the Human, outside the Agent's write domain. Writes the pre-run anchor A or
the post-run anchor Z. Never overwrites, never opens the workspace tree, never
builds a manifest (manifest_tool.py does that); it only hashes files it is given.
It cannot make the Human's attestation true: it sets baseline_reproduced_identical
to true only after it has compared two baseline manifest files byte for byte.

    python -I anchor_tool.py pre --run-id ID --workspace-root DIR --baseline FILE \
        --baseline-repeat FILE2 --fixture fixture.json --scenario FX-ELIGIBLE --out A.json
    python -I anchor_tool.py post --run-id ID --session-id SID --post FILE \
        --package DIR --out Z.json

Exit 0 written; 2 refused (nothing written). Refusals: output exists; output inside the
workspace root (pre) or the package (post); baseline inside the workspace root;
the two baselines differ; a required input is missing or unreadable; the scenario or
a Task is unknown; a package file is missing.
"""
import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

PACKAGE_FILES = ("run.json", "events.jsonl", "runtime.jsonl", "manifest.json")


class Refuse(Exception):
    pass


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path, what):
    try:
        with open(path, "rb") as fh:
            return fh.read()
    except OSError as e:
        raise Refuse("cannot read %s: %s" % (what, e))


def inside(child, parent):
    c, p = os.path.normcase(os.path.realpath(child)), os.path.normcase(os.path.realpath(parent))
    return c == p or c.startswith(p.rstrip(os.sep) + os.sep)


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def serialize(obj):
    return (json.dumps(obj, sort_keys=True, ensure_ascii=True, indent=1) + "\n").encode("utf-8")


def build_pre(a, recorded_at):
    if inside(a.baseline, a.workspace_root):
        raise Refuse("baseline manifest must be outside the workspace root")
    b1, b2 = read(a.baseline, "baseline"), read(a.baseline_repeat, "baseline-repeat")
    if b1 != b2:
        raise Refuse("baseline and baseline-repeat differ; baseline_reproduced_identical cannot be true")
    fx = json.loads(read(a.fixture, "fixture").decode("utf-8"))
    sc = fx.get("scenarios", {}).get(a.scenario)
    if sc is None:
        raise Refuse("unknown scenario " + a.scenario)
    tasks = []
    for t in sc["anchor_tasks"]:
        spec = fx.get("tasks", {}).get(t["task_id"])
        if spec is None:
            raise Refuse("unknown task " + t["task_id"])
        tasks.append({"task_id": t["task_id"], "priority": spec["priority"], "scope": list(spec["scope"]),
                      "expected_final_state": t["expected_final_state"]})
    root = os.path.abspath(a.workspace_root)
    return {"record_version": 1, "recorded_by": "Human", "recorded_at": recorded_at, "run_id": a.run_id,
            "workspace_root": root, "observed_root": root,
            "baseline_manifest": os.path.basename(a.baseline), "baseline_sha256": sha(b1),
            "baseline_reproduced_identical": True, "tasks": tasks}


def build_post(a, recorded_at):
    if inside(a.out, a.package):
        raise Refuse("output must be outside the package")
    pkg = {name: sha(read(os.path.join(a.package, name), "package/" + name)) for name in PACKAGE_FILES}
    return {"record_version": 1, "recorded_by": "Human", "recorded_at": recorded_at, "run_id": a.run_id,
            "session_id": a.session_id, "post_manifest_sha256": sha(read(a.post, "post manifest")),
            "package": pkg}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="mode", required=True)
    p = sub.add_parser("pre")
    for f in ("run-id", "workspace-root", "baseline", "baseline-repeat", "fixture", "scenario", "out"):
        p.add_argument("--" + f, required=True)
    q = sub.add_parser("post")
    for f in ("run-id", "session-id", "post", "package", "out"):
        q.add_argument("--" + f, required=True)
    a = ap.parse_args(argv)
    try:
        if os.path.exists(a.out):
            raise Refuse("refusing to overwrite " + a.out)
        if a.mode == "pre":
            if inside(a.out, a.workspace_root):
                raise Refuse("output must be outside the workspace root")
            obj = build_pre(a, now())
        else:
            obj = build_post(a, now())
        data = serialize(obj)
        with open(a.out, "xb") as fh:
            fh.write(data)
    except Refuse as e:
        print("refused: " + str(e), file=sys.stderr)
        return 2
    print(json.dumps({"out": a.out, "sha256": sha(data)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
