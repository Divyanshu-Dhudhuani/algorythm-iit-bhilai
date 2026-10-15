#!/usr/bin/env python3
"""Validate student PRs: only own folder + at most one students.json entry.

Usage (in CI):
    python3 .github/scripts/validate.py --base origin/main --head HEAD

Rules:
  - Changed files must be ONLY: students/<FOLDER>/** and optionally students.json
  - Never touch: students/_template/**, index.html, sessions.json, sessions/**, .github/**, README.md
  - New student: students.json gains exactly ONE entry; folder == name-id; page == students/<folder>/index.html
  - Update (own bio edit): students.json untouched; all changed files inside ONE folder already listed in base students.json
"""
import argparse, json, re, subprocess, sys
from pathlib import Path

FOLDER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*-[A-Za-z0-9_-]+$")
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

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--head", default="HEAD")
    args = ap.parse_args()
    errors = []

    files = changed_files(args.base, args.head)
    print(f"Changed files ({len(files)}):")
    for f in files: print(f"  - {f}")
    if not files:
        errors.append(fail("No files changed. Add your folder + students.json entry on your branch."))

    # 1. Forbidden paths
    for f in files:
        if f in FORBIDDEN_FILES or f.startswith(FORBIDDEN_PREFIXES):
            errors.append(fail(f"Forbidden change: `{f}`. Student PRs may ONLY touch `students/<NAME>-<ID>/**` and `students.json`."))
        if f.startswith("students/_template"):
            errors.append(fail("Do not edit `students/_template/`. Copy it to your own folder instead."))
        if f == "students.json":
            continue
        if not f.startswith("students/"):
            errors.append(fail(f"Forbidden change: `{f}`. Only `students/<NAME>-<ID>/**` + `students.json` allowed."))
    if errors:
        return report(errors)

    student_files = [f for f in files if f.startswith("students/")]
    json_touched = "students.json" in files

    # collect touched folders
    folders = sorted({f.split("/")[1] for f in student_files if len(f.split("/")) > 1 and f != "students.json"})
    for fo in folders:
        if fo in ("_template",):
            continue
        if not FOLDER_RE.match(fo):
            errors.append(fail(
                f"Bad folder name `{fo}`. Must be `<NAME>-<ID>` keeping original case, "
                "letters/numbers/_/-, start with letter. Example: `Swarnadip-12345`."))
        if fo.count("-") < 1:
            errors.append(fail(f"Bad folder name `{fo}`. Must contain NAME-ID separated by `-`."))
    if len([f for f in folders if f != "_template"]) > 1:
        errors.append(fail(f"Too many student folders touched: {folders}. One PR = one student folder."))
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
    head_by_folder = {e.get("folder"): e for e in head_list if isinstance(e, dict)}

    if json_touched:
        # must be exactly one ADDED entry, zero removed/modified
        base_set = {(e.get("name"), e.get("id"), e.get("folder")) for e in base_list if isinstance(e, dict)}
        head_set = {(e.get("name"), e.get("id"), e.get("folder")) for e in head_list if isinstance(e, dict)}
        added = [e for e in head_list if isinstance(e, dict) and (e.get("name"), e.get("id"), e.get("folder")) not in base_set]
        removed = [e for e in base_list if isinstance(e, dict) and (e.get("name"), e.get("id"), e.get("folder")) not in head_set]
        if len(added) != 1 or removed:
            errors.append(fail(
                f"students.json must add EXACTLY one entry (found +{len(added)}/-{len(removed)}). "
                "Do not edit or reformat other lines — resolve conflicts by keeping both entries."))
            return report(errors)
        entry = added[0]
        for k in ("name", "id", "folder", "page"):
            if not entry.get(k) or not isinstance(entry[k], str):
                errors.append(fail(f"students.json entry missing/invalid `{k}`. Required: name, id, folder, page (+ optional github)."))
        if errors: return report(errors)
        name, sid, folder, page = entry["name"].strip(), entry["id"].strip(), entry["folder"].strip(), entry["page"].strip()
        if folder != f"{name}-{sid}":
            errors.append(fail(f"`folder` must equal `<name>-<id>` exactly (case-sensitive). Got folder=`{folder}`, expected `{name}-{sid}`."))
        if page != f"students/{folder}/index.html":
            errors.append(fail(f"`page` must be `students/{folder}/index.html`. Got `{page}`."))
        if not FOLDER_RE.match(folder):
            errors.append(fail(f"Bad folder value `{folder}`. Keep original case, start with letter, allowed: A-Za-z0-9_- plus single `-` separator."))
        # duplicates in head (names may repeat — different students can share a first name)
        ids=[e.get("id") for e in head_list]; folders_l=[e.get("folder") for e in head_list]
        if ids.count(sid) > 1: errors.append(fail(f"Duplicate id `{sid}` in students.json. Your ID must be unique."))
        if folders_l.count(folder) > 1: errors.append(fail(f"Duplicate folder `{folder}` in students.json."))
        # touched folder must match entry folder
        if folders and folders != [folder]:
            errors.append(fail(f"Changed folder `{folders}` does not match students.json entry folder `{folder}`. They must match."))
        target_folder = folder
    else:
        # owner-update mode: no json change, exactly one pre-existing folder
        if len(folders) != 1:
            errors.append(fail("Without students.json change you must edit exactly ONE existing student folder (your own)."))
            return report(errors)
        target_folder = folders[0]
        if target_folder not in base_by_folder:
            errors.append(fail(
                f"Folder `{target_folder}` is not listed in students.json on main. "
                "First PR must add folder + one students.json line together."))
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
        errors.append(fail(f"`{idx}` must contain an `<h1>` or `<title>`."))
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
        print(f"\nVALIDATION FAILED ({len(errors)} error(s)). Fix on the SAME branch and push — see README §1–2.")
        return 1
    print("\nVALIDATION PASSED ✅")
    return 0

if __name__ == "__main__":
    sys.exit(main())
