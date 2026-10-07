"""Seed collection objects and loans.

Usage:
    python seed.py            # seeds the local `museum` catalog directory
    python seed.py my_dir     # or another directory you passed to `pxt schema update`
"""
import sys
from pathlib import Path

import pixeltable as pxt

target = sys.argv[1] if len(sys.argv) > 1 else 'museum'
HERE = Path(__file__).resolve().parent

SEED = {
    'objects': [
        {'accession': '1931.12', 'title': 'Harbor at Dusk', 'medium': 'oil on canvas', 'year': 1928, 'gallery': 'G4'},
        {'accession': '1977.03', 'title': 'Bronze Heron', 'medium': 'bronze', 'year': 1902, 'gallery': 'G1'},
        {'accession': '2004.88', 'title': 'Untitled (Blue Grid)', 'medium': 'acrylic', 'year': 1969, 'gallery': 'G7'},
    ],
    'loans': [
        {'accession': '1931.12', 'borrower': 'City Art Museum', 'venue': 'Rotterdam', 'status': 'out', 'days_out': 140, 'notes': None, 'curator': 'okafor'},
        {'accession': '1977.03', 'borrower': 'Coastal Arts Center', 'venue': 'Monterey', 'status': 'in-transit', 'days_out': 9, 'notes': 'crate 3 of 3', 'curator': 'okafor'},
        {'accession': '2004.88', 'borrower': 'University Gallery', 'venue': 'Ann Arbor', 'status': 'out', 'days_out': 101, 'notes': None, 'curator': 'lindqvist'},
    ],
}

for table_name, rows in SEED.items():
    t = pxt.get_table(f'{target}/{table_name}')
    if t.count() > 0:
        print(f'{target}/{table_name} already has {t.count()} rows; skipping')
        continue
    for row in rows:
        for k, v in row.items():
            if isinstance(v, str) and v.startswith('data/'):
                row[k] = str(HERE / v)   # local sample media file
    t.insert(rows)
    print(f'inserted {len(rows)} rows into {target}/{table_name}')
