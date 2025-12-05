"""
Tests for METAR Remarks Decoder.
"""

import pytest
from src.domain.remarks_decoder import RemarksDecoder

class TestRemarksDecoder:
    """Test cases for METAR remarks decoding."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.decoder = RemarksDecoder()
    
    def test_empty_remarks(self):
        """Test empty remarks string."""
        data = self.decoder.decode("")
        assert data.raw_remarks == ""
        assert data.automated_station_type is None
    
    def test_automated_station(self):
        """Test automated station type extraction."""
        # AO1: Automated station without precipitation discriminator
        data = self.decoder.decode("AO1")
        assert data.automated_station_type == "AO1"
        
        # AO2: Automated station with precipitation discriminator
        data = self.decoder.decode("AO2")
        assert data.automated_station_type == "AO2"
    
    def test_peak_wind(self):
        """Test peak wind extraction."""
        # PK WND 28045/15
        data = self.decoder.decode("PK WND 28045/15")
        assert data.peak_wind_direction == 280
        assert data.peak_wind_speed == 45
        assert data.peak_wind_time == "15"
    
    def test_wind_shift(self):
        """Test wind shift extraction."""
        # WSHFT 30
        data = self.decoder.decode("WSHFT 30")
        assert data.wind_shift_time == "30"
        assert data.wind_shift_frontal is False
        
        # WSHFT 1730 FROPA
        data = self.decoder.decode("WSHFT 1730 FROPA")
        assert data.wind_shift_time == "1730"
        assert data.wind_shift_frontal is True
    
    def test_visibility_remarks(self):
        """Test visibility remarks extraction."""
        # Tower visibility
        data = self.decoder.decode("TWR VIS 1 1/2")
        assert data.tower_visibility == 1.5
        
        # Surface visibility
        data = self.decoder.decode("SFC VIS 2")
        assert data.surface_visibility == 2.0
        
        # Variable visibility
        data = self.decoder.decode("VIS 1/2V2")
        assert data.variable_visibility == "1/2V2"
        
        # Sector visibility
        data = self.decoder.decode("VIS NE 2 1/2")
        assert data.sector_visibility["NE"] == 2.5
    
    def test_lightning(self):
        """Test lightning information extraction."""
        # Distant lightning
        data = self.decoder.decode("LTG DSNT NW")
        assert "LTG" in data.lightning_types
        assert data.lightning_location == "DSNT NW"
        
        # Frequent lightning overhead
        data = self.decoder.decode("FRQ LTGIC OHD")
        assert data.lightning_frequency == "FRQ"
        assert "LTGIC" in data.lightning_types
        assert data.lightning_location == "OHD"
    
    def test_precipitation_times(self):
        """Test precipitation beginning/ending times."""
        # Rain began at 05, ended at 30
        data = self.decoder.decode("RAB05E30")
        assert len(data.precipitation_began_ended) == 1
        assert data.precipitation_began_ended[0]['type'] == 'RA'
        assert data.precipitation_began_ended[0]['began'] == '05'
        assert data.precipitation_began_ended[0]['ended'] == '30'
        
        # Snow began at 20
        data = self.decoder.decode("SNB20")
        assert len(data.precipitation_began_ended) == 1
        assert data.precipitation_began_ended[0]['type'] == 'SN'
        assert data.precipitation_began_ended[0]['began'] == '20'
        assert data.precipitation_began_ended[0]['ended'] is None
    
    def test_precipitation_amounts(self):
        """Test precipitation amounts extraction."""
        # Hourly precip: 0.09 inches
        data = self.decoder.decode("P0009")
        assert data.hourly_precip == 0.09
        
        # 6hr precip: 2.17 inches
        data = self.decoder.decode("60217")
        assert data.precip_6hr == 2.17
        
        # 24hr precip: 1.25 inches
        data = self.decoder.decode("70125")
        assert data.precip_24hr == 1.25
    
    def test_snow_data(self):
        """Test snow data extraction."""
        # Snow depth: 21 inches
        data = self.decoder.decode("4/021")
        assert data.snow_depth == 21
        
        # Snow increasing rapidly
        data = self.decoder.decode("SNINCR 2/10")
        assert "2 inches" in data.snow_increasing_rapidly
        
        # Water equivalent
        data = self.decoder.decode("933036")
        assert data.water_equivalent_snow == 3.6
    
    def test_pressure_data(self):
        """Test pressure data extraction."""
        # SLP: 1020.1 hPa
        data = self.decoder.decode("SLP201")
        assert data.sea_level_pressure == 1020.1
        
        # SLP: 999.8 hPa
        data = self.decoder.decode("SLP998")
        assert data.sea_level_pressure == 999.8
        
        # Pressure tendency: rising, +3.2 hPa
        data = self.decoder.decode("52032")
        assert data.pressure_change == 3.2
        assert data.pressure_tendency == "increasing"
    
    def test_temperature_data(self):
        """Test temperature data extraction."""
        # Precise temp/dew: 4.4C / -2.8C
        data = self.decoder.decode("T00441028")
        assert data.temperature_precise == 4.4
        assert data.dewpoint_precise == -2.8
        
        # Max temp 6hr: 14.2C
        data = self.decoder.decode("10142")
        assert data.max_temp_6hr == 14.2
        
        # Min temp 6hr: -1.2C
        data = self.decoder.decode("21012")
        assert data.min_temp_6hr == -1.2
        
        # 24hr max/min: 5.6C / -1.5C
        data = self.decoder.decode("400561015")
        assert data.max_temp_24hr == 5.6
        assert data.min_temp_24hr == -1.5
    
    def test_sensor_status(self):
        """Test sensor status extraction."""
        data = self.decoder.decode("RVRNO PWINO")
        assert "RVRNO" in data.sensor_status
        assert "PWINO" in data.sensor_status
    
    def test_maintenance(self):
        """Test maintenance indicator."""
        data = self.decoder.decode("$")
        assert data.maintenance_needed is True
    
    def test_plain_language(self):
        """Test plain language extraction."""
        # Should extract "BIRD HAZARD"
        data = self.decoder.decode("AO2 BIRD HAZARD SLP123")
        assert "BIRD HAZARD" in data.plain_language
    
    def test_complex_remarks(self):
        """Test a complex real-world remarks string."""
        # KJFK remarks
        remarks = "AO2 PK WND 28045/15 SLP201 T00441028 10142 21012 52032 $"
        data = self.decoder.decode(remarks)
        
        assert data.automated_station_type == "AO2"
        assert data.peak_wind_speed == 45
        assert data.sea_level_pressure == 1020.1
        assert data.temperature_precise == 4.4
        assert data.max_temp_6hr == 14.2
        assert data.min_temp_6hr == -1.2
        assert data.pressure_change == 3.2
        assert data.maintenance_needed is True
