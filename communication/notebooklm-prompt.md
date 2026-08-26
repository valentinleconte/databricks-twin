# NotebookLM setup — video pitch for databricks-twin

## 1. Sources to upload

In a new NotebookLM notebook, add these as sources:

1. **`video-pitch-source.md`** (required — this is the primary script NotebookLM should draw from)
2. **`README.md`** (optional, adds detail — the Mermaid architecture diagram won't render for
   NotebookLM, but the surrounding prose on the bugs found, the eval numbers, and the license
   section is useful extra context)

Do **not** add `NOTES.md` — it's a working engineering log (in French, besides), not pitch
material, and will pull the tone toward a raw bug list instead of a pitch.

## 2. Customization prompt

Go to **Studio → Video Overview → Customize**, and paste this:

```
Create a confident, technical pitch video for a software portfolio project, aimed at a technical
interviewer or Solutions Engineer who will watch this before or during a job interview
conversation.

Target length: 2 to 3 minutes. Tighter is better than padded — cut detail before you cut clarity.

Structure to follow, in this order:
1. A one-sentence hook: what this project is and why it exists. It's a companion to an earlier
   project (openrag-twin, a replica of IBM's OpenRAG) — the point of this one is proving the same
   engineering rigor holds on a second, different vendor's platform (Databricks), not just repeating
   a trick that worked once.
2. The architecture: name each real Databricks piece (Unity Catalog, Vector Search, Genie, Model
   Serving, MLflow, Databricks Apps) and its one job, briefly. Don't read a component list — explain
   the flow of a request through the system: chat UI to agent to one of two tools to an answer.
3. The core scenario: an agent that DECIDES between two tools — searching indexed documentation
   with a cited source URL, or asking a Genie space a natural-language question that Genie turns
   into real SQL against a governed table — instead of always retrieving. Make clear this is the
   same "decide, don't just retrieve" pattern as the first project, but the second tool is
   reimplemented as something genuinely native to this platform, not a ported mock.
4. One concrete example of engineering depth: the Genie permission bug. Explain it precisely — it
   worked in local testing (run under an already-privileged personal account) and failed only once
   actually deployed to production as a real app with its own service principal identity, because
   granting CAN_RUN on a Genie space only grants permission to ask it a question — Genie then runs
   its generated SQL under the caller's own separate Unity Catalog grants. A viewer with software
   background should come away understanding the actual permission-chain mechanism, not just that
   "a bug was fixed."
5. Close on measured rigor and scope: a golden set run three times reports an honest 82%, not a
   cleaned-up 100%, with the two real gaps (occasional malformed tool calls, occasional
   hallucination on questions the docs don't cover) named rather than hidden. This is a small,
   deliberately scoped project built to be defended in conversation, not to look impressive from a
   distance.

Tone: precise and confident, like an engineer explaining their own work to a peer — not a marketing
narrator, no hype language, no exclamation points in the narration style, no "revolutionary" or
"game-changing." Technical vocabulary is fine and expected; the audience is technical.

Avoid: reciting file paths or directory names, listing dependency version numbers, restating the
same point in the intro and the conclusion, generic AI-product-demo phrasing ("in today's
fast-paced world of AI...").

If you generate slide visuals, prefer simple architecture/flow diagrams over walls of bullet text,
and keep on-screen text short enough to read in the time it's shown. If you show the eval numbers
on screen, show the real ones (13/15, 11/15, 13/15 — 82% mean) rather than rounding up.
```

## 3. After generating

- Watch it once before publishing. NotebookLM sometimes over-simplifies the permission-bug
  explanation (step 4) — if it does, regenerate with a note added to the prompt: *"Give the Genie
  permission bug more technical precision — a viewer who works with software should understand
  exactly which grant was missing and why local testing didn't catch it."*
- Export the video as `databricks-twin-tech-pitch.mp4` and save it in this `communication/`
  directory, alongside a `thumbnail.png` (a screenshot of the video's first frame works well, same
  as openrag-twin's).
- Once both files are in place, ask me to wire up the GitHub Pages player and the README embed —
  the plumbing (`pitch.html`, `.github/workflows/pages.yml`) is already set up and waiting for the
  two files, same mechanism as openrag-twin's.
