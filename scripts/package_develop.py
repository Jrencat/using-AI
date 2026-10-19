"""Generate or check the distributable copies; edit only the source documents."""

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COPIES = {
    ROOT / "docs/workflow/develop.md": ROOT / "skills/develop/references/develop.md",
    ROOT / "LICENSE": ROOT / "skills/develop/LICENSE",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for source, target in COPIES.items():
        content = source.read_bytes()
        if args.check:
            if not target.is_file() or target.read_bytes() != content:
                parser.exit(1, f"Out of date: {target}; run python scripts/package_develop.py\n")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
    print("Skill package is synchronized.")


if __name__ == "__main__":
    main()
