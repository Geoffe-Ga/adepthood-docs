# domain/safety — acute-distress screening

`backend/src/domain/safety.py` (375 lines). A pure, deterministic
*screen* — "not a diagnosis, not treatment, not advice"
(`safety.py:1-10`). `assess_distress(text)` returns a typed
`DistressSignal(level, category)` where `level` is `"elevated"` only for
explicit **acute** phrasing in four categories (`DistressCategory`,
`safety.py:83-90`): `suicidal_intent`, `self_harm`,
`medication_cessation`, `intent_to_harm`. Consumed by the journal care
path: `POST /journal/{entry_id}/resonance` screens the entry and, on an
elevated signal, returns the [care surface](care.md) alongside the
reflection (`safety.py:8-10`).

## Deliberately conservative

The design statement (`backend/src/domain/safety.py:14-23`):

```text
Adepthood honors ordinary darkness — grief, sadness, emptiness, the "dark night
of the soul", existential struggle — as real developmental territory, and must
never pathologize it (NORTH-STAR §10). So matching is intentionally narrow: each
category fires only on phrasing that expresses *acute intent or action* ...
When phrasing is ambiguous between ordinary darkness and acute distress we
prefer **not** to flag ... The phrase lists below are explicit and auditable
rather than clever; add to them only with a corresponding negative test
guarding ordinary darkness.
```

## The phrase lists (`safety.py:113-158`)

Explicit regex alternations per category, matched case-insensitively on
word boundaries — e.g. `kill myself`, `end my life`, `want to die`,
`better off dead` (suicidal intent); `hurt myself`, `self[ -]harm`
(self-harm); `kill (him|her|them|someone|everyone)` (intent to harm);
`stop(ping|ped)? (taking )?(my )?(meds|medication|pills|antidepressants)`
(medication cessation). Categories are checked in list order; the first
non-denied match wins (`safety.py:108-112,371-374`).

## Normalization (`_normalize`, `safety.py:328-343`)

Pipeline order is load-bearing: (1) fold six alternate apostrophe code
points to ASCII `'` — *before* NFKC, which would decompose U+00B4 into
space + combining acute (`safety.py:165-177`); (2) neutralize every
Unicode format character (category `Cf`: zero-width, bidi controls, soft
hyphen) to a space so "invisible splices cannot defeat matching"
(`safety.py:179-181`); (3) NFKC (folds fullwidth forms); (4) lowercase +
whitespace collapse. Rationale: "the dangerous failure direction for a
crisis screen is a false negative" (`safety.py:29-32`).

## Negation handling (deterministic, no parser)

- **Window**: a match is suppressed only by a negator in the last
  `_NEGATION_WINDOW_WORDS = 5` tokens strictly *before* it, clipped to
  the current clause — boundaries are `. ! ? ; ,` **and** the
  coordinating conjunctions `and`/`but` (`safety.py:183-218,231-241`).
  `or`/`nor` deliberately do **not** clip: "I would never kill myself or
  hurt myself" is a single denial (`safety.py:203-209`).
- **Logical negators** (`never`, `not`, `no plans to`, `don't`, …) count
  by **parity**: odd negates, even (including zero) does not — double
  negation ("I can't say I don't want to die") still flags
  (`safety.py:186-195,244-256`). Bare `no` is excluded: it would negate
  "No. I want to kill myself" (`safety.py:188-189`).
- **Temporal negators** (`no longer`, `used to`) negate only when
  directly abutting the match — "more than I used to I want to die"
  still flags (`safety.py:197-201`).
- **Or-chain inheritance**: a match that is the bare right conjunct of
  an "X or Y" / "X nor Y" coordination is suppressed when its left acute
  conjunct is itself denied, resolved *iteratively* with memoization so
  "an adversarially long or-chain terminates without RecursionError"
  (`safety.py:58-67,259-325`); each walk step moves strictly leftward,
  and caching collapses overlapping walks "from cubic to quadratic total
  work" (`safety.py:304-308`). Any intervening words break the
  coordination — "I have no plans to kill myself or I will hurt myself"
  still flags the self-harm conjunct (`safety.py:65-67`).
- A negator that is *part of* a positive phrase (the "don't" in "don't
  want to be alive anymore") can never self-suppress, because only text
  strictly before the match is inspected (`safety.py:54-56,247-248`).

## Worked examples

| Input | Result |
| --- | --- |
| "I feel empty and lost in the dark night of the soul" | `none` — ordinary darkness passes through |
| "I want to die" | `elevated` / `suicidal_intent` |
| "I would never kill myself" | `none` — one logical negator in the window |
| "I can't say I don't want to die" | `elevated` — even count is not, odd is; here two negators = even… the parity rule counts `can't` + `don't` = 2 → *not* negated → flags |
| "I would never kill myself or hurt myself" | `none` — the denial is inherited across `or` |
| "I would never hurt myself, but I want to kill him" | `elevated` / `intent_to_harm` — the comma and `but` clip the window |
| "I used to cut myself" | `none` — abutting temporal negator |

Purity: standard library only — no FastAPI, SQLModel, network, or LLM
imports (`safety.py:69`).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
