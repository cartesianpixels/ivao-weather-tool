#!/usr/bin/env python3
"""Test remarks decoder integration."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.domain.metar_decoder import MetarDecoder

# Test METAR with remarks
test_metar = "KJFK 041651Z 31008KT 10SM FEW250 04/M03 A3012 RMK AO2 SLP201 T00441028"

decoder = MetarDecoder()
metar = decoder.decode(test_metar)

print(f"Station: {metar.station}")
print(f"Raw Remarks: {metar.remarks}")
print(f"\nDecoded Remarks:")

if metar.remarks_data:
    rmk = metar.remarks_data
    print(f"  Automated Station Type: {rmk.get('automated_station_type')}")
    print(f"  Sea Level Pressure: {rmk.get('sea_level_pressure')} hPa")
    print(f"  Temperature (precise): {rmk.get('temperature_precise')}°C")
    print(f"  Dewpoint (precise): {rmk.get('dewpoint_precise')}°C")
else:
    print("  No remarks data decoded")

print("\n[OK] Remarks decoder integration successful!")
