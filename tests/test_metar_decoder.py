"""
Tests for METAR decoder.
"""

import pytest
from datetime import datetime, timezone
from src.domain.metar_decoder import MetarDecoder


class TestMetarDecoder:
    """Test cases for METAR decoding."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.decoder = MetarDecoder()
    
    def test_basic_metar(self):
        """Test basic METAR decoding."""
        metar_str = "KJFK 041651Z 31008KT 10SM FEW250 04/M03 A3012"
        metar = self.decoder.decode(metar_str)
        
        assert metar.station == "KJFK"
        assert metar.wind.direction == 310
        assert metar.wind.speed == 8
        assert metar.wind.gust is None
        assert metar.visibility.value == 10.0
        assert metar.temperature.temperature == 4
        assert metar.temperature.dewpoint == -3
        assert metar.pressure.value == 30.12
        assert metar.pressure.unit == "inHg"
        assert len(metar.clouds) == 1
        assert metar.clouds[0].coverage == "FEW"
        assert metar.clouds[0].altitude == 25000
    
    def test_metar_with_gusts(self):
        """Test METAR with wind gusts."""
        metar_str = "KLAX 041653Z 24015G25KT 10SM FEW015 BKN250 18/14 A2990"
        metar = self.decoder.decode(metar_str)
        
        assert metar.wind.direction == 240
        assert metar.wind.speed == 15
        assert metar.wind.gust == 25
    
    def test_variable_wind(self):
        """Test variable wind direction."""
        metar_str = "KORD 041656Z VRB05KT 10SM SCT250 03/M06 A3015"
        metar = self.decoder.decode(metar_str)
        
        assert metar.wind.variable is True
        assert metar.wind.direction is None
        assert metar.wind.speed == 5
    
    def test_variable_wind_range(self):
        """Test variable wind with direction range."""
        metar_str = "KSFO 041656Z 28008KT 240V320 10SM FEW015 SCT200 14/12 A3012 280V320"
        metar = self.decoder.decode(metar_str)
        
        assert metar.wind.direction == 280
        assert metar.wind.speed == 8
        # Variable range should be captured
        assert metar.wind.variable_from == 280 or metar.wind.variable_from == 240
        assert metar.wind.variable_to == 320
    
    def test_fractional_visibility(self):
        """Test fractional visibility."""
        metar_str = "KBOS 041654Z 09012KT 1/2SM FG OVC002 06/06 A3008"
        metar = self.decoder.decode(metar_str)
        
        assert metar.visibility.value == 0.5
        assert metar.visibility.unit == "SM"
    
    def test_mixed_visibility(self):
        """Test mixed fraction visibility (e.g., 1 1/2SM)."""
        metar_str = "KDFW 041653Z 18010KT 1 1/2SM BR BKN003 OVC010 16/15 A2990"
        metar = self.decoder.decode(metar_str)
        
        assert metar.visibility.value == 1.5
    
    def test_weather_phenomena(self):
        """Test weather phenomena parsing."""
        metar_str = "KSEA 041656Z 16008KT 3SM -RA BR BKN008 OVC015 10/09 A2985"
        metar = self.decoder.decode(metar_str)
        
        assert len(metar.weather) == 2
        # Light rain
        assert metar.weather[0].intensity == '-'
        assert 'RA' in metar.weather[0].precipitation
        # Mist
        assert 'BR' in metar.weather[1].obscuration
    
    def test_thunderstorm(self):
        """Test thunderstorm with heavy rain."""
        metar_str = "KATL 041652Z 27015G28KT 2SM +TSRA BKN008CB OVC040 22/21 A2970"
        metar = self.decoder.decode(metar_str)
        
        assert len(metar.weather) == 1
        assert metar.weather[0].intensity == '+'
        assert metar.weather[0].descriptor == 'TS'
        assert 'RA' in metar.weather[0].precipitation
        # Check for CB clouds
        assert any(c.type == 'CB' for c in metar.clouds)
    
    def test_multiple_cloud_layers(self):
        """Test multiple cloud layers."""
        metar_str = "KDEN 041653Z 36012KT 10SM FEW060 SCT120 BKN200 OVC250 08/M08 A3025"
        metar = self.decoder.decode(metar_str)
        
        assert len(metar.clouds) == 4
        assert metar.clouds[0].coverage == "FEW"
        assert metar.clouds[0].altitude == 6000
        assert metar.clouds[1].coverage == "SCT"
        assert metar.clouds[1].altitude == 12000
        assert metar.clouds[2].coverage == "BKN"
        assert metar.clouds[2].altitude == 20000
        assert metar.clouds[3].coverage == "OVC"
        assert metar.clouds[3].altitude == 25000
    
    def test_negative_temperature(self):
        """Test negative temperature parsing."""
        metar_str = "PANC 041653Z 09005KT 10SM FEW100 M15/M20 A2980"
        metar = self.decoder.decode(metar_str)
        
        assert metar.temperature.temperature == -15
        assert metar.temperature.dewpoint == -20
    
    def test_auto_station(self):
        """Test automated station flag."""
        metar_str = "KPHX 041651Z AUTO 09008KT 10SM CLR 28/01 A2995"
        metar = self.decoder.decode(metar_str)
        
        assert metar.auto is True
        assert metar.corrected is False
    
    def test_corrected_metar(self):
        """Test corrected METAR flag."""
        metar_str = "KMIA 041653Z COR 09015KT 10SM FEW025 SCT250 26/22 A3005"
        metar = self.decoder.decode(metar_str)
        
        assert metar.corrected is True
        assert metar.auto is False
    
    def test_remarks_section(self):
        """Test remarks extraction."""
        metar_str = "KJFK 041651Z 31008KT 10SM FEW250 04/M03 A3012 RMK AO2 SLP201 T00441028"
        metar = self.decoder.decode(metar_str)
        
        assert metar.remarks is not None
        assert "AO2" in metar.remarks
        assert "SLP201" in metar.remarks
    
    def test_flight_category_vfr(self):
        """Test VFR flight category."""
        metar_str = "KJFK 041651Z 31008KT 10SM FEW250 04/M03 A3012"
        metar = self.decoder.decode(metar_str)
        
        assert metar.flight_category == "VFR"
    
    def test_flight_category_mvfr(self):
        """Test MVFR flight category."""
        metar_str = "KBOS 041654Z 09012KT 4SM BR SCT015 06/05 A3008"
        metar = self.decoder.decode(metar_str)
        
        assert metar.flight_category == "MVFR"
    
    def test_flight_category_ifr(self):
        """Test IFR flight category."""
        metar_str = "KSEA 041656Z 16008KT 2SM -RA BR BKN008 10/09 A2985"
        metar = self.decoder.decode(metar_str)
        
        assert metar.flight_category == "IFR"
    
    def test_flight_category_lifr(self):
        """Test LIFR flight category."""
        metar_str = "KBOS 041654Z 09012KT 1/2SM FG OVC002 06/06 A3008"
        metar = self.decoder.decode(metar_str)
        
        assert metar.flight_category == "LIFR"
    
    def test_international_format(self):
        """Test international METAR format with QNH."""
        metar_str = "EGLL 041650Z 27015KT 9999 FEW040 12/08 Q1015"
        metar = self.decoder.decode(metar_str)
        
        assert metar.station == "EGLL"
        assert metar.pressure.value == 1015.0
        assert metar.pressure.unit == "hPa"
    
    def test_cavok(self):
        """Test CAVOK (Ceiling And Visibility OK)."""
        metar_str = "LFPG 041630Z 24008KT CAVOK 15/08 Q1018"
        metar = self.decoder.decode(metar_str)
        
        assert metar.visibility.value == 10.0
        assert metar.station == "LFPG"
    
    def test_sky_clear(self):
        """Test sky clear conditions."""
        metar_str = "KPHX 041651Z 09008KT 10SM SKC 28/01 A2995"
        metar = self.decoder.decode(metar_str)
        
        assert len(metar.clouds) == 1
        assert metar.clouds[0].coverage == "SKC"
    
    def test_vertical_visibility(self):
        """Test vertical visibility (obscured sky)."""
        metar_str = "KORD 041656Z 09005KT 1/4SM FG VV002 06/06 A3010"
        metar = self.decoder.decode(metar_str)
        
        assert any(c.coverage == "VV" for c in metar.clouds)
        assert metar.flight_category == "LIFR"
    
    def test_missing_components(self):
        """Test METAR with missing components."""
        metar_str = "KJFK 041651Z 31008KT 10SM FEW250"
        metar = self.decoder.decode(metar_str)
        
        assert metar.station == "KJFK"
        assert metar.wind is not None
        assert metar.visibility is not None
        assert metar.temperature is None
        assert metar.pressure is None
    
    def test_invalid_metar(self):
        """Test invalid METAR raises error."""
        with pytest.raises(ValueError):
            self.decoder.decode("INVALID METAR STRING")
    
    def test_real_world_example_1(self):
        """Test real-world METAR from KJFK."""
        metar_str = "KJFK 041651Z 31008KT 10SM FEW250 04/M03 A3012 RMK AO2 SLP201 T00441028"
        metar = self.decoder.decode(metar_str)
        
        assert metar.station == "KJFK"
        assert metar.flight_category == "VFR"
        assert metar.raw_text == metar_str
    
    def test_real_world_example_2(self):
        """Test real-world METAR from KSEA."""
        metar_str = "KSEA 041656Z 16008KT 10SM FEW015 BKN200 14/12 A3001 RMK AO2 SLP159 T01440122"
        metar = self.decoder.decode(metar_str)
        
        assert metar.station == "KSEA"
        assert metar.visibility.value == 10.0
        assert len(metar.clouds) == 2
