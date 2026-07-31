# Architecture

System-level structure of each Adepthood repo and the connections between
them: components, service boundaries, data flow, storage schemas, and
deployment topology.

## Inclusion criteria

File a page (or update an existing one) here when a merged PR:

- Adds, removes, or replaces a major component (a service, app, package,
  database, queue, or external integration).
- Changes a service or module boundary — what talks to what, or which layer
  owns a responsibility.
- Changes a storage schema, migration strategy, or data model in a way that
  affects more than one module.
- Changes deployment topology, hosting, or the runtime environment
  (new platform, new build target, new infrastructure dependency).
- Introduces or rewires a cross-repo integration (one repo consuming
  another's artifacts, APIs, or data).

Do **not** file here for: single-function refactors, UI-only changes
(see [Design](../design/index.md)), or choices between alternatives —
record those as ADRs in [Decisions](../decisions/index.md) and link the
resulting structure from a page here.

## Conventions

- One page per system or per cross-cutting concern, named
  `<repo-or-concern>.md` (for example `adepthood-backend.md`,
  `cross-repo-sync.md`).
- Open each page with a short "as of" line referencing the most recent PR
  folded into it.
