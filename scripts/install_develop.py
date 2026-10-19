"""Install the local develop Skill without overwriting existing content."""

import argparse
import os
from pathlib import Path
import shutil

from package_develop import COPIES, ROOT


def destination(agent, project):
    if project is not None:
        base = project.resolve()
        if not base.is_dir():
            raise ValueError(f"Project does not exist: {base}")
    else:
        base = Path.home()
    if agent == "claude":
        # Claude supports relocating its configuration directory.
        if project is None and os.environ.get("CLAUDE_CONFIG_DIR"):
            return Path(os.environ["CLAUDE_CONFIG_DIR"]).expanduser().resolve() / "skills/develop"
        return base / ".claude/skills/develop"
    return base / ".agents/skills/develop"


def install(agent, project):
    source = ROOT / "skills/develop"
    for original, copy in COPIES.items():
        if not copy.is_file() or original.read_bytes() != copy.read_bytes():
            raise ValueError("Stale package; run python scripts/package_develop.py first")
    target = destination(agent, project)
    if target.exists() or target.is_symlink():
        raise ValueError(f"Destination already exists; left untouched: {target}")
    if agent == "claude":
        command = target.parents[1] / "commands/develop.md"
        if command.exists():
            raise ValueError(f"Existing /develop command; resolve the name conflict first: {command}")
    target.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation also prevents a concurrent install from being overwritten.
    target.mkdir()
    shutil.copytree(source, target, dirs_exist_ok=True)
    print(f"Installed: {target}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", choices=("codex", "claude"), required=True)
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--user", action="store_true")
    scope.add_argument("--project", type=Path)
    args = parser.parse_args()
    try:
        install(args.agent, args.project)
    except (ValueError, OSError) as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
