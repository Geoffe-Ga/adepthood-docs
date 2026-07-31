# 0006. Graduated engagement: "you choose your depth"

## Status

Accepted (backfilled 2026-07-31; the thesis was written 2026-06-29 in
adepthood `NORTH-STAR.md`).

## Context

Adepthood began with a course-shaped surface — stages, habits, practices,
and reading as co-equal tabs. The north-star review (`NORTH-STAR.md`)
concluded that mandatory curriculum framing conflicts with the product's
ethos (anti-guru, anti-lock-in, care boundaries) and with how its four
personas actually engage: most people flourish at different, self-chosen
depths, and some flourish by eventually leaving.

## Decision

Make the journal the floor and every other system an optional, independent
ring. The governing principle is **"you choose your depth"**: nothing past
the journal is mandatory, nothing is gated behind anything else, and deeper
rings (prompted journaling, habit scaffolding, the practice ramp, the course
reading, the Digital Sangha) are offered only as resonant, one-tap-declinable
invitations — never gamified pressure, streak-shame, or guilt mechanics. The
Map reads as a wheel of wholeness (balance across ten facets), never as
altitude climbed. Success explicitly includes a user outgrowing the app.

## Consequences

- The invitation engine becomes a first-class subsystem with resonance
  gating (backend `domain/invitations.py`, `domain/resonance.py`,
  `models/invitation_signal.py`, `models/user_depth_preferences.py`).
- Every feature epic is re-scoped through this lens: journal-as-home
  navigation, opt-in course, wheel-shaped Map, surfaced privacy.
- Dark patterns are structurally forbidden — any design that punishes
  leaving or shames shallowness fails review regardless of engagement
  metrics.
- Care guardrails are load-bearing: the app complements professional
  mental-health care, never replaces it, and must surface human pathways in
  acute distress (`NORTH-STAR.md`, section 10; backend `domain/care.py`,
  `domain/safety.py`).
- The docs treatment lives at
  [Graduated engagement](../design/graduated-engagement.md).
