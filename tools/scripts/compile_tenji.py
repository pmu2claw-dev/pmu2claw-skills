#!/usr/bin/env python3
"""
compile_tenji.py

把 request/spec 串成：parse -> normalize -> validate -> excel
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ai_parser import parse_user_request
from generate_excel import append, generate
from spec_validator import validate_spec
from sheet_classifier import classify_workbook
from bootstrap_family import bootstrap_spec
from build_sa_index import build_index, _is_fresh, _index_path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TENJI compile wrapper")
    parser.add_argument("--request", help="自然語言需求")
    parser.add_argument("--request-file", help="需求文字檔")
    parser.add_argument("--spec", help="既有 spec.json")
    parser.add_argument("--existing-excel", help="現有 Excel，通常表示 append")
    parser.add_argument("--output", help="輸出 .xlsm 路徑")
    parser.add_argument("--summary-out", help="summary json 輸出路徑")
    parser.add_argument("--normalized-spec-out", help="normalized spec json 輸出路徑")
    # SA intake mode
    parser.add_argument("--sa-workbook", help="SA Test Plan workbook (.xlsx/.xlsm)")
    parser.add_argument("--sa-sheet", help="SA sheet name (auto-detected if omitted)")
    parser.add_argument("--sa-family", help="Mode family override for SA bootstrap")
    parser.add_argument("--sa-dut-notes", default="", help="DUT circuit notes")
    parser.add_argument("--classify-only", action="store_true",
                        help="Only classify SA workbook sheets, do not generate Excel")
    parser.add_argument("--build-index", action="store_true",
                        help="Build/refresh SA workbook index then exit")
    parser.add_argument("--query-case", help="Look up a case ID from SA index (e.g. '2-11')")
    return parser.parse_args()


def _load_request(args: argparse.Namespace) -> str | None:
    if args.request:
        return args.request
    if args.request_file:
        return Path(args.request_file).read_text(encoding="utf-8").strip()
    return None


def _resolve_output_target(args: argparse.Namespace, action: str) -> str:
    if args.output:
        return args.output
    if action == "append" and args.existing_excel:
        return args.existing_excel
    raise SystemExit("需要提供 --output；若 append 也可直接提供 --existing-excel")


def _default_json_path(output_target: str, suffix: str) -> str:
    output_path = Path(output_target)
    return str(output_path.with_suffix("") ) + suffix


def main() -> int:
    args = _parse_args()

    # ── Index-only operations ────────────────────────────────────────────────
    if (args.build_index or args.query_case) and args.sa_workbook:
        wb_path = Path(args.sa_workbook).resolve()
        index = build_index(wb_path, force=args.build_index)
        if args.query_case:
            from build_sa_index import query_case
            result = query_case(index, args.query_case)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            from build_sa_index import print_summary
            print_summary(index)
        return 0

    # ── SA intake mode ────────────────────────────────────────────────────────
    if args.sa_workbook:
        wb_path = Path(args.sa_workbook).resolve()
        # Use cached index when fresh; rebuild otherwise (auto-invalidates on file change)
        if _is_fresh(wb_path, _index_path(wb_path)):
            cached = build_index(wb_path)  # returns from disk, no re-parse
            classified = {
                "sheets": cached["sheets"],
                "ic_name": cached["ic_name"],
                "project": cached["project"],
                "warnings": cached["warnings"],
                "recommended_entry_sheet": next(
                    (s["name"] for s in cached["sheets"] if s.get("role") == "testcase"),
                    None,
                ),
            }
        else:
            classified = classify_workbook(wb_path)
            build_index(wb_path, force=True)  # update cache in background

        if args.classify_only:
            print(json.dumps(classified, ensure_ascii=False, indent=2))
            return 0

        # Auto-pick entry sheet
        sheet = args.sa_sheet or classified.get("recommended_entry_sheet")
        if not sheet:
            print("SA workbook 中找不到合適的測試案例頁，請用 --sa-sheet 手動指定", file=sys.stderr)
            print(json.dumps(classified, ensure_ascii=False, indent=2), file=sys.stderr)
            return 1

        raw_spec = bootstrap_spec(
            workbook_path=args.sa_workbook,
            sheet_name=sheet,
            family=args.sa_family,
            dut_notes=args.sa_dut_notes,
            ic_name=classified.get("ic_name", ""),
            project=classified.get("project", ""),
        )

        # Emit classification warnings to stderr
        for w in classified.get("warnings", []):
            print(f"[SA] {w}", file=sys.stderr)

    # ── standard mode ─────────────────────────────────────────────────────────
    else:
        request_text = _load_request(args)
        if not any([request_text, args.spec]):
            print("請提供 --request / --request-file / --spec / --sa-workbook 其中一項", file=sys.stderr)
            return 1

        if args.spec:
            raw_spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
        else:
            raw_spec = parse_user_request(request_text or "", existing_excel=args.existing_excel)

    validation = validate_spec(raw_spec, existing_excel=args.existing_excel)
    normalized_spec = validation["normalized_spec"]
    output_target = _resolve_output_target(args, normalized_spec.get("action", "generate"))

    spec_out = args.normalized_spec_out or _default_json_path(output_target, ".spec.json")
    summary_out = args.summary_out or _default_json_path(output_target, ".summary.json")

    Path(spec_out).write_text(
        json.dumps(normalized_spec, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    if not validation["ok"]:
        summary = {
            "ok": False,
            "stage": "validate",
            "output_path": None,
            "errors": validation["errors"],
            "warnings": validation["warnings"],
            "memory_warnings": validation.get("memory_warnings", []),
            "memory_rules_applied": validation.get("memory_rules_applied", []),
            "memory_context_preview": validation.get("memory_context_preview", ""),
            "normalized_spec_path": spec_out,
        }
        Path(summary_out).write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 1

    action = normalized_spec["action"]
    if action == "append":
        output_path = append(normalized_spec, output_target)
    else:
        output_path = generate(normalized_spec, output_target)

    summary = {
        "ok": True,
        "stage": "completed",
        "action": action,
        "output_path": output_path,
        "errors": validation["errors"],
        "warnings": validation["warnings"],
        "memory_warnings": validation.get("memory_warnings", []),
        "memory_rules_applied": validation.get("memory_rules_applied", []),
        "memory_context_preview": validation.get("memory_context_preview", ""),
        "normalized_spec_path": spec_out,
    }
    Path(summary_out).write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())