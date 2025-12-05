"""
Manual METAR/TAF Decoder Dialog for IVAO Weather Tool.
Allows users to paste raw METAR or TAF text and see decoded output.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextEdit, QPushButton, QGroupBox, QScrollArea,
    QWidget, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from src.domain.metar_decoder import MetarDecoder
from src.domain.taf_decoder import TafDecoder
from .widgets.weather_display import WeatherDisplay


class ManualDecoderDialog(QDialog):
    """Dialog for manually decoding METAR/TAF data."""
    
    def __init__(self, parent=None):
        """Initialize manual decoder dialog."""
        super().__init__(parent)
        
        self.setWindowTitle("Manual METAR/TAF Decoder")
        self.setMinimumSize(800, 700)
        
        # Initialize decoders
        self.metar_decoder = MetarDecoder()
        self.taf_decoder = TafDecoder()
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Input section
        input_group = QGroupBox("Paste METAR or TAF")
        input_layout = QVBoxLayout(input_group)
        
        # Instructions
        instructions = QLabel("Paste raw METAR or TAF text below. The decoder will automatically detect the type.")
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; font-size: 11px; margin-bottom: 5px;")
        input_layout.addWidget(instructions)
        
        # Text input
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText(
            "Example METAR:\nKJFK 041651Z 31008KT 10SM FEW250 04/M03 A3012 RMK AO2 SLP201\n\n"
            "Example TAF:\nTAF KJFK 041730Z 0418/0524 31012KT P6SM FEW250"
        )
        self.input_text.setMinimumHeight(120)
        self.input_text.setMaximumHeight(150)
        font = QFont("Courier New", 10)
        self.input_text.setFont(font)
        input_layout.addWidget(self.input_text)
        
        layout.addWidget(input_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.decode_button = QPushButton("Decode")
        self.decode_button.setMinimumWidth(100)
        self.decode_button.clicked.connect(self._on_decode)
        self.decode_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        button_layout.addWidget(self.decode_button)
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.setMinimumWidth(100)
        self.clear_button.clicked.connect(self._on_clear)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
            QPushButton:pressed {
                background-color: #424242;
            }
        """)
        button_layout.addWidget(self.clear_button)
        
        layout.addLayout(button_layout)
        
        # Output section
        output_group = QGroupBox("Decoded Output")
        output_layout = QVBoxLayout(output_group)
        
        # Create a weather display widget for output
        self.output_display = WeatherDisplay()
        output_layout.addWidget(self.output_display)
        
        layout.addWidget(output_group)
        
        # Set default focus
        self.input_text.setFocus()
        
    def _on_decode(self):
        """Handle decode button click."""
        raw_text = self.input_text.toPlainText().strip()
        
        if not raw_text:
            QMessageBox.warning(
                self,
                "No Input",
                "Please paste METAR or TAF text to decode."
            )
            return
        
        # Try to detect and decode
        try:
            # Check if it's a TAF
            if raw_text.upper().startswith('TAF'):
                self._decode_taf(raw_text)
            # Check if it looks like a METAR
            elif self._looks_like_metar(raw_text):
                self._decode_metar(raw_text)
            else:
                QMessageBox.warning(
                    self,
                    "Unknown Format",
                    "Could not detect if this is a METAR or TAF.\n\n"
                    "Make sure the text starts with 'TAF' for TAF forecasts, "
                    "or contains a valid METAR format."
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Decode Error",
                f"Error decoding weather data:\n\n{str(e)}\n\n"
                "Please check that the format is correct."
            )
    
    def _looks_like_metar(self, text: str) -> bool:
        """Check if text looks like a METAR."""
        # Simple heuristic: METARs typically start with a 4-letter station code
        # followed by a date-time group
        parts = text.split()
        if len(parts) < 2:
            return False
        
        # First part should be 4 letters (station code) or "METAR"
        first = parts[0].upper()
        if first == "METAR":
            return True
        
        if len(first) == 4 and first.isalpha():
            # Second part should be date-time (6 digits + Z)
            second = parts[1]
            if len(second) == 7 and second[:-1].isdigit() and second[-1] == 'Z':
                return True
        
        return False
    
    def _decode_metar(self, raw_text: str):
        """Decode METAR text."""
        try:
            metar_data = self.metar_decoder.decode(raw_text)
            self.output_display.update_weather(metar_data, None)
        except Exception as e:
            raise Exception(f"METAR decode failed: {str(e)}")
    
    def _decode_taf(self, raw_text: str):
        """Decode TAF text."""
        try:
            taf_data = self.taf_decoder.decode(raw_text)
            # Create a minimal METAR-like object for display purposes
            # We'll just show the TAF
            self.output_display._clear_layout()
            self.output_display._add_taf_section(taf_data)
        except Exception as e:
            raise Exception(f"TAF decode failed: {str(e)}")
    
    def _on_clear(self):
        """Handle clear button click."""
        self.input_text.clear()
        self.output_display.show_welcome_message()
        self.input_text.setFocus()
