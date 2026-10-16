#!/usr/bin/env python3
"""Provision a student bio page from an `add me:` issue. Runs in CI.

Usage: provision.py --title "<issue title>" --author <login> --issue <num>
  - Parses `add me: <NAME>-<ID>` (strict; NAME/ID have no hyphens).
  - Refuses (comment + close) when the title is bad or the author already
    has a folder - one folder per GitHub account.
  - Else runs students/add-me.py, personalizes the template, pushes branch
    add-NAME-ID-<author>, opens the PR, comments its link, closes the issue.
  - DRY_RUN=1: file ops happen, but no git push / gh mutations (prints only).

The auto-merge pipeline then validates + merges the PR like any other.
"""
import argparse, json, os, re, subprocess, sys
from pathlib import Path

TITLE_RE = re.compile(r"^add me:\s*([A-Za-z][A-Za-z0-9_]*)-([A-Za-z0-9]+)\s*$", re.IGNORECASE)
DRY = os.environ.get("DRY_RUN") == "1"

def sh(*args):
    return subprocess.run(args, capture_output=True, text=True)

def gh(*args):
    if DRY:
        print("[DRYRUN] gh", " ".join(args))
        class R:
            returncode = 0
            stdout = ""
            stderr = ""
        return R()
    return sh("gh", *args)

def issue_comment(num, body):
    gh("issue", "comment", str(num), "--body", body)

def close_issue(num):
    gh("issue", "close", str(num))

USAGE = ("I could not read that. To get your bio page, open an issue titled exactly:\n"
         "`add me: YourName-YourID`\n"
         "YourName = real name, letters/numbers/_, no hyphens. "
         "YourID = roll number, letters/numbers, no hyphens. "
         "Your GitHub username is taken from your account automatically.")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True)
    ap.add_argument("--author", required=True)
    ap.add_argument("--issue", required=True)
    args = ap.parse_args()
    author = args.author.strip().lstrip("@")

    m = TITLE_RE.match(args.title.strip())
    if not m:
        issue_comment(args.issue, "[FAIL] " + USAGE)
        close_issue(args.issue)
        print("invalid title; usage posted."); return 0
    name, sid = m.group(1), m.group(2)

    data = json.loads(Path("students.json").read_text())
    mine = [e for e in data if (e.get("github") or "").lower() == author.lower()]
    if mine:
        issue_comment(args.issue,
                      f"[FAIL] @{author} you already have `{mine[0].get('folder')}`. "
                      "One folder per account - edit it via an `update-...` PR instead.")
        close_issue(args.issue)
        print("duplicate user; refused."); return 0

    folder = f"{name}-{sid}-{author}"
    r = sh(sys.executable, "students/add-me.py",
           "--name", name, "--id", sid, "--github", author)
    if r.returncode != 0:
        issue_comment(args.issue,
                      f"[FAIL] Could not scaffold `{folder}`:\n```\n{r.stdout.strip()}\n```\n"
                      "Fix the values and open a new `add me:` issue.")
        close_issue(args.issue)
        print("add-me failed; reported."); return 1
    # light personalization (student fills the rest)
    idx = Path("students") / folder / "index.html"
    t = idx.read_text()
    t = t.replace("Your Name", name).replace("YourID", sid)
    idx.write_text(t)

    branch = f"add-{folder}"
    sh("git", "checkout", "-b", branch)
    sh("git", "add", f"students/{folder}", "students.json")
    sh("git", "-c", "user.name=github-actions[bot]",
       "-c", "user.email=41898282+github-actions[bot]@users.noreply.github.com",
       "commit", "-m", f"add: {folder}")
    if DRY:
        print(f"[DRYRUN] would push {branch}, open PR, comment + close issue {args.issue}.")
        print(f"folder={folder}"); return 0
    p = sh("git", "push", "origin", f"HEAD:{branch}")
    if p.returncode != 0:
        issue_comment(args.issue, f"[FAIL] Push failed for `{branch}` - asking a maintainer for help.")
        print("push failed."); return 1
    pr = gh("pr", "create", "--title", f"add: {folder}",
            "--body", f"Provisioned from issue #{args.issue} for @{author}. "
                      "Personalize your page, then this auto-merges when checks pass.",
            "--base", "main", "--head", branch)
    url = pr.stdout.strip().splitlines()[-1] if pr.stdout.strip() else ""
    issue_comment(args.issue,
                  f"[OK] Your page is scaffolded! PR: {url}\n"
                  f"Next: open the PR, edit `students/{folder}/index.html` to make it yours, "
                  "commit on the PR branch. It auto-merges when checks are green.")
    close_issue(args.issue)
    print(f"provisioned {folder} -> {url}"); return 0

if __name__ == "__main__":
    sys.exit(main())
