---
name: jd6628h-dual-power-mode-analysis
description: Analyze JD6628H 雙電源模式 SA test-plan scenarios and infer TENJI Test Note mapping by independent-port bring-up, control-path switching, and surviving-port validation.
---

# When to use
Use this when the user provides JD6628H 雙電源模式 (`雙電源模式`) test-plan items or answer `.xlsm` files and wants to:

- understand how a dual-power scenario maps into TENJI `Test Note`
- learn reusable translation logic instead of memorizing item numbers
- compare C1-first and C2-first mirror cases
- infer whether a case is independent dual-9V coexistence, fallback, or another dual-power behavior

This skill is for read-only analysis of the original workbook and answer workbook.

# Core principle
Do **not** reuse the 單電源模式 reasoning model by default.

In JD6628H dual-power cases, start by deciding whether the testcase is verifying:
1. **independent dual-port operation** (each port keeps its own negotiated output), or
2. **interaction/fallback behavior** between ports.

For the common independent case, the measured node follows the port currently being brought up or the port that survives after a detach. It is **not** a shared-5V / recovery-to-9V primary-port model like many 單電源 cases.

# Port/control model rules
## Type-C attach model
Typical Type-C attach sequence in TENJI answer files:
- `ForceV vatach1 7V 0A` or `ForceV vatach2 7V 0A`
- `UR k3 ON` for C1 / `UR k4 ON` for C2
- `PD_command PD_INIT`
- `PD_command PD_req9v`
- measure the corresponding `VBUS1` or `VBUS2`

## Dual-input power rails
Dual-power answers may also enable both rails before port actions, for example:
- `ForceV VIN 5 200mA` + `UR k0 ON`
- `ForceV VIN2 5 200mA` + `UR k1 ON`

Treat these as the dual-power environment setup, not as evidence of a shared output bus.

# Decision tree
## Step 1: identify whether the testcase is independent or shared/fallback
Read the expected-result wording first.

### Signs of independent dual-port behavior
- one port insertion produces `VBUS1 = 9V` or `VBUS2 = 9V`
- later insertion of another Type-C port also produces its own 9V
- the first port is explicitly described as remaining unchanged
- detach of the second port only checks that the surviving port still keeps 9V
- no wording about shared charging, pull-down to 5V, or recovery from 5V

If these signs are present, analyze the case as **independent coexistence**.

## Step 2: for each attach step, measure the port being proven
When a new Type-C port is inserted and the expected result says that port rises to 9V, the answer workbook typically:
- switches the attach/control path to that port
- negotiates 9V on that port
- measures that port's own VBUS node

Examples:
- bring up C2 -> measure `VBUS2`
- bring up C1 -> measure `VBUS1`

## Step 3: after detach, measure the surviving port
If the testcase says the surviving port remains unchanged at 9V after the other port detaches:
- detach the leaving port (`vatachX = 0`, `UR kX OFF`)
- measure the surviving port's `VBUS`
- judge `7.2 ~ 10.8V`

# Stable mapping rules learned from JD6628H dual-power examples
## Rule A — dual-power independent cases are not shared-bus cases
Do not force a single primary-port / shared-5V interpretation when the expected results clearly show both ports independently at 9V.

## Rule B — answer pseudo code may switch UR control to the newly inserted port
In independent coexistence cases, when the second Type-C port is inserted, the answer workbook may turn off the prior CC path and enable the new one, for example:
- `UR k4 OFF`
- `UR k3 ON`

Treat this as **control-path switching for new-port negotiation**, not proof that the first port lost its independent 9V output.

## Rule C — measurement follows the currently validated port during attach
If the step proves the newly inserted port successfully negotiated 9V, measure that new port's VBUS even when another port is already active.

## Rule D — measurement follows the surviving port after detach
If the step proves the remaining port stayed stable after the other port detached, measure the surviving port's VBUS.

# Known worked example
## 2-10
Scenario shape:
- category: `空載插拔測試 (C2 + C1)`
- sequence: C2 inserts first, then C1 inserts, then C1 detaches
- expected behavior: C2 = 9V, then C1 = 9V while C2 stays 9V, then C2 remains 9V after C1 detach

Observed Test Note mapping:
1. `C2_9V_5`
   - dual rails enabled: `VIN`, `VIN2`
   - `vatach2` + `UR k4 ON`
   - `PD_INIT` -> `PD_req9v`
   - measure `VBUS2`
   - judge `7.2 ~ 10.8V`
2. `C1_Atach_5`
   - `vatach1`
   - `UR k4 OFF`, `UR k3 ON`
   - `PD_INIT` -> `PD_req9v`
   - measure `VBUS1`
   - judge `7.2 ~ 10.8V`
3. `C1_detach_5`
   - `vatach1 = 0`, `UR k3 OFF`
   - measure `VBUS2`
   - judge `7.2 ~ 10.8V`
   - cleanup includes turning off `vatach2`, `VIN`, `VIN2`

Reusable interpretation:
- first attached port establishes its own 9V
- second attached port negotiates its own 9V without converting the system into shared 5V
- after second-port detach, verify the first port still holds 9V

# Recommended workflow
1. Read the source `雙電源模式` row from the original test-plan workbook.
2. Split the ordered events into attach/detach actions.
3. Decide whether the prose describes independent coexistence or interaction/fallback.
4. Read the answer workbook `Test Note` rows for that item.
5. For each step, record:
   - acted-on port
   - UR / attach path selected
   - measured VBUS node
   - voltage judgment
   - whether the step proves new-port bring-up or surviving-port stability
6. Check whether a mirrored C1/C2 version should exist by symmetry.

# Output format
Return concise structured notes:

## test plan summary
- category / function / step list / expected results

## Test Note mapping
- one bullet per generated TENJI step
- symbol
- key actions
- measured node
- voltage judgment

## inferred logic
- independent coexistence vs fallback/share
- why the measured node changes or stays the same

## reusable rule
- the generalizable translation pattern learned from the case

## anomalies
- prose-vs-answer mismatch, if any

# Pitfalls
- Do not apply the 單電源 `shared 5V` / `recover 9V` model unless the expected results actually describe that behavior.
- Do not assume a UR path switch means the previously active port lost output.
- Do not measure the previously active port on a step whose purpose is to prove the newly inserted port reached 9V.
- Do not ignore dual-rail setup (`VIN`, `VIN2`) when reconstructing the TENJI environment.

# Verification checklist
Before finalizing, confirm:
- the measured VBUS node matches the answer workbook row
- the voltage band matches the worksheet values
- the attach/control path matches the acted-on port
- the conclusion distinguishes independent coexistence from shared/fallback behavior
