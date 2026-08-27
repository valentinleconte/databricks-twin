# Communication

Pitch materials for databricks-twin, meant for a human audience rather than the build/runtime.

- **`pitch.md`** — a short, spoken elevator pitch (30s / 90s versions), meant to be said aloud in
  conversation rather than watched.
- **`databricks-twin-tech-pitch.mp4`** — a ~3:30 video pitch of the project (what it is, the
  architecture, the routing scenario, the Genie permission bug as evidence of depth). Embedded in
  the [main README](../README.md); kept here too as a direct, dependency-free way to reach it.

Generated with [NotebookLM](https://notebooklm.google.com) from
[`video-pitch-source.md`](video-pitch-source.md), using the prompt in
[`notebooklm-prompt.md`](notebooklm-prompt.md). Served via a GitHub Pages player
([`pitch.html`](pitch.html), deployed by [`.github/workflows/pages.yml`](../.github/workflows/pages.yml))
since GitHub READMEs can't embed video directly — same mechanism as
[openrag-twin's](https://github.com/valentinleconte/openrag-twin/tree/main/communication).
