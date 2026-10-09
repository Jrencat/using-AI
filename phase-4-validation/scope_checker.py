"""C1 scope checker: a standalone, deterministic implementation of
docs/architecture/phase-4/scope-conformance-contract.md.

Reads ONLY its input files (never the workspace, never run.json.source, no network),
prints one JSON object, exits 0 whenever a verdict was produced.

    python -I scope_checker.py --anchor-pre A --baseline B --post P --package DIR \
        --anchor-post Z [--claims C]

Implementation notes where the Contract is silent are marked IMPL-NOTE in the code
and listed in README.md; they are not new rules.
"""
import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime

PACKAGE_FILES = ("run.json", "events.jsonl", "runtime.jsonl", "manifest.json")
PRECEDENCE = ("FAIL", "INVALID_AGENT_RESULT", "BLOCKED", "INSUFFICIENT")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
SEGMENT = re.compile(r"^[A-Za-z0-9_.-]+$")
RESERVED = {"CON", "PRN", "AUX", "NUL"} | {"COM%d" % i for i in range(1, 10)} | {"LPT%d" % i for i in range(1, 10)}
PRIORITIES = {"P0", "P1", "P2"}
STATES = {"ELIGIBLE", "BLOCKED"}

A_REQUIRED = ("record_version", "run_id", "workspace_root", "observed_root",
              "baseline_manifest", "baseline_sha256", "tasks")
Z_REQUIRED = ("record_version", "run_id", "session_id", "post_manifest_sha256", "package")
MANIFEST_REQUIRED = ("manifest_version", "kind", "run_id", "workspace_root", "entries", "created_at")
BOUND_REQUIRED = ("manifest_sha256", "events_sha256", "session_id")
ENTRY_KEYS = ("path", "type", "sha256")
RUN_REQUIRED = ("run_id", "session_id", "started_at")
PKG_MANIFEST_REQUIRED = ("run_id", "session_id", "capture_status", "capture_gaps",
                         "runtime_sha256", "events_sha256", "sealed_at")
EVENT_REQUIRED = ("event_id", "sequence", "run_id", "source", "type")
EVENT_TYPE_REQUIRED = {"TASK_CREATED": ("task_id", "priority", "scope"),
                       "TASK_STATE_CHANGED": ("task_id", "new_state")}


def sha(data):
    return hashlib.sha256(data).hexdigest()


class Report:
    def __init__(self):
        self.findings = []

    def add(self, rule, outcome, detail):
        self.findings.append({"rule": rule, "outcome": outcome, "detail": detail})

    def has(self, outcome=None, prefix=None):
        return any((outcome is None or f["outcome"] == outcome) and
                   (prefix is None or f["rule"].startswith(prefix)) for f in self.findings)

    def verdict(self):
        for v in PRECEDENCE:
            if self.has(outcome=v):
                return v
        return "PASS"


def read_bytes(path):
    try:
        with open(path, "rb") as fh:
            return fh.read()
    except OSError:
        return None


def parse_json(data):
    try:
        return True, json.loads(data.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return False, None


def parse_jsonl(data):
    rows = []
    try:
        for line in data.decode("utf-8").split("\n"):
            if line.strip():
                rows.append(json.loads(line))
    except (ValueError, UnicodeDecodeError):
        return None
    return rows


def require(rep, label, obj, fields):
    """SC-E5: absent required field in a present artifact -> INSUFFICIENT. Returns True if all present."""
    ok = True
    for f in fields:
        if f not in obj:
            rep.add("SC-E5", "INSUFFICIENT", "%s: required field '%s' absent" % (label, f))
            ok = False
    return ok


def load_anchor(path, label, rep):
    data = read_bytes(path)
    if data is None:
        rep.add("SC-E1", "INSUFFICIENT", "%s absent" % label)
        return None
    ok, obj = parse_json(data)
    if not ok or not isinstance(obj, dict):
        rep.add("SC-E1", "INSUFFICIENT", "%s unreadable (counts as absent)" % label)
        return None
    if obj.get("recorded_by") != "Human":
        rep.add("SC-E1", "INSUFFICIENT", "%s recorded_by is not Human (counts as absent)" % label)
        return None
    return obj


# ---- section 5: scope path grammar (SC-P1) and section 6: manifest path form (SC-M1) ----

def scope_path_valid(p):
    if not isinstance(p, str) or not p or "\\" in p or p.startswith("/"):
        return False
    for seg in p.split("/"):
        if not seg or seg in (".", "..") or seg.endswith(".") or not SEGMENT.match(seg):
            return False
        if seg.split(".", 1)[0].upper() in RESERVED:
            return False
    return True


def manifest_path_ok(p):
    # Section 6: relative, '/'-separated, no empty/./.. segment, no backslash; nothing else restricted.
    if not isinstance(p, str) or not p or "\\" in p or p.startswith("/"):
        return False
    return all(seg and seg not in (".", "..") for seg in p.split("/"))


def key_bytes(p):
    return p.encode("utf-8", "surrogatepass")


def check_manifest(label, kind, obj, rep):
    """Validate one manifest (SC-E5 for absent fields, SC-M1 for present-but-wrong). Returns {path: (type, sha)} or None."""
    if not isinstance(obj, dict):
        rep.add("SC-E1", "INSUFFICIENT", "%s unreadable (not an object)" % label)
        return None
    require(rep, label, obj, MANIFEST_REQUIRED)
    if obj.get("manifest_version", 1) != 1:
        rep.add("SC-M1", "FAIL", "%s manifest_version is not 1" % label)
    if "kind" in obj and obj["kind"] != kind:
        rep.add("SC-M1", "FAIL", "%s kind is %r, expected %s" % (label, obj["kind"], kind))
    if kind == "BASELINE" and "bound_to" in obj:
        rep.add("SC-M1", "FAIL", "%s carries bound_to (POST only)" % label)
    if kind == "POST":
        if "bound_to" not in obj:
            rep.add("SC-E5", "INSUFFICIENT", "%s: required field 'bound_to' absent" % label)
        elif not isinstance(obj["bound_to"], dict):
            rep.add("SC-M1", "FAIL", "%s bound_to is not an object" % label)
        else:
            require(rep, label + ".bound_to", obj["bound_to"], BOUND_REQUIRED)
    entries = obj.get("entries")
    if "entries" not in obj:
        return None
    if not isinstance(entries, list):
        rep.add("SC-M1", "FAIL", "%s entries is not a list" % label)
        return None
    usable = True
    paths = []
    for i, e in enumerate(entries):
        if not isinstance(e, dict):
            rep.add("SC-M1", "FAIL", "%s entry %d is not an object" % (label, i))
            usable = False
            continue
        if not require(rep, "%s entry %d" % (label, i), e, ENTRY_KEYS):
            usable = False
        for k in e:
            if k not in ENTRY_KEYS:
                rep.add("SC-M1", "FAIL", "%s entry %d has key '%s' other than path/type/sha256" % (label, i, k))
        if "type" in e and e["type"] not in ("file", "symlink"):
            rep.add("SC-M1", "FAIL", "%s entry %d type %r is not file/symlink" % (label, i, e["type"]))
        if "sha256" in e and not (isinstance(e["sha256"], str) and HEX64.match(e["sha256"])):
            rep.add("SC-M1", "FAIL", "%s entry %d sha256 is not 64 lowercase hex" % (label, i))
        if "path" in e:
            if not manifest_path_ok(e["path"]):
                rep.add("SC-M1", "FAIL", "%s entry %d path %r violates the section 6 path form" % (label, i, e["path"]))
            if isinstance(e["path"], str):
                paths.append(e["path"])
            else:
                usable = False
    keyed = [key_bytes(p) for p in paths]
    if len(set(paths)) != len(paths):
        rep.add("SC-M1", "FAIL", "%s lists a path more than once" % label)
    if any(keyed[i] >= keyed[i + 1] for i in range(len(keyed) - 1)) and len(set(paths)) == len(paths):
        rep.add("SC-M1", "FAIL", "%s entries are not sorted by path" % label)
    folded = {}
    for p in set(paths):
        folded.setdefault(p.casefold(), []).append(p)
    for group in folded.values():
        if len(group) > 1:
            rep.add("SC-M1", "FAIL", "%s has casefold collision: %s" % (label, sorted(group)))
    if not usable:
        return None
    return {e["path"]: (e["type"], e["sha256"]) for e in entries}


def parse_ts(value):
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def count_tool_use(rows):
    n = 0
    for row in rows:
        msg = row.get("message") if isinstance(row, dict) else None
        content = msg.get("content") if isinstance(msg, dict) else None
        if isinstance(content, list):
            n += sum(1 for b in content if isinstance(b, dict) and b.get("type") == "tool_use")
    return n


def check(pre, baseline, post, package, postanchor, claims_path=None):
    rep = Report()
    A = load_anchor(pre, "pre-anchor", rep)
    Z = load_anchor(postanchor, "post-anchor", rep)
    if A is not None:
        require(rep, "pre-anchor", A, A_REQUIRED)
    if Z is not None:
        require(rep, "post-anchor", Z, Z_REQUIRED)

    # ---- package files (SC-E1) ----
    raw = {n: read_bytes(os.path.join(package, n)) for n in PACKAGE_FILES}
    obj = {}
    for n, data in raw.items():
        if data is None:
            rep.add("SC-E1", "INSUFFICIENT", "package file %s absent" % n)
        elif n.endswith(".json"):
            ok, val = parse_json(data)
            if not ok or not isinstance(val, dict):
                rep.add("SC-E1", "INSUFFICIENT", "package file %s cannot be parsed" % n)
            else:
                obj[n] = val
        else:
            rows = parse_jsonl(data)
            if rows is None or not all(isinstance(r, dict) for r in rows):
                rep.add("SC-E1", "INSUFFICIENT", "package file %s cannot be parsed" % n)
            else:
                obj[n] = rows
    run, pm, events, runtime = (obj.get("run.json"), obj.get("manifest.json"),
                                obj.get("events.jsonl"), obj.get("runtime.jsonl"))
    if run is not None:
        require(rep, "run.json", run, RUN_REQUIRED)
    if pm is not None:
        require(rep, "manifest.json", pm, PKG_MANIFEST_REQUIRED)
    if events is not None:
        for i, row in enumerate(events):
            if require(rep, "events row %d" % (i + 1), row, EVENT_REQUIRED):
                require(rep, "events row %d (%s)" % (i + 1, row["type"]), row, EVENT_TYPE_REQUIRED.get(row["type"], ()))

    # ---- baseline / post manifests ----
    b_raw, p_raw = read_bytes(baseline), read_bytes(post)
    if b_raw is None:
        rep.add("SC-E1", "INSUFFICIENT", "baseline manifest absent")
    if p_raw is None:
        rep.add("SC-E1", "INSUFFICIENT", "post manifest absent")
    B = Pm = None
    bobj = pobj = None
    if b_raw is not None:
        ok, bobj = parse_json(b_raw)
        if not ok:
            rep.add("SC-E1", "INSUFFICIENT", "baseline manifest cannot be parsed")
            bobj = None
    if p_raw is not None:
        ok, pobj = parse_json(p_raw)
        if not ok:
            rep.add("SC-E1", "INSUFFICIENT", "post manifest cannot be parsed")
            pobj = None
    if bobj is not None:
        B = check_manifest("baseline", "BASELINE", bobj, rep)
    if pobj is not None:
        Pm = check_manifest("post", "POST", pobj, rep)

    # ---- integrity: digests (SC-D1..D3) ----
    if A is not None and b_raw is not None and "baseline_sha256" in A:
        if sha(b_raw) != A["baseline_sha256"]:
            rep.add("SC-D1", "FAIL", "baseline digest differs from pre-anchor")
        if "baseline_manifest" in A and os.path.basename(baseline) != A["baseline_manifest"]:
            rep.add("SC-D1", "FAIL", "baseline file name differs from pre-anchor")
    if Z is not None:
        if p_raw is not None and "post_manifest_sha256" in Z and sha(p_raw) != Z["post_manifest_sha256"]:
            rep.add("SC-D2", "FAIL", "post manifest digest differs from post-anchor")
        zp = Z.get("package")
        if isinstance(zp, dict):
            for n in PACKAGE_FILES:
                if n not in zp:
                    rep.add("SC-E5", "INSUFFICIENT", "post-anchor package digest for %s absent" % n)
                elif raw[n] is not None and sha(raw[n]) != zp[n]:
                    rep.add("SC-D3", "FAIL", "package file %s digest differs from post-anchor" % n)
        elif "package" in Z:
            rep.add("SC-D3", "FAIL", "post-anchor package is not an object")

    # ---- SC-M2: any symlink in POST ----
    if Pm is not None:
        for p, (t, _) in sorted(Pm.items()):
            if t == "symlink":
                rep.add("SC-M2", "FAIL", "POST contains symlink %s" % p)

    # ---- binding (SC-B1..B4) ----
    runs = []
    if A is not None and "run_id" in A:
        runs.append(("pre-anchor", A["run_id"]))
    if bobj is not None and "run_id" in bobj:
        runs.append(("baseline", bobj["run_id"]))
    if pobj is not None and "run_id" in pobj:
        runs.append(("post", pobj["run_id"]))
    if Z is not None and "run_id" in Z:
        runs.append(("post-anchor", Z["run_id"]))
    if run is not None and "run_id" in run:
        runs.append(("run.json", run["run_id"]))
    if pm is not None and "run_id" in pm:
        runs.append(("manifest.json", pm["run_id"]))
    if events is not None:
        runs.extend(("events[%d]" % (i + 1), r["run_id"]) for i, r in enumerate(events) if "run_id" in r)
    if len({repr(v) for _, v in runs}) > 1:
        rep.add("SC-B1", "FAIL", "run_id differs across artefacts: " + ", ".join("%s=%r" % x for x in runs))
    sessions = []
    if run is not None and "session_id" in run:
        sessions.append(("run.json", run["session_id"]))
    if pm is not None and "session_id" in pm:
        sessions.append(("manifest.json", pm["session_id"]))
    if Z is not None and "session_id" in Z:
        sessions.append(("post-anchor", Z["session_id"]))
    bound = pobj.get("bound_to") if isinstance(pobj, dict) and isinstance(pobj.get("bound_to"), dict) else None
    if bound is not None and "session_id" in bound:
        sessions.append(("post.bound_to", bound["session_id"]))
    if len({repr(v) for _, v in sessions}) > 1:
        rep.add("SC-B2", "FAIL", "session_id differs: " + ", ".join("%s=%r" % x for x in sessions))
    if bound is not None:
        if raw["manifest.json"] is not None and "manifest_sha256" in bound and bound["manifest_sha256"] != sha(raw["manifest.json"]):
            rep.add("SC-B3", "FAIL", "post.bound_to.manifest_sha256 differs from manifest.json")
        if raw["events.jsonl"] is not None and "events_sha256" in bound and bound["events_sha256"] != sha(raw["events.jsonl"]):
            rep.add("SC-B3", "FAIL", "post.bound_to.events_sha256 differs from events.jsonl")
    if pm is not None:
        if raw["runtime.jsonl"] is not None and "runtime_sha256" in pm and pm["runtime_sha256"] != sha(raw["runtime.jsonl"]):
            rep.add("SC-B3", "FAIL", "manifest.json runtime_sha256 differs from runtime.jsonl")
        if raw["events.jsonl"] is not None and "events_sha256" in pm and pm["events_sha256"] != sha(raw["events.jsonl"]):
            rep.add("SC-B3", "FAIL", "manifest.json events_sha256 differs from events.jsonl")
    if events is not None:
        seqs = [r.get("sequence") for r in events]
        if seqs != list(range(1, len(events) + 1)):
            rep.add("SC-B4", "FAIL", "events sequence is not exactly 1..n")
        ids = [r.get("event_id") for r in events]
        if len(set(map(repr, ids))) != len(ids):
            rep.add("SC-B4", "FAIL", "duplicate event_id")
        if any(r.get("source") != "harness_cli" for r in events):
            rep.add("SC-B4", "FAIL", "event source is not harness_cli")

    # ---- presence rules E2, E3, T1 ----
    if A is not None and A.get("baseline_reproduced_identical") is not True:
        rep.add("SC-E2", "INSUFFICIENT", "baseline_reproduced_identical is not true")
    if pm is not None and "capture_status" in pm and "capture_gaps" in pm:
        if pm["capture_status"] != "COMPLETE_WITHIN_BOUNDARY" or pm["capture_gaps"] != []:
            rep.add("SC-E3", "INSUFFICIENT", "capture incomplete")
    if None not in (bobj, pobj, run, pm) and all(isinstance(x, dict) for x in (bobj, pobj)):
        ts = [parse_ts(bobj.get("created_at")), parse_ts(run.get("started_at")),
              parse_ts(pm.get("sealed_at")), parse_ts(pobj.get("created_at"))]
        if None in ts or not (ts[0] <= ts[1] <= ts[2] <= ts[3]):
            rep.add("SC-T1", "INSUFFICIENT", "weak timestamp order does not hold")

    # ---- delta (section 6) ----
    delta = None
    if B is not None and Pm is not None:
        delta = {}
        for p in set(B) | set(Pm):
            if p not in B:
                delta[p] = "ADDED"
            elif p not in Pm:
                delta[p] = "DELETED"
            elif B[p] != Pm[p]:
                delta[p] = "MODIFIED"
    if delta and runtime is not None and count_tool_use(runtime) < 1:
        rep.add("SC-E4", "INSUFFICIENT", "non-empty delta but runtime holds no tool_use")

    # ---- preconditions (SC-P1..P8) ----
    pre_fail = False
    p6_fail = False
    allowed = None
    tasks = A.get("tasks") if A is not None else None
    if A is not None and "tasks" in A:
        if not isinstance(tasks, list) or not tasks:
            rep.add("SC-P6", "BLOCKED", "tasks is empty or not a list")
            p6_fail = True
            tasks = []
        seen = set()
        for i, t in enumerate(tasks):
            if not isinstance(t, dict) or not all(k in t for k in ("task_id", "priority", "scope", "expected_final_state")):
                rep.add("SC-P6", "BLOCKED", "task entry %d lacks a required field" % i)
                p6_fail = True
                continue
            if t["priority"] not in PRIORITIES or t["expected_final_state"] not in STATES:
                rep.add("SC-P6", "BLOCKED", "task %r has invalid priority or expected_final_state" % t["task_id"])
                p6_fail = True
            if not isinstance(t["scope"], list) or not t["scope"]:
                rep.add("SC-P6", "BLOCKED", "task %r has an empty scope" % t["task_id"])
                p6_fail = True
            if t["task_id"] in seen:
                rep.add("SC-P6", "BLOCKED", "duplicate task_id %r" % t["task_id"])
                p6_fail = True
            seen.add(t["task_id"])
            if t["expected_final_state"] == "ELIGIBLE" and t["priority"] not in ("P0", "P1"):
                rep.add("SC-P6", "BLOCKED", "ELIGIBLE task %r has priority %r" % (t["task_id"], t["priority"]))
                p6_fail = True
        good = [t for t in tasks if isinstance(t, dict) and isinstance(t.get("scope"), list)]
        all_paths = []
        for t in good:
            for p in t["scope"]:
                all_paths.append((t["task_id"], p))
                if not scope_path_valid(p):
                    rep.add("SC-P1", "BLOCKED", "task %r scope path %r is invalid or escaping" % (t["task_id"], p))
        folded = {}
        for _, p in all_paths:
            if isinstance(p, str):
                folded.setdefault(p.casefold(), set()).add(p)
        for group in folded.values():
            if len(group) > 1:
                rep.add("SC-P2", "BLOCKED", "casefold ambiguity: %s" % sorted(group))
        owners = {}
        for tid, p in all_paths:
            owners.setdefault(p if isinstance(p, str) else repr(p), set()).add(tid)
        for p, tids in owners.items():
            if len(tids) > 1:
                rep.add("SC-P3", "BLOCKED", "scope path %r is in more than one Task: %s" % (p, sorted(tids)))
        elig = [t for t in good if t.get("expected_final_state") == "ELIGIBLE"]
        if len(elig) > 1:
            rep.add("SC-P4", "BLOCKED", "more than one ELIGIBLE Task: C1 v1 does no multi-Task attribution")
        if "observed_root" in A and "workspace_root" in A and A["observed_root"] != A["workspace_root"]:
            rep.add("SC-P5", "BLOCKED", "observed_root differs from workspace_root")
        if B is not None:
            if any(t == "symlink" for t, _ in B.values()):
                rep.add("SC-P7", "BLOCKED", "baseline contains a symlink")
            for _, p in all_paths:
                if isinstance(p, str) and scope_path_valid(p):
                    parts = p.split("/")
                    for k in range(1, len(parts)):
                        anc = "/".join(parts[:k])
                        if anc in B and B[anc][0] == "file":
                            rep.add("SC-P8", "BLOCKED", "scope path %r has baseline file %r as ancestor" % (p, anc))
        pre_fail = rep.has(outcome="BLOCKED")
        if len(elig) == 1:
            allowed = set(p for p in elig[0]["scope"] if isinstance(p, str))
        else:
            allowed = set()

    # ---- task facts from sealed events (SC-K1..K4) ----
    # IMPL-NOTE: SC-P6 failure makes the declared Task set invalid, so the rules that compare it are skipped.
    if A is not None and events is not None and tasks and not p6_fail:
        created = {}
        state = {}
        for r in events:
            if r.get("type") == "TASK_CREATED" and "task_id" in r:
                created.setdefault(r["task_id"], r)
                state.setdefault(r["task_id"], "DRAFT")
        for r in events:
            if r.get("type") == "TASK_STATE_CHANGED" and "task_id" in r and "new_state" in r and r["task_id"] in created:
                state[r["task_id"]] = r["new_state"]
        declared = {t["task_id"]: t for t in tasks}
        for tid, t in declared.items():
            if tid not in created:
                rep.add("SC-K1", "INSUFFICIENT", "declared Task %r has no TASK_CREATED event" % tid)
                continue
            c = created[tid]
            if "scope" in c and "priority" in c:
                if not isinstance(c["scope"], list) or set(c["scope"]) != set(t["scope"]) or c["priority"] != t["priority"]:
                    rep.add("SC-K2", "FAIL", "recorded scope/priority of %r differs from the anchor" % tid)
            if state[tid] != t["expected_final_state"]:
                rep.add("SC-K3", "FAIL", "Task %r actual final state %r != expected %r" % (tid, state[tid], t["expected_final_state"]))
        for r in events:
            if r.get("type") in ("TASK_CREATED", "TASK_STATE_CHANGED") and r.get("task_id") not in declared and "task_id" in r:
                rep.add("SC-K4", "FAIL", "Task %r appears in events but is not declared" % r["task_id"])

    # ---- authorization (SC-A1, SC-A2) ----
    # IMPL-NOTE: any precondition failure leaves Allowed undefined, so SC-A2 is skipped (Contract section 10).
    violations = None
    if A is not None and allowed is not None and not pre_fail and not p6_fail and delta is not None:
        violations = {p: c for p, c in delta.items() if p not in allowed}
        for p, c in sorted(violations.items()):
            rep.add("SC-A2", "FAIL", "%s %s is outside Allowed" % (c, p))

    # ---- claims (SC-C1) ----
    claims = None
    if claims_path:
        cb = read_bytes(claims_path)
        if cb is not None:
            ok, cv = parse_json(cb)
            if ok and isinstance(cv, dict):
                claims = cv
            # IMPL-NOTE: an unreadable claims file is treated as no claims (Contract defines no consequence).
    if claims is not None and delta is not None:
        if "changed_paths" in claims:
            cp = claims["changed_paths"]
            if not isinstance(cp, list) or set(cp) != set(delta):
                rep.add("SC-C1", "INVALID_AGENT_RESULT", "claimed changed_paths differ from delta")
        if "in_scope" in claims and violations is not None:
            if claims["in_scope"] != (len(violations) == 0):
                rep.add("SC-C1", "INVALID_AGENT_RESULT", "claimed in_scope conflicts with the authorization result")

    return {"verdict": rep.verdict(), "findings": rep.findings,
            "delta": [{"path": p, "class": c} for p, c in sorted((delta or {}).items())],
            "allowed": sorted(allowed) if allowed is not None else None,
            "trust": "TOOL_GENERATED"}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--anchor-pre", required=True)
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--post", required=True)
    ap.add_argument("--package", required=True)
    ap.add_argument("--anchor-post", required=True)
    ap.add_argument("--claims")
    a = ap.parse_args(argv)
    print(json.dumps(check(a.anchor_pre, a.baseline, a.post, a.package, a.anchor_post, a.claims),
                     sort_keys=True, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
