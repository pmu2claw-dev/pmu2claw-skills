from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


TOKEN_RE = re.compile(r"[A-Za-z0-9_./+-]+|[\u4e00-\u9fff]{1,8}")


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text or "")]


def _iter_markdown_bullets(text: str):
    for raw_line in (text or "").splitlines():
        line = raw_line.strip()
        if line.startswith("- "):
            yield line[2:].strip()


def _normalize_excerpt(text: str, max_len: int = 220) -> str:
    compact = re.sub(r"\s+", " ", (text or "").strip())
    if len(compact) <= max_len:
        return compact
    return compact[: max_len - 1].rstrip() + "…"


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


def _extract_markdown_rules(text: str, source: str) -> list[dict[str, Any]]:
    rules: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, bullet in enumerate(_iter_markdown_bullets(text), start=1):
        excerpt = _normalize_excerpt(bullet)
        if not excerpt or excerpt in seen:
            continue
        seen.add(excerpt)
        rules.append(
            {
                "id": f"{source}:{index}",
                "source": source,
                "category": _rule_category(excerpt),
                "text": excerpt,
                "tokens": _tokenize(excerpt),
            }
        )
    return rules


def _extract_feedback_rules(text: str, source: str) -> list[dict[str, Any]]:
    allowed_types = {"learn", "correction", "validator_failure"}
    rules: list[dict[str, Any]] = []
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
                "id": f"{source}:{index}",
                "source": source,
                "category": _rule_category(content),
                "text": content,
                "tokens": _tokenize(content),
            }
        )
    return rules


def load_memory_rules(memory_root: Path | None = None, ic_name: str | None = None) -> list[dict[str, Any]]:
    if memory_root is None:
        return []

    collected: list[dict[str, Any]] = []
    memory_file = memory_root / "MEMORY.md"
    collected.extend(_extract_markdown_rules(_read_text(memory_file), "MEMORY.md"))

    knowledge_dir = memory_root / "knowledge"
    if ic_name:
        clean_ic = re.sub(r"[^a-zA-Z0-9]+", "_", ic_name).upper()
        project_file = knowledge_dir / f"{clean_ic}.md"
        if project_file.exists():
            collected.extend(
                _extract_markdown_rules(_read_text(project_file), f"knowledge/{project_file.name}")
            )

    daily_memory_dir = memory_root / "memory"
    if daily_memory_dir.exists():
        for path in sorted(daily_memory_dir.glob("*.md")):
            collected.extend(_extract_markdown_rules(_read_text(path), f"memory/{path.name}"))

    learned_file = knowledge_dir / "learned.md"
    collected.extend(_extract_markdown_rules(_read_text(learned_file), "knowledge/learned.md"))

    feedback_file = memory_root / "feedback" / "feedback.jsonl"
    collected.extend(_extract_feedback_rules(_read_text(feedback_file), "feedback/feedback.jsonl"))

    deduped: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for rule in collected:
        key = (str(rule.get("category", "")), str(rule.get("text", "")))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(rule)
    return deduped


def _score_rule(rule: dict[str, Any], query: str) -> int:
    query_tokens = set(_tokenize(query))
    if not query_tokens:
        return 0
    rule_tokens = set(rule.get("tokens") or [])
    overlap = len(query_tokens.intersection(rule_tokens))
    source_bonus = 1 if str(rule.get("source", "")).startswith("MEMORY") else 0
    return overlap * 4 + source_bonus


def select_relevant_rules(query: str, memory_root: Path | None = None, limit: int = 8, ic_name: str | None = None) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    for rule in load_memory_rules(memory_root=memory_root, ic_name=ic_name):
        score = _score_rule(rule, query)
        if score <= 0:
            continue
        enriched = dict(rule)
        enriched["score"] = score
        scored.append(enriched)

    scored.sort(key=lambda item: (-int(item.get("score", 0)), str(item.get("source", "")), str(item.get("id", ""))))
    return scored[:limit]


def build_memory_brief(
    query: str,
    memory_root: Path | None = None,
    limit: int = 8,
    max_chars: int = 2400,
    ic_name: str | None = None,
) -> dict[str, Any]:
    selected = select_relevant_rules(
        query=query,
        memory_root=memory_root,
        limit=limit,
        ic_name=ic_name,
    )
    if not selected:
        return {"brief": "", "context_preview": "", "rules_applied": []}

    lines = ["", "## Durable memory rules", "請優先遵守以下已驗證規則："]
    rules_applied: list[dict[str, Any]] = []
    preview_lines: list[str] = []

    current_len = sum(len(line) for line in lines)
    for rule in selected:
        excerpt = _normalize_excerpt(str(rule.get("text", "")), max_len=180)
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
