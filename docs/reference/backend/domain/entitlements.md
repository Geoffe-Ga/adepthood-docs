# domain/entitlements — product classification & course access

`backend/src/domain/entitlements.py` (405 lines). Two concerns live
together deliberately: classifying what a Gumroad product id *is* (the
APTITUDE course, or a BotMason token pack and its size), and the
course-access entitlement lifecycle. "One module owning every allowlist
is what keeps the classifications from drifting apart, so a product can
never both grant the course and mint credits by accident. Every allowlist
is read at call time, so a rotation needs no restart, and every one fails
closed: unset means 'matches nothing'" (`entitlements.py:1-11`).

## Reason codes (`entitlements.py:74-86`)

`signup_redemption`, `webhook_sale`, `refund`, `cancellation` (the two
webhook revocations are kept apart so an operator can tell "the buyer got
their money back" from "the subscription simply lapsed"),
`admin_override` (forward-reserved — no manual revocation path exists
yet), `duplicate_signup`, `email_mismatch`. Every grant/revoke logs a
structured line with a reason code and ids only — "never a raw email or
license key" (`entitlements.py:13-16`).

## Environment-driven allowlists

| Variable | Role |
| --- | --- |
| `GUMROAD_APTITUDE_PRODUCT_IDS` | Comma-separated ids that count as "the course"; read at call time (`entitlements.py:88-92,240-247`) |
| `GUMROAD_TOKEN_PACK_PRODUCT_IDS` | Which products are credit packs — the security gate (`entitlements.py:94-105,250-256`) |
| `GUMROAD_TOKEN_PACK_SIZES` | `product_id:count` entries — the money. Kept separate so "an operator can add a product to the allowlist and see it credit nothing until they price it, rather than have a typo in one variable silently mint an unintended amount" (`entitlements.py:94-100`) |

Parsing is defensive throughout: `_split_ids` tolerates padding/blank
entries (`entitlements.py:227-237`); `_is_positive_count` requires plain
ASCII decimal > 0 — `isascii()` rejects fullwidth numerals that
`isdigit()` accepts, and "a non-positive pack size would turn a purchase
into a no-op or, worse, a debit" (`entitlements.py:269-279`);
`_parse_size_entry` drops malformed entries rather than defaulting —
"there is no safe fallback size for real money"
(`entitlements.py:281-294`); duplicate ids resolve right-most
(`entitlements.py:296-306`). `token_pack_size` answers `None` for
unconfigured ids, "which every caller must treat as 'credit nothing'"
(`entitlements.py:308-319`). `is_aptitude_product_id` /
`is_token_pack_product_id` both fail closed on blank/unlisted ids
(`entitlements.py:258-267,321-332`).

## Entitlement lifecycle

- `grant_course_access(session, user, sale=None, *, product_id=None,
  reason_code=REASON_SIGNUP_REDEMPTION)` — **idempotent**: when an
  active grant exists its sale link is updated in place, never a
  duplicate row; provenance (`source_sale_id`, `product_id`) is only
  overwritten by non-`None` derivations "so a bare re-grant cannot erase
  provenance". Commits, then logs `entitlement_granted`
  (`entitlements.py:159-195`).
- `has_course_access(session, user_id)` — an active (`revoked_at IS
  NULL`) `course_access` row exists (`entitlements.py:198-201`).
- `revoke_course_access(session, user_id, reason)` — sets `revoked_at`
  (freeing the partial-unique slot so a later re-grant creates a fresh
  row), commits, logs `entitlement_revoked`; no active grant is a silent
  no-op (`entitlements.py:203-224`).

The at-most-one-active invariant is DB-backed
(`ix_entitlement_user_kind_active`,
[data-model/commerce-wallet](../data-model/commerce-wallet.md)).

## `verify_aptitude_license(email, license_key, *, client=None)`

The signup gate's verifier (`entitlements.py:334-359`). Outcomes
(`LicenseOutcome`, `entitlements.py:112-118`): `VERIFIED` (with the
matched purchase), `INVALID`, `EMAIL_MISMATCH`, `LICENSE_REQUIRED`.

Rules: a blank key short-circuits to `LICENSE_REQUIRED` before any
Gumroad call; otherwise the allowlist is walked in order, stopping at the
first `success` answer. A reversed purchase — refunded, charged back, or
under an unresolved dispute (`disputed and not dispute_won`; a won
dispute leaves the sale legitimate) — folds to `INVALID` **before the
email is compared**, "so the rejection is byte-for-byte identical to an
unknown key and never leaks that the license was once valid"
(`entitlements.py:362-393`). A case-insensitive email match on a live
purchase yields `VERIFIED`; any other holder `EMAIL_MISMATCH`; no match
across the allowlist is `INVALID` (`entitlements.py:395-406`).
`GumroadUnavailableError` propagates untouched so the route can fail
closed (mapped to 503, `entitlements.py:351-354`).

Consumers: [api/auth](../api/auth.md) (signup redemption),
[api/gumroad](../api/gumroad.md) (webhook grant/revoke + token packs),
[api/course](../api/course.md) (access checks).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
