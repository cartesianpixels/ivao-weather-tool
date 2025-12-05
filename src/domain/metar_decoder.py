"""
METAR Decoder for IVAO Weather Tool.
Parses raw METAR strings into structured MetarData objects.
"""

import re
from datetime import datetime, timezone
from typing import Optional, List, Tuple
from ..data.models import (
    MetarData, WindData, VisibilityData, CloudLayer,
    WeatherPhenomenon, TemperatureData, PressureData
)
from .remarks_decoder import RemarksDecoder
from dataclasses import asdict


class MetarDecoder:
    """Decodes METAR observations into structured data."""
    
    def __init__(self):
        """Initialize METAR decoder with remarks decoder."""
        self.remarks_decoder = RemarksDecoder()
    
    # Regex patterns for METAR components
    STATION_PATTERN = r'^([A-Z]{4})\s+'
    DATETIME_PATTERN = r'(\d{6}Z)\s+'
    WIND_PATTERN = r'((\d{3})|VRB)(\d{2,3})(G(\d{2,3}))?(KT|MPS)\s+'
    WIND_VARIABLE_PATTERN = r'(\d{3})V(\d{3})\s+'
    VISIBILITY_PATTERN = r'(M)?(\d+(?:/\d+)?|\d+\s+\d+/\d+)(SM)\s+'
    WEATHER_PATTERN = r'([-+])?(MI|BC|PR|DR|BL|SH|TS|FZ)?(DZ|RA|SN|SG|IC|PL|GR|GS|UP|BR|FG|FU|VA|DU|SA|HZ|PY|PO|SQ|FC|SS|DS)+\s+'
    CLOUD_PATTERN = r'(SKC|CLR|NSC|NCD|FEW|SCT|BKN|OVC|VV)(\d{3})?(CB|TCU)?\s+'
    TEMP_DEW_PATTERN = r'(M)?(\d{2})/(M)?(\d{2})\s+'
    ALTIMETER_PATTERN = r'(A|Q)(\d{4})\s*'
    
    # Weather phenomenon codes
    INTENSITY_CODES = {'-': 'light', '+': 'heavy', '': 'moderate'}
    DESCRIPTOR_CODES = {
        'MI': 'shallow', 'BC': 'patches', 'PR': 'partial', 'DR': 'low drifting',
        'BL': 'blowing', 'SH': 'showers', 'TS': 'thunderstorm', 'FZ': 'freezing'
    }
    PRECIPITATION_CODES = {
        'DZ': 'drizzle', 'RA': 'rain', 'SN': 'snow', 'SG': 'snow grains',
        'IC': 'ice crystals', 'PL': 'ice pellets', 'GR': 'hail', 'GS': 'small hail',
        'UP': 'unknown precipitation'
    }
    OBSCURATION_CODES = {
        'BR': 'mist', 'FG': 'fog', 'FU': 'smoke', 'VA': 'volcanic ash',
        'DU': 'dust', 'SA': 'sand', 'HZ': 'haze', 'PY': 'spray'
    }
    OTHER_CODES = {
        'PO': 'dust/sand whirls', 'SQ': 'squalls', 'FC': 'funnel cloud',
        'SS': 'sandstorm', 'DS': 'duststorm'
    }
    
    # Cloud coverage codes
    CLOUD_COVERAGE = {
        'SKC': 'sky clear', 'CLR': 'clear', 'NSC': 'no significant clouds',
        'NCD': 'no clouds detected', 'FEW': 'few', 'SCT': 'scattered',
        'BKN': 'broken', 'OVC': 'overcast', 'VV': 'vertical visibility'
    }
    
    def decode(self, raw_metar: str, station: Optional[str] = None) -> MetarData:
        """
        Decode a raw METAR string into a MetarData object.
        
        Args:
            raw_metar: Raw METAR string
            station: Optional station override (if not in METAR)
            
        Returns:
            MetarData object with parsed components
            
        Raises:
            ValueError: If METAR cannot be parsed
        """
        # Clean up the input
        metar = raw_metar.strip()
        original_metar = metar
        
        # Extract station
        station_code = self._extract_station(metar, station)
        metar = re.sub(self.STATION_PATTERN, '', metar, count=1)
        
        # Check for AUTO and COR flags
        auto = 'AUTO' in metar
        corrected = 'COR' in metar
        metar = metar.replace('AUTO', '').replace('COR', '')
        
        # Extract observation time
        obs_time = self._extract_datetime(metar)
        metar = re.sub(self.DATETIME_PATTERN, '', metar, count=1)
        
        # Extract wind
        wind_data, metar = self._extract_wind(metar)
        
        # Extract visibility
        visibility_data, metar = self._extract_visibility(metar)
        
        # Extract weather phenomena
        weather_list, metar = self._extract_weather(metar)
        
        # Extract clouds
        clouds_list, metar = self._extract_clouds(metar)
        
        # Extract temperature and dewpoint
        temp_data, metar = self._extract_temperature(metar)
        
        # Extract altimeter
        pressure_data, metar = self._extract_pressure(metar)
        
        # Extract remarks (everything after RMK)
        remarks = None
        remarks_data = None
        if 'RMK' in metar:
            parts = metar.split('RMK', 1)
            metar = parts[0]
            remarks = parts[1].strip() if len(parts) > 1 else None
            
            # Decode remarks
            if remarks:
                decoded_remarks = self.remarks_decoder.decode(remarks)
                remarks_data = asdict(decoded_remarks)
        
        # Calculate flight category
        flight_category = self._calculate_flight_category(visibility_data, clouds_list)
        
        return MetarData(
            station=station_code,
            observation_time=obs_time,
            raw_text=original_metar,
            wind=wind_data,
            visibility=visibility_data,
            weather=weather_list,
            clouds=clouds_list,
            temperature=temp_data,
            pressure=pressure_data,
            flight_category=flight_category,
            auto=auto,
            corrected=corrected,
            remarks=remarks,
            remarks_data=remarks_data,
            cached_at=datetime.now(timezone.utc)
        )
    
    def _extract_station(self, metar: str, override: Optional[str] = None) -> str:
        """Extract station identifier."""
        if override:
            return override.upper()
        
        match = re.match(self.STATION_PATTERN, metar)
        if not match:
            raise ValueError("Cannot find station identifier in METAR")
        return match.group(1)
    
    def _extract_datetime(self, metar: str) -> datetime:
        """Extract observation datetime."""
        match = re.search(self.DATETIME_PATTERN, metar)
        if not match:
            raise ValueError("Cannot find datetime in METAR")
        
        dt_str = match.group(1)  # Format: DDHHmmZ
        day = int(dt_str[0:2])
        hour = int(dt_str[2:4])
        minute = int(dt_str[4:6])
        
        # Use current year and month (METAR doesn't include year/month)
        now = datetime.now(timezone.utc)
        obs_time = datetime(now.year, now.month, day, hour, minute, tzinfo=timezone.utc)
        
        # Handle month rollover
        if obs_time > now:
            # Observation is from previous month
            if now.month == 1:
                obs_time = obs_time.replace(year=now.year - 1, month=12)
            else:
                obs_time = obs_time.replace(month=now.month - 1)
        
        return obs_time
    
    def _extract_wind(self, metar: str) -> Tuple[Optional[WindData], str]:
        """Extract wind information."""
        match = re.search(self.WIND_PATTERN, metar)
        if not match:
            return None, metar
        
        direction_str = match.group(2) if match.group(2) else None
        direction = int(direction_str) if direction_str else None
        speed = int(match.group(3))
        gust = int(match.group(5)) if match.group(5) else None
        variable = match.group(1) == 'VRB'
        
        # Remove wind from string
        metar = re.sub(self.WIND_PATTERN, '', metar, count=1)
        
        # Check for variable wind direction
        var_from = None
        var_to = None
        var_match = re.search(self.WIND_VARIABLE_PATTERN, metar)
        if var_match:
            var_from = int(var_match.group(1))
            var_to = int(var_match.group(2))
            metar = re.sub(self.WIND_VARIABLE_PATTERN, '', metar, count=1)
        
        return WindData(
            direction=direction,
            speed=speed,
            gust=gust,
            variable=variable,
            variable_from=var_from,
            variable_to=var_to
        ), metar
    
    def _extract_visibility(self, metar: str) -> Tuple[Optional[VisibilityData], str]:
        """Extract visibility information."""
        # Handle CAVOK (Ceiling And Visibility OK)
        if 'CAVOK' in metar:
            metar = metar.replace('CAVOK', '')
            return VisibilityData(value=10.0, unit='SM', less_than=False), metar
        
        match = re.search(self.VISIBILITY_PATTERN, metar)
        if not match:
            return None, metar
        
        less_than = match.group(1) == 'M'
        vis_str = match.group(2)
        
        # Parse fractional visibility (e.g., "1/2", "1 1/2")
        if '/' in vis_str:
            if ' ' in vis_str:
                # Format: "1 1/2"
                parts = vis_str.split()
                whole = int(parts[0])
                frac_parts = parts[1].split('/')
                value = whole + int(frac_parts[0]) / int(frac_parts[1])
            else:
                # Format: "1/2"
                frac_parts = vis_str.split('/')
                value = int(frac_parts[0]) / int(frac_parts[1])
        else:
            value = float(vis_str)
        
        metar = re.sub(self.VISIBILITY_PATTERN, '', metar, count=1)
        
        return VisibilityData(value=value, unit='SM', less_than=less_than), metar
    
    def _extract_weather(self, metar: str) -> Tuple[List[WeatherPhenomenon], str]:
        """Extract weather phenomena."""
        weather_list = []
        
        while True:
            match = re.search(self.WEATHER_PATTERN, metar)
            if not match:
                break
            
            intensity = match.group(1) if match.group(1) else ''
            descriptor = match.group(2) if match.group(2) else None
            phenomena = match.group(3)
            
            # Parse phenomena codes (2-letter codes)
            precip = []
            obscur = []
            other = []
            
            for i in range(0, len(phenomena), 2):
                code = phenomena[i:i+2]
                if code in self.PRECIPITATION_CODES:
                    precip.append(code)
                elif code in self.OBSCURATION_CODES:
                    obscur.append(code)
                elif code in self.OTHER_CODES:
                    other.append(code)
            
            weather_list.append(WeatherPhenomenon(
                intensity=intensity if intensity else None,
                descriptor=descriptor,
                precipitation=precip,
                obscuration=obscur,
                other=other
            ))
            
            metar = re.sub(self.WEATHER_PATTERN, '', metar, count=1)
        
        return weather_list, metar
    
    def _extract_clouds(self, metar: str) -> Tuple[List[CloudLayer], str]:
        """Extract cloud layers."""
        clouds = []
        
        while True:
            match = re.search(self.CLOUD_PATTERN, metar)
            if not match:
                break
            
            coverage = match.group(1)
            altitude = int(match.group(2)) * 100 if match.group(2) else None
            cloud_type = match.group(3) if match.group(3) else None
            
            clouds.append(CloudLayer(
                coverage=coverage,
                altitude=altitude,
                type=cloud_type
            ))
            
            metar = re.sub(self.CLOUD_PATTERN, '', metar, count=1)
        
        return clouds, metar
    
    def _extract_temperature(self, metar: str) -> Tuple[Optional[TemperatureData], str]:
        """Extract temperature and dewpoint."""
        match = re.search(self.TEMP_DEW_PATTERN, metar)
        if not match:
            return None, metar
        
        temp = int(match.group(2))
        if match.group(1) == 'M':
            temp = -temp
        
        dewpoint = int(match.group(4))
        if match.group(3) == 'M':
            dewpoint = -dewpoint
        
        metar = re.sub(self.TEMP_DEW_PATTERN, '', metar, count=1)
        
        return TemperatureData(temperature=temp, dewpoint=dewpoint), metar
    
    def _extract_pressure(self, metar: str) -> Tuple[Optional[PressureData], str]:
        """Extract altimeter/pressure setting."""
        match = re.search(self.ALTIMETER_PATTERN, metar)
        if not match:
            return None, metar
        
        unit_code = match.group(1)
        value_str = match.group(2)
        
        if unit_code == 'A':
            # US format: inches of mercury (e.g., A3012 = 30.12 inHg)
            value = int(value_str) / 100.0
            unit = 'inHg'
        else:
            # International format: hectopascals (e.g., Q1013 = 1013 hPa)
            value = float(value_str)
            unit = 'hPa'
        
        metar = re.sub(self.ALTIMETER_PATTERN, '', metar, count=1)
        
        return PressureData(value=value, unit=unit), metar
    
    def _calculate_flight_category(
        self,
        visibility: Optional[VisibilityData],
        clouds: List[CloudLayer]
    ) -> str:
        """
        Calculate flight category based on visibility and ceiling.
        
        VFR: Visibility >= 5 SM and Ceiling >= 3000 ft
        MVFR: Visibility 3-5 SM or Ceiling 1000-3000 ft
        IFR: Visibility 1-3 SM or Ceiling 500-1000 ft
        LIFR: Visibility < 1 SM or Ceiling < 500 ft
        """
        vis_value = visibility.value if visibility else 10.0
        
        # Find ceiling (lowest BKN or OVC layer)
        ceiling = None
        for cloud in clouds:
            if cloud.coverage in ['BKN', 'OVC', 'VV'] and cloud.altitude is not None:
                if ceiling is None or cloud.altitude < ceiling:
                    ceiling = cloud.altitude
        
        # Default to high ceiling if none reported
        if ceiling is None:
            ceiling = 10000
        
        # Determine category
        if vis_value < 1 or ceiling < 500:
            return 'LIFR'
        elif vis_value < 3 or ceiling < 1000:
            return 'IFR'
        elif vis_value <= 5 or ceiling <= 3000:
            return 'MVFR'
        else:
            return 'VFR'
