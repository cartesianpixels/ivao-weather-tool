"""
Weather Display Widget for IVAO Weather Tool.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QScrollArea, QFrame, QGridLayout, QGroupBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from src.domain.weather_interpreter import WeatherInterpreter

class WeatherDisplay(QWidget):
    """
    Widget to display decoded METAR and TAF data.
    """
    
    def __init__(self, parent=None):
        """Initialize weather display."""
        super().__init__(parent)
        
        self.interpreter = WeatherInterpreter()
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area for content
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        # Container widget
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.container_layout.setSpacing(20)
        
        self.scroll.setWidget(self.container)
        self.layout.addWidget(self.scroll)
        
        # Initial state
        self.show_welcome_message()
        
    def show_welcome_message(self):
        """Show welcome message when no data is loaded."""
        self._clear_layout()
        
        label = QLabel("Enter an airport code to view weather")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = label.font()
        font.setPointSize(14)
        label.setFont(font)
        label.setStyleSheet("color: #888;")
        
        self.container_layout.addWidget(label)
        
    def update_weather(self, metar_data, taf_data=None):
        """Update display with new weather data."""
        self._clear_layout()
        
        if metar_data:
            self._add_metar_section(metar_data)
            
        if taf_data:
            self._add_taf_section(taf_data)
            
        self.container_layout.addStretch()
        
    def _add_metar_section(self, metar):
        """Add METAR data section."""
        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        station_label = QLabel(metar.station)
        station_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(station_label)
        
        if metar.flight_category:
            cat_label = QLabel(metar.flight_category)
            cat_label.setStyleSheet(f"""
                background-color: {self._get_category_color(metar.flight_category)};
                color: white;
                padding: 4px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            """)
            header_layout.addWidget(cat_label)
            
        header_layout.addStretch()
        
        time_label = QLabel(metar.observation_time.strftime("%d %H:%M UTC"))
        time_label.setStyleSheet("font-size: 12px; color: #666;")
        header_layout.addWidget(time_label)
        
        self.container_layout.addWidget(header)
        
        # Raw Text
        raw_label = QLabel(metar.raw_text)
        raw_label.setWordWrap(True)
        raw_label.setStyleSheet("""
            font-family: 'Courier New', monospace; 
            background: #f5f5f5; 
            padding: 12px; 
            border-radius: 6px;
            border-left: 4px solid #2196F3;
            font-size: 11px;
        """)
        self.container_layout.addWidget(raw_label)
        
        # Interpretation
        interpretation = self.interpreter.interpret_metar(metar)
        if interpretation:
            interp_label = QLabel(interpretation)
            interp_label.setTextFormat(Qt.TextFormat.RichText)  # Enable HTML rendering
            interp_label.setWordWrap(True)
            interp_label.setStyleSheet("""
                background: #E3F2FD;
                padding: 12px;
                border-radius: 6px;
                color: #1565C0;
                font-size: 12px;
                line-height: 1.5;
            """)
            self.container_layout.addWidget(interp_label)
        
        # Details Grid
        details_group = QGroupBox("Weather Details")
        details_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        grid = QGridLayout()
        grid.setSpacing(15)
        grid.setColumnStretch(1, 1)
        
        row = 0
        
        # Wind
        if metar.wind:
            wind_label = self._create_label("Wind:", bold=True)
            grid.addWidget(wind_label, row, 0, Qt.AlignmentFlag.AlignTop)
            
            if metar.wind.direction == 0 and metar.wind.speed == 0:
                wind_text = "Calm"
            elif metar.wind.variable:
                wind_text = f"Variable at {metar.wind.speed} kt"
            else:
                wind_text = f"{metar.wind.direction:03d}° at {metar.wind.speed} kt"
                if metar.wind.gust:
                    wind_text += f" gusting to {metar.wind.gust} kt"
                if metar.wind.variable_from and metar.wind.variable_to:
                    wind_text += f"\nVariable between {metar.wind.variable_from:03d}° and {metar.wind.variable_to:03d}°"
            
            grid.addWidget(QLabel(wind_text), row, 1)
            row += 1
            
        # Visibility
        if metar.visibility:
            grid.addWidget(self._create_label("Visibility:", bold=True), row, 0)
            vis_text = f"{metar.visibility.value} {metar.visibility.unit}"
            if metar.visibility.value >= 10 and metar.visibility.unit == "SM":
                vis_text += " (Unlimited)"
            grid.addWidget(QLabel(vis_text), row, 1)
            row += 1
            
        # Weather Phenomena
        if metar.weather:
            grid.addWidget(self._create_label("Weather:", bold=True), row, 0, Qt.AlignmentFlag.AlignTop)
            weather_widget = QWidget()
            weather_layout = QVBoxLayout(weather_widget)
            weather_layout.setContentsMargins(0, 0, 0, 0)
            weather_layout.setSpacing(5)
            
            for wx in metar.weather:
                wx_text = wx.raw
                # Get interpretation
                wx_interp = self.interpreter.interpret_weather_phenomena([wx])
                if wx_interp:
                    wx_text += f" — {wx_interp}"
                wx_label = QLabel(wx_text)
                wx_label.setWordWrap(True)
                weather_layout.addWidget(wx_label)
            
            grid.addWidget(weather_widget, row, 1)
            row += 1
            
        # Clouds
        if metar.clouds:
            grid.addWidget(self._create_label("Clouds:", bold=True), row, 0, Qt.AlignmentFlag.AlignTop)
            cloud_widget = QWidget()
            cloud_layout = QVBoxLayout(cloud_widget)
            cloud_layout.setContentsMargins(0, 0, 0, 0)
            cloud_layout.setSpacing(5)
            
            cloud_interp = self.interpreter.interpret_clouds(metar.clouds)
            if cloud_interp:
                cloud_layout.addWidget(QLabel(cloud_interp))
            else:
                for cloud in metar.clouds:
                    text = cloud.coverage
                    if cloud.altitude:
                        text += f" at {cloud.altitude} ft"
                    if cloud.type:
                        text += f" ({cloud.type})"
                    cloud_layout.addWidget(QLabel(text))
            
            grid.addWidget(cloud_widget, row, 1)
            row += 1
            
        # Temp/Dew
        if metar.temperature:
            grid.addWidget(self._create_label("Temperature:", bold=True), row, 0)
            temp_text = f"{metar.temperature.temperature}°C / {metar.temperature.dewpoint}°C"
            temp_text += f"\n({self._celsius_to_fahrenheit(metar.temperature.temperature)}°F / "
            temp_text += f"{self._celsius_to_fahrenheit(metar.temperature.dewpoint)}°F)"
            grid.addWidget(QLabel(temp_text), row, 1)
            row += 1
            
        # Pressure
        if metar.pressure:
            grid.addWidget(self._create_label("Pressure:", bold=True), row, 0)
            pressure_text = f"{metar.pressure.value} {metar.pressure.unit}"
            if metar.pressure.unit == "inHg":
                # Convert to hPa
                hpa = metar.pressure.value * 33.8639
                pressure_text += f" ({hpa:.1f} hPa)"
            grid.addWidget(QLabel(pressure_text), row, 1)
            row += 1
            
        details_group.setLayout(grid)
        self.container_layout.addWidget(details_group)
        
        # Remarks
        if metar.remarks:
            self._add_remarks_section(metar.remarks)
            
    def _add_remarks_section(self, remarks):
        """Add decoded remarks section."""
        remarks_group = QGroupBox("Remarks")
        remarks_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        remarks_layout = QVBoxLayout()
        remarks_layout.setSpacing(8)
        
        # Station Type
        if remarks.station_type:
            remarks_layout.addWidget(QLabel(f"• Station Type: {remarks.station_type}"))
            
        # Peak Wind
        if remarks.peak_wind:
            pw = remarks.peak_wind
            text = f"• Peak Wind: {pw.speed} kt from {pw.direction}° at {pw.time}"
            remarks_layout.addWidget(QLabel(text))
            
        # Wind Shift
        if remarks.wind_shift:
            ws = remarks.wind_shift
            text = f"• Wind Shift at {ws.time}"
            if ws.frontal:
                text += " (frontal)"
            remarks_layout.addWidget(QLabel(text))
            
        # Visibility
        if remarks.tower_visibility:
            remarks_layout.addWidget(QLabel(f"• Tower Visibility: {remarks.tower_visibility}"))
        if remarks.surface_visibility:
            remarks_layout.addWidget(QLabel(f"• Surface Visibility: {remarks.surface_visibility}"))
            
        # Lightning
        if remarks.lightning:
            lt = remarks.lightning
            text = f"• Lightning: {', '.join(lt.types)}"
            if lt.distance:
                text += f" {lt.distance}"
            if lt.directions:
                text += f" {', '.join(lt.directions)}"
            remarks_layout.addWidget(QLabel(text))
            
        # Precipitation
        if remarks.precipitation_begin_end:
            for precip in remarks.precipitation_begin_end:
                text = f"• {precip.phenomenon}"
                if precip.began:
                    text += f" began {precip.began}"
                if precip.ended:
                    text += f" ended {precip.ended}"
                remarks_layout.addWidget(QLabel(text))
                
        # Sea Level Pressure
        if remarks.sea_level_pressure:
            remarks_layout.addWidget(QLabel(f"• Sea Level Pressure: {remarks.sea_level_pressure} hPa"))
            
        # Plain Language
        if remarks.plain_language:
            for remark in remarks.plain_language:
                label = QLabel(f"• {remark}")
                label.setWordWrap(True)
                remarks_layout.addWidget(label)
        
        if remarks_layout.count() > 0:
            remarks_group.setLayout(remarks_layout)
            self.container_layout.addWidget(remarks_group)
            
    def _add_taf_section(self, taf):
        """Add TAF data section."""
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #ddd; margin: 10px 0;")
        self.container_layout.addWidget(line)
        
        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Terminal Aerodrome Forecast (TAF)")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        if taf.issue_time:
            issue_label = QLabel(f"Issued: {taf.issue_time.strftime('%d %H:%M UTC')}")
            issue_label.setStyleSheet("font-size: 12px; color: #666;")
            header_layout.addWidget(issue_label)
        
        self.container_layout.addWidget(header)
        
        # Valid Period
        if taf.valid_from and taf.valid_to:
            valid_label = QLabel(
                f"Valid: {taf.valid_from.strftime('%d %H:%M')} - {taf.valid_to.strftime('%d %H:%M UTC')}"
            )
            valid_label.setStyleSheet("font-size: 12px; color: #666; margin-bottom: 10px;")
            self.container_layout.addWidget(valid_label)
        
        # Raw Text
        raw_label = QLabel(taf.raw_text)
        raw_label.setWordWrap(True)
        raw_label.setStyleSheet("""
            font-family: 'Courier New', monospace; 
            background: #f5f5f5; 
            padding: 12px; 
            border-radius: 6px;
            border-left: 4px solid #FF9800;
            font-size: 11px;
        """)
        self.container_layout.addWidget(raw_label)
        
        # Interpretation
        interpretation = self.interpreter.interpret_taf(taf)
        if interpretation:
            interp_label = QLabel(interpretation)
            interp_label.setWordWrap(True)
            interp_label.setStyleSheet("""
                background: #FFF3E0;
                padding: 12px;
                border-radius: 6px;
                color: #E65100;
                font-size: 12px;
                line-height: 1.5;
            """)
            self.container_layout.addWidget(interp_label)
        
        # Base Forecast
        if taf.forecast:
            self._add_forecast_period("Base Forecast", taf.forecast, is_base=True)
        
        # Change Groups
        if taf.change_groups:
            for group in taf.change_groups:
                self._add_forecast_period(
                    self._get_change_group_title(group),
                    group,
                    is_base=False
                )
                
    def _add_forecast_period(self, title, forecast, is_base=False):
        """Add a forecast period (base or change group)."""
        group = QGroupBox(title)
        
        if is_base:
            style = "border: 2px solid #4CAF50; background-color: #F1F8F4;"
        else:
            style = "border: 2px solid #FF9800; background-color: #FFF8F0;"
            
        group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                {style}
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # Time period
        if hasattr(forecast, 'time_from') and forecast.time_from:
            time_text = f"Period: {forecast.time_from.strftime('%d %H:%M')}"
            if hasattr(forecast, 'time_to') and forecast.time_to:
                time_text += f" - {forecast.time_to.strftime('%d %H:%M UTC')}"
            time_label = QLabel(time_text)
            time_label.setStyleSheet("color: #666; font-size: 11px; font-weight: normal;")
            layout.addWidget(time_label)
        
        # Probability
        if hasattr(forecast, 'probability') and forecast.probability:
            prob_label = QLabel(f"Probability: {forecast.probability}%")
            prob_label.setStyleSheet("color: #F44336; font-weight: bold; font-size: 11px;")
            layout.addWidget(prob_label)
        
        # Wind
        if forecast.wind:
            wind = forecast.wind
            if wind.direction == 0 and wind.speed == 0:
                wind_text = "Wind: Calm"
            else:
                wind_text = f"Wind: {wind.direction:03d}° at {wind.speed} kt"
                if wind.gust:
                    wind_text += f" G{wind.gust}"
            layout.addWidget(QLabel(wind_text))
        
        # Visibility
        if forecast.visibility:
            vis_text = f"Visibility: {forecast.visibility.value} {forecast.visibility.unit}"
            layout.addWidget(QLabel(vis_text))
        
        # Weather
        if forecast.weather:
            for wx in forecast.weather:
                wx_text = f"Weather: {wx.raw}"
                wx_interp = self.interpreter.interpret_weather_phenomena([wx])
                if wx_interp:
                    wx_text += f" — {wx_interp}"
                wx_label = QLabel(wx_text)
                wx_label.setWordWrap(True)
                layout.addWidget(wx_label)
        
        # Clouds
        if forecast.clouds:
            cloud_interp = self.interpreter.interpret_clouds(forecast.clouds)
            if cloud_interp:
                layout.addWidget(QLabel(f"Clouds: {cloud_interp}"))
            else:
                for cloud in forecast.clouds:
                    text = f"Clouds: {cloud.coverage}"
                    if cloud.altitude:
                        text += f" at {cloud.altitude} ft"
                    if cloud.type:
                        text += f" ({cloud.type})"
                    layout.addWidget(QLabel(text))
        
        group.setLayout(layout)
        self.container_layout.addWidget(group)
        
    def _get_change_group_title(self, group):
        """Get title for change group."""
        if group.change_type == "FM":
            return f"FROM {group.time_from.strftime('%d %H:%M UTC') if group.time_from else ''}"
        elif group.change_type == "TEMPO":
            return "TEMPORARY"
        elif group.change_type == "BECMG":
            return "BECOMING"
        elif group.change_type == "PROB":
            return f"PROBABILITY {group.probability}%"
        return group.change_type or "Change"
        
    def _create_label(self, text, bold=False):
        """Create a styled label."""
        label = QLabel(text)
        if bold:
            font = label.font()
            font.setBold(True)
            label.setFont(font)
        return label
        
    def _celsius_to_fahrenheit(self, celsius):
        """Convert Celsius to Fahrenheit."""
        return round(celsius * 9/5 + 32)
        
    def _get_category_color(self, category):
        """Get color for flight category."""
        colors = {
            'VFR': '#4CAF50',   # Green
            'MVFR': '#2196F3',  # Blue
            'IFR': '#FF9800',   # Orange
            'LIFR': '#F44336'   # Red
        }
        return colors.get(category, '#9E9E9E')  # Grey default
        
    def _clear_layout(self):
        """Clear all widgets from layout."""
        # Remove all widgets
        while self.container_layout.count():
            child = self.container_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_sublayout(child.layout())
                
    def _clear_sublayout(self, layout):
        """Recursively clear a sublayout."""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_sublayout(child.layout())
