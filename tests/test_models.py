"""
Unit tests for data models.
"""

import pytest
from datetime import datetime
from src.data.models import (
    WindData, VisibilityData, CloudLayer, MetarData,
    TafData, TafPeriod, UserSettings, StationInfo
)


def test_wind_data_valid():
    """Test valid wind data creation."""
    wind = WindData(direction=270, speed=10, gust=15)
    assert wind.direction == 270
    assert wind.speed == 10
    assert wind.gust == 15
    assert not wind.variable


def test_wind_data_variable():
    """Test variable wind data."""
    wind = WindData(
        direction=None,
        speed=5,
        variable=True,
        variable_from=180,
        variable_to=240
    )
    assert wind.variable
    assert wind.variable_from == 180
    assert wind.variable_to == 240


def test_visibility_data():
    """Test visibility data."""
    vis = VisibilityData(value=10.0, unit="SM")
    assert vis.value == 10.0
    assert vis.unit == "SM"
    assert not vis.less_than


def test_cloud_layer():
    """Test cloud layer data."""
    cloud = CloudLayer(coverage="BKN", altitude=2500, type="CB")
    assert cloud.coverage == "BKN"
    assert cloud.altitude == 2500
    assert cloud.type == "CB"


def test_metar_data_minimal():
    """Test minimal METAR data."""
    metar = MetarData(
        station="KJFK",
        observation_time=datetime(2025, 12, 4, 16, 51),
        raw_text="KJFK 041651Z 31008KT 10SM FEW250 04/M03 A3012"
    )
    assert metar.station == "KJFK"
    assert metar.raw_text
    assert not metar.auto
    assert not metar.corrected


def test_metar_data_with_flight_category():
    """Test METAR with flight category."""
    metar = MetarData(
        station="KJFK",
        observation_time=datetime(2025, 12, 4, 16, 51),
        raw_text="KJFK 041651Z 31008KT 10SM FEW250 04/M03 A3012",
        flight_category="VFR"
    )
    assert metar.flight_category == "VFR"


def test_taf_period():
    """Test TAF period data."""
    period = TafPeriod(
        from_time=datetime(2025, 12, 4, 18, 0),
        to_time=datetime(2025, 12, 5, 0, 0),
        change_indicator="TEMPO"
    )
    assert period.change_indicator == "TEMPO"
    assert period.from_time < period.to_time


def test_taf_data():
    """Test TAF data."""
    taf = TafData(
        station="KJFK",
        issue_time=datetime(2025, 12, 4, 16, 0),
        valid_from=datetime(2025, 12, 4, 18, 0),
        valid_to=datetime(2025, 12, 5, 18, 0),
        raw_text="TAF KJFK 041600Z 0418/0518 31010KT P6SM FEW250"
    )
    assert taf.station == "KJFK"
    assert not taf.amended
    assert len(taf.periods) == 0  # No periods added yet


def test_station_info():
    """Test station information."""
    station = StationInfo(
        icao="KJFK",
        name="John F Kennedy International Airport",
        latitude=40.6398,
        longitude=-73.7789,
        elevation=13,
        is_favorite=True
    )
    assert station.icao == "KJFK"
    assert station.is_favorite
    assert station.elevation == 13


def test_user_settings_defaults():
    """Test user settings with defaults."""
    settings = UserSettings()
    assert settings.theme == "dark"
    assert settings.wind_unit == "knots"
    assert settings.temperature_unit == "celsius"
    assert settings.update_frequency_minutes == 5
    assert "KJFK" in settings.default_airports


def test_user_settings_custom():
    """Test custom user settings."""
    settings = UserSettings(
        theme="light",
        wind_unit="mph",
        temperature_unit="fahrenheit",
        default_airports=["KLAX", "KSFO"]
    )
    assert settings.theme == "light"
    assert settings.wind_unit == "mph"
    assert "KLAX" in settings.default_airports
