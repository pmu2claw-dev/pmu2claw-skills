from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GateResult:
    ok: bool
    hard_failures: list[str] = field(default_factory=list)
    soft_warnings: list[str] = field(default_factory=list)
    fidelity_score: int = 100
    lineage: dict[str, Any] = field(default_factory=dict)


def _fidelity_score(spec: dict[str, Any], validation_errors: list[str], validation_warnings: list[str]) -> int:
    items = spec.get("test_items") if isinstance(spec.get("test_items"), list) else []
    item_count = len(items)

    score = 100
    score -= min(len(validation_errors) * 20, 60)
    score -= min(len(validation_warnings) * 5, 20)

    if item_count == 0:
        score -= 20

    for item in items:
        commands = item.get("commands", []) if isinstance(item, dict) else []
        if not commands:
            score -= 3

    return max(0, min(100, score))


def evaluate_gates(
    spec: dict[str, Any],
    validation_errors: list[str],
    validation_warnings: list[str],
    strict: bool = False,
) -> GateResult:
    hard_failures: list[str] = []
    soft_warnings: list[str] = []

    action = spec.get("action")
    if action not in {"generate", "append"}:
        hard_failures.append(f"Invalid action for gate: {action}")

    if validation_errors:
        hard_failures.extend(validation_errors)

    if validation_warnings:
        soft_warnings.extend(validation_warnings)

    if strict and validation_warnings:
        hard_failures.append("Strict gate enabled: warnings are treated as failures")

    fidelity = _fidelity_score(spec, validation_errors, validation_warnings)

    parser_meta = spec.get("_parser_meta", {}) if isinstance(spec.get("_parser_meta"), dict) else {}
    lineage = {
        "action": action,
        "symbol_count": len(spec.get("test_items", []) if isinstance(spec.get("test_items"), list) else []),
        "memory_rules_applied": parser_meta.get("memory_rules_applied", []),
        "fallback_used": bool(parser_meta.get("fallback_used", False)),
        "repaired": bool(parser_meta.get("repaired", False)),
    }

    ok = len(hard_failures) == 0
    return GateResult(
        ok=ok,
        hard_failures=hard_failures,
        soft_warnings=soft_warnings,
        fidelity_score=fidelity,
        lineage=lineage,
    )
