from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .memory_loader import build_memory_brief


ATTACH_RE = re.compile(
    r"\b(attach(?:[_ /-]?(?:sink|source))?|detach(?:[_ /-]?(?:sink|source))?|atatch|插入|拔除|插拔)\b",
    re.IGNORECASE,
)
TRIGGER_RE = re.compile(r"\b(trigger|dp/?dm|bc1\.2|bc12|pd_command|pd_req|request|qc|hvdcp|dcp)\b", re.IGNORECASE)
JUDGE_RE = re.compile(r"\bjudge[a-z]*\b", re.IGNORECASE)
MEASV_RE = re.compile(r"\bmeasv\b|vbus", re.IGNORECASE)
FORMULA_RE = re.compile(r"\bformula(?:_gby)?\b", re.IGNORECASE)
JUDGEDBL_RE = re.compile(r"\bjudgedbl\b", re.IGNORECASE)
WAIT_LINE_RE = re.compile(r"^\s*wait\b", re.IGNORECASE)
RUN_PATTERN_RE = re.compile(r"^\s*run\s+pattern\b|^\s*run_pattern\b", re.IGNORECASE)
QC_RE = re.compile(r"\b(qc|hvdcp|bc1\.2|bc12|dcp|dp/?dm)\b", re.IGNORECASE)
PROTOCOL_RE = re.compile(r"\b(protocol|pd|pdo|attach|detach|request|trigger|sink|source|vbus)\b", re.IGNORECASE)
UR_RE = re.compile(r"\bur\s*k?\d+\b|\bur[_ ]k\d+\b", re.IGNORECASE)
OS_RE = re.compile(r"\b(os|open\s*/?short|pwr_os)\b", re.IGNORECASE)
RESISTANCE_HINT_RE = re.compile(r"\b(res|resistance|open short|short)\b", re.IGNORECASE)


def _command_lines(item: dict[str, Any]) -> list[str]:
    commands = item.get("commands", [])
    lines: list[str] = []
    if isinstance(commands, list):
        for command in commands:
            if not isinstance(command, dict):
                continue
            cmd = str(command.get("cmd") or "").strip()
            pin = str(command.get("pin") or "").strip()
            params = str(command.get("params") or command.get("value") or "").strip()
            parts = [part for part in [cmd, pin, params] if part]
            if parts:
                lines.append(" ".join(parts))
    return lines


def _item_lines(item: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for field in ["measure_cond", "pseudo_code", "run_pattern"]:
        value = str(item.get(field) or "")
        if value.strip():
            lines.extend([line.strip() for line in value.splitlines() if line.strip()])
    lines.extend(_command_lines(item))
    return lines


def _item_text(item: dict[str, Any]) -> str:
    fragments = [
        str(item.get("name") or ""),
        str(item.get("test_item") or ""),
        str(item.get("symbol") or ""),
        str(item.get("description") or ""),
        str(item.get("note") or ""),
        str(item.get("measure_cond") or ""),
        str(item.get("pseudo_code") or ""),
        str(item.get("run_pattern") or ""),
        "\n".join(_command_lines(item)),
    ]
    return "\n".join(fragment for fragment in fragments if fragment).strip()


def _spec_query(spec: dict[str, Any]) -> str:
    chunks = [
        str(spec.get("project") or ""),
        str(spec.get("ic_name") or ""),
        str(spec.get("notes") or ""),
    ]
    for item in spec.get("test_items", [])[:6]:
        chunks.append(_item_text(item))
    return "\n".join(chunk for chunk in chunks if chunk).strip()


def _is_os_item(item: dict[str, Any]) -> bool:
    text = _item_text(item)
    symbol = str(item.get("symbol") or "")
    return bool(OS_RE.search(text) or symbol.upper().startswith("OS"))


def _is_qc_like(item: dict[str, Any]) -> bool:
    return bool(QC_RE.search(_item_text(item)))


def _is_protocol_like(item: dict[str, Any]) -> bool:
    return bool(PROTOCOL_RE.search(_item_text(item)) or _is_qc_like(item))


def _judge_count(item: dict[str, Any]) -> int:
    return sum(1 for line in _item_lines(item) if JUDGE_RE.search(line))


def _has_bc12_context(spec: dict[str, Any]) -> bool:
    return any(re.search(r"bc1\.2|bc12", _item_text(item), re.IGNORECASE) for item in spec.get("test_items", []))


def _has_ur_mapping(spec: dict[str, Any]) -> bool:
    for pin in spec.get("pinmap", []):
        if str(pin.get("ur_num") or "").strip():
            return True
    return False


def apply_memory_rules(spec: dict[str, Any], memory_root: Path | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    memory_context = build_memory_brief(
        query=_spec_query(spec),
        memory_root=memory_root,
        limit=6,
        max_chars=1600,
        ic_name=str(spec.get("ic_name") or "") or None,
    )
    applied_rules = list(memory_context.get("rules_applied", []))

    bc12_present = _has_bc12_context(spec)
    ur_mapping_present = _has_ur_mapping(spec)
    any_qc_item = any(_is_qc_like(item) for item in spec.get("test_items", []))

    for item in spec.get("test_items", []):
        item_name = str(item.get("name") or item.get("test_item") or "<unnamed>")
        text = _item_text(item)
        lines = _item_lines(item)

        if _is_protocol_like(item):
            if not ATTACH_RE.search(text):
                warnings.append(f"{item_name}: protocol 測項未偵測到 Attach/Detach，請確認是否為連續流程的中間步驟")
            if not TRIGGER_RE.search(text):
                errors.append(f"{item_name}: protocol 測項缺少關鍵 Trigger (PD_req/DP-DM/BC1.2) 指令")
            if (MEASV_RE.search(text) or QC_RE.search(text)) and not JUDGE_RE.search(text):
                errors.append(f"{item_name}: 偵測到量測動作但缺少 Judge 判定指令")

        if _is_os_item(item):
            symbol = str(item.get("symbol") or "").upper()
            if symbol.startswith("OS"):
                extra_commands = bool(item.get("commands"))
                extra_fields = any(
                    str(item.get(field) or "").strip()
                    for field in ["measure_cond", "pseudo_code", "run_pattern"]
                )
                pwr_seq = str(item.get("pwr_seq") or "")
                if (extra_commands or extra_fields) and pwr_seq != "PWR_OS":
                    errors.append(f"{item_name}: OS 測項 (PWR_OS) 應維持固定空格式，請勿加入額外指令")

        judge_count = _judge_count(item)
        if judge_count > 1:
            errors.append(f"{item_name}: 單一 test item 不應含多個 Judge，請拆成多行事件鏈")

        wait_streak = 0
        run_pattern_streak = 0
        for line in lines:
            if WAIT_LINE_RE.search(line):
                wait_streak += 1
                if wait_streak >= 2:
                    warnings.append(f"{item_name}: 偵測到連續 Wait，請確認是否為冗餘等待")
            else:
                wait_streak = 0

            if RUN_PATTERN_RE.search(line):
                run_pattern_streak += 1
                if run_pattern_streak >= 2:
                    warnings.append(f"{item_name}: 偵測到連續 Run Pattern，請確認是否需要合併")
            else:
                run_pattern_streak = 0

        if FORMULA_RE.search(text) and not JUDGEDBL_RE.search(text):
            warnings.append(f"{item_name}: Formula 結果建議搭配 JudgeDbl 判定")

        if RESISTANCE_HINT_RE.search(text) and (not FORMULA_RE.search(text) or not JUDGEDBL_RE.search(text)):
            warnings.append(f"{item_name}: OS/RES 類判定通常應包含 Formula + JudgeDbl 組合")

        if UR_RE.search(text) and not ur_mapping_present:
            warnings.append(f"{item_name}: 使用 UR relay，但 pinmap 未提供 ur_num 映射，請勿猜測 relay 對應")

    if any_qc_item and not bc12_present:
        errors.append("QC/HVDCP 類 spec 缺少 BC1.2 前置流程")

    return {
        "errors": errors,
        "warnings": warnings,
        "memory_warnings": warnings.copy(),
        "memory_rules_applied": applied_rules,
        "memory_context_preview": memory_context.get("context_preview", ""),
    }
