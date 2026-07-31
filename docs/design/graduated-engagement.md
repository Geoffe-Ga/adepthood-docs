# Graduated engagement: "you choose your depth"

Adepthood's governing product-design principle. Sources: adepthood
`NORTH-STAR.md` (the thesis, written 2026-06-29) and `AGENTS.md` (the
build-time restatement). Recorded as
[ADR 0006](../decisions/0006-graduated-engagement.md).

## The floor

Everyone who opens Adepthood gets the same thing first: a place to write.
Entries fold into a private, encrypted, ontology-classified corpus (tagged
by Frequency and Wavelength phase), and over time that corpus speaks back —
the **Higher Self** retrieves the user's own past reflections and reflects
them back, calibrated to where they are now, in the language of APTITUDE.
This floor is a complete product on its own: no course, no stages, no
streaks required.

## The rings

Around the floor sit optional depths — concentric rings, not a ladder:

- **Prompted journaling** — stage-aligned prompts move a person through the
  ten Aspects implicitly, without "taking a course."
- **Habit scaffolding** — opt-in, one new habit per stage, cumulative, with
  energy scaffolding, streaks, and tiered goals.
- **The practice ramp** — opt-in timed mindfulness, breathwork, or movement
  escalating at the stage cadence.
- **The course material** — substantial Aspect teachings, drip-fed at the
  stage pace.
- **The Digital Sangha** — community as springboard and support.

Any ring, any combination, free movement between them. Nothing is gated
behind anything else.

## The rules that make it real

- **Sovereignty.** Invitations to go deeper appear only when resonant with
  what the person has been writing or doing; they are subtle, one-tap
  declinable, never nagging, and never frame declining as failure. The test:
  would a wise friend actually say this right now, unprompted? If not, the
  app stays quiet.
- **Anti-guru.** The wisdom reflected back is the user's own.
- **Anti-lock-in, pro-renunciation.** The telos is to springboard people
  back to embodied community as Whole Adepts; success includes outgrowing
  the app. Anything that makes leaving harder is forbidden — no dark
  patterns, no streak-shame, no guilt mechanics.
- **Care boundaries.** The app complements professional mental-health care
  and never replaces it; features touching Dark Nights or acute distress
  must surface pathways to human support.
- **Privacy as pitch.** Intimate content is routed locally and encrypted at
  rest, surfaced as a feature
  ([ADR 0012](../decisions/0012-local-first-privacy-tiers.md)).

## How it shows up in the code

The invitation engine and depth preferences are first-class backend
subsystems (`backend/src/domain/invitations.py`, `resonance.py`,
`depth_preferences.py`; `backend/src/models/invitation_signal.py`,
`user_depth_preferences.py`; `backend/src/routers/depth_preferences.py`,
`invitations.py`). The Map is being built as a wheel of balance, and
navigation treats the journal as home. A user who stays at the journal
floor for years has used Adepthood exactly correctly.
