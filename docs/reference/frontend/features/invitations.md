# Invitations

`frontend/src/features/Invitations/` (4 files: `InvitationStack.tsx`,
`InvitationNote.tsx`, `invitationCopy.ts`, `useInvitations.ts`) — the
subtle invitation surface of NORTH-STAR §6: resonant, declinable
invitations toward deeper rings, never gamified pressure.

## Surface

`InvitationStack` renders on the Journal shelf
(`frontend/src/features/Journal/JournalShelfScreen.tsx:38`); each
`InvitationNote` presents one invitation with copy keyed by
`invitationCopy.ts` from the `(target_type, kind)` pair — target types
`habit | practice | course | sangha | embodied_community`, kinds
`readiness | consistency | mastery`
(`frontend/src/api/schemas.ts:539-546`).

## `useInvitations`

The hook "loads the pending invitation surface on mount and decays it one
tap at a time" (`useInvitations.ts:1-9`):

- **Silent by default** — an empty list is the common, un-nagging case, and
  a failed load stays silent: "invitations must never nag or crash the tab"
  (`useInvitations.ts:38-51`).
- **Optimistic dismiss with revert**: the row is removed immediately,
  `invitations.dismiss` (idempotent, deterministic key
  `dismiss-invitation:{id}`) confirms, and the snapshot is restored on
  error. A per-id in-flight guard stops double-taps; an unmount guard drops
  late resolutions (`useInvitations.ts:53-66`,
  `frontend/src/api/index.ts:1686-1692`).
- Committed state is mirrored into a ref so the revert branch can snapshot
  synchronously even when the API rejects immediately
  (`useInvitations.ts:30-36`).

## Stores and API

No store usage. API: the `invitations` namespace only (bare-array list +
dismiss).

*Grounded in adepthood@55eef11, 2026-07-31.*
