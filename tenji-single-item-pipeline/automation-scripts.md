# Related automation scripts (added 2026-05-06)

These scripts live at `~/.openclaw/workspace-tenji/scripts/` and extend the single-item pipeline with upstream SA intake capability.

## New entry points

### When you have an SA workbook instead of an ANS sample

```bash
# Step 1: classify sheets
python3 sheet_classifier.py SA_plan.xlsx

# Step 2: bootstrap spec (replaces manual draft when no ANS exists)
python3 bootstrap_family.py \
    --workbook SA_plan.xlsx --sheet "TC_Main" \
    --family SinglePwr_C2A --output draft.spec.json

# Step 3: compile to Excel (same as before)
python3 compile_tenji.py --spec draft.spec.json --output TN.xlsm
```

Or collapse steps 1–3:
```bash
python3 compile_tenji.py --sa-workbook SA_plan.xlsx --sa-family SinglePwr_C2A --output TN.xlsm
```

### Family rules now formalized in mode_expander.py

All 6 families have exact row-count rules enforced programmatically:

```python
from mode_expander import expand_mode_row
items = expand_mode_row("SinglePwr_C2A", {"name": "VBUS 9V", "min": "8.5", "max": "9.5"})
# → exactly 3 items: Single_power2 row, PD_req5V row, PD_req9V row
```

`spec_validator.py` uses these same rules for post-generation validation.

### Feedback loop

```bash
# After user corrections, log to feedback.jsonl:
echo '{"ts":"2026-05-06T10:00:00","type":"correction","context":{"family":"SinglePwr_C2A","field":"max_v","old":"9.5","new":"10.0"},"note":"10V tolerant spec"}' >> ~/workspace-tenji/feedback.jsonl

# Then update LEARNINGS.md:
python3 feedback_processor.py
```

## Decision: ANS sample exists vs. not

| Situation | Use |
|---|---|
| Validated ANS workbook exists | `tenji-single-item-pipeline` (byte copy or extract→reassemble) |
| No ANS, SA sheet available | `bootstrap_family.py` → review → `compile_tenji.py` |
| No ANS, no SA sheet | Minimal spec draft → `ai_parser.py` → validate |
