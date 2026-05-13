#!/usr/bin/env python3
"""
Bootstrap a TENJI spec for a new IC/family when no ANS sample exists.

Takes an SA testcase sheet (via sheet_classifier output or raw rows)
plus optional DUT circuit notes, and generates a first-pass spec JSON
that compile_tenji.py can consume.

Usage:
  python3 bootstrap_family.py --sa <classified.json> --sheet <sheet_name> \
      --family <family> [--dut-notes <notes.txt>] [--output <spec.json>]

Or programmatically:
  from bootstrap_family import bootstrap_spec
  spec = bootstrap_spec(classified_result, sheet_name="TC_Main",
                        family="SinglePwr_C2A", dut_notes="JD6628H C2A port")
"""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import siblings
sys.path.insert(0, str(Path(__file__).parent))
from sheet_classifier import classify_workbook, _load_shared_strings, _load_sheet_names, _load_rel_map, _read_sheet_rows, _header_set, NS
from mode_expander import expand_mode_row, resolve_family, FAMILY_MAP


def _detect_family_from_text(text: str) -> Optional[str]:
    """Heuristic: infer family from SA sheet text."""
    t = text.lower()
    if "智能盲插" in t or "smart blind" in t:
        return "SmartBlind"
    if "電壓跟隨" in t or "volt follow" in t:
        return "VoltFollow"
    if "雙電源" in t or "dual power" in t or "dual pwr" in t:
        return "DualPwr"
    if "single_power4" in t or "單電源4" in t:
        return "Single_power4"
    if "single_power3" in t or "單電源3" in t:
        return "Single_power3"
    if "single_power2" in t or "c2a" in t or "單電源" in t:
        return "SinglePwr_C2A"
    return None


def _extract_rows_from_workbook(wb_path: str, sheet_name: str) -> List[List[str]]:
    path = Path(wb_path)
    try:
        zf = zipfile.ZipFile(path, "r")
    except Exception as e:
        raise IOError(f"無法開啟 {path}: {e}")

    with zf:
        shared = _load_shared_strings(zf)
        sheet_names = _load_sheet_names(zf)
        rel_map = _load_rel_map(zf)

        for sname, rid in sheet_names:
            if sname == sheet_name:
                rel_path = rel_map.get(rid, "")
                if rel_path:
                    return _read_sheet_rows(zf, rel_path, shared, max_rows=500)
    raise ValueError(f"Sheet '{sheet_name}' 不存在於 {path.name}")


def _rows_to_sa_dicts(rows: List[List[str]]) -> List[Dict[str, Any]]:
    """Convert raw rows to list of SA row dicts using first row as headers."""
    if not rows:
        return []
    headers = [h.strip().lower() for h in rows[0]]
    result = []
    for row in rows[1:]:
        if not any(c.strip() for c in row):
            continue
        entry: Dict[str, Any] = {}
        for i, h in enumerate(headers):
            entry[h] = row[i].strip() if i < len(row) else ""
        result.append(entry)
    return result


def _sa_row_to_normalized(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Map SA column names → standard keys."""
    def g(*keys: str) -> str:
        for k in keys:
            v = str(raw.get(k) or raw.get(k.lower()) or "").strip()
            if v:
                return v
        return ""

    return {
        "name": g("功能", "測試項目", "test item", "name", "description"),
        "symbol": g("symbol", "符號", "name"),
        "min": g("min", "最小", "lower limit"),
        "max": g("max", "最大", "upper limit"),
        "typ": g("typ", "典型"),
        "unit": g("unit", "單位"),
        "description": g("說明", "description", "預期結果", "pass criteria"),
    }


def bootstrap_spec(
    workbook_path: str,
    sheet_name: str,
    family: Optional[str] = None,
    dut_notes: str = "",
    ic_name: str = "",
    project: str = "",
) -> Dict[str, Any]:
    """
    Generate a first-pass TENJI spec from SA testcase rows.

    When family is None, auto-detects from sheet content.
    When no ANS sample exists, uses mode_expander rules to scaffold rows.
    """
    rows = _extract_rows_from_workbook(workbook_path, sheet_name)

    # Auto-detect family
    all_text = " ".join(c for row in rows for c in row)
    resolved_family = family or _detect_family_from_text(all_text + " " + dut_notes)

    if resolved_family is None:
        raise ValueError(
            "無法自動判斷家族。請使用 --family 指定: " + ", ".join(sorted(FAMILY_MAP.keys()))
        )

    confirmed_family = resolve_family(resolved_family)
    if confirmed_family is None:
        raise ValueError(f"未知家族: '{resolved_family}'")

    sa_dicts = _rows_to_sa_dicts(rows)
    test_items: List[Dict[str, Any]] = []

    for sa_raw in sa_dicts:
        sa_norm = _sa_row_to_normalized(sa_raw)
        if not sa_norm["name"]:
            continue
        try:
            expanded = expand_mode_row(confirmed_family, sa_norm)
            test_items.extend(expanded)
        except Exception as e:
            # Don't crash — emit a placeholder
            test_items.append({
                "bin": "", "name": sa_norm["name"], "test_item": sa_norm["name"],
                "symbol": sa_norm.get("symbol", "UNKNOWN"),
                "pwr_seq": "", "pseudo_code": "", "run_pattern": "", "measure_cond": "",
                "description": f"[bootstrap placeholder — {e}]",
                "min": sa_norm["min"], "typ": sa_norm["typ"], "max": sa_norm["max"],
                "unit": sa_norm["unit"], "note": "", "commands": [],
            })

    # Build minimal pinmap from DUT notes heuristic
    pinmap = _infer_pinmap(confirmed_family, dut_notes)

    spec: Dict[str, Any] = {
        "action": "generate",
        "ic_name": ic_name or _guess_ic(all_text) or "Unknown IC",
        "project": project or "Unknown Project",
        "notes": f"Bootstrap from SA sheet '{sheet_name}' | family={confirmed_family}" + (
            f" | DUT: {dut_notes}" if dut_notes else ""
        ),
        "pinmap": pinmap,
        "power_sequence": _default_power_sequence(confirmed_family),
        "test_items": test_items,
        "revisions": [],
        "i2c_sequences": [],
        "_parser_meta": {
            "fallback_used": True,
            "bootstrap_family": confirmed_family,
            "source_sheet": sheet_name,
            "source_workbook": workbook_path,
        },
    }
    return spec


def _guess_ic(text: str) -> str:
    import re
    m = re.search(r"\b(JD\d{4}[A-Z]*|RT\d{4}[A-Z]*|SC\d{4}[A-Z]*)\b", text)
    return m.group(0) if m else ""


def _infer_pinmap(family: str, notes: str) -> List[Dict[str, Any]]:
    """Generate a skeletal pinmap based on family port usage."""
    base: List[Dict[str, Any]] = []

    def pin(name: str, typ: str = "VBUS") -> Dict[str, Any]:
        return {
            "pin_name": name, "pin": name, "type": typ,
            "power_monitor": "", "instrument": "", "mvi_pin": "",
            "mvi_ch": "", "mcpmu_ch": "", "pe_ref": "", "pe_name": "",
            "pe_ch": "", "ur_num": "", "ur0": "N", "ur1": "O",
            "up_diode": "", "dn_diode": "", "N": "N", "O": "O",
        }

    if family in ("SinglePwr_C2A",):
        base = [pin("VBUSC_C2"), pin("CC1_C2", "CC"), pin("CC2_C2", "CC")]
    elif family == "Single_power3":
        base = [pin("VBUSC_C2"), pin("VBUSC_C3"), pin("CC1_C2", "CC")]
    elif family == "Single_power4":
        base = [pin("VBUSC_C4"), pin("CC1_C4", "CC")]
    elif family == "DualPwr":
        base = [pin("VBUSC_C2"), pin("VBUSC_C3"), pin("CC1_C2", "CC"), pin("CC1_C3", "CC")]
    elif family == "VoltFollow":
        base = [pin("VBUSC_C2"), pin("VBUSC_C3")]
    elif family == "SmartBlind":
        base = [pin("VBUSC_C2"), pin("CC1_C2", "CC"), pin("CC2_C2", "CC")]

    return base


def _default_power_sequence(family: str) -> Dict[str, List[Dict[str, Any]]]:
    def step(pin: str, action: str, delay: str = "50ms") -> Dict[str, Any]:
        return {"pin": pin, "action": action, "voltage": action, "delay": delay, "max_v": ""}

    if family == "SinglePwr_C2A":
        return {
            "Single_power2": [step("VBUSC_C2", "5V")],
            "PD_req9V": [step("VBUSC_C2", "9V")],
            "PD_req5V": [step("VBUSC_C2", "5V")],
        }
    elif family in ("Single_power3", "Single_power4"):
        port = "VBUSC_C4" if family == "Single_power4" else "VBUSC_C2"
        return {
            family: [step(port, "5V")],
            "PD_req9V": [step(port, "9V")],
            "PD_req5V": [step(port, "5V")],
        }
    elif family == "DualPwr":
        return {
            "DualPwr_C2": [step("VBUSC_C2", "5V")],
            "DualPwr_C3": [step("VBUSC_C3", "5V")],
        }
    elif family == "VoltFollow":
        return {
            "VoltFollow_9V": [step("VBUSC_C3", "9V")],
            "VoltFollow_5V": [step("VBUSC_C3", "5V")],
        }
    elif family == "SmartBlind":
        return {
            "SmartBlind_Attach": [step("VBUSC_C2", "5V")],
            "SmartBlind_Steady": [step("VBUSC_C2", "5V")],
        }
    return {}


def main() -> int:
    p = argparse.ArgumentParser(description="Bootstrap TENJI spec from SA sheet")
    p.add_argument("--workbook", required=True, help="SA workbook path (.xlsx/.xlsm)")
    p.add_argument("--sheet", required=True, help="Sheet name to process")
    p.add_argument("--family", help="Mode family override")
    p.add_argument("--dut-notes", default="", help="DUT circuit notes (free text)")
    p.add_argument("--ic-name", default="", help="IC name override")
    p.add_argument("--project", default="", help="Project name override")
    p.add_argument("--output", help="Output spec JSON path (stdout if omitted)")
    args = p.parse_args()

    spec = bootstrap_spec(
        workbook_path=args.workbook,
        sheet_name=args.sheet,
        family=args.family,
        dut_notes=args.dut_notes,
        ic_name=args.ic_name,
        project=args.project,
    )

    out = json.dumps(spec, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"Spec written to {args.output}", file=sys.stderr)
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
