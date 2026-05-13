#!/usr/bin/env python3
"""
build_sa_index.py — Build a compact index of an SA test plan workbook.

Index is stored at ~/.openclaw/workspace-tenji/sa-index/<stem>.index.json
and includes source mtime + sha256 for automatic invalidation.

Usage:
  python3 build_sa_index.py <workbook.xlsx>          # build / refresh
  python3 build_sa_index.py <workbook.xlsx> --check  # print status (fresh/stale/missing)
  python3 build_sa_index.py <workbook.xlsx> --query "單電源2-11"  # look up a case

Index format:
{
  "source": "/abs/path/to/workbook.xlsx",
  "mtime": 1234567890.0,
  "sha256": "abcdef...",
  "built_at": "2026-05-06T13:00:00Z",
  "ic_name": "JD6628H",
  "project": "...",
  "sheets": [
    {
      "name": "單電源模式",
      "role": "testcase",
      "strategy": "direct_map",
      "row_count": 120,
      "cases": [
        {"case_id": "2-1", "row": 3, "name": "C1單插可升壓至9V", "min": "8.5", "max": "9.5", "unit": "V"}
      ]
    }
  ],
  "case_index": {
    "2-1":  {"sheet": "單電源模式", "row": 3,  "name": "..."},
    "2-2":  {"sheet": "單電源模式", "row": 24, "name": "..."}
  }
}
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent))
from sheet_classifier import (
    classify_workbook,
    _load_shared_strings, _load_sheet_names, _load_rel_map,
    _read_sheet_rows, _header_set, NS,
)

INDEX_DIR = Path.home() / ".openclaw/workspace-tenji/sa-index"

CASE_ID_RE = re.compile(r"\b(\d+)-(\d+)\b")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _index_path(source: Path) -> Path:
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    return INDEX_DIR / (source.stem + ".index.json")


def _is_fresh(source: Path, idx_path: Path) -> bool:
    if not idx_path.exists():
        return False
    try:
        stored = json.loads(idx_path.read_text(encoding="utf-8"))
        return (
            abs(stored.get("mtime", 0) - source.stat().st_mtime) < 1.0
            and stored.get("sha256") == _sha256(source)
        )
    except Exception:
        return False


def _extract_cases_from_rows(rows: List[List[str]]) -> List[Dict[str, Any]]:
    """
    Scan a testcase sheet's rows for case IDs (pattern N-N in column B or I).
    Returns list of {case_id, row (1-based), name, min, max, unit}.
    """
    if not rows:
        return []

    # Detect header row index (first row with recognisable headers)
    header_idx = 0
    for i, row in enumerate(rows[:8]):
        low = [c.strip().lower() for c in row]
        if any(h in low for h in ("no.", "no", "功能", "測試項目", "test item")):
            header_idx = i
            break

    headers = [c.strip().lower() for c in rows[header_idx]] if rows else []

    def col(row: List[str], *names: str) -> str:
        for name in names:
            try:
                idx = headers.index(name)
                return row[idx].strip() if idx < len(row) else ""
            except ValueError:
                pass
        # fallback: positional guesses
        return ""

    cases: List[Dict[str, Any]] = []
    seen_ids: set = set()

    for row_idx, row in enumerate(rows[header_idx + 1:], start=header_idx + 2):
        if not any(c.strip() for c in row):
            continue

        # Try to find a case ID anywhere in the first 4 columns
        case_id = ""
        for cell in row[:4]:
            m = CASE_ID_RE.search(cell.strip())
            if m:
                case_id = m.group(0)
                break

        if not case_id or case_id in seen_ids:
            continue
        seen_ids.add(case_id)

        name = (
            col(row, "功能", "測試項目", "test item", "description", "name")
            or next((c.strip() for c in row[1:6] if c.strip() and not CASE_ID_RE.match(c.strip())), "")
        )
        cases.append({
            "case_id": case_id,
            "row": row_idx,
            "name": name[:80],
            "min": col(row, "min", "最小"),
            "max": col(row, "max", "最大"),
            "unit": col(row, "unit", "單位"),
        })

    return cases


def build_index(source: Path, force: bool = False) -> Dict[str, Any]:
    idx_path = _index_path(source)

    if not force and _is_fresh(source, idx_path):
        return json.loads(idx_path.read_text(encoding="utf-8"))

    classified = classify_workbook(source)

    # Re-open to extract case rows from testcase sheets
    zf = zipfile.ZipFile(source, "r")
    with zf:
        shared = _load_shared_strings(zf)
        sheet_names_map = {name: rid for name, rid in _load_sheet_names(zf)}
        rel_map = _load_rel_map(zf)

        sheets_out = []
        case_index: Dict[str, Dict[str, Any]] = {}

        for sheet_info in classified["sheets"]:
            sname = sheet_info["name"]
            entry: Dict[str, Any] = {
                "name": sname,
                "role": sheet_info["role"],
                "strategy": sheet_info["strategy"],
                "row_count": sheet_info["row_count"],
                "cases": [],
            }

            if sheet_info["role"] == "testcase":
                rid = sheet_names_map.get(sname, "")
                rel_path = rel_map.get(rid, "")
                if rel_path:
                    rows = _read_sheet_rows(zf, rel_path, shared, max_rows=500)
                    cases = _extract_cases_from_rows(rows)
                    entry["cases"] = cases
                    for c in cases:
                        case_index[c["case_id"]] = {
                            "sheet": sname,
                            "row": c["row"],
                            "name": c["name"],
                            "min": c["min"],
                            "max": c["max"],
                            "unit": c["unit"],
                        }

            sheets_out.append(entry)

    index: Dict[str, Any] = {
        "source": str(source.resolve()),
        "mtime": source.stat().st_mtime,
        "sha256": _sha256(source),
        "built_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ic_name": classified.get("ic_name", ""),
        "project": classified.get("project", ""),
        "sheets": sheets_out,
        "case_index": case_index,
        "warnings": classified.get("warnings", []),
    }

    idx_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    return index


def query_case(index: Dict[str, Any], case_id: str) -> Optional[Dict[str, Any]]:
    """Look up a case by ID (exact or partial match)."""
    ci = index.get("case_index", {})
    if case_id in ci:
        return {case_id: ci[case_id]}
    # partial: e.g. "2-11" matches "2-11" but also fuzzy
    matches = {k: v for k, v in ci.items() if case_id in k}
    return matches or None


def print_summary(index: Dict[str, Any]) -> None:
    src = Path(index["source"]).name
    built = index.get("built_at", "?")
    ic = index.get("ic_name", "?")
    print(f"Index: {src}  IC={ic}  built={built}")
    total_cases = sum(len(s.get("cases", [])) for s in index["sheets"])
    print(f"Sheets: {len(index['sheets'])}  Cases indexed: {total_cases}")
    for s in index["sheets"]:
        nc = len(s.get("cases", []))
        flag = f" ({nc} cases)" if nc else ""
        print(f"  [{s['role']:12s}] {s['name']}{flag}")
    for w in index.get("warnings", []):
        print(f"  ⚠ {w}")


def main() -> int:
    p = argparse.ArgumentParser(description="Build SA workbook index")
    p.add_argument("workbook", help="SA workbook path (.xlsx/.xlsm)")
    p.add_argument("--force", action="store_true", help="Rebuild even if fresh")
    p.add_argument("--check", action="store_true", help="Check freshness only")
    p.add_argument("--query", help="Look up a case ID")
    p.add_argument("--json", action="store_true", help="Output full index as JSON")
    args = p.parse_args()

    source = Path(args.workbook).resolve()
    if not source.exists():
        print(f"Error: {source} not found", file=sys.stderr)
        return 1

    idx_path = _index_path(source)

    if args.check:
        fresh = _is_fresh(source, idx_path)
        print("fresh" if fresh else ("stale" if idx_path.exists() else "missing"))
        return 0

    index = build_index(source, force=args.force)

    if args.query:
        result = query_case(index, args.query)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.json:
        print(json.dumps(index, ensure_ascii=False, indent=2))
        return 0

    print_summary(index)
    print(f"\nIndex saved: {idx_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
