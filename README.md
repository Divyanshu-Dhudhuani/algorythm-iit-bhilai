# ALGORYTHM Sessions — IIT Bhilai

Main hub for all ALGORYTHM session slide decks + student bio pages.

- **Live site:** GitHub Pages serves `index.html` from `main` (root). It reads `students.json` + `sessions.json` and renders the lists — no build step.
- **Slide decks:** HTML files under `sessions/<session-id>/`. Linked from `index.html` via `sessions.json`. Since they are plain HTML, they open directly in the browser.
- **Student pages:** each student owns `students/<NAME>-<ID>-<GithubUsername>/index.html` + **one line** in `students.json`. `index.html` at root reads that JSON and creates the directory of webpages.

> Students get featured by opening a Pull Request. PRs that follow the exact format below are **auto-merged** by GitHub Actions 🤖.

---

## 1. For students — add your bio page (required workflow)

> ⚠️ **You MUST create your own branch first. PRs raised directly from `main` are auto-rejected.**
> ⚠️ **You may ONLY edit the folder carrying YOUR OWN GitHub username. Touching anyone else's folder = auto-rejected.**
> ⚠️ **If your PR shows a merge conflict, it will NOT be merged. Resolve it locally first, then push.**

### Step 0 — one-time setup

```bash
# Fork this repo on GitHub (click Fork), then:
git clone https://github.com/<YOUR-USERNAME>/algorythm-iit-bhilai.git
cd algorythm-iit-bhilai
git remote add upstream https://github.com/<OWNER>/algorythm-iit-bhilai.git
git fetch upstream
git checkout main
git reset --hard upstream/main
```

### Step 1 — ALWAYS create your own branch from updated `main`

```bash
git checkout main
git pull upstream main      # or: git fetch upstream && git reset --hard upstream/main
git checkout -b add-<NAME>-<ID>-<YourGithubUsername>
# Example: git checkout -b add-Swarnadip-12345-Swarnadip-Kar
```

Rules:
- Branch name must be `add-<NAME>-<ID>-<YourGithubUsername>` (same suffix as your folder). Keep your original case.
- The username part MUST be YOUR OWN GitHub username (case-insensitive match with the PR author). You cannot open a PR for someone else's folder.
- Never commit directly to `main`. Never open a PR whose head branch is `main`/`master` — the bot rejects it.
- One student = one branch = one PR.

### Step 2 — create your folder

```bash
cp -r students/_template students/<NAME>-<ID>-<YourGithubUsername>
# Example: cp -r students/_template students/Swarnadip-12345-Swarnadip-Kar
```

Rules:
- Folder must be exactly `<NAME>-<ID>-<GithubUsername>` — keep your original case (no forced lowercase).
- NAME = your real name: letters/numbers/`_`, start with letter, NO hyphens. ID = your roll no. / chosen ID: letters/numbers, NO hyphens (keeps the 3-part split unambiguous). Last part = YOUR GitHub username (may contain hyphens).
- Example: `Swarnadip-12345-Swarnadip-Kar` → NAME=`Swarnadip`, ID=`12345`, GithubUsername=`Swarnadip-Kar`. Keep ID stable forever.
- Inside your folder: `index.html` is **required** (put your real name in `<h1>`/`<title>`). You may add `style.css` and images (total < 500 KB). Do NOT touch anyone else's folder — the bot checks the username part against YOUR login.

Edit `students/<NAME>-<ID>-<GithubUsername>/index.html` — make it beautiful. See `students/_template/index.html` and `students/Swarnadip-12345-Swarnadip-Kar/index.html`. Your page is listed on the main hub (`index.html`) automatically from `students.json`.

### Step 3 — add ONE line to `students.json`

Append exactly one JSON object (keep alphabetical order if you can, trailing commas matter):

```json
[
  {
    "name": "Swarnadip",
    "id": "12345",
    "folder": "Swarnadip-12345-Swarnadip-Kar",
    "page": "students/Swarnadip-12345-Swarnadip-Kar/index.html",
    "github": "Swarnadip-Kar"
  }
]
```

Rules:
- `folder` MUST equal `<name>-<id>-<github>` exactly (case-sensitive).
- `page` MUST equal `students/<folder>/index.html`.
- `github` MUST equal YOUR GitHub username (matches the PR author, case-insensitive).
- `id` + `folder` + `github` must be unique — no duplicates (same first name is fine; one folder per GitHub account).
- Only ONE new entry per PR. Do not reformat the whole file.

### Step 4 — commit + push your branch, open PR to `main`

```bash
git add students/<NAME>-<ID>-<YourGithubUsername> students.json
git status   # MUST show only your folder + students.json
git commit -m "add: <NAME>-<ID>-<YourGithubUsername> bio page"
git push -u origin add-<NAME>-<ID>-<YourGithubUsername>
```

Then on GitHub: **Compare & pull request** → base: `upstream/main` ← compare: `<YOUR-USERNAME>:add-<NAME>-<ID>-<YourGithubUsername>`.

PR title format (required for auto-merge):

```
add: <NAME>-<ID>-<GithubUsername>
# Example: add: Swarnadip-12345-Swarnadip-Kar
```

PR body: write 1 line — your name + what your page has.

### Step 5 — what the bot checks (auto-merge rules)

The `validate-and-automerge` Action approves + squash-merges ONLY if ALL pass:

1. ✅ Head branch is NOT `main`/`master` — must be `add-<NAME>-<ID>-<GithubUsername>`, and its username part MUST equal YOUR login (the PR author).
2. ✅ Base branch is `main`.
3. ✅ No merge conflicts (`mergeable` = clean). **Conflicting PRs are rejected — see §2.**
4. ✅ Changed files = ONLY YOUR OWN `students/<NAME>-<ID>-<GithubUsername>/**` + `students.json` (nothing else — never `_template/`, never someone else's folder).
5. ✅ `students.json` diff = exactly +1 entry, valid JSON, `folder == name-id-github`, `page == students/<folder>/index.html`, `github` == YOUR username, no duplicate id/folder/github-user.
6. ✅ `students/<NAME>-<ID>-<GithubUsername>/index.html` exists, contains `<html>` + `<h1>`/`<title>` with your real name, < 500 KB, no secrets.
7. ✅ For **edits** (updating your own bio later): `students.json` may stay untouched, but then you may ONLY touch files inside YOUR OWN already-listed folder. Same branch rule applies (`update-<NAME>-<ID>-<GithubUsername>`).

If any check fails, the bot posts a comment explaining what to fix. Fix on the SAME branch + push — the PR re-checks automatically. No need to open a new PR.

---

## 2. Merge conflicts — resolve locally first, then push (mandatory)

If your PR page shows **“This branch has conflicts that must be resolved”**, the bot will **reject it and never merge it** until YOU fix it. This almost always means someone else edited `students.json` before you (same lines).

Do NOT click “Resolve conflicts” on github.com for `students.json` unless you know JSON well — one stray comma breaks the whole site. Fix locally:

```bash
# on YOUR branch
git fetch upstream
git rebase upstream/main
# OR: git merge upstream/main
# Git will mark CONFLICT in students.json. Open it, keep BOTH entries (yours + theirs), remove <<<<<<< ======= >>>>>>> markers, ensure valid JSON.

# verify JSON is still valid:
python3 -c "import json; json.load(open('students.json')); print('JSON OK')"

# verify your entry + folder still correct:
python3 .github/scripts/validate.py --base upstream/main --head HEAD || true

git add students.json
git rebase --continue   # if you used rebase (or: git commit, if you used merge)
git push --force-with-lease   # after rebase; plain `git push` after merge
```

Then confirm on your PR page: “This branch has no conflicts” + green ✅ checks. The bot will auto-merge from there.

> First-timer tip: always `git pull upstream main` / `rebase` **right before** you start Step 1 — most conflicts disappear if you start from fresh `main`.

---

## 3. For maintainers — sessions, Pages, repo settings

Add a session:

1. Copy deck HTML into `sessions/<new-session-id>/index.html` (+ extras).
2. Add one object to `sessions.json` (id/title/date/description/deck/files).
3. Push to `main` — `index.html` picks it up automatically. No rebuild.

GitHub Pages: Settings → Pages → Deploy from branch `main` / root (already configured via `.github/workflows/pages.yml` as backup). Site URL is shown in the workflow + repo About section.

Branch protection (active): `main` requires the `validate` check + PR before merging (strict off so queued auto-merges complete). Admins can still push session decks directly. Auto-merge bot has `contents:write + pull-requests:write` and squash-merges compliant PRs.

Management notes (private, NOT in git): see `../management/` next to this repo — owner checklist, links, roll list. Never commit that folder.

---

## Repo layout

```
algorythm-iit-bhilai/
  index.html            ← main hub (reads JSON, renders sessions + students)
  students.json         ← THE main file students append one line to
  sessions.json         ← slide-deck catalogue
  students/
    _template/index.html
    Swarnadip-12345-Swarnadip-Kar/index.html   ← example
    <NAME>-<ID>-<GithubUsername>/index.html  ← yours (username MUST be yours)
  sessions/
    session-01-intro-explore/index.html (+ pdf/md/png)
    session-02-git-agents/index.html (+ …)
    session-02-1-git-recovery/index.html (+ …)
  .github/
    workflows/validate-and-automerge.yml
    workflows/pages.yml
    scripts/validate.py
```
