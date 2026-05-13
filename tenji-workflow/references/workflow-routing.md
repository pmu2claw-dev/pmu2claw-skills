# Workflow Routing

Use this file to decide how to process a TENJI-related request.

## Route A — Syntax / manual
Use when the user asks about:
- command syntax
- workbook sheet meaning
- TTR or macro usage
- pseudocode or I2C column rules
- tenji2uvm flow

Output: concise explanation with exact syntax or workbook guidance.

## Route B — Protocol to test logic
Use when the user asks about:
- charging protocol behavior
- request / response chain
- event order
- fallback or coexistence

Read protocol references first. Output: event chain or decision table.

## Route C — Test plan decomposition
Use when the user provides:
- workbook rows
- xlsx/xlsm content
- spec paragraphs
- a named test item group

Output in this order:
1. identify pre-state
2. identify stimulus/request
3. identify timing/filter
4. identify expected transition
5. identify verification window
6. identify fallback/cleanup

## Route D — Tenji mapping
Use when the user wants:
- B~N row content
- test fields
- excel mapping
- workbook-ready text

If protocol semantics are still unclear, do not map yet. Go back to Route B or C first.
