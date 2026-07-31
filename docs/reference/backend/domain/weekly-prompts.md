# domain/weekly_prompts — the 36 weekly reflection prompts

`backend/src/domain/weekly_prompts.py` (143 lines). Seed data and lookup
helpers for the 36 weekly reflection prompts across the APTITUDE program,
grouped three weeks per Archetypal Wavelength band
(`weekly_prompts.py:1-16`).

## Data

- `WEEKLY_PROMPTS: dict[int, str]` — exactly one prompt question per week
  1..36 (`weekly_prompts.py:20-95`). Bands in order: Beige (1-3), Purple
  (4-6), Red (7-9), Blue (10-12), Orange (13-15), Green (16-18), Yellow
  (19-21), Turquoise (22-24), Coral (25-27), Teal (28-30), Indigo
  (31-33), Ultraviolet (34-36).
- `TOTAL_WEEKS = 36` (`weekly_prompts.py:97`).
- `PROMPT_BANDS` — the 12 band labels in developmental order; "each band
  spans `WEEKS_PER_BAND` consecutive weeks, so the 12 bands tile the
  36-week program exactly (12 * 3 == TOTAL_WEEKS)"
  (`weekly_prompts.py:99-115`).
- `WEEKS_PER_BAND = 3`; `PROMPTS_PER_WEEK = 1` — named "so the ordinal in
  the title isn't a bare literal" (`weekly_prompts.py:117-122`).

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

*Grounded in adepthood@fbc529d, 2026-07-31.*
