---
name: tim2tenji-project-detail-ui-slice
description: Add one minimal TIM2TENJI project-detail UI slice by exposing an already-existing backend field in the static app, proving it first with JS render tests and then a browser smoke check.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# When to use
Use this when TIM2TENJI already exposes project-detail data from `get_project` in the backend, but the web app still does not show it in the project detail view.

Typical examples:
- generated artifacts already returned by API but not rendered in UI
- new conversation/session/project metadata field exists in API payload but is invisible in the app
- project detail needs one more read-only panel without changing core backend behavior

# Goal
Ship one small, honest UI slice that makes an existing project-detail capability visible in the app without drifting away from backend contracts.

# Core approach
Treat this as a thin vertical slice across:
- `tim2tenji/static/index.html`
- `tim2tenji/static/app.js`
- `tim2tenji/static/render.js`
- `tests/js/render.test.mjs`

Do not invent new frontend-only data shapes. Reuse the backend payload as-is.

# Recommended workflow
1. Inspect the current UI entry points.
   - Read `tim2tenji/static/index.html`
   - Read `tim2tenji/static/app.js`
   - Read `tim2tenji/static/render.js`
   - Read `tests/js/render.test.mjs`
2. Confirm the backend field already exists in `GET /api/projects/{slug}`.
   - If the backend contract is not there yet, stop and finish the backend slice first.
3. Add a failing JS render test first.
   - Preferred pattern: add or import a dedicated render helper such as `artifactMarkup()`.
   - Test escaping, not just happy-path markup, because this UI uses `innerHTML`.
4. Run the JS test alone and verify RED.
   - Example:
     - `node --test tests/js/render.test.mjs`
   - A useful expected failure is: requested export does not exist yet.
5. Add the minimal implementation.
   - In `render.js`, add one small helper that renders the new record shape.
   - In `app.js`, import that helper and extend `renderProjectDetail(detail)`.
   - In `index.html`, add a new panel and empty-state container.
6. Keep the UI contract minimal.
   - Show existing backend fields directly.
   - For artifacts, a good first cut is:
     - `artifact_type`
     - `path`
7. Re-run the JS tests until green.
8. Run the Python suite to catch accidental regressions from touched app packaging or imports.
   - Example:
     - `python -m unittest discover -s tests -p 'test_*.py'`
9. Start the app and do a browser smoke check against `/`.
   - Example serve command:
     - `python -m tim2tenji.cli serve --host 127.0.0.1 --port 8765`
   - Verify the new panel heading and empty state are visible when no data exists.
10. Record the git working tree so the UI files are easy to review separately from existing dirty docs.

# Proven pattern for generated artifacts
When backend `get_project` already returns:
```json
{
  "artifacts": [
    {"artifact_type": "parsed-workbook", "path": "artifacts/parsed-workbooks/foo.json"}
  ]
}
```
use this shape directly in the UI:
- `index.html`: add a `Generated Artifacts` section with `id="artifacts"`
- `app.js`: cache `elements.artifacts`, then render either empty-state text or `detail.artifacts.map(artifactMarkup)`
- `render.js`: implement `artifactMarkup(item)` with escaped `artifact_type` and `path`
- `tests/js/render.test.mjs`: assert dangerous strings are escaped in both fields

# Pitfalls
# Pitfalls
- Updating `app.js` to call a new helper before exporting it from `render.js`
- Adding tests that import a new render helper without actually exporting it from `render.js`; in practice this shows up as an early Node module/import failure before assertions run
- When adding parse-source or mapping-draft result cards, forgetting that nested workbook cells and row fields also flow through `innerHTML`; escape `source_filename`, `file_type`, `created_at`, `mode`, `testcase_reference`, sheet names, cell addresses/values, and row fields in the shared helper
- Adding UI markup without a corresponding DOM lookup in `elements`
- Forgetting empty-state handling, which makes browser smoke checks misleading on blank projects
- Rendering raw API strings into `innerHTML` without escaping
- Treating a backend-missing field as a frontend task; finish backend contract alignment first

# Verification checklist
Before calling the UI slice done, verify all of these:
- new JS test was added first and observed failing
- if the new test imports a helper such as `workbookActionResultMarkup`, confirm the failure is really the missing export/helper and not a different contract mismatch
- `node --test tests/js/render.test.mjs` passes
- `python -m unittest discover -s tests -p 'test_*.py'` passes, because TIM2TENJI also has Python coverage around static rendering/import paths
- browser smoke check shows the new panel heading on `/`
- empty-state text is visible when no records exist
- displayed fields are HTML-escaped in the dedicated render helper, including nested workbook sheets/cells or mapping rows when present

# Notes specific to TIM2TENJI
- Prefer a thin read-only project-detail panel before adding interactive UI workflows.
- This is especially effective right after a backend slice that surfaces persisted project artifacts through `get_project`.
- Keep alpha scope honest: expose existing workspace data; do not imply mother-template export, review workflow, or unresolved-auto-resolution exists when it does not.
