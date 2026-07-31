# domain/resonance — anchored margin notes from an LLM

`backend/src/domain/resonance.py` (248 lines). Turns a journal entry
into anchored margin notes. Pure domain logic with the LLM injected — no
FastAPI, no DB. The trust model is the module's spine: "The model
proposes short notes with a verbatim `quote` from the body; we resolve
each quote to character offsets *ourselves* (never trusting
model-supplied indices) and drop anything that doesn't anchor cleanly"
(`resonance.py:1-7`).

## Constants and types

| Symbol | Value / shape | Notes |
| --- | --- | --- |
| `VALID_KINDS` | `{"theme", "connection", "symbol"}` | Literals, not imported from `models.marginalia`, so the domain stays DB-free; `test_resonance_service` guards against enum drift (`resonance.py:19-21`) |
| `ANCHOR_TEXT_MAX` / `NOTE_MAX` / `ESSAY_MAX` | `280` / `600` / `10_000` | Mirror the model columns (`resonance.py:22-24`) |
| `_DEFAULT_MAX_NOTES` | `5` | Cap per entry (`resonance.py:25`) |
| `MAX_PRIOR_ENTRIES` / `_PRIOR_ENTRY_CHARS` | `5` / `1000` | Bounds the prompt cost "so a caller passing a long history can't blow up the context window / token bill" (`resonance.py:26-29`) |
| `ResonanceLLM` | Protocol: `async complete(prompt) -> str` | The minimal injected seam (`resonance.py:71-74`) |
| `_AnchoredSpan` | Protocol with `anchor_start`/`anchor_end` | Lets `_overlaps` serve both this module and `detection.CompletionDetected` without cross-imports (`resonance.py:32-48`) |

## `build_prompt(body, prior_entries=None, max_notes=5)`

Structured STRICT-JSON prompt (`{"notes": [{"kind", "quote", "note"}]}`)
asking for warm second-person notes, with prior entries (capped and
truncated) supplied "for 'connection' notes only" in a `<prior>` block
(`resonance.py:77-110`). It **leads with the medication guardrail**, and
the duplication is deliberate (`backend/src/domain/resonance.py:82-85`):

```python
    Leads with :data:`~domain.care.MEDICATION_GUARDRAIL`. The botmason adapter
    (:class:`services.marginalia.BotmasonResonanceLLM`) also injects the same
    guardrail at the system role, so it is intentionally present twice on this
    path (defense-in-depth) — do not "deduplicate" by removing either copy.
```

## `generate_marginalia(body, *, llm, prior_entries=None, max_notes=5)`

The pipeline (`resonance.py:187-210`):

1. `_parse_drafts` / `_load_json_list` — defensive JSON parsing; any
   malformed payload or item yields `[]`/skip, never an exception
   (`resonance.py:113-139`).
2. `_anchor` — kind must be in `VALID_KINDS`; `_quote_span` locates the
   quote **verbatim** with `body.find(quote)` (empty or >280-char quotes
   rejected); the note is sanitized via `security.sanitize_user_text`
   with `NOTE_MAX` (`resonance.py:142-174`).
3. Overlap dedupe — half-open span intersection
   (`a.anchor_start < b.anchor_end and b.anchor_start < a.anchor_end`),
   first note wins (`resonance.py:177-184,205-206`).
4. Cap at `max_notes` (`resonance.py:207-209`).

`anchor_text` is re-sliced from the body (`body[start:end]`), not taken
from the model (`resonance.py:168-172`).

## `generate_essay(*, llm, body, anchor_text, kind, note) -> str`

Expands one note into "a short, warm letter" — plain prose, no JSON
(`resonance.py:213-230,243-247`). `_sanitize_essay` truncates to
`ESSAY_MAX` rather than raising; if NFC normalization expands the text
back over the cap, it re-trims at `ESSAY_MAX // 2` for headroom
(`resonance.py:233-240`).

## Worked example

Model returns
`{"notes": [{"kind": "theme", "quote": "the river kept moving", "note": "..."},
{"kind": "vibe", ...}, {"kind": "symbol", "quote": "not in the body", ...}]}`:
note 1 anchors at the quote's `find` offset; note 2 is dropped (invalid
kind); note 3 is dropped (quote not found). Result: one anchored note.

Consumers: the journal resonance path and marginalia essay generation —
see [api/botmason](../api/botmason.md) and [api/journal](../api/journal.md);
persistence shapes in
[data-model/journal-reflection](../data-model/journal-reflection.md).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
