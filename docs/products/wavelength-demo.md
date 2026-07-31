# wavelength-demo

As of the 2026-07-31 baseline seed (issue #3).

A scroll-driven single-page site that makes the Archetypal Wavelength
visceral: one sine wave stays fixed in the center of the screen while
scrolling headers rename its six phases as nineteen different "modes" of
the same wave — the Addiction Wavelength, the Enshittification Wavelength,
the Wavelength of the Seasons, and more.

## What it does for its visitor

- **One idea, felt.** The same six-phase shape — Rising, Peaking,
  Withdrawal, Diminishing, Bottoming Out, Restoration — recurs under an
  astonishing range of human and natural rhythms; watching nineteen modes
  ride one wave makes the claim land in seconds.
- **Meaningful geometry.** Vertical position encodes energy (white crest to
  black trough) and direction encodes valence (warm yellow ascending, cool
  purple descending), so "Bliss" and "Depression" sit exactly where you
  feel they should.
- **A trajectory, not a loop.** The page is explicit that it renders a
  wavelength (through time), not a cycle — the conceptual distinction the
  whole ecosystem maintains.
- **Doors deeper.** It links to the Archetypal Wavelength philosophy and
  the WavelengthWatch app for people who want more than the demo.

## Content provenance

Every mode and phase string is quoted verbatim from the "Expanded List"
sheet of the Archetypal Wavelength spreadsheet (rows marked for inclusion),
kept in `src/data/modes.ts`; modes are colored by AQAL quadrant. Editorial
framing (titles, glosses) is the only added text.

## How to use it

Visit the deployed page, scroll. To run or develop it:
[Run wavelength-demo locally](../how-to/run-wavelength-demo-locally.md).

## Cross-repo relationships

The ecosystem's marketing front door: pure promotion for the philosophy,
the watch, and (by shared vocabulary) the course and app. No runtime
dependencies on the other repos — its only coupling is the ontology.
