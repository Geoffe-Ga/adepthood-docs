# API — botmason (wallet) router

`backend/src/routers/botmason.py` (107 lines).
`APIRouter(tags=["botmason"])` — **no prefix**; paths mount at `/user/*`
(`botmason.py:38`). Every user gets `BOTMASON_MONTHLY_CAP` free message
credits per calendar month; once spent, requests fall through to
`offering_balance` (purchased/gifted credits, no expiry). "The
conversational chat endpoints were retired in favour of journal resonance
— this router now only exposes the wallet surface … that resonance and
its sibling features charge against" (`botmason.py:1-8`).

| Method | Path | Rate limit | Auth | Request DTO | Response | Success | Errors |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GET | `/user/balance` | — | JWT | — | `BalanceResponse` | 200 | — |
| GET | `/user/usage` | — | JWT | — | `UsageResponse` | 200 | — |
| POST | `/user/balance/add` | 5/minute | **admin** (`require_admin`) | `BalanceAddRequest` | `BalanceAddResponse` | 200 | 401 (no/invalid JWT), 403 `admin_required` (non-admin), 403 `user_not_found` (TOCTOU: admin row deleted mid-request) |

Notes:

- `/user/usage` computes the monthly rollover **without committing**
  (BUG-BM-015): "a GET must not mutate persistent state. The UPDATE runs
  inside the session so the response reflects the post-reset values" and
  the rollover UPDATE is idempotent (`botmason.py:51-74`). Response
  fields: `monthly_messages_used`, `monthly_messages_remaining`
  (clamped at 0), `monthly_cap`, `monthly_reset_date`,
  `offering_balance` (`botmason.py:68-74`).
- `/user/balance/add` credits the **calling admin's own** wallet through
  `services.wallet.add_balance` with `actor_user_id=admin.id`, then
  commits and logs `balance_added` (`botmason.py:77-107`). Every wallet
  mutation lands a `WalletAudit` row — see
  [data-model/commerce-wallet](../data-model/commerce-wallet.md).
- DTOs in `backend/src/schemas/botmason.py`; admin gating in
  `backend/src/dependencies/auth.py:39-51`.

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
