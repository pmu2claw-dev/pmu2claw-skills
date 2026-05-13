#!/usr/bin/env python3
"""
TENJI spec normalizer

把 parser/舊格式/半結構化 spec 統一成 generate_excel 可接受的標準格式。
"""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from typing import Any, Dict, List


DEFAULT_SPEC = {
    "action": "generate",
    "ic_name": "Unknown IC",
    "project": "Unknown Project",
    "notes": "",
    "pinmap": [],
    "power_sequence": {},
    "test_items": [],
    "revisions": [],
    "i2c_sequences": [],
}


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def _normalize_action(action: Any, existing_excel: str | None = None) -> str:
    value = _safe_str(action).lower()
    if value in {"generate", "append"}:
        return value
    return "append" if existing_excel else "generate"


def _normalize_pin_entry(entry: Any) -> Dict[str, Any]:
    raw = entry if isinstance(entry, dict) else {"pin": entry}
    pin_name = _safe_str(
        raw.get("pin_name")
        or raw.get("pin")
        or raw.get("name")
        or raw.get("pinName")
    )
    return {
        "power_monitor": _safe_str(raw.get("power_monitor") or raw.get("type")),
        "pin_name": pin_name,
        "pin": pin_name,
        "type": _safe_str(raw.get("type")),
        "instrument": _safe_str(raw.get("instrument")),
        "mvi_pin": _safe_str(raw.get("mvi_pin") or raw.get("instrument")),
        "mvi_ch": _safe_str(raw.get("mvi_ch")),
        "mcpmu_ch": _safe_str(raw.get("mcpmu_ch")),
        "pe_ref": _safe_str(raw.get("pe_ref")),
        "pe_name": _safe_str(raw.get("pe_name")),
        "pe_ch": _safe_str(raw.get("pe_ch")),
        "ur_num": _safe_str(raw.get("ur_num")),
        "ur0": _safe_str(raw.get("ur0") or raw.get("N")),
        "ur1": _safe_str(raw.get("ur1") or raw.get("O")),
        "up_diode": _safe_str(raw.get("up_diode")),
        "dn_diode": _safe_str(raw.get("dn_diode")),
        "N": _safe_str(raw.get("N") or raw.get("ur0")),
        "O": _safe_str(raw.get("O") or raw.get("ur1")),
    }


def _normalize_power_entry(entry: Any) -> Dict[str, Any]:
    raw = entry if isinstance(entry, dict) else {"pin": "", "action": _safe_str(entry)}
    return {
        "pin": _safe_str(raw.get("pin") or raw.get("name")),
        "action": _safe_str(raw.get("action") or raw.get("voltage")),
        "voltage": _safe_str(raw.get("voltage") or raw.get("action")),
        "delay": _safe_str(raw.get("delay")),
        "max_v": _safe_str(raw.get("max_v")),
    }


def _normalize_power_sequence(value: Any) -> Dict[str, List[Dict[str, Any]]]:
    if isinstance(value, list):
        return {"PWR_Normal": [_normalize_power_entry(item) for item in value]}

    if not isinstance(value, dict):
        return {}

    normalized = {}
    for group_name, entries in value.items():
        if isinstance(entries, list):
            normalized[_safe_str(group_name)] = [_normalize_power_entry(item) for item in entries]
    return normalized


def _normalize_command(entry: Any) -> Dict[str, str]:
    raw = entry if isinstance(entry, dict) else {"cmd": _safe_str(entry)}
    return {
        "cmd": _safe_str(raw.get("cmd")),
        "pin": _safe_str(raw.get("pin")),
        "params": _safe_str(raw.get("params")),
    }


def _normalize_test_item(entry: Any, index: int) -> Dict[str, Any]:
    raw = entry if isinstance(entry, dict) else {"name": _safe_str(entry)}
    name = _safe_str(raw.get("name") or raw.get("test_item") or f"TestItem_{index}")
    symbol = _safe_str(raw.get("symbol") or name)
    commands = raw.get("commands", [])
    if not isinstance(commands, list):
        commands = []

    return {
        "bin": _safe_str(raw.get("bin")),
        "name": name,
        "test_item": _safe_str(raw.get("test_item") or name),
        "symbol": symbol,
        "pwr_seq": _safe_str(raw.get("pwr_seq")),
        "pseudo_code": _safe_str(raw.get("pseudo_code")),
        "run_pattern": _safe_str(raw.get("run_pattern")),
        "measure_cond": _safe_str(raw.get("measure_cond")),
        "description": _safe_str(raw.get("description")),
        "min": _safe_str(raw.get("min")),
        "typ": _safe_str(raw.get("typ")),
        "max": _safe_str(raw.get("max")),
        "unit": _safe_str(raw.get("unit")),
        "note": _safe_str(raw.get("note")),
        "ds_page": _safe_str(raw.get("ds_page")),
        "ds_sec": _safe_str(raw.get("ds_sec")),
        "qc_min": _safe_str(raw.get("qc_min")),
        "qc_max": _safe_str(raw.get("qc_max")),
        "commands": [_normalize_command(cmd) for cmd in commands],
    }


def _normalize_revisions(revisions: Any) -> List[Dict[str, str]]:
    if not isinstance(revisions, list):
        return []

    result = []
    for raw in revisions:
        if not isinstance(raw, dict):
            continue
        result.append(
            {
                "date": _safe_str(raw.get("date")),
                "revision": _safe_str(raw.get("revision")),
                "reviser": _safe_str(raw.get("reviser")),
                "change": _safe_str(raw.get("change")),
            }
        )
    return result


def _normalize_string_list(values: Any) -> List[str]:
    if not isinstance(values, list):
        return []
    return [_safe_str(value) for value in values if _safe_str(value)]


def _normalize_memory_rules(rules: Any) -> List[Dict[str, Any]]:
    if not isinstance(rules, list):
        return []

    normalized_rules: List[Dict[str, Any]] = []
    for raw in rules:
        if isinstance(raw, dict):
            text_excerpt = _safe_str(raw.get("text_excerpt") or raw.get("text") or raw.get("content"))
            if not text_excerpt:
                continue
            normalized_rules.append(
                {
                    "id": _safe_str(raw.get("id")),
                    "category": _safe_str(raw.get("category")),
                    "source": _safe_str(raw.get("source")),
                    "text_excerpt": text_excerpt,
                    "score": _safe_str(raw.get("score")),
                }
            )
        else:
            text_excerpt = _safe_str(raw)
            if text_excerpt:
                normalized_rules.append(
                    {
                        "id": "",
                        "category": "",
                        "source": "",
                        "text_excerpt": text_excerpt,
                        "score": "",
                    }
                )
    return normalized_rules


def normalize_spec(spec: Dict[str, Any] | None, existing_excel: str | None = None) -> Dict[str, Any]:
    raw = deepcopy(spec or {})
    normalized = deepcopy(DEFAULT_SPEC)

    normalized["action"] = _normalize_action(raw.get("action"), existing_excel=existing_excel)
    normalized["ic_name"] = _safe_str(raw.get("ic_name"), DEFAULT_SPEC["ic_name"])
    normalized["project"] = _safe_str(raw.get("project"), DEFAULT_SPEC["project"])
    normalized["notes"] = _safe_str(raw.get("notes"))
    normalized["i2c_sequences"] = raw.get("i2c_sequences", []) if isinstance(raw.get("i2c_sequences", []), list) else []

    pin_entries = raw.get("pinmap")
    if not isinstance(pin_entries, list):
        pin_entries = raw.get("pins", []) if isinstance(raw.get("pins", []), list) else []
    normalized["pinmap"] = [_normalize_pin_entry(item) for item in pin_entries]

    normalized["power_sequence"] = _normalize_power_sequence(raw.get("power_sequence"))

    test_items = raw.get("test_items", [])
    if not isinstance(test_items, list):
        test_items = []
    normalized["test_items"] = [
        _normalize_test_item(item, index + 1) for index, item in enumerate(test_items)
    ]

    normalized["revisions"] = _normalize_revisions(raw.get("revisions", []))

    parser_meta = raw.get("_parser_meta", {}) if isinstance(raw.get("_parser_meta"), dict) else {}
    normalized["_parser_meta"] = {
        "fallback_used": bool(parser_meta.get("fallback_used", False)),
        "existing_excel": _safe_str(existing_excel or parser_meta.get("existing_excel")),
        "memory_context_preview": _safe_str(parser_meta.get("memory_context_preview")),
        "memory_rules_applied": _normalize_memory_rules(parser_meta.get("memory_rules_applied")),
        "memory_warnings": _normalize_string_list(parser_meta.get("memory_warnings")),
    }

    return normalized


def main() -> int:
    if len(sys.argv) < 2:
        print("用法: python3 spec_normalizer.py <spec.json>", file=sys.stderr)
        return 1

    with open(sys.argv[1], encoding="utf-8") as fh:
        spec = json.load(fh)

    print(json.dumps(normalize_spec(spec), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())