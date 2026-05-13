# Procedure

## 1. Confirm the file path
Use the cached document path supplied by Hermes. Treat the workbook as read-only.

## 2. Parse workbook structure with Python
Use `execute_code` to inspect the OOXML package. Extract at minimum:

- sheet name
- visible/hidden state
- worksheet target xml
- dimension range (for rough size)
- non-empty row/cell counts
- first 2–3 meaningful rows
- a few sample testcase rows

Implementation notes:

- resolve sheet relationship IDs from `workbook.xml.rels`
- decode shared strings from `sharedStrings.xml`
- for each cell, handle formula, shared-string, inline-string, and raw value cases
- identify candidate testcase rows by patterns like numeric `A` column + populated `C/D/E/F`
- if you need `openpyxl` for a quick workbook read-back and `python3` fails with `ModuleNotFoundError: openpyxl`, retry with `/usr/bin/python3` before changing approach; on some hosts the system interpreter has the Excel dependency while the default shell `python3` does not

## 3. Separate sheet types
Classify sheets into buckets such as:

- summary/dashboard
- datasheet/parametric spec validation
- feature testcase sheets
- protocol testcase sheets
- mode/config matrix sheets
- compatibility sheets
- misc/reliability sheets

Typical signal that a sheet is a normal testcase sheet:

- headers like `No.`, `功能`/`Function`, `測試項目`/`Test Item`, `測試方法`/`Test Condition`, `預期結果/規格`/`Specification`, `驗證方法`

Typical signal that a sheet is **not** a simple testcase sheet:

- heavy formula usage for cross-sheet summary
- PDO tables / mode matrices / port combination enumerations
- parameter tables with min/typ/max/unit columns

## 4. Identify TENJI-ready vs special-case sheets
Mark sheets as:

### Direct-map candidates
Usually sheets whose rows already behave like testcase records, with columns equivalent to:

- function
- test item
- test method / condition
- expected result / spec
- verification method

### Needs-normalization candidates
Usually sheets like:

- EC/timing parameter tables
- protocol matrices
- power mode matrices
- PDO capability tables
- summary sheets with formulas only

These often require one-to-many expansion or custom rules before TENJI import.

Additional classification guidance discovered in this workflow:

- Treat summary/dashboard sheets with cross-sheet formulas (for example COUNTIF over feature sheets) as coverage/readiness trackers only, not testcase sources.
- Treat DUT schematic netlists provided alongside the workbook as a control-resource map for later conversion. They are used to identify controllable attach/detach paths, VBUS paths, I2C/DPDM gating, NTC, OPTO, discharge, and other simulation resources — not just a DUT pin list.
- When testcase wording alone does not fully reveal the control method, compare the test-environment circuitry too. In particular, inspect control elements such as UR switching paths/states to infer how attach, VBUS routing, CC gating, or measurement selection is actually realized in TENJI.

## 5. Report project understanding first
Before proposing conversion, summarize what the workbook reveals about the project, for example:

- key verification domains covered
- whether the workbook mixes SA definitions with DRD/ARD/CAD/TIM tracking
- whether it is a pure testcase source or an integrated execution tracker

This matches the user's preferred workflow: understand the SA plan structure/content before converting anything into TENJI.

# Output format
Return a concise but structured report:

## Workbook nature
- one-line description of what the file is

## Sheet groups
- grouped inventory with sheet names

## Common testcase schema
- shared columns observed across feature sheets

## Direct-map sheets
- list of sheets that can map to TENJI with minimal reshaping

## Special handling sheets
- list plus why they need custom handling

## Recommended next step
- usually: create a sheet-to-TENJI mapping table, or pilot one representative sheet first

# Pitfalls
- Do not assume every populated row is a testcase; summary sheets can mimic numeric rows via formulas.
- In SA workbooks that visually group testcase families, category or section cells may be merged/only populated on the first row of the family. Carry the previous non-empty category forward for subsequent rows instead of treating blank continuation rows as uncategorized.
- Do not classify or learn testcase intent primarily from item numbers/order (`項次`, `2-1`, etc.); numbering may differ across projects. Infer intent from the test plan's functional description, expected behavior, and any DUT/test-environment context available.
- When referring to testcase items in analysis or discussion, always include the mode/context prefix (for example `單電源2-1`, `雙電源2-1`, `電壓跟隨2-1`) instead of a bare item number, because different workbooks can reuse the same item codes.
- Do not treat mode/PDO matrices as flat testcase tables without defining expansion rules.
- Do not damage original workbooks by renaming extensions, rezipping, or rewriting files.
- Do not skip cross-team tracking columns (`owner`, `due date`, `pattern ready`, `TIM`, `issue`, `status`) when they may matter to TENJI intake.

# Verification
Before finalizing, verify that:

- sheet count and names match workbook metadata
- sample rows actually come from the reported sheets
- direct-map vs special-case classification is justified by observed headers/content
- the report clearly distinguishes structure understanding from actual TENJI conversion

# Reuse notes
This skill is reusable for charger / protocol IC verification workbooks where a single Excel file mixes:

- SA testcase definitions
- electrical/timing specs
- protocol coverage
- mode matrices
- cross-team verification tracking

---
