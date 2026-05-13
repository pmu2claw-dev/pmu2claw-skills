---
name: tim2tenji-backend-feature-slice
description: Extend TIM2TENJI with one new backend feature slice across domain/service/API/MCP layers using tests as the contract and verifying with targeted unittest suites.
---

# When to use
Use this when adding a new TIM2TENJI capability that must be reachable consistently from:
- domain/helper module(s)
- `tim2tenji/service.py`
- `tim2tenji/api.py`
- `tim2tenji/mcp_server.py`
- corresponding `tests/test_*.py`

Typical triggers:
- adding a new parsed artifact or generated artifact
- exposing a repository method through API and MCP
- making project detail / health metadata reflect the new capability
- a feature exists in one layer but not the others

# Goal
Add one minimal end-to-end backend feature slice without large refactors, keep service/API/MCP contracts aligned, and prove it with focused tests before moving on.

# Core approach
Treat the tests as the contract, then wire the implementation through the repository first, and expose that same repository method through API and MCP so the interface does not fork.

When choosing the *first* TIM2TENJI backend slice for an alpha/private-preview codebase, prefer a "surface what already exists" slice over a speculative new capability. A good first cut is often making an already-persisted project artifact visible through `get_project` consistently across service/API/MCP.

# Recommended workflow
1. Read the implementation entry points and the relevant tests first.
   - `tim2tenji/service.py`
   - `tim2tenji/api.py`
   - `tim2tenji/mcp_server.py`
   - targeted tests such as `tests/test_service.py`, `tests/test_api.py`, `tests/test_mcp_server.py`, plus any domain-specific test file
2. Identify the single canonical repository method to add in `ProjectRepository`.
   - Example pattern: `generate_mapping_draft(slug, filename)`
3. If the feature has its own domain logic, keep it in a dedicated module instead of bloating `service.py`.
   - Example: `tim2tenji/draft_generation.py`
4. Add/adjust service-layer dataclasses so API and MCP can serialize the same structure.
5. Expose the repository method through API.
   - Add a dedicated request model if needed.
   - Return `asdict(...)` of the service/dataclass object.
   - Normalize expected error mapping, typically `FileNotFoundError -> 404`, `ValueError -> 400`.
6. Expose the same repository method through MCP.
   - Register an actual MCP tool function, not just health metadata or server description text.
   - If health/instructions enumerate capabilities or limitations, update them too.
- If the feature is reported as "stuck" or "almost done," prove where the slice actually stops before coding.
- Search `service.py`, `api.py`, `mcp_server.py`, and `tests/test_*.py` for the feature name and its expected artifact/tool/route names.
- Check MCP `instructions` / `health()` metadata for explicit capability or limitation strings; these often reveal the real supported boundary.
- Inspect recent git history to see the last completed feature slice, so you do not mistake a T3 draft feature for a T4 export feature.
- Re-read product-facing docs such as `README.md`, `docs/MVP_PLAN.md`, `docs/AI_TOOL_PACKAGING.md`, `docs/DOMAIN_MODEL.md`, and `docs/ARCHITECTURE.md` to confirm the alpha boundary before choosing the slice. If export/rule-engine/review workflows are explicitly deferred there, do not start with them.
8. For project-detail improvements, compare `workspace.py` directory conventions against the public contract.
   - If a read-time artifact metadata slice is already done (`get_project` exposes `{artifact_type, path, source_filename, created_at}`), a strong next slice is to make the generator-written artifact JSON carry the same traceability metadata instead of relying only on read-time fallback.
   - Drive that slice with service-layer failing tests that open the persisted JSON files under `artifacts/parsed-workbooks/*.json` and `artifacts/mapping-drafts/*.json`, then assert `source_filename` and `created_at` on the saved payload itself — not just on `get_project()` responses.
   - Keep the implementation minimal by routing generator writes through one helper such as `_artifact_payload(payload)` that preserves existing fields and `setdefault("created_at", self._now_iso())` before `_write_json(...)`.

- Favor a minimal dataclass-backed record such as `{artifact_type, path}` before inventing richer metadata contracts.
- If you need one small metadata follow-up slice after `{artifact_type, path}`, prefer traceability fields that already exist or can be derived cheaply: `{source_filename, created_at}`.
- A practical pattern for that metadata slice is:
  - `source_filename`: read `source_filename` from the artifact JSON when present; otherwise fall back to the artifact filename with the trailing `.json` removed.
  - `created_at`: derive from the artifact file's mtime and serialize as a UTC ISO timestamp.
- Prefer project-relative POSIX paths over absolute filesystem paths.
- If current generated artifacts are JSON-only, it is reasonable to start with `artifacts/**/*.json` instead of broad file scanning.
- A practical type heuristic is deriving `artifact_type` from the first directory below `artifacts/`, singularizing simple plurals like `parsed-workbooks -> parsed-workbook` and `mapping-drafts -> mapping-draft`.
- If the new contract field must appear in live generator responses (not just persisted artifact JSON), propagate it through every dataclass boundary instead of relying on `_artifact_payload(...)` alone. In practice for the parser→draft generator→service path this means updating upstream domain objects such as `ParsedWorkbook` and `WorkbookMappingDraft`, then the service-facing record such as `MappingDraftRecord`, so `asdict(...)` in API and MCP naturally includes the field.
9. Update tests to expect the new tool/route/record behavior.
   - For metadata slices that reach the web UI, add a JS render test that asserts the new artifact fields are HTML-escaped before wiring the UI.

   - Good pattern:
     - `python -m unittest tests.test_draft_generation tests.test_service tests.test_api tests.test_mcp_server -v`
10. Only after those pass should you move on to export/UI work.

# Proven implementation pattern
## Service layer
- Import the dedicated domain helper into `service.py`.
- Add a repository method that:
  - resolves the project and source file
  - validates file type / existence
  - reuses existing parser/domain objects when possible
  - builds the new artifact
  - persists the artifact under the project `artifacts/` tree with a filename that preserves the original source filename
  - returns a dataclass record usable by both API and MCP

## API layer
- Add a minimal request model, usually just the source filename for generation steps.
- Add a dedicated route rather than overloading an unrelated parse/upload endpoint.
- Serialize via `asdict()` so tests can assert stable JSON.

## MCP layer
- Keep tool behavior thin: call repository, return serialized dataclass.
- If `--print-tools` is tested, ensure the new tool is actually registered in `create_mcp_server()`.
- Update health/instructions only as secondary metadata; they do not replace tool registration.

# Pitfalls
- Updating persistence helpers so saved artifact JSON gets a new field, but forgetting that API/MCP responses are serialized from upstream dataclasses; the response contract will still miss the field until those dataclasses are updated too.
- In `tests/test_mcp_server.py`, regex assertions over JSON snippets should use raw strings (for example `r'"created_at": "[^\"]+\+00:00"'`) to avoid invalid escape warnings while still matching the serialized payload.
- Updating `tests/test_mcp_server.py` to expect a tool name without actually registering the tool in `mcp_server.py`.
- Updating MCP health capabilities but forgetting the callable MCP tool.
- Letting API, MCP, and service each invent slightly different response shapes.
- Skipping a re-read after patching `mcp_server.py`; small patch edits can break dict/indent structure.
- Moving too quickly to export/UI before targeted backend tests are green.

# Verification checklist
Before calling the feature slice done, verify all of these:
- domain-specific tests pass
- service tests pass
- API tests pass
- MCP tests pass
- `--print-tools` includes the new MCP tool when applicable
- persisted artifact path exists under the project `artifacts/` tree
- API and MCP both return the same dataclass-backed shape

# Notes specific to TIM2TENJI
- Prefer minimal viable end-to-end progress over broad architectural resets.
- When a feature starts as a new artifact type, preserve original filenames in persisted artifact naming.
- For continuing work, finish backend contract alignment first, then move to export flow, then one-click UI/API/MCP wiring, then full verification.
