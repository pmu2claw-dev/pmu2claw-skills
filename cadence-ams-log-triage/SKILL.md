---
name: cadence-ams-log-triage
description: Analyze large Cadence Xcelium/Spectre AMS xrun logs to separate terminal analog failures from secondary noise, identify the most suspicious mixed-signal interface blocks, and assess whether the run failed from convergence or simply slowness.
---

# Cadence AMS xrun log triage

Use this when a user shares an `xrun`/AMS mixed-signal log and asks why the simulation failed, which circuits are implicated, whether it was convergence-related, or whether the simulation was simply too slow.

## When to use
- Large Cadence `xrun(64)` logs with Xcelium + Spectre AMS output
- Terminal messages such as `*E,RNALER`, `Analysis 'tran' was terminated prematurely`, or repeated `*E,FNINUS`
- User wants a practical culprit list (which blocks/signals/models to inspect first), not just raw log excerpts

## Goals
1. Confirm whether the failure is digital compile/elaboration or analog transient/runtime.
2. Separate secondary runtime noise from the true terminal error path.
3. Recover the exact Spectre diagnostic if present; if absent, say so explicitly.
4. Identify the most suspicious hierarchy blocks / Verilog-A or connect-module sources.
5. Assess whether the run failed from slowness, convergence, or another analog issue.

## Workflow

### 1) Read the header and runtime context
Use `read_file` on the first ~200-250 lines.
Capture:
- `xrun` version
- key options (`-simcompatible_ams`, `+notimingcheck`, `-xmsimargs`, `-spectre_args`, timescale, rawdir)
- top-level test name
- start timestamp and command context

This quickly tells you whether the run is AMS and where the analog raw/results directory is expected.

### 2) Find terminal failure strings first
Search the full log for high-signal markers, not generic `error` alone.
Good regex terms:
- `RNALER`
- `Analysis .* terminated prematurely`
- `spectre_ori terminated prematurely`
- `fatal|FATAL`
- `SPECTRE-`
- `did not converge|no convergence|timestep too small|singular matrix|blowup|Newton`
- `FNINUS`

Use `search_files` for focused matches and `read_file` around the final region.

### 3) Distinguish terminal cause from secondary recurring errors
A frequent trap in AMS logs is repeated errors that look serious but are not what killed the run.
Example:
- `xmsim: *E,FNINUS: File name ../psf is already in use as a SHM database.`

If the run continues afterward (probe creation, `run`, Spectre banner, activity stats, etc.), treat it as **secondary/noisy unless later evidence proves otherwise**.

### 4) Read the last 100-150 lines verbatim
Use `read_file` near the end of the log. Confirm:
- whether `tran` stopped
- whether Spectre reports `1 error, N warnings...`
- whether the analog fatal message text is actually present in the xrun log
- performance summary: start/end time, elapsed time, memory, CPU

If the log ends with only summary lines like:
- `Analysis 'tran' was terminated prematurely due to an error.`
- `xmsim: *E,RNALER: Simulation terminated due to analog error.`

then do **not** overclaim the exact analog root cause.

### 5) If the end region is dominated by repeated instance lines, summarize them programmatically
AMS logs often dump hundreds of `reporting instances` without the introductory sentence visible in the extracted chunk. Use `execute_code` on the log to:
- iterate over the repeated instance lines
- count them by source file + line
- count by major hierarchy block (e.g. `CS_TOP`, `PD1`, `PD2`, `QC1`, `QC2`, `TMODE`)
- count by internal model marker (e.g. `_cds_internal_L2E_2_dynsup_`, `_cds_internal_sw1_nmos_`)

This converts noisy tails into a ranked suspect list.

Suggested parsing pattern:
- instance lines often look like `1: <hierarchy>:<source_path>:<line>`
- source hotspots tell you which connect-module or Verilog-A model is most implicated
- hierarchy hotspots tell you which functional blocks the user should inspect first

### 6) Interpret AMS activity statistics
If present, inspect lines such as:
- `Number of IEs with D-to-A X edge`
- `Number of IEs with A-to-D X edge`
- `IE with max number of D-to-A edges`
- `IEs with max number of A-to-D edges`

These are extremely useful for mixed-signal triage. High counts on L2E/E2L interfaces usually indicate unstable or suspicious AMS boundary behavior even when the exact Spectre fatal text is missing.

### 7) Judge “slow simulation” separately from “failed simulation”
Use the run summary to decide whether slowness was the problem.
If the log shows the run died in ~minutes with modest CPU/memory, say it **failed relatively quickly** rather than being a classic performance/timestep crawl.
Only call it a slowness issue when the evidence supports that conclusion.

### 8) State uncertainty correctly
If the xrun log does **not** contain the exact Spectre error text, say:
- the run definitely failed in analog transient/Spectre
- it is likely related to AMS interfaces / behavioral models / unstable control signals if the evidence points there
- but the exact subtype (singular matrix, timestep, convergence, model range error, etc.) is **not proven from this log alone**

Recommend obtaining the raw Spectre log/output in that case.

## Output structure to the user
Provide:
1. **Root-cause class** — e.g. analog `tran` failure, not digital compile.
2. **Secondary errors** — e.g. repeated `FNINUS` database conflict that did not immediately stop the run.
3. **Most suspicious blocks/signals** — hierarchy names from activity stats and instance counts.
4. **Most suspicious source models** — e.g. `L2E_2_dynsup.vams`, `sw1_nmos`, `sw1_real`, `TG_MV_ISO`.
5. **Convergence/slowness judgment** — explicit evidence only.
6. **Next-check recommendations** — specific signals and models to inspect.

## Practical heuristics learned
- Repeated `FNINUS` with continued execution is often a probe/results-database conflict, not the ultimate kill shot.
- `RNALER` + `Analysis 'tran' was terminated prematurely` is enough to classify the failure as analog/Spectre-side.
- Large tails of `1: <instance>:<source>:<line>` often indicate suppressed AMS/reporting-instance warnings; counting them is more useful than quoting pages of them.
- When `L2E/E2L` connect modules dominate the suspect list, highlight unstable mixed-signal boundary control signals first.
- AMS activity-stat lines like `IE with max number of D-to-A edges` and `IEs with max number of A-to-D edges` are high-value clues; promote those named interface signals to the top of the suspect list.
- Do not claim “no convergence” unless the log actually says so or includes a recognizably equivalent Spectre fatal diagnostic.

## Pitfalls
- Do not trust raw `error` searches alone; they produce lots of noise (`-errormax`, filenames containing `error`, `errors: 0`).
- Do not treat every repeated runtime error as root cause.
- Do not present the most repeated instance line as proven root cause; it is a suspect hotspot, not proof.
- Do not infer “too slow” just because there are many warnings.

## Verification checklist
Before finalizing, verify that you have explicitly answered:
- Was it analog or digital?
- What exact terminal messages prove that?
- Was there evidence of convergence, or only suspicion?
- Was it actually slow, or did it fail quickly?
- Which blocks/models should the user inspect first?
- Which errors are likely secondary noise?
