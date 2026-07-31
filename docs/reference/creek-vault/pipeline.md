# Creek-Vault — pipeline and core algorithms

The four most load-bearing mechanisms in `creek-tools`: deterministic
fragment identity, the pipeline stage machine, the privacy/consent model,
and the right-to-be-forgotten purge.

## 1. Deterministic fragment identity

Every atomic unit in the vault is a *fragment* whose ID is a content hash,
making all re-processing idempotent
(`creek/ingest/base.py:329-345`):

```python
def generate_fragment_id(source: str, timestamp: datetime, content: str) -> str:
    hash_input = f"{source}:{timestamp.isoformat()}:{content}"
    digest = hashlib.sha256(hash_input.encode()).hexdigest()[:12]
    return f"frag-{digest}"
```

Worked example: re-ingesting the same Claude export twice computes the same
`frag-XXXXXXXXXXXX` for every message, so the second run is a no-op — the
property the README states as "Deterministic. Fragment IDs are hashed from
`(source, timestamp, content)` so re-processing is idempotent."

Child fragments (from the FEAT-020/021/022 splitter/aggregator) hash
`(parent_id, level, index)` instead of content — deliberately, because
"content-keyed IDs would change every time a trivial whitespace edit landed
upstream and explode the resonance graph"
(`creek/ingest/base.py:348-383`). The same shape (`frag-` + 12 hex chars)
means "child IDs are indistinguishable from root IDs downstream and the same
dedup, indexing, and resonance code paths work for both" (`:355-359`).

## 2. The pipeline stage machine

`Pipeline.run(source_path, vault_path)` executes the fixed stage order
documented in its own docstring (`creek/pipeline.py:285-308`):

```text
0. Consent check (if consent_manager configured)
1. Redaction scan on source files
2. Ingestion (discover ingestors for source type)
3. Classification (rule -> LLM -> review queue)
4. Vault write (persist classified fragments + bodies)
5. Linking (embeddings, temporal, threads, eddies)
6. Index generation
7. Pre-LLM yield summary (FEAT-005)
```

Two behaviors are worth quoting exactly:

- **Consent short-circuits ingestion, not observability.** "If … no prior
  consent exists for the source, ingestion and all downstream stages are
  skipped. Redaction scanning and index generation still run regardless"
  (`creek/pipeline.py:288-291`, implemented at `:310-325`).
- **The yield summary always emits**, "even on consent-skipped runs the
  audit report wants a row" — and a failure to write it "must NOT abort the
  pipeline — the audit substrate is observability, not a precondition for
  the run" (`creek/pipeline.py:348-351`, `:360-366`).

Classification is tiered by cost: deterministic rules first, then the local
model (Ollama), with an LLM "residue" counted per run
(`PreLLMYieldSummary` fields `deterministic_classified`,
`local_model_processed`, `residue`, `no_llm` —
`creek/pipeline.py:372-377`). "Local-first by default. Classification runs
on Ollama; embeddings on `sentence-transformers`. The Anthropic API path is
opt-in" (`README.md`, Key capabilities; the provider split is ADR-0003,
`docs/architecture/ADR/0003-decoupled-provider-abstractions.md`, and
local-only embeddings are ADR-0004).

## 3. Privacy tiers and the two consent surfaces

The privacy model has two independent gates, per `README.md` (Key
capabilities): *ingestion* consent (first-run per source, prompt logged to
`00-Creek-Meta/Processing-Log/consent-log.json`) and *downstream* tier
filtering — "generation, mining, drafts, MCP queries … filter or refuse
fragments by tier independently."

Tier semantics in code (`creek/models.py:329-346`): `open` — "openly
publishable, not internet-public" (naming fixed in INC-003); `personal`;
`intimate` — "reserved exclusively for self-authored fragments". Two
downstream rules follow from the tier:

- **Unclassified is not open.** For admission decisions an explicit
  `unclassified` tier "ranks with `personal` (#961), so only a `personal`
  ceiling or broader admits it" (`creek_mcp/tier_ceiling.py:10-16`).
- **Intimate never goes to a cloud model.** Every LLM call derives a
  routing tier "so `creek.classify.llm.router.ModelRouter` applies the
  `Intimate`-never-cloud gate (#928)" (`creek_mcp/tier_ceiling.py:16-21`).

Overrides that widen visibility (`--include-tier`) are themselves recorded
in hash-chained audit logs (`creek/cli.py:87-113`;
`creek/classify/privacy_filter.py` provides `record_privacy_override`).

## 4. Right-to-be-forgotten: the purge engine

`PurgeEngine` (`creek/purge/engine.py:221-`) implements scoped deletion —
`purge_fragment`, `purge_source`, `purge_source_path`,
`purge_classifications`, `purge_daterange`, `purge_vault(confirmation)` —
with `dry_run` support (`:234`) and a vault-marker check so it cannot run
against a non-vault directory (`_require_vault_marker`, `:545`).

What "scrub every reference" means, per `README.md` (Key capabilities),
each backed by engine internals:

1. Wiki-links by title across every `.md` file in the vault.
2. Word-boundary fragment-ID mentions in YAML provenance lists
   (`source_fragments:` in drafts) and prose bodies.
3. Matching rows in `00-Creek-Meta/embeddings.parquet`
   (`_purge_cache_for`, `creek/purge/engine.py:571`; a vault purge deletes
   the cache file outright, `_delete_cache_file`, `:597`).
4. When the deleted note is an intimate-tier save, the full-body stub under
   `10-Liminal/Compost/intimate-stubs/` is deleted too
   (`_purge_intimate_stub`, `creek/purge/engine.py:708`), "so a scoped
   purge no longer leaves the intimate body on disk."
5. "The hash-chained purge audit log is the only artifact retained for
   compliance reconstruction."

The CLI wraps these as the five `creek purge …` commands (see
[CLI surface](creek-cli.md)); the MCP surface re-exposes them behind
elevated auth (see [MCP server](mcp-server.md)).

## Supporting decisions (ADRs)

`creek-tools/docs/architecture/ADR/` records the decisions the code above
encodes: 0001 single source of truth for quality gates; 0002 MIME
verification library; 0003 decoupled provider abstractions; 0004 embeddings
stay local; 0005 confidential volume key, no escrow; 0006 enclave
attestation trust model; 0007 confidential per-user hosting.

---

*Grounded in creek-vault@85d230b, 2026-07-31.*
