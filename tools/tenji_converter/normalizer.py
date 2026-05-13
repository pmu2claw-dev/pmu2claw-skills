from __future__ import annotations

from copy import deepcopy
from typing import Any


DEFAULT_SPEC: dict[str, Any] = {
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


def _normalize_pin_entry(entry: Any) -> dict[str, Any]:
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


def _normalize_power_entry(entry: Any) -> dict[str, Any]:
    raw = entry if isinstance(entry, dict) else {"pin": "", "action": _safe_str(entry)}
    return {
        "pin": _safe_str(raw.get("pin") or raw.get("name")),
        "action": _safe_str(raw.get("action") or raw.get("voltage")),
        "voltage": _safe_str(raw.get("voltage") or raw.get("action")),
        "delay": _safe_str(raw.get("delay")),
        "max_v": _safe_str(raw.get("max_v")),
    }


def _normalize_power_sequence(value: Any) -> dict[str, list[dict[str, Any]]]:
    if isinstance(value, list):
        return {"PWR_Normal": [_normalize_power_entry(item) for item in value]}

    if not isinstance(value, dict):
        return {}

    normalized: dict[str, list[dict[str, Any]]] = {}
    for group_name, entries in value.items():
        if isinstance(entries, list):
            normalized[_safe_str(group_name)] = [_normalize_power_entry(item) for item in entries]
    return normalized


def _normalize_command(entry: Any) -> dict[str, str]:
    raw = entry if isinstance(entry, dict) else {"cmd": _safe_str(entry)}
    value = _safe_str(raw.get("params") or raw.get("value"))
    return {
        "cmd": _safe_str(raw.get("cmd")),
        "pin": _safe_str(raw.get("pin")),
        "params": value,
        "value": value,
    }


def _normalize_test_item(entry: Any, index: int) -> dict[str, Any]:
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
        "category": _safe_str(raw.get("category") or "General"),
        "scenario": _safe_str(raw.get("scenario") or raw.get("description")),
        "pwr_seq": _safe_str(raw.get("pwr_seq")),
        "pseudo_code": _safe_str(raw.get("pseudo_code")),
        "run_pattern": _safe_str(raw.get("run_pattern")),
        "measure_cond": _safe_str(raw.get("measure_cond")),
        "description": _safe_str(raw.get("description")),
        "expected": _safe_str(raw.get("expected")),
        "lower": _safe_str(raw.get("lower") or raw.get("min")),
        "min": _safe_str(raw.get("min") or raw.get("lower")),
        "typ": _safe_str(raw.get("typ")),
        "upper": _safe_str(raw.get("upper") or raw.get("max")),
        "max": _safe_str(raw.get("max") or raw.get("upper")),
        "unit": _safe_str(raw.get("unit")),
        "note": _safe_str(raw.get("note")),
        "comment": _safe_str(raw.get("comment") or raw.get("note")),
        "judge": _safe_str(raw.get("judge")),
        "ds_page": _safe_str(raw.get("ds_page")),
        "ds_sec": _safe_str(raw.get("ds_sec")),
        "qc_min": _safe_str(raw.get("qc_min")),
        "qc_max": _safe_str(raw.get("qc_max")),
        "commands": [_normalize_command(cmd) for cmd in commands],
    }


def _normalize_revisions(revisions: Any) -> list[dict[str, str]]:
    if not isinstance(revisions, list):
        return []

    result: list[dict[str, str]] = []
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


def _normalize_string_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return [_safe_str(value) for value in values if _safe_str(value)]


def _normalize_memory_rules(rules: Any) -> list[dict[str, Any]]:
    if not isinstance(rules, list):
        return []

    normalized_rules: list[dict[str, Any]] = []
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


def _to_legacy_items(test_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    legacy: list[dict[str, Any]] = []
    for item in test_items:
        legacy.append(
            {
                "category": item.get("category", "General"),
                "scenario": item.get("scenario", item.get("description", "")),
                "power": item.get("pwr_seq", ""),
                "block": item.get("name", item.get("test_item", "")),
                "symbol": item.get("symbol", ""),
                "measure_cond": item.get("measure_cond", ""),
                "commands": item.get("commands", []),
                "expected": item.get("expected", ""),
                "lower": item.get("lower", item.get("min", "")),
                "upper": item.get("upper", item.get("max", "")),
                "unit": item.get("unit", ""),
                "judge": item.get("judge", ""),
                "comment": item.get("comment", item.get("note", "")),
            }
        )
    return legacy


def normalize_spec(spec: dict[str, Any] | None, existing_excel: str | None = None) -> dict[str, Any]:
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

    test_items = raw.get("test_items")
    if not isinstance(test_items, list):
        test_items = raw.get("items") if isinstance(raw.get("items"), list) else []

    normalized["test_items"] = [
        _normalize_test_item(item, index + 1) for index, item in enumerate(test_items)
    ]
    normalized["items"] = _to_legacy_items(normalized["test_items"])

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
