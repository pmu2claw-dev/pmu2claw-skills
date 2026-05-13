# Output Modes

Choose the smallest mode that satisfies the request.

## Summary
Use for quick explanation or review comments.

## Event chain
Use when the user asks:
- 事件鏈
- 怎麼拆舉
- step by step behavior
- protocol sequence

Recommended structure:
- E0 baseline
- E1 attach / entry
- E2 qualification
- E3 request
- E4 transition
- V1 verify
- F fallback

## Decision table
Use when the user needs a reusable matrix for multiple items.

Recommended columns:
- item
- pre-state
- stimulus
- timing/filter
- expected transition
- final state
- verify
- fallback / notes

## Tenji mapping
Use only when semantics are already stable.

Recommended order:
- test item intent
- row split
- B~N content
- remarks / risk flags

## Review / debug note
Use when inspecting existing workbook content.

Focus on:
- state carryover
- hidden assumptions
- bad symbol naming
- missing verify window
- wrong protocol interpretation
