# domain/weekly_prompts — the 36 weekly reflection prompts

`backend/src/domain/weekly_prompts.py` (143 lines). Seed data and lookup
helpers for the 36 weekly reflection prompts across the APTITUDE program,
grouped by APTITUDE stage band — three weeks each for Beige through Teal,
six each for Ultraviolet and Clear Light (`weekly_prompts.py:11-18`).

## Data

- `WEEKLY_PROMPTS: dict[int, str]` — exactly one prompt question per week
  1..36 (`weekly_prompts.py:20-95`). Bands in order, each spanning its
  stage's weeks: Beige (1-3), Purple (4-6), Red (7-9), Blue (10-12),
  Orange (13-15), Green (16-18), Yellow (19-21), Teal (22-24), Ultraviolet
  (25-30), Clear Light (31-36) — "the ten APTITUDE positions, Beige
  through Clear Light" (`weekly_prompts.py:11-18`).
- `TOTAL_WEEKS = 36` (`weekly_prompts.py:97`).
- `PROMPT_BANDS` — the ten band labels in course order (the order the
  program introduces each capacity, not a ranking); "Taken straight from
  the frequency vocabulary so this module cannot drift from it"
  (`weekly_prompts.py:41-44`). Each band spans its own entry in
  `WEEKS_PER_STAGE` — `(3, 3, 3, 3, 3, 3, 3, 3, 6, 6)` — so the ten bands
  tile the 36-week program exactly: "Ten stages does not mean thirty
  weeks" (`weekly_prompts.py:15-18`, `constants.py:30-41`).
- `WEEKS_PER_STAGE` — re-exported from `domain.constants` as "the
  companion of `PROMPT_BANDS` (weeks each band spans, same order)", because
  "there is no single weeks-per-band number — the last two bands are twice
  as long as the rest" (`weekly_prompts.py:50-53`). The `WEEKS_PER_BAND = 3`
  and `PROMPTS_PER_WEEK = 1` constants that the `prompt_title_for_week`
  excerpt below reads from existed only at adepthood@fbc529d; neither is in
  the module on `main`.

## Functions

`get_prompt_for_week(week_number) -> str | None` — dictionary lookup;
`None` out of range (`weekly_prompts.py:125-127`).

`prompt_title_for_week(week_number) -> str | None` — the default journal
title for a week's prompt submission
(`backend/src/domain/weekly_prompts.py:130-143`):

```python
    if week_number < 1 or week_number > TOTAL_WEEKS:
        return None
    band = PROMPT_BANDS[(week_number - 1) // WEEKS_PER_BAND]
    week_in_band = ((week_number - 1) % WEEKS_PER_BAND) + 1
    return f"{band} week {week_in_band} Prompt #{PROMPTS_PER_WEEK}"
```

That `// WEEKS_PER_BAND` arithmetic assumes every band is three weeks
long, which is only true of Beige through Teal. The module now walks
`WEEKS_PER_STAGE` week by week instead (`_place_of_week`,
`weekly_prompts.py:122-132`), so weeks 25-30 land in Ultraviolet and
31-36 in Clear Light.

Worked example from the docstring: week 8 (the second Red week) →
`"Red week 2 Prompt #1"`. "This is the default a user sees in the compose
title; they may override it" (`weekly_prompts.py:135-137`).

## Consumers

- [api/prompts](../api/prompts.md) serves the week's prompt and stores
  answers as `PromptResponse` rows (unique per `(user, week)`,
  `backend/src/models/prompt_response.py:19-21`).
- [program-calendar](program-calendar.md) imports `TOTAL_WEEKS` as the
  week clamp (`backend/src/domain/program_calendar.py:22`).

---

*Grounded in adepthood@fbc529d, 2026-07-31. Band schedule, `PROMPT_BANDS`
and `WEEKS_PER_STAGE` claims re-verified against adepthood@78fb127 (`main`),
2026-10-03. The `prompt_title_for_week` excerpt and its worked example, with
the `WEEKS_PER_BAND` / `PROMPTS_PER_WEEK` constants they read from, describe
adepthood@fbc529d only; `main` builds the title in
`WeekPrompt.default_title` (`weekly_prompts.py:92-99`) from the
`WEEKS_PER_STAGE` walk.*
