# Communication

Pitch materials for databricks-twin, meant for a human audience rather than the build/runtime.

- **`pitch.md`** — a short, spoken elevator pitch (30s / 90s versions), meant to be said aloud in
  conversation rather than watched.
- **`databricks-twin-tech-pitch.mp4`** *(not yet generated)* — a ~2-3 minute video pitch of the
  project (what it is, the architecture, the routing scenario, the Genie permission bug as evidence
  of depth). Will be embedded in the [main README](../README.md) once it exists; kept here too as a
  direct, dependency-free way to reach it.

To generate it: see [`notebooklm-prompt.md`](notebooklm-prompt.md) — upload
[`video-pitch-source.md`](video-pitch-source.md) to [NotebookLM](https://notebooklm.google.com) and
use the customization prompt there. Save the export as `databricks-twin-tech-pitch.mp4` plus a
`thumbnail.png` in this directory; the GitHub Pages player
([`pitch.html`](pitch.html), deployed by [`.github/workflows/pages.yml`](../.github/workflows/pages.yml))
picks both up automatically on the next push — same mechanism as
[openrag-twin's](https://github.com/valentinleconte/openrag-twin/tree/main/communication).
