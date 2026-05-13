#!/usr/bin/env python3
"""
SA mode-matrix → TENJI test_items expander.

Handles 4 JD6628H mode families:
  SinglePwr_C2A   — 3 rows (Single_power2 + PD_req9V → PD_req5V → PD_req9V), measure VBUSC_C2
  Single_power3   — 4 rows, charge detect + 9V + 5V + back to 9V, measure VBUSC_C2 / VBUSC_C3
  Single_power4   — 4 rows (mirrored), measure VBUSC_C4
  DualPwr         — variable rows, two active ports, VBUSC_C2 + VBUSC_C3
  VoltFollow      — 2 rows (C2 follows C3 voltage), ForceV on C3, MeasV on C2
  SmartBlind      — variable, blind insertion + auto role detect

Entry point:
    expand_mode_row(family, sa_row_dict, pinmap) -> List[test_item_dict]
    expand_matrix_sheet(family, rows, headers, pinmap) -> List[test_item_dict]
"""

from __future__ import annotations

import copy
import re
from typing import Any, Dict, List, Optional

# ── helpers ──────────────────────────────────────────────────────────────────

def _s(v: Any) -> str:
    return str(v or "").strip()


def _safe_symbol(raw: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", raw.strip())


def _base_item(symbol: str, name: str, pwr_seq: str, description: str) -> Dict[str, Any]:
    return {
        "bin": "",
        "name": name,
        "test_item": name,
        "symbol": symbol,
        "pwr_seq": pwr_seq,
        "pseudo_code": "",
        "run_pattern": "",
        "measure_cond": "",
        "description": description,
        "min": "",
        "typ": "",
        "max": "",
        "unit": "",
        "note": "",
        "commands": [],
    }


def _measv_item(symbol: str, name: str, pwr_seq: str, pin: str,
                min_v: str = "", typ_v: str = "", max_v: str = "", unit: str = "V",
                description: str = "") -> Dict[str, Any]:
    item = _base_item(symbol, name, pwr_seq, description)
    item["measure_cond"] = f"MeasV {pin}"
    item["min"] = min_v
    item["typ"] = typ_v
    item["max"] = max_v
    item["unit"] = unit
    return item


def _pd_req_item(symbol: str, name: str, pwr_seq: str, req_v: str,
                 measure_pin: str, min_v: str = "", max_v: str = "",
                 description: str = "") -> Dict[str, Any]:
    item = _base_item(symbol, name, pwr_seq, description)
    item["pseudo_code"] = f"PD_req{req_v}"
    item["measure_cond"] = f"MeasV {measure_pin}"
    item["min"] = min_v
    item["max"] = max_v
    item["unit"] = "V"
    return item


# ── family rule implementations ───────────────────────────────────────────────

def _expand_single_pwr_c2a(sa: Dict[str, Any], base_sym: str) -> List[Dict[str, Any]]:
    """
    SinglePwr_C2A — exactly 3 TENJI rows:
      row1: Single_power2 + PD_req9V → attach C2A, request 9V, MeasV VBUSC_C2
      row2: PD_req5V → re-request 5V, MeasV VBUSC_C2
      row3: PD_req9V → re-request 9V, MeasV VBUSC_C2
    """
    min_v = _s(sa.get("min", ""))
    max_v = _s(sa.get("max", ""))
    return [
        _pd_req_item(f"{base_sym}_9V_r1", f"{base_sym} 接C2A請求9V",
                     "Single_power2", "9V", "VBUSC_C2", min_v, max_v,
                     "C2A接入，PD握手請求9V，量測VBUSC_C2"),
        _pd_req_item(f"{base_sym}_5V_r2", f"{base_sym} 降回5V",
                     "PD_req5V", "5V", "VBUSC_C2", "4.75", "5.25",
                     "重新請求5V，確認降壓過渡"),
        _pd_req_item(f"{base_sym}_9V_r3", f"{base_sym} 重請9V",
                     "PD_req9V", "9V", "VBUSC_C2", min_v, max_v,
                     "再度請求9V，確認穩壓"),
    ]


def _expand_single_power3(sa: Dict[str, Any], base_sym: str) -> List[Dict[str, Any]]:
    """
    Single_power3 — 4 rows:
      row1: detect charger, MeasV VBUSC_C2 (5V default)
      row2: PD_req9V, MeasV VBUSC_C2
      row3: PD_req5V, MeasV VBUSC_C3 (output side)
      row4: PD_req9V again, MeasV VBUSC_C3
    """
    min9 = _s(sa.get("min", "8.5"))
    max9 = _s(sa.get("max", "9.5"))
    return [
        _measv_item(f"{base_sym}_det", f"{base_sym} 充電偵測",
                    "Single_power3", "VBUSC_C2", "4.75", "5", "5.25", "V",
                    "偵測充電器接入，量測C2 5V"),
        _pd_req_item(f"{base_sym}_9V_r1", f"{base_sym} 請求9V",
                     "PD_req9V", "9V", "VBUSC_C2", min9, max9,
                     "PD請求9V，量測輸入VBUSC_C2"),
        _pd_req_item(f"{base_sym}_5V_r3", f"{base_sym} 降5V量C3",
                     "PD_req5V", "5V", "VBUSC_C3", "4.75", "5.25",
                     "請求5V，量測輸出側VBUSC_C3"),
        _pd_req_item(f"{base_sym}_9V_r4", f"{base_sym} 重9V量C3",
                     "PD_req9V", "9V", "VBUSC_C3", min9, max9,
                     "再請求9V，量測輸出側VBUSC_C3"),
    ]


def _expand_single_power4(sa: Dict[str, Any], base_sym: str) -> List[Dict[str, Any]]:
    """
    Single_power4 — 4 rows (mirrored of power3, but C4 port).
    """
    min9 = _s(sa.get("min", "8.5"))
    max9 = _s(sa.get("max", "9.5"))
    return [
        _measv_item(f"{base_sym}_det", f"{base_sym} C4偵測",
                    "Single_power4", "VBUSC_C4", "4.75", "5", "5.25", "V",
                    "C4充電偵測"),
        _pd_req_item(f"{base_sym}_9V_r1", f"{base_sym} C4請求9V",
                     "PD_req9V", "9V", "VBUSC_C4", min9, max9,
                     "C4 PD請求9V"),
        _pd_req_item(f"{base_sym}_5V_r3", f"{base_sym} C4降5V",
                     "PD_req5V", "5V", "VBUSC_C4", "4.75", "5.25",
                     "C4請求5V過渡"),
        _pd_req_item(f"{base_sym}_9V_r4", f"{base_sym} C4重9V",
                     "PD_req9V", "9V", "VBUSC_C4", min9, max9,
                     "C4再請求9V"),
    ]


def _expand_dual_pwr(sa: Dict[str, Any], base_sym: str) -> List[Dict[str, Any]]:
    """
    DualPwr — two concurrent active ports (C2 + C3).
    Generates: attach both → C2 steady → C3 steady → cross-load event.
    """
    min_v = _s(sa.get("min", ""))
    max_v = _s(sa.get("max", ""))
    items = [
        _measv_item(f"{base_sym}_C2", f"{base_sym} C2量測",
                    "DualPwr_C2", "VBUSC_C2", min_v, "", max_v, "V",
                    "雙電源 C2 穩態量測"),
        _measv_item(f"{base_sym}_C3", f"{base_sym} C3量測",
                    "DualPwr_C3", "VBUSC_C3", min_v, "", max_v, "V",
                    "雙電源 C3 穩態量測"),
    ]
    # cross-load event: cut C2, verify C3 absorbs load
    cross = _base_item(f"{base_sym}_xload", f"{base_sym} C2斷後C3接管",
                       "DualPwr_C3", "C2斷電後C3應維持供電")
    cross["pseudo_code"] = "UR kN OFF\nWait 200ms"
    cross["measure_cond"] = "MeasV VBUSC_C3"
    cross["min"] = min_v
    cross["max"] = max_v
    cross["unit"] = "V"
    items.append(cross)
    return items


def _expand_volt_follow(sa: Dict[str, Any], base_sym: str) -> List[Dict[str, Any]]:
    """
    VoltFollow — C2 output tracks C3 input voltage.
    Row1: set C3 to 9V, measure C2 (should equal C3).
    Row2: set C3 to 5V, measure C2.
    """
    items = [
        _measv_item(f"{base_sym}_9V", f"{base_sym} 9V跟隨",
                    "VoltFollow_9V", "VBUSC_C2", "8.5", "9", "9.5", "V",
                    "C3=9V, C2應跟隨輸出9V"),
        _measv_item(f"{base_sym}_5V", f"{base_sym} 5V跟隨",
                    "VoltFollow_5V", "VBUSC_C2", "4.75", "5", "5.25", "V",
                    "C3=5V, C2應跟隨輸出5V"),
    ]
    # set pseudo_code for forcing C3
    items[0]["pseudo_code"] = "ForceV VBUSC_C3 9V"
    items[1]["pseudo_code"] = "ForceV VBUSC_C3 5V"
    return items


def _expand_smart_blind(sa: Dict[str, Any], base_sym: str) -> List[Dict[str, Any]]:
    """
    SmartBlind — blind insertion, auto role (Sink/Source) detection.
    Generates: insert → role detect check → steady-state measure.
    """
    min_v = _s(sa.get("min", ""))
    max_v = _s(sa.get("max", ""))
    role_check = _base_item(f"{base_sym}_role", f"{base_sym} 角色偵測",
                            "SmartBlind_Attach", "盲插後自動判定 Source/Sink 角色")
    role_check["pseudo_code"] = "Attach C2A\nWait 500ms"
    role_check["run_pattern"] = "RoleDetect"
    role_check["note"] = "需確認 cc1/cc2 狀態"

    steady = _measv_item(f"{base_sym}_steady", f"{base_sym} 穩態量測",
                         "SmartBlind_Steady", "VBUSC_C2", min_v, "", max_v, "V",
                         "盲插穩定後量測VBUS")
    return [role_check, steady]


# ── family dispatch ───────────────────────────────────────────────────────────

FAMILY_MAP = {
    "SinglePwr_C2A": _expand_single_pwr_c2a,
    "Single_power3": _expand_single_power3,
    "Single_power4": _expand_single_power4,
    "DualPwr":       _expand_dual_pwr,
    "VoltFollow":    _expand_volt_follow,
    "SmartBlind":    _expand_smart_blind,
}

# aliases from SA test-plan wording
FAMILY_ALIASES = {
    "單電源c2a": "SinglePwr_C2A",
    "single pwr c2a": "SinglePwr_C2A",
    "single_power2": "SinglePwr_C2A",
    "單電源3": "Single_power3",
    "single_power3": "Single_power3",
    "單電源4": "Single_power4",
    "single_power4": "Single_power4",
    "雙電源": "DualPwr",
    "dual power": "DualPwr",
    "dual pwr": "DualPwr",
    "電壓跟隨": "VoltFollow",
    "volt follow": "VoltFollow",
    "voltage follow": "VoltFollow",
    "智能盲插": "SmartBlind",
    "smart blind": "SmartBlind",
    "blind insert": "SmartBlind",
}


def resolve_family(raw_family: str) -> Optional[str]:
    raw = raw_family.strip()
    # exact case-insensitive match against canonical names
    for canonical in FAMILY_MAP:
        if raw.lower() == canonical.lower():
            return canonical
    # alias lookup
    return FAMILY_ALIASES.get(raw.lower())


def expand_mode_row(family: str, sa_row: Dict[str, Any],
                    base_symbol: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Expand a single SA row into TENJI test_items using the family rule.

    Args:
        family:      canonical family name or alias
        sa_row:      dict with keys like no, name/功能, min, max, unit, description
        base_symbol: override symbol prefix; auto-derived from sa_row if None

    Returns:
        List of test_item dicts (ready for spec["test_items"])
    """
    resolved = resolve_family(family)
    if resolved is None:
        raise ValueError(f"未知家族名稱: '{family}'。已知: {sorted(FAMILY_MAP.keys())}")

    base_sym = base_symbol or _safe_symbol(
        _s(sa_row.get("symbol") or sa_row.get("name") or sa_row.get("功能") or f"Item_{resolved}")
    )

    fn = FAMILY_MAP[resolved]
    return fn(sa_row, base_sym)


def expand_matrix_sheet(family: str, rows: List[List[str]], headers: List[str],
                        pinmap: Optional[List[Dict]] = None) -> List[Dict[str, Any]]:
    """
    Expand an entire mode-matrix sheet (list of rows) into test_items.

    headers: column names list (first row of sheet)
    rows:    data rows (each is a list of cell strings)
    """
    h_lower = [h.strip().lower() for h in headers]

    def col(row: List[str], *names: str) -> str:
        for name in names:
            try:
                idx = h_lower.index(name.lower())
                if idx < len(row):
                    return row[idx].strip()
            except ValueError:
                pass
        return ""

    all_items: List[Dict[str, Any]] = []
    for i, row in enumerate(rows):
        if not any(c.strip() for c in row):
            continue
        sa = {
            "no": col(row, "no", "no.", "編號"),
            "name": col(row, "功能", "名稱", "test item", "description"),
            "min": col(row, "min", "最小"),
            "max": col(row, "max", "最大"),
            "unit": col(row, "unit", "單位"),
        }
        sym_prefix = _safe_symbol(sa["name"] or f"Row{i+1}")
        try:
            items = expand_mode_row(family, sa, sym_prefix)
        except ValueError:
            items = []
        all_items.extend(items)

    return all_items


def main() -> int:
    import json
    import sys

    if len(sys.argv) < 3:
        print("用法: python3 mode_expander.py <family> <sa_row.json>", file=sys.stderr)
        print("  family 可為: " + ", ".join(sorted(FAMILY_MAP.keys())), file=sys.stderr)
        return 1

    family = sys.argv[1]
    with open(sys.argv[2], encoding="utf-8") as fh:
        sa_row = json.load(fh)

    items = expand_mode_row(family, sa_row)
    print(json.dumps(items, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
