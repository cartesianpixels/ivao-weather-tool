"""
Search Bar Widget for IVAO Weather Tool.
"""

from PySide6.QtWidgets import QLineEdit, QCompleter
from PySide6.QtCore import Qt, Signal

class SearchBar(QLineEdit):
    """
    Search bar for airport codes with autocomplete.
    """
    
    # Signal emitted when a search is triggered (enter pressed or item selected)
    search_triggered = Signal(str)
    
    def __init__(self, parent=None):
        """Initialize search bar."""
        super().__init__(parent)
        
        self.setPlaceholderText("Enter airport code (e.g., KJFK, EGLL)...")
        self.setClearButtonEnabled(True)
        
        # Setup completer (will be populated with airport data later)
        self.completer = QCompleter([])
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.setCompleter(self.completer)
        
        # Connect signals
        self.returnPressed.connect(self._on_return_pressed)
        self.completer.activated.connect(self._on_completer_activated)
        
    def _on_return_pressed(self):
        """Handle return key press."""
        text = self.text().strip().upper()
        if text:
            self.search_triggered.emit(text)
            
    def _on_completer_activated(self, text):
        """Handle selection from completer."""
        if text:
            self.search_triggered.emit(text)
            
    def update_completer_model(self, items: list[str]):
        """Update the autocomplete list."""
        from PySide6.QtCore import QStringListModel
        model = QStringListModel(items)
        self.completer.setModel(model)
