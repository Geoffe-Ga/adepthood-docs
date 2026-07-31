# Walkthrough: signing in

Email and password through the login route's lockout and credential
gates, JWT issuance, secure storage on the device, navigator gating, and
the token's whole later life — how every request attaches it, and what
happens when it expires. All paths are repo-relative to
`Geoffe-Ga/adepthood`.

## Login, hop by hop

1. **The submit.** `LoginScreen` canonicalizes the email and calls the
   auth context's `login`
   (`frontend/src/features/Auth/LoginScreen.tsx:100-109`) — the
   canonicalization exists "so the same signup / login pair can't end up
   looking like two distinct accounts"
   (`frontend/src/features/Auth/LoginScreen.tsx:107-109`).

2. **The context action.** `useAuthActions.login` calls
   `authApi.login({ email, password })` and, on success, funnels the
   response through `applyAuthResponse`
   (`frontend/src/context/AuthContext.tsx:599-604`, client object at
   `frontend/src/api/index.ts:2722`). The request body is the
   `AuthRequest` DTO — email plus a length-bounded password
   (`backend/src/routers/auth.py:198-236`); the bounds exist because an
   unbounded field "gives an attacker a free DoS lever (each attempt
   costs ~250 ms server-side)" (BUG-AUTH-017,
   `backend/src/routers/auth.py:201-207`).

3. **The route.** `POST /auth/login` is rate-limited to 5/minute per
   client (`@limiter.limit("5/minute")`,
   `backend/src/routers/auth.py:802-822`). The whole
   check-verify-record sequence runs inside a per-email serialization
   ("concurrent failed attempts cannot all pass the threshold-1 check
   before any of them inserts", BUG-AUTH-007,
   `backend/src/routers/auth.py:811-815`, lock machinery at `434-506`).

4. **Lockout gate.** `_is_account_locked` locks the account when the
   most recent `MAX_FAILED_ATTEMPTS = 5` attempts
   (`backend/src/routers/auth.py:165`) within
   `LOCKOUT_DURATION = timedelta(minutes=15)`
   (`backend/src/routers/auth.py:168`) are all failures
   (`backend/src/routers/auth.py:388-410`).

5. **Credential and state gates.** `_verify_login_or_raise` looks up
   the user, verifies the password with bcrypt
   (`backend/src/routers/auth.py:280-311`), then rejects disabled or
   soft-deleted accounts — and every rejection, including lockout,
   raises the *same* `401 invalid_credentials` "so the caller cannot
   distinguish 'locked' from 'wrong password' from 'disabled'"; the
   state gate deliberately runs after the password check so response
   timing matches an ordinary wrong-password attempt
   (`backend/src/routers/auth.py:769-800`).

6. **JWT issuance.** `_create_token` mints an HS256 JWT
   (`backend/src/routers/auth.py:72-73`) with a 1-hour TTL
   (`_TOKEN_TTL = timedelta(hours=1)`,
   `backend/src/routers/auth.py:78`), a fresh per-token `jti` claim for
   later revocation (BUG-AUTH-013,
   `backend/src/routers/auth.py:313-324`), and a *fractional* `iat` so
   the password-reset gate can order two tokens issued in the same
   second (BUG-AUTH-024, `backend/src/routers/auth.py:327-359`):

    ```python
    payload = {
        "sub": str(user_id),
        "exp": int((now + _TOKEN_TTL).timestamp()),
        "iat": now.timestamp(),
        "jti": jti,
    }
    ```

7. **The response.** `AuthResponse` carries the token, the user id, and
   the server's stored IANA timezone — included precisely so the
   frontend needs no follow-up `GET /users/me` to compute user-local
   streaks (`backend/src/routers/auth.py:264-277`):

    ```json
    { "token": "<jwt>", "user_id": 7, "timezone": "America/Los_Angeles" }
    ```

8. **Persist, then surface.** `applyAuthResponse`
   (`frontend/src/context/AuthContext.tsx:424`) awaits the secure
   write *before* exposing the token to React state (BUG-AUTH-001,
   rationale at `frontend/src/context/AuthContext.tsx:281-284`). The
   token lives in a SecureStore-backed store under the key
   `adepthood_auth_token`
   (`frontend/src/storage/authStorage.ts:16-30`).

9. **Screen gating.** Navigation is chosen by the explicit
   `authStatus` state machine, not by token-null checks
   (`frontend/src/App.tsx:163-187`): `'loading'` renders a splash,
   `'anonymous'` mounts the `AuthStack` (GetStarted / Login / Signup /
   password-reset screens, `frontend/src/App.tsx:111-125`), and
   `'authenticated'` mounts the `RootStack` with the app tabs. The
   fourth state, `'reauth-required'`, keeps RootStack mounted and
   overlays a `ReauthSheet` instead of unmounting the user's screen
   (BUG-NAV-001/002, `frontend/src/App.tsx:130-133` and `187`); the
   state graph is documented at
   `frontend/src/context/AuthContext.tsx:53-56`.

## How later requests carry the token

1. **A getter, not a copy.** The AuthContext registers a stable token
   getter with the API layer (`setTokenGetter`,
   `frontend/src/context/AuthContext.tsx:326-341`), held in a ref that
   outlives the effect so "a mid-request logout ... can't lose the
   reference before the HTTP client reads it"
   (BUG-FRONTEND-INFRA-013,
   `frontend/src/context/AuthContext.tsx:322-333`).

2. **Bearer attach.** Every call through the shared `request` core
   resolves `token ?? tokenGetter?.() ?? null` and sets
   `Authorization: Bearer <token>` when present
   (`frontend/src/api/index.ts:330-347`).

3. **Server-side verification.** `get_current_user` decodes the JWT,
   checks the `jti` against the `revokedtoken` table ("one indexed
   SELECT per request, not a full scan"), and gates on the
   account-state flags so a disabled or deleted user "cannot ride an
   existing token past the deletion / disable boundary"
   (`backend/src/routers/auth.py:999-1025`). Every rejection is an
   identical `401 unauthorized` "to prevent attackers from
   distinguishing token states" (OWASP A07:2021,
   `backend/src/routers/auth.py:1016-1020`).

## Expiry and refresh

1. **A 401 arrives.** For non-`/auth/` paths, the client attempts one
   token refresh and one retry (`retryWithRefresh`,
   `frontend/src/api/index.ts:684-711`; `/auth/` paths own their own
   401 UI, `frontend/src/api/index.ts:715-720`).

2. **One refresh, shared.** Concurrent 401s share a single in-flight
   refresh promise — "N concurrent callers await exactly one network
   refresh" (`frontend/src/api/index.ts:549-560`).

3. **`POST /auth/refresh`.** Rate-limited to 1/minute, the route
   requires a *still-valid* token, revokes the old token's `jti` into
   `revokedtoken` — "a stolen-and-refreshed token cannot be replayed
   until its original `exp`" — and mints a fresh 1-hour token, again
   returning the stored timezone
   (`backend/src/routers/auth.py:1057-1096`). Double-revocation from a
   double-clicked refresh is caught and ignored
   (`backend/src/routers/auth.py:1076-1082`).

4. **Validate before trusting.** The refresh response is Zod-validated
   (`loginAuthResponseSchema.safeParse`) so a malformed `{}` body
   becomes a refresh *failure* rather than a `Bearer undefined` zombie
   session (BUG-API-007/017, `frontend/src/api/index.ts:577-593`).

5. **Guarded apply.** `saveTokenThenApply` writes the new token only
   while the live ref still equals the exact token the refresh was
   issued for, so a stale refresh "can never clobber a fresh login"
   (BUG-FRONTEND-INFRA-012,
   `frontend/src/context/AuthContext.tsx:293-320`).

There is no separate refresh-token credential: refresh exchanges a
live access token for a new one, so a token that fully expires (past
its 1-hour `exp`) cannot be refreshed and the user must re-authenticate.

## Failure modes

- **Wrong password / locked / disabled / deleted** — all collapse to
  `401 invalid_credentials` with matched timing; the specific reason is
  only logged server-side (`backend/src/routers/auth.py:769-800`).
- **Login rate limit** — more than 5 attempts/minute from one client
  is throttled by slowapi before the handler runs
  (`backend/src/routers/auth.py:802-803`).
- **Refresh fails (expired, revoked, malformed body)** — the client
  fires the global unauthorized callback with a *classified* reason:
  `'not_authenticated'` when no token was ever sent (an anonymous call
  to a protected endpoint must not claim "session expired"),
  `'session_expired'` or `'invalid_token'` otherwise (BUG-API-018,
  `frontend/src/api/index.ts:660-703`).
- **Reason-routed UI** — `clearTokenForReauth` maps
  `'not_authenticated'` to the `'anonymous'` navigator and everything
  else to `'reauth-required'`, which overlays the ReauthSheet without
  unmounting RootStack
  (`frontend/src/context/AuthContext.tsx:260-278`).
- **App killed mid-refresh** — the new token is persisted before React
  state sees it, so a crash between response and write cannot strand a
  half-applied session (BUG-AUTH-001,
  `frontend/src/context/AuthContext.tsx:281-299`).
- **Misconfigured server secret** — token mint/verify refuses to run
  with an unset or placeholder `SECRET_KEY`
  (`backend/src/routers/auth.py:171-178`).

*Grounded in Geoffe-Ga/adepthood@55eef11, 2026-07-31.*
