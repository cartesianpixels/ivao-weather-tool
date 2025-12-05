"""
Tests for Weather Calculator.
"""

import pytest
from src.domain.weather_calculator import WeatherCalculator
from src.data.models import (
    VisibilityData, CloudLayer, TemperatureData, 
    PressureData, WindData
)

class TestWeatherCalculator:
    """Test cases for weather calculations."""
    
    def test_flight_category_vfr(self):
        """Test VFR flight category calculation."""
        vis = VisibilityData(value=10.0, unit='SM', less_than=False)
        clouds = [CloudLayer(coverage='FEW', altitude=5000, type=None)]
        
        category = WeatherCalculator.calculate_flight_category(vis, clouds)
        assert category == 'VFR'
    
    def test_flight_category_mvfr(self):
        """Test MVFR flight category calculation."""
        # MVFR due to visibility
        vis = VisibilityData(value=4.0, unit='SM', less_than=False)
        clouds = [CloudLayer(coverage='FEW', altitude=5000, type=None)]
        assert WeatherCalculator.calculate_flight_category(vis, clouds) == 'MVFR'
        
        # MVFR due to ceiling
        vis = VisibilityData(value=10.0, unit='SM', less_than=False)
        clouds = [CloudLayer(coverage='BKN', altitude=2500, type=None)]
        assert WeatherCalculator.calculate_flight_category(vis, clouds) == 'MVFR'
    
    def test_flight_category_ifr(self):
        """Test IFR flight category calculation."""
        # IFR due to visibility
        vis = VisibilityData(value=2.0, unit='SM', less_than=False)
        clouds = [CloudLayer(coverage='FEW', altitude=5000, type=None)]
        assert WeatherCalculator.calculate_flight_category(vis, clouds) == 'IFR'
        
        # IFR due to ceiling
        vis = VisibilityData(value=10.0, unit='SM', less_than=False)
        clouds = [CloudLayer(coverage='OVC', altitude=800, type=None)]
        assert WeatherCalculator.calculate_flight_category(vis, clouds) == 'IFR'
    
    def test_flight_category_lifr(self):
        """Test LIFR flight category calculation."""
        # LIFR due to visibility
        vis = VisibilityData(value=0.5, unit='SM', less_than=False)
        clouds = [CloudLayer(coverage='FEW', altitude=5000, type=None)]
        assert WeatherCalculator.calculate_flight_category(vis, clouds) == 'LIFR'
        
        # LIFR due to ceiling
        vis = VisibilityData(value=10.0, unit='SM', less_than=False)
        clouds = [CloudLayer(coverage='VV', altitude=200, type=None)]
        assert WeatherCalculator.calculate_flight_category(vis, clouds) == 'LIFR'
        
    def test_density_altitude(self):
        """Test density altitude calculation."""
        # Standard day at sea level: 15C, 29.92 inHg -> DA = 0
        da = WeatherCalculator.calculate_density_altitude(0, 15)
        assert abs(da) < 50  # Allow small rounding diff
        
        # Hot day at altitude: 5000ft, 30C
        # ISA at 5000ft = 15 - (2 * 5) = 5C
        # Deviation = 30 - 5 = 25C
        # DA = 5000 + (120 * 25) = 5000 + 3000 = 8000ft
        da = WeatherCalculator.calculate_density_altitude(5000, 30)
        assert abs(da - 8000) < 50
        
    def test_pressure_altitude(self):
        """Test pressure altitude calculation."""
        # Standard pressure: PA = Field Elevation
        pa = WeatherCalculator.calculate_pressure_altitude(1000, 29.92)
        assert abs(pa - 1000) < 10
        
        # Low pressure: 28.92 inHg (1 inch lower = +1000ft PA)
        pa = WeatherCalculator.calculate_pressure_altitude(1000, 28.92)
        assert abs(pa - 2000) < 10
        
        # High pressure: 30.92 inHg (1 inch higher = -1000ft PA)
        pa = WeatherCalculator.calculate_pressure_altitude(1000, 30.92)
        assert abs(pa - 0) < 10
        
    def test_crosswind_component(self):
        """Test crosswind component calculation."""
        # Direct headwind
        hw, xw = WeatherCalculator.calculate_crosswind_component(360, 10, 360)
        assert hw == 10
        assert xw == 0
        
        # Direct crosswind
        hw, xw = WeatherCalculator.calculate_crosswind_component(90, 10, 360)
        assert abs(hw) < 1  # Near zero
        assert xw == 10
        
        # 45 degree crosswind
        # cos(45) = sin(45) ≈ 0.707
        hw, xw = WeatherCalculator.calculate_crosswind_component(45, 10, 360)
        assert abs(hw - 7) <= 1
        assert abs(xw - 7) <= 1
        
    def test_relative_humidity(self):
        """Test relative humidity calculation."""
        # Temp = Dewpoint -> 100% RH
        rh = WeatherCalculator.calculate_relative_humidity(10, 10)
        assert rh == 100
        
        # Large spread -> Low RH
        rh = WeatherCalculator.calculate_relative_humidity(20, 0)
        assert rh < 50
        
    def test_conversions(self):
        """Test unit conversions."""
        # C to F
        assert WeatherCalculator.celsius_to_fahrenheit(0) == 32
        assert WeatherCalculator.celsius_to_fahrenheit(100) == 212
        
        # F to C
        assert WeatherCalculator.fahrenheit_to_celsius(32) == 0
        assert WeatherCalculator.fahrenheit_to_celsius(212) == 100
        
        # Knots to MPH
        assert WeatherCalculator.knots_to_mph(100) == 115
        
        # MPH to Knots
        assert WeatherCalculator.mph_to_knots(115) == 99  # Rounding
        
    def test_descriptions(self):
        """Test description generators."""
        # Cloud base
        assert "low" in WeatherCalculator.get_cloud_base_description(500)
        assert "mid-level" in WeatherCalculator.get_cloud_base_description(3000)
        assert "high" in WeatherCalculator.get_cloud_base_description(10000)
        
        # Wind
        wind = WindData(direction=360, speed=10, gust=20, variable=False)
        desc = WeatherCalculator.get_wind_description(wind)
        assert "360" in desc
        assert "10 knots" in desc
        assert "gusting to 20" in desc
        
        # Visibility
        vis = VisibilityData(value=10.0, unit='SM', less_than=False)
        assert "excellent" in WeatherCalculator.get_visibility_description(vis)
        
        vis = VisibilityData(value=0.5, unit='SM', less_than=False)
        assert "very poor" in WeatherCalculator.get_visibility_description(vis)
        
        # Temperature
        temp = TemperatureData(temperature=20, dewpoint=18)
        desc = WeatherCalculator.get_temperature_description(temp)
        assert "20°C" in desc
        assert "fog or low clouds likely" in desc
