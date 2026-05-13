# Sheet classification model
Classify each source sheet into one of these groups.

## 1. Direct testcase sheets
Typical headers:
- `No.`
- `功能` / `Function`
- `測試項目` / `Test Item`
- `測試方法`
- `預期結果/規格`
- `驗證方法`

Examples from charger/protocol projects:
- `FBO`
- `Discharge`
- `NTC`
- `OCP`
- `OTP`
- `OVP`
- `PD`
- `QC`
- `SCP`
- `UFCS`

These usually map mostly into TENJI `Test Note`.

## 2. Spec-driven sheets
Typical headers:
- `Function`
- `Test Item`
- `Symbol`
- `Test Condition`
- `Specification`
- `min/typ/max/unit`

Examples:
- `EC_Test`
- `Timing`

These also map into `Test Note`, but are better treated as spec-centric entries because TENJI can absorb numeric bounds into `Min/Typ/Max/Unit` columns.

## 3. Scenario / mode matrix sheets
Typical headers:
- `類別`
- `測試功能`
- `測試方式`
- `預期結果`
- `Send SRC Cap`
- `Target voltage`
- `Gate ON`
- `Request PDO`
- `Protocol`
- `驗證方法`
- `sim`

Examples:
- `單電源模式`
- `雙電源模式`
- `電壓跟隨模式`
- `智能盲插模式`

In JD6628H-style SA plans, these four mode sheets can share one canonical scenario schema at the same header row (for example row 14), with repeated item numbers reused across modes. When that happens, treat them as one scenario-family set with different behavioral semantics, not as interchangeable flat testcase sheets.

These are NOT row-to-row imports. A single scenario row often becomes multiple TENJI `Test Note` rows, usually one per logical step or state transition.

### JD6628H mode-family interpretation cues
Do not reuse one mode's reasoning model for another just because the columns look identical.

- `單電源模式`: usually model primary-port boost -> secondary/tertiary join -> shared `5V` or later recovery, with measurement following the validation target of each step.
- `雙電源模式`: first decide whether the prose describes independent coexistence or interaction/fallback. Do not force single-power `shared 5V` logic onto a case whose expected result says both ports keep `9V` independently.
- `電壓跟隨模式`: treat the follower port as constrained by the currently leading/primary port's negotiated voltage. Do not casually relabel these rows as ordinary dual-power cases.
- `智能盲插模式`: track primary/secondary role transitions explicitly. A single insertion event can contain an intermediate fallback/shared state before a later boosted target, so avoid collapsing that into one steady-state row if the answer logic shows multiple observable transitions.

## 4. Summary / tracker / execution-only sheets
Examples:
- `Summary`
- sheets dominated by owner/due date/status formulas
- pure compatibility trackers or execution dashboards

Usually do not map into TENJI core content, except possibly traceability notes.

# TENJI Test Note field mapping
Typical `Test Note` columns in the mother template:
- `B Bin`
- `C Test Item`
- `D Symbol`
- `E PWR Sequence`
- `F Pseudo code`
- `G RunPattern Pattern / Wait`
- `H Measure Condition`
- `I Description`
- `J/K/L/M = Min/Typ/Max/Unit`
- `N 備註`

Use this mapping logic.

## Direct testcase sheets -> Test Note
Map as follows:
- source function/category -> `B Bin`
- source `測試項目` / `Test Item` -> `C Test Item`
- source `Symbol` if present, else generate a stable symbol -> `D Symbol`
- source power/mode identifier if explicit -> `E PWR Sequence`
- source pseudo/register flow if explicit -> `F Pseudo code`
- source pattern name/path if explicit -> `G RunPattern`
- source `測試方法` / `Test Condition` -> `H Measure Condition`
- source `預期結果/規格` -> `I Description`
- parsed numeric limits -> `J/K/L/M`
- source sheet, row, verification method, protocol/mode metadata, unresolved assumptions -> `N 備註`

## Spec-driven sheets -> Test Note
For `EC_Test` / `Timing` style rows:
- `Function` -> `B Bin`
- `Test Item` -> `C Test Item`
- `Symbol` -> `D Symbol`
- `Test Condition` -> `H Measure Condition`
- `min/typ/max/unit` -> `J/K/L/M`
- verification/tracker info -> `N 備註`

This is usually the cleanest one-row-to-one-note case.

## Scenario / mode sheets -> expanded Test Note rows
A single scenario row should be split into multiple TENJI notes when the source contains multi-step behavior such as:
- attach one port
- attach second port
- voltage transition
- detach one port
- cleanup/reset

Recommended pattern:
1. split `測試方式` into ordered steps
2. extract the ordered event roles first: who is inserted first, who is inserted second, who is detached, and which port remains the primary observed port
3. align each step with the corresponding expected result fragment from `預期結果`
4. create one TENJI note per meaningful observable state transition
5. keep shared metadata (protocol, gate, request PDO, target voltage, source-cap preset) in `備註`
6. generate stable `Symbol` names reflecting scenario + step

Additional proven rules from JD6628H single-power cases:
- When the user provides a known-good answer workbook for a nearby case, reverse-engineer the populated `Test Note` rows first before generating a new case. In practice, rows 3–5 often encode a three-stage scenario pattern: row 3 = primary port attach / initial boost, row 4 = secondary participant attach / shared-5V transition, row 5 = secondary detach / primary recovery plus cleanup.
- Prevention gate: before generating any new mode-family case, explicitly search for exact-case and nearby answer workbooks and record which one is the primary lineage reference. If an exact or near-family answer workbook exists, do not start from a prose/scenario generator surface.
- Prevention gate: lock the output surface before writing rows. Record the expected workbook family name (for example `Single_power2` / `Single_power3`), row-count pattern, symbol naming pattern, and command vocabulary (`ForceV`, `UR`, `PD_command`, `MeasV`, `JudgeV` vs. abstract `Source Step`, `Target voltage`, `Gate ON`). If the generated draft uses a different surface than the chosen reference, stop and rebuild from the reference shape instead of patching prose.
- Prevention gate: treat exact-case answer workbooks as mother templates for neighboring cases in the same family. Only substitute the truly variable parts (ports, PDO requests, voltage windows, mirrored UR / attach nodes, measured node by step intent); preserve the validated wrapper rows, family naming, and control-script skeleton.
- Prevention gate: add a final lineage review before delivery. Compare at least one generated testcase against the chosen answer workbook and verify: (1) same row granularity, (2) same style family, (3) same naming grammar, (4) same control-language level, and (5) only expected semantic deltas. If the diff reads like "generator summary" vs "ATE script", the case is not ready to deliver.
- Use mirrored answer pairs to isolate port-role semantics before writing a new case. For example, comparing `單電源2-1` (C1-first) against `單電源2-10` (C2-first) reveals that the TENJI structure stays stage-aligned while only the port-specific attach nodes, UR controls, measured VBUS node, and symbol naming mirror between C1 and C2.
- Do not group mixed-port scenarios only by port set (`C + A`, `A + C1`, etc.). Classify them by ordered role semantics: primary port established first, secondary participant inserted later, recovery after secondary detach.
- The measured node usually follows the primary observed port, not simply the most recently attached port.
- When the secondary participant is an A-port in JD6628H-style environments, its attach/load behavior is represented through `VBUSC_A`-style power nodes plus `DP_A/DM_A` negotiation rather than the Type-C attach model (`vatachX + UR_k(CC)`).
- In A-primary recovery cases, do not assume that secondary detach alone proves recovery. The TENJI answer may replay the A-port `DP_A/DM_A` negotiation sequence after detach and only then measure whether `VBUSC_A` returns to the boosted target.
- When mirroring a scenario from `C1` to `C2`, do not only swap attach/CC nodes; also inspect VBUS routing / bridge controls (for example `UR_k7`) because the TENJI answer may require extra path setup that is not explicit in testcase prose.
- In three-participant single-power scenarios, choose the measured node by the validation target of the current step: when checking whether the original primary port was pulled down into shared 5V, keep measuring the primary; when checking whether a newly inserted Type-C participant successfully joined the shared 5V bus, switch measurement to that new participant's `VBUSC_*` node.
- After detaching the third participant, do not assume the remaining pair recovers to 9V. Follow the expected-result semantics: if the testcase says the surviving pair continues shared charging, keep the judge window at 5V and measure the surviving primary participant.
- `2-61` and `2-79` style rows form a strong C1/C2 mirror pattern: map `C1` <-> `C2`, `vatach1` <-> `vatach2`, `UR_k3` <-> `UR_k4`, and `VBUSC_C1` <-> `VBUSC_C2`, then verify whether the measurement target also mirrors based on step intent.
- In dual-power variants of that mirror family, do not assume the A-port step should be validated by re-measuring the original PD port. The TENJI answer may validate the A-port directly through `VBUSC_A` while the PD-side resource ownership stays on the C-port side.
- In dual-power C2-first / A-second / C1-third scenarios, the third participant can trigger an explicit port handoff such as `UR k4 OFF` -> `UR k3 ON`; treat that as a routing/control-state transition, not just a new attach event.
- For those dual-power handoff cases, use this measurement rule: first step measure the established primary PD port, second step may measure `VBUSC_A` directly for A-port validation, third step measure the newly inserted PD participant if the expected result says it becomes the boosted output, and after detach return measurement to the surviving primary PD pair.
- If the expected result after the final detach says the remaining pair continues shared charging, keep the judge window at 5V on the surviving PD port even if the removed participant had previously negotiated 9V.
- Some answer workbooks can contain a description/implementation mismatch in the final step (for example wording says "maintain 5V" but the scripted flow re-requests 9V and judges a 9V window). Treat this as an answer-template inconsistency to flag, not as a rule to generalize.
- A practical fast-delivery fallback was validated for the JD6628H `單電源2-1~2-9` C1-first / C2-join family when exact `UR` / `PD_command` reconstruction is still incomplete: expand each source item into the three measurable voltage states only — `(1) primary attach / initial boost`, `(2) secondary attach / shared 5V`, `(3) secondary detach / primary recovery` — and defer the final physical cleanup detach step if it is not needed for the first inspectable workbook.
- For that fast-delivery fallback, populate the TENJI mother template directly with `openpyxl` by copying the mother template to a new `.xlsm`, clearing only `Test Note` values, preserving styles, and writing columns `B:N` row-by-row. This gives a usable workbook faster than trying to force incomplete logic through a prose-oriented generator.
- Important `openpyxl` worksheet-editing pitfall from the JD6628H workbook writer: do not blanket-clear a `Test Note` rectangle with `ws.cell(r, c).value = None` before checking merges. Existing TENJI templates can contain merged ranges, and non-anchor cells are `MergedCell` objects whose `.value` is read-only. A reusable safe pattern is:
  1. inspect `ws.merged_cells.ranges`
  2. build a set of merged child coordinates (all cells except each range's top-left anchor)
  3. when clearing/writing, skip those child coordinates
  4. if the body region will be fully rewritten, unmerge only the overlapping body ranges before final writes, or restrict writes to anchor cells only
  5. after generation, reopen the workbook and verify the intended `Test Note` rows rather than assuming the clear/write pass succeeded
- For the same JD6628H `單電源2-1~2-9` family, a practice-like full-flow reconstruction rule is now confirmed: use the source sheet's `Request PDO` column as the authoritative PD-request sequence, not the `SINK_12V/20V` capability text in the action column. In these rows, step 1 requests the primary boosted PDO (`PDO2/3/5` => `9/12/20V`), step 2 drops to shared `PDO1`/`5V` when C2 joins, and step 3 re-requests the original primary PDO after C2 detaches. A reusable TENJI skeleton is: `ForceV VIN` -> `ForceV vatach1` -> `UR k3 ON` -> `PD_INIT` -> `PD_req<primary>` -> judge C1 boosted / C2 absent -> `ForceV vatach2` -> `UR k4 ON` -> `PD_INIT` -> `PD_req5v` -> judge both at 5V -> `ForceV vatach2 0V` -> `UR k4 OFF` -> `PD_INIT` -> `PD_req<primary>` -> judge C1 recovered / C2 absent.
- User-corrected structural rule for TENJI conversion: each verifiable step / judge must occupy its own `Test Note` row and align to exactly one SPEC / Description fragment. Do not compress an entire multi-transition testcase into one row just because the flow can be expressed in one multiline TENJI block. For `單電源2-1~2-9`, the reliable split is one row each for `(1) primary-only boost`, `(2) shared-5V after secondary attach`, `(3) primary recovery after secondary detach`.
- User-corrected workbook-level rule: `OS_test` belongs at the whole TENJI workbook head and tail only. Do not insert `OS_test` around each testcase or around each split step.
- Current learned packaging rule for this workflow: workbook structure should be `OS_test` at the beginning -> all testcase rows in sequence -> `OS_test` at the end. The inner testcase body is still split row-by-row by observable state transition, but `OS_test` itself is only workbook-scoped.
- Current learned caution: do not misread workbook-level `OS_test` as evidence that each testcase needs local pre-check / post-check rows. Separate testcase splitting rules from workbook wrapper rules.
- User-corrected multi-case assembly rule: for multi-case TENJI delivery, first convert each testcase as an independent single-case with its own validated row body, then assemble the final workbook by placing those single-case bodies sequentially into one `Test Note` surface and adding only workbook-level head `OS_test` and tail `OS_test2`. Do not infer multi-case row shapes directly from a family block when a more reliable single-case conversion path exists.
- Repair rule validated on JD6628H `單電源2-1~2-9` split-row output: when rebuilding from the mother template, explicitly rewrite workbook row 2 as head `OS_test`, write all testcase body rows after it, then append tail `OS_test2` immediately after the last testcase row. Do not rely on a bulk clear + body rewrite pass to preserve those wrapper rows automatically.
- SPEC fill rule validated on the same family: for per-step voltage-validation rows, populate `J/K/L/M` as `Min/Typ/Max/Unit = (=K<row>*0.8, target_voltage, =K<row>*1.2, V)`, where `target_voltage` is the step's actual judged target (`5/9/12/20`) derived from the per-step Request-PDO/result mapping. A structurally correct workbook is still incomplete if split rows have Description and Measure Condition but leave `SPEC` blank.
- Style-preservation rule from the repair pass: copy the mother-template or known-good answer style row that matches the semantic row type instead of reusing one style for every output row. In the validated JD6628H template/reference set, row 2 is the workbook-head `OS_test` wrapper style, rows 3/4/5 provide the three body-row styles for `(1) primary-only boost`, `(2) shared-5V`, `(3) recovery`, and row 6 is a usable workbook-tail `OS_test2` wrapper style. When regenerating a family workbook quickly, assign styles by semantic row type first, then verify representative first/last rows after save.
- Border/frame fidelity rule learned from `單電源空載插拔測試 C2+C1 2-10~2-18`: do **not** copy `_style` wholesale from an intermediate reviewed `.xlsx` unless you have confirmed that workbook still carries the TENJI mother-template borders. A reviewed/helper `.xlsx` can have correct cell values but flattened styles (`style_id` nearly uniform, no merged header/body frame, no double-line borders). Safe fast path: copy only cell values from the helper workbook, and source styles from the mother template or a known-good `.xlsm` answer workbook by semantic row type. Before delivery, explicitly inspect representative cells such as `B2/C2/N2`, `B3/C3/N3`, and the tail row to confirm the expected double-border frame is still present.
- Border-fidelity repair rule validated on `單電源 C2+C1 2-10~2-18`: if you are rebuilding a final `.xlsm` from an intermediate/reviewed `.xlsx`, do **not** copy `_style` from that `.xlsx` unless you have explicitly verified that its borders and TENJI frame formatting are intact. A reviewed helper `.xlsx` can contain correct cell values but almost no real TENJI formatting (for example `style_id=2` everywhere and no frame borders). Copying those styles into the `.xlsm` will wipe the mother-template frame. Safe pattern: `(1)` clear target values, `(2)` apply semantic row styles from the mother template or a known-good `.xlsm` reference row set, `(3)` copy only cell values from the reviewed `.xlsx`, `(4)` reopen and inspect representative border cells such as `B2/C2/N2`, `B3/C3/N3`, and the tail row after save, and `(5)` optionally run a headless Office import/export probe to confirm the borders still render.
- For regeneration-speed work on this JD6628H workflow, benchmark the current generator path before redesigning it. A reliable probe is `/usr/bin/time -p /usr/bin/python3 <generator>.py`, because this environment has repeatedly shown that `execute_code` and the default `python3` may not have `openpyxl` while `/usr/bin/python3` does.
- When the user asks for "快" regeneration, separate three costs instead of treating them as one problem: `(1) finding the right source/answer/version`, `(2) generating row specs`, and `(3) writing the `.xlsm``. In practice, repeated repo-wide searching/version comparison can dominate perceived latency more than the actual workbook write.
- For single-case requests (for example `單電源2-1` only), prefer a case-level fast path over family-wide reruns: resolve one mode-qualified case, derive its observable-state row spec, validate that spec, then write the workbook. This is usually a better optimization target than re-running a broader `2-1~2-9` generator or repeating document searches.
- In that first-pass workbook, it is acceptable to place the TENJI DSL only in `Measure Condition` while leaving `Pseudo code` blank, provided the row is clearly traceable and not mislabeled as final logic. A proven minimal pattern is:
  - `ForceV VBUS1 <typ> 100m`
  - `MeasV VBUS1 <low> <high> V_<case>_s<step>`
  - `JudgeV VBUS1 <judge_min> <judge_max>`
- For the same family, a stable first-pass row mapping is:
  - `Test Item` = `SinglePwr_C1C2`
  - `Symbol` = `SP_<case>_S1`, `SP_<case>_S2`, `SP_<case>_S3`
  - `PWR Sequence` = `PWR_VBUS`
  - `RunPattern/Wait` = blank for step 1, `Wait 5s` for later steps when the source says so
  - `Description` = expected-result fragment aligned to each step
  - `備註` = source row/item + category/function/verify/sim/owner/due traceability
- Label this output as a first-pass TENJI workbook, not a full final answer, because it restores machine-readable TENJI-style measurement content quickly while the exact attach / negotiation / routing actions (`UR`, `PD_INIT`, `PD_req*`) are still being reverse-engineered.

Example naming pattern:
- `SP_2_1_C1_ONLY_9V`
- `SP_2_1_C1_C2_SHARE_5V`
- `SP_2_1_C1_RECOVER_9V`

# Mother-template supporting sheets
## PinMap
Read the mother template's existing `PinMap` first and prefer its existing pin names. Do not invent renamed nets if the workbook/netlist already aligns with template pins.

## Power sequence
If source rows imply power setup (e.g. VBUS-oriented tests) but do not define full reusable sequences, reference an existing generic sequence like `PWR_VBUS` only when justified. Otherwise leave for later authoring.

## Pattern
Only populate if the source workbook truly provides pattern names or file references. Many SA plans do not; leave blank rather than inventing fake paths.

## PseudoCode
Only populate when there is reusable structured content (register writes, protocol commands, primitive operations). Plain prose test steps usually belong in `Measure Condition`, not the `PseudoCode` library.

# Traceability rules
Always preserve enough source provenance to audit the conversion later. Put these into remarks when needed:
- source workbook sheet name
- source row number
- protocol / gate / request PDO / target-voltage metadata
- whether the item was direct-mapped or step-expanded
- any manual assumptions or unresolved ambiguities

# Writing-output fallback when Python Excel libraries are unavailable
If you must deliver a filled `.xlsm` but `openpyxl` or equivalent Excel libraries are unavailable, use this OOXML-safe fallback:

1. copy the mother-template `.xlsm` to a new output path first
2. open the copied file as a zip container
3. edit only the target worksheet XML (for example `xl/worksheets/sheet2.xml` for `Test Note`)
4. preserve the template workbook structure, macros, and untouched sheets exactly as-is
5. preserve existing row/cell style attributes from the template whenever possible
6. write new cell values using `inlineStr` text nodes to avoid rebuilding `sharedStrings.xml`
7. only overwrite the intended populated rows/cells, not the full workbook layout
8. after writing, re-read the produced workbook through OOXML parsing and verify the expected rows/cells

This fallback is especially useful for TENJI mother-template generation because it keeps VBA macros intact and avoids dependency on non-installed Python packages.

Practical notes from the JD6628H workflow:
- `Test Note` often lives in `xl/worksheets/sheet2.xml`, but always confirm via `workbook.xml` + `workbook.xml.rels` instead of hard-coding.
- A safe minimal write strategy is: keep the template file, populate only `A:N` values for the intended `Test Note` rows, and leave all other sheets untouched.
- If you need visual fidelity similar to a reference answer workbook, copy the source row heights into the output row attributes (`ht`, `customHeight`) while keeping the template's style IDs.
- Verify the generated output by re-reading the new `.xlsm` and checking the exact `Symbol`, `Measure Condition`, `Description`, and `Min/Typ/Max/Unit` fields.
- Treat workbook-content correctness and workbook-format preservation as two separate checks. A file can contain the right Test Note prose yet still be the wrong workbook package for Excel-visible fidelity.
- If the user first wants a correct workbook to inspect and a known-good answer/reference workbook already exists, it is acceptable to deliver a clearly labeled first-pass copy of that reference immediately, then continue reverse-engineering the generator/writer. In that case, verify the interim file by hash equality plus OOXML read-back of the key `Test Note` rows so the user gets a usable file before the final template-faithful writer is ready.
- When debugging a bad TENJI `.xlsm`, compare at least four artifacts if available: the mother template, a minimally filled template-copy output, the current generated output, and a known-good reference answer. This helps separate mapping mistakes from writer/serialization damage.
- During OOXML comparison, inspect not only cell values but also package-level signals: presence/count of `xl/sharedStrings.xml`, `styles.xml` counts (`cellXfs`, `fonts`, `fills`), worksheet `dimension`, row attributes like `ht` / `customHeight` / `spans`, and whether text cells are emitted as shared strings or `inlineStr`.
- Formula-bearing regions need an extra integrity check: compare worksheet cells, their `<f>` nodes, and `xl/calcChain.xml` together. In one JD6628H `.xlsm` failure, direct XML editing replaced shared-formula cells (`J3:J5`, `L3:L5`) with plain numeric `<v>` values but left the old calcChain entries intact. Excel/Office tools could still see a calculation chain for cells that no longer had formulas, producing a "file has problems / repair" style failure. When editing a TENJI workbook directly, either preserve the original shared-formula structure (for example `t="shared"`, `si`, `ref`) or update/remove the calcChain consistently.
- `openpyxl.load_workbook(..., keep_vba=True)` plus `wb.save(...)` can preserve `vbaProject.bin` yet still rewrite the workbook package substantially: sharedStrings may disappear in favor of `inlineStr`, style IDs may be reindexed, dimensions may change, and row metadata may be regenerated. Do not treat `keep_vba=True` as a guarantee of mother-template fidelity.
- A practical verification combo for generated TENJI `.xlsm` files is: (1) OOXML read-back of the intended `Test Note` cells, (2) confirm formula cells still load as formulas in `openpyxl` rather than downgraded numeric literals, and (3) run a headless Office import/export probe such as `libreoffice --headless --convert-to xlsx ...` to catch package-level corruption before delivery.
- Another JD6628H-specific failure mode is harsher: a hand-edited OOXML workbook can parse correctly and show populated `sheet2.xml` / `Test Note` cells in tool-based read-back, yet Excel/WPS still renders the `Test Note` sheet as visually blank. Treat programmatic OOXML verification and actual Office UI visibility as separate gates. If this happens, stop using direct zip/XML patching for final delivery and rebuild/save from a known-good workbook through `openpyxl.load_workbook(..., keep_vba=True)` followed by `wb.save(...)`, then re-open and, when possible, pass the file through a headless Office loader/converter before sending.
- In the current OpenClaw JSON -> TENJI pipeline, continuation rows cannot be represented by a sentinel like `"__blank__"` in `test_item`: `spec_normalizer._normalize_test_item()` derives `name = raw.name or raw.test_item or TestItem_i` and then sets `test_item = raw.test_item or name`, so that sentinel is written literally into column C. If the answer workbook expects visually blank continuation rows, plan for a writer/normalizer fix or a post-write edit instead of assuming the spec pipeline will preserve a blank-looking placeholder.
- Another practical packaging caution from the JD6628H `.xlsm` generate path: `openpyxl` may emit warnings like `wmf image format is not supported so the image is being dropped` when loading a macro-enabled TENJI template. Treat this as a workbook-fidelity warning, not proof that testcase content is wrong. If the output is otherwise correct, add an extra delivery check: reopen the saved `.xlsm`, compare `xl/vbaProject.bin` hash to the template, and run a headless Office import/export probe so image/object loss or package damage is caught before delivery.
- A high-signal verification stack for fast TENJI `.xlsm` delivery is now: `(1)` save from `openpyxl.load_workbook(..., keep_vba=True)`, `(2)` reopen and audit representative `Test Note` rows, `(3)` compare `xl/vbaProject.bin` SHA-256 with the template, `(4)` run `libreoffice --headless --convert-to xlsx ...` and inspect the converted `Test Note` rows. This catches logic mistakes, macro loss, and many package-level fidelity issues before sending.
- Direct-extraction pitfall from the validated `單電源2-25~2-30 C2+A` delivery path: if you copy populated `Test Note` rows from a golden workbook into a new workbook at different row numbers, rewrite any row-local formulas that reference the same-row judge cell. Example: moving a source row with `=K99*0.8` into destination row `3` must become `=K3*0.8`; otherwise Min/Max formulas silently keep pointing at the old source-row `K` cell.
- Another extraction pitfall: do not use one already-mutated output sheet as the donor for template wrapper rows. Load the mother template twice when scripting subset workbooks — one pristine workbook/sheet as the donor for header/footer rows, and a separate output workbook copy to clear and populate. Otherwise a prior clear/copy pass can duplicate stale testcase rows or lose the intended wrapper row content.
- For JD6628H-style subset deliveries where you have both `(a)` an exact-case validated answer workbook and `(b)` a larger populated golden/reference workbook, use a split donor strategy instead of forcing everything from one file: copy workbook wrapper rows (`OS_test` head / `OS_test2` tail) from the exact answer workbook, but copy the testcase body rows from the larger golden/reference block. This preserves the exact workbook-family wrapper surface while still letting you extract a wider testcase range from the populated reference lineage.
- In that split-donor extraction, keep header row 1 from the pristine template/reference surface, map the golden body rows into the new destination rows, and rewrite any row-local formulas so they point at the new row numbers (for example `=K99*0.8` -> `=K3*0.8`).
- After building the subset workbook, run a full donor-alignment audit rather than checking only representative rows: compare wrapper rows cell-by-cell against the answer workbook and compare each copied body row cell-by-cell against the golden/reference source (with expected formula row remap). Treat `mismatch_count 0` as the release gate for the extraction step.
- If the target `Test Note` body overlaps merged ranges, unmerge only the overlapping body ranges before clearing/writing that region. This avoids `MergedCell` write failures and also reduces the chance of stale merged artifacts surviving under the copied subset rows.
- After extracting a subset workbook, explicitly clear trailing body rows beyond the copied testcase block. Reopening only the apparent first rows can miss leftover template/sample rows still present below the delivered family.
- Exact front-subset extraction workflow validated for JD6628H `單電源2-25~2-26` on this host: when no dedicated `*2-25*2-26*.xlsm` exists but a validated family workbook `JD6628H_SinglePwr_2-25_to_2-30_C2A_*.xlsm` does, the fastest safe delivery path is to clone that family workbook, keep rows `2:10` (`OS_test` + `2-25 S1~S4` + `2-26 S1~S4`), copy the existing tail wrapper row (`OS_test2`, originally row `27`) to the new tail row (`11`) with styles and row-dimension metadata preserved, then clear `B:N` for rows `12+`. Save through `openpyxl.load_workbook(..., keep_vba=True)` and verify four gates: `(1)` reopened `Test Note` shows rows `2:11` exactly as intended, `(2)` `vbaProject.bin` SHA-256 still matches the mother template, `(3)` LibreOffice headless converts the new `.xlsm` to `.xlsx`, and `(4)` the converted workbook reads back the same `Test Note` rows. This is a reusable pattern for contiguous-front subset deliveries from a validated family workbook.
- Exact two-case assembly workflow also validated for JD6628H `單電源2-25~2-26` when the only trustworthy lineage is the single-case answer workbooks and a previously delivered family/subset workbook is discovered to be prose-style or otherwise from the wrong surface. Safe rebuild path: start from the exact `2-25` answer workbook as the package/style/macro base, insert three rows before its original tail wrapper, recreate merged testcase spans so the sheet has `C3:C5` for `2-25` and `C6:C8` for `2-26`, copy the `2-26` answer body rows `3:5` into destination rows `6:8`, move/copy the original `OS_test2` tail row to row `9`, and clear rows below the new tail to avoid stale artifacts. Critical details: `(1)` only write the merged-anchor cells for column C (`C3` and `C6`), not merged children, `(2)` rewrite row-local formulas when shifting the donor rows (`=K3*0.8` -> `=K6*0.8`, `=K4*0.8` -> `=K7*0.8`, etc.), `(3)` preserve styles from the exact donor cells rather than inventing new row surfaces, and `(4)` verify the rebuilt workbook by reopening `Test Note`, checking merged ranges, confirming `vbaProject.bin` hash still matches the single-case answers/template lineage, and running a headless LibreOffice `.xlsm` -> `.xlsx` conversion plus read-back. This is the preferred repair workflow when the user reports that a delivered multi-case workbook used prose placeholders like `SP_2_25_S1` instead of TENJI DSL and the correct lineage exists as exact single-case answer workbooks.

# Recommended implementation architecture: single-item pipeline scaffold
For reusable automation, prefer a four-stage pipeline instead of one monolithic generator.

## Stage 1: single-item conversion
Create one formal `item_spec.json` per mode-qualified testcase.
Recommended responsibilities:
- input: one testcase / one source-row scope
- resolve lineage first from exact-case or nearby validated answer workbooks
- normalize the testcase into explicit body rows with stable row order
- emit a durable JSON artifact rather than writing the workbook immediately

Useful starter fields:
- top level: `schema_version`, `created_at_utc`, `status`, `case_id`, `family`, `source`, `lineage`, `workbook_rules`, `merge_rules`, `body_rows`
- per body row: `row_index_within_case`, `symbol`, `test_item_anchor`, `pwr_sequence`, `pseudo_code`, `run_pattern_wait`, `measure_condition`, `description`, `min_formula`, `typ`, `max_formula`, `unit`, `remarks`, `style_source`

Treat the single-item spec as the canonical intermediate artifact. Do not treat it as disposable scratch output.

## Stage 2: single-item validation
Run a dedicated validator before any workbook assembly.
Minimum gates:
- required top-level keys present
- required body-row keys present
- row indexes sequential from `1`
- symbols unique within the testcase
- at least one row anchors the merged `Test Item` cell
- `measure_condition` contains TENJI DSL tokens (`ForceV`, `ForceI`, `UR`, `PD_command`, `MeasV`, `JudgeV`, `Wait`) rather than prose-only markers such as `Source Step:` or `Target voltage:`
- `lineage.primary_references` is non-empty
- workbook wrapper policy remains workbook-scoped (`OS_test` head, `OS_test2` tail) rather than testcase-scoped

This validator should fail fast before touching the `.xlsm`.

## Stage 3: workbook assembly
The assembler should only do package/layout work:
- load the mother template or exact-case answer workbook as the workbook surface
- clear the target body region safely with merged-cell awareness
- write validated item specs sequentially
- merge the testcase `C` column span per testcase
- copy semantic row styles from `style_source` donor rows
- insert only workbook-level wrapper rows (`OS_test` head and `OS_test2` tail)

Important separation rule: the assembler must not do semantic inference. All testcase meaning should already be fixed in the single-item specs.

## Stage 4: workbook verification
Use a dedicated verifier after save.
Recommended checks:
- reopen with `openpyxl.load_workbook(..., keep_vba=True)`
- inspect visible `Test Note` rows and merged ranges
- compute file SHA-256 and `xl/vbaProject.bin` SHA-256
- run a LibreOffice headless `.xlsm` -> `.xlsx` probe and read back the converted `Test Note` rows

## Minimal file/module split that worked well
A reusable scaffold for this pipeline is:
- `common.py` — JSON helpers, hash helpers, VBA hash, LibreOffice probe, cell/style copy helpers
- `schema.py` — DSL token list, prose-marker list, item-spec factory
- `convert_single_item.py` — builds one starter or final item spec
- `validate_single_item.py` — enforces single-item gates
- `assemble_workbook.py` — combines validated specs into one workbook
- `verify_workbook.py` — performs post-save verification

This architecture is preferred when the user wants a "single-case first, then assemble multi-case workbook" workflow and when wrong multi-case outputs must be quarantined rather than patched in place.

# Verification checklist
Before finalizing mapping results, verify that:
- source sheet classification is justified by observed headers/content
- spec sheets really populate min/typ/max/unit correctly
- scenario sheets were expanded instead of flattened
- generated symbols are stable and human-readable
- traceability back to source sheet/row is preserved
- no unsupported pattern/pseudocode fields were fabricated

# Review-artifact bundle for scenario-family mappings
When a mode/scenario family is being reviewed in stages (for example JD6628H B-line `雙電源模式` / `電壓跟隨模式` / `智能盲插模式`), produce a small artifact bundle before calling the work complete.

## Recommended artifact set
1. `*_MAPPING_COMPLIANCE.md`
   - mode-specific semantic rules
   - row-splitting rules
   - known open points / anomalies
2. `*_ROW_DRAFT.json`
   - one object per intended TENJI row
   - include mode-qualified testcase, source row, symbol, description fragment, target voltage fragment, request PDO fragment, suggested measured node, judge band, and per-row status
3. `*_ROW_DRAFT.md`
   - human-review table grouped by mode and testcase
4. `*_REVIEW_CHECKLIST.md`
   - traceability checks
   - row-splitting checks
   - mother-template column-alignment checks
   - negotiation / voltage correctness checks
   - manual-review hotspots
5. `*_STATUS_CLOSEOUT.md`
   - explicit decision: `final complete` vs `core mapping complete / pending sign-off`
   - counts of draft-ready vs needs-manual-review rows
   - exact blockers preventing final close

## Row-draft status discipline
For scenario-family reviews, mark each expanded row with an explicit delivery status.
Useful minimal statuses:
- `draft-ready`: row split, target fragment, judge target, and traceability are ready for review
- `needs_manual_review`: answer-workbook evidence, anomaly resolution, or measured-node inference is still unresolved

Do not silently leave uncertain rows looking complete. If a role-transfer or control-path inference still depends on answer-workbook reading, mark that row `needs_manual_review`.

## Closeout decision rule
Do not label the scenario-family mapping `final complete` merely because most rows are drafted.
A safe reusable status ladder is:
- `core mapping complete`
- `row-draft complete`
- `pending final sign-off`
- `final complete`

Only use `final complete` when all of the following are true:
- mode-aware references are complete
- every observable expected-result fragment has its own row
- manual-review anomalies have been explained or corrected
- any answer-workbook-dependent measured node / control-path inference is confirmed
- if the deliverable is a final workbook, draft `measure_condition_strategy` content has been upgraded into final TENJI DSL
- the review checklist has been signed off

# Hard-gate SOP for TENJI Excel conversion
Use this as a mandatory pre-delivery gate. If any item fails, do not present the workbook as final.

## 1. Pre-conversion mapping spec
Before writing the workbook, create a per-testcase mapping table that records:
- mode-qualified testcase name (for example `單電源2-8`, not bare `2-8`)
- source sheet name and row number
- expected-result fragments split into observable steps
- `Request PDO` sequence and mapped voltages (`PDO1=5V`, `PDO2=9V`, `PDO3=12V`, `PDO5=20V` unless the source says otherwise)
- intended TENJI row count for the testcase
- one target judge/description pair per row
- workbook-level wrappers required (`OS_test` head/tail when applicable)

## 2. Separate workbook-level vs testcase-level rules
Never mix these layers.
- Workbook-level rules: package wrappers such as `OS_test` at the overall workbook head and tail.
- Testcase-level rules: row splitting, symbols, attach/detach flow, judge targets, and per-step descriptions.
A testcase split that looks correct is still incomplete if the workbook wrapper rule is missing.

## 3. Row-template discipline
Use testcase semantics and distinct SPEC/judge obligations to decide row count before generation.

Process:
- decompose the testcase into observable expected-result fragments
- identify which fragments require independent judge/SPEC evaluation
- assign at least one TENJI row to each distinct verification obligation
- treat learned family patterns only as priors/review aids, not fixed row-count templates

Example: a family such as JD6628H `單電源2-1~2-9` often lands on three rows (`primary-only boost`, `shared 5V after secondary join`, `primary recovery after secondary detach`), but that is valid because the testcase semantics produce three distinct verification obligations — not because the family must always be three rows.

Then enforce these per row:
- exactly one observable state transition or tightly coupled verification obligation
- exactly one aligned Description / SPEC fragment
- exactly one judge intent
- stable, human-readable symbol naming

Do not compress multiple transitions into one row even if the TENJI DSL fits in one multiline block, and do not force a testcase into a fixed family row count when the parsed SPEC/judge obligations imply more or fewer rows.

## 4. PDO mapping gate
Derive PD requests from the source `Request PDO` column, not from shorthand capability text in action prose.
Record the voltage mapping explicitly in the conversion notes and verify that each generated TENJI row requests the intended PDO for that step.

## 5. Packaging gate
Before delivery, verify workbook packaging separately from testcase logic:
- workbook opens successfully as `.xlsm`
- workbook head contains `OS_test` when the workflow requires it
- workbook tail contains `OS_test` when the workflow requires it
- testcase rows appear between those wrappers in the intended order
- do not treat row-count / sheet-count / revision-history checks as sufficient; packaging is still wrong if wrapper rows were cleared by the rewrite pass

## 5b. Content-completeness gate
Before calling a TENJI workbook final, run an explicit cell-content audit in addition to structural checks:
- every body row has non-empty `J/K/L/M` when that testcase step is a voltage/spec-validation row
- workbook wrapper rows (`OS_test` / `OS_test2`) still exist at the intended head/tail rows after generation
- `Description`, `Measure Condition`, and `SPEC` are all checked together on representative first/last testcase rows, not just one of them
- never mark verification complete based only on `.xlsm` readability, row counts, or revision-history updates
- if the workbook is split-row output, confirm that each generated row still aligns to exactly one Description fragment and one SPEC fragment after the final save/reopen pass


## 6. Traceability gate
Every generated row should still be auditable back to source context. Preserve enough information in remarks/description to recover:
- source sheet / row
- mode-qualified testcase name
- step number or observable state
- key metadata such as protocol / request PDO / target voltage

## 7. Delivery labeling gate
If the workbook still lacks pieces allowed only in interim output (for example `Pseudo code` intentionally blank, workbook wrapper not yet inserted, or row logic still being mirrored from a nearby answer), label it explicitly as `first-pass` or `intermediate`, not final.
Only call it final after workbook-level and testcase-level gates both pass.

## 8. Final release checklist
Minimum pass set before calling the workbook final:
- `.xlsm` opens successfully
- source scenario understood before conversion
- mode-qualified testcase naming used
- every expected-result fragment mapped to its own row
- no multi-judge / multi-step compression into one row
- `Request PDO` mapping verified
- TENJI DSL present (not prose-only)
- workbook-level `OS_test` head/tail rule satisfied when applicable
- traceability preserved
- output status honestly labeled as first-pass vs final
- semantic correctness and golden-surface correctness both verified separately when a validated answer workbook exists
- row naming pattern matches the answer-workbook lineage rather than a generator placeholder pattern (for example not leaving `SP_<case>_S#` when the golden lineage is action-oriented)
- control/measurement vocabulary matches the golden lineage (for example `ForceV / ForceI / UR / PD_command / MeasV / JudgeV`) instead of stopping at prose blocks like `Source Step / Gate ON / Target voltage`
- if a delivered workbook is reported wrong, compare it with the pre-delivery source workbook by full-file hash plus representative `Test Note` row dumps to determine whether the defect came from generation/mapping or only from later packaging/copy steps

# Pitfalls
- Do not flatten mode/scenario sheets into one TENJI row per source row.
- Do not treat owner/due-date/TIM tracker columns as core testcase content.
- Do not force pattern or pseudocode values when the source does not provide them.
- Do not destroy the original workbook or original TENJI mother template during parsing.
- Do not rename pins when the mother template already contains matching names.

# Recommended workflow
1. Inspect source workbook structure first.
2. Inspect TENJI mother-template sheet roles.
3. Classify source sheets into testcase/spec/scenario/tracker.
4. Draft explicit field mapping rules per class.
5. Pilot one representative row or scenario.
6. Verify the produced TENJI rows by reading them back from OOXML.
7. Only then scale to batch conversion.

# Reuse notes
This workflow is especially reusable for charger/protocol IC projects where one workbook mixes:
- PD/QC/SCP/UFCS protocol coverage
- electrical/timing spec validation
- power-mode scenario matrices
- TIM readiness / issue tracking
- shared pin naming already present in a TENJI mother template

---
