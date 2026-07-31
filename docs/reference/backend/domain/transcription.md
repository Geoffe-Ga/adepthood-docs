# domain/transcription — the Journal Photographer prompt

`backend/src/domain/transcription.py` (64 lines). Builds the plain-text
instruction sent to the LLM when a user photographs a handwritten journal
page to turn it into faithful body text. Unlike its sibling
resonance/detection prompt builders it deliberately returns *body text
only* — no STRICT-JSON response contract, "because the model's job here
is transcription, not structured extraction" (`transcription.py:1-9`).

## `build_transcription_prompt() -> str`

Pure, zero-argument, deterministic: the shared medication-safety
guardrail from [domain/care](care.md) followed by fixed transcription
instructions (`backend/src/domain/transcription.py:57-64`):

```python
def build_transcription_prompt() -> str:
    """Return the handwriting-transcription prompt (guardrail + conventions).

    Pure, zero-argument, and deterministic: the medication-safety guardrail
    followed by the fixed transcription instructions, identical on every call.
    Returns body-text instructions only — no STRICT-JSON response contract.
    """
    return f"{MEDICATION_GUARDRAIL}\n\n{_TRANSCRIPTION_INSTRUCTIONS}"
```

Determinism is a cost decision: "Holding the whole instruction as a
fixed string means every call sends byte-identical text, which lets the
provider serve prompt-cache hits across requests instead of re-billing
the shared preamble each time" (`transcription.py:17-21`).

## The fixed conventions (`transcription.py:10-15,30-54`)

- Transcribe every word verbatim — no summarizing, correcting, or
  rewording.
- Illegible word → `[illegible]`, keep transcribing.
- Uncertain reading → best guess with a bracketed question mark, e.g.
  `[word?]`.
- Struck-through text is dropped entirely, never bracketed.
- Caret / margin insertions are integrated inline where the writer
  intended.
- Output is the body text only — no preamble, commentary, markdown, or
  headers.

The prompt embeds two few-shot examples (strike-through removal and an
illegible mid-sentence word, `transcription.py:47-51`).

Consumed by [api/transcription](../api/transcription.md); each metered
call logs to `LLMUsageLog` with `journal_entry_id = None` — "a stateless
call that has no associated entry"
(`backend/src/models/llm_usage_log.py:53-55`).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
