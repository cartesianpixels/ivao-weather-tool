"""
Main Window for IVAO Weather Tool.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QToolBar, QStatusBar, QMessageBox
)
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import Qt, QSize

from .widgets.search_bar import SearchBar
from .widgets.weather_display import WeatherDisplay
from .calculator_window import CalculatorWindow
from .weather_fetcher import WeatherFetcher
from src.domain.metar_decoder import MetarDecoder
from src.domain.taf_decoder import TafDecoder

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        """Initialize main window."""
        super().__init__()
        
        self.setWindowTitle("IVAO Weather Tool")
        self.setMinimumSize(800, 600)
        
        # Initialize decoders
        self.metar_decoder = MetarDecoder()
        self.taf_decoder = TafDecoder()
        
        # Initialize calculator window
        self.calculator_window = None
        self.current_metar = None
        
        # Setup UI
        self._setup_ui()
        self._setup_toolbar()
        self._setup_menu()
        
    def _setup_ui(self):
        """Setup central widget and layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Search Bar
        self.search_bar = SearchBar()
        self.search_bar.search_triggered.connect(self._on_search)
        layout.addWidget(self.search_bar)
        
        # Weather Display
        self.weather_display = WeatherDisplay()
        layout.addWidget(self.weather_display)
        
        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
    def _setup_toolbar(self):
        """Setup toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Refresh Action
        refresh_action = QAction("Refresh", self)
        refresh_action.setStatusTip("Refresh current weather")
        refresh_action.triggered.connect(self._on_refresh)
        toolbar.addAction(refresh_action)
        
        toolbar.addSeparator()
        
        # Calculator Action
        calc_action = QAction("Calculator", self)
        calc_action.setStatusTip("Open weather calculator")
        calc_action.triggered.connect(self._show_calculator)
        toolbar.addAction(calc_action)
        
        toolbar.addSeparator()
        
        # Settings Action
        settings_action = QAction("Settings", self)
        settings_action.setStatusTip("Configure application settings")
        toolbar.addAction(settings_action)
        
    def _setup_menu(self):
        """Setup menu bar."""
        menu = self.menuBar()
        
        # File Menu
        file_menu = menu.addMenu("&File")
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View Menu
        view_menu = menu.addMenu("&View")
        # Add view options later
        
        # Help Menu
        help_menu = menu.addMenu("&Help")
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        
    def _on_search(self, airport_code):
        """Handle airport search."""
        self.status_bar.showMessage(f"Fetching weather for {airport_code}...")
        self.search_bar.setEnabled(False)
        
        # Create and start weather fetcher thread
        self.fetcher = WeatherFetcher(airport_code.upper())
        self.fetcher.weather_ready.connect(self._on_weather_ready)
        self.fetcher.error_occurred.connect(self._on_weather_error)
        self.fetcher.finished.connect(lambda: self.search_bar.setEnabled(True))
        self.fetcher.start()
        
    def _on_weather_ready(self, metar_data, taf_data):
        """Handle successful weather fetch."""
        self.current_metar = metar_data
        self.weather_display.update_weather(metar_data, taf_data)
        
        # Update calculator if window is open
        if self.calculator_window and self.calculator_window.isVisible():
            self.calculator_window.update_from_metar(metar_data)
            
        self.status_bar.showMessage(f"Weather updated for {metar_data.station}")
        
    def _on_weather_error(self, error_msg):
        """Handle weather fetch error."""
        self.status_bar.showMessage(f"Error: {error_msg}")
        QMessageBox.warning(self, "Error", error_msg)
            
    def _on_refresh(self):
        """Handle refresh action."""
        current_text = self.search_bar.text().strip()
        if current_text:
            self._on_search(current_text)
            
    def _show_calculator(self):
        """Show calculator window."""
        if not self.calculator_window:
            self.calculator_window = CalculatorWindow(self)
            
        # Update with current METAR if available
        if self.current_metar:
            self.calculator_window.update_from_metar(self.current_metar)
            
        self.calculator_window.show()
        self.calculator_window.raise_()
        self.calculator_window.activateWindow()
            
    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About IVAO Weather Tool",
            "IVAO Weather Tool\n\nA comprehensive weather analysis tool for flight simulation.\n\nVersion 0.1.0"
        )
