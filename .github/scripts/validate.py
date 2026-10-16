#!/usr/bin/env python3
"""Validate student PRs: only YOUR OWN folder + at most one students.json entry.

Folder format: <NAME>-<ID>-<GithubUsername>  (keep original case)
  Example: Swarnadip-12342210-Swarnadip-Kar
  - NAME: your real name, letters/numbers/_, starts with letter (no hyphens)
  - ID: your roll no. / chosen ID, letters/numbers (no hyphens)
  - GithubUsername: MUST equal the PR author's GitHub username (case-insensitive)

Usage (in CI):
    python3 .github/scripts/validate.py --base origin/main --head HEAD --author <PR-author-login>

Rules:
  - Changed files must be ONLY: students/<YOUR-FOLDER>/** and optionally students.json
  - You may ONLY touch the folder whose username part matches YOUR GitHub username
  - Never touch: students/_template/**, anyone else's folder, index.html,
    sessions.json, sessions/**, .github/**, README.md
  - New student: students.json gains exactly ONE entry;
    folder == name-id-github; page == students/<folder>/index.html
  - Update (own bio edit): students.json untouched; all changed files inside
    YOUR OWN already-listed folder.
"""
import argparse, json, re, subprocess, sys
from pathlib import Path

NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
ID_RE = re.compile(r"^[A-Za-z0-9]+$")
GITHUB_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")
FORBIDDEN_PREFIXES = ("sessions/", ".github/", ".git/")
FORBIDDEN_FILES = {"index.html", "sessions.json", "README.md", ".gitignore", "CNAME"}
MAX_PAGE_BYTES = 500 * 1024
SECRET_PATTERNS = ["BEGIN PRIVATE KEY", "BEGIN RSA PRIVATE KEY", "AKIA", "aws_secret"]

def sh(*args):
    return subprocess.run(args, capture_output=True, text=True)

def changed_files(base, head):
    r = sh("git", "diff", "--name-only", f"{base}...{head}")
    if r.returncode != 0:
        # fallback for initial runs without merge-base
        r = sh("git", "diff", "--name-only", f"{base}", f"{head}")
        if r.returncode != 0:
            print(f"::error::git diff failed: {r.stderr}"); sys.exit(2)
    return [l.strip() for l in r.stdout.splitlines() if l.strip()]

def load_at(ref, path):
    r = sh("git", "show", f"{ref}:{path}")
    if r.returncode != 0:
        return None, f"missing {path} at {ref}"
    try:
        return json.loads(r.stdout), None
    except json.JSONDecodeError as e:
        return None, f"{path} at {ref} is not valid JSON: {e}"

def fail(msg):
    print(f"::error::{msg}")
    return msg

def split_folder(folder):
    """Split <NAME>-<ID>-<user> into parts.

    NAME and ID contain no hyphens, but GitHub usernames MAY - so the
    username is everything after the SECOND hyphen.
    """
    parts = folder.split("-")
    if len(parts) < 3 or not parts[0] or not parts[1] or not parts[2]:
        return None
    return parts[0], parts[1], "-".join(parts[2:])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--head", default="HEAD")
    ap.add_argument("--author", default=None,
                    help="GitHub username of the PR author; enforces you-only-edit-your-own-folder")
    args = ap.parse_args()
    author = args.author.strip().lstrip("@") if args.author else None
    errors = []

    files = changed_files(args.base, args.head)
    print(f"Changed files ({len(files)}):")
    for f in files: print(f"  - {f}")
    if author:
        print(f"PR author: {author} (ownership enforced)")
    else:
        print("No --author given: ownership check skipped (local run).")
    if not files:
        errors.append(fail("No files changed. Add your folder + students.json entry on your branch."))

    # 1. Forbidden paths
    for f in files:
        if f in FORBIDDEN_FILES or f.startswith(FORBIDDEN_PREFIXES):
            errors.append(fail(f"Forbidden change: `{f}`. Student PRs may ONLY touch YOUR OWN `students/<NAME>-<ID>-<GithubUsername>/**` and `students.json`."))
        if f.startswith("students/_template"):
            errors.append(fail("Do not edit `students/_template/`. Copy it to your own folder instead."))
        if f == "students.json":
            continue
        if not f.startswith("students/"):
            errors.append(fail(f"Forbidden change: `{f}`. Only your own student folder + `students.json` allowed."))
    if errors:
        return report(errors)

    student_files = [f for f in files if f.startswith("students/")]
    json_touched = "students.json" in files

    # collect touched folders
    folders = sorted({f.split("/")[1] for f in student_files if len(f.split("/")) > 1 and f != "students.json"})
    for fo in folders:
        if fo in ("_template",):
            continue
        parts = split_folder(fo)
        if not parts:
            errors.append(fail(
                f"Bad folder name `{fo}`. Must be `<NAME>-<ID>-<GithubUsername>` "
                "(NAME and ID contain no hyphens; the username is everything after the 2nd `-`). "
                "Example: `Swarnadip-12342210-Swarnadip-Kar`."))
            continue
        name_p, id_p, user_p = parts
        if not NAME_RE.match(name_p):
            errors.append(fail(f"Bad NAME part `{name_p}` in `{fo}`. Use your real name: letters/numbers/_, start with letter, no hyphens."))
        if not ID_RE.match(id_p):
            errors.append(fail(f"Bad ID part `{id_p}` in `{fo}`. Use your roll no./ID: letters/numbers, no hyphens."))
        if not GITHUB_RE.match(user_p):
            errors.append(fail(f"Bad GithubUsername part `{user_p}` in `{fo}`. Must be a valid GitHub username."))
        if author and user_p.lower() != author.lower():
            errors.append(fail(
                f"Ownership violation: folder `{fo}` belongs to GitHub user `{user_p}`, "
                f"but this PR was opened by `{author}`. You may ONLY edit the folder with YOUR OWN username."))
    if len([f for f in folders if f != "_template"]) > 1:
        errors.append(fail(f"Too many student folders touched: {folders}. One PR = your own folder only."))
    if errors:
        return report(errors)

    base_list, e1 = load_at(args.base, "students.json")
    head_list, e2 = load_at(args.head, "students.json")
    if e1: errors.append(fail(e1))
    if e2: errors.append(fail(e2))
    if errors:
        return report(errors)
    if not isinstance(base_list, list) or not isinstance(head_list, list):
        errors.append(fail("students.json must be a JSON array."))
        return report(errors)

    base_by_folder = {e.get("folder"): e for e in base_list if isinstance(e, dict)}

    if json_touched:
        # must be exactly one ADDED entry, zero removed/modified (folder is the identity)
        base_folders = {e.get("folder") for e in base_list if isinstance(e, dict)}
        head_folders = {e.get("folder") for e in head_list if isinstance(e, dict)}
        added = [e for e in head_list if isinstance(e, dict) and e.get("folder") not in base_folders]
        removed = [e for e in base_list if isinstance(e, dict) and e.get("folder") not in head_folders]
        if len(added) != 1 or removed:
            errors.append(fail(
                f"students.json must add EXACTLY one entry (found +{len(added)}/-{len(removed)}). "
                "Do not edit or reformat other lines - resolve conflicts by keeping both entries."))
            return report(errors)
        entry = added[0]
        for k in ("name", "id", "folder", "page", "github"):
            if not entry.get(k) or not isinstance(entry[k], str):
                errors.append(fail(f"students.json entry missing/invalid `{k}`. Required: name, id, folder, page, github."))
        if errors: return report(errors)
        name = entry["name"].strip(); sid = entry["id"].strip()
        folder = entry["folder"].strip(); page = entry["page"].strip()
        gh = entry["github"].strip()
        if folder != f"{name}-{sid}-{gh}":
            errors.append(fail(f"`folder` must equal `<name>-<id>-<github>` exactly (case-sensitive). Got `{folder}`, expected `{name}-{sid}-{gh}`."))
        if page != f"students/{folder}/index.html":
            errors.append(fail(f"`page` must be `students/{folder}/index.html`. Got `{page}`."))
        parts = split_folder(folder)
        if not parts:
            errors.append(fail(f"Bad folder value `{folder}`. Must be `<NAME>-<ID>-<GithubUsername>`."))
        else:
            name_p, id_p, user_p = parts
            if not NAME_RE.match(name_p):
                errors.append(fail(f"Bad NAME part `{name_p}`. Use your real name: letters/numbers/_, start with letter, no hyphens."))
            if not ID_RE.match(id_p):
                errors.append(fail(f"Bad ID part `{id_p}`. Use your roll no./ID: letters/numbers, no hyphens."))
            if not GITHUB_RE.match(user_p):
                errors.append(fail(f"Bad GithubUsername part `{user_p}`. Must be a valid GitHub username."))
        if author:
            if gh.lower() != author.lower():
                errors.append(fail(
                    f"Ownership violation: students.json entry claims GitHub user `{gh}`, "
                    f"but this PR was opened by `{author}`. Your entry must use YOUR OWN username."))
            elif parts and parts[2].lower() != author.lower():
                errors.append(fail(
                    f"Ownership violation: folder username `{parts[2]}` != PR author `{author}`."))
        # duplicates in head (same first name is fine - folder/id/github must be unique)
        ids = [e.get("id") for e in head_list]
        folders_l = [e.get("folder") for e in head_list]
        ghs = [(e.get("github") or "").lower() for e in head_list]
        if ids.count(sid) > 1: errors.append(fail(f"Duplicate id `{sid}` in students.json. Your ID must be unique."))
        if folders_l.count(folder) > 1: errors.append(fail(f"Duplicate folder `{folder}` in students.json."))
        if ghs.count(gh.lower()) > 1: errors.append(fail(f"Duplicate GitHub user `{gh}` in students.json. One folder per GitHub account."))
        # touched folder must match entry folder
        if folders and folders != [folder]:
            errors.append(fail(f"Changed folder `{folders}` does not match students.json entry folder `{folder}`. They must match."))
        target_folder = folder
    else:
        # owner-update mode: no json change, exactly ONE pre-existing folder - and it must be yours
        if len(folders) != 1:
            errors.append(fail("Without students.json change you must edit exactly ONE student folder (your own)."))
            return report(errors)
        target_folder = folders[0]
        base_entry = base_by_folder.get(target_folder)
        if not base_entry:
            errors.append(fail(
                f"Folder `{target_folder}` is not listed in students.json on main. "
                "First PR must add folder + one students.json line together."))
            return report(errors)
        if author and (base_entry.get("github") or "").lower() != author.lower():
            errors.append(fail(
                f"Ownership violation: folder `{target_folder}` belongs to GitHub user "
                f"`{base_entry.get('github')}`, but this PR was opened by `{author}`. "
                "You may ONLY edit the folder with YOUR OWN username."))
            return report(errors)
        print(f"Owner-update mode for {target_folder} (students.json untouched). OK.")

    # 2. index.html checks (working tree == HEAD in CI after checkout)
    idx = Path("students") / target_folder / "index.html"
    if not idx.is_file():
        errors.append(fail(f"Missing required file `students/{target_folder}/index.html`. Copy from `students/_template/`."))
        return report(errors)
    data = idx.read_bytes()
    if len(data) > MAX_PAGE_BYTES:
        errors.append(fail(f"`{idx}` is {len(data)} bytes > 500 KB. Compress images."))
    text = data.decode("utf-8", errors="replace")
    if "<html" not in text.lower():
        errors.append(fail(f"`{idx}` must contain `<html>`."))
    if "<h1" not in text.lower() and "<title" not in text.lower():
        errors.append(fail(f"`{idx}` must contain an `<h1>` or `<title>` (use your real name)."))
    for pat in SECRET_PATTERNS:
        if pat in text:
            errors.append(fail(f"`{idx}` looks like it contains a secret (`{pat}`). Remove keys/tokens."))
    # size of whole folder
    total = sum(p.stat().st_size for p in (Path("students")/target_folder).rglob("*") if p.is_file())
    if total > MAX_PAGE_BYTES:
        errors.append(fail(f"Folder `students/{target_folder}/` is {total} bytes > 500 KB total."))
    return report(errors)

def report(errors):
    if errors:
        print(f"\nVALIDATION FAILED ({len(errors)} error(s)). Fix on the SAME branch and push - see README §1-2.")
        return 1
    print("\nVALIDATION PASSED")
    return 0

if __name__ == "__main__":
    sys.exit(main())
