# Auth

`frontend/src/features/Auth/` — the pre-auth screens mounted by
`AuthNavigator` while `authStatus === 'anonymous'`, plus the `ReauthSheet`
overlay shown in `'reauth-required'` (`frontend/src/App.tsx:113-127,184-189`).
The session state machine itself lives in
`frontend/src/context/AuthContext.tsx` (see
[Navigation — auth gate](../navigation.md#auth-gate-rootnavigator) and
[ADR 0004](../../../decisions/0004-jwt-auth.md)).

## Screens

| Screen | Route | Responsibility |
| --- | --- | --- |
| `GetStartedScreen` | `GetStarted` | pre-auth landing; its buy CTA opens `GUMROAD_PRODUCT_URL` (`frontend/src/config.ts:64-69`) |
| `LoginScreen` | `Login` | email/password login via `useAuth().login` |
| `SignupScreen` | `Signup` | signup with the **required** Gumroad license key — the `Signup` action type takes it as a required third argument so "the paid-content gate is only real if the type system refuses a call that forgets it" (`AuthContext.tsx:35-40`); route param `licenseKey` seeds the form (`App.tsx:47-49`) |
| `ForgotPasswordScreen` | `ForgotPassword` | `auth.requestPasswordReset` — always-202 anti-enumeration |
| `ResetPasswordScreen` | `ResetPassword` | trades the emailed token via `confirmPasswordReset` (`AuthContext.tsx:631-640`) |
| `CancelResetScreen` | `CancelReset` | the "this wasn't me" landing (`auth.cancelPasswordReset`) |
| `ReauthSheet` | (overlay, not a route) | in-place re-authentication that keeps RootStack mounted (BUG-NAV-001, `App.tsx:184-189`) |

Shared building blocks: `AuthScreenContainer`, `AuthBrandBand`,
`SocialAuthButtons`, the `components/` fields (`EmailField`,
`PasswordField`, `LicenseKeyField`), and `auth.styles.ts`.

## Hooks and helpers

- **`useAuthSubmit(fn, { fallback })`** — the shared submit state machine
  every auth form uses: one `error`/`submitting` pair, failures mapped
  through `formatApiError`, a stable-identity `run` with an in-flight guard
  so a double submit is a no-op
  (`frontend/src/features/Auth/useAuthSubmit.ts:6-58`).
- **`useSignupForm`**, **`passwordValidation.ts`**,
  **`licenseKeyValidation.ts`**, **`canonicalizeEmail.ts`**,
  **`signupErrorRouting.ts`** — form state and validation helpers.
- **Social sign-in**: `useGoogleAuth` / `useAppleAuth` obtain provider ID
  tokens (config in `oauthConfig.ts`), `socialFlow.ts` sequences the
  exchange. The context exchange returns a `SocialSignInResult` value union
  — `success | needs_license | error` — instead of throwing, because
  `needs_license` is a normal branch that opens the inline license step
  (`AuthContext.tsx:67-92,474-499`). Only the collapsed
  `409 needs_license` refusal routes there; any other 409 is a plain error
  so the user isn't stranded re-entering a key that was never the problem
  (`AuthContext.tsx:483-499`).
- **`resetToken.ts`** — parses the recovery deep-link token.

## Session-machine behaviors this module leans on

- Signup attaches the device IANA timezone and converts the backend's
  `user_id == 0` duplicate-email sentinel into a client-side
  `ApiError(409, 'email_in_use')` (`AuthContext.tsx:438-472`).
- Apple's `full_name` is a one-shot gift: it rides every leg of the flow
  including the license retry, "because that retry is the request that
  creates the account — and Apple will never offer the name again"
  (`AuthContext.tsx:531-559`).
- Persistence-first ordering (BUG-AUTH-005): `applyAuthResponse` awaits
  `saveToken` before mutating React state, shared by login / signup /
  password-reset (`AuthContext.tsx:414-436`).
- Logout and the sheet's "sign out instead" both run `tearDownSession`,
  which clears the token (arming a retry marker if the delete fails), wipes
  every store and per-user storage key, and lands `'anonymous'`
  (BUG-FE-STATE-001, `AuthContext.tsx:580-596`).

Stores: `useWelcomeStore` (the Welcome gate reads first-run state around
these screens). API: the `auth` namespace only.

*Grounded in adepthood@55eef11, 2026-07-31.*
