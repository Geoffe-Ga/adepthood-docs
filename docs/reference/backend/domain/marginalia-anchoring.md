# domain/marginalia_anchoring — re-anchoring notes after edits

`backend/src/domain/marginalia_anchoring.py` (38 lines). Pure string
logic — no LLM, no DB. When a journal entry's body changes, each margin
note either re-anchors to its snapshot text or is marked stale; notes are
never deleted on edit (`marginalia_anchoring.py:1-6`).

## API

`reanchor_one(anchor_text, anchor_start, new_body) -> ReanchorResult`
where `ReanchorResult` is a frozen dataclass of
`(anchor_start, anchor_end, stale)` (`marginalia_anchoring.py:13-19`).

The complete algorithm (`backend/src/domain/marginalia_anchoring.py:22-38`):

```python
def reanchor_one(anchor_text: str, anchor_start: int, new_body: str) -> ReanchorResult:
    """Re-locate ``anchor_text`` in ``new_body``.

    - Fast path: if the old offsets still spell ``anchor_text``, keep them.
    - Else the **first** occurrence of ``anchor_text`` becomes the new span
      (documented choice; duplicate passages anchor to the earliest match).
    - Empty ``anchor_text`` or no occurrence → stale, offsets left unchanged.
    """
    if not anchor_text:
        return ReanchorResult(anchor_start, anchor_start, stale=True)
    end = anchor_start + len(anchor_text)
    if anchor_start >= 0 and new_body[anchor_start:end] == anchor_text:
        return ReanchorResult(anchor_start, end, stale=False)
    found = new_body.find(anchor_text)
    if found != -1:
        return ReanchorResult(found, found + len(anchor_text), stale=False)
    return ReanchorResult(anchor_start, end, stale=True)
```

## Rules

1. **Fast path** — old offsets still spell the snapshot exactly: span
   unchanged, not stale.
2. **Relocation** — snapshot found elsewhere: the *first* occurrence wins
   (an explicit documented choice for duplicate passages).
3. **Stale** — empty snapshot or no occurrence: `stale=True`, offsets
   left where they were (for the empty case the span collapses to
   `(start, start)`).

## Worked examples

| `anchor_text` | `anchor_start` | `new_body` | Result |
| --- | --- | --- | --- |
| `"the river"` | 4 | `"saw the river again"` | `(4, 13, stale=False)` — fast path |
| `"the river"` | 4 | `"today the river rose"` | `(6, 15, stale=False)` — first `find` |
| `"the river"` | 4 | `"all dried up"` | `(4, 13, stale=True)` — offsets untouched |
| `""` | 7 | anything | `(7, 7, stale=True)` |

## Consumers

The journal update path applies this to each `Marginalia` row (and the
mirror logic to pending `PromotedQuote` spans) when an entry body is
edited — see [api/journal](../api/journal.md). The `stale` flag maps to
`MarginaliaStatus.STALE`
(`backend/src/models/marginalia.py:31-39`).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
