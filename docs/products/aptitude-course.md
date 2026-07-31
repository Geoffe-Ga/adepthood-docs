# APTITUDE Course

As of the 2026-07-31 baseline seed (issue #3).

The APTITUDE course is a ten-stage, 36-week rite of passage "from Liminal
Creep to Whole Adept — from insight to embodiment, from temporary
enlightenment to sustainable practice" (aptitude-course `README.md`). The
repo is the curriculum itself: roughly 130k+ words of teaching content,
versioned like software.

## What it does for its reader

- **Ten stages as notes on a scale.** BEIGE through CLEAR LIGHT, each a
  capacity to bring online — not a rung to climb past. Wholeness is playing
  the right chord for the moment.
- **A complete container per stage.** Each stage ships ~11,000–14,000 words
  across sections: the stage's mood with integrated/repressed/excessive
  expressions, journaling prompts, a key practice with alternatives, a
  default habit, gift and shadow, divine gender, and a full six-phase
  Wavelength breakdown with medicinal and overdose expressions per phase.
- **A rhythm to live by.** Sections carry `release_day` pacing so the
  reading drips over the 36-week arc rather than arriving as a wall of
  text.

## Audience

Written for "neurodivergent spiritual seekers who struggle with embodiment
despite having mystical insights" (aptitude-course `CLAUDE.md`) — the same
people the app's four personas describe.

## How it is consumed

Readers meet the course through the Adepthood app's Course ring; the app
vendors a pinned commit and reads through `manifest.json` only
([ADR 0011](../decisions/0011-manifest-consumption-contract.md)). Authors
work in Markdown under `markdown/`, following `CONTENT_FORMAT.md`, and
rebuild the manifest —
[Build the manifest](../how-to/build-the-aptitude-course-manifest.md).

## Cross-repo relationships

The course is the canonical text of the ontology every other product
implements: the app paces it, the vault classifies by it, the watch
condenses it, and the demo page advertises its central wave.
