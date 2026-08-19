# domain/creek_vault — the vault seam

`backend/src/domain/creek_vault.py` (283 lines). The vocabulary and value
types adepthood uses to talk to an optional Creek Vault
confidential-compute enclave — "and *nothing else*: no FastAPI, no
SQLModel/DB, no `httpx`" (`creek_vault.py:1-9`). The transport lives
behind an injected `CreekVaultClient` protocol so the concrete adapter
(`services.creek_vault_client`) can be swapped, faked, or absent.

The governing principle is **graceful degradation**: "no feature
adepthood ships today depends on a vault being present"
(`creek_vault.py:11-14`). Two invariants are load-bearing
(`backend/src/domain/creek_vault.py:16-24`):

```text
* **Fail closed on tier.** :func:`tier_ceiling_for` raises rather than defaulting
  to :attr:`VaultTierCeiling.OPEN` for an unknown classification. Silently
  widening a tier would let sensitive content leave under a looser ceiling than
  the writer chose -- the opposite of "you choose your depth."
* **Privacy over debuggability.** The error hierarchy exists so the service layer
  can normalize any transport failure to :class:`CreekVaultUnavailableError`
  *without* echoing the entry body or an API key into the message.
```

The authoritative wire contract is **Creek's own published `/v1` bundle**
(`docs/contracts/adepthood-v1/` in the Creek-Vault repo), which adepthood
vendors byte-for-byte under `backend/tests/fixtures/creek_v1/`. The
adepthood-side document `docs/creek-vault-mcp-contract.md` was reduced to
a pointer to it, plus the material Creek does not own — the tier-name
mapping and the Wheel projection. Its filename still says `mcp` purely
for link stability; nothing about the transport is implied by it.
`CONTRACT_VERSION = "0.2.0"` (`creek_vault.py:49`).

!!! note "Corrected 2026-08-19"

    This page previously reported `CONTRACT_VERSION = "0.1.0-draft"` and
    `CONSUMER_ID = "CREEK_MCP_CONSUMER"`. Both are gone from the code.
    The draft version string was retired by adepthood's ADR 0004
    (Decision 3), which requires it never reappear in the contract doc,
    and `CONSUMER_ID` was deleted with the MCP client — it never carried
    any tenancy meaning, and the real per-deployment binding that
    replaced it is `CREEK_VAULT_OWNER_USER_ID` (ADR 0004 Decision 7).

## Capabilities and tiers

`CreekCapability` — adepthood's own names for the capabilities a vault
may advertise: `creek.handshake`, `creek.journal`, `creek.upload`,
`creek.save`, `creek.classify`, `creek.reflect`, `creek.wheel`;
"adepthood must never assume a capability exists without first seeing
it" in the handshake (`creek_vault.py:52-69`). These are telemetry and
error keys rather than wire names — over `/v1` the same four live
capabilities are spelled `capabilities`, `journal-upsert`,
`reflections` and `wheel`, and `services/creek_vault_client.py`
translates between the two.

`VaultTierCeiling` — `open` / `personal` / `intimate`; `OPEN` is Creek's
word for what adepthood calls `PUBLIC` (`creek_vault.py:65-76`). The
mapping is keyed by raw `JournalClassification` *strings* so the module
stays DB-free, with a drift-guard test asserting the key sets match
(`creek_vault.py:79-88`). `tier_ceiling_for(classification)` fails
closed: `ValueError` on unknown input — "the safe answer to 'I don't
know this tier' is to refuse the call, not to widen it"
(`creek_vault.py:91-103`).

## Errors

- `CreekVaultError(RuntimeError)` — one vault-agnostic catch type; "an
  unrelated internal bug propagates unchanged so the real defect is not
  masked" (`creek_vault.py:106-112`).
- `CreekVaultUnavailableError` — transport failure; message deliberately
  static, never interpolating the entry body or an API key
  (`creek_vault.py:115-122`).
- `CreekCapabilityUnsupportedError` — the handshake did not advertise
  the capability (or no vault is configured — the local-fallback client
  raises it for every read/compute capability). "Degradation is
  per-capability, not all-or-nothing" (`creek_vault.py:125-134`).

## Value types

| Type | Shape | Notes |
| --- | --- | --- |
| `HandshakeResult` | `available`, `contract_version`, `ontology_version`, `capabilities: frozenset`, `attestation` | Frozen so a cached handshake can't be mutated under later reads; `HandshakeResult.unavailable()` is the single canonical "no usable vault" value every degradation path collapses to (`creek_vault.py:137-169`) |
| `VaultIngestRequest` | `entry_id`, `body`, `tier`, `tier_ceiling`, `created_at` | `entry_id` keys the stored fragment, so re-sending is idempotent and edits in place; for a journal entry `tier == tier_ceiling`, so Creek "stores at exactly that tier and refuses any widening (it never downgrades)" (`creek_vault.py:172-190`) |
| `VaultIngestResult` | `stored`, `vault_ref` | `stored=False` with `vault_ref=None` on the local-fallback path — a no-op, not an error (`creek_vault.py:193-204`) |
| `VaultClassification` | `tags: tuple[str, ...]` | Frequency/Wavelength-phase tags (`creek_vault.py:207-211`) |
| `VaultWheelAspect` / `VaultWheelBalance` | per-Aspect fullness rows | Domain-native mirror of the transport payload; the adapter owns the Pydantic parse (`creek_vault.py:214-238`) |

## `CreekVaultClient` protocol (`creek_vault.py:241-283`)

`handshake()` (never raises — incompatible/absent vaults yield
`unavailable()`), `is_available()`, `supports(capability)`,
`ingest(request)`, `classify(body, tier_ceiling)`,
`reflect(body, tier_ceiling)` (a Higher Self reflection grounded in the
corpus), and `wheel()`. `wheel` is the one capability whose *field-level*
parse errors are **not** normalized to unavailable — the consumer owns
field validation, and a caller that cannot obtain the wheel "falls back
to computing the balance locally" (`creek_vault.py:275-283`; the local
computation is [domain/wheel](wheel.md)).

Persistence linkage: a successful ingest writes
`JournalEntry.vault_ref` / `vault_tags`
(`backend/src/models/journal_entry.py:224-232`); corpus-theme
invitations consume `wheel()` readings
([domain/invitations](invitations.md)). See also ADR
[0012 — local-first privacy tiers](../../../decisions/0012-local-first-privacy-tiers.md).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
