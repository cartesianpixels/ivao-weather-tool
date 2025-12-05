"""
Tests for Weather Interpreter.
"""

import pytest
from datetime import datetime, timezone
from src.domain.weather_interpreter import WeatherInterpreter
from src.data.models import (
    MetarData, TafData, TafPeriod, WindData, VisibilityData,
    CloudLayer, WeatherPhenomenon, TemperatureData, PressureData
)

class TestWeatherInterpreter:
    """Test cases for weather interpretation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.now = datetime(2023, 10, 4, 12, 0, tzinfo=timezone.utc)
    
    def test_interpret_metar(self):
        """Test METAR interpretation."""
        metar = MetarData(
            station="KJFK",
            observation_time=self.now,
            raw_text="KJFK 041200Z 36010KT 10SM FEW250 20/15 A3012",
            wind=WindData(direction=360, speed=10),
            visibility=VisibilityData(value=10.0, unit='SM', less_than=False),
            clouds=[CloudLayer(coverage='FEW', altitude=25000)],
            temperature=TemperatureData(temperature=20, dewpoint=15),
            pressure=PressureData(value=30.12, unit='inHg'),
            flight_category='VFR',
            auto=False,
            corrected=False,
            cached_at=self.now
        )
        
        text = WeatherInterpreter.interpret_metar(metar)
        
        assert "METAR for KJFK" in text
        assert "Observed at 12:00 UTC" in text
        assert "Flight Category: VFR" in text
        assert "From 360° at 10 knots" in text
        assert "10 statute miles or greater" in text
        assert "few clouds (1-2 oktas) at 25000 feet" in text
        assert "20°C" in text
        assert "30.12 inHg" in text
    
    def test_interpret_taf(self):
        """Test TAF interpretation."""
        valid_from = datetime(2023, 10, 4, 12, 0, tzinfo=timezone.utc)
        valid_to = datetime(2023, 10, 5, 12, 0, tzinfo=timezone.utc)
        
        period = TafPeriod(
            from_time=valid_from,
            to_time=valid_to,
            change_indicator=None,
            probability=None,
            wind=WindData(direction=360, speed=10),
            visibility=VisibilityData(value=10.0, unit='SM', less_than=False),
            weather=[],
            clouds=[CloudLayer(coverage='FEW', altitude=25000)]
        )
        
        taf = TafData(
            station="KJFK",
            issue_time=self.now,
            valid_from=valid_from,
            valid_to=valid_to,
            raw_text="TAF KJFK...",
            periods=[period],
            amended=False,
            cached_at=self.now
        )
        
        text = WeatherInterpreter.interpret_taf(taf)
        
        assert "TAF for KJFK" in text
        assert "Issued at 12:00 UTC" in text
        assert "Base Forecast" in text
        assert "From 360° at 10 knots" in text
    
    def test_interpret_weather_phenomena(self):
        """Test weather phenomena interpretation."""
        # +TSRA (Heavy Thunderstorm Rain)
        wx = WeatherPhenomenon(
            intensity='+',
            descriptor='TS',
            precipitation=['RA'],
            obscuration=[],
            other=[]
        )
        
        desc = WeatherInterpreter._interpret_weather_phenomena([wx])
        assert "heavy" in desc
        assert "thunderstorm with" in desc
        assert "rain" in desc
        
        # BR (Mist)
        wx = WeatherPhenomenon(
            intensity=None,
            descriptor=None,
            precipitation=[],
            obscuration=['BR'],
            other=[]
        )
        
        desc = WeatherInterpreter._interpret_weather_phenomena([wx])
        assert "mist" in desc
    
    def test_interpret_clouds(self):
        """Test cloud interpretation."""
        # FEW025CB
        clouds = [CloudLayer(coverage='FEW', altitude=2500, type='CB')]
        desc = WeatherInterpreter._interpret_clouds(clouds)
        
        assert "few clouds" in desc
        assert "2500 feet" in desc
        assert "cumulonimbus" in desc
        
        # OVC010
        clouds = [CloudLayer(coverage='OVC', altitude=1000, type=None)]
        desc = WeatherInterpreter._interpret_clouds(clouds)
        
        assert "overcast" in desc
        assert "1000 feet" in desc
    
    def test_training_explanation(self):
        """Test training explanation generation."""
        metar = MetarData(
            station="KJFK",
            observation_time=self.now,
            raw_text="KJFK...",
            wind=WindData(direction=360, speed=10, gust=20),
            flight_category='VFR',
            cached_at=self.now
        )
        
        text = WeatherInterpreter.get_training_explanation(metar)
        
        assert "METAR TRAINING BREAKDOWN" in text
        assert "Station Identifier: KJFK" in text
        assert "360° = Wind direction" in text
        assert "10KT = Wind speed" in text
        assert "G20KT = Gusts" in text
        assert "Flight Category: VFR" in text
