from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import load_json
from schema import DSL_TOKENS, PROSE_MARKERS


REQUIRED_TOP_LEVEL_KEYS = {
    'schema_version',
    'created_at_utc',
    'status',
    'case_id',
    'family',
    'source',
    'lineage',
    'workbook_rules',
    'merge_rules',
    'body_rows',
}

REQUIRED_ROW_KEYS = {
    'row_index_within_case',
    'symbol',
    'test_item_anchor',
    'pwr_sequence',
    'pseudo_code',
    'run_pattern_wait',
    'measure_condition',
    'description',
    'min_formula',
    'typ',
    'max_formula',
    'unit',
    'remarks',
    'style_source',
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Validate a TENJI single-item spec JSON.')
    parser.add_argument('--input', required=True)
    parser.add_argument('--allow-draft', action='store_true')
    return parser.parse_args()


def validate_singlepwr_c2a(rows: list[dict]) -> list[str]:
    errors: list[str] = []
    if len(rows) != 3:
        errors.append(f'SinglePwr_C2A expects exactly 3 body rows, got {len(rows)}')
        return errors

    row1, row2, row3 = rows
    if row1.get('test_item_anchor') != 'Single_power2':
        errors.append('SinglePwr_C2A row 1 should anchor merged test item as Single_power2')
    if 'PD_command PD_req9v' not in str(row1.get('measure_condition')):
        errors.append('SinglePwr_C2A row 1 should request 9V via PD_req9v')
    if 'VBUSC_C2' not in str(row1.get('measure_condition')):
        errors.append('SinglePwr_C2A row 1 should measure VBUSC_C2')
    if row1.get('typ') != 9:
        errors.append(f"SinglePwr_C2A row 1 typ should be 9, got {row1.get('typ')}")

    if 'PD_command PD_req5v' not in str(row2.get('measure_condition')):
        errors.append('SinglePwr_C2A row 2 should request 5V share via PD_req5v')
    if 'VBUSC_C2' not in str(row2.get('measure_condition')):
        errors.append('SinglePwr_C2A row 2 should keep measuring VBUSC_C2 during A share state')
    if row2.get('typ') != 5:
        errors.append(f"SinglePwr_C2A row 2 typ should be 5, got {row2.get('typ')}")

    if 'PD_command PD_req9v' not in str(row3.get('measure_condition')):
        errors.append('SinglePwr_C2A row 3 should re-request 9V via PD_req9v after detach')
    if 'VBUSC_C2' not in str(row3.get('measure_condition')):
        errors.append('SinglePwr_C2A row 3 should measure VBUSC_C2 during recovery')
    if row3.get('typ') != 9:
        errors.append(f"SinglePwr_C2A row 3 typ should be 9, got {row3.get('typ')}")
    return errors


def validate(payload: dict, allow_draft: bool) -> list[str]:
    errors: list[str] = []

    missing = REQUIRED_TOP_LEVEL_KEYS - payload.keys()
    if missing:
        errors.append(f'missing top-level keys: {sorted(missing)}')

    if payload.get('status') == 'draft' and not allow_draft:
        errors.append('status is still draft; pass --allow-draft only for partial review')

    rows = payload.get('body_rows') or []
    if not rows:
        errors.append('body_rows is empty')
        return errors

    expected_index = 1
    seen_symbols: set[str] = set()
    has_anchor = False
    for row in rows:
        row_missing = REQUIRED_ROW_KEYS - row.keys()
        if row_missing:
            errors.append(
                f'row {row.get("row_index_within_case", "?")} missing keys: {sorted(row_missing)}'
            )
            continue

        if row['row_index_within_case'] != expected_index:
            errors.append(
                f'row_index_within_case should be sequential from 1; '
                f'expected {expected_index}, got {row["row_index_within_case"]}'
            )
        expected_index += 1

        symbol = row['symbol']
        if not symbol:
            errors.append(f'row {row["row_index_within_case"]}: symbol is empty')
        elif symbol in seen_symbols:
            errors.append(f'duplicate symbol: {symbol}')
        else:
            seen_symbols.add(symbol)

        if row['test_item_anchor']:
            has_anchor = True

        mc = row.get('measure_condition')
        if not mc:
            errors.append(f'row {row["row_index_within_case"]}: measure_condition is empty')
        else:
            if not any(token in mc for token in DSL_TOKENS):
                errors.append(
                    f'row {row["row_index_within_case"]}: measure_condition has no TENJI DSL token '
                    f'({DSL_TOKENS})'
                )
            bad_markers = [marker for marker in PROSE_MARKERS if marker in mc]
            if bad_markers:
                errors.append(
                    f'row {row["row_index_within_case"]}: measure_condition still contains prose markers {bad_markers}'
                )

        description = row.get('description')
        if not description:
            errors.append(f'row {row["row_index_within_case"]}: description is empty')

        if row.get('typ') is None and row.get('unit'):
            errors.append(f'row {row["row_index_within_case"]}: typ is empty while unit is set')

        min_formula = row.get('min_formula')
        if min_formula and 'KROW' not in str(min_formula) and not str(min_formula).startswith('=K'):
            errors.append(f'row {row["row_index_within_case"]}: min_formula should reference KROW or real K-row formula')

        max_formula = row.get('max_formula')
        if max_formula and 'KROW' not in str(max_formula) and not str(max_formula).startswith('=K'):
            errors.append(f'row {row["row_index_within_case"]}: max_formula should reference KROW or real K-row formula')

        style_source = row.get('style_source') or {}
        if not style_source.get('sheet'):
            errors.append(f'row {row["row_index_within_case"]}: style_source.sheet is empty')
        if payload.get('status') != 'draft' and not style_source.get('workbook'):
            errors.append(f'row {row["row_index_within_case"]}: reviewed rows must keep style_source.workbook')

    if not has_anchor:
        errors.append('no row contains test_item_anchor; at least first body row should anchor merged C column')

    lineage_refs = payload.get('lineage', {}).get('primary_references') or []
    if not lineage_refs:
        errors.append('lineage.primary_references is empty')

    wrapper_policy = payload.get('workbook_rules', {}).get('wrapper_policy')
    if wrapper_policy != 'workbook_scope_only':
        errors.append('workbook_rules.wrapper_policy must be workbook_scope_only')

    family = payload.get('family')
    if family == 'SinglePwr_C2A':
        errors.extend(validate_singlepwr_c2a(rows))

    return errors


def main() -> int:
    args = parse_args()
    payload = load_json(args.input)
    errors = validate(payload, allow_draft=args.allow_draft)
    report = {
        'input': str(Path(args.input)),
        'error_count': len(errors),
        'errors': errors,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
