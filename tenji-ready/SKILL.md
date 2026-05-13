---
name: tenji-ready
description: Supply reusable TENJI-ready test fields, Excel mappings, and protocol-specific output patterns. Use when the user asks for ready-to-fill test fields, Tenji column mappings, protocol test templates, example rows, or protocol-to-TENJI conversion patterns for PD, PPS, QC, AFC, FCP, UFCS, BC1.2, Apple, Type-C current, PE, or VOOC.
---

# Tenji Ready

Use this skill when the user needs output that is already close to workbook-ready format.

## Core workflow

1. Determine whether the user needs:
   - test fields
   - excel mapping
   - case pattern / example
   - coverage lookup
2. Read only the matching reference file.
3. Preserve protocol-specific semantics. Do not flatten them into generic placeholders.
4. If the request starts from a spec or event chain rather than a mapping, first use `tenji-workflow` and optionally `protocol-knowledge`.

## Reference map

### Test fields
- `references/test-fields/PD-test-fields.md`
- `references/test-fields/PPS-test-fields.md`
- `references/test-fields/BC12-test-fields.md`
- `references/test-fields/AFC-test-fields.md`
- `references/test-fields/FCP-test-fields.md`
- `references/test-fields/UFCS-test-fields.md`
- `references/test-fields/Apple-test-fields.md`
- `references/test-fields/TypeC-Current-test-fields.md`
- `references/test-fields/PE-test-fields.md`
- `references/test-fields/VOOC-test-fields.md`

### Excel mapping
- `references/excel-mapping/PD-excel-mapping.md`
- `references/excel-mapping/PPS-excel-mapping.md`
- `references/excel-mapping/BC12-excel-mapping.md`
- `references/excel-mapping/AFC-excel-mapping.md`
- `references/excel-mapping/FCP-excel-mapping.md`
- `references/excel-mapping/UFCS-excel-mapping.md`
- `references/excel-mapping/Apple-excel-mapping.md`
- `references/excel-mapping/TypeC-Current-excel-mapping.md`
- `references/excel-mapping/PE-excel-mapping.md`
- `references/excel-mapping/VOOC-excel-mapping.md`
- `references/excel-mapping/QC-excel-mapping.md`

### Indexes
- `references/indexes/STATUS-MATRIX.md`
- `references/indexes/INDEX.md`
- `references/indexes/README.md`

## Working rules

- Prefer protocol-specific mappings over generic templates.
- If the workbook row wording implies hidden previous state, call it out before reusing it.
- Keep test-item split logical: pre-state establish, request, transition, verify, fallback.
- When the user asks for JD-style case analysis, extract the event chain first and then map.
