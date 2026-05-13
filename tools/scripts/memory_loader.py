#!/usr/bin/env python3
"""
TENJI durable memory loader

將 MEMORY / daily memory / learned / feedback 收斂成可供 parser 與 validator
共用的 query-aware brief 與規則清單。
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, List


WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
MEMORY_FILE = WORKSPACE_ROOT / "MEMORY.md"
DAILY_MEMORY_DIR = WORKSPACE_ROOT / "memory"
KNOWLEDGE_FILE = WORKSPACE_ROOT / "knowledge" / "learned.md"
FEEDBACK_FILE = WORKSPACE_ROOT / "feedback" / "feedback.jsonl"

TOKEN_RE = re.compile(r"[A-Za-z0-9_./+-]+|[\u4e00-\u9fff]{1,8}")

ALIASES = {
    "qc": {"qc", "hvdcp", "dp", "dm", "bc1.2", "bc12", "dcp", "vbus", "a口", "快充"},
    "protocol": {"protocol", "pd", "attach", "detach", "request", "trigger", "pdo", "sink", "source"},
    "os": {"os", "open", "short", "pwr_os", "fixed", "固定格式"},
    "pinmap": {"pinmap", "pin", "ur", "relay", "routing", "pin map"},
    "formula": {"formula", "judgedbl", "measv", "judgev", "電壓", "公式"},
    "tmu": {"tmu", "delay", "freq", "frequency", "duty", "period", "rise", "fall"},
    "syntax": {"0x", "hex", "wait", "judge", "symbol", "slave", "pseudo", "run", "pattern"},
}


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _tokenize(text: str) -> List[str]:
    return [token.lower() for token in TOKEN_RE.findall(text or "")]


def _rule_category(text: str) -> str:
    lowered = (text or "").lower()
    if any(keyword in lowered for keyword in ["qc", "bc1.2", "bc12", "dp/dm", "dcp", "hvdcp"]):
        return "protocol"
    if any(keyword in lowered for keyword in ["attach", "detach", "trigger", "pdo", "pd_"]):
        return "protocol"
    if any(keyword in lowered for keyword in ["pinmap", "ur", "relay"]):
        return "pinmap"
    if any(keyword in lowered for keyword in ["os", "pwr_os", "固定格式"]):
        return "format"
    if any(keyword in lowered for keyword in ["0x", "hex", "_tmu", "wait", "judge", "formula"]):
        return "syntax"
    return "general"


def _normalize_excerpt(text: str, max_len: int = 220) -> str:
    compact = re.sub(r"\s+", " ", (text or "").strip())
    if len(compact) <= max_len:
        return compact
    return compact[: max_len - 1].rstrip() + "…"


def _rule_id(source: str, index: int) -> str:
    clean = re.sub(r"[^a-zA-Z0-9_.-]+", "-", source).strip("-")
    return f"{clean}:{index}"


def _iter_markdown_bullets(text: str) -> Iterable[str]:
    for raw_line in (text or "").splitlines():
        line = raw_line.strip()
        if line.startswith("- "):
            yield line[2:].strip()


def _extract_markdown_rules(text: str, source: str) -> List[Dict[str, Any]]:
    rules: List[Dict[str, Any]] = []
    seen: set[str] = set()
    for index, bullet in enumerate(_iter_markdown_bullets(text), start=1):
        excerpt = _normalize_excerpt(bullet)
        if not excerpt or excerpt in seen:
            continue
        seen.add(excerpt)
        rules.append(
            {
                "id": _rule_id(source, index),
                "source": source,
                "category": _rule_category(excerpt),
                "text": excerpt,
                "tokens": _tokenize(excerpt),
            }
        )
    return rules


def _extract_feedback_rules(text: str, source: str) -> List[Dict[str, Any]]:
    allowed_types = {"learn", "correction", "validator_failure"}
    rules: List[Dict[str, Any]] = []
    seen: set[str] = set()

    for index, line in enumerate((text or "").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if payload.get("type") not in allowed_types:
            continue
        content = _normalize_excerpt(str(payload.get("content") or payload.get("reason") or ""), max_len=260)
        if not content or content in seen:
            continue
        seen.add(content)
        rules.append(
            {
                "id": _rule_id(source, index),
                "source": source,
                "category": _rule_category(content),
                "text": content,
                "tokens": _tokenize(content),
            }
        )
    return rules


@lru_cache(maxsize=1)
def load_memory_rules(ic_name: str | None = None) -> List[Dict[str, Any]]:
    collected: List[Dict[str, Any]] = []
    collected.extend(_extract_markdown_rules(_read_text(MEMORY_FILE), "MEMORY.md"))

    # 新增：優先讀取專案專屬記憶檔
    if ic_name:
        clean_ic = re.sub(r"[^a-zA-Z0-9]+", "_", ic_name).upper()
        project_file = WORKSPACE_ROOT / "knowledge" / f"{clean_ic}.md"
        if project_file.exists():
            collected.extend(_extract_markdown_rules(_read_text(project_file), f"knowledge/{project_file.name}"))

    if DAILY_MEMORY_DIR.exists():
        for path in sorted(DAILY_MEMORY_DIR.glob("*.md")):
            collected.extend(_extract_markdown_rules(_read_text(path), f"memory/{path.name}"))

    collected.extend(_extract_markdown_rules(_read_text(KNOWLEDGE_FILE), "knowledge/learned.md"))
    collected.extend(_extract_feedback_rules(_read_text(FEEDBACK_FILE), "feedback/feedback.jsonl"))

    deduped: List[Dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for rule in collected:
        key = (rule.get("category", ""), rule.get("text", ""))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(rule)
    return deduped


def _alias_bonus(rule_text: str, query_tokens: set[str]) -> int:
    lowered = rule_text.lower()
    bonus = 0
    for alias_tokens in ALIASES.values():
        if query_tokens.intersection(alias_tokens) and any(token in lowered for token in alias_tokens):
            bonus += 2
    return bonus


def _score_rule(rule: Dict[str, Any], query: str) -> int:
    query_tokens = set(_tokenize(query))
    if not query_tokens:
        return 0

    rule_tokens = set(rule.get("tokens") or [])
    overlap = len(query_tokens.intersection(rule_tokens))
    bonus = _alias_bonus(rule.get("text", ""), query_tokens)
    source_bonus = 1 if str(rule.get("source", "")).startswith("MEMORY") else 0
    return overlap * 4 + bonus + source_bonus


def select_relevant_rules(query: str, limit: int = 8) -> List[Dict[str, Any]]:
    scored: List[Dict[str, Any]] = []
    for rule in load_memory_rules():
        score = _score_rule(rule, query)
        if score <= 0:
            continue
        enriched = dict(rule)
        enriched["score"] = score
        scored.append(enriched)

    if not scored:
        return []

    scored.sort(key=lambda item: (-int(item.get("score", 0)), item.get("source", ""), item.get("id", "")))
    return scored[:limit]


def build_memory_brief(query: str, limit: int = 8, max_chars: int = 2400) -> Dict[str, Any]:
    selected = select_relevant_rules(query, limit=limit)
    if not selected:
        return {
            "brief": "",
            "context_preview": "",
            "rules_applied": [],
        }

    lines = ["", "## Durable memory rules", "請優先遵守以下已驗證規則："]
    rules_applied: List[Dict[str, Any]] = []
    preview_lines: List[str] = []

    current_len = sum(len(line) for line in lines)
    for rule in selected:
        excerpt = _normalize_excerpt(rule.get("text", ""), max_len=180)
        line = f"- [{rule.get('category', 'general')}] {excerpt}"
        projected = current_len + len(line) + 1
        if projected > max_chars:
            break
        lines.append(line)
        current_len = projected
        rules_applied.append(
            {
                "id": rule.get("id", ""),
                "category": rule.get("category", ""),
                "source": rule.get("source", ""),
                "text_excerpt": excerpt,
                "score": rule.get("score", 0),
            }
        )
        preview_lines.append(f"[{rule.get('category', 'general')}] {excerpt}")

    return {
        "brief": "\n".join(lines) if rules_applied else "",
        "context_preview": " | ".join(preview_lines[:4]),
        "rules_applied": rules_applied,
    }


__all__ = [
    "build_memory_brief",
    "load_memory_rules",
    "select_relevant_rules",
]