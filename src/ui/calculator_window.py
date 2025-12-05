"""
Calculator Window for IVAO Weather Tool.
"""

from PySide6.QtWidgets import QDialog, QVBoxLayout
from PySide6.QtCore import Qt

from .widgets.calculator import WeatherCalculatorWidget
from src.data.models import MetarData


class CalculatorWindow(QDialog):
    """
    Separate window for weather calculator.
    """
    
    def __init__(self, parent=None):
        """Initialize calculator window."""
        super().__init__(parent)
        
        self.setWindowTitle("Weather Calculator")
        self.setMinimumSize(500, 600)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.calculator = WeatherCalculatorWidget()
        layout.addWidget(self.calculator)
        
    def update_from_metar(self, metar: MetarData):
        """Update calculator from METAR data."""
        self.calculator.update_from_metar(metar)
