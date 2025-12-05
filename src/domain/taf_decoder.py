"""
TAF Decoder for IVAO Weather Tool.
Parses raw TAF strings into structured TafData objects.
"""

import re
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Tuple
from ..data.models import (
    TafData, TafPeriod, WindData, VisibilityData,
    CloudLayer, WeatherPhenomenon
)


class TafDecoder:
    """Decodes TAF forecasts into structured data."""
    
    # Regex patterns for TAF components
    STATION_PATTERN = r'^TAF\s+(AMD\s+)?([A-Z]{4})\s+'
    ISSUE_PATTERN = r'(\d{6}Z)\s+'
    VALID_PATTERN = r'(\d{4})/(\d{4})\s+'
    
    # Change indicators
    CHANGE_PATTERN = r'(FM|TEMPO|BECMG|PROB\d{2})\s*'
    FM_PATTERN = r'FM(\d{6})\s+'
    TEMPO_BECMG_PATTERN = r'(TEMPO|BECMG)\s+(\d{4})/(\d{4})\s+'
    PROB_PATTERN = r'PROB(\d{2})\s+(TEMPO\s+)?(\d{4})/(\d{4})\s+'
    
    # Weather patterns (reuse from METAR)
    WIND_PATTERN = r'((\d{3})|VRB)(\d{2,3})(G(\d{2,3}))?(KT|MPS)\s+'
    VISIBILITY_PATTERN = r'(P)?(M)?(\d+(?:/\d+)?|\d+\s+\d+/\d+)(SM)\s+'
    WEATHER_PATTERN = r'([-+])?(MI|BC|PR|DR|BL|SH|TS|FZ)?(DZ|RA|SN|SG|IC|PL|GR|GS|UP|BR|FG|FU|VA|DU|SA|HZ|PY|PO|SQ|FC|SS|DS)+\s+'
    CLOUD_PATTERN = r'(SKC|CLR|NSC|NCD|FEW|SCT|BKN|OVC|VV)(\d{3})?(CB|TCU)?\s+'
    
    def decode(self, raw_taf: str, station: Optional[str] = None) -> TafData:
        """
        Decode a raw TAF string into a TafData object.
        
        Args:
            raw_taf: Raw TAF string
            station: Optional station override
            
        Returns:
            TafData object with parsed forecast periods
            
        Raises:
            ValueError: If TAF cannot be parsed
        """
        # Clean up the input
        taf = raw_taf.strip()
        original_taf = taf
        
        # Check for AMD (amended) flag
        amended = 'AMD' in taf[:20]
        
        # Extract station
        station_code = self._extract_station(taf, station)
        taf = re.sub(self.STATION_PATTERN, '', taf, count=1)
        
        # Extract issue time
        issue_time = self._extract_issue_time(taf)
        taf = re.sub(self.ISSUE_PATTERN, '', taf, count=1)
        
        # Extract valid period
        valid_from, valid_to, taf = self._extract_valid_period(taf, issue_time)
        
        # Parse forecast periods
        periods = self._parse_periods(taf, issue_time, valid_from, valid_to)
        
        return TafData(
            station=station_code,
            issue_time=issue_time,
            valid_from=valid_from,
            valid_to=valid_to,
            raw_text=original_taf,
            periods=periods,
            amended=amended,
            cached_at=datetime.now(timezone.utc)
        )
    
    def _extract_station(self, taf: str, override: Optional[str] = None) -> str:
        """Extract station identifier."""
        if override:
            return override.upper()
        
        match = re.match(self.STATION_PATTERN, taf)
        if not match:
            raise ValueError("Cannot find station identifier in TAF")
        return match.group(2)
    
    def _extract_issue_time(self, taf: str) -> datetime:
        """Extract TAF issuance time."""
        match = re.search(self.ISSUE_PATTERN, taf)
        if not match:
            raise ValueError("Cannot find issue time in TAF")
        
        dt_str = match.group(1)  # Format: DDHHmmZ
        day = int(dt_str[0:2])
        hour = int(dt_str[2:4])
        minute = int(dt_str[4:6])
        
        # Use current year and month
        now = datetime.now(timezone.utc)
        issue_time = datetime(now.year, now.month, day, hour, minute, tzinfo=timezone.utc)
        
        # Handle month rollover
        if issue_time > now + timedelta(days=1):
            if now.month == 1:
                issue_time = issue_time.replace(year=now.year - 1, month=12)
            else:
                issue_time = issue_time.replace(month=now.month - 1)
        
        return issue_time
    
    def _extract_valid_period(
        self,
        taf: str,
        issue_time: datetime
    ) -> Tuple[datetime, datetime, str]:
        """Extract TAF valid period."""
        match = re.search(self.VALID_PATTERN, taf)
        if not match:
            raise ValueError("Cannot find valid period in TAF")
        
        from_str = match.group(1)  # Format: DDHH
        to_str = match.group(2)     # Format: DDHH
        
        from_day = int(from_str[0:2])
        from_hour = int(from_str[2:4])
        to_day = int(to_str[0:2])
        to_hour = int(to_str[2:4])
        
        # Handle hour 24 (which means 00 of next day)
        if from_hour == 24:
            from_hour = 0
            from_day += 1
        if to_hour == 24:
            to_hour = 0
            to_day += 1
        
        # Build datetime objects
        valid_from = datetime(
            issue_time.year, issue_time.month, from_day, from_hour,
            tzinfo=timezone.utc
        )
        valid_to = datetime(
            issue_time.year, issue_time.month, to_day, to_hour,
            tzinfo=timezone.utc
        )
        
        # Handle day rollover
        if valid_to < valid_from:
            # Valid period crosses month boundary
            valid_to = valid_to.replace(month=valid_to.month + 1 if valid_to.month < 12 else 1)
            if valid_to.month == 1:
                valid_to = valid_to.replace(year=valid_to.year + 1)
        
        taf = re.sub(self.VALID_PATTERN, '', taf, count=1)
        
        return valid_from, valid_to, taf
    
    def _parse_periods(
        self,
        taf: str,
        issue_time: datetime,
        valid_from: datetime,
        valid_to: datetime
    ) -> List[TafPeriod]:
        """Parse all forecast periods from TAF."""
        periods = []
        
        # Split TAF into change groups
        # Look for FM, TEMPO, BECMG, PROB indicators
        parts = re.split(r'\s+(FM\d{6}|TEMPO|BECMG|PROB\d{2})\s+', taf)
        
        # First part is the base forecast
        if parts[0].strip():
            base_period = self._parse_base_period(parts[0], valid_from, valid_to)
            if base_period:
                periods.append(base_period)
        
        # Parse change groups
        i = 1
        while i < len(parts) - 1:
            indicator = parts[i].strip()
            content = parts[i + 1].strip()
            
            period = self._parse_change_group(indicator, content, issue_time, valid_from, valid_to)
            if period:
                periods.append(period)
            
            i += 2
        
        return periods
    
    def _parse_base_period(
        self,
        content: str,
        valid_from: datetime,
        valid_to: datetime
    ) -> Optional[TafPeriod]:
        """Parse the base forecast period."""
        content += ' '  # Ensure trailing space for regex patterns
        wind, content = self._extract_wind(content)
        visibility, content = self._extract_visibility(content)
        weather, content = self._extract_weather(content)
        clouds, content = self._extract_clouds(content)
        
        return TafPeriod(
            from_time=valid_from,
            to_time=valid_to,
            change_indicator=None,
            probability=None,
            wind=wind,
            visibility=visibility,
            weather=weather,
            clouds=clouds
        )
    
    def _parse_change_group(
        self,
        indicator: str,
        content: str,
        issue_time: datetime,
        base_from: datetime,
        base_to: datetime
    ) -> Optional[TafPeriod]:
        """Parse a change group (FM, TEMPO, BECMG, PROB)."""
        content += ' '  # Ensure trailing space for regex patterns
        if indicator.startswith('FM'):
            return self._parse_fm_group(indicator, content, issue_time, base_to)
        elif indicator.startswith('PROB'):
            return self._parse_prob_group(indicator, content, issue_time)
        elif indicator in ['TEMPO', 'BECMG']:
            return self._parse_tempo_becmg_group(indicator, content, issue_time)
        
        return None
    
    def _parse_fm_group(
        self,
        indicator: str,
        content: str,
        issue_time: datetime,
        base_to: datetime
    ) -> Optional[TafPeriod]:
        """Parse FM (FROM) group."""
        # Extract time from FM indicator (e.g., FM121800)
        match = re.match(r'FM(\d{6})', indicator)
        if not match:
            return None
        
        time_str = match.group(1)
        day = int(time_str[0:2])
        hour = int(time_str[2:4])
        minute = int(time_str[4:6])
        
        from_time = datetime(
            issue_time.year, issue_time.month, day, hour, minute,
            tzinfo=timezone.utc
        )
        
        # FM groups run until the next change or end of TAF
        to_time = base_to
        
        wind, content = self._extract_wind(content)
        visibility, content = self._extract_visibility(content)
        weather, content = self._extract_weather(content)
        clouds, content = self._extract_clouds(content)
        
        return TafPeriod(
            from_time=from_time,
            to_time=to_time,
            change_indicator='FM',
            probability=None,
            wind=wind,
            visibility=visibility,
            weather=weather,
            clouds=clouds
        )
    
    def _parse_tempo_becmg_group(
        self,
        indicator: str,
        content: str,
        issue_time: datetime
    ) -> Optional[TafPeriod]:
        """Parse TEMPO or BECMG group."""
        # Extract time period (e.g., TEMPO 1218/1224)
        match = re.match(r'(\d{4})/(\d{4})\s+', content)
        if not match:
            return None
        
        from_str = match.group(1)
        to_str = match.group(2)
        content = re.sub(r'(\d{4})/(\d{4})\s+', '', content, count=1)
        
        from_day = int(from_str[0:2])
        from_hour = int(from_str[2:4])
        to_day = int(to_str[0:2])
        to_hour = int(to_str[2:4])
        
        # Handle hour 24 (which means 00 of next day)
        if from_hour == 24:
            from_hour = 0
            from_day += 1
        if to_hour == 24:
            to_hour = 0
            to_day += 1
        
        from_time = datetime(
            issue_time.year, issue_time.month, from_day, from_hour,
            tzinfo=timezone.utc
        )
        to_time = datetime(
            issue_time.year, issue_time.month, to_day, to_hour,
            tzinfo=timezone.utc
        )
        
        wind, content = self._extract_wind(content)
        visibility, content = self._extract_visibility(content)
        weather, content = self._extract_weather(content)
        clouds, content = self._extract_clouds(content)
        
        return TafPeriod(
            from_time=from_time,
            to_time=to_time,
            change_indicator=indicator,
            probability=None,
            wind=wind,
            visibility=visibility,
            weather=weather,
            clouds=clouds
        )
    
    def _parse_prob_group(
        self,
        indicator: str,
        content: str,
        issue_time: datetime
    ) -> Optional[TafPeriod]:
        """Parse PROB (probability) group."""
        # Extract probability (e.g., PROB30)
        prob_match = re.match(r'PROB(\d{2})', indicator)
        if not prob_match:
            return None
        
        probability = int(prob_match.group(1))
        
        # Check for TEMPO after PROB
        has_tempo = content.startswith('TEMPO')
        if has_tempo:
            content = content.replace('TEMPO', '', 1).strip()
        
        # Extract time period
        match = re.match(r'(\d{4})/(\d{4})\s+', content)
        if not match:
            return None
        
        from_str = match.group(1)
        to_str = match.group(2)
        content = re.sub(r'(\d{4})/(\d{4})\s+', '', content, count=1)
        
        from_day = int(from_str[0:2])
        from_hour = int(from_str[2:4])
        to_day = int(to_str[0:2])
        to_hour = int(to_str[2:4])
        
        # Handle hour 24 (which means 00 of next day)
        if from_hour == 24:
            from_hour = 0
            from_day += 1
        if to_hour == 24:
            to_hour = 0
            to_day += 1
        
        from_time = datetime(
            issue_time.year, issue_time.month, from_day, from_hour,
            tzinfo=timezone.utc
        )
        to_time = datetime(
            issue_time.year, issue_time.month, to_day, to_hour,
            tzinfo=timezone.utc
        )
        
        wind, content = self._extract_wind(content)
        visibility, content = self._extract_visibility(content)
        weather, content = self._extract_weather(content)
        clouds, content = self._extract_clouds(content)
        
        change_ind = 'PROB' + ('TEMPO' if has_tempo else '')
        
        return TafPeriod(
            from_time=from_time,
            to_time=to_time,
            change_indicator=change_ind,
            probability=probability,
            wind=wind,
            visibility=visibility,
            weather=weather,
            clouds=clouds
        )
    
    # Reuse extraction methods from METAR decoder
    def _extract_wind(self, text: str) -> Tuple[Optional[WindData], str]:
        """Extract wind information."""
        match = re.search(self.WIND_PATTERN, text)
        if not match:
            return None, text
        
        direction_str = match.group(2) if match.group(2) else None
        direction = int(direction_str) if direction_str else None
        speed = int(match.group(3))
        gust = int(match.group(5)) if match.group(5) else None
        variable = match.group(1) == 'VRB'
        
        text = re.sub(self.WIND_PATTERN, '', text, count=1)
        
        return WindData(
            direction=direction,
            speed=speed,
            gust=gust,
            variable=variable
        ), text
    
    def _extract_visibility(self, text: str) -> Tuple[Optional[VisibilityData], str]:
        """Extract visibility information."""
        match = re.search(self.VISIBILITY_PATTERN, text)
        if not match:
            return None, text
        
        greater_than = match.group(1) == 'P'
        less_than = match.group(2) == 'M'
        vis_str = match.group(3)
        
        # Parse fractional visibility
        if '/' in vis_str:
            if ' ' in vis_str:
                parts = vis_str.split()
                whole = int(parts[0])
                frac_parts = parts[1].split('/')
                value = whole + int(frac_parts[0]) / int(frac_parts[1])
            else:
                frac_parts = vis_str.split('/')
                value = int(frac_parts[0]) / int(frac_parts[1])
        else:
            value = float(vis_str)
        
        # P6SM means "greater than 6 SM", treat as 10
        if greater_than:
            value = 10.0
        
        text = re.sub(self.VISIBILITY_PATTERN, '', text, count=1)
        
        return VisibilityData(value=value, unit='SM', less_than=less_than), text
    
    def _extract_weather(self, text: str) -> Tuple[List[WeatherPhenomenon], str]:
        """Extract weather phenomena."""
        weather_list = []
        
        while True:
            match = re.search(self.WEATHER_PATTERN, text)
            if not match:
                break
            
            intensity = match.group(1) if match.group(1) else None
            descriptor = match.group(2) if match.group(2) else None
            phenomena = match.group(3)
            
            # Parse phenomena codes
            precip = []
            obscur = []
            other = []
            
            # Reuse codes from METAR decoder
            PRECIPITATION_CODES = {'DZ', 'RA', 'SN', 'SG', 'IC', 'PL', 'GR', 'GS', 'UP'}
            OBSCURATION_CODES = {'BR', 'FG', 'FU', 'VA', 'DU', 'SA', 'HZ', 'PY'}
            OTHER_CODES = {'PO', 'SQ', 'FC', 'SS', 'DS'}
            
            for i in range(0, len(phenomena), 2):
                code = phenomena[i:i+2]
                if code in PRECIPITATION_CODES:
                    precip.append(code)
                elif code in OBSCURATION_CODES:
                    obscur.append(code)
                elif code in OTHER_CODES:
                    other.append(code)
            
            weather_list.append(WeatherPhenomenon(
                intensity=intensity,
                descriptor=descriptor,
                precipitation=precip,
                obscuration=obscur,
                other=other
            ))
            
            text = re.sub(self.WEATHER_PATTERN, '', text, count=1)
        
        return weather_list, text
    
    def _extract_clouds(self, text: str) -> Tuple[List[CloudLayer], str]:
        """Extract cloud layers."""
        clouds = []
        
        while True:
            match = re.search(self.CLOUD_PATTERN, text)
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
            
            text = re.sub(self.CLOUD_PATTERN, '', text, count=1)
        
        return clouds, text
