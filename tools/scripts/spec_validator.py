#!/usr/bin/env python3
"""
TENJI spec validator
"""

from __future__ import annotations

import json
import re
import sys
from typing import Any, Dict, List

from memory_rules import apply_memory_rules
from spec_normalizer import normalize_spec


TIME_UNIT_RE = re.compile(r"^\s*\d+(?:\.\d+)?\s*(?:ns|us|ms|s)\s*$", re.IGNORECASE)
FORCE_V_RE = re.compile(r"ForceV\s+([0-9]+(?:\.[0-9]+)?)\s*([munkM]?V)", re.IGNORECASE)
INVALID_HEX_RE = re.compile(r"\b[0-9A-Fa-f]+h\b")
TMU_COMMAND_RE = re.compile(r"^(MeasFreq|MeasDuty|MeasPeriod|MeasWidth|MeasRise|MeasFall)", re.IGNORECASE)


def _merge_memory_rules(*rule_groups: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    merged: List[Dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()

    for rules in rule_groups:
        for rule in rules or []:
            if not isinstance(rule, dict):
                continue
            key = (
                str(rule.get("id") or ""),
                str(rule.get("source") or ""),
                str(rule.get("text_excerpt") or rule.get("text") or ""),
            )
            if key in seen:
                continue
            seen.add(key)
            merged.append(
                {
                    "id": str(rule.get("id") or ""),
                    "category": str(rule.get("category") or ""),
                    "source": str(rule.get("source") or ""),
                    "text_excerpt": str(rule.get("text_excerpt") or rule.get("text") or ""),
                    "score": rule.get("score", ""),
                }
            )

    return merged


def _merge_string_lists(*groups: List[str]) -> List[str]:
    merged: List[str] = []
    seen: set[str] = set()
    for group in groups:
        for value in group or []:
            text = str(value or "").strip()
            if not text or text in seen:
                continue
            seen.add(text)
            merged.append(text)
    return merged


def _merge_context_preview(*previews: str) -> str:
    merged = _merge_string_lists([preview for preview in previews if str(preview or "").strip()])
    return " | ".join(merged)


def _parse_voltage_to_volts(value: Any) -> float | None:
    text = str(value or "").strip()
    if not text:
        return None

    match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*([munkM]?V)", text, re.IGNORECASE)
    if not match:
        return None

    number = float(match.group(1))
    unit = match.group(2).lower()
    factors = {
        "uv": 1e-6,
        "mv": 1e-3,
        "v": 1.0,
        "kv": 1e3,
    }
    return number * factors.get(unit, 1.0)


def _validate_action(spec: Dict[str, Any], errors: List[str]) -> None:
    if spec.get("action") not in {"generate", "append"}:
        errors.append(f"action 非法：{spec.get('action')}")


def _validate_collections(spec: Dict[str, Any], errors: List[str]) -> None:
    if not isinstance(spec.get("pinmap"), list):
        errors.append("pinmap 必須是 list")
    if not isinstance(spec.get("test_items"), list):
        errors.append("test_items 必須是 list")
    if not isinstance(spec.get("power_sequence"), dict):
        errors.append("power_sequence 必須是 dict")


def _pin_name_set(spec: Dict[str, Any]) -> set[str]:
    return {
        str(pin.get("pin_name") or pin.get("pin") or "").strip()
        for pin in spec.get("pinmap", [])
        if str(pin.get("pin_name") or pin.get("pin") or "").strip()
    }


def _pin_voltage_floor_map(spec: Dict[str, Any]) -> Dict[str, float]:
    floors: Dict[str, float] = {}
    for pin in spec.get("pinmap", []):
        name = str(pin.get("pin_name") or pin.get("pin") or "").strip()
        if not name:
            continue
        voltages = [
            _parse_voltage_to_volts(pin.get("N")),
            _parse_voltage_to_volts(pin.get("O")),
            _parse_voltage_to_volts(pin.get("ur0")),
            _parse_voltage_to_volts(pin.get("ur1")),
        ]
        valid = [v for v in voltages if v is not None]
        if valid:
            floors[name] = max(valid)
    return floors


def _validate_symbols(spec: Dict[str, Any], errors: List[str]) -> None:
    seen: Dict[str, int] = {}
    for idx, item in enumerate(spec.get("test_items", []), start=1):
        symbol = str(item.get("symbol") or "").strip()
        if not symbol:
            errors.append(f"第 {idx} 個 test item 缺少 symbol")
            continue
        if symbol in seen:
            errors.append(f"symbol 重複：{symbol}（第 {seen[symbol]} 與第 {idx} 項）")
        else:
            seen[symbol] = idx


def _validate_commands(
    spec: Dict[str, Any],
    errors: List[str],
    warnings: List[str],
) -> None:
    pin_names = _pin_name_set(spec)
    voltage_floors = _pin_voltage_floor_map(spec)

    for item in spec.get("test_items", []):
        item_name = str(item.get("name") or item.get("test_item") or "<unnamed>")
        symbol = str(item.get("symbol") or "")
        display_name = f"{item_name} ({symbol})" if symbol else item_name
        
        commands = item.get("commands", [])
        if not isinstance(commands, list):
            errors.append(f"{display_name}: commands 必須是 list")
            continue

        for idx, cmd in enumerate(commands):
            cmd_name = str(cmd.get("cmd") or "").strip()
            pin = str(cmd.get("pin") or "").strip()
            params = str(cmd.get("params") or "").strip()
            if not cmd_name:
                warnings.append(f"{display_name}: 第 {idx + 1} 條 command 缺少 cmd")
                continue

            if cmd_name.lower() == "wait" and not TIME_UNIT_RE.match(params):
                errors.append(f"{display_name}: Wait 參數缺少合法時間單位：{params or '<empty>'}")

            if INVALID_HEX_RE.search(params) or INVALID_HEX_RE.search(str(item.get("pseudo_code") or "")):
                errors.append(f"{display_name}: 偵測到非法 hex 格式（請改用 0x 開頭）")

            if pin and pin_names and pin not in pin_names:
                errors.append(f"{display_name}: 指令 pin `{pin}` 不存在於 pinmap")

            if TMU_COMMAND_RE.match(cmd_name):
                if not symbol.endswith("_TMU"):
                    errors.append(f"{display_name}: TMU/頻率類量測的 symbol 必須以 _TMU 結尾")

            if cmd_name in {"TuneV", "TuneI"}:
                has_following_judge = any(
                    str(next_cmd.get("cmd") or "").startswith("Judge")
                    for next_cmd in commands[idx + 1 : idx + 2]
                )
                if not has_following_judge:
                    warnings.append(f"{item_name}: {cmd_name} 後建議下一條緊接 Judge 指令")

            if (item_name.startswith("IQ_") or item_name.startswith("Leak_")) and cmd_name == "ForceV":
                forced_v = _parse_voltage_to_volts(params)
                floor_v = voltage_floors.get(pin)
                if forced_v is not None and floor_v is not None and forced_v < floor_v:
                    errors.append(
                        f"{item_name}: ForceV {params} 低於 pin `{pin}` 的 N/O 電壓下限"
                    )


def validate_spec(spec: Dict[str, Any], existing_excel: str | None = None) -> Dict[str, Any]:
    normalized = normalize_spec(spec, existing_excel=existing_excel)
    errors: List[str] = []
    warnings: List[str] = []

    _validate_action(normalized, errors)
    _validate_collections(normalized, errors)
    _validate_symbols(normalized, errors)
    _validate_commands(normalized, errors, warnings)

    memory_result = apply_memory_rules(normalized)
    errors.extend(memory_result["errors"])
    warnings.extend(memory_result["warnings"])

    normalized.setdefault("_parser_meta", {})
    existing_memory_rules = normalized["_parser_meta"].get("memory_rules_applied", [])
    existing_memory_warnings = normalized["_parser_meta"].get("memory_warnings", [])
    existing_memory_preview = normalized["_parser_meta"].get("memory_context_preview", "")

    merged_memory_rules = _merge_memory_rules(existing_memory_rules, memory_result["memory_rules_applied"])
    merged_memory_warnings = _merge_string_lists(existing_memory_warnings, memory_result["memory_warnings"])
    merged_memory_preview = _merge_context_preview(existing_memory_preview, memory_result["memory_context_preview"])

    normalized["_parser_meta"]["memory_context_preview"] = merged_memory_preview
    normalized["_parser_meta"]["memory_rules_applied"] = merged_memory_rules
    normalized["_parser_meta"]["memory_warnings"] = merged_memory_warnings

    if normalized.get("_parser_meta", {}).get("fallback_used"):
        warnings.append("parser 使用了 fallback minimal spec，請人工確認內容")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "memory_warnings": merged_memory_warnings,
        "memory_rules_applied": merged_memory_rules,
        "memory_context_preview": merged_memory_preview,
        "normalized_spec": normalized,
        "summary": {
            "pin_count": len(normalized.get("pinmap", [])),
            "test_item_count": len(normalized.get("test_items", [])),
            "warning_count": len(warnings),
            "error_count": len(errors),
            "memory_rule_count": len(merged_memory_rules),
        },
    }


def main() -> int:
    if len(sys.argv) < 2:
        print("用法: python3 spec_validator.py <spec.json>", file=sys.stderr)
        return 1

    with open(sys.argv[1], encoding="utf-8") as fh:
        spec = json.load(fh)

    result = validate_spec(spec)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())