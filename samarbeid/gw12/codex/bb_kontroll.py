#!/usr/bin/env python3
"""GW12 chip audit note.

Bench Boost was activated in GW11. It is unavailable in GW12-R19, so the
GW11 paired BB-date audit is intentionally not run for this decision horizon.
Free Hit dates are evaluated in modell_r2.py's common chip grid.
"""
import json
from pathlib import Path
O=Path(__file__).resolve().parent
status=json.loads((O/'status.json').read_text())
assert status.get('status')=='fullført', 'Run modell.py through completion first'
print('No Bench Boost audit: BB1 was used in GW11; see chiprutenett.csv for Free Hit dates.')
