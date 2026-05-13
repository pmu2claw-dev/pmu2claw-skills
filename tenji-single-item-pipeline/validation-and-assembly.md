# Validation rules
## General reviewed-row checks
For non-draft specs:
- `style_source.sheet` must exist
- `style_source.workbook` must exist
- `lineage.primary_references` must be non-empty
- wrapper policy must remain `workbook_scope_only`

## SinglePwr_C2A family rules
Validated working rules for `SinglePwr_C2A`:
- exactly 3 body rows
- row 1 `test_item_anchor` must be `Single_power2`
- row 1 must contain `PD_command PD_req9v`
- row 2 must contain `PD_command PD_req5v`
- row 3 must contain `PD_command PD_req9v`
- all 3 rows must measure `VBUSC_C2`
- row `typ` values must be `9`, `5`, `9`

These rules caught incorrect drift where the shared-state row accidentally requested 9V instead of 5V.

# Roundtrip assembly + verification
## Assemble
Typical command:

```bash
/usr/bin/python3 assemble_workbook.py \
  --template /path/to/JD6628H_SinglePwr_2-25_ANS_TenjiV2.2_R0.1.xlsm \
  --output /tmp/singlepwr_2_25_roundtrip.xlsm \
  --item-spec /tmp/singlepwr_2_25.json
```

Expected report shape for a single extracted case:
- `item_count: 1`
- case starts at row 3
- case ends at row 5
- tail row usually 6 when using the single-case answer workbook as template

## Verify
Typical command:

```bash
/usr/bin/python3 verify_workbook.py \
  --workbook /tmp/singlepwr_2_25_roundtrip.xlsm \
  --sheet-name 'Test Note' \
  --start-row 1 \
  --end-row 6 \
  --libreoffice-outdir /tmp/lo_probe
```

## Expected verification findings for the `2-25` single-case roundtrip
- merged ranges include `C3:C5`
- row 1 in verification output is the header
- row 2 is `OS_test`
- actual extracted case body starts at row 3
- row 3 contains `Single_power2 / C2_9V_2`
- row 4 contains `A_Atach_2`
- row 5 contains `A_detach_2`
- LibreOffice conversion should succeed and produce a readable `.xlsx`

# Important experiential findings
## Verification indexing
A test initially failed because the expected verification row indexes were off by one section:
- `verify_workbook.py` includes the header row and `OS_test`
- therefore the first real case body row is index `2` in the JSON `rows` array only if row numbering started from 1? No — be careful:
  - `rows[0]` = sheet row 1 header
  - `rows[1]` = sheet row 2 `OS_test`
  - `rows[2]` = sheet row 3 first real body row

When writing assertions, do not assume the first case body row is `rows[1]`.

## Surface-lineage gate: ANS-style beats family-golden for single-item delivery
A later JD6628H `單電源2-25~2-30` incident showed that a workbook can be semantically valid and even come from a validated family/golden delivery, yet still be the **wrong surface** for the user's expected deliverable.

Observed mismatch:
- existing single-case ANS workbooks for `2-25` and `2-26` used the classic ANS surface:
  - `Test Item = Single_power2`
  - action-oriented symbols such as `C2_9V_2`, `A_Atach_2`, `A_detach_2`
  - TENJI DSL directly in `Measure Condition` (`ForceV`, `ForceI`, `UR`, `PD_command`, `MeasV`, `JudgeV`)
  - 3 body rows between workbook-level `OS_test` / `OS_test2`
- a previously delivered `2-25~2-30` family workbook was still wrong for that request because it used a prose/generator-style surface:
  - `Test Item = SinglePwr_C2A`
  - placeholder symbols like `SP_2_25_S1`
  - prose blocks like `Source Step`, `Target voltage`, `Gate ON`
  - 4 body rows per case

Reusable rule:
1. if the user asks for a file "照之前的 ANS 風格" or compares against a prior ANS workbook, do **not** assume a validated family workbook is authoritative just because it is golden or already delivered
2. first compare the candidate workbook against the prior ANS lineage on these columns/traits:
   - column C `Test Item`
   - column D `Symbol`
   - column H `Measure Condition` vocabulary
   - body-row count per testcase
3. for **single-item delivery**, exact-case or nearby single-case ANS workbooks outrank family/golden workbooks when the surfaces differ
4. if the family workbook reads like `generator summary` while the ANS workbook reads like `ATE script`, quarantine the family workbook for that delivery goal and rebuild from the ANS lineage instead of patching the prose surface in place

Practical pre-delivery surface audit:
- dump representative `Test Note` rows from the candidate delivery workbook and the prior ANS workbook
- compare `C/D/H/I/J/K/L/M/N` side by side for at least one testcase
- reject the candidate if the ANS lineage is action-script / TENJI-DSL and the candidate is still placeholder/prose-style, even when package integrity and macros are fine

## Exact-copy vs resave rule for ANS lineage
A later `單電源2-25~2-30` ANS-style rebuild added an important packaging rule:
- if an **exact single-case ANS workbook already exists** for the requested case, prefer a byte-preserving file copy as the deliverable base instead of loading and saving it through `openpyxl`
- only generate/edit workbooks for the cases that truly have no exact ANS lineage available

Reason:
- an `openpyxl.load_workbook(..., keep_vba=True)` -> `wb.save(...)` roundtrip can keep `xl/vbaProject.bin` intact yet still rewrite the workbook package heavily
- in the observed JD6628H ANS-style workbook, the roundtrip dropped `xl/calcChain.xml`, moved comment parts, removed drawing/media relationships, rewrote shared strings, and reduced file size substantially even though the resulting file still opened
- therefore, when the source workbook is already the exact expected ANS deliverable surface, resaving creates unnecessary package drift with no user benefit

Practical decision tree:
1. if exact ANS workbook exists for the requested case -> copy it directly and verify read-back/hash/macros
2. if no exact ANS workbook exists but a nearby ANS-style workbook exists -> use that ANS-style workbook as the editable surface base, changing only the truly variable testcase cells
3. do **not** use a prose-style family workbook as the editable base for an ANS-style redelivery unless you have already proven its surface matches the ANS lineage
4. after any save-based generation, compare package-level signals (`namelist` diff, file size, VBA hash, readable probe) so you know whether you preserved only content or also introduced packaging drift

## Combined ANS-style family assembly from exact single-case donors
A later `單電源2-25~2-30` delivery request needed **one combined `.xlsm`** while still keeping the classic 3-row ANS surface (`Single_power2` / `A_Atach_2` / `A_detach_2`) instead of the existing prose/family workbook shape.

## Single-case rebuild when the exact ANS workbook is missing but an ANS-style family workbook exists
A later `單電源2-27` delivery used an important hybrid pattern:
- there was **no exact single-case `2-27` ANS workbook** available
- nearby exact ANS single-case donors existed (`2-25`, `2-26`)
- an already validated **combined ANS-style family workbook** also existed and already contained the correct `2-27` rows on the right surface

Reusable decision rule:
1. if the requested single case has no exact ANS workbook, search for a **combined family workbook that already matches the ANS surface**, not just the semantics
2. if that family workbook uses the same surface conventions as the target lineage — for example:
   - `Test Item = Single_power2`
   - symbols like `C2_12V_2`, `A_Atach_2`, `A_detach_2`
   - TENJI DSL in `Measure Condition`
   - 3-row body shape with workbook-level `OS_test` / `OS_test2`
   then it is acceptable to treat that family workbook as the **authoritative content source** for the missing case
3. use the nearest exact single-case ANS workbook as the **package/style donor** (same merge pattern, row styling, VBA-bearing shell)
4. copy the donor workbook first, then edit only the truly case-specific cells in `Test Note`
5. preserve the merged-item pattern — for a `C3:C5` single-case shell, only write `C3`, never `C4/C5`

Worked `2-27` pattern:
- source test plan showed `C2=PDO3 -> C2=PDO1 -> C2=PDO3`
- therefore `2-27` is the `C2 12V` family, not `9V`
- the combined ANS-style family workbook confirmed the exact target surface for the missing case:
  - row 1 symbol `C2_12V_2`
  - row 1 `PD_req12v`, judge `9.6~14.4`
  - row 2 `A_Atach_2`, `PD_req5v`, judge `4~6`
  - row 3 `A_detach_2`, `PD_req12v`, judge `9.6~14.4`
- a nearby exact single-case ANS workbook (`2-26`) was then used as the base `.xlsm`, with only the variable cells changed to the `2-27` values

Practical verification gates for this hybrid path:
- confirm the rebuilt workbook still has the single-case shell shape (`OS_test`, 3 body rows, `OS_test2`)
- read back `Test Note` rows `1:6` after save, not just the edited cells in memory
- confirm merged ranges still include `C3:C5`
- compare `xl/vbaProject.bin` hash between donor and rebuilt output
- compare zip entry sets between donor and rebuilt output to catch accidental package-part loss
- run headless LibreOffice conversion on the rebuilt `.xlsm`

This rule is specifically useful when the missing case is part of a family that has already been validated as an ANS-style combined workbook, and the delivery goal is a **single-case ANS `.xlsm`** rather than another family workbook.

Worked approach on this host:
1. use the exact `2-25` ANS workbook as the combined-workbook template base so `OS_test`, row styling, and VBA payload come from a real ANS file
2. use `2-26` as a same-family donor to confirm the reusable 3-row surface is stable
3. rebuild only `Test Note` rows `3:20` as six 3-row case blocks:
   - `2-25` rows `3:5`
   - `2-26` rows `6:8`
   - `2-27` rows `9:11`
   - `2-28` rows `12:14`
   - `2-29` rows `15:17`
   - `2-30` rows `18:20`
4. keep row `21` as the copied `OS_test2` tail row from the ANS template
5. preserve the ANS merged-item pattern by creating one merge per case block:
   - `C3:C5`, `C6:C8`, `C9:C11`, `C12:C14`, `C15:C17`, `C18:C20`
6. for generated cases without exact source workbooks, synthesize only the variable content:
   - symbol (`C2_9V_2` / `C2_12V_2` / `C2_20V_2`)
   - `PD_req*`
   - judge bands (`7.2~10.8`, `9.6~14.4`, `16~24`)
   - description text and row-local formulas (`=K{row}*0.8`, `=K{row}*1.2`)
7. clone styles from donor semantic rows by copying cells `B:N` and row-level presentation only, then overwrite values

Important implementation detail:
- when cloning row presentation with `openpyxl`, copy `height`, `hidden`, and `outlineLevel`, but **do not assign** `RowDimension.customHeight`; on this host it raised `AttributeError: property 'customHeight' of 'RowDimension' object has no setter`

Verification gates that proved the combined file was acceptable:
- full-file SHA-256 recorded
- `xl/vbaProject.bin` SHA-256 exactly matched the base ANS template
- reopen `Test Note` and verify anchors, symbols, descriptions, merged ranges, and formulas for first/middle/last cases
- run `libreoffice --headless --convert-to xlsx` on the final `.xlsm` and inspect the converted workbook rows, not an unrelated earlier prose-style probe file

When to use this pattern:
- the user wants **one family workbook** but explicitly still wants the **ANS single-case surface lineage**
- you have at least one exact ANS workbook that can serve as the package/style template
- an existing family workbook is structurally valid but visually/procedurally the wrong surface for delivery

## Combined ANS-style family assembly for 4-row `Single_power3` / `C1+C2+A` cases
A later `單電源2-43~2-60` delivery established a parallel reusable pattern for the `Single_power3` family, where each testcase occupies **4 body rows** rather than 3.

Worked `2-43~2-60` approach on this host:
1. use the exact `2-43` ANS workbook as the package/style/VBA donor
2. read the SA-plan source rows for `2-43~2-60` and derive the boosted target voltage from the first expected-result line (`9V` / `12V` / `20V`)
3. rebuild the combined workbook as 18 consecutive 4-row blocks in `Test Note`, starting at row `3`
4. for each case, preserve the surface shape:
   - row 1: `Single_power3` + boosted `C1_<voltage>V_3`
   - row 2: `C2_Atach_3` and shared `5V`
   - row 3: `A_Atach_3` and shared `5V`
   - row 4: `A_detach_3`
5. create one merged testcase anchor per case block:
   - `C3:C6`, `C7:C10`, ... , `C71:C74`
6. copy the semantic row styles from donor rows `3:6`, copy the donor tail row `7` to the new final tail row `75`, and clear rows after the tail
7. rewrite row-local formulas for every destination row (`=K{row}*0.8`, `=K{row}*1.2`)

Critical semantic rule learned from this family:
- if the exact `2-43` answer workbook's final step looks anomalous or family-inconsistent, do **not** blindly generalize that final-step TENJI block to all later cases
- for `2-43~2-60`, the safe generalization was to follow the SA-plan semantics for step 4: after `A_detach_3`, `C1/C2` **maintain shared 5V**, so judge `VBUSC_C1` at `4~6V` rather than re-requesting the boosted voltage
- treat this as a lineage anomaly check: donor workbook gives the surface and row styles, but family-wide step semantics must still be cross-checked against the source plan before cloning

Reusable voltage-mapping rule for this family:
- `9V` -> symbol `C1_9V_3`, request `PD_req9v`, judge `7.2~10.8`
- `12V` -> symbol `C1_12V_3`, request `PD_req12v`, judge `9.6~14.4`
- `20V` -> symbol `C1_20V_3`, request `PD_req20v`, judge `16~24`
- rows 2~4 keep `typ=5` with formulas based on the destination row's `K` cell

Verification gates that proved this 4-row family file was acceptable:
- record full-file SHA-256
- confirm `xl/vbaProject.bin` SHA-256 matches the exact donor workbook
- reopen `Test Note` and inspect at least first/middle/last cases (for example `2-43`, `2-52`, `2-60`)
- confirm merged ranges span every 4-row block up to `C71:C74`
- confirm the copied tail wrapper is at row `75`
- run `libreoffice --headless --convert-to xlsx` and inspect the converted workbook rows to ensure the visible surface survived office import/export

## Combined ANS-style family assembly for 4-row `Single_power4` mirror families (`2-61~2-96`)
A later `單電源2-61~2-96` delivery established a reusable combined-workbook pattern for the three-participant mirror families:
- `2-61~2-78`: `C1 -> A -> C2 -> C2 detach`
- `2-79~2-96`: `C2 -> A -> C1 -> C1 detach`

Worked approach on this host:
1. use the exact `2-61` ANS workbook as the package/VBA shell and final output base
2. use the exact `2-79` ANS workbook as the mirrored C2-family semantic/style donor
3. read the SA-plan source rows for `2-61~2-96` and derive the boosted voltage family from the first `Request PDO` / expected-result line:
   - `PDO2` -> `9V`
   - `PDO3` -> `12V`
   - `PDO5` -> `20V`
4. rebuild the combined workbook as 36 consecutive 4-row blocks starting at row `3`, then place the copied `OS_test2` tail row at row `147`
5. create one merged testcase anchor per case block (`C3:C6`, `C7:C10`, ... , `C143:C146`)
6. for each case, copy rows `3:6` from the matching semantic donor first, then overwrite only the variable cells

Important donor-selection rule:
- do not flatten the whole family onto one donor surface just because the semantic shape is mirrored
- the `2-61` and `2-79` answer workbooks contain meaningful surface differences beyond simple `C1 <-> C2` swaps, including row-local timing/script details and symbol variants
- safe rule:
  - `2-61~2-78` use `2-61` rows `3:6` as the row-style / script donor
  - `2-79~2-96` use `2-79` rows `3:6` as the row-style / script donor

Stable row pattern for this family:
1. row 1 = primary Type-C only, boosted voltage on the primary port
2. row 2 = A joins, primary drops to shared `5V`
3. row 3 = third Type-C participant joins, measure the newcomer at `5V`
4. row 4 = third participant detaches, surviving primary + A remain at `5V`

Variable content to synthesize per case:
- row-1 symbol: `C1_9V_4` / `C1_12V_4` / `C1_20V_4` or mirrored `C2_9V_4` / `C2_12V_4` / `C2_20V_4`
- row-1 `PD_command`: `PD_req9v` / `PD_req12v` / `PD_req20v`
- row-1 judge band: `7.2~10.8`, `9.6~14.4`, or `16~24`
- row descriptions from the exact SA source row
- row-local formulas rewritten to destination rows (`=K<row>*0.8`, `=K<row>*1.2`)

Verification gates that proved this family file was acceptable:
- record full-file SHA-256
- confirm the output `xl/vbaProject.bin` hash matches the chosen package-shell donor (`2-61` in this workflow)
- reopen and inspect representative first/middle/last cases from both mirror halves, for example `2-61`, `2-70`, `2-79`, `2-88`, `2-96`
- confirm the merged-range count equals the testcase count (`36`)
- confirm the tail wrapper row is `OS_test2` at row `147` and rows below are cleared
- run `libreoffice --headless --convert-to xlsx` and read back representative cases from the converted workbook, not just the `.xlsm`

## Quick redelivery of an already-validated `2-61~2-96` family workbook
When the user says they just want the file (`檔案請給我`) and an existing family deliverable is already present under `workspace-tenji/deliveries`, prefer **verification + direct handoff** over rebuilding.

Worked quick-release path on this host:
1. use the existing family workbook as the candidate deliverable, for example:
   - `/home/user/workspace-tenji/deliveries/JD6628H_SinglePwr_2-61_to_2-96_TenjiV2.2_R0.1_ANSstyle_deliver.xlsm`
2. inspect it with `/usr/bin/python3`, not bare `python3`, because `python3` on this host may lack `openpyxl`
3. reopen `Test Note` with `keep_vba=True` and verify these structural checkpoints:
   - row `2` = `OS_test`
   - rows `3:6` begin the `2-61` block
   - row `75` begins the mirrored `2-79` block
   - rows `143:146` hold the final `2-96` block
   - row `147` = `OS_test2`
4. confirm merged testcase anchors still exist for all 36 cases
5. compute both full-file SHA-256 and `xl/vbaProject.bin` SHA-256
6. run `libreoffice --headless --convert-to xlsx` and reopen the converted workbook to confirm the visible `Test Note` surface survived Office-style import/export
7. only after those checks, hand over the concrete file path directly

Representative quick-audit rows that were sufficient in practice:
- start of first mirror half: `2:10`
- start of second mirror half: `75`
- end of workbook: `143:147`

This quick-redelivery path is the right choice when the task is **deliver the verified file now**, not regenerate a new combined workbook.

# Test recipe


```bash
pytest -q tests/test_tenji_pipeline.py::test_convert_single_item_extracts_real_answer_workbook -q
pytest -q tests/test_tenji_pipeline.py::test_validate_single_item_enforces_singlepwr_c2a_rules -q
pytest -q tests/test_tenji_pipeline.py::test_assemble_and_verify_roundtrip_single_case -q
pytest -q tests/test_tenji_pipeline.py
```

# Pitfalls
- Do not rely on starter draft JSON when a real answer workbook exists.
- Do not drop `style_source.workbook` from reviewed rows; roundtrip style provenance matters.
- Do not infer body-row verification indexes without checking whether header + `OS_test` are included.
- Do not change `SinglePwr_C2A` row 2 into a 9V request; the family-specific validator should reject it.
- If using Python Excel tooling on this host, prefer `/usr/bin/python3` when `python3` lacks `openpyxl`.

# Done criteria
You are done when:
- reviewed spec was extracted from answer workbook
- family-specific validation passes
- assembled workbook reopens successfully
- `verify_workbook.py` shows the expected merged range and row contents
- LibreOffice headless conversion succeeds
- the focused tests and the full pipeline test file all pass

---
