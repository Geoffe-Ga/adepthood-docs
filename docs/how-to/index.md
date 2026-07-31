# How-To

Task-oriented guides: numbered steps a developer or agent follows to
accomplish one concrete goal, verified against the current state of the
repos.

## Inclusion criteria

File a guide (or update an existing one) here when a merged PR:

- Adds or changes a setup procedure (environment bootstrap, credentials,
  local services).
- Adds or changes a recurring operation (running a scan, cutting a release,
  seeding data, building the knowledge graph).
- Changes a command, flag, path, or prerequisite that an existing guide
  mentions — stale steps are bugs; update the guide in the same sync run.
- Introduces tooling that agents must invoke in a specific way.

Do **not** file here for: conceptual explanations (put the concept in
[Architecture](../architecture/index.md) and link it), or policy — that
belongs in [Contributing](../contributing/index.md).

## Conventions

- Name guides as imperatives: `run-the-backend-locally.md`,
  `build-the-knowledge-graph.md`.
- Every guide states its prerequisites first and ends with how to verify
  success.
