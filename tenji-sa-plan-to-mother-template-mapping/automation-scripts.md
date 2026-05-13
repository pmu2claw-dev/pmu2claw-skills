# Automation layer (added 2026-05-06)

## Automated pipeline entry points

The following scripts under `~/.openclaw/workspace-tenji/scripts/` form an end-to-end automation layer:

### sheet_classifier.py — SA workbook intake
Reads SA Excel via OOXML (read-only), classifies each sheet into one of:
- `testcase` → strategy `direct_map` (TENJI-ready)
- `mode_matrix` → strategy `scenario_expand` (needs family expansion)
- `spec_ec` / `spec_timing` → strategy `spec_extract` (needs limit extraction)
- `pdo_table` → strategy `spec_extract`
- `power_matrix`, `summary`, `skip`, `unknown`

Outputs JSON with `recommended_entry_sheet` and per-sheet `notes`.

```
python3 sheet_classifier.py SA_plan.xlsx
```

### mode_expander.py — Mode-matrix row expansion

Expands one SA testcase row into N TENJI test_item rows using family rules:

| Family | Rows | Notes |
|---|---|---|
| `SinglePwr_C2A` | 3 | Single_power2 + PD_req9V → PD_req5V → PD_req9V, all MeasV VBUSC_C2 |
| `Single_power3` | 4 | detect + 9V(C2) + 5V(C3) + 9V(C3) |
| `Single_power4` | 4 | mirrored of power3 on C4 port |
| `DualPwr` | 3 | C2 steady + C3 steady + cross-load event |
| `VoltFollow` | 2 | ForceV C3 9V/5V, MeasV C2 |
| `SmartBlind` | 2 | blind attach + role detect + steady measure |

Family aliases accepted (Chinese/English): `單電源c2a`, `雙電源`, `電壓跟隨`, `智能盲插`, etc.

```python
from mode_expander import expand_mode_row
items = expand_mode_row("SinglePwr_C2A", {"name": "VBUS 9V", "min": "8.5", "max": "9.5"})
```

### bootstrap_family.py — First-pass spec without ANS sample

When no ANS workbook exists, generates a scaffold spec from SA rows alone:

```
python3 bootstrap_family.py \
    --workbook SA_JD6628H.xlsx \
    --sheet "TC_Main" \
    --family SinglePwr_C2A \
    --dut-notes "JD6628H C2A port, 9V/3A" \
    --output first_pass.spec.json
```

Auto-detects family from sheet text if `--family` omitted.
Generates skeletal `pinmap` and `power_sequence` stubs that must be reviewed.

### feedback_processor.py — Feedback → learned rules

Reads `feedback.jsonl` and updates `LEARNINGS.md` Auto-learned section:

```
python3 feedback_processor.py          # live update
python3 feedback_processor.py --dry-run  # preview only
```

feedback.jsonl entry format:
```json
{"ts":"2026-05-06T10:00:00","type":"correction","context":{"family":"SinglePwr_C2A","field":"max_v","old":"9.5","new":"10.0"},"note":"允許10V tolerant"}
```

`type` values: `correction`, `confirm`, `reject`

### Integrated pipeline (compile_tenji.py SA mode)

```bash
# Classify only
python3 compile_tenji.py --sa-workbook plan.xlsx --classify-only

# Full SA intake → Excel
python3 compile_tenji.py \
    --sa-workbook SA_JD6628H_testplan.xlsx \
    --sa-family SinglePwr_C2A \
    --sa-dut-notes "C2A port only" \
    --output JD6628H_TN.xlsm
```

## Decision tree: SA sheet → TENJI strategy

```
SA sheet
 ├─ role=testcase & tenji_ready=true  → direct_map via ai_parser + validate
 ├─ role=mode_matrix                  → scenario_expand via mode_expander
 │    └─ infer family from headers/DUT notes, then expand each row
 ├─ role=spec_ec / spec_timing        → spec_extract: pull min/typ/max → Judge rows
 ├─ role=pdo_table                    → spec_extract: map PDO entries → ForceV/MeasI rows
 ├─ role=power_matrix                 → spec_extract: define pwr_seq groups
 └─ role=skip / unknown              → manual review required
```

## New family onboarding (no ANS sample)

1. Run `sheet_classifier.py` to identify sheets and auto-detect IC name
2. Run `bootstrap_family.py` with `--family` (or let it auto-detect)
3. Review generated `first_pass.spec.json`:
   - Verify pinmap pins exist on actual DUT schematic
   - Adjust min/max limits from datasheet
   - Fill pseudo_code for any placeholder items
4. Run `compile_tenji.py --spec first_pass.spec.json --output TN_draft.xlsm`
5. Open in LibreOffice/Excel to verify visually
6. Log corrections to `feedback.jsonl`
7. Run `feedback_processor.py` to update `LEARNINGS.md`
