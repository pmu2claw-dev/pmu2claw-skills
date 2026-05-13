---
name: tenji-sa-plan-intake
description: Inspect an SA test plan Excel workbook read-only (OOXML). Classify sheets by role, identify TENJI-ready sheets, report structure before any conversion.
---

# When to use
User provides SA workbook and wants structure analysis before TENJI conversion.
Triggers: inspect / analyze / SA workbook / 看看 / 結構 / 分析 SA / 哪些頁可以轉

Do NOT rename, rezip, or edit source files.

# Goal
Classify sheets → identify direct-map vs special-case → recommend entry sheet → hand off to automation.

# Quick approach
```python
import zipfile, xml.etree.ElementTree as ET
# Open as zip, read xl/workbook.xml → xl/sharedStrings.xml → worksheet XMLs
# Never use openpyxl (would alter file)
```

Sheet roles:
- `testcase` (headers: No./功能/測試項目/測試方法/預期結果) → direct_map
- `mode_matrix` (headers: 模式/scenario/state) → scenario_expand
- `spec_ec/timing` (headers: parameter/symbol/min/typ/max) → spec_extract
- `pdo_table`, `power_matrix` → spec_extract
- `summary/tracker`, cover/封面/revision → skip

# Automated classification (preferred)
```bash
python3 ~/.openclaw/workspace-tenji/scripts/sheet_classifier.py SA_plan.xlsx
```
Outputs JSON with role, strategy, tenji_ready, recommended_entry_sheet per sheet.

# Supplemental markdown/text shadow view (optional)
When the workbook is large or the user also provided DUT collateral (netlists, PDFs, DOCX, HTML, ZIPs), generate a **secondary semantic view** for search/summarization/cross-document comparison.

Use this only as a helper layer:
- Keep the OOXML sheet/row classifier as the source of truth for workbook structure.
- Treat markdown/text extraction as a shadow view for keyword search, semantic linking, and evidence gathering.
- Never let markdown flattening override merged-cell/layout semantics or workbook-level truth.

Good use cases:
- fast full-workbook keyword search across many sheets
- linking test-plan terms to DUT netlist / spec / PDF wording
- extracting repeated parameter names, mode names, rails, signals, and protocol terms

Guardrails:
- do NOT rename, rezip, or edit the source workbook
- do NOT use the markdown shadow view as the sole basis for row mapping
- for macro-bearing or heavily formatted workbooks, prefer OOXML/manual inspection for authoritative structure

# Full pipeline handoff
```bash
# Direct to Excel (known family)
python3 ~/.openclaw/workspace-tenji/scripts/compile_tenji.py \
  --sa-workbook plan.xlsx --sa-family SinglePwr_C2A --output TN.xlsm

# Classify only
python3 ~/.openclaw/workspace-tenji/scripts/compile_tenji.py \
  --sa-workbook plan.xlsx --classify-only
```

Families: SinglePwr_C2A(3行) / Single_power3(4行) / Single_power4(4行) / DualPwr(3行) / VoltFollow(2行) / SmartBlind(2行)
Aliases: 單電源c2a / 雙電源 / 電壓跟隨 / 智能盲插

See `intake-procedure.md` for detailed OOXML parsing steps, header detection patterns, and output format.
See `references/markitdown-shadow-view.md` for using a markdown/text shadow view to cross-link SA workbooks with DUT collateral without replacing the authoritative OOXML intake.

# SA Index (pre-built cache)
Large workbooks should be indexed first to avoid re-parsing on every request:

```bash
# Build index (run once, or after workbook update)
python3 ~/.openclaw/workspace-tenji/scripts/build_sa_index.py plan.xlsx

# Check if index is still fresh
python3 ~/.openclaw/workspace-tenji/scripts/build_sa_index.py plan.xlsx --check

# Look up a specific case without re-reading the workbook
python3 ~/.openclaw/workspace-tenji/scripts/build_sa_index.py plan.xlsx --query "2-11"

# Via compile_tenji
python3 ~/.openclaw/workspace-tenji/scripts/compile_tenji.py \
  --sa-workbook plan.xlsx --build-index

python3 ~/.openclaw/workspace-tenji/scripts/compile_tenji.py \
  --sa-workbook plan.xlsx --query-case "2-11"
```

Index is stored at `~/.openclaw/workspace-tenji/sa-index/<name>.index.json`.
Auto-invalidates when source file mtime or sha256 changes.
Contains: sheet inventory + per-case {row, name, min, max, unit} for all testcase sheets.
