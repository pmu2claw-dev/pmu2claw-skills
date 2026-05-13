---
name: tenji-sa-plan-to-mother-template-mapping
description: Map an SA test plan workbook into a TENJI mother template. Classify sheets (testcase/spec/scenario), expand mode-matrix rows into TENJI Test Note rows, preserve originals read-only.
---

# When to use
After SA workbook is inspected. User wants SA content mapped into a TENJI `.xlsm` template.

Triggers: map SA→TENJI / convert test plan / generate Test Note from SA sheet / 轉 TENJI / SA 轉換

# Three-input model
1. SA test plan workbook (source rows, modes, expected results)
2. DUT/test-environment evidence (attach controls, UR paths, VBUS nodes)
3. TENJI mother template or validated ANS workbook (row shape, wrappers, symbols)

Never rename, rezip, or destructively edit source files. Parse OOXML read-only.

# Sheet roles (quick ref)
- `testcase` → direct_map (TENJI-ready)
- `mode_matrix` → scenario_expand (one SA row → N TENJI rows)
- `spec_ec/timing` → spec_extract (pull min/typ/max → Judge rows)
- `pdo_table` → spec_extract
- `summary/tracker` → skip

# Family row counts (SinglePwr confirmed by 2-2 delivery 2026-05-06)
| Family | Rows | pwr_seq row1 | measure pin |
|---|---|---|---|
| SinglePwr_C2A | 3 | PWR_VBUS* | VBUSC_C1* |
| Single_power3 | 4 | project-specific | VBUSC_C2/C3 |
| Single_power4 | 4 | project-specific | VBUSC_C4 |
| DualPwr | 3 | DualPwr_C2/C3 | VBUSC_C2+C3 |
| VoltFollow | 2 | VoltFollow_9V/5V | VBUSC_C2 |
| SmartBlind | 2 | SmartBlind_Attach | VBUSC_C2 |

*JD6628H project values — verify per-project pinmap before generating.

# TENJI field mapping (core)
| SA column | TENJI field |
|---|---|
| 功能/測試項目 | test_item + symbol prefix |
| 預期結果/Pass Criteria | description |
| min/max | min/max (formula =K*0.8/=K*1.2 pattern) |
| 驗證方法 | measure_cond |
| 模式 | pwr_seq group |

# Workbook structure rules
- OS_test head + body rows + OS_test2 tail
- C3:C5 merged for ANS-style surface
- vbaProject.bin hash must be preserved
- min=K*0.8 / max=K*1.2 Excel formula pattern (not hardcoded values)

# Automation scripts (fast path)
```bash
# Classify SA workbook
python3 ~/.openclaw/workspace-tenji/scripts/sheet_classifier.py plan.xlsx

# Full pipeline (known family, no LLM needed)
python3 ~/.openclaw/workspace-tenji/scripts/compile_tenji.py \
  --sa-workbook plan.xlsx --sa-family SinglePwr_C2A --output TN.xlsm

# Bootstrap without ANS sample
python3 ~/.openclaw/workspace-tenji/scripts/bootstrap_family.py \
  --workbook plan.xlsx --sheet "TC_Main" --family SinglePwr_C2A --output draft.spec.json
```

See `automation-scripts.md` for full script reference.
See `mapping-rules.md` for detailed sheet classification, scenario expansion rules, SOP gates, and pitfalls.

# Done criteria
- `.xlsm` opens, VBA hash preserved
- OS_test head/tail present
- every body row has non-empty J/K/L/M for spec-validation rows
- traceability to source sheet/row preserved in description
- labeled first-pass vs final
