# domain/care — the care surface and medication guardrail

`backend/src/domain/care.py` (132 lines). Non-clinical care resources
surfaced on an acute-distress signal. Pure, reviewable, localizable data —
no FastAPI, no DB, no network, no LLM (`care.py:1-3`). When
`domain.safety.assess_distress` screens an entry as carrying an
acute-distress signal, "the care surface must accompany — and never be
replaced by — the AI's reflection, so a distressed person is pointed at
**human and professional** support rather than left alone with a chatbot
(NORTH-STAR §10)" (`care.py:4-8`).

The module's own boundary statement (`backend/src/domain/care.py:12-17`):

```python
These are *pointers*, not care: a warm, non-shaming invitation plus a short,
auditable list of ways to reach a person (988, Crisis Text Line, someone you
trust) and a professional. There is **no diagnosis, no medication guidance, no
treatment advice** here — that belongs to a person and their prescriber, not to
software. The copy is gathered into module constants precisely so it can be
reviewed and localized in one place rather than scattered through a handler.
```

## Types

- `CareKind = Literal["hotline", "text_line", "human", "professional"]`
  (`care.py:25`).
- `CareResource` (frozen): `kind`, `name`, `contact`, `what_it_is`
  (`care.py:28-40`).
- `CarePayload` (frozen): `message` + `resources`, "returned alongside
  (never instead of) the resonance reflection" (`care.py:43-52`).

## Constants

- `CARE_MESSAGE` — a warm, non-shaming invitation that explicitly does
  not frame distress as failure (`care.py:55-65`).
- `CARE_RESOURCES` — exactly four pointers, ordered: 988 Suicide & Crisis
  Lifeline (hotline), Crisis Text Line (text `HOME` to 741741), someone
  you trust (human), a mental-health professional (`care.py:67-106`).
  "Order leads with the immediate crisis lines, then a trusted person,
  then professional care" (`care.py:67-69`).
- `MEDICATION_GUARDRAIL` — a safety instruction addressed to the *model*,
  embedded in **every** prompt that sends a user's writing to an LLM
  (`backend/src/domain/care.py:116-122`):

```python
MEDICATION_GUARDRAIL = (
    "Safety boundary: never advise the writer to reduce, stop, or change any "
    "medication — including psychiatric medication — and never suggest a "
    "specific dose. That decision belongs to the writer and their prescriber. "
    "Affirm the writer's agency and, when medication comes up, defer it to them "
    "and their prescriber rather than offering medical direction."
)
```

One shared constant means each prompt builder imports the same boundary,
"so it can be reviewed and revised in exactly one place rather than
drifting across builders" (`care.py:109-115`). Importers:
[resonance](resonance.md), [detection](detection.md),
[transcription](transcription.md).

## `build_care_payload() -> CarePayload`

Pure and deterministic — the same constants every time, "derived from
nothing user-specific so it can never leak across users"
(`care.py:125-132`). Triggered by the distress screen in
[safety](safety.md); delivered by the resonance path in
[api/botmason](../api/botmason.md).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
