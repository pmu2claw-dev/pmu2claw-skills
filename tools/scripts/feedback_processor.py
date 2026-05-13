#!/usr/bin/env python3
"""
Feedback processor: reads feedback.jsonl → updates learned.md + memory_rules.py stubs.

Each feedback.jsonl entry shape:
{
  "ts": "2026-...",
  "type": "correction|confirm|reject",
  "context": { "family": "...", "symbol": "...", "field": "...", "old": "...", "new": "..." },
  "note": "human explanation"
}

Processing:
  - correction: write rule to learned.md, bump correction_count
  - confirm: reinforce existing rule match
  - reject: flag rule for review if confirm_count < 2

Output: updated learned.md section + printed diff summary.
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

WORKSPACE = Path(__file__).parent.parent
FEEDBACK_FILE = WORKSPACE / "feedback.jsonl"
LEARNED_FILE  = WORKSPACE / "LEARNINGS.md"

SECTION_RE = re.compile(r"^##\s+(.+)$", re.MULTILINE)
RULE_HEADER_RE = re.compile(r"^###\s+(.+)$", re.MULTILINE)


def _load_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    entries = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return entries


def _load_learned(path: Path) -> str:
    if not path.exists():
        return "# TENJI Learned Rules\n\n"
    return path.read_text(encoding="utf-8")


def _rule_key(entry: Dict[str, Any]) -> str:
    ctx = entry.get("context", {})
    family = ctx.get("family", "general")
    field  = ctx.get("field", "unknown")
    return f"{family}:{field}"


def _format_rule_block(key: str, entries: List[Dict[str, Any]]) -> str:
    family, field = key.split(":", 1)
    corrections = [e for e in entries if e.get("type") == "correction"]
    confirms    = [e for e in entries if e.get("type") == "confirm"]
    rejects     = [e for e in entries if e.get("type") == "reject"]

    lines = [f"### [{family}] {field}"]
    lines.append(f"- 修正次數: {len(corrections)} | 確認: {len(confirms)} | 拒絕: {len(rejects)}")

    if corrections:
        last = corrections[-1]
        ctx = last.get("context", {})
        old = ctx.get("old", "")
        new = ctx.get("new", "")
        note = last.get("note", "")
        ts = last.get("ts", "")
        lines.append(f"- 最新修正 ({ts[:10]}): `{old}` → `{new}`")
        if note:
            lines.append(f"  - 說明: {note}")

    if len(rejects) > len(confirms):
        lines.append("- ⚠️ 拒絕次數 > 確認次數，此規則需人工複審")

    return "\n".join(lines)


def _inject_or_update_section(learned_text: str, rules_by_key: Dict[str, List[Dict]]) -> str:
    """Upsert an '## Auto-learned Corrections' section."""
    section_header = "## Auto-learned Corrections\n"
    section_end_re = re.compile(r"^##\s+(?!Auto-learned)", re.MULTILINE)

    if "## Auto-learned Corrections" in learned_text:
        # find the section start
        start = learned_text.index("## Auto-learned Corrections")
        end_match = section_end_re.search(learned_text, start + 1)
        end = end_match.start() if end_match else len(learned_text)
        prefix = learned_text[:start]
        suffix = learned_text[end:]
    else:
        prefix = learned_text.rstrip() + "\n\n"
        suffix = ""

    blocks = [section_header]
    for key in sorted(rules_by_key.keys()):
        blocks.append(_format_rule_block(key, rules_by_key[key]))
        blocks.append("")

    return prefix + "\n".join(blocks) + "\n" + suffix


def process_feedback(feedback_path: Optional[Path] = None,
                     learned_path: Optional[Path] = None,
                     dry_run: bool = False) -> Dict[str, Any]:
    fb_path = feedback_path or FEEDBACK_FILE
    ld_path = learned_path or LEARNED_FILE

    entries = _load_jsonl(fb_path)
    if not entries:
        return {"status": "ok", "processed": 0, "message": "feedback.jsonl 為空或不存在"}

    # Group by rule key
    by_key: Dict[str, List[Dict]] = defaultdict(list)
    for entry in entries:
        by_key[_rule_key(entry)].append(entry)

    learned_text = _load_learned(ld_path)
    updated_text = _inject_or_update_section(learned_text, by_key)

    added_rules = 0
    updated_rules = 0
    flagged_rules = []

    for key, group in by_key.items():
        corrections = [e for e in group if e.get("type") == "correction"]
        rejects     = [e for e in group if e.get("type") == "reject"]
        confirms    = [e for e in group if e.get("type") == "confirm"]
        if corrections:
            if key in learned_text:
                updated_rules += 1
            else:
                added_rules += 1
        if len(rejects) > len(confirms):
            flagged_rules.append(key)

    if not dry_run:
        ld_path.write_text(updated_text, encoding="utf-8")

    return {
        "status": "ok",
        "processed": len(entries),
        "rules_added": added_rules,
        "rules_updated": updated_rules,
        "rules_flagged_for_review": flagged_rules,
        "dry_run": dry_run,
    }


def main() -> int:
    dry = "--dry-run" in sys.argv
    result = process_feedback(dry_run=dry)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
