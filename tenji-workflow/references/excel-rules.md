# Excel Rules

Use this file as the canonical formatting contract for TENJI B~N output.

## B~N columns
- B = Bin
- C = Test_Item
- D = Symbol
- E = PWR Sequence
- F = PseudoCode
- G = Wait/Run Pattern
- H = Measure Condition
- I = Description
- J = Min
- K = Typ
- L = Max
- M = Unit
- N = Remarks

## Hard rules
- Start test items from row 3 in workbook context.
- Symbol must be unique.
- Time / frequency / delay style items must use `_TMU` suffix when required.
- Hex values must use `0x` prefix.
- Multi-step Measure Condition content belongs in one cell with line breaks.
- TuneV / TuneI style sweep steps need an immediate break / judge pairing.
- Pin names must match PinMap definitions.

## Structural split rule
When converting protocol or test-plan content into TENJI rows, split the logic into these phases whenever possible:
1. pre-state establish
2. request / stimulus
3. wait / qualification
4. transition
5. verify
6. fallback / recovery

## Review flags
Call out these issues explicitly if present:
- state inherit ambiguity
- hidden protocol precondition
- request code not explicit
- verify window missing
- fallback path missing
