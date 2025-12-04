"""
Data models for IVAO Weather Tool.
Pydantic models for weather data validation and serialization.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class WindData(BaseModel):
    """Wind information from METAR/TAF."""
    direction: Optional[int] = Field(None, ge=0, le=360, description="Wind direction in degrees")
    speed: int = Field(..., ge=0, description="Wind speed in knots")
    gust: Optional[int] = Field(None, ge=0, description="Gust speed in knots")
    variable: bool = Field(False, description="Variable wind direction")
    variable_from: Optional[int] = Field(None, ge=0, le=360)
    variable_to: Optional[int] = Field(None, ge=0, le=360)


class VisibilityData(BaseModel):
    """Visibility information."""
    value: float = Field(..., ge=0, description="Visibility in statute miles")
    unit: str = Field("SM", description="Unit of measurement")
    less_than: bool = Field(False, description="Less than reported value")


class CloudLayer(BaseModel):
    """Individual cloud layer."""
    coverage: str = Field(..., description="SKC, FEW, SCT, BKN, OVC")
    altitude: Optional[int] = Field(None, description="Cloud base in feet AGL")
    type: Optional[str] = Field(None, description="Cloud type (CB, TCU, etc.)")


class WeatherPhenomenon(BaseModel):
    """Weather phenomenon (rain, snow, fog, etc.)."""
    intensity: Optional[str] = Field(None, description="+, -, or None for moderate")
    descriptor: Optional[str] = Field(None, description="MI, BC, PR, DR, BL, SH, TS, FZ")
    precipitation: List[str] = Field(default_factory=list, description="DZ, RA, SN, SG, etc.")
    obscuration: List[str] = Field(default_factory=list, description="BR, FG, FU, VA, etc.")
    other: List[str] = Field(default_factory=list, description="PO, SQ, FC, SS, DS")


class TemperatureData(BaseModel):
    """Temperature and dewpoint."""
    temperature: int = Field(..., description="Temperature in Celsius")
    dewpoint: int = Field(..., description="Dewpoint in Celsius")


class PressureData(BaseModel):
    """Altimeter/pressure information."""
    value: float = Field(..., description="Pressure value")
    unit: str = Field("inHg", description="Unit: inHg or hPa")


class MetarData(BaseModel):
    """Complete METAR observation."""
    station: str = Field(..., min_length=4, max_length=4, description="ICAO station code")
    observation_time: datetime = Field(..., description="Observation timestamp")
    raw_text: str = Field(..., description="Raw METAR string")
    
    # Decoded fields
    wind: Optional[WindData] = None
    visibility: Optional[VisibilityData] = None
    weather: List[WeatherPhenomenon] = Field(default_factory=list)
    clouds: List[CloudLayer] = Field(default_factory=list)
    temperature: Optional[TemperatureData] = None
    pressure: Optional[PressureData] = None
    
    # Flight category
    flight_category: Optional[str] = Field(None, description="VFR, MVFR, IFR, LIFR")
    
    # Metadata
    auto: bool = Field(False, description="Automated observation")
    corrected: bool = Field(False, description="Corrected report")
    remarks: Optional[str] = Field(None, description="Remarks section")
    
    # Cache metadata
    cached_at: Optional[datetime] = Field(None, description="When this was cached")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "station": "KJFK",
                "observation_time": "2025-12-04T16:51:00Z",
                "raw_text": "KJFK 041651Z 31008KT 10SM FEW250 04/M03 A3012",
                "flight_category": "VFR"
            }
        }
    )


class TafPeriod(BaseModel):
    """TAF forecast period."""
    from_time: datetime = Field(..., description="Period start time")
    to_time: datetime = Field(..., description="Period end time")
    change_indicator: Optional[str] = Field(None, description="FM, TEMPO, BECMG, PROB")
    probability: Optional[int] = Field(None, ge=0, le=100, description="Probability percentage")
    
    # Weather conditions
    wind: Optional[WindData] = None
    visibility: Optional[VisibilityData] = None
    weather: List[WeatherPhenomenon] = Field(default_factory=list)
    clouds: List[CloudLayer] = Field(default_factory=list)


class TafData(BaseModel):
    """Complete TAF forecast."""
    station: str = Field(..., min_length=4, max_length=4, description="ICAO station code")
    issue_time: datetime = Field(..., description="TAF issuance time")
    valid_from: datetime = Field(..., description="Forecast valid from")
    valid_to: datetime = Field(..., description="Forecast valid to")
    raw_text: str = Field(..., description="Raw TAF string")
    
    # Forecast periods
    periods: List[TafPeriod] = Field(default_factory=list)
    
    # Metadata
    amended: bool = Field(False, description="Amended TAF")
    cached_at: Optional[datetime] = Field(None, description="When this was cached")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "station": "KJFK",
                "issue_time": "2025-12-04T16:00:00Z",
                "valid_from": "2025-12-04T18:00:00Z",
                "valid_to": "2025-12-05T18:00:00Z",
                "raw_text": "TAF KJFK 041600Z 0418/0518 31010KT P6SM FEW250"
            }
        }
    )


class PirepData(BaseModel):
    """Pilot Report (PIREP)."""
    report_type: str = Field(..., description="UA (routine) or UUA (urgent)")
    observation_time: datetime = Field(..., description="Report timestamp")
    location: str = Field(..., description="Location of report")
    aircraft_type: Optional[str] = Field(None, description="Aircraft type")
    altitude: Optional[int] = Field(None, description="Altitude in feet")
    
    # Weather observations
    sky_conditions: Optional[str] = None
    turbulence: Optional[str] = None
    icing: Optional[str] = None
    visibility: Optional[str] = None
    temperature: Optional[int] = None
    wind: Optional[str] = None
    
    raw_text: str = Field(..., description="Raw PIREP text")
    cached_at: Optional[datetime] = Field(None, description="When this was cached")


class StationInfo(BaseModel):
    """Airport/station information."""
    icao: str = Field(..., min_length=4, max_length=4, description="ICAO code")
    name: Optional[str] = Field(None, description="Airport name")
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    elevation: Optional[int] = Field(None, description="Elevation in feet")
    
    # User preferences
    is_favorite: bool = Field(False, description="User favorite")
    last_accessed: Optional[datetime] = Field(None, description="Last time user viewed")


class UserSettings(BaseModel):
    """User application settings."""
    # Default airports
    default_airports: List[str] = Field(default_factory=lambda: ["KJFK", "KLAX", "KORD"])
    
    # Update settings
    update_frequency_minutes: int = Field(5, ge=1, le=60)
    cache_ttl_minutes: int = Field(10, ge=1, le=120)
    
    # Display preferences
    theme: str = Field("dark", description="light or dark")
    wind_unit: str = Field("knots", description="knots or mph")
    temperature_unit: str = Field("celsius", description="celsius or fahrenheit")
    pressure_unit: str = Field("inHg", description="inHg or hPa")
    
    # Training
    show_training_hints: bool = Field(True)
    completed_lessons: List[str] = Field(default_factory=list)
