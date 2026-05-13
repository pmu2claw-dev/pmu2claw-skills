# JD6628H single-power combined delivery reference

## Scope
Validated combined direct-delivery workbook for `單電源2-1 ~ 2-79` on this host.

## Output
- combined workbook: `/home/user/workspace-tenji/deliveries/JD6628H_SinglePwr_2-1_to_2-79_TenjiV2.2_R0.1_deliver.xlsm`
- verification summary: `/home/user/workspace-tenji/verification/singlepwr_2_1_to_79_combined/build_summary.json`
- LibreOffice probe: `/home/user/workspace-tenji/verification/singlepwr_2_1_to_79_combined/lo/JD6628H_SinglePwr_2-1_to_2-79_TenjiV2.2_R0.1_deliver.xlsx`

## Verified segment map
- `2-1~2-9` -> copied from split-row workbook `JD6628H_SinglePwr_2-1_to_2-9_SplitRows_TenjiV2.2_R0.2.xlsm`
- `2-10~2-18` -> copied from split-row workbook `JD6628H_SinglePwr_2-10_to_2-18_SplitRows_TenjiV2.2_R0.1.xlsm`
- `2-19~2-24` -> rebuilt as one 3-row `C1 -> A -> A detach` family using exact ANS donors `2-19` and `2-24` plus SA-plan `Request PDO` semantics for the intermediate cases
- `2-25~2-30` -> copied from validated family workbook `JD6628H_SinglePwr_2-25_to_2-30_C2A_TenjiV2.2_R0.5_ANSstyle_deliver.xlsm`
- `2-31~2-36` -> copied from validated family workbook `JD6628H_SinglePwr_2-31_to_2-36_A_C1_TenjiV2.2_R0.1_deliver.xlsm`
- `2-37~2-42` -> copied from validated family workbook `JD6628H_SinglePwr_2-37_to_2-42_A_C2_TenjiV2.2_R0.1_deliver.xlsm`
- `2-43~2-60` -> copied from validated family workbook `JD6628H_SinglePwr_2-43_to_2-60_C1C2A_TenjiV2.2_R0.1_ANSstyle_deliver.xlsm`
- `2-61~2-79` -> copied from validated family workbook `JD6628H_SinglePwr_2-61_to_2-96_TenjiV2.2_R0.1_ANSstyle_deliver.xlsm`, but only rows covering `2-61~2-79`

## Assembly shape
- package shell: mother template `CASE_2026-04-01_JD6628H_BM2922AA_JD6628H_TenjiV2.2_R0.1.xlsm`
- total body rows: `274`
- final tail row: `277`
- final case count: `79`
- first case: `2-1`
- last case: `2-79`
- row-shape mix is intentional:
  - split-row surface for `2-1~2-18`
  - 3-row ANS families for `2-19~2-42`
  - 4-row ANS families for `2-43~2-79`

## Verification facts
- base SHA-256: `7af155d861404bf06bd013dc2558a53ea3724dfe96a5862f18449c0a77da99f1`
- output SHA-256: `2dde885c207f35960c354b9ea7c84920984e3d49cefbd0c144228d4a3aed5a64`
- base `xl/vbaProject.bin` SHA-256: `0bb4cd496cb53c9afac10379826f9ca2902f2d9c580b6afb79ebcea46f8db0ae`
- output `xl/vbaProject.bin` SHA-256: `0bb4cd496cb53c9afac10379826f9ca2902f2d9c580b6afb79ebcea46f8db0ae`
- VBA preserved: `true`
- merged-range count: `61`
- LibreOffice conversion: success (`exit_code=0`)

## Delivery behavior learned
When the user asks for a big contiguous range like `直接做一份 單電源2-1~2-79的給我`, do not pause to over-explain the assembly plan. Build, verify, then hand back:
1. the concrete `.xlsm` path
2. the verification-summary path
3. the attachment line (`MEDIA:`) if the interface supports it

## Pitfalls
- Do not normalize all families to one row shape in a direct deliverable; preserve validated donor surfaces.
- Do not accidentally include `2-80~2-96` when slicing from the `2-61~2-96` family workbook.
- Split-row workbooks for `2-1~2-18` may not put the case token at the start of each row description; when assembling a combined workbook, prepend the case token to the first row of each 3-row block so downstream scans can recover `2-x` coverage cleanly.
- Keep only one final `OS_test2` row at the end of the combined workbook.
