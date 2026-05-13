# Review Checklist

Use this checklist when reviewing TENJI output, event chains, or workbook rows.

## Semantic checks
- Is the protocol precondition explicit?
- Is baseline state clear?
- Is request/stimulus explicit?
- Is qualification/filter timing explicit?
- Is expected transition explicit?
- Is verify window explicit?
- Is fallback or recovery path mentioned when needed?

## TENJI checks
- Is Symbol unique?
- Is `_TMU` suffix used where required?
- Are hex values written with `0x`?
- Are pin names consistent with PinMap?
- Are multi-step H-column actions split with line breaks?
- Are Tune/TuneI style actions paired with a break/judge?

## Risk flags
- state inherit ambiguity
- implicit previous row dependency
- protocol family confusion
- verify range too vague
- request code inferred rather than stated
