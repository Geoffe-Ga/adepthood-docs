# WavelengthWatch

As of the 2026-07-31 baseline seed (issue #3).

WavelengthWatch puts the Archetypal Wavelength on the wrist: a watchOS-only
companion for browsing every layer and phase of the model, seeing
"medicinal" and "toxic" expressions side by side, and reaching context-aware
self-care strategies in the moment you need them.

## What it does for its user

- **Browse the whole curriculum from the watch** — layers and phases,
  ordered consistently, with the full catalog cached on-device (24-hour
  TTL) so it works offline.
- **See both edges of every phase.** Each phase surfaces its healthy (Rx)
  and unhealthy (toxic/OD) expressions together, making the model a
  real-time self-check rather than reading material.
- **Log from the wrist.** A journal loop records which curriculum entry and
  strategy matched your moment — stored locally first, synced to the
  backend only if cloud sync is enabled (privacy-first).
- **Stay current.** Background refresh keeps content fresh without
  foreground use.

## How to use it

Today: build and run from source —
[Run WavelengthWatch locally](../how-to/run-wavelengthwatch-locally.md).
The project has not yet been deployed to production; an App Store launch is
planned (WavelengthWatch `README.md`).

## Cross-repo relationships

The watch serves the same six-phase model that the course teaches in depth
and the app paces life around — sized for the two-second glance instead of
the twenty-minute read. `wavelength-demo` promotes it, and its knowledge
graph federates into adepthood's pan-graph like every other satellite.
