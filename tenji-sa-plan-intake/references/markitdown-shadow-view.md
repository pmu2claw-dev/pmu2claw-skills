# MarkItDown shadow view for SA-plan + DUT collateral

Use this reference when the user provides an SA workbook plus supporting DUT materials and you want a fast text/markdown layer for search and semantic comparison.

## Purpose

Create a secondary, non-authoritative text view that complements OOXML workbook inspection.

Authoritative layer:
- OOXML workbook structure
- sheet roles
- row anchors / testcase numbering
- template-sensitive layout interpretation

Shadow layer:
- markitdown-produced markdown/text
- fast keyword search
- cross-document term linking
- quick summarization across workbook + netlist + specs

## Best-fit inputs

- `.xlsx` / `.xls` workbooks where you need quick content search across many sheets
- DUT collateral such as:
  - plain-text netlists (`.scs`, `.sp`, `.cir`, `.txt`)
  - PDF datasheets/specs
  - DOCX notes
  - HTML exports
  - ZIP bundles of mixed documents

## Recommended workflow

1. Run the normal OOXML intake/classifier first.
2. Generate or obtain a markdown/text shadow view of the workbook and supporting DUT files.
3. Extract repeated terms from the shadow view:
   - testcase IDs
   - mode names
   - parameter/symbol names
   - rails / supplies
   - DUT block names
   - signal / pin names
   - protocol keywords
4. Use the shadow view to find supporting evidence and wording matches.
5. Return to the authoritative OOXML / netlist parser for final row-level or structure-sensitive conclusions.

## Guardrails

- Never use markdown flattening as the sole basis for workbook row mapping.
- Do not trust flattened table output for merged-cell semantics or workbook layout meaning.
- For `.xlsm` or highly formatted mother-template-like workbooks, treat text extraction as advisory only.
- MarkItDown is good for ingestion/search, not for preserving Excel/VBA/template fidelity.

## Practical value

This works especially well when the real task is not just “read one workbook” but “compare what the workbook says against DUT evidence spread across several file formats.”