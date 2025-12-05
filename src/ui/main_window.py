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
from .manual_decoder_dialog import ManualDecoderDialog
from .settings_dialog import SettingsDialog
from .weather_fetcher import WeatherFetcher
from src.domain.metar_decoder import MetarDecoder
from src.domain.taf_decoder import TafDecoder
from src.data.models import UserSettings
from src.ui.theme_manager import ThemeManager

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, app):
        """Initialize main window."""
        super().__init__()
        
        self.app = app  # Store QApplication reference for theme changes
        
        self.setWindowTitle("IVAO Weather Tool")
        self.setMinimumSize(800, 600)
        
        # Initialize decoders
        self.metar_decoder = MetarDecoder()
        self.taf_decoder = TafDecoder()
        
        # Initialize windows
        self.calculator_window = None
        self.manual_decoder_window = None
        self.current_metar = None
        
        # Initialize settings with defaults
        self.user_settings = UserSettings()
        
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
        
        # Manual Decoder Action
        decoder_action = QAction("Manual Decoder", self)
        decoder_action.setStatusTip("Manually decode METAR/TAF")
        decoder_action.triggered.connect(self._show_manual_decoder)
        toolbar.addAction(decoder_action)
        
        toolbar.addSeparator()
        
        # Settings Action
        settings_action = QAction("Settings", self)
        settings_action.setStatusTip("Configure application settings")
        settings_action.triggered.connect(self._show_settings)
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
        
        # Tools Menu
        tools_menu = menu.addMenu("&Tools")
        
        calc_menu_action = QAction("&Calculator", self)
        calc_menu_action.setShortcut("Ctrl+K")
        calc_menu_action.triggered.connect(self._show_calculator)
        tools_menu.addAction(calc_menu_action)
        
        decoder_menu_action = QAction("&Manual Decoder", self)
        decoder_menu_action.setShortcut("Ctrl+M")
        decoder_menu_action.triggered.connect(self._show_manual_decoder)
        tools_menu.addAction(decoder_menu_action)
        
        tools_menu.addSeparator()
        
        settings_menu_action = QAction("&Settings", self)
        settings_menu_action.setShortcut("Ctrl+,")
        settings_menu_action.triggered.connect(self._show_settings)
        tools_menu.addAction(settings_menu_action)
        
        # View Menu
        view_menu = menu.addMenu("&View")
        
        # Toggle calculator
        self.toggle_calc_action = QAction("Show Calculator", self)
        self.toggle_calc_action.setCheckable(True)
        self.toggle_calc_action.triggered.connect(self._toggle_calculator)
        view_menu.addAction(self.toggle_calc_action)
        
        # Toggle status bar
        self.toggle_status_action = QAction("Show Status Bar", self)
        self.toggle_status_action.setCheckable(True)
        self.toggle_status_action.setChecked(True)
        self.toggle_status_action.triggered.connect(self._toggle_status_bar)
        view_menu.addAction(self.toggle_status_action)
        
        view_menu.addSeparator()
        
        # Font size submenu
        font_menu = view_menu.addMenu("Font Size")
        
        small_font_action = QAction("Small", self)
        small_font_action.triggered.connect(lambda: self._set_font_size("small"))
        font_menu.addAction(small_font_action)
        
        medium_font_action = QAction("Medium", self)
        medium_font_action.triggered.connect(lambda: self._set_font_size("medium"))
        font_menu.addAction(medium_font_action)
        
        large_font_action = QAction("Large", self)
        large_font_action.triggered.connect(lambda: self._set_font_size("large"))
        font_menu.addAction(large_font_action)
        
        view_menu.addSeparator()
        
        # Reset layout
        reset_action = QAction("Reset Layout", self)
        reset_action.triggered.connect(self._reset_layout)
        view_menu.addAction(reset_action)
        
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
            
    def _show_manual_decoder(self):
        """Show manual decoder dialog."""
        if not self.manual_decoder_window:
            self.manual_decoder_window = ManualDecoderDialog(self)
        
        self.manual_decoder_window.show()
        self.manual_decoder_window.raise_()
        self.manual_decoder_window.activateWindow()
    
    def _show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self.user_settings, self)
        if dialog.exec():
            new_settings = dialog.get_settings()
            if new_settings:
                old_theme = self.user_settings.theme
                self.user_settings = new_settings
                
                # Apply theme if changed
                if new_settings.theme != old_theme:
                    ThemeManager.apply_theme(self.app, new_settings.theme)
                    self.status_bar.showMessage(f"Theme changed to {new_settings.theme}", 3000)
                else:
                    self.status_bar.showMessage("Settings saved", 3000)
    
    def _toggle_calculator(self):
        """Toggle calculator window visibility."""
        if self.calculator_window and self.calculator_window.isVisible():
            self.calculator_window.hide()
            self.toggle_calc_action.setChecked(False)
        else:
            self._show_calculator()
            self.toggle_calc_action.setChecked(True)
    
    def _toggle_status_bar(self):
        """Toggle status bar visibility."""
        if self.status_bar.isVisible():
            self.status_bar.hide()
        else:
            self.status_bar.show()
    
    def _set_font_size(self, size: str):
        """Set application font size."""
        from PySide6.QtGui import QFont
        
        font = self.font()
        if size == "small":
            font.setPointSize(9)
        elif size == "medium":
            font.setPointSize(10)
        elif size == "large":
            font.setPointSize(12)
        
        self.setFont(font)
        self.status_bar.showMessage(f"Font size set to {size}", 2000)
    
    def _reset_layout(self):
        """Reset window layout to defaults."""
        self.resize(800, 600)
        self.move(100, 100)
        self.status_bar.showMessage("Layout reset", 2000)
    
    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About IVAO Weather Tool",
            "IVAO Weather Tool\n\nA comprehensive weather analysis tool for flight simulation.\n\nVersion 0.1.0"
        )
