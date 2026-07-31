# domain/timezone — IANA timezone validation

`backend/src/domain/timezone.py` (55 lines). Shared validation for the
two trust boundaries that accept an inbound IANA timezone name —
`POST /auth/signup` and `PUT /users/me/timezone` — so their rules cannot
drift apart (`timezone.py:1-8`).

| Symbol | Behavior |
| --- | --- |
| `MAX_TIMEZONE_LENGTH = 64` | Cap matching the `User.timezone` column width; IANA names are at most 33 chars today (`America/Argentina/ComodRivadavia`), 64 leaves headroom (`timezone.py:14-16`) |
| `coerce_timezone_input(value) -> str \| None` | `None` for missing / non-string / empty / whitespace-only input (fall back to default); otherwise the trimmed string (`timezone.py:19-29`) |
| `check_timezone_resolves(candidate) -> None` | Raises `ValueError` if over 64 chars or unknown to `zoneinfo` (`timezone.py:32-41`) |
| `normalize_timezone(value, default) -> str` | The composed boundary rule — see below (`timezone.py:44-55`) |

The composed rule (`backend/src/domain/timezone.py:44-55`):

```python
def normalize_timezone(value: object, default: str) -> str:
    """Coerce, default, and validate an inbound timezone value.

    Blank / missing input returns ``default``; otherwise the trimmed name is
    validated and returned, raising ``ValueError`` on an unknown or oversized
    name so the trust boundary surfaces a 422 instead of storing bad data.
    """
    candidate = coerce_timezone_input(value)
    if candidate is None:
        return default
    check_timezone_resolves(candidate)
    return candidate
```

## Worked examples

| Input | `default="UTC"` result |
| --- | --- |
| `None`, `""`, `"   "`, `42` | `"UTC"` |
| `" America/Los_Angeles "` | `"America/Los_Angeles"` |
| `"Mars/Olympus_Mons"` | `ValueError: unknown IANA timezone` → 422 at the boundary |
| 65+ char string | `ValueError: timezone must be 64 chars or fewer` |

The stored zone is then read by [domain/dates](dates.md) for all
local-day math (`backend/src/models/user.py:50-56`).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
