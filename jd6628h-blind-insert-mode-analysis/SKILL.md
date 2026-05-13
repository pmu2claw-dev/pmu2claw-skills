---
name: jd6628h-blind-insert-mode-analysis
description: Analyze JD6628H 智能盲插模式 SA-plan rows and answer workbooks to determine whether a case is a basic blind-insert scenario or a fallback/role-transfer family, with measured-node and control-path evidence preserved for TENJI mapping.
---

# When to use
Use this when the user is working on JD6628H `智能盲插模式` rows and wants to:

- decide how many TENJI `Test Note` rows a blind-insert testcase should expand into
- identify the real measured node for each observable state
- confirm control-path evidence from answer workbooks
- close anomalies before calling the mapping final

This skill is read-only analysis of source `.xlsx` plus answer `.xlsm` workbooks.

# Core principle
Do **not** treat every blind-insert row as a simple 3-row pattern.

First decide whether the testcase is:
1. a **basic blind-insert** case, or
2. a **fallback -> role-transfer -> recovery** case.

If the expected result contains an intermediate constrained / fallback state and then a later `轉主路` or boosted-target transition, it must not be flattened.

# Required parsing approach
Parse both source and answer workbooks read-only through OOXML.

Read at least:
- `xl/workbook.xml`
- `xl/_rels/workbook.xml.rels`
- `xl/sharedStrings.xml` if present
- target worksheet XML files

## Relationship-target normalization pitfall
When resolving worksheet paths from `workbook.xml.rels`, normalize all three cases:
- `worksheets/sheet2.xml` -> `xl/worksheets/sheet2.xml`
- `xl/worksheets/sheet2.xml` -> keep as-is
- `/xl/worksheets/sheet2.xml` -> strip the leading slash

Some answer `.xlsm` files use absolute-style targets like `/xl/worksheets/sheet2.xml`; if you blindly prepend `xl/`, you will incorrectly try to read `xl/xl/...` and miss the sheet.

## Answer-workbook discovery pitfall
Do not require the authoritative workbook filename to match `*_ANS*.xlsm`.

In this JD6628H workflow, the usable answer evidence can instead appear in a combined TENJI workbook such as:
- `JD6628H_BM2922AA_Dual2-1_Blind2-3_TenjiV2.2_R0.1.xlsm`

Implications:
- broaden discovery beyond `*ANS*` filename filters when no results appear
- check mixed-family TENJI workbooks in `Downloads` or the user-provided answer directory
- verify authority from actual `Test Note` content, not the filename pattern alone
- one workbook may only cover a subset of cases, so absence of `智能盲插2-6` / `2-9` evidence is a real blocker, not a search mistake

# Family classification rules
## 1. Basic blind-insert family
Typical JD6628H cases:
- `智能盲插2-1`
- `智能盲插2-2`
- `智能盲插2-4`
- `智能盲插2-5`
- `智能盲插2-7`
- `智能盲插2-8`
- `智能盲插2-9` (structure only; source still has a numbering anomaly)

Default expansion:
- S1 primary establish
- S2 secondary event / newcomer target output
- S3 secondary detach / primary survives

Typical measured-node pattern:
- S1 -> `VBUSC_C1`
- S2 -> `VBUSC_C2`
- S3 -> `VBUSC_C1`

## 2. Role-transfer family
Confirmed family members:
- `智能盲插2-3`
- `智能盲插2-6`

Default expansion:
- S1 primary establish
- S2 fallback / constrained state after secondary insertion
- S3 role transfer / boosted target after negotiation
- S4 primary recover / survive after secondary detach

Do not compress S2 and S3 into one row.

# Confirmed answer-workbook evidence
## 智能盲插2-3
Confirmed from answer workbook:
- answer file: `JD6628H_BM2922AA_Dual2-1_Blind2-3_TenjiV2.2_R0.1.xlsm`
- sheet: `Test Note`
- row: 4
- symbol: `BI_2_3_C1_9V_C2_20V`
- description: `智能盲插 2-3：C1先9V，C2插入後請求20V並轉主路，拔除C2後C1維持9V`
- remarks: `Protocol supplement: fallback/role transition`

Observed control-path / judge sequence:
1. `ForceV VIN 5 200mA`
2. `ForceV vatach1 7V 0A`
3. `UR k3 ON`
4. `PD_command PD_INIT`
5. `PD_command PD_req9v`
6. `JudgeV VBUSC_C1 7.2 10.8`
7. `JudgeV VBUSC_C2 0 0.8`
8. `ForceV vatach2 7V 0A`
9. `UR k4 ON`
10. before 20V request: `JudgeV VBUSC_C1 7.2 10.8`, `JudgeV VBUSC_C2 4 6`
11. `PD_command PD_INIT`
12. `PD_command PD_req20v`
13. after role transfer: `JudgeV VBUSC_C1 7.2 10.8`, `JudgeV VBUSC_C2 16 21.5`
14. detach: `ForceV vatach2 0V 0A`, `UR k4 OFF`
15. final: `JudgeV VBUSC_C1 7.2 10.8`, `JudgeV VBUSC_C2 0 0.8`

Interpretation:
- S1 validates primary C1 at 9V.
- S2 is a real fallback/constrained state: C2 is present but only at 5V before boosted negotiation completes.
- S3 validates the boosted newcomer (`VBUSC_C2`) while C1 remains active at 9V.
- S4 validates recovery/survival after C2 detach.

## TENJI split-row delivery rule validated on 智能盲插2-3
A practical conversion lesson from the final workbook delivery:
- the answer workbook can show `智能盲插2-3` as one compressed `Test Note` row (`BI_2_3_C1_9V_C2_20V`),
- but for this user's TENJI workflow, the final deliverable should still be expanded into **four observable rows**, one judge target per row.

Recommended split-row output:
- `BI_2_3_C1_ONLY_9V`
- `BI_2_3_C2_FALLBACK_5V`
- `BI_2_3_C2_TRANSFER_20V`
- `BI_2_3_C1_RECOVER_9V`

Recommended `SPEC Typ` values by row:
- S1 = `9V`
- S2 = `5V`
- S3 = `20V`
- S4 = `9V`

Recommended measured-condition fragments by row:
- S1: `PD_req9v`, judge `VBUSC_C1=9V`, `VBUSC_C2=0V`
- S2: `ForceV vatach2 7V 0A`, `UR k4 ON`, judge `VBUSC_C2=5V fallback`
- S3: `PD_req20v`, judge `VBUSC_C2=20V`
- S4: `ForceV vatach2 0V 0A`, `UR k4 OFF`, judge `VBUSC_C1=9V`, `VBUSC_C2=0V`

Packaging pattern validated for this single-case workbook:
- row 2 = workbook-head `OS_test`
- rows 3..6 = the four split body rows
- row 7 = workbook-tail `OS_test2`
- each body row gets its own `Min/Typ/Max/Unit`, using the JD6628H voltage-row convention `Min = Typ*0.8`, `Max = Typ*1.2`, `Unit = V`

Important closeout rule learned here:
- the source SA row contains an additional final `C1` detach cleanup state,
- but the answer-workbook judged states stop at `C2` detach -> `C1` recovery,
- so the delivered TENJI workbook should stop at the last answer-verified judged state unless a separate cleanup row is explicitly required by reviewed answer evidence.
- If that final cleanup is omitted from the body rows, preserve it as a traceability note rather than silently discarding it.

## Reusable measured-node rule for this role-transfer family
For `C1 first, C2 later, C2 target > C1 target` cases:
- S1 -> primary node `VBUSC_C1`
- S2 -> still read both nodes, but the differentiating newcomer fallback evidence is on `VBUSC_C2`
- S3 -> the decisive boosted-target judge is the newcomer node `VBUSC_C2`
- S4 -> recovery / survival goes back to `VBUSC_C1`

Do not assume the role-transfer row should keep measuring the original primary. The answer for `智能盲插2-3` proves the decisive boosted-target check moves to `VBUSC_C2`.

# Source-workbook anomaly handling
## 智能盲插2-6
Source anomaly:
- `Target voltage` step 1 says `VBUS1=12V`
- `Request PDO` step 1 says `C1=PDO2`

Do not silently normalize this.
Mark it explicitly as a source anomaly until an answer workbook or reviewer confirms whether:
- the `Request PDO` should really be `PDO3`, or
- the target-voltage text is wrong, or
- the project uses a nonstandard PDO numbering in this mode.

## 智能盲插2-9
Source anomaly:
- `Request PDO` shows `4.C1=PDO5` with no `3.` entry

Treat this as a numbering-gap anomaly, not proof of an extra hidden state.
Until answer evidence says otherwise, keep `智能盲插2-9` in the basic 3-row family:
- S1 primary
- S2 secondary event
- S3 secondary detach

# Closeout rule
Do not mark blind-insert analysis `final complete` unless all are true:
- role-transfer rows have answer-workbook evidence for measured node and control path
- source anomalies are explained or corrected
- row splitting preserves one observable judge per row
- any final TENJI DSL is based on confirmed evidence, not only prose inference

# Recommended workflow
1. Read the source `智能盲插模式` row and split its observable states from `預期結果`.
2. Decide whether the row is basic or role-transfer family.
3. Parse the answer workbook `Test Note` read-only.
4. Extract symbol, description, remarks, control-path primitives, and every `JudgeV` target.
5. Record the measured node per stage, not only the final state.
6. If answer evidence is missing, leave the row `needs_manual_review` instead of guessing.
7. Keep source anomalies visible in the draft artifacts and closeout checklist.

# Output format
Return concise structured notes:

## source summary
- mode-qualified testcase
- source row
- observable states
- anomaly flags, if any

## answer evidence
- workbook path
- Test Note row
- symbol
- decisive control-path / judge sequence

## mapping result
- S1/S2/S3(/S4) row split
- measured node per row
- judge band per row
- status: `draft-ready` or `needs_manual_review`

## closeout decision
- `core mapping complete` / `pending sign-off` / `final complete`

# Pitfalls
- Do not flatten fallback and boosted-role-transfer into one row.
- Do not convert a numbering typo into a semantic extra step.
- Do not call a row final when answer-workbook evidence is still missing.
- Do not miss absolute-style worksheet targets like `/xl/worksheets/sheet2.xml` when parsing answer `.xlsm` files.

# Verification checklist
Before finalizing, confirm:
- source row and mode-qualified testcase match the workbook
- relation targets were normalized correctly
- every cited `JudgeV` comes from the answer workbook, not inference
- anomalies are labeled explicitly
- role-transfer rows are not marked `draft-ready` without answer evidence
