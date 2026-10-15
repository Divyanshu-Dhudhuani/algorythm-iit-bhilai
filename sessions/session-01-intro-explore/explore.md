# ALGORYTHM Session 1 — Explore Further

You have the map. Now wander a little. Pick ONE section per day, do the tiny task at the end of each. No setup needed beyond browser + GitHub.

**RULE: docs first, then build. If stuck 15 min, ask in WhatsApp group.**

---

## 1. HTML — your bio page lives here

What: the skeleton of every webpage. Your homework is just one HTML file + a little CSS.

Minimal page:

```html
<h1>Your Name</h1>
<p>CSE '29, IIT Bhilai. I like ...</p>
<a href="https://github.com/you">GitHub</a> | <a href="https://linkedin.com/in/you">LinkedIn</a>
```

Do this:

- Open [MDN HTML basics](https://developer.mozilla.org/en-US/docs/Web/HTML) when you need a tag
- Beautify: one `<style>` block or a `style.css` file. Steal like an artist, then modify.
- Task: add bio + 2 links + 1 image to your homework page tonight.

Watch first: [Fireship](https://www.youtube.com/@Fireship) — "HTML in 100 Seconds" (then his CSS / Flexbox videos if you want layout fast).

---

## 2. JSON — how apps and AI talk

What: text format for data. Keys + values. You already saw it in the demo: `proximity-modular-core.json` — the whole AI prompt re-read every turn (~975k tokens). Lesson: AI has no memory, context is everything.

Example:

```json
{ "title": "Proximity: Modular Core", "messages": [ { "role": "user", "text": "hello" } ] }
```

Do this:

- Open any `.json` in VS Code, note brackets matter.
- Validate: paste into [JSONLint](https://jsonlint.com/) or run: `python3 -m json.tool file.json`
- Task: open your bio repo, add a `data.json` with `{ "name": "...", "interests": [...] }` and read it back.

Watch first: [Fireship — "JSON in 100 Seconds"](https://www.youtube.com/@Fireship). Then [3Blue1Brown](https://www.youtube.com/@3blue1brown) for the intuition of how tokens/vectors work (not JSON, but why AI eats JSON).

---

## 3. Git + GitHub — time machine + proof

What: Git = version history on your machine. GitHub = that history online = your proof of work.

Only 5 commands for now (from today's msg):

```bash
git init
git status
git add index.html
git commit -m "my first bio page"
git push
```

Do this:

- Make a [GitHub account](https://github.com/), create repo, push your bio folder tonight.
- Every improvement = one commit with a clear message.
- Never commit passwords / API keys (see section 5).
- Task: make 3 commits tonight — v1 name only, v2 +bio/links, v3 +CSS.

Learn: [GitHub Get Started docs](https://docs.github.com/en/get-started) + [Fireship "Git in 100 Seconds"](https://www.youtube.com/@Fireship).

---

## 4. LinkedIn — the story (GitHub is the proof)

GitHub proves you built. LinkedIn tells the story: who you are, what you want, what you learned.

Checklist (10 min):

- Sign up at [LinkedIn](https://www.linkedin.com/)
- Photo + headline: "CSE '29 @ IIT Bhilai | Exploring Web + AI"
- About: 3 lines — who, what you're building, what you're looking for.
- Add: ALGORYTHM Session 1 homework link (your GitHub repo / hosted page).
- Connect: classmates + seniors + 2 people whose work you liked.

---

## 5. API Keys — free AI without paying

What: a secret string that lets your code call an AI model. Like a password — never push to GitHub, never share screenshots of it.

Safety:

- Put keys in `.env`, add `.env` to `.gitignore`. If you leaked one, revoke/regenerate immediately on the provider site.
- Task: get ONE free key below, use it only locally, never commit it.

---

## 6. [OpenRouter](https://openrouter.ai/) — try models with free keys

What: one place to try many AI models. Many have free tiers — perfect for students.

Do this:

- Login > [Keys](https://openrouter.ai/keys) > Create key. Copy once.
- Go to [Chat / Playground](https://openrouter.ai/chat), pick a model tagged `:free`, ask anything.
- Compare: ask the same question to 2 different free models, note style/speed difference.
- Pro tip: GLM 5.3 was free for ~10 days recently. If you track feeds, you catch the next free window. The feed IS the edge.

---

## 7. [Artificial Analysis](https://artificialanalysis.ai/) — which model is actually best?

What: independent leaderboard — quality, speed, price per model. Check BEFORE you pick a model for a project.

Do this:

- Open [Leaderboards](https://artificialanalysis.ai/leaderboards/models), sort by coding / reasoning.
- Note the price column: best != cheapest. For homework, free+good beats best+paid.
- Task: pick your OpenRouter free model based on this board, not hype.

---

## YouTube — subscribe later, remember now

From today's slide (Where to stay updated):

1. [Fireship](https://www.youtube.com/@Fireship) — fast news + "in 100 Seconds" explainers. Start: HTML / CSS / Git / JSON in 100 Seconds playlist.
2. [3Blue1Brown](https://www.youtube.com/@3blue1brown) — deep intuition (neural nets, math behind AI). Start: "Neural Networks" series Ch.1-2.
3. [Two-Minute Papers](https://www.youtube.com/@TwoMinutePapers) — research wow in 2 min. Start: any recent AI/video paper — shows what's coming.
4. [Linus Tech Tips (LTT)](https://www.youtube.com/@LinusTechTips) — hardware fun. Start: any PC build / gadget video — reminds you tech is physical too.

How to use: 1 video/day. Fireship for breadth, 3Blue1Brown for depth, Two-Minute Papers for wonder, LTT for fun.

---

## For Next Week (30-45 min)

1. LinkedIn + GitHub accounts (10 min)
2. Push name-only HTML page (10 min)
3. Beautify + bio + links, commit each step (15 min)
4. Bonus: add `data.json` + get one OpenRouter `:free` key and try it (10 min)

Best pages get featured next session. Doubts → WhatsApp group. Fill [feedback form](https://forms.gle/ALq3DSrTAbE6rY4v8).
