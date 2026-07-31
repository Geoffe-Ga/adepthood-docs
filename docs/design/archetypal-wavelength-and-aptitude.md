# The Archetypal Wavelength and the APTITUDE program

The conceptual model underneath every product in the ecosystem, as
implemented as of 2026-07-31. Sources: aptitude-course `README.md` and
`CLAUDE.md`, adepthood `NORTH-STAR.md`, wavelength-demo `README.md`.

## The ten stages (Aspects, Frequencies)

APTITUDE (*Adepthood: Praxis and Theory for Integrating, Tuning, and
Unbridling from Determinism Effectively*) is a ten-stage, 36-week program.
The stages reframe Wilber/Graves developmental models: not a ladder to
climb but **notes on a musical scale** — wholeness is the ability to play
the right chord for the moment, with all ten notes available.

1. BEIGE — Yes-And-Ness (Agency)
2. PURPLE — Yes-And-Ness (Receptivity)
3. RED — Self-Love
4. BLUE — Community Love
5. ORANGE — Intellectual Understanding
6. GREEN — Embodied Understanding
7. YELLOW — Systems Wisdom
8. TEAL — True Self Connection
9. ULTRAVIOLET — Unity
10. CLEAR LIGHT — Emptiness (śūnyatā)

Each stage ships a key practice, an ongoing habit, and journaling prompts
(aptitude-course `markdown/<NN>-<stage>/`). The same ten-fold structure
appears as Adepthood's **Aspects**, Creek-Vault's **Frequencies**, and the
watch catalog's layers — one ontology, three products
(adepthood `NORTH-STAR.md`, section 11).

## The six phases (the Wavelength)

The Archetypal Wavelength is the rhythm running under the stages: **Rising →
Peaking → Withdrawal → Diminishing → Bottoming Out → Restoration**. Each
stage's course chapter breaks all six phases down with medicinal (Rx) and
overdose (OD) expressions; WavelengthWatch surfaces those side by side with
self-care strategies; wavelength-demo renders the wave itself, with vertical
position encoding energy and direction encoding valence.

A precise distinction the products carry: a **wavelength** is a trajectory
through time; a **cycle** is the same shape with time removed and the
arrows looping back (wavelength-demo `README.md`; adepthood `NORTH-STAR.md`,
section 5).

## The cadence as implemented in Adepthood

One rhythm paces every opt-in ring: a 36-week arc — the first eight stages
at three weeks each, the final two (Unity, Emptiness) at six weeks each. It
governs when journal prompts shift, when a new habit is offered, when the
practice ramp steps up, and how the course reading drips (`release_day` in
aptitude-course's `manifest.json`; adepthood backend
`domain/program_calendar.py`, `domain/stage_progress.py`).

The arc loops rather than ends: finish Stage 10, begin again at Stage 1,
each pass deepening balance across frequencies. Accordingly the Map is a
**wheel of wholeness** — which facets are full, which are thin — never an
altitude ranking of the traveler. The model's own ascending vocabulary
("higher frequencies") describes the territory, not the person's worth.

## Design implications

- No ranking or shaming of person or stages against each other; no
  streak-shame when a phase turns down.
- Phase-awareness is a feature surface: journal entries are
  ontology-classified by Frequency and Wavelength phase, which is what lets
  the Higher Self reflect back phase-appropriately.
- The [graduated-engagement principle](graduated-engagement.md) decides how
  much of this model any given user ever sees.
