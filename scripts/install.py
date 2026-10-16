#!/usr/bin/env python3
"""Copy the complete skill bundle into a skills directory without overwriting it."""

import argparse
from pathlib import Path
import shutil


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dest",
        type=Path,
        default=Path.home() / ".agents" / "skills",
        help="Skills directory. Default: ~/.agents/skills",
    )
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1] / "skills"
    skills = sorted(path for path in source.iterdir() if (path / "SKILL.md").is_file())
    destination = args.dest.expanduser().resolve()
    conflicts = [destination / skill.name for skill in skills
                 if (destination / skill.name).exists() or (destination / skill.name).is_symlink()]
    if conflicts:
        parser.exit(1, "Nothing installed. Back up or move these existing paths first:\n"
                    + "\n".join(str(path) for path in conflicts) + "\n")
    destination.mkdir(parents=True, exist_ok=True)
    for skill in skills:
        shutil.copytree(skill, destination / skill.name)
    print(f"Installed {len(skills)} skills into {destination}")
    print("Start a new agent session to load the skills.")


if __name__ == "__main__":
    main()
