"""
Weather Interpreter for IVAO Weather Tool.
Provides human-readable interpretations of weather data for training purposes.
"""

from typing import List
from ..data.models import MetarData, TafData, TafPeriod, WeatherPhenomenon
from .weather_calculator import WeatherCalculator


class WeatherInterpreter:
    """Interprets weather data into plain English for training."""
    
    # Weather phenomenon descriptions
    INTENSITY_DESC = {
        '-': 'light',
        '+': 'heavy',
        None: 'moderate'
    }
    
    DESCRIPTOR_DESC = {
        'MI': 'shallow',
        'BC': 'patches of',
        'PR': 'partial',
        'DR': 'low drifting',
        'BL': 'blowing',
        'SH': 'showers of',
        'TS': 'thunderstorm with',
        'FZ': 'freezing'
    }
    
    PRECIP_DESC = {
        'DZ': 'drizzle',
        'RA': 'rain',
        'SN': 'snow',
        'SG': 'snow grains',
        'IC': 'ice crystals',
        'PL': 'ice pellets',
        'GR': 'hail',
        'GS': 'small hail',
        'UP': 'unknown precipitation'
    }
    
    OBSCURATION_DESC = {
        'BR': 'mist',
        'FG': 'fog',
        'FU': 'smoke',
        'VA': 'volcanic ash',
        'DU': 'dust',
        'SA': 'sand',
        'HZ': 'haze',
        'PY': 'spray'
    }
    
    OTHER_DESC = {
        'PO': 'dust or sand whirls',
        'SQ': 'squalls',
        'FC': 'funnel cloud',
        'SS': 'sandstorm',
        'DS': 'duststorm'
    }
    
    CLOUD_COVERAGE_DESC = {
        'SKC': 'sky clear',
        'CLR': 'clear below 12,000 feet',
        'NSC': 'no significant clouds',
        'NCD': 'no clouds detected',
        'FEW': 'few clouds (1-2 oktas)',
        'SCT': 'scattered clouds (3-4 oktas)',
        'BKN': 'broken clouds (5-7 oktas)',
        'OVC': 'overcast (8 oktas)',
        'VV': 'vertical visibility (obscured sky)'
    }
    
    @classmethod
    def interpret_metar(cls, metar: MetarData) -> str:
        """
        Generate a plain English interpretation of a METAR.
        
        Args:
            metar: Decoded METAR data
            
        Returns:
            Human-readable interpretation
        """
        lines = []
        
        # Header
        lines.append(f"METAR for {metar.station}")
        lines.append(f"Observed at {metar.observation_time.strftime('%H:%M UTC on %B %d, %Y')}")
        
        if metar.auto:
            lines.append("(Automated observation)")
        if metar.corrected:
            lines.append("(Corrected report)")
        
        lines.append("")
        
        # Flight category
        if metar.flight_category:
            cat_desc = WeatherCalculator.get_flight_category_description(metar.flight_category)
            lines.append(f"<b>Flight Category: {metar.flight_category}</b>")
            lines.append(f"{cat_desc}")
            lines.append("")
        
        # Wind
        if metar.wind:
            lines.append(f"<b>Wind:</b> {WeatherCalculator.get_wind_description(metar.wind)}")
        
        # Visibility
        if metar.visibility:
            lines.append(f"<b>Visibility:</b> {WeatherCalculator.get_visibility_description(metar.visibility)}")
        
        # Weather phenomena
        if metar.weather:
            weather_desc = cls.interpret_weather_phenomena(metar.weather)
            lines.append(f"<b>Weather:</b> {weather_desc}")
        
        # Clouds
        if metar.clouds:
            cloud_desc = cls.interpret_clouds(metar.clouds)
            lines.append(f"<b>Clouds:</b> {cloud_desc}")
        
        # Temperature
        if metar.temperature:
            lines.append(f"<b>Temperature:</b> {WeatherCalculator.get_temperature_description(metar.temperature)}")
        
        # Pressure
        if metar.pressure:
            lines.append(f"<b>Altimeter:</b> {metar.pressure.value} {metar.pressure.unit}")
        
        # Remarks
        if metar.remarks:
            lines.append(f"<br><b>Remarks:</b> {metar.remarks}")
        
        # Raw METAR
        lines.append(f"<br><b>Raw METAR:</b> {metar.raw_text}")
        
        return "\n".join(lines)
    
    @classmethod
    def interpret_taf(cls, taf: TafData) -> str:
        """
        Generate a plain English interpretation of a TAF.
        
        Args:
            taf: Decoded TAF data
            
        Returns:
            Human-readable interpretation
        """
        lines = []
        
        # Header
        lines.append(f"TAF for {taf.station}")
        lines.append(f"Issued at {taf.issue_time.strftime('%H:%M UTC on %B %d, %Y')}")
        lines.append(f"Valid from {taf.valid_from.strftime('%H:%M UTC %b %d')} to {taf.valid_to.strftime('%H:%M UTC %b %d')}")
        
        if taf.amended:
            lines.append("(Amended forecast)")
        
        lines.append("")
        
        # Forecast periods
        for i, period in enumerate(taf.periods):
            period_desc = cls._interpret_taf_period(period, i == 0)
            lines.append(period_desc)
            lines.append("")
        
        # Raw TAF
        lines.append(f"<b>Raw TAF:</b><br>{taf.raw_text}")
        
        return "\n".join(lines)
    
    @classmethod
    def _interpret_taf_period(cls, period: TafPeriod, is_base: bool) -> str:
        """Interpret a single TAF forecast period."""
        lines = []
        
        # Period header
        if is_base:
            header = "<b>Base Forecast</b>"
        elif period.change_indicator == 'FM':
            header = f"<b>From {period.from_time.strftime('%H:%M UTC')}</b>"
        elif period.change_indicator == 'TEMPO':
            header = f"<b>Temporary conditions from {period.from_time.strftime('%H:%M')} to {period.to_time.strftime('%H:%M UTC')}</b>"
        elif period.change_indicator == 'BECMG':
            header = f"<b>Becoming from {period.from_time.strftime('%H:%M')} to {period.to_time.strftime('%H:%M UTC')}</b>"
        elif period.change_indicator and period.change_indicator.startswith('PROB'):
            prob_text = f"{period.probability}% probability" if period.probability else "Probability"
            header = f"<b>{prob_text} from {period.from_time.strftime('%H:%M')} to {period.to_time.strftime('%H:%M UTC')}</b>"
        else:
            header = f"<b>Period: {period.from_time.strftime('%H:%M')} to {period.to_time.strftime('%H:%M UTC')}</b>"
        
        lines.append(header)
        
        # Conditions
        conditions = []
        
        if period.wind:
            conditions.append(f"Wind: {WeatherCalculator.get_wind_description(period.wind)}")
        
        if period.visibility:
            conditions.append(f"Visibility: {WeatherCalculator.get_visibility_description(period.visibility)}")
        
        if period.weather:
            weather_desc = cls.interpret_weather_phenomena(period.weather)
            conditions.append(f"Weather: {weather_desc}")
        
        if period.clouds:
            cloud_desc = cls.interpret_clouds(period.clouds)
            conditions.append(f"Clouds: {cloud_desc}")
        
        if conditions:
            lines.extend(conditions)
        else:
            lines.append("No significant changes")
        
        return "\n".join(lines)
    
    @classmethod
    def interpret_weather_phenomena(cls, weather_list: List[WeatherPhenomenon]) -> str:
        """Interpret weather phenomena into plain English."""
        descriptions = []
        
        for wx in weather_list:
            parts = []
            
            # Intensity
            if wx.intensity:
                parts.append(cls.INTENSITY_DESC.get(wx.intensity, ''))
            
            # Descriptor
            if wx.descriptor:
                parts.append(cls.DESCRIPTOR_DESC.get(wx.descriptor, wx.descriptor))
            
            # Precipitation
            for code in wx.precipitation:
                parts.append(cls.PRECIP_DESC.get(code, code))
            
            # Obscuration
            for code in wx.obscuration:
                parts.append(cls.OBSCURATION_DESC.get(code, code))
            
            # Other
            for code in wx.other:
                parts.append(cls.OTHER_DESC.get(code, code))
            
            descriptions.append(' '.join(parts))
        
        return ', '.join(descriptions) if descriptions else 'None'
    
    @classmethod
    def interpret_clouds(cls, clouds: List) -> str:
        """Interpret cloud layers into plain English."""
        if not clouds:
            return "No clouds reported"
        
        descriptions = []
        
        for cloud in clouds:
            coverage_desc = cls.CLOUD_COVERAGE_DESC.get(cloud.coverage, cloud.coverage)
            
            if cloud.altitude:
                alt_desc = f"at {cloud.altitude} feet"
            else:
                alt_desc = ""
            
            cloud_type = ""
            if cloud.type == 'CB':
                cloud_type = " (cumulonimbus - thunderstorm clouds)"
            elif cloud.type == 'TCU':
                cloud_type = " (towering cumulus)"
            
            parts = [coverage_desc, alt_desc, cloud_type]
            descriptions.append(' '.join(p for p in parts if p))
        
        return '; '.join(descriptions)
    
    @classmethod
    def get_training_explanation(cls, metar: MetarData) -> str:
        """
        Generate detailed training explanation for a METAR.
        
        Args:
            metar: Decoded METAR data
            
        Returns:
            Detailed educational explanation
        """
        lines = []
        
        lines.append("=== METAR TRAINING BREAKDOWN ===")
        lines.append("")
        
        # Station
        lines.append(f"<b>Station Identifier: {metar.station}</b>")
        lines.append("The 4-letter ICAO code identifying the airport or weather station.")
        lines.append("")
        
        # Time
        lines.append(f"<b>Observation Time: {metar.observation_time.strftime('%d%H%MZ')}</b>")
        lines.append(f"Day {metar.observation_time.day} of the month, at {metar.observation_time.strftime('%H:%M')} Zulu (UTC) time.")
        lines.append("")
        
        # Wind
        if metar.wind:
            lines.append("<b>Wind Information:</b>")
            if metar.wind.variable:
                lines.append("VRB = Variable wind direction")
            else:
                lines.append(f"{metar.wind.direction:03d}° = Wind direction (magnetic)")
            lines.append(f"{metar.wind.speed}KT = Wind speed in knots")
            if metar.wind.gust:
                lines.append(f"G{metar.wind.gust}KT = Gusts to {metar.wind.gust} knots")
            lines.append("")
        
        # Flight category explanation
        if metar.flight_category:
            lines.append(f"<b>Flight Category: {metar.flight_category}</b>")
            lines.append(WeatherCalculator.get_flight_category_description(metar.flight_category))
            lines.append("")
        
        return "\n".join(lines)
