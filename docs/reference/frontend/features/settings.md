# Settings

`frontend/src/features/Settings/` — the Settings hub and its three
sub-screens, all pushed on the RootStack (the tab-header gear opens the hub,
`frontend/src/navigation/BottomTabs.tsx:163-180`).

## Screens

| Screen | Route | Responsibility |
| --- | --- | --- |
| `SettingsHubScreen` | `Settings` | "Warm Settings landing hub (#835). Groups the scattered settings entries — Account (API key, time zone) and Session (log out) — as warm editorial rows"; logout moved off the tab header into the hub's Session group (`SettingsHubScreen.tsx:23-28`). Also hosts `ChooseDepthsSection` and the privacy promise copy — "Entries you mark Intimate are never sent to any AI", exposed as a combined a11y label (`SettingsHubScreen.tsx:33-39`) |
| `ApiKeySettingsScreen` | `ApiKeySettings` | BYOK LLM key management over `useApiKey()` (`frontend/src/context/ApiKeyContext.tsx:44-68`); surfaces `loadError` as a "secure storage unavailable" warning; providers cataloged in `byokProviders.ts`; deep-linkable at `adepthood://api-key-settings` |
| `TimezoneSettingsScreen` | `TimezoneSettings` | `users.updateMyTimezone` then pushes the echoed zone into `AuthContext.setUserTimezone` so user-local helpers update immediately (issue #261, `frontend/src/api/index.ts:2826-2844`, `frontend/src/context/AuthContext.tsx:107-113`) |
| `SupportCareScreen` | `SupportCare` | the human/professional support directory from `careResources.ts` (rendered with `components/care/CareResourceCard`) |

## Choose your depths

`ChooseDepthsSection` is the settings face of graduated engagement
([ADR 0006](../../../decisions/0006-graduated-engagement.md)): it toggles
the four ring flags through `useDepthPreferencesStore.update`, which stores
only the server's echoed full snapshot (non-optimistic — a backend rule may
force a dependent ring off,
`frontend/src/store/useDepthPreferencesStore.ts:14-17,59-67`). Flipping a
ring off removes its tab live and, if focused, redirects to Journal
(`frontend/src/navigation/BottomTabs.tsx:99-140`).

## Shared form scaffolding

`shared/useSettingsForm.ts`, `shared/settingsFormLayout.ts`, and
`shared/SettingsFeedbackBanner.tsx` give the sub-screens one submit/feedback
pattern.

## Stores and API

Stores: `useDepthPreferencesStore`. API: `users` (timezone). The API-key
screen works through `ApiKeyContext` (SecureStore-backed, never uploaded —
`frontend/src/context/ApiKeyContext.tsx:14-24`), and logout calls
`useAuth().logout`.

*Grounded in adepthood@55eef11, 2026-07-31.*
