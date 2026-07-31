# API — gumroad webhook router

`backend/src/routers/gumroad.py` (324 lines).
`APIRouter(prefix="/webhooks/gumroad", tags=["gumroad"])`
(`gumroad.py:59`).

| Method | Path | Auth | Request | Response | Success | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| POST | `/webhooks/gumroad/ping?secret=…` | shared secret (constant-time query-param check) | form-encoded Gumroad ping | `dict` | 200 — always, on any authenticated well-formed ping (incl. replays and unknown events) | 401 `invalid_signature` (`gumroad.py:91`), 400 `malformed_payload` (`gumroad.py:106`) |

## Design (`gumroad.py:1-27`)

- **Secret before body**: the shared secret is checked *before* the body
  is read, "so an unauthenticated caller can never drive the parser"
  (`gumroad.py:3-5`).
- **Verbatim, idempotent persistence**: valid pings persist into
  `GumroadSale`, keyed by `sale_id` — replays collapse onto the existing
  row; the row is persisted *before* the handler runs, "so an orphan
  reversal ping is captured even though it reverses nothing"
  (`gumroad.py:298-308`).
- **Always 200** on captured events so Gumroad never re-queues something
  already stored (`gumroad.py:300-302`).
- **Event dispatch** via `_EVENT_HANDLERS`, "the single table that also
  defines what counts as a known event" (`KNOWN_RESOURCE_NAMES`,
  `gumroad.py:9-10,289`).
- **Sale side effects, disjoint allowlists**: an APTITUDE product grants
  `course_access`; a token-pack product credits the wallet — "at most
  one fires", both idempotent, and "the credited amount comes solely
  from the operator-configured pack-size map — never from a payload
  field, which a forged ping would control" (`gumroad.py:12-17`;
  classification in [domain/entitlements](../domain/entitlements.md)).
- **Reversals**: `refund` and `dispute` return the money;
  `cancellation` and `subscription_ended` only stop renewals. All four
  "compete for one exactly-once claim on the stored sale"
  (`GumroadSale.revocation_processed_at`,
  [data-model/commerce-wallet](../data-model/commerce-wallet.md)) and
  read every fact off the stored row, not the ping
  (`gumroad.py:19-23`).
- **Secrets discipline**: the webhook secret, buyer email, and raw
  payload never appear in log text (`gumroad.py:25-26`); skip-reason
  markers are static tokens (`unknown_product`, `refunded_sale`,
  `sale_previously_reversed`, `token_pack_size_unconfigured`,
  `token_pack_credited`, `gumroad.py:72-76`).

DTO: `backend/src/schemas/gumroad.py`.

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
