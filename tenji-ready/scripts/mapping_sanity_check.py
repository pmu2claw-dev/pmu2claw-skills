#!/usr/bin/env python3
import sys
from pathlib import Path

REQUIRED_HEADERS = [
    'B (Bin)', 'C (Test_Item)', 'D (Symbol)', 'E (PWR Sequence)',
    'F (PseudoCode)', 'G (Wait/Run Pattern)', 'H (Measure Condition)',
    'I (Description)', 'J (Min)', 'K (Typ)', 'L (Max)', 'M (Unit)', 'N (Remarks)'
]


def main():
    if len(sys.argv) != 2:
        print('usage: mapping_sanity_check.py <markdown-file>', file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    text = path.read_text(encoding='utf-8')
    ok = True
    for h in REQUIRED_HEADERS:
        if h not in text:
            print(f'MISSING HEADER TOKEN: {h}')
            ok = False
    if '_TMU' not in text:
        print('WARN: no _TMU token found; verify timing/frequency items if applicable')
    if '0x' not in text:
        print('WARN: no 0x token found; verify hex formatting if applicable')
    if ok:
        print('PASS: basic markdown mapping sanity check passed')
        return 0
    return 1

if __name__ == '__main__':
    raise SystemExit(main())
