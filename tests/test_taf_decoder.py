"""
Tests for TAF decoder.
"""

import pytest
from datetime import datetime, timezone
from src.domain.taf_decoder import TafDecoder


class TestTafDecoder:
    """Test cases for TAF decoding."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.decoder = TafDecoder()
    
    def test_basic_taf(self):
        """Test basic TAF decoding."""
        taf_str = "TAF KJFK 041730Z 0418/0524 31012KT P6SM FEW250"
        taf = self.decoder.decode(taf_str)
        
        assert taf.station == "KJFK"
        assert taf.amended is False
        assert len(taf.periods) == 1
        assert taf.periods[0].wind.direction == 310
        assert taf.periods[0].wind.speed == 12
    
    def test_amended_taf(self):
        """Test amended TAF."""
        taf_str = "TAF AMD KLAX 041730Z 0418/0524 24015KT P6SM SCT015 BKN250"
        taf = self.decoder.decode(taf_str)
        
        assert taf.station == "KLAX"
        assert taf.amended is True
    
    def test_taf_with_fm_group(self):
        """Test TAF with FM (FROM) change group."""
        taf_str = "TAF KORD 041730Z 0418/0524 27010KT P6SM FEW250 FM050200 31015KT P6SM SCT050"
        taf = self.decoder.decode(taf_str)
        
        assert len(taf.periods) == 2
        # Base forecast
        assert taf.periods[0].change_indicator is None
        assert taf.periods[0].wind.direction == 270
        # FM group
        assert taf.periods[1].change_indicator == "FM"
        assert taf.periods[1].wind.direction == 310
        assert taf.periods[1].wind.speed == 15
    
    def test_taf_with_tempo(self):
        """Test TAF with TEMPO group."""
        taf_str = "TAF KSEA 041730Z 0418/0524 16010KT P6SM FEW015 TEMPO 0420/0424 5SM -RA BKN015"
        taf = self.decoder.decode(taf_str)
        
        assert len(taf.periods) == 2
        # TEMPO group
        tempo_period = taf.periods[1]
        assert tempo_period.change_indicator == "TEMPO"
        assert tempo_period.visibility.value == 5.0
        assert len(tempo_period.weather) > 0
    
    def test_taf_with_becmg(self):
        """Test TAF with BECMG group."""
        taf_str = "TAF KBOS 041730Z 0418/0524 09015KT P6SM SCT250 BECMG 0500/0502 BKN015"
        taf = self.decoder.decode(taf_str)
        
        assert len(taf.periods) == 2
        # BECMG group
        becmg_period = taf.periods[1]
        assert becmg_period.change_indicator == "BECMG"
        assert len(becmg_period.clouds) > 0
    
    def test_taf_with_prob(self):
        """Test TAF with PROB group."""
        taf_str = "TAF KATL 041730Z 0418/0524 27015KT P6SM SCT040 PROB30 0420/0424 2SM TSRA BKN020CB"
        taf = self.decoder.decode(taf_str)
        
        assert len(taf.periods) == 2
        # PROB group
        prob_period = taf.periods[1]
        assert prob_period.change_indicator.startswith("PROB")
        assert prob_period.probability == 30
        assert len(prob_period.weather) > 0
    
    def test_taf_with_prob_tempo(self):
        """Test TAF with PROB TEMPO group."""
        taf_str = "TAF KDFW 041730Z 0418/0524 18012KT P6SM FEW250 PROB40 TEMPO 0502/0506 3SM -TSRA BKN025CB"
        taf = self.decoder.decode(taf_str)
        
        assert len(taf.periods) == 2
        prob_tempo = taf.periods[1]
        assert "PROB" in prob_tempo.change_indicator
        assert prob_tempo.probability == 40
    
    def test_complex_taf(self):
        """Test complex TAF with multiple change groups."""
        taf_str = """TAF KJFK 041730Z 0418/0524 31012KT P6SM FEW250 
                     FM050000 28015G25KT P6SM SCT050 
                     TEMPO 0506/0510 5SM -RA BKN030 
                     FM051200 32010KT P6SM BKN015"""
        taf = self.decoder.decode(taf_str)
        
        assert len(taf.periods) == 4
        assert taf.periods[0].change_indicator is None  # Base
        assert taf.periods[1].change_indicator == "FM"
        assert taf.periods[2].change_indicator == "TEMPO"
        assert taf.periods[3].change_indicator == "FM"
    
    def test_taf_with_weather_phenomena(self):
        """Test TAF with various weather phenomena."""
        taf_str = "TAF KSEA 041730Z 0418/0524 16010KT 3SM -RA BR BKN015"
        taf = self.decoder.decode(taf_str)
        
        base_period = taf.periods[0]
        assert len(base_period.weather) == 2
        # Light rain
        assert any(w.intensity == '-' and 'RA' in w.precipitation for w in base_period.weather)
        # Mist
        assert any('BR' in w.obscuration for w in base_period.weather)
    
    def test_taf_with_multiple_cloud_layers(self):
        """Test TAF with multiple cloud layers."""
        taf_str = "TAF KDEN 041730Z 0418/0524 36012KT P6SM FEW060 SCT120 BKN200"
        taf = self.decoder.decode(taf_str)
        
        base_period = taf.periods[0]
        assert len(base_period.clouds) == 3
        assert base_period.clouds[0].coverage == "FEW"
        assert base_period.clouds[1].coverage == "SCT"
        assert base_period.clouds[2].coverage == "BKN"
    
    def test_taf_with_gusts(self):
        """Test TAF with wind gusts."""
        taf_str = "TAF KLAX 041730Z 0418/0524 24015G25KT P6SM FEW015"
        taf = self.decoder.decode(taf_str)
        
        base_period = taf.periods[0]
        assert base_period.wind.gust == 25
    
    def test_taf_with_variable_wind(self):
        """Test TAF with variable wind."""
        taf_str = "TAF KORD 041730Z 0418/0524 VRB05KT P6SM SCT250"
        taf = self.decoder.decode(taf_str)
        
        base_period = taf.periods[0]
        assert base_period.wind.variable is True
        assert base_period.wind.speed == 5
    
    def test_taf_valid_period_parsing(self):
        """Test TAF valid period parsing."""
        taf_str = "TAF KJFK 041730Z 0418/0524 31012KT P6SM FEW250"
        taf = self.decoder.decode(taf_str)
        
        # Valid from day 04, hour 18
        assert taf.valid_from.day == 4
        assert taf.valid_from.hour == 18
        # Valid to day 05, hour 24 (00 next day)
        # Since hour 24 becomes hour 0 of next day, day becomes 6
        assert taf.valid_to.day == 6
        assert taf.valid_to.hour == 0
    
    def test_taf_issue_time_parsing(self):
        """Test TAF issue time parsing."""
        taf_str = "TAF KJFK 041730Z 0418/0524 31012KT P6SM FEW250"
        taf = self.decoder.decode(taf_str)
        
        assert taf.issue_time.day == 4
        assert taf.issue_time.hour == 17
        assert taf.issue_time.minute == 30
    
    def test_taf_with_cb_clouds(self):
        """Test TAF with cumulonimbus clouds."""
        taf_str = "TAF KATL 041730Z 0418/0524 27015KT 3SM TSRA BKN020CB"
        taf = self.decoder.decode(taf_str)
        
        base_period = taf.periods[0]
        assert any(c.type == "CB" for c in base_period.clouds)
    
    def test_taf_with_tcu_clouds(self):
        """Test TAF with towering cumulus clouds."""
        taf_str = "TAF KMIA 041730Z 0418/0524 09015KT P6SM SCT025TCU"
        taf = self.decoder.decode(taf_str)
        
        base_period = taf.periods[0]
        assert any(c.type == "TCU" for c in base_period.clouds)
    
    def test_invalid_taf(self):
        """Test invalid TAF raises error."""
        with pytest.raises(ValueError):
            self.decoder.decode("INVALID TAF STRING")
    
    def test_real_world_taf_1(self):
        """Test real-world TAF from KJFK."""
        taf_str = """TAF KJFK 041730Z 0418/0524 31012KT P6SM FEW250 
                     FM050000 28015G25KT P6SM SCT050 
                     FM051200 32010KT P6SM BKN015"""
        taf = self.decoder.decode(taf_str)
        
        assert taf.station == "KJFK"
        assert len(taf.periods) >= 1
        assert taf.raw_text is not None
    
    def test_real_world_taf_2(self):
        """Test real-world TAF from KSEA."""
        taf_str = "TAF KSEA 041730Z 0418/0524 16010KT P6SM FEW015 TEMPO 0420/0502 5SM -RA BKN020"
        taf = self.decoder.decode(taf_str)
        
        assert taf.station == "KSEA"
        assert len(taf.periods) >= 1
