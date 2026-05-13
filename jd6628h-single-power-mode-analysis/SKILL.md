---
name: jd6628h-single-power-mode-analysis
description: Analyze JD6628H 單電源模式 SA test-plan scenarios and infer TENJI mapping by primary/secondary/tertiary port roles, measurement target, and 5V-share vs 9V-recovery intent.
---

# When to use
Use this when the user provides JD6628H 單電源模式 (`單電源模式`) test-plan items or answer `.xlsm` files and wants to:

- understand how a scenario maps into TENJI `Test Note`
- learn the reusable translation logic instead of memorizing item numbers
- compare mirrored C1/C2 scenarios
- infer likely measurement targets before opening the answer file

This skill is for **structure/logic learning** from the original workbook and answer workbook while preserving both files unchanged.

# Core principle
Do **not** learn these scenarios by item number ordering alone.

Instead classify each step by:
1. which port establishes the initial boosted state
2. which port joins later as secondary / tertiary participant
3. which port the step is actually trying to verify
4. whether the expected end state is **shared 5V** or **recovery to 9V**

The measured node follows the **verification target**, not simply the newest attached port.

# Port model rules
## Type-C ports (C1 / C2)
Typical attach model:
- `ForceV vatach1 7V 0A` or `ForceV vatach2 7V 0A`
- `UR k3 ON` for C1 / `UR k4 ON` for C2
- `PD_command PD_INIT`
- `PD_command PD_req5v` or `PD_command PD_req9v`

Observed PinMap anchors:
- `CC1_C1 -> UR_k3`
- `CC1_C2 -> UR_k4`

## A port
A-port is **not** modeled as Type-C attach.

Typical A-port model uses:
- `ForceV VBUSC_A ...`
- `ForceI VBUSC_A ...`
- sometimes `DP_A / DM_A` negotiation or handshake

Never translate A-port as `vatachA + CC UR`.

# Decision tree
## Step 1: determine the primary port
Find the first port that:
- attaches successfully
- negotiates / behaves as the initial active source path
- reaches boosted output (typically 9V)

That port is the **primary**.

Typical first-step check:
- measure primary `VBUSC_*`
- judge `7.2 ~ 10.8V`

## Step 2: when a second port joins
Ask what the step is verifying.

### If verifying the primary got pulled back to shared 5V
- keep measuring the **primary** node
- judge `4 ~ 6V`

### If verifying the newcomer successfully joined shared 5V
- measure the **newly attached** node
- judge `4 ~ 6V`

## Step 3: when a third port joins
Again ask what is being verified.

### If the intent is “existing primary now shares at 5V”
- measure primary

### If the intent is “new third participant successfully entered shared 5V”
- measure the newcomer (`VBUSC_C1`, `VBUSC_C2`, or `VBUSC_A` as appropriate)

## Step 4: when a port detaches
Read the expected-result wording carefully.

### If wording says maintain share / 維持5V充電
- measure the surviving primary or surviving target node
- expect `4 ~ 6V`

### If wording says recover boost / 回復升壓至9V
- answer workbook may replay negotiation
- then measure the recovering primary
- expect `7.2 ~ 10.8V`

# Stable mapping rules learned from JD6628H examples
## Rule A — primary is the first boosted port
Examples:
- C1-first scenario -> primary often `VBUSC_C1`
- C2-first scenario -> primary often `VBUSC_C2`
- A-first scenario -> primary often `VBUSC_A`

## Rule B — second participant often proves primary dropped to 5V share
Examples:
- A joins C1-primary -> measure `VBUSC_C1`
- C2 joins A-primary -> measure `VBUSC_A`

## Rule C — third participant often gets its own measurement
If the step is meant to prove the newcomer has entered shared power, the answer workbook often measures the newcomer directly.

Examples:
- C2 joins C1/A scenario -> measure `VBUSC_C2`
- C1 joins C2/A scenario -> measure `VBUSC_C1`

## Rule D — A-primary recovery may require replaying A-port negotiation
When A is the recovering primary, do not assume secondary detach alone proves recovery. The answer may replay `DP_A/DM_A` or equivalent A-port negotiation before measuring recovery.

## Rule E — mirrored C1/C2 scenarios can often be inferred by symmetric substitution
Common substitutions:
- `C1 <-> C2`
- `vatach1 <-> vatach2`
- `UR_k3 <-> UR_k4`
- `VBUSC_C1 <-> VBUSC_C2`

But always verify whether extra routing / control steps differ.

## Rule F — split rows by observable state first, but direct-delivery workbooks may need to preserve an existing golden row shape
There are **two valid row-shape contexts** for JD6628H single-power work, and you must choose the right one for the user's requested outcome.

### Context 1: first-pass semantic split workbook
When you are generating a new mapping from the SA source plus a mother template, the default is still:

#### Two-port family -> often 3 TENJI rows
Applies to shapes like:
- `單電源2-1`: `C1 -> C2 join -> C2 leave`
- `單電源2-10`: `C2 -> C1 join -> C1 leave`
- `單電源2-19`: `C1 -> A join -> A leave`
- `單電源2-25`: `C2 -> A join -> A leave`
- `單電源2-31`: `A -> C1 join -> C1 leave`
- `單電源2-37`: `A -> C2 join -> C2 leave`

Stable semantic split:
1. primary-only boosted state
2. second participant causes shared-5V state
3. second participant leaves and surviving primary either recovers to boost or remains at 5V per expected-result wording

#### Three-port family -> often 4 TENJI rows
Applies to shapes like:
- `單電源2-43`: `C1 -> C2 -> A -> A leave`
- `單電源2-61`: `C1 -> A -> C2 -> C2 leave`
- `單電源2-79`: `C2 -> A -> C1 -> C1 leave`

Stable semantic split:
1. primary-only boosted state
2. second participant joins, measure the state transition on the validation target
3. third participant joins; often measure the newcomer directly to prove it entered shared 5V
4. third participant leaves; measure the surviving target according to the expected-result wording

### Context 2: direct-delivery workbook matching an existing golden answer
If the user asks for a finished TENJI Excel file and you can find a **known-good answer workbook or validated composite workbook** that already contains the target family, that golden workbook takes precedence over first-pass re-inference.

In that context, preserve the existing row shape exactly and crop/extract the needed rows into a delivery workbook rather than re-synthesizing from scratch.

Important validated finding:
- `JD6628H_SinglePwr_NonFPGA_TenjiV2.2_R0.1.xlsm` already contains `單電源2-25 ~ 2-30` as `SinglePwr_C2A`
- those cases are laid out as **4 rows per case**:
  1. `S1` primary-only boosted state
  2. `S2` A joins, shared `5V`
  3. `S3` A detaches, primary recovers to the original PDO band
  4. `S4` final cleanup detach (`Wait 10s` then `C2拔除`)
- therefore for direct delivery of `2-25 ~ 2-30`, do **not** collapse to a 3-row first-pass version if the goal is to hand over a workbook matching the validated golden structure

Practical rule:
1. search for an existing answer/golden workbook first
2. if an exact family workbook already exists (for example a prebuilt `2-25_to_2-30` delivery workbook under `workspace-tenji`), prefer reusing that validated workbook instead of regenerating from scratch
3. inspect the exact target rows in `Test Note`
4. for direct handoff, it is acceptable to copy the validated workbook to a new delivery filename rather than rebuilding the workbook body, as long as the copy is verified
5. preserve `.xlsm` macro payload and validate by workbook open/convert plus `vbaProject.bin` hash if possible
6. a high-confidence quick-release check for these reused family workbooks is: `(a)` confirm the copied file is hash-identical to the validated source, `(b)` reopen and audit representative first/last testcase rows in `Test Note`, and `(c)` run a headless LibreOffice conversion to `.xlsx` to confirm package readability before delivery
7. For the exact `單電源2-25 ~ 2-30` `SinglePwr_C2A` re-delivery workflow on this host, prefer reusing the already validated family workbook under `workspace-tenji/deliveries` when present (for example `JD6628H_SinglePwr_2-25_to_2-30_C2A_TenjiV2.2_R0.4_deliver.xlsm`) rather than regenerating the family. Safe redelivery procedure:
   - verify the candidate delivery workbook still contains `OS_test` head, body rows for `2-25 ~ 2-30`, and `OS_test2` tail by reopening `Test Note`
   - spot-check representative rows from both ends of the family (for example `2-25 S1~S4` and `2-30 S1~S4`)
   - confirm full-file SHA-256 equality against the last validated family file if one exists
   - compare `xl/vbaProject.bin` SHA-256 against the template or prior validated file to ensure macro payload preservation
   - run `libreoffice --headless --convert-to xlsx ...` as a package-readability gate
   - if all checks pass and the user only wants a fresh direct handoff, copy that verified workbook to a new delivery filename instead of rebuilding

## Rule G — source `Request PDO` column is the authoritative PD-request sequence
When reconstructing TENJI from the SA workbook, derive `PD_req*` from the source `Request PDO` column first, not merely from prose such as `SINK_9V` / `SINK_12V` / `SINK_20V` in the action column.

For the validated single-power families:
- `PDO1` -> shared `5V`
- `PDO2` -> `9V`
- `PDO3` -> `12V`
- `PDO5` -> `20V`

Typical single-power pattern:
1. step 1 requests the primary boosted PDO
2. step 2 drops to `PDO1` / `5V` when another participant joins
3. step 3 re-requests the original primary PDO only if the expected result says recovery

## Rule H — A-port behavior splits into two different reusable families
### A as secondary participant
Typical actions are power-node based and do not use Type-C attach primitives:
- `ForceV VBUSC_A 2.6 100mA`
- `Wait 1ms`
- `ForceI VBUSC_A 0 5`

For the stable two-port `C1 -> A -> A detach` family (`單電源2-19~2-24`):
- row 1 measures `VBUSC_C1` after the initial `PD_req*` derived from the first `Request PDO`
- row 2 still measures `VBUSC_C1` and judges `4~6V` when A joins, regardless of whether the prose says A is `SINK_9V` or `SINK_12V`
- row 3 drops A, then replays `PD_INIT` + the original C1 `PD_req*`, and measures `VBUSC_C1` for recovery to the original PDO band
- A-side capability text in the action column is informative, but the authoritative recovery voltage still comes from the `Request PDO` column

Direct-delivery finding for exact `.xlsm` handoff in this family:
- this host now has exact standalone ANS workbooks for both `2-19` and `2-24`
- prefer the exact donor workbook when it exists; do **not** keep using a synthetic `2-19`-based fallback for `2-24` once the exact `2-24` answer file is available
- `2-24` confirms the same stable row shape as the rest of the `C1 -> A -> A detach` family:
  1. row 1 = `Single_power1` + `C1_20V_2`
  2. row 2 = `A_Atach`
  3. row 3 = `A_detach`
  4. workbook wrapper = `OS_test` head + `OS_test2` tail + merged `C3:C5`
- for `2-19~2-24` family delivery, the safer preference order is:
  1. exact case donor (`2-19`, `2-24`, or other exact file if found)
  2. nearby exact donor with the same verified `Request PDO` obligations
  3. only then a synthetic fallback assembled from another donor plus source-row semantics
- exact `2-24` workbook evidence also confirms the 20V recovery path uses direct `PD_req20v` + `MeasV/JudgeV VBUSC_C1 16 24`, while the A-attach row still stays at `4~6V`
- important workbook quirk: the single-case answer skeleton keeps `Test Item` merged as `C3:C5`; when editing with openpyxl, only write `C3` and never try to assign `C4` or `C5`, or you will hit a read-only `MergedCell` error
- after editing, verify that `C3:C5` merge still exists and that `xl/vbaProject.bin` hash matches the skeleton source if the goal is package-preserving delivery

This is the common model in `單電源2-19`, `單電源2-24`, `單電源2-25`, `單電源2-43`, `單電源2-61`, `單電源2-79`.

### Combined direct-delivery pattern for `單電源2-1 ~ 2-79`
A later combined handoff established a reusable assembly pattern for users who ask for one workbook covering the whole single-power range instead of many per-family files.

Validated host strategy:
1. start from the mother template `.xlsm` as the package shell
2. assemble body blocks from already validated segment workbooks instead of regenerating every case from scratch
3. allow mixed row shapes inside one workbook when that is what the validated donors require:
   - `2-1~2-18` kept the existing split-row 3-step surface from the generated family workbooks
   - `2-19~2-42` used 3-row ANS-style families
   - `2-43~2-79` used 4-row ANS-style families
4. for `2-19~2-24`, prefer exact donors where available (`2-19`, `2-24`) and fill the intermediate cases by the same authoritative `Request PDO` / expected-result family logic
5. preserve all donor-specific merged `Test Item` ranges when copying blocks into the combined workbook
6. append one final `OS_test2` tail row only after the last copied case block
7. verify the combined workbook by checking:
   - first case = `2-1`
   - last case = `2-79`
   - case count = `79`
   - merged-range count matches the expected block structure
   - `xl/vbaProject.bin` hash is preserved against the mother template shell
   - headless LibreOffice conversion succeeds

Practical implication:
- for large contiguous deliveries, think in terms of **verified segment assembly** rather than one monolithic re-synthesis pass
- mixed row shapes are acceptable when they are grounded in validated donor workbooks and the user asked for a direct deliverable rather than a normalized semantic export
- keep the response concise and hand over the concrete verified file path immediately once the combined workbook is ready

See `references/jd6628h-single-power-combined-delivery.md` for the concrete `2-1~2-79` segment map and verification summary.

## References
- `references/jd6628h-single-power-combined-delivery.md` — verified segment map, row-shape mix, hashes, and delivery notes for the combined `2-1~2-79` workbook

## Rule I — three-port measurement targeting has a stable JD6628H mirror pattern


This is the common model in `單電源2-31` and `單電源2-37`.

### Direct-delivery combined workbook pattern for `單電源2-37 ~ 2-42`
A later direct handoff for `單電源2-37 ~ 2-42` established a reusable ANS-style family-build pattern for the `A -> C2 join -> C2 detach` family:

- preserve the classic 3-row ANS surface rather than inventing a prose/generator family surface
- use `Single_power3` as the merged `Test Item` anchor for each 3-row case block
- step symbols stay stable by phase:
  - row 1: `A_9V_2` or `A_12V_2`
  - row 2: `C2_Atach_2`
  - row 3: `C2_detach_2`
- measure node remains `VBUSC_A` for all three rows because the verification target is the A-side primary path:
  1. A-only boosted state
  2. A drops to shared 5V when C2 joins
  3. A recovers to the original boosted band after C2 detaches
- the family split for this validated range was:
  - `2-37 ~ 2-39` -> 9V family (`7.2~10.8`, typ `9`, symbol `A_9V_2`)
  - `2-40 ~ 2-42` -> 12V family (`9.6~14.4`, typ `12`, symbol `A_12V_2`)

Worked delivery shape on this host:
1. keep workbook head row `OS_test` and tail row `OS_test2`
2. assemble six 3-row case blocks in `Test Note` rows `3:20`
3. preserve one merged `Test Item` range per case:
   - `C3:C5`, `C6:C8`, `C9:C11`, `C12:C14`, `C15:C17`, `C18:C20`
4. for each case, only the row-1 voltage band/type/symbol changes between the 9V and 12V subfamilies; row-2 and row-3 shared-5V / recovery structure stays the same except the recovery judgment follows the family voltage
5. verify the finished `.xlsm` by reopening `Test Note`, confirming all six merged ranges, checking representative first/last cases, confirming `xl/vbaProject.bin` hash preservation, and running headless LibreOffice conversion

This pattern is useful when the user wants one combined Excel deliverable for the A-primary / C2-secondary family and expects the old ANS-style `Test Note` surface.

## Rule I — three-port measurement targeting has a stable JD6628H mirror pattern
For `C1/A/C2` and `C2/A/C1` families:
- row 1 measures the initial primary PD port
- row 2 still measures that primary PD port while it drops to shared `5V`
- row 3 measures the newly joined third participant (`VBUSC_C2` or `VBUSC_C1`) to prove it entered the shared bus
- row 4 returns to the surviving primary PD port

This is strongly confirmed by the `單電源2-61` <-> `單電源2-79` mirror pair.

# Known worked examples
## 2-37
Scenario shape:
- primary = A
- secondary = C2

Observed logic:
1. A only -> `VBUSC_A` at 9V
2. C2 joins -> still measure `VBUSC_A`, now 5V share
3. C2 detaches -> replay A-side negotiation, then `VBUSC_A` returns to 9V

## 2-43
Scenario shape:
- primary = C1
- secondary = C2
- tertiary = A

Observed logic:
1. C1 only -> `VBUSC_C1` at 9V
2. C2 joins -> `VBUSC_C1` drops to 5V
3. A joins -> measure `VBUSC_A` at 5V
4. Answer file appears inconsistent with prose: workbook action looks like recovery-to-9V even though description says maintain 5V sharing

Treat this as an anomaly / mismatch case.

## 2-61
Scenario shape:
- primary = C1
- secondary = A
- tertiary = C2

Observed logic:
1. C1 only -> 9V on `VBUSC_C1`
2. A joins -> measure `VBUSC_C1`, confirm drop to 5V
3. C2 joins -> measure `VBUSC_C2`, confirm newcomer entered shared 5V
4. C2 detaches -> measure `VBUSC_C1`, C1/A maintain 5V

## 2-79
Scenario shape:
- primary = C2
- secondary = A
- tertiary = C1

Observed logic:
1. C2 only -> 9V on `VBUSC_C2`
2. A joins -> measure `VBUSC_C2`, confirm drop to 5V
3. C1 joins -> measure `VBUSC_C1`, confirm newcomer entered shared 5V
4. C1 detaches -> measure `VBUSC_C2`, C2/A maintain 5V

This is the mirror of 2-61.

# Recommended workflow
1. Read the source `單電源模式` row from the original test-plan workbook.
2. Split the step sequence into ordered attach/detach events.
3. Identify primary / secondary / tertiary roles from behavior, not item number.
4. Read the answer workbook `Test Note` rows for the item.
5. For each step, record:
   - action port
   - measured node
   - expected band (`4~6` or `7.2~10.8`)
   - whether the step proves primary-share, newcomer-share, or recovery
6. Compare against mirrored scenarios when available.
7. Flag any prose-vs-answer mismatch explicitly.

# Output format
Return concise structured notes:

## test plan summary
- category / function / step list / expected results

## Test Note mapping
- one bullet per generated TENJI step
- symbol
- key action(s)
- measured node
- voltage judgment

## inferred logic
- primary / secondary / tertiary roles
- why the measured node changes or stays the same

## reusable rule
- the generalizable translation pattern learned from the case

## anomalies
- prose-vs-answer mismatch, if any

# Pitfalls
- Do not assume newest attached port is always the measured node.
- Do not flatten all attach steps into one rule; ask what each step verifies.
- Do not model A-port as Type-C attach.
- Do not assume detach means recovery to 9V; many cases intentionally stay at shared 5V.
- Do not trust item-number similarity more than scenario-role similarity.

# Verification checklist
Before finalizing, confirm:
- the primary port is justified by the first boosted-state step
- each measured node matches the actual answer workbook row
- each judgment band matches the worksheet values
- any C1/C2 mirror claim is supported by corresponding control-path swaps
- any anomaly is explicitly labeled rather than silently normalized
