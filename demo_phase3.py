#!/usr/bin/env python3
"""
Demo script showing Phase 3 capabilities.
Demonstrates METAR/TAF decoding and interpretation.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.domain.metar_decoder import MetarDecoder
from src.domain.taf_decoder import TafDecoder
from src.domain.weather_calculator import WeatherCalculator
from src.domain.weather_interpreter import WeatherInterpreter


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_subsection(title: str):
    """Print a subsection header."""
    print(f"\n{'-' * 70}")
    print(f"  {title}")
    print(f"{'-' * 70}")


def main():
    """Demo the decoding capabilities."""
    print_section("IVAO Weather Tool - Phase 3 Demo")
    print("METAR/TAF Decoding and Interpretation")
    
    # Initialize decoders
    metar_decoder = MetarDecoder()
    taf_decoder = TafDecoder()
    
    # ========================================================================
    # Test 1: Basic METAR Decoding
    # ========================================================================
    print_section("Test 1: Basic METAR Decoding")
    
    metar_examples = [
        "KJFK 041651Z 31008KT 10SM FEW250 04/M03 A3012 RMK AO2 SLP201",
        "KLAX 041653Z 24015G25KT 10SM FEW015 BKN250 18/14 A2990",
        "KSEA 041656Z 16008KT 3SM -RA BR BKN008 OVC015 10/09 A2985",
        "KBOS 041654Z 09012KT 1/2SM FG OVC002 06/06 A3008",
    ]
    
    for raw_metar in metar_examples:
        print_subsection(f"Decoding: {raw_metar}")
        
        try:
            metar = metar_decoder.decode(raw_metar)
            
            print(f"[OK] Station: {metar.station}")
            print(f"[OK] Time: {metar.observation_time.strftime('%d %H:%M UTC')}")
            print(f"[OK] Flight Category: {metar.flight_category}")
            
            if metar.wind:
                print(f"[OK] Wind: {WeatherCalculator.get_wind_description(metar.wind)}")
            
            if metar.visibility:
                print(f"[OK] Visibility: {WeatherCalculator.get_visibility_description(metar.visibility)}")
            
            if metar.weather:
                wx_desc = WeatherInterpreter._interpret_weather_phenomena(metar.weather)
                print(f"[OK] Weather: {wx_desc}")
            
            if metar.clouds:
                cloud_desc = WeatherInterpreter._interpret_clouds(metar.clouds)
                print(f"[OK] Clouds: {cloud_desc}")
            
            if metar.temperature:
                temp_c = metar.temperature.temperature
                temp_f = WeatherCalculator.celsius_to_fahrenheit(temp_c)
                dew_c = metar.temperature.dewpoint
                dew_f = WeatherCalculator.celsius_to_fahrenheit(dew_c)
                rh = WeatherCalculator.calculate_relative_humidity(temp_c, dew_c)
                print(f"[OK] Temperature: {temp_c}°C ({temp_f}°F), Dewpoint: {dew_c}°C ({dew_f}°F)")
                print(f"   Relative Humidity: {rh}%")
            
            if metar.pressure:
                print(f"[OK] Altimeter: {metar.pressure.value} {metar.pressure.unit}")
            
        except Exception as e:
            print(f"[ERROR] Error decoding METAR: {e}")
    
    # ========================================================================
    # Test 2: Flight Category Calculations
    # ========================================================================
    print_section("Test 2: Flight Category Calculations")
    
    print("\nFlight categories are calculated based on visibility and ceiling:")
    print("  * VFR:  Visibility >= 5 SM and Ceiling >= 3000 ft")
    print("  * MVFR: Visibility 3-5 SM or Ceiling 1000-3000 ft")
    print("  * IFR:  Visibility 1-3 SM or Ceiling 500-1000 ft")
    print("  * LIFR: Visibility < 1 SM or Ceiling < 500 ft")
    
    for raw_metar in metar_examples:
        metar = metar_decoder.decode(raw_metar)
        cat_desc = WeatherCalculator.get_flight_category_description(metar.flight_category)
        print(f"\n{metar.station}: {metar.flight_category}")
        print(f"  {cat_desc}")
    
    # ========================================================================
    # Test 3: Weather Calculations
    # ========================================================================
    print_section("Test 3: Weather Calculations")
    
    print_subsection("Crosswind Component Calculation")
    print("\nScenario: Runway 27 (270°), Wind 310° at 15 knots")
    headwind, crosswind = WeatherCalculator.calculate_crosswind_component(310, 15, 270)
    print(f"[OK] Headwind component: {headwind} knots")
    print(f"[OK] Crosswind component: {crosswind} knots")
    
    print_subsection("Density Altitude Calculation")
    print("\nScenario: Pressure altitude 5000 ft, Temperature 30°C")
    density_alt = WeatherCalculator.calculate_density_altitude(5000, 30)
    print(f"[OK] Density altitude: {density_alt} feet")
    print("   (High density altitude reduces aircraft performance)")
    
    # ========================================================================
    # Test 4: TAF Decoding
    # ========================================================================
    print_section("Test 4: TAF Decoding")
    
    taf_examples = [
        "TAF KJFK 041730Z 0418/0524 31012KT P6SM FEW250",
        "TAF KORD 041730Z 0418/0524 27010KT P6SM FEW250 FM050200 31015KT P6SM SCT050",
        "TAF KSEA 041730Z 0418/0524 16010KT P6SM FEW015 TEMPO 0420/0424 5SM -RA BKN015",
    ]
    
    for raw_taf in taf_examples:
        print_subsection(f"Decoding TAF")
        print(f"Raw: {raw_taf}\n")
        
        try:
            taf = taf_decoder.decode(raw_taf)
            
            print(f"[OK] Station: {taf.station}")
            print(f"[OK] Issued: {taf.issue_time.strftime('%d %H:%M UTC')}")
            print(f"[OK] Valid: {taf.valid_from.strftime('%d %H:%M')} to {taf.valid_to.strftime('%d %H:%M UTC')}")
            print(f"[OK] Number of forecast periods: {len(taf.periods)}")
            
            for i, period in enumerate(taf.periods):
                if period.change_indicator:
                    print(f"\n   Period {i+1}: {period.change_indicator}")
                else:
                    print(f"\n   Period {i+1}: Base Forecast")
                
                print(f"   Time: {period.from_time.strftime('%H:%M')} - {period.to_time.strftime('%H:%M UTC')}")
                
                if period.wind:
                    print(f"   Wind: {WeatherCalculator.get_wind_description(period.wind)}")
                
                if period.visibility:
                    print(f"   Visibility: {period.visibility.value} SM")
                
                if period.clouds:
                    cloud_desc = WeatherInterpreter._interpret_clouds(period.clouds)
                    print(f"   Clouds: {cloud_desc}")
        
        except Exception as e:
            print(f"[ERROR] Error decoding TAF: {e}")
    
    # ========================================================================
    # Test 5: Human-Readable Interpretation
    # ========================================================================
    print_section("Test 5: Human-Readable Interpretation")
    
    print_subsection("Full METAR Interpretation")
    sample_metar = metar_decoder.decode("KJFK 041651Z 31008KT 10SM FEW250 04/M03 A3012")
    interpretation = WeatherInterpreter.interpret_metar(sample_metar)
    print(interpretation)
    
    print_subsection("Training Explanation")
    training_text = WeatherInterpreter.get_training_explanation(sample_metar)
    print(training_text)
    
    # ========================================================================
    # Test 6: Unit Conversions
    # ========================================================================
    print_section("Test 6: Unit Conversions")
    
    print("\n[OK] Temperature conversions:")
    print(f"   0C = {WeatherCalculator.celsius_to_fahrenheit(0)}F")
    print(f"   20C = {WeatherCalculator.celsius_to_fahrenheit(20)}F")
    print(f"   -10C = {WeatherCalculator.celsius_to_fahrenheit(-10)}F")
    
    print("\n[OK] Wind speed conversions:")
    print(f"   10 knots = {WeatherCalculator.knots_to_mph(10)} mph")
    print(f"   25 knots = {WeatherCalculator.knots_to_mph(25)} mph")
    
    print("\n[OK] Pressure conversions:")
    print(f"   30.12 inHg = {WeatherCalculator.inhg_to_hpa(30.12)} hPa")
    print(f"   1013 hPa = {WeatherCalculator.hpa_to_inhg(1013)} inHg")
    
    # ========================================================================
    # Summary
    # ========================================================================
    print_section("Phase 3 Demo Complete!")
    
    print("\n[SUMMARY] Phase 3 Capabilities:")
    print("   [OK] METAR decoding with full component parsing")
    print("   [OK] TAF decoding with change group support (FM, TEMPO, BECMG, PROB)")
    print("   [OK] Flight category calculation (VFR/MVFR/IFR/LIFR)")
    print("   [OK] Weather calculations (crosswind, density altitude, etc.)")
    print("   [OK] Human-readable interpretations for training")
    print("   [OK] Unit conversions (temperature, wind, pressure)")
    print("   [OK] Comprehensive test coverage")
    
    print("\n[NEXT] Phase 4 will integrate this with the UI layer!")
    print()


if __name__ == "__main__":
    main()
