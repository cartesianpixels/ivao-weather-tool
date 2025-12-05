"""
Weather Calculator Widget for IVAO Weather Tool.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QGroupBox, QGridLayout, QPushButton, QTabWidget, QComboBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QDoubleValidator, QIntValidator

from src.domain.weather_calculator import WeatherCalculator
from src.data.models import MetarData


class WeatherCalculatorWidget(QWidget):
    """
    Widget for weather-related calculations.
    """
    
    def __init__(self, parent=None):
        """Initialize calculator widget."""
        super().__init__(parent)
        
        self.current_metar = None
        self.calculator = WeatherCalculator()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("Weather Calculator")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Tab widget for different calculators
        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_density_altitude_tab(), "Density Altitude")
        self.tabs.addTab(self._create_crosswind_tab(), "Crosswind")
        self.tabs.addTab(self._create_conversions_tab(), "Conversions")
        
        layout.addWidget(self.tabs)
        layout.addStretch()
        
    def update_from_metar(self, metar: MetarData):
        """Update calculator inputs from METAR data."""
        self.current_metar = metar
        
        # Update density altitude calculator
        if metar.temperature:
            self.da_temp_input.setText(str(metar.temperature.temperature))
        if metar.pressure:
            if metar.pressure.unit == "inHg":
                self.da_altimeter_input.setText(str(metar.pressure.value))
            else:
                # Convert hPa to inHg
                inhg = WeatherCalculator.hpa_to_inhg(int(metar.pressure.value))
                self.da_altimeter_input.setText(f"{inhg:.2f}")
        
        # Update crosswind calculator
        if metar.wind:
            self.cw_wind_dir_input.setText(str(metar.wind.direction))
            self.cw_wind_speed_input.setText(str(metar.wind.speed))
            
    def _create_density_altitude_tab(self):
        """Create density altitude calculator tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Info box
        info = QLabel(
            "Density altitude affects aircraft performance. "
            "Higher density altitude means reduced performance (longer takeoff, reduced climb rate)."
        )
        info.setWordWrap(True)
        info.setStyleSheet("""
            background: #E3F2FD;
            padding: 10px;
            border-radius: 4px;
            color: #1565C0;
            font-size: 11px;
        """)
        layout.addWidget(info)
        
        # Input group
        input_group = QGroupBox("Inputs")
        input_layout = QGridLayout()
        input_layout.setSpacing(10)
        
        # Field elevation
        input_layout.addWidget(QLabel("Field Elevation (ft MSL):"), 0, 0)
        self.da_elevation_input = QLineEdit()
        self.da_elevation_input.setValidator(QIntValidator(0, 15000))
        self.da_elevation_input.setPlaceholderText("e.g., 5000")
        self.da_elevation_input.textChanged.connect(self._calculate_density_altitude)
        input_layout.addWidget(self.da_elevation_input, 0, 1)
        
        # Altimeter setting
        input_layout.addWidget(QLabel("Altimeter (inHg):"), 1, 0)
        self.da_altimeter_input = QLineEdit()
        self.da_altimeter_input.setValidator(QDoubleValidator(28.0, 31.0, 2))
        self.da_altimeter_input.setPlaceholderText("e.g., 29.92")
        self.da_altimeter_input.textChanged.connect(self._calculate_density_altitude)
        input_layout.addWidget(self.da_altimeter_input, 1, 1)
        
        # Temperature
        input_layout.addWidget(QLabel("Temperature (°C):"), 2, 0)
        self.da_temp_input = QLineEdit()
        self.da_temp_input.setValidator(QIntValidator(-50, 50))
        self.da_temp_input.setPlaceholderText("e.g., 25")
        self.da_temp_input.textChanged.connect(self._calculate_density_altitude)
        input_layout.addWidget(self.da_temp_input, 2, 1)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Results group
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout()
        
        self.da_pressure_alt_label = QLabel("Pressure Altitude: —")
        self.da_pressure_alt_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        results_layout.addWidget(self.da_pressure_alt_label)
        
        self.da_density_alt_label = QLabel("Density Altitude: —")
        self.da_density_alt_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #F44336;")
        results_layout.addWidget(self.da_density_alt_label)
        
        self.da_interpretation_label = QLabel("")
        self.da_interpretation_label.setWordWrap(True)
        self.da_interpretation_label.setStyleSheet("margin-top: 10px; color: #666;")
        results_layout.addWidget(self.da_interpretation_label)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        layout.addStretch()
        return widget
        
    def _create_crosswind_tab(self):
        """Create crosswind component calculator tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Info box
        info = QLabel(
            "Calculate headwind and crosswind components for runway operations. "
            "Crosswind limits vary by aircraft type."
        )
        info.setWordWrap(True)
        info.setStyleSheet("""
            background: #E3F2FD;
            padding: 10px;
            border-radius: 4px;
            color: #1565C0;
            font-size: 11px;
        """)
        layout.addWidget(info)
        
        # Input group
        input_group = QGroupBox("Inputs")
        input_layout = QGridLayout()
        input_layout.setSpacing(10)
        
        # Wind direction
        input_layout.addWidget(QLabel("Wind Direction (°):"), 0, 0)
        self.cw_wind_dir_input = QLineEdit()
        self.cw_wind_dir_input.setValidator(QIntValidator(0, 360))
        self.cw_wind_dir_input.setPlaceholderText("e.g., 270")
        self.cw_wind_dir_input.textChanged.connect(self._calculate_crosswind)
        input_layout.addWidget(self.cw_wind_dir_input, 0, 1)
        
        # Wind speed
        input_layout.addWidget(QLabel("Wind Speed (kt):"), 1, 0)
        self.cw_wind_speed_input = QLineEdit()
        self.cw_wind_speed_input.setValidator(QIntValidator(0, 100))
        self.cw_wind_speed_input.setPlaceholderText("e.g., 15")
        self.cw_wind_speed_input.textChanged.connect(self._calculate_crosswind)
        input_layout.addWidget(self.cw_wind_speed_input, 1, 1)
        
        # Runway heading
        input_layout.addWidget(QLabel("Runway Heading (°):"), 2, 0)
        self.cw_runway_input = QLineEdit()
        self.cw_runway_input.setValidator(QIntValidator(0, 360))
        self.cw_runway_input.setPlaceholderText("e.g., 240")
        self.cw_runway_input.textChanged.connect(self._calculate_crosswind)
        input_layout.addWidget(self.cw_runway_input, 2, 1)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Results group
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout()
        
        self.cw_headwind_label = QLabel("Headwind Component: —")
        self.cw_headwind_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        results_layout.addWidget(self.cw_headwind_label)
        
        self.cw_crosswind_label = QLabel("Crosswind Component: —")
        self.cw_crosswind_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #FF9800;")
        results_layout.addWidget(self.cw_crosswind_label)
        
        self.cw_interpretation_label = QLabel("")
        self.cw_interpretation_label.setWordWrap(True)
        self.cw_interpretation_label.setStyleSheet("margin-top: 10px; color: #666;")
        results_layout.addWidget(self.cw_interpretation_label)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        layout.addStretch()
        return widget
        
    def _create_conversions_tab(self):
        """Create unit conversions tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        # Temperature conversion
        temp_group = QGroupBox("Temperature")
        temp_layout = QGridLayout()
        temp_layout.setSpacing(10)
        
        temp_layout.addWidget(QLabel("Celsius:"), 0, 0)
        self.temp_c_input = QLineEdit()
        self.temp_c_input.setValidator(QIntValidator(-100, 100))
        self.temp_c_input.textChanged.connect(self._convert_temperature)
        temp_layout.addWidget(self.temp_c_input, 0, 1)
        
        temp_layout.addWidget(QLabel("Fahrenheit:"), 1, 0)
        self.temp_f_input = QLineEdit()
        self.temp_f_input.setValidator(QIntValidator(-150, 200))
        self.temp_f_input.textChanged.connect(self._convert_temperature_reverse)
        temp_layout.addWidget(self.temp_f_input, 1, 1)
        
        temp_group.setLayout(temp_layout)
        layout.addWidget(temp_group)
        
        # Pressure conversion
        pressure_group = QGroupBox("Pressure")
        pressure_layout = QGridLayout()
        pressure_layout.setSpacing(10)
        
        pressure_layout.addWidget(QLabel("inHg:"), 0, 0)
        self.pressure_inhg_input = QLineEdit()
        self.pressure_inhg_input.setValidator(QDoubleValidator(28.0, 31.0, 2))
        self.pressure_inhg_input.textChanged.connect(self._convert_pressure)
        pressure_layout.addWidget(self.pressure_inhg_input, 0, 1)
        
        pressure_layout.addWidget(QLabel("hPa:"), 1, 0)
        self.pressure_hpa_input = QLineEdit()
        self.pressure_hpa_input.setValidator(QIntValidator(900, 1100))
        self.pressure_hpa_input.textChanged.connect(self._convert_pressure_reverse)
        pressure_layout.addWidget(self.pressure_hpa_input, 1, 1)
        
        pressure_group.setLayout(pressure_layout)
        layout.addWidget(pressure_group)
        
        # Speed conversion
        speed_group = QGroupBox("Wind Speed")
        speed_layout = QGridLayout()
        speed_layout.setSpacing(10)
        
        speed_layout.addWidget(QLabel("Knots:"), 0, 0)
        self.speed_kt_input = QLineEdit()
        self.speed_kt_input.setValidator(QIntValidator(0, 200))
        self.speed_kt_input.textChanged.connect(self._convert_speed)
        speed_layout.addWidget(self.speed_kt_input, 0, 1)
        
        speed_layout.addWidget(QLabel("MPH:"), 1, 0)
        self.speed_mph_input = QLineEdit()
        self.speed_mph_input.setValidator(QIntValidator(0, 250))
        self.speed_mph_input.textChanged.connect(self._convert_speed_reverse)
        speed_layout.addWidget(self.speed_mph_input, 1, 1)
        
        speed_group.setLayout(speed_layout)
        layout.addWidget(speed_group)
        
        layout.addStretch()
        return widget
        
    def _calculate_density_altitude(self):
        """Calculate and display density altitude."""
        try:
            elevation = int(self.da_elevation_input.text()) if self.da_elevation_input.text() else None
            altimeter = float(self.da_altimeter_input.text()) if self.da_altimeter_input.text() else None
            temp = int(self.da_temp_input.text()) if self.da_temp_input.text() else None
            
            if elevation is not None and altimeter is not None:
                # Calculate pressure altitude
                pressure_alt = WeatherCalculator.calculate_pressure_altitude(
                    elevation, altimeter, 'inHg'
                )
                self.da_pressure_alt_label.setText(f"Pressure Altitude: {pressure_alt:,} ft")
                
                if temp is not None:
                    # Calculate density altitude
                    density_alt = WeatherCalculator.calculate_density_altitude(
                        pressure_alt, temp
                    )
                    self.da_density_alt_label.setText(f"Density Altitude: {density_alt:,} ft")
                    
                    # Interpretation
                    diff = density_alt - elevation
                    if diff > 2000:
                        interp = f"⚠️ Density altitude is {diff:,} ft higher than field elevation. Expect significantly reduced aircraft performance."
                    elif diff > 1000:
                        interp = f"⚠️ Density altitude is {diff:,} ft higher than field elevation. Expect reduced aircraft performance."
                    elif diff > 0:
                        interp = f"Density altitude is {diff:,} ft higher than field elevation. Slight performance reduction."
                    else:
                        interp = "Density altitude is at or below field elevation. Good performance conditions."
                    
                    self.da_interpretation_label.setText(interp)
                else:
                    self.da_density_alt_label.setText("Density Altitude: —")
                    self.da_interpretation_label.setText("")
            else:
                self.da_pressure_alt_label.setText("Pressure Altitude: —")
                self.da_density_alt_label.setText("Density Altitude: —")
                self.da_interpretation_label.setText("")
                
        except (ValueError, ZeroDivisionError):
            pass
            
    def _calculate_crosswind(self):
        """Calculate and display crosswind components."""
        try:
            wind_dir = int(self.cw_wind_dir_input.text()) if self.cw_wind_dir_input.text() else None
            wind_speed = int(self.cw_wind_speed_input.text()) if self.cw_wind_speed_input.text() else None
            runway = int(self.cw_runway_input.text()) if self.cw_runway_input.text() else None
            
            if wind_dir is not None and wind_speed is not None and runway is not None:
                headwind, crosswind = WeatherCalculator.calculate_crosswind_component(
                    wind_dir, wind_speed, runway
                )
                
                # Display headwind (negative = tailwind)
                if headwind >= 0:
                    self.cw_headwind_label.setText(f"Headwind Component: {headwind:.1f} kt")
                else:
                    self.cw_headwind_label.setText(f"Tailwind Component: {abs(headwind):.1f} kt")
                    self.cw_headwind_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #F44336;")
                
                # Display crosswind
                self.cw_crosswind_label.setText(f"Crosswind Component: {abs(crosswind):.1f} kt")
                
                # Interpretation
                if abs(crosswind) > 15:
                    interp = f"⚠️ Strong crosswind! Exceeds typical light aircraft limits."
                elif abs(crosswind) > 10:
                    interp = f"⚠️ Moderate crosswind. Use caution, especially in light aircraft."
                elif abs(crosswind) > 5:
                    interp = "Light crosswind. Manageable for most aircraft."
                else:
                    interp = "Minimal crosswind. Favorable conditions."
                    
                if headwind < -5:
                    interp += f" ⚠️ Tailwind of {abs(headwind):.1f} kt - consider opposite runway if available."
                    
                self.cw_interpretation_label.setText(interp)
            else:
                self.cw_headwind_label.setText("Headwind Component: —")
                self.cw_crosswind_label.setText("Crosswind Component: —")
                self.cw_interpretation_label.setText("")
                
        except (ValueError, ZeroDivisionError):
            pass
            
    def _convert_temperature(self):
        """Convert Celsius to Fahrenheit."""
        try:
            if self.temp_c_input.text():
                celsius = int(self.temp_c_input.text())
                fahrenheit = WeatherCalculator.celsius_to_fahrenheit(celsius)
                self.temp_f_input.blockSignals(True)
                self.temp_f_input.setText(str(fahrenheit))
                self.temp_f_input.blockSignals(False)
        except ValueError:
            pass
            
    def _convert_temperature_reverse(self):
        """Convert Fahrenheit to Celsius."""
        try:
            if self.temp_f_input.text():
                fahrenheit = int(self.temp_f_input.text())
                celsius = WeatherCalculator.fahrenheit_to_celsius(fahrenheit)
                self.temp_c_input.blockSignals(True)
                self.temp_c_input.setText(str(celsius))
                self.temp_c_input.blockSignals(False)
        except ValueError:
            pass
            
    def _convert_pressure(self):
        """Convert inHg to hPa."""
        try:
            if self.pressure_inhg_input.text():
                inhg = float(self.pressure_inhg_input.text())
                hpa = WeatherCalculator.inhg_to_hpa(inhg)
                self.pressure_hpa_input.blockSignals(True)
                self.pressure_hpa_input.setText(str(int(hpa)))
                self.pressure_hpa_input.blockSignals(False)
        except ValueError:
            pass
            
    def _convert_pressure_reverse(self):
        """Convert hPa to inHg."""
        try:
            if self.pressure_hpa_input.text():
                hpa = int(self.pressure_hpa_input.text())
                inhg = WeatherCalculator.hpa_to_inhg(hpa)
                self.pressure_inhg_input.blockSignals(True)
                self.pressure_inhg_input.setText(f"{inhg:.2f}")
                self.pressure_inhg_input.blockSignals(False)
        except ValueError:
            pass
            
    def _convert_speed(self):
        """Convert knots to MPH."""
        try:
            if self.speed_kt_input.text():
                knots = int(self.speed_kt_input.text())
                mph = WeatherCalculator.knots_to_mph(knots)
                self.speed_mph_input.blockSignals(True)
                self.speed_mph_input.setText(str(int(mph)))
                self.speed_mph_input.blockSignals(False)
        except ValueError:
            pass
            
    def _convert_speed_reverse(self):
        """Convert MPH to knots."""
        try:
            if self.speed_mph_input.text():
                mph = int(self.speed_mph_input.text())
                knots = WeatherCalculator.mph_to_knots(mph)
                self.speed_kt_input.blockSignals(True)
                self.speed_kt_input.setText(str(int(knots)))
                self.speed_kt_input.blockSignals(False)
        except ValueError:
            pass
