# TDD and commit conventions

How change is made and recorded across the ecosystem, as of 2026-07-31.
Sources: adepthood `AGENTS.md` and `CLAUDE.md`; conventions mirrored in the
satellite repos' own `CLAUDE.md`/`CONTRIBUTING.md` files.

## Test-driven development is required

- Write the test first, watch it fail, then implement (red–green–refactor;
  the `stay-green` skill encodes the loop).
- Every bug fix includes a failing test that reproduces the bug before it
  is resolved.
- No untested assumptions: validate changes with tests, by running the app,
  and by checking real backend interactions.
- Work in cycles — test → think → implement → test → refine → repeat until
  all green ("Respect the Archetypal Wavelength", adepthood `AGENTS.md`).

Canonical test shapes:

```python
@pytest.mark.asyncio
async def test_endpoint(async_client: AsyncClient) -> None:
    response = await async_client.post("/endpoint", json={"key": "value"})
    assert response.status_code == 201
```

```typescript
it("does the thing", () => {
  const { getByText } = render(<Component />);
  fireEvent.press(getByText("Button"));
  expect(getByText("Result")).toBeTruthy();
});
```

## Conventional commits, small and atomic

Enforced by commitlint in adepthood's pre-commit; the same style is used
ecosystem-wide, including this docs repo:

```text
feat(backend): add session factory and get_session dependency
test(backend): add integration tests for /health endpoint
fix(frontend): correct habit type mismatch in API response
docs(architecture): fold adepthood#123 energy-domain split into backend page
```

- One logical change per commit; keep PRs reviewable.
- Feature branches always; `main` is protected by hook and by policy.
- PRs state a human-readable summary and confirm the gates passed.

## Code style values

- Write code that teaches; comment intentions more than syntax.
- No magic numbers without named constants.
- Leave TODOs only when actionable and necessary — never for problems
  solvable now.
- Pin GitHub Actions to full commit SHAs with a version comment — never
  mutable tags (adepthood `AGENTS.md`, rule 6; visible in this repo's
  workflows too).
