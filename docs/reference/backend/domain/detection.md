# domain/detection — completion detection over a journal entry

`backend/src/domain/detection.py` (195 lines). Reads an entry and decides
which of the user's tracked habits or practices the writer actually
*did*. Same trust model as [resonance](resonance.md): "the model proposes
a candidate **index** (into the supplied candidate list) plus a
**verbatim quote**; the server resolves the index against the candidates
it supplied and anchors the quote itself in the body. Model-supplied ids
and character offsets are never trusted, and anything that doesn't
resolve cleanly is dropped" (`detection.py:1-11`).

## Constants and types

| Symbol | Value | Notes |
| --- | --- | --- |
| `VALID_TARGET_TYPES` | `{"habit", "practice"}` | Domain literals; `test_detection_service` guards against `CompletionTargetType` drift (`detection.py:23-26`) |
| `LABEL_MAX` | `255` | Must match `CompletionSuggestion.label`'s `_LABEL_MAX` — "a longer detected label passes here but fails at DB insert in the endpoint layer" (`detection.py:27-29`) |
| `MAX_HITS` | `5` | Default cap (`detection.py:30`) |
| `DetectionCandidate` | `(index, target_type, target_id, name)` | Built by the server from real rows, "so `target_type`/`target_id` are trusted; the model only ever picks an `index` and copies a quote" (`detection.py:33-44`) |
| `CompletionDetected` | `(target_type, target_id, label, anchor_start, anchor_end, anchor_text)` | A resolved, anchored detection (`detection.py:55-64`) |

## `build_detection_prompt(body, candidates)`

Numbers the candidates and asks for `{"hits": [{"index": 0, "quote":
"..."}]}`. The instruction "excludes intentions, plans, and avoidance so
'I want to meditate' or 'I skipped sugar' is not read as a completion"
(`detection.py:67-93`). Leads with `MEDICATION_GUARDRAIL`; the botmason
adapter also injects it at the system role — intentionally present twice
(defense-in-depth), "do not remove either copy" (`detection.py:74-77`).

## `detect_completions(body, *, candidates, llm, max_hits=5)`

(`backend/src/domain/detection.py:177-196`):

```python
    With no candidates the LLM is never called and ``[]`` is returned — a hard
    cost guard the endpoint relies on. Otherwise hits are resolved against the
    supplied candidates (bad index/quote dropped), de-duplicated by target and by
    overlapping span, and capped at ``max_hits``.
    """
    if not candidates:
        return []
    raw = await llm.complete(build_detection_prompt(body, candidates))
    by_index = {c.index: c for c in candidates}
    return _collect_hits(body, _parse_hit_drafts(raw), by_index, max_hits)
```

Resolution pipeline:

1. `_parse_hit_drafts` — well-formed items only; note the explicit
   `not isinstance(index, bool)` guard, since `True` is an `int` in
   Python (`detection.py:96-112`).
2. `_anchor_hit` — the index must address a supplied candidate; the
   quote must occur verbatim in the body (via resonance's
   `_quote_span`); the label is the sanitized quote, `None` if it cannot
   fit `LABEL_MAX` after cleaning (`detection.py:115-145`).
3. `_is_duplicate` — a hit is dropped if its `(target_type, target_id)`
   was already kept **or** its span overlaps any kept span (shared
   `_overlaps` from resonance) (`detection.py:148-154`).
4. Cap at `max_hits` (`detection.py:157-174`).

## Worked example

Candidates `[0: "Meditation" (practice, up_id=9), 1: "Hydrate" (habit,
goal_id=4)]`; body `"Sat for twenty minutes this morning."`; model
returns hits `[{index: 0, quote: "Sat for twenty minutes"}, {index: 0,
quote: "this morning"}, {index: 7, quote: "..."}]` → hit 1 anchors and is
kept; hit 2 is dropped (duplicate target); hit 3 is dropped (unknown
index). Result: one `CompletionDetected` targeting the practice, whose
acceptance would create a `CompletionSuggestion` row
([data-model/journal-reflection](../data-model/journal-reflection.md)).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
