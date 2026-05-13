---
name: tenji-workflow
description: Convert Fitipower TENJI requests into executable workflow decisions and output formats. Use when the user asks to write, review, debug, restructure, or explain TENJI Excel test definitions, convert a protocol/test plan into TENJI-ready content, build event chains, split test items into measurable substeps, or normalize output into Tenji columns B~N.
---

# Tenji Workflow

Use this skill as the main entry point for TENJI task execution.

## Core workflow

1. Classify the request into one of four modes:
   - **syntax/manual**: TENJI grammar, sheet structure, command usage, tenji2uvm flow
   - **protocol-to-test**: turn charging protocol knowledge into test logic
   - **test-plan-to-event-chain**: split rows/specs into event sequence and sub-checks
   - **tenji-mapping**: produce or review B~N mapping output
2. Choose the output mode before drafting content:
   - summary
   - event chain
   - decision table
   - Tenji B~N mapping
   - review / debug notes
3. Read only the references needed for the selected mode.
4. Keep the answer in Traditional Chinese unless the user asks otherwise.
5. Preserve exact filenames, symbols, pin names, voltages, timing, and workbook identifiers.

## Decision tree

- If the user asks about TENJI syntax, command meaning, Excel sheet usage, TTR, macro, or tenji2uvm flow: read the matching reference in `references/`.
- If the user asks how to split a test plan, spec, or protocol step into testable actions: read `references/output-modes.md` and, when protocol-specific, also use the `protocol-knowledge` skill.
- If the user asks for actual test fields, mapping patterns, or ready-to-use output rows: use the `tenji-ready` skill.
- If a task mixes protocol understanding and TENJI output, do protocol interpretation first, then convert to event chain, then convert to Tenji mapping.

## Required invariants

- Treat Tenji B~N columns as canonical. Use `references/excel-rules.md`.
- Symbol must be unique.
- Timing/frequency/delay style items must use `_TMU` suffix when required.
- Keep request phase, transition phase, verify phase, and fallback phase distinct.
- Never merge protocol assumptions into a mapping without stating the precondition.
- When a row relies on previous state, call out **state inherit ambiguity** explicitly.

## Reference map

Read these files only when needed:

- `references/excel-rules.md` — canonical B~N rules and formatting constraints
- `references/workflow-routing.md` — classify requests and select output mode
- `references/output-modes.md` — how to write summary / event chain / decision table / mapping
- `references/review-checklist.md` — review and debug checklist
- `references/CORE_RULES.md` — detailed TENJI rules inherited from the existing guide
- `references/excel-structure.md` — workbook sheet structure
- `references/syntax-commands.md` — core syntax for column H
- `references/ttr-commands.md` — parallel/TTR commands
- `references/macro-commands.md` — macro commands
- `references/pseudocode-i2c.md` — column F pseudocode rules
- `references/autorun-commands.md` — autorun-related commands
- `references/tenji2uvm-flow.md` — conversion flow
- `references/qa-and-rules.md` — QA and common pitfalls

## Output discipline

Prefer the smallest format that answers the request:

- Ask/answer only → summary
- Sequence explanation → event chain
- Reusable structure → decision table
- Real workbook content → Tenji B~N mapping

Do not dump the whole manual when only one slice is needed.
