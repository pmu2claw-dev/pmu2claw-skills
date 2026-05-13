from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

DSL_TOKENS = [
    'ForceV',
    'ForceI',
    'UR',
    'PD_command',
    'MeasV',
    'JudgeV',
    'Wait',
]

PROSE_MARKERS = [
    'Source Step:',
    'Target voltage:',
    'Send SRC Cap:',
    'Request PDO:',
    'Protocol:',
    'Expected:',
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def make_row_spec(
    *,
    row_index_within_case: int,
    symbol: str | None,
    test_item_anchor: str | None,
    pwr_sequence: str | None,
    pseudo_code: str | None,
    run_pattern_wait: str | None,
    measure_condition: str | None,
    description: str | None,
    min_formula: Any,
    typ: Any,
    max_formula: Any,
    unit: str | None,
    remarks: str | None,
    style_source_workbook: str | None,
    style_source_sheet: str = 'Test Note',
    style_source_row: int | None = None,
    bin_value: int | None = 5,
) -> dict[str, Any]:
    return {
        'row_index_within_case': row_index_within_case,
        'bin_value': bin_value,
        'symbol': symbol,
        'test_item_anchor': test_item_anchor,
        'pwr_sequence': pwr_sequence,
        'pseudo_code': pseudo_code,
        'run_pattern_wait': run_pattern_wait,
        'measure_condition': measure_condition,
        'description': description,
        'min_formula': min_formula,
        'typ': typ,
        'max_formula': max_formula,
        'unit': unit,
        'remarks': remarks,
        'style_source': {
            'workbook': style_source_workbook,
            'sheet': style_source_sheet,
            'row': style_source_row,
        },
    }


def make_item_spec(
    *,
    case_id: str,
    family: str,
    source_sheet: str,
    source_row: int | None,
    lineage_refs: list[str],
    body_rows: list[dict[str, Any]],
    status: str = 'draft',
    reasoning_note: str | None = None,
) -> dict[str, Any]:
    return {
        'schema_version': '0.1.0',
        'created_at_utc': utc_now(),
        'status': status,
        'case_id': case_id,
        'family': family,
        'source': {
            'sheet': source_sheet,
            'row': source_row,
        },
        'lineage': {
            'primary_references': lineage_refs,
            'reasoning_note': reasoning_note,
        },
        'workbook_rules': {
            'wrapper_policy': 'workbook_scope_only',
            'head_wrapper': 'OS_test',
            'tail_wrapper': 'OS_test2',
        },
        'merge_rules': {
            'test_item_column': 'C',
            'merge_body_rows': True,
        },
        'body_rows': body_rows,
    }


def new_item_spec(
    *,
    case_id: str,
    family: str,
    source_sheet: str,
    source_row: int | None,
    row_count: int,
    lineage_refs: list[str],
) -> dict[str, Any]:
    normalized = case_id.replace('-', '_').replace('單電源', 'singlepwr_')
    rows = [
        make_row_spec(
            row_index_within_case=idx,
            symbol=f'{normalized}_S{idx}',
            test_item_anchor=None,
            pwr_sequence='PWR_VBUS',
            pseudo_code=None,
            run_pattern_wait=None,
            measure_condition=None,
            description=None,
            min_formula='=KROW*0.8',
            typ=None,
            max_formula='=KROW*1.2',
            unit='V',
            remarks=None,
            style_source_workbook=None,
            style_source_row=None,
            bin_value=5,
        )
        for idx in range(1, row_count + 1)
    ]
    return make_item_spec(
        case_id=case_id,
        family=family,
        source_sheet=source_sheet,
        source_row=source_row,
        lineage_refs=lineage_refs,
        body_rows=rows,
        status='draft',
        reasoning_note=None,
    )
