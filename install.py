#!/usr/bin/env python3
"""
Install the rust-webapp skill for Claude Code.

Usage:
    curl -sSL https://raw.githubusercontent.com/arsenyinfo/skills/main/install.py | python3
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_URL = "https://github.com/arsenyinfo/skills.git"
SKILL_NAME = "rust-webapp"
SOURCE_SKILL_PATH = Path("skills") / SKILL_NAME


def check_prerequisites() -> list[str]:
    missing = []
    if not shutil.which("jq"):
        missing.append("jq (install with: brew install jq)")
    if not shutil.which("neonctl"):
        missing.append("neonctl (install with: npm i -g neonctl)")
    if not shutil.which("cargo"):
        missing.append("cargo (install from: https://rustup.rs)")
    if not shutil.which("sqlx"):
        missing.append("sqlx (install with: cargo install sqlx-cli --features postgres,native-tls)")
    return missing


def main():
    missing = check_prerequisites()
    if missing:
        print("Missing prerequisites:")
        for dep in missing:
            print(f"  - {dep}")
        print("\nRequired environment variables:")
        print("  export NEON_API_KEY=your-key")
        print("  export NEON_PROJECT_ID=your-project-id")
        sys.exit(1)

    skills_dir = Path.home() / ".claude" / "skills"
    target_dir = skills_dir / SKILL_NAME

    print(f"Installing {SKILL_NAME} skill...")

    # create skills directory if needed
    skills_dir.mkdir(parents=True, exist_ok=True)

    # remove existing installation
    if target_dir.exists():
        print(f"Removing existing installation at {target_dir}")
        shutil.rmtree(target_dir)

    # clone to temp dir and copy contents
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp) / "repo"
        print(f"Cloning from {REPO_URL}...")
        subprocess.run(
            ["git", "clone", "--depth", "1", REPO_URL, str(tmp_path)],
            check=True,
            capture_output=True,
        )

        print(f"Installing to {target_dir}...")
        shutil.copytree(tmp_path / SOURCE_SKILL_PATH, target_dir)

    # make scripts executable
    scripts_dir = target_dir / "scripts"
    if scripts_dir.exists():
        for script in scripts_dir.iterdir():
            if script.is_file():
                script.chmod(script.stat().st_mode | 0o111)

    print(f"\nInstalled to: {target_dir}")
    print("\nSet environment variables:")
    print("  export NEON_API_KEY=your-key")
    print("  export NEON_PROJECT_ID=your-project-id")
    print("\nDone!")


if __name__ == "__main__":
    main()
