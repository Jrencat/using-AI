"""C1 manifest tool (Scope Conformance Contract section 6).

Walks an observed root and writes a BASELINE or POST manifest. Never follows
symlinks or Windows reparse points (they are recorded as type "symlink"),
has no ignore list, records only path/type/sha256 of files and symlinks, and
fails closed on anything it cannot classify. It reads only the observed root.

    python -I manifest_tool.py --root DIR --kind BASELINE --run-id ID --out FILE
    python -I manifest_tool.py --root DIR --kind POST --run-id ID --out FILE \
        --bound-manifest PKG/manifest.json --bound-events PKG/events.jsonl --session-id SID
"""
import argparse
import hashlib
import json
import os
import stat
import sys
from datetime import datetime, timezone

REPARSE = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def is_link(path):
    st = os.lstat(path)
    return stat.S_ISLNK(st.st_mode) or bool(getattr(st, "st_file_attributes", 0) & REPARSE)


def collect(root):
    """Return manifest entries (sorted bytewise by path) for every file/symlink under root."""
    entries = []

    def walk(directory, prefix):
        with os.scandir(directory) as it:
            items = sorted(it, key=lambda e: e.name)
        for e in items:
            rel = prefix + e.name
            if is_link(e.path):
                target = os.readlink(e.path)
                entries.append({"path": rel, "type": "symlink",
                                "sha256": sha256(target.encode("utf-8", "surrogatepass"))})
            elif e.is_dir(follow_symlinks=False):
                walk(e.path, rel + "/")
            elif e.is_file(follow_symlinks=False):
                with open(e.path, "rb") as fh:
                    entries.append({"path": rel, "type": "file", "sha256": sha256(fh.read())})
            else:
                raise OSError("unsupported directory entry (fail closed): " + rel)

    walk(os.fspath(root), "")
    entries.sort(key=lambda x: x["path"].encode("utf-8", "surrogatepass"))
    return entries


def build_manifest(root, kind, run_id, workspace_label, created_at, bound_to=None):
    if kind not in ("BASELINE", "POST"):
        raise ValueError("kind must be BASELINE or POST")
    if (kind == "POST") != (bound_to is not None):
        raise ValueError("bound_to is required for POST and forbidden for BASELINE")
    obj = {"manifest_version": 1, "kind": kind, "run_id": run_id,
           "workspace_root": workspace_label, "entries": collect(root), "created_at": created_at}
    if bound_to is not None:
        obj["bound_to"] = bound_to
    return obj


def serialize(obj):
    return (json.dumps(obj, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", required=True)
    ap.add_argument("--kind", required=True, choices=("BASELINE", "POST"))
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workspace-label", default=None, help="informational label; default: the --root argument")
    ap.add_argument("--created-at", default=None, help="ISO-8601; default: now (UTC)")
    ap.add_argument("--bound-manifest")
    ap.add_argument("--bound-events")
    ap.add_argument("--session-id")
    a = ap.parse_args(argv)
    if os.path.exists(a.out):
        print("refusing to overwrite " + a.out, file=sys.stderr)
        return 2
    bound = None
    if a.kind == "POST":
        if not (a.bound_manifest and a.bound_events and a.session_id):
            print("POST requires --bound-manifest, --bound-events and --session-id", file=sys.stderr)
            return 2
        with open(a.bound_manifest, "rb") as m, open(a.bound_events, "rb") as e:
            bound = {"manifest_sha256": sha256(m.read()), "events_sha256": sha256(e.read()),
                     "session_id": a.session_id}
    created = a.created_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    obj = build_manifest(a.root, a.kind, a.run_id, a.workspace_label or a.root, created, bound)
    with open(a.out, "xb") as fh:
        fh.write(serialize(obj))
    print(json.dumps({"out": a.out, "entries": len(obj["entries"]), "sha256": sha256(serialize(obj))}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
