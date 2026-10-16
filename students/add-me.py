#!/usr/bin/env python3
"""Scaffold your ALGORYTHM bio page + students.json entry. Run from repo root.

  python3 students/add-me.py --name YourName --id YourID --github YourGithubUsername

Creates students/<NAME>-<ID>-<GithubUsername>/ from _template and appends the
exact students.json line the hub needs. Then edit your index.html, commit,
push your branch, and open a PR titled:  add: <NAME>-<ID>-<GithubUsername>
"""
import argparse, json, shutil, subprocess, sys
from pathlib import Path

import re
NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
ID_RE = re.compile(r"^[A-Za-z0-9]+$")
GITHUB_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")

def main():
    ap = argparse.ArgumentParser(description="Scaffold your ALGORYTHM bio page.")
    ap.add_argument("--name", required=True, help="Your real name (letters/numbers/_, no hyphens)")
    ap.add_argument("--id", required=True, help="Your roll no./ID (letters/numbers, no hyphens)")
    ap.add_argument("--github", required=True, help="YOUR OWN GitHub username")
    args = ap.parse_args()

    root = Path.cwd()
    if not (root / "students.json").exists() or not (root / "students" / "_template").is_dir():
        sys.exit("Run this from the repo root (where students.json lives).")

    name, sid, gh = args.name.strip(), args.id.strip(), args.github.strip().lstrip("@")
    problems = []
    if not NAME_RE.match(name):
        problems.append(f"bad --name `{name}`: letters/numbers/_, start with letter, no hyphens.")
    if not ID_RE.match(sid):
        problems.append(f"bad --id `{sid}`: letters/numbers, no hyphens.")
    if not GITHUB_RE.match(gh):
        problems.append(f"bad --github `{gh}`: must be a valid GitHub username.")
    if not problems and gh.lower() != guess_login() and guess_login():
        print(f"NOTE: --github `{gh}` != your `gh` login `{guess_login()}`. The PR bot checks ownership - use your own username.")
    if problems:
        sys.exit("ERROR:\n  " + "\n  ".join(problems))

    folder = f"{name}-{sid}-{gh}"
    dest = root / "students" / folder
    data = json.loads((root / "students.json").read_text())
    if dest.exists():
        sys.exit(f"ERROR: folder students/{folder}/ already exists. Editing it instead? Just edit files inside it.")
    if any(e.get("folder") == folder for e in data):
        sys.exit(f"ERROR: students.json already lists `{folder}`.")
    if any(e.get("id") == sid for e in data):
        sys.exit(f"ERROR: id `{sid}` is already taken in students.json.")
    if any((e.get("github") or "").lower() == gh.lower() for e in data):
        sys.exit(f"ERROR: GitHub user `{gh}` already has a folder. One folder per account - edit yours instead.")

    shutil.copytree(root / "students" / "_template", dest)
    data.append({"name": name, "id": sid, "folder": folder,
                 "page": f"students/{folder}/index.html", "github": gh})
    data.sort(key=lambda e: e.get("folder", ""))
    (root / "students.json").write_text(json.dumps(data, indent=2))
    print(f"Created students/{folder}/ + students.json entry.")
    print("Next:")
    print(f"  1. Edit students/{folder}/index.html (make it yours)")
    print(f"  2. git add students/{folder} students.json && git commit -m \"add: {folder} bio page\"")
    print(f"  3. Push your branch and open a PR titled:  add: {folder}")

def guess_login():
    try:
        r = subprocess.run(["gh", "api", "user", "--jq", ".login"],
                           capture_output=True, text=True, timeout=10)
        return r.stdout.strip() or None
    except Exception:
        return None

if __name__ == "__main__":
    main()
