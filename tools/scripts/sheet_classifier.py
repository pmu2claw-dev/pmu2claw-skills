#!/usr/bin/env python3
"""
SA Test Plan sheet classifier — OOXML read-only.

Reads an SA Excel workbook and classifies each sheet into a role,
then recommends a mapping strategy per sheet for the TENJI pipeline.

Output JSON:
{
  "workbook": "<path>",
  "ic_name": "...",
  "project": "...",
  "sheets": [
    {
      "index": 0,
      "name": "...",
      "role": "testcase|spec_ec|spec_timing|mode_matrix|pdo_table|power_matrix|summary|unknown",
      "strategy": "direct_map|scenario_expand|spec_extract|skip",
      "tenji_ready": true|false,
      "headers": ["..."],
      "row_count": 42,
      "notes": "..."
    }
  ],
  "recommended_entry_sheet": "...",
  "warnings": ["..."]
}
"""

from __future__ import annotations

import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

NS = {
    "ss": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r":  "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

# ── headers that strongly indicate a testcase sheet ──────────────────────────
TC_HEADERS = {
    "no.", "no", "功能", "測試項目", "test item", "testitem",
    "測試方法", "預期結果", "驗證方法", "pass criteria", "result",
}
# headers that indicate an EC/Timing spec sheet
EC_HEADERS = {"parameter", "symbol", "min", "typ", "max", "unit", "condition", "電氣規格"}
TIMING_HEADERS = {"timing", "delay", "rise", "fall", "tsetup", "thold", "時序"}
# mode matrix / scenario table
MODE_HEADERS = {"mode", "模式", "功能模式", "scenario", "state", "power mode", "dual port", "雙電源"}
# PDO / power capability table
PDO_HEADERS = {"pdo", "pdo type", "voltage", "current", "power", "apdo", "epdo"}
# power-on sequence
PWRSEQ_HEADERS = {"power sequence", "pwr seq", "上電順序", "power on"}
# summary / tracker
SUMMARY_HEADERS = {"status", "owner", "pass/fail", "progress", "coverage", "total"}

SKIP_NAMES = re.compile(
    r"(cover|封面|revision|history|change\s*log|目錄|toc|index|readme|about|說明)",
    re.IGNORECASE,
)

IC_NAME_RE = re.compile(
    r"\b(JD\d{4}[A-Z]*|RT\d{4}[A-Z]*|SC\d{4}[A-Z]*|[A-Z]{2,4}\d{4}[A-Z]*)\b"
)
PROJECT_RE = re.compile(r"(?i)(project|專案|品號|part\s*no\.?)[:\s]+([^\n\r,;]+)")


def _open_zip(path: Path) -> Optional[zipfile.ZipFile]:
    try:
        return zipfile.ZipFile(path, "r")
    except Exception:
        return None


def _load_shared_strings(zf: zipfile.ZipFile) -> List[str]:
    try:
        with zf.open("xl/sharedStrings.xml") as fh:
            root = ET.parse(fh).getroot()
        strings: List[str] = []
        for si in root.findall("ss:si", NS):
            parts = [t.text or "" for t in si.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")]
            strings.append("".join(parts))
        return strings
    except Exception:
        return []


def _load_sheet_names(zf: zipfile.ZipFile) -> List[Tuple[str, str]]:
    """Returns list of (sheet_name, rId) in workbook order."""
    try:
        with zf.open("xl/workbook.xml") as fh:
            root = ET.parse(fh).getroot()
        sheets = []
        for s in root.findall(".//ss:sheet", NS):
            name = s.get("name", "")
            rid = s.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id", "")
            sheets.append((name, rid))
        return sheets
    except Exception:
        return []


def _load_rel_map(zf: zipfile.ZipFile) -> Dict[str, str]:
    """rId → xl/worksheets/sheetN.xml path."""
    try:
        with zf.open("xl/_rels/workbook.xml.rels") as fh:
            root = ET.parse(fh).getroot()
        rel_ns = "http://schemas.openxmlformats.org/package/2006/relationships"
        result = {}
        for rel in root.findall(f"{{{rel_ns}}}Relationship"):
            rid = rel.get("Id", "")
            target = rel.get("Target", "")
            if "worksheet" in target.lower():
                result[rid] = "xl/" + target.lstrip("/") if not target.startswith("xl/") else target
        return result
    except Exception:
        return {}


def _cell_value(cell: ET.Element, shared: List[str]) -> str:
    t_attr = cell.get("t", "")
    v_el = cell.find("ss:v", NS)
    if v_el is None or v_el.text is None:
        # try inline string
        is_el = cell.find("ss:is/ss:t", NS)
        return (is_el.text or "").strip() if is_el is not None else ""
    if t_attr == "s":
        try:
            return shared[int(v_el.text)]
        except (IndexError, ValueError):
            return ""
    if t_attr == "str":
        return v_el.text.strip()
    return v_el.text.strip()


def _read_sheet_rows(zf: zipfile.ZipFile, rel_path: str, shared: List[str], max_rows: int = 200) -> List[List[str]]:
    try:
        with zf.open(rel_path) as fh:
            root = ET.parse(fh).getroot()
    except Exception:
        return []

    rows: List[List[str]] = []
    for row_el in root.findall(".//ss:row", NS):
        cells: List[str] = []
        for cell in row_el.findall("ss:c", NS):
            cells.append(_cell_value(cell, shared))
        rows.append(cells)
        if len(rows) >= max_rows:
            break
    return rows


def _header_set(rows: List[List[str]]) -> set:
    """Flatten first 5 rows into a lowercase string set for header detection."""
    result: set = set()
    for row in rows[:5]:
        for cell in row:
            v = cell.strip().lower()
            if v:
                result.add(v)
    return result


def _scan_all_text(rows: List[List[str]]) -> str:
    return " ".join(c for row in rows for c in row if c.strip()).lower()


def _count_data_rows(rows: List[List[str]]) -> int:
    return sum(1 for row in rows[5:] if any(c.strip() for c in row))


def _classify_sheet(name: str, rows: List[List[str]]) -> Dict[str, Any]:
    if SKIP_NAMES.search(name):
        return {"role": "skip", "strategy": "skip", "tenji_ready": False, "notes": "封面/目錄頁自動略過"}

    headers = _header_set(rows)
    all_text = _scan_all_text(rows)
    row_count = _count_data_rows(rows)

    # PDO table
    if len(PDO_HEADERS & headers) >= 2:
        return {"role": "pdo_table", "strategy": "spec_extract",
                "tenji_ready": False,
                "notes": "PDO 能力表 — 需手動萃取並轉為 ForceV/MeasI 測項"}

    # Timing spec
    if len(TIMING_HEADERS & headers) >= 1 and len(EC_HEADERS & headers) >= 2:
        return {"role": "spec_timing", "strategy": "spec_extract",
                "tenji_ready": False,
                "notes": "Timing 規格表 — 需萃取 min/typ/max 後生成 Wait/MeasV 測項"}

    # EC spec
    if len(EC_HEADERS & headers) >= 3:
        return {"role": "spec_ec", "strategy": "spec_extract",
                "tenji_ready": False,
                "notes": "電氣規格表 — 需萃取限值後映射至 Judge 測項"}

    # Mode matrix / scenario
    if len(MODE_HEADERS & headers) >= 1:
        return {"role": "mode_matrix", "strategy": "scenario_expand",
                "tenji_ready": False,
                "notes": "模式矩陣 — 每一格對應一個狀態轉移，需展開成多個 TENJI 測項"}

    # Power sequence
    if len(PWRSEQ_HEADERS & headers) >= 1:
        return {"role": "power_matrix", "strategy": "spec_extract",
                "tenji_ready": False,
                "notes": "上電時序表 — 萃取 pwr_seq 群組定義"}

    # Summary / tracker
    if len(SUMMARY_HEADERS & headers) >= 2 and row_count > 0:
        return {"role": "summary", "strategy": "skip",
                "tenji_ready": False,
                "notes": "進度追蹤表 — 不直接映射，僅供參考"}

    # Testcase sheet — direct map
    if len(TC_HEADERS & headers) >= 2:
        return {"role": "testcase", "strategy": "direct_map",
                "tenji_ready": True,
                "notes": "測試案例表 — 可直接對應 TENJI Test Note 欄位"}

    # Fallback
    if row_count == 0:
        return {"role": "skip", "strategy": "skip",
                "tenji_ready": False, "notes": "空白頁"}

    return {"role": "unknown", "strategy": "skip",
            "tenji_ready": False,
            "notes": f"無法自動分類 (headers={list(headers)[:8]})"}


def _extract_ic_project(rows: List[List[str]], sheet_name: str) -> Tuple[str, str]:
    all_text = " ".join(c for row in rows[:20] for c in row if c.strip())
    ic_match = IC_NAME_RE.search(all_text)
    ic_name = ic_match.group(0) if ic_match else ""

    proj_match = PROJECT_RE.search(all_text)
    project = proj_match.group(2).strip() if proj_match else ""

    return ic_name, project


def classify_workbook(path: str | Path) -> Dict[str, Any]:
    path = Path(path)
    zf = _open_zip(path)
    if zf is None:
        return {"error": f"Cannot open {path} as zip/xlsx"}

    with zf:
        shared = _load_shared_strings(zf)
        sheet_names = _load_sheet_names(zf)
        rel_map = _load_rel_map(zf)

        ic_name = ""
        project = ""
        classified = []
        warnings: List[str] = []

        for idx, (sname, rid) in enumerate(sheet_names):
            rel_path = rel_map.get(rid, "")
            if not rel_path:
                warnings.append(f"Sheet '{sname}' 找不到對應的 worksheet 檔案")
                continue

            rows = _read_sheet_rows(zf, rel_path, shared)
            result = _classify_sheet(sname, rows)

            if not ic_name and rows:
                ic_name, project = _extract_ic_project(rows, sname)

            header_set = _header_set(rows)

            classified.append({
                "index": idx,
                "name": sname,
                "role": result["role"],
                "strategy": result["strategy"],
                "tenji_ready": result["tenji_ready"],
                "headers": sorted(header_set)[:16],
                "row_count": _count_data_rows(rows),
                "notes": result["notes"],
            })

    # pick the best entry sheet (first tenji_ready testcase, else first direct_map)
    entry = next(
        (s["name"] for s in classified if s["tenji_ready"] and s["role"] == "testcase"),
        next((s["name"] for s in classified if s["strategy"] == "direct_map"), None),
    )

    tc_count = sum(1 for s in classified if s["role"] == "testcase")
    matrix_count = sum(1 for s in classified if s["role"] == "mode_matrix")
    ec_count = sum(1 for s in classified if s["role"] in ("spec_ec", "spec_timing"))

    if tc_count == 0:
        warnings.append("未找到可直接對應的測試案例頁，需人工確認")
    if matrix_count > 0:
        warnings.append(f"有 {matrix_count} 個模式矩陣頁需要場景展開，每格對應一個或多個 TENJI 測項")
    if ec_count > 0:
        warnings.append(f"有 {ec_count} 個規格表頁需萃取限值，建議核對 DS 頁碼")

    return {
        "workbook": str(path),
        "ic_name": ic_name or "Unknown",
        "project": project or "Unknown",
        "sheets": classified,
        "recommended_entry_sheet": entry,
        "warnings": warnings,
    }


def main() -> int:
    if len(sys.argv) < 2:
        print("用法: python3 sheet_classifier.py <SA_testplan.xlsx>", file=sys.stderr)
        return 1
    result = classify_workbook(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
