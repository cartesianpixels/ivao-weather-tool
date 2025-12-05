"""
Weather Calculator for IVAO Weather Tool.
Calculates derived weather values and flight planning parameters.
"""

import math
from typing import Optional, Tuple
from ..data.models import (
    MetarData, VisibilityData, CloudLayer,
    TemperatureData, PressureData, WindData
)


class WeatherCalculator:
    """Calculates derived weather values and flight planning parameters."""
    
    @staticmethod
    def calculate_flight_category(
        visibility: Optional[VisibilityData],
        clouds: list[CloudLayer]
    ) -> str:
        """
        Calculate flight category based on visibility and ceiling.
        
        Categories (FAA):
        - VFR: Visibility >= 5 SM and Ceiling >= 3000 ft
        - MVFR: Visibility 3-5 SM or Ceiling 1000-3000 ft
        - IFR: Visibility 1-3 SM or Ceiling 500-1000 ft
        - LIFR: Visibility < 1 SM or Ceiling < 500 ft
        
        Args:
            visibility: Visibility data
            clouds: List of cloud layers
            
        Returns:
            Flight category string: VFR, MVFR, IFR, or LIFR
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
    
    @staticmethod
    def calculate_density_altitude(
        pressure_alt: int,
        temperature_c: int
    ) -> int:
        """
        Calculate density altitude.
        
        Formula: DA = PA + [120 × (OAT - ISA_temp)]
        where ISA_temp = 15 - (2 × PA / 1000)
        
        Args:
            pressure_alt: Pressure altitude in feet
            temperature_c: Outside air temperature in Celsius
            
        Returns:
            Density altitude in feet
        """
        # Calculate ISA temperature at this altitude
        isa_temp = 15 - (2 * pressure_alt / 1000)
        
        # Calculate density altitude
        temp_deviation = temperature_c - isa_temp
        density_alt = pressure_alt + (120 * temp_deviation)
        
        return int(density_alt)
    
    @staticmethod
    def calculate_pressure_altitude(
        field_elevation: int,
        altimeter_setting: float,
        unit: str = 'inHg'
    ) -> int:
        """
        Calculate pressure altitude.
        
        Args:
            field_elevation: Field elevation in feet MSL
            altimeter_setting: Altimeter setting
            unit: Unit of altimeter setting ('inHg' or 'hPa')
            
        Returns:
            Pressure altitude in feet
        """
        # Convert to inHg if needed
        if unit == 'hPa':
            altimeter_inhg = altimeter_setting * 0.02953
        else:
            altimeter_inhg = altimeter_setting
        
        # Standard pressure is 29.92 inHg
        # 1 inHg ≈ 1000 feet
        pressure_alt = field_elevation + ((29.92 - altimeter_inhg) * 1000)
        
        return int(pressure_alt)
    
    @staticmethod
    def calculate_crosswind_component(
        wind_direction: int,
        wind_speed: int,
        runway_heading: int
    ) -> Tuple[int, int]:
        """
        Calculate headwind and crosswind components.
        
        Args:
            wind_direction: Wind direction in degrees
            wind_speed: Wind speed in knots
            runway_heading: Runway heading in degrees
            
        Returns:
            Tuple of (headwind_component, crosswind_component) in knots
            Negative headwind = tailwind
        """
        # Calculate angle between wind and runway
        angle = abs(wind_direction - runway_heading)
        
        # Normalize to 0-180 degrees
        if angle > 180:
            angle = 360 - angle
        
        # Convert to radians
        angle_rad = math.radians(angle)
        
        # Calculate components
        headwind = int(wind_speed * math.cos(angle_rad))
        crosswind = int(abs(wind_speed * math.sin(angle_rad)))
        
        return headwind, crosswind
    
    @staticmethod
    def calculate_relative_humidity(
        temperature_c: int,
        dewpoint_c: int
    ) -> int:
        """
        Calculate relative humidity using Magnus formula.
        
        Args:
            temperature_c: Temperature in Celsius
            dewpoint_c: Dewpoint in Celsius
            
        Returns:
            Relative humidity as percentage (0-100)
        """
        # Magnus formula constants
        a = 17.27
        b = 237.7
        
        # Calculate saturation vapor pressure
        alpha_t = (a * temperature_c) / (b + temperature_c)
        alpha_d = (a * dewpoint_c) / (b + dewpoint_c)
        
        # Relative humidity
        rh = 100 * math.exp(alpha_d - alpha_t)
        
        return int(min(100, max(0, rh)))
    
    @staticmethod
    def celsius_to_fahrenheit(celsius: int) -> int:
        """Convert Celsius to Fahrenheit."""
        return int((celsius * 9/5) + 32)
    
    @staticmethod
    def fahrenheit_to_celsius(fahrenheit: int) -> int:
        """Convert Fahrenheit to Celsius."""
        return int((fahrenheit - 32) * 5/9)
    
    @staticmethod
    def knots_to_mph(knots: int) -> int:
        """Convert knots to miles per hour."""
        return int(knots * 1.15078)
    
    @staticmethod
    def mph_to_knots(mph: int) -> int:
        """Convert miles per hour to knots."""
        return int(mph / 1.15078)
    
    @staticmethod
    def inhg_to_hpa(inhg: float) -> int:
        """Convert inches of mercury to hectopascals."""
        return int(inhg * 33.8639)
    
    @staticmethod
    def hpa_to_inhg(hpa: int) -> float:
        """Convert hectopascals to inches of mercury."""
        return round(hpa * 0.02953, 2)
    
    @staticmethod
    def get_cloud_base_description(altitude: Optional[int]) -> str:
        """
        Get human-readable cloud base description.
        
        Args:
            altitude: Cloud base altitude in feet AGL
            
        Returns:
            Description string
        """
        if altitude is None:
            return "unknown altitude"
        
        if altitude < 1000:
            return f"{altitude} feet (low)"
        elif altitude < 6500:
            return f"{altitude} feet (mid-level)"
        else:
            return f"{altitude} feet (high)"
    
    @staticmethod
    def get_wind_description(wind: Optional[WindData]) -> str:
        """
        Get human-readable wind description.
        
        Args:
            wind: Wind data
            
        Returns:
            Description string
        """
        if not wind:
            return "Wind information not available"
        
        if wind.speed == 0:
            return "Calm winds"
        
        if wind.variable:
            wind_str = f"Variable at {wind.speed} knots"
        else:
            wind_str = f"From {wind.direction:03d}° at {wind.speed} knots"
        
        if wind.gust:
            wind_str += f", gusting to {wind.gust} knots"
        
        if wind.variable_from and wind.variable_to:
            wind_str += f" (variable between {wind.variable_from:03d}° and {wind.variable_to:03d}°)"
        
        return wind_str
    
    @staticmethod
    def get_visibility_description(visibility: Optional[VisibilityData]) -> str:
        """
        Get human-readable visibility description.
        
        Args:
            visibility: Visibility data
            
        Returns:
            Description string
        """
        if not visibility:
            return "Visibility not reported"
        
        prefix = "Less than " if visibility.less_than else ""
        
        if visibility.value >= 10:
            return "10 statute miles or greater (excellent)"
        elif visibility.value >= 5:
            return f"{prefix}{visibility.value} statute miles (good)"
        elif visibility.value >= 3:
            return f"{prefix}{visibility.value} statute miles (moderate)"
        elif visibility.value >= 1:
            return f"{prefix}{visibility.value} statute miles (poor)"
        else:
            return f"{prefix}{visibility.value} statute miles (very poor)"
    
    @staticmethod
    def get_flight_category_description(category: str) -> str:
        """
        Get detailed description of flight category.
        
        Args:
            category: Flight category (VFR, MVFR, IFR, LIFR)
            
        Returns:
            Description string
        """
        descriptions = {
            'VFR': 'Visual Flight Rules - Good conditions for visual flight',
            'MVFR': 'Marginal VFR - Reduced visibility or ceiling, VFR flight possible but challenging',
            'IFR': 'Instrument Flight Rules - IFR conditions, visual flight not recommended',
            'LIFR': 'Low IFR - Very poor conditions, IFR flight challenging'
        }
        return descriptions.get(category, 'Unknown category')
    
    @staticmethod
    def get_temperature_description(temp: Optional[TemperatureData]) -> str:
        """
        Get human-readable temperature description.
        
        Args:
            temp: Temperature data
            
        Returns:
            Description string
        """
        if not temp:
            return "Temperature not reported"
        
        temp_f = WeatherCalculator.celsius_to_fahrenheit(temp.temperature)
        dew_f = WeatherCalculator.celsius_to_fahrenheit(temp.dewpoint)
        
        spread = temp.temperature - temp.dewpoint
        rh = WeatherCalculator.calculate_relative_humidity(temp.temperature, temp.dewpoint)
        
        desc = f"{temp.temperature}°C ({temp_f}°F), dewpoint {temp.dewpoint}°C ({dew_f}°F)"
        desc += f"\nTemperature-dewpoint spread: {spread}°C, relative humidity: {rh}%"
        
        if spread <= 2:
            desc += " (fog or low clouds likely)"
        elif spread <= 5:
            desc += " (high humidity)"
        
        return desc
