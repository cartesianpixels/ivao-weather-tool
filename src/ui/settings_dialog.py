"""
Settings Dialog for IVAO Weather Tool.
Allows users to configure application preferences.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QSpinBox, QTabWidget, QWidget,
    QPushButton, QGridLayout, QGroupBox, QListWidget,
    QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt, Signal

from src.data.models import UserSettings


class SettingsDialog(QDialog):
    """Dialog for application settings."""
    
    settings_changed = Signal(UserSettings)
    
    def __init__(self, current_settings: UserSettings, parent=None):
        """
        Initialize settings dialog.
        
        Args:
            current_settings: Current user settings
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.setWindowTitle("Settings")
        self.setMinimumSize(500, 400)
        
        self.current_settings = current_settings
        self.new_settings = None
        
        self._setup_ui()
        self._load_settings()
        
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Tab widget
        self.tabs = QTabWidget()
        
        # Display tab
        self.display_tab = self._create_display_tab()
        self.tabs.addTab(self.display_tab, "Display")
        
        # Updates tab
        self.updates_tab = self._create_updates_tab()
        self.tabs.addTab(self.updates_tab, "Updates")
        
        # Airports tab
        self.airports_tab = self._create_airports_tab()
        self.tabs.addTab(self.airports_tab, "Airports")
        
        layout.addWidget(self.tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setMinimumWidth(100)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        save_button = QPushButton("Save")
        save_button.setMinimumWidth(100)
        save_button.clicked.connect(self._on_save)
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        button_layout.addWidget(save_button)
        
        layout.addLayout(button_layout)
    
    def _create_display_tab(self) -> QWidget:
        """Create display preferences tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Display group
        display_group = QGroupBox("Display Preferences")
        grid = QGridLayout()
        grid.setSpacing(10)
        
        # Theme
        grid.addWidget(QLabel("Theme:"), 0, 0)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        grid.addWidget(self.theme_combo, 0, 1)
        
        # Wind units
        grid.addWidget(QLabel("Wind Units:"), 1, 0)
        self.wind_unit_combo = QComboBox()
        self.wind_unit_combo.addItems(["knots", "mph"])
        grid.addWidget(self.wind_unit_combo, 1, 1)
        
        # Temperature units
        grid.addWidget(QLabel("Temperature:"), 2, 0)
        self.temp_unit_combo = QComboBox()
        self.temp_unit_combo.addItems(["celsius", "fahrenheit"])
        grid.addWidget(self.temp_unit_combo, 2, 1)
        
        # Pressure units
        grid.addWidget(QLabel("Pressure:"), 3, 0)
        self.pressure_unit_combo = QComboBox()
        self.pressure_unit_combo.addItems(["inHg", "hPa"])
        grid.addWidget(self.pressure_unit_combo, 3, 1)
        
        display_group.setLayout(grid)
        layout.addWidget(display_group)
        
        layout.addStretch()
        return widget
    
    def _create_updates_tab(self) -> QWidget:
        """Create update settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Update group
        update_group = QGroupBox("Update Settings")
        grid = QGridLayout()
        grid.setSpacing(10)
        
        # Update frequency
        grid.addWidget(QLabel("Auto-refresh interval:"), 0, 0)
        freq_layout = QHBoxLayout()
        self.update_freq_spin = QSpinBox()
        self.update_freq_spin.setRange(1, 60)
        self.update_freq_spin.setSuffix(" minutes")
        freq_layout.addWidget(self.update_freq_spin)
        freq_layout.addStretch()
        grid.addLayout(freq_layout, 0, 1)
        
        # Cache TTL
        grid.addWidget(QLabel("Cache duration:"), 1, 0)
        cache_layout = QHBoxLayout()
        self.cache_ttl_spin = QSpinBox()
        self.cache_ttl_spin.setRange(1, 120)
        self.cache_ttl_spin.setSuffix(" minutes")
        cache_layout.addWidget(self.cache_ttl_spin)
        cache_layout.addStretch()
        grid.addLayout(cache_layout, 1, 1)
        
        update_group.setLayout(grid)
        layout.addWidget(update_group)
        
        # Info label
        info = QLabel(
            "Note: Auto-refresh is not yet implemented. "
            "These settings will be used in a future update."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #666; font-size: 10px; margin-top: 10px;")
        layout.addWidget(info)
        
        layout.addStretch()
        return widget
    
    def _create_airports_tab(self) -> QWidget:
        """Create default airports tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Airports group
        airports_group = QGroupBox("Default Airports")
        airports_layout = QVBoxLayout()
        
        info = QLabel("These airports will be shown on startup (future feature):")
        info.setWordWrap(True)
        airports_layout.addWidget(info)
        
        # Airport list
        self.airport_list = QListWidget()
        self.airport_list.setMaximumHeight(150)
        airports_layout.addWidget(self.airport_list)
        
        # Add/Remove buttons
        button_layout = QHBoxLayout()
        
        self.airport_input = QLineEdit()
        self.airport_input.setPlaceholderText("Enter ICAO code (e.g., KJFK)")
        self.airport_input.setMaxLength(4)
        button_layout.addWidget(self.airport_input)
        
        add_button = QPushButton("Add")
        add_button.clicked.connect(self._add_airport)
        button_layout.addWidget(add_button)
        
        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(self._remove_airport)
        button_layout.addWidget(remove_button)
        
        airports_layout.addLayout(button_layout)
        
        airports_group.setLayout(airports_layout)
        layout.addWidget(airports_group)
        
        layout.addStretch()
        return widget
    
    def _load_settings(self):
        """Load current settings into UI."""
        # Display settings
        self.theme_combo.setCurrentText(self.current_settings.theme)
        self.wind_unit_combo.setCurrentText(self.current_settings.wind_unit)
        self.temp_unit_combo.setCurrentText(self.current_settings.temperature_unit)
        self.pressure_unit_combo.setCurrentText(self.current_settings.pressure_unit)
        
        # Update settings
        self.update_freq_spin.setValue(self.current_settings.update_frequency_minutes)
        self.cache_ttl_spin.setValue(self.current_settings.cache_ttl_minutes)
        
        # Airports
        self.airport_list.clear()
        for airport in self.current_settings.default_airports:
            self.airport_list.addItem(airport)
    
    def _add_airport(self):
        """Add airport to list."""
        airport = self.airport_input.text().strip().upper()
        
        if not airport:
            return
        
        if len(airport) != 4 or not airport.isalpha():
            QMessageBox.warning(
                self,
                "Invalid Airport",
                "Airport code must be 4 letters (e.g., KJFK)"
            )
            return
        
        # Check if already in list
        for i in range(self.airport_list.count()):
            if self.airport_list.item(i).text() == airport:
                QMessageBox.information(
                    self,
                    "Duplicate",
                    f"{airport} is already in the list"
                )
                return
        
        self.airport_list.addItem(airport)
        self.airport_input.clear()
    
    def _remove_airport(self):
        """Remove selected airport from list."""
        current_item = self.airport_list.currentItem()
        if current_item:
            self.airport_list.takeItem(self.airport_list.row(current_item))
    
    def _on_save(self):
        """Save settings and close dialog."""
        # Collect airports
        airports = []
        for i in range(self.airport_list.count()):
            airports.append(self.airport_list.item(i).text())
        
        # Create new settings object
        self.new_settings = UserSettings(
            theme=self.theme_combo.currentText(),
            wind_unit=self.wind_unit_combo.currentText(),
            temperature_unit=self.temp_unit_combo.currentText(),
            pressure_unit=self.pressure_unit_combo.currentText(),
            update_frequency_minutes=self.update_freq_spin.value(),
            cache_ttl_minutes=self.cache_ttl_spin.value(),
            default_airports=airports if airports else ["KJFK", "KLAX", "KORD"],
            show_training_hints=self.current_settings.show_training_hints,
            completed_lessons=self.current_settings.completed_lessons
        )
        
        self.settings_changed.emit(self.new_settings)
        self.accept()
    
    def get_settings(self) -> UserSettings:
        """Get the new settings."""
        return self.new_settings
