"""
METAR Remarks Decoder for IVAO Weather Tool.
Decodes the RMK (remarks) section of METAR reports.
"""

import re
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class RemarksData:
    """Parsed METAR remarks data."""
    
    # Automated station type
    automated_station_type: Optional[str] = None  # AO1 or AO2
    
    # Peak wind
    peak_wind_direction: Optional[int] = None
    peak_wind_speed: Optional[int] = None
    peak_wind_time: Optional[str] = None
    
    # Wind shift
    wind_shift_time: Optional[str] = None
    wind_shift_frontal: bool = False
    
    # Tower/surface visibility
    tower_visibility: Optional[float] = None
    surface_visibility: Optional[float] = None
    variable_visibility: Optional[str] = None
    
    # Sector visibility
    sector_visibility: Dict[str, float] = field(default_factory=dict)
    
    # Visibility at second location
    visibility_second_location: Optional[float] = None
    second_location_name: Optional[str] = None
    
    # Lightning
    lightning_types: List[str] = field(default_factory=list)
    lightning_frequency: Optional[str] = None
    lightning_location: Optional[str] = None
    
    # Precipitation
    precipitation_began_ended: List[Dict[str, Any]] = field(default_factory=list)
    thunderstorm_began_ended: List[Dict[str, Any]] = field(default_factory=list)
    
    # Precipitation amounts
    hourly_precip: Optional[float] = None  # inches
    precip_3hr: Optional[float] = None
    precip_6hr: Optional[float] = None
    precip_24hr: Optional[float] = None
    
    # Snow
    snow_depth: Optional[int] = None  # inches
    snow_increasing_rapidly: Optional[str] = None
    water_equivalent_snow: Optional[float] = None
    
    # Pressure
    sea_level_pressure: Optional[float] = None  # hPa
    pressure_tendency: Optional[str] = None
    pressure_change: Optional[float] = None
    
    # Temperature
    temperature_precise: Optional[float] = None  # Celsius (tenths)
    dewpoint_precise: Optional[float] = None  # Celsius (tenths)
    max_temp_6hr: Optional[float] = None
    min_temp_6hr: Optional[float] = None
    max_temp_24hr: Optional[float] = None
    min_temp_24hr: Optional[float] = None
    
    # Sensor status
    sensor_status: List[str] = field(default_factory=list)
    
    # Maintenance needed
    maintenance_needed: bool = False
    
    # Plain language remarks
    plain_language: List[str] = field(default_factory=list)
    
    # Raw remarks string
    raw_remarks: str = ""


class RemarksDecoder:
    """Decodes METAR remarks section."""
    
    # Automated station type
    AO_PATTERN = r'\b(AO[12])\b'
    
    # Peak wind: PK WND 28045/15
    PEAK_WIND_PATTERN = r'PK\s+WND\s+(\d{3})(\d{2,3})/(\d{2,4})'
    
    # Wind shift: WSHFT 30 or WSHFT 1730 FROPA
    WIND_SHIFT_PATTERN = r'WSHFT\s+(\d{2,4})(\s+FROPA)?'
    
    # Tower/surface visibility: TWR VIS 1 1/2 or SFC VIS 2
    TOWER_VIS_PATTERN = r'TWR\s+VIS\s+([\d\s/]+)'
    SURFACE_VIS_PATTERN = r'SFC\s+VIS\s+([\d\s/]+)'
    
    # Variable visibility: VIS 1/2V2
    VARIABLE_VIS_PATTERN = r'VIS\s+([\d/]+)V([\d/]+)'
    
    # Sector visibility: VIS N 2 or VIS NE 1 1/2
    SECTOR_VIS_PATTERN = r'VIS\s+([NEWS]{1,2})\s+([\d\s/]+)'
    
    # Lightning: LTG DSNT NW or FRQ LTGIC OHD
    LIGHTNING_PATTERN = r'(?:(OCNL|FRQ|CONS)\s+)?(LTG|LTGIC|LTGCG|LTGCA|LTGCC)\s+(OHD|DSNT|VC|AND)?\s*([NEWS]{1,2})?'
    
    # Precipitation began/ended: RAB05E30 or SNB20
    PRECIP_BEG_END_PATTERN = r'([A-Z]{2})(B(\d{2,4}))?(E(\d{2,4}))?'
    
    # Hourly precipitation: P0009
    HOURLY_PRECIP_PATTERN = r'\bP(\d{4})\b'
    
    # 3/6 hour precipitation: 60217
    PRECIP_3_6HR_PATTERN = r'\b6(\d{4})\b'
    
    # 24 hour precipitation: 70125
    PRECIP_24HR_PATTERN = r'\b7(\d{4})\b'
    
    # Snow depth: 4/021
    SNOW_DEPTH_PATTERN = r'\b4/(\d{3})\b'
    
    # Snow increasing rapidly: SNINCR 2/10
    SNOW_INCR_PATTERN = r'SNINCR\s+(\d+)/(\d+)'
    
    # Water equivalent of snow: 933036
    WATER_EQUIV_SNOW_PATTERN = r'\b933(\d{3})\b'
    
    # Sea level pressure: SLP201 (1020.1 hPa)
    SLP_PATTERN = r'\bSLP(\d{3})\b'
    
    # Precise temperature/dewpoint: T00441028 (4.4C / -2.8C)
    TEMP_PRECISE_PATTERN = r'\bT([01])(\d{3})([01])(\d{3})\b'
    
    # Max/min temperature 6hr: 10142 (max 14.2C) or 21012 (min -1.2C)
    MAX_TEMP_6HR_PATTERN = r'\b1([01])(\d{3})\b'
    MIN_TEMP_6HR_PATTERN = r'\b2([01])(\d{3})\b'
    
    # Max/min temperature 24hr: 400561015 (max 5.6C, min -1.5C)
    TEMP_24HR_PATTERN = r'\b4([01])(\d{3})([01])(\d{3})\b'
    
    # Pressure tendency: 52032 (rising, +3.2 hPa in 3 hrs)
    PRESSURE_TENDENCY_PATTERN = r'\b5([0-8])(\d{3})\b'
    
    # Sensor status: RVRNO, PWINO, PNO, FZRANO, TSNO, VISNO
    SENSOR_STATUS_PATTERN = r'\b(RVRNO|PWINO|PNO|FZRANO|TSNO|VISNO|CHINO)\b'
    
    # Maintenance indicator
    MAINTENANCE_PATTERN = r'(^|\s)\$'
    
    def decode(self, remarks: str) -> RemarksData:
        """
        Decode METAR remarks section.
        
        Args:
            remarks: Raw remarks string (after RMK)
            
        Returns:
            RemarksData object with parsed remarks
        """
        if not remarks:
            return RemarksData()
        
        data = RemarksData(raw_remarks=remarks)
        
        # Extract coded data groups
        self._extract_automated_station(remarks, data)
        self._extract_peak_wind(remarks, data)
        self._extract_wind_shift(remarks, data)
        self._extract_visibility_remarks(remarks, data)
        self._extract_lightning(remarks, data)
        self._extract_precipitation_times(remarks, data)
        self._extract_precipitation_amounts(remarks, data)
        self._extract_snow_data(remarks, data)
        self._extract_pressure_data(remarks, data)
        self._extract_temperature_data(remarks, data)
        self._extract_sensor_status(remarks, data)
        self._extract_maintenance(remarks, data)
        self._extract_plain_language(remarks, data)
        
        return data
    
    def _extract_automated_station(self, remarks: str, data: RemarksData):
        """Extract automated station type (AO1/AO2)."""
        match = re.search(self.AO_PATTERN, remarks)
        if match:
            data.automated_station_type = match.group(1)
    
    def _extract_peak_wind(self, remarks: str, data: RemarksData):
        """Extract peak wind data."""
        match = re.search(self.PEAK_WIND_PATTERN, remarks)
        if match:
            data.peak_wind_direction = int(match.group(1))
            data.peak_wind_speed = int(match.group(2))
            data.peak_wind_time = match.group(3)
    
    def _extract_wind_shift(self, remarks: str, data: RemarksData):
        """Extract wind shift data."""
        match = re.search(self.WIND_SHIFT_PATTERN, remarks)
        if match:
            data.wind_shift_time = match.group(1)
            data.wind_shift_frontal = match.group(2) is not None
    
    def _extract_visibility_remarks(self, remarks: str, data: RemarksData):
        """Extract visibility remarks."""
        # Tower visibility
        match = re.search(self.TOWER_VIS_PATTERN, remarks)
        if match:
            data.tower_visibility = self._parse_visibility(match.group(1))
        
        # Surface visibility
        match = re.search(self.SURFACE_VIS_PATTERN, remarks)
        if match:
            data.surface_visibility = self._parse_visibility(match.group(1))
        
        # Variable visibility
        match = re.search(self.VARIABLE_VIS_PATTERN, remarks)
        if match:
            data.variable_visibility = f"{match.group(1)}V{match.group(2)}"
        
        # Sector visibility
        for match in re.finditer(self.SECTOR_VIS_PATTERN, remarks):
            sector = match.group(1)
            vis = self._parse_visibility(match.group(2))
            data.sector_visibility[sector] = vis
    
    def _extract_lightning(self, remarks: str, data: RemarksData):
        """Extract lightning information."""
        match = re.search(self.LIGHTNING_PATTERN, remarks)
        if match:
            data.lightning_frequency = match.group(1)  # OCNL, FRQ, CONS
            data.lightning_types.append(match.group(2))  # LTG, LTGIC, etc.
            if match.group(3):
                data.lightning_location = match.group(3)  # OHD, DSNT, VC
            if match.group(4):
                if data.lightning_location:
                    data.lightning_location += f" {match.group(4)}"
                else:
                    data.lightning_location = match.group(4)
    
    def _extract_precipitation_times(self, remarks: str, data: RemarksData):
        """Extract precipitation beginning/ending times."""
        # Common precipitation types
        precip_types = ['RA', 'SN', 'DZ', 'SG', 'IC', 'PL', 'GR', 'GS']
        ts_types = ['TS']
        
        for match in re.finditer(self.PRECIP_BEG_END_PATTERN, remarks):
            precip_type = match.group(1)
            begin_time = match.group(3) if match.group(3) else None
            end_time = match.group(5) if match.group(5) else None
            
            if precip_type in precip_types:
                data.precipitation_began_ended.append({
                    'type': precip_type,
                    'began': begin_time,
                    'ended': end_time
                })
            elif precip_type in ts_types:
                data.thunderstorm_began_ended.append({
                    'began': begin_time,
                    'ended': end_time
                })
    
    def _extract_precipitation_amounts(self, remarks: str, data: RemarksData):
        """Extract precipitation amount data."""
        # Hourly precipitation
        match = re.search(self.HOURLY_PRECIP_PATTERN, remarks)
        if match:
            value = int(match.group(1))
            data.hourly_precip = value / 100.0  # Convert to inches
        
        # 3/6 hour precipitation
        match = re.search(self.PRECIP_3_6HR_PATTERN, remarks)
        if match:
            value = int(match.group(1))
            data.precip_6hr = value / 100.0  # Assume 6hr for now
        
        # 24 hour precipitation
        match = re.search(self.PRECIP_24HR_PATTERN, remarks)
        if match:
            value = int(match.group(1))
            data.precip_24hr = value / 100.0
    
    def _extract_snow_data(self, remarks: str, data: RemarksData):
        """Extract snow-related data."""
        # Snow depth
        match = re.search(self.SNOW_DEPTH_PATTERN, remarks)
        if match:
            data.snow_depth = int(match.group(1))
        
        # Snow increasing rapidly
        match = re.search(self.SNOW_INCR_PATTERN, remarks)
        if match:
            data.snow_increasing_rapidly = f"{match.group(1)} inches in past {match.group(2)} minutes"
        
        # Water equivalent of snow
        match = re.search(self.WATER_EQUIV_SNOW_PATTERN, remarks)
        if match:
            value = int(match.group(1))
            data.water_equivalent_snow = value / 10.0  # Convert to inches
    
    def _extract_pressure_data(self, remarks: str, data: RemarksData):
        """Extract pressure-related data."""
        # Sea level pressure
        match = re.search(self.SLP_PATTERN, remarks)
        if match:
            slp_code = int(match.group(1))
            # SLP is coded as last 3 digits of hPa
            # 201 = 1020.1, 998 = 999.8
            if slp_code >= 500:
                data.sea_level_pressure = 900 + (slp_code / 10.0)
            else:
                data.sea_level_pressure = 1000 + (slp_code / 10.0)
        
        # Pressure tendency
        match = re.search(self.PRESSURE_TENDENCY_PATTERN, remarks)
        if match:
            tendency_code = int(match.group(1))
            change_value = int(match.group(2))
            data.pressure_change = change_value / 10.0  # Convert to hPa
            
            # Tendency codes: 0-3 rising, 4 steady, 5-8 falling
            tendency_desc = {
                0: 'increasing then decreasing',
                1: 'increasing then steady',
                2: 'increasing',
                3: 'increasing rapidly',
                4: 'steady',
                5: 'decreasing then increasing',
                6: 'decreasing then steady',
                7: 'decreasing',
                8: 'decreasing rapidly'
            }
            data.pressure_tendency = tendency_desc.get(tendency_code, 'unknown')
    
    def _extract_temperature_data(self, remarks: str, data: RemarksData):
        """Extract temperature-related data."""
        # Precise temperature/dewpoint
        match = re.search(self.TEMP_PRECISE_PATTERN, remarks)
        if match:
            temp_sign = 1 if match.group(1) == '0' else -1
            temp_value = int(match.group(2))
            data.temperature_precise = temp_sign * (temp_value / 10.0)
            
            dew_sign = 1 if match.group(3) == '0' else -1
            dew_value = int(match.group(4))
            data.dewpoint_precise = dew_sign * (dew_value / 10.0)
        
        # Max temperature 6hr
        match = re.search(self.MAX_TEMP_6HR_PATTERN, remarks)
        if match:
            sign = 1 if match.group(1) == '0' else -1
            value = int(match.group(2))
            data.max_temp_6hr = sign * (value / 10.0)
        
        # Min temperature 6hr
        match = re.search(self.MIN_TEMP_6HR_PATTERN, remarks)
        if match:
            sign = 1 if match.group(1) == '0' else -1
            value = int(match.group(2))
            data.min_temp_6hr = sign * (value / 10.0)
        
        # 24hr max/min temperature
        match = re.search(self.TEMP_24HR_PATTERN, remarks)
        if match:
            max_sign = 1 if match.group(1) == '0' else -1
            max_value = int(match.group(2))
            data.max_temp_24hr = max_sign * (max_value / 10.0)
            
            min_sign = 1 if match.group(3) == '0' else -1
            min_value = int(match.group(4))
            data.min_temp_24hr = min_sign * (min_value / 10.0)
    
    def _extract_sensor_status(self, remarks: str, data: RemarksData):
        """Extract sensor status indicators."""
        for match in re.finditer(self.SENSOR_STATUS_PATTERN, remarks):
            data.sensor_status.append(match.group(1))
    
    def _extract_maintenance(self, remarks: str, data: RemarksData):
        """Extract maintenance indicator."""
        if re.search(self.MAINTENANCE_PATTERN, remarks):
            data.maintenance_needed = True
    
    def _extract_plain_language(self, remarks: str, data: RemarksData):
        """Extract plain language remarks."""
        # Remove all coded groups to get plain language
        cleaned = remarks
        
        # Remove all known patterns
        patterns = [
            self.AO_PATTERN, self.PEAK_WIND_PATTERN, self.WIND_SHIFT_PATTERN,
            self.TOWER_VIS_PATTERN, self.SURFACE_VIS_PATTERN, self.VARIABLE_VIS_PATTERN,
            self.SECTOR_VIS_PATTERN, self.LIGHTNING_PATTERN, self.HOURLY_PRECIP_PATTERN,
            self.PRECIP_3_6HR_PATTERN, self.PRECIP_24HR_PATTERN, self.SNOW_DEPTH_PATTERN,
            self.SNOW_INCR_PATTERN, self.WATER_EQUIV_SNOW_PATTERN, self.SLP_PATTERN,
            self.TEMP_PRECISE_PATTERN, self.MAX_TEMP_6HR_PATTERN, self.MIN_TEMP_6HR_PATTERN,
            self.TEMP_24HR_PATTERN, self.PRESSURE_TENDENCY_PATTERN, self.SENSOR_STATUS_PATTERN,
            self.MAINTENANCE_PATTERN
        ]
        
        for pattern in patterns:
            cleaned = re.sub(pattern, '', cleaned)
        
        # Split into words and filter out empty strings
        words = cleaned.split()
        if words:
            # Group into phrases (simple approach)
            data.plain_language = [' '.join(words)]
    
    def _parse_visibility(self, vis_str: str) -> float:
        """Parse visibility string to float value."""
        vis_str = vis_str.strip()
        
        # Handle fractions
        if '/' in vis_str:
            if ' ' in vis_str:
                # e.g., "1 1/2"
                parts = vis_str.split()
                whole = int(parts[0])
                frac_parts = parts[1].split('/')
                return whole + int(frac_parts[0]) / int(frac_parts[1])
            else:
                # e.g., "1/2"
                frac_parts = vis_str.split('/')
                return int(frac_parts[0]) / int(frac_parts[1])
        else:
            return float(vis_str)
