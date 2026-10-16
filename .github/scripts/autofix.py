#!/usr/bin/env python3
"""CI helper: auto-add a missing students.json entry to a student PR.

Runs on the checked-out PR head. Only acts when ALL hold:
  - exactly ONE new student folder vs --base (ignoring _template)
  - students.json is UNTOUCHED vs --base
  - folder parses as <NAME>-<ID>-<user> and user == --author (case-insensitive)

With --branch it commits (as github-actions[bot]) and pushes to the PR branch.
Exit codes: 0 = NOOP or PUSHED, 3 = NEEDS_MANUAL (push failed; snippet.md
written for the bot to post). Always prints the exact snippet on stdout too.
"""
import argparse, json, os, re, subprocess, sys
from pathlib import Path

NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
ID_RE = re.compile(r"^[A-Za-z0-9]+$")
GITHUB_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")

def sh(*args, check=False):
    return subprocess.run(args, capture_output=True, text=True)

def emit_result(value):
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write(f"result={value}\n")

def ls_dirs(ref):
    r = sh("git", "ls-tree", "-d", "--name-only", ref, "--", "students/")
    if r.returncode != 0:
        return set()
    return {l.strip().split("/")[1] for l in r.stdout.splitlines()
            if l.strip().startswith("students/") and len(l.strip().split("/")) > 1}

def split_folder(folder):
    parts = folder.split("-")
    if len(parts) < 3 or not parts[0] or not parts[1] or not parts[2]:
        return None
    return parts[0], parts[1], "-".join(parts[2:])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--author", required=True)
    ap.add_argument("--branch", default=None, help="PR head branch to push the fix to")
    args = ap.parse_args()
    author = args.author.strip().lstrip("@")

    base_dirs = ls_dirs(args.base)
    head_dirs = ls_dirs("HEAD")
    new_folders = sorted((head_dirs - base_dirs) - {"_template"})
    if len(new_folders) != 1:
        print(f"NOOP: expected exactly 1 new student folder, found {new_folders}.")
        emit_result("noop"); return 0

    r = sh("git", "diff", "--name-only", f"{args.base}", "HEAD", "--", "students.json")
    if r.stdout.strip():
        print("NOOP: students.json was touched by the PR itself; leaving it alone.")
        emit_result("noop"); return 0

    folder = new_folders[0]
    parts = split_folder(folder)
    if not parts:
        print(f"NOOP: folder `{folder}` is not valid <NAME>-<ID>-<user>; validator will report it.")
        emit_result("noop"); return 0
    name_p, id_p, user_p = parts
    if not (NAME_RE.match(name_p) and ID_RE.match(id_p) and GITHUB_RE.match(user_p)):
        print(f"NOOP: folder `{folder}` has invalid parts; validator will report it.")
        emit_result("noop"); return 0
    if user_p.lower() != author.lower():
        print(f"NOOP: folder user `{user_p}` != PR author `{author}`; validator will report it.")
        emit_result("noop"); return 0

    data = json.loads(Path("students.json").read_text())
    entry = {"name": name_p, "id": id_p, "folder": folder,
             "page": f"students/{folder}/index.html", "github": user_p}
    data.append(entry)
    data.sort(key=lambda e: e.get("folder", ""))
    snippet = ("You forgot the `students.json` line, so here is the exact entry "
               "your PR needs (already in the required format):\n"
               "```json\n" + json.dumps(entry, indent=2) + "\n```")
    print(snippet)
    Path("snippet.md").write_text(snippet + "\n")

    if not args.branch:
        print("NOOP: --branch not given (dry run); students.json left untouched.")
        emit_result("noop"); return 0

    Path("students.json").write_text(json.dumps(data, indent=2))
    sh("git", "config", "user.name", "github-actions[bot]")
    sh("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
    sh("git", "add", "students.json")
    c = sh("git", "-c", "user.name=github-actions[bot]",
           "-c", "user.email=41898282+github-actions[bot]@users.noreply.github.com",
           "commit", "-m", f"chore: add students.json entry for {folder}")
    if c.returncode != 0:
        print(f"NEEDS_MANUAL: commit failed: {c.stderr.strip()}")
        sh("git", "checkout", "--", "students.json")
        emit_result("manual"); return 3
    p = sh("git", "push", "origin", f"HEAD:{args.branch}")
    if p.returncode != 0:
        print(f"NEEDS_MANUAL: push failed: {p.stderr.strip()}")
        print("HINT: the PR author likely disabled 'Allow edits from maintainers'.")
        sh("git", "reset", "--hard", "HEAD~1")
        emit_result("manual"); return 3
    sh("git", "fetch", "origin", args.branch, "--depth=1")
    sh("git", "reset", "--hard", "FETCH_HEAD")
    print(f"PUSHED: entry committed to {args.branch}.")
    emit_result("pushed"); return 0

if __name__ == "__main__":
    sys.exit(main())
