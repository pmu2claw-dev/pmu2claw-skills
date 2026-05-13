#!/usr/bin/env python3
from pathlib import Path

base = Path(__file__).resolve().parents[1]
for sub in ['references']:
    root = base / sub
    print(f'[{sub}]')
    for p in sorted(root.rglob('*')):
        if p.is_file():
            print(p.relative_to(base))
