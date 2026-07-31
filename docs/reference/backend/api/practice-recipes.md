# API — practice-recipes router

`backend/src/routers/practice_recipes.py` (394 lines).
`APIRouter(prefix="/practice-recipes", tags=["practice-recipes"])`
(`practice_recipes.py:68`). Library + apply-to-user-practice endpoints
(`practice_recipes.py:1-21`).

| Method | Path | Auth | Request DTO | Response | Success | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| GET | `/practice-recipes/?mode=` | JWT | `PaginationParams`, optional `mode` filter | `Page[PracticeRecipeOut]` or bare list | 200 | — |
| POST | `/practice-recipes/` | JWT | `PracticeRecipeCreate` | `PracticeRecipeOut` | **201** | 409 `recipe_slug_taken`, 400 `recipe_persist_failed` |
| GET | `/practice-recipes/{recipe_id}` | JWT | — | `PracticeRecipeOut` | 200 | 404 `practice_recipe_not_found` |
| PATCH | `/practice-recipes/{recipe_id}` | JWT | `PracticeRecipeUpdate` | `PracticeRecipeOut` | 200 | 404; 403 `cannot_modify_system_recipe`; 400 `recipe_invariant_violated` |
| DELETE | `/practice-recipes/{recipe_id}` | JWT | — | — | **204** | 404; 403 `cannot_modify_system_recipe` |
| POST | `/practice-recipes/{recipe_id}/apply-to/{user_practice_id}` | JWT + owned user-practice | — | `UserPracticeDetail` | 200 | 404 `practice_recipe_not_found` / `user_practice_not_found` / `practice_not_found`; 403; 422 (malformed config); 400 `mode_mismatch` |

Notes:

- **Visibility / mutation** mirror practice-tags: system recipes
  (`owner_user_id IS NULL`) are readable but immutable — mutation is 403
  `cannot_modify_system_recipe`; the client's "edit a system recipe"
  flow *forks* a personal copy via POST with a new slug
  (`practice_recipes.py:7-9,20-21`).
- **Listing is N+1-free** (issue #470): steps are batched into one
  `WHERE recipe_id IN (...)` query, and pagination slices recipe rows
  *before* hydration "so the step lookup stays bounded to the current
  page" (`practice_recipes.py:198-206`).
- **PATCH replaces wholesale**: name + description + rounds + steps;
  slug and mode are immutable ("a slug rename would break any
  UserPractice that captured the recipe by id, and a mode swap would
  invalidate the step tag mappings"). Concurrency is deliberately
  last-write-wins — recipes are personal, so "the conflict surface is
  … vanishingly small" (`practice_recipes.py:270-284`).
- **Delete** cascades step rows only; UserPractice rows are unaffected —
  "the recipe only ever populated their override JSON, never pointed at
  the recipe by FK" (`practice_recipes.py:325-330`).
- **Apply** materialises the recipe into
  `UserPractice.mode_config_override` through *the same* ownership
  dependency and `_validate_mode_config_against_catalog` gate as the
  customise endpoint, "so the override invariant ('mode may not
  change') cannot be bypassed via the recipe path" — identical error
  shapes: 422 structured field errors, 400 `mode_mismatch`
  (`practice_recipes.py:14-18,349-358`).

DTOs: `backend/src/schemas/practice_recipe.py`. Model + constraints:
[data-model/practice](../data-model/practice.md); resolution rule:
[domain/practice-resolution](../domain/practice-resolution.md).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
