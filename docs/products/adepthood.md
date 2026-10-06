# Adepthood (the app)

As of the 2026-07-31 baseline seed (issue #3).

Adepthood is, at its floor, a private journal-first personal knowledge base
whose growing body of writing becomes a "Higher Self" that reflects the
user's own wisdom back in the language of the APTITUDE program and the
Archetypal Wavelength. Around that floor sit optional, self-chosen depths —
prompted journaling, habit scaffolding, a practice ramp, the course reading,
and the Digital Sangha. Nothing is gated, nothing is mandatory: **you choose
your depth** (adepthood `NORTH-STAR.md`).

## Feature surface

- **Journal + Higher Self (the floor, always on).** Free writing folded
  into a private, encrypted store of the writer's own words, tagged by
  stage and Wavelength phase, that speaks back — noticing when a new entry
  echoes an older one, adding marginalia, and lifting out quotes worth
  keeping.
- **Prompted journaling.** Stage-aligned prompts that carry a writer
  through the ten Aspects of Wholeness implicitly.
- **Habits.** Opt-in one-habit-per-stage scaffolding with energy planning,
  streaks, and tiered goals — and no streak-shame by design.
- **Practice.** An opt-in ramp of timed practices (eleven kinds,
  including breathwork, grounding variants, and card meditation) with a
  launchable timer, sound cues, a browsable catalog, custom practices, and
  share links.
- **Course.** The APTITUDE reading, arriving on each stage's schedule from
  a fixed edition of the course text.
- **Map.** A wheel of wholeness showing balance across the ten facets —
  never altitude climbed.
- **Invitations.** Openings toward deeper rings, offered only when your own
  writing calls for one and declinable in a single tap — the "wise friend"
  test governs every one.

## Who it serves

Four personas from the north star, each settling at a different depth: the
Householder Shaman (guided completion of unfinished initiations), the
Neurospicy User Manual (the Wavelength as a manual for one's moods), the
Chronically Online mystic (a Sangha designed to springboard them back to
embodied life), and the Liminal Creep becoming a Whole Adept (the full
36-week loop, repeatedly). The app's deepest success for any user is its
own eventual obsolescence — leaving whole is the telos.

## Cross-repo relationships

- Consumes `aptitude-course` via the manifest contract
  ([architecture](../architecture/aptitude-course.md)).
- Shares its ontology with Creek-Vault (Aspects = Frequencies) and a Creek
  Vault MCP seam is part of the product thesis.
- Publishes the knowledge-graph release that federates all five repos.

Platform: iOS/Android/web via Expo. Status: pre-launch; the roadmap's
Phase 1 ("Make It Real") has shipped and later phases are in flight
(`prompts/github-issues/README.md`).
