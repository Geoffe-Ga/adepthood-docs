# API — transcription router

`backend/src/routers/transcription.py` (202 lines).
`APIRouter(prefix="/journal", tags=["journal"])` (`transcription.py:45`)
— a separate module from the journal router, mounting one route under the
same prefix. The Journal Photographer: post one photographed handwritten
page, get back faithful transcribed body text (`transcription.py:1-8`).

| Method | Path | Rate limit | Auth | Request | Response | Success | Errors |
| --- | --- | --- | --- | --- | --- | --- | --- |
| POST | `/journal/transcribe-page` | 20/minute | JWT (+ optional `X-LLM-API-Key` header) | `TranscribePageRequest` (`image_base64`, `media_type`) | `TranscribePageResponse` (`text`) | 200 | 422 `invalid_image` / `image_too_large` / `model_lacks_vision`, 402 (wallet empty, from `preflight_deduction`), 502 `llm_provider_error` |

## Strict ordering — never bill a failed pass

"Validate the image before charging, charge before the LLM call, and
roll the charge back on any provider failure — so a rejected or failed
request never bills the wallet" (`transcription.py:5-8`). The handler
sequence (`transcription.py:170-202`): `_validate_image` → wallet
`preflight_deduction` → `_run_transcription` (rolls the session back on
either provider error, `transcription.py:142-167`) →
`record_llm_usage(journal_entry_id=None)` → one atomic commit.

## Image validation (cheapest check first)

(`transcription.py:121-139`): (1) an encoded-length pre-guard rejects
oversize payloads "without allocating the decoded bytes" (base64 4/3
expansion + padding, `transcription.py:52-56`); (2) strict base64 decode
→ 422 `invalid_image`; (3) decoded cap `MAX_TRANSCRIBE_IMAGE_BYTES` =
5 MB — matching the provider's own per-image ceiling so oversize is
rejected "before any wallet or LLM work" (`transcription.py:47-50`);
(4) magic-byte sniff (JPEG/PNG/WebP prefixes via a dispatch table, no
python-magic dependency) against the declared media type
(`transcription.py:63-95`).

## Notable decisions

- **Stateless**: no journal row is written; the metered `LLMUsageLog`
  row carries `journal_entry_id=None` (`transcription.py:180-186`;
  [data-model/commerce-wallet](../data-model/commerce-wallet.md)).
- **Rate limit** is double the resonance endpoint's 10/minute because "a
  single capture session can fan out to ~10 page calls"
  (`transcription.py:58-61`).
- **`model_lacks_vision` vs 502**: `LLMVisionUnsupportedError` is
  checked before its parent `LLMProviderError` — a text-only model is a
  well-formed request the model cannot serve (422), distinct from a
  genuine upstream failure (502) (`transcription.py:145-167`).
- **Privacy invariant**: the base64 payload and transcribed text are
  never logged or interpolated into exceptions; only user id and token
  count are (`transcription.py:10-12,188-201`).
- The prompt is the deterministic guardrailed constant from
  [domain/transcription](../domain/transcription.md).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
