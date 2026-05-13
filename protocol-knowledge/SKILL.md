---
name: protocol-knowledge
description: Provide charging-protocol knowledge for TENJI and test-planning work. Use when the user asks to explain, compare, validate, or convert protocol behavior for PD, PPS, QC, AFC, FCP, UFCS, BC1.2, Apple divider mode, USB-C current, VOOC, or mixed legacy D+/D- coexistence, especially before writing event chains, decision tables, or Tenji mappings.
---

# Protocol Knowledge

Use this skill as the protocol interpretation layer before writing TENJI output.

## Core workflow

1. Identify the protocol family and whether the request is about:
   - official behavior
   - implementation / coexistence
   - benchmark / chip view
   - test conversion
2. Read the minimum matching reference set.
3. Separate these layers explicitly:
   - attach / baseline
   - ownership / protocol detect
   - negotiation / request
   - transition / hold
   - fallback / coexistence
4. Only after the protocol logic is clear, hand off to event chain or Tenji mapping.

## Reference map

- `references/official/` — per-protocol notes and definitions
- `references/implementation/legacy-dpdm-decision-tree.md` — multi-protocol routing on D+/D-
- `references/implementation/legacy-dpdm-event-chain.md` — event-sequence view for legacy D+/D-
- `references/implementation/physical-interface.md` — physical interface notes
- `references/benchmark/protocol-chips.md` — controller / charger / protection chip view
- `references/STATUS-MATRIX.md` — coverage and maturity
- `references/INDEX.md` and `references/README.md` — navigation

## Working rules

- Do not collapse BC1.2, Apple divider mode, analog D+/D- protocols, and digital D+/D- protocols into one vague flow.
- State preconditions clearly.
- If a protocol path depends on a baseline state or previous negotiated state, say so explicitly.
- When protocol coexistence exists, describe arbitration order and fallback order.
- Keep terminology consistent with the protocol source material.

## Hand-off rule

When the user ultimately wants test execution content, convert protocol knowledge into one of these intermediate forms before writing rows:
- event chain
- decision table
- test fields
- B~N mapping
