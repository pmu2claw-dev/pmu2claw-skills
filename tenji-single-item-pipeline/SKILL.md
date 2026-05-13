---
name: tenji-single-item-pipeline
description: Extract a reviewed TENJI single-item spec from an ANS workbook, validate family rules, assemble .xlsm, verify roundtrip. Use when ANS workbook exists; use bootstrap_family.py when it doesn't.
---

# When to use
ANS workbook exists → use this skill (byte-copy or extract→reassemble).
No ANS workbook → use `bootstrap_family.py` + `compile_tenji.py --sa-workbook`.

Triggers: single item / 單電源2-x / extract spec / roundtrip / ANS lineage / family validation

# Core workflow
1. Extract exact body rows from `Test Note` into formal row specs (use `make_item_spec`, not `new_item_spec`)
2. Preserve `style_source.workbook/sheet/row` per row
3. Run family-specific validation
4. Assemble back into `.xlsm`
5. Verify: reopen + merged ranges + LibreOffice headless

# Extraction: find case rows
Scan column I (Description) for case token (e.g. `2-25`). Extract until `OS_test2` or empty symbol+measure.

Fields per row: B(bin) C(test_item) D(symbol) E(pwr_seq) F(pseudo_code) G(run_pattern) H(measure_cond) I(description) J(min) K(typ) L(max) M(unit) N(remarks) + style_source

# Family rules (SinglePwr_C2A confirmed 2026-05-06)
- 3 body rows: C1_9V (PWR_VBUS) → C2_Atach → C2_detach
- measure pin: VBUSC_C1 (JD6628H), verify per project
- min=K*0.8 / max=K*1.2 Excel formula (not hardcoded)
- OS_test head + C3:C5 merged + OS_test2 tail
- vbaProject.bin hash must be preserved

Single_power3/4 → 4 rows. See `validation-and-assembly.md` for all family details.

# ANS-style surface rule
Prefer byte-copy of ANS workbook over openpyxl resave when possible.
openpyxl resave risk: drops calcChain.xml, rewrites sharedStrings, loses formula references.

## Near-case donor rule when exact ANS workbook is missing but surface is identical
A later `單電源2-11` delivery validated a lightweight single-item reuse path for the mirrored `C2 -> C1 join -> C1 detach` family:

- exact `2-11` ANS workbook was missing
- nearby exact `2-10` ANS workbook existed
- SA source row `2-11` showed the same observable verification states as `2-10`
- the authoritative fields for TENJI row content (`預期結果`, `Target voltage`, `Request PDO`) were unchanged from `2-10`
- only the action prose changed (`C1` advertised `12V` instead of `9V`), but that prose did **not** change the validated TENJI row surface because step 2 still dropped to `PDO1/5V` and step 3 still recovered the original `C2` `PDO2/9V`

Safe reuse rule:
1. inspect the SA source row for the requested case and the nearby exact donor case side by side
2. compare these source columns first, not the casual `SINK_xV` wording in the step prose:
   - `預期結果`
   - `Target voltage`
   - `Request PDO`
   - protocol / verify columns when present
3. if those fields imply the same 3-row verification obligations, reuse the nearby ANS workbook as the package/surface donor
4. keep the donor's TENJI DSL, symbols, formulas, merged ranges, and wrapper rows unchanged unless one of the authoritative source fields proves they must change
5. for cases like `2-11`, update only the case-qualified description cells (`I3:I5`) so the delivered workbook names the requested testcase correctly while preserving the validated `Test Note` surface
6. verify by reopening the `.xlsm`, checking `C3:C5`, confirming `vbaProject.bin` hash preservation, and running headless LibreOffice conversion

Practical implication for the `單電源2-10~2-18` C2-first family:
- do **not** overfit to the step prose `C1插入 SINK_12V/20V`
- if `Request PDO` still says `step1=C2 PDO2`, `step2=both PDO1`, `step3=C2 PDO2`, the direct-delivery surface remains the same `9V -> 5V -> 9V` ANS pattern
- in that situation, a nearby exact ANS workbook can be used as the single-case donor without regenerating the DSL

# Fast path (no LLM)
```bash
python3 ~/.openclaw/workspace-tenji/scripts/compile_tenji.py \
  --sa-workbook plan.xlsx --sa-family SinglePwr_C2A --output TN.xlsm
```

See `automation-scripts.md` for full reference. See `validation-and-assembly.md` for detailed rules.

# Done criteria
- reviewed spec extracted from ANS workbook
- family validation passes
- `.xlsm` reopens, VBA hash preserved, merged ranges correct
- LibreOffice headless conversion succeeds
