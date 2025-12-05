"""
IVAO Weather Tool Application Entry Point.
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path so we can import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.ui.theme_manager import ThemeManager

def setup_logging():
    """Configure logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """Main application entry point."""
    setup_logging()
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("IVAO Weather Tool")
    app.setOrganizationName("IVAO")
    app.setApplicationVersion("1.0.0")
    
    # Author Metadata
    app.setProperty("author", "Abdellah Chaaibi")
    app.setProperty("ivao_vid", "710267")
    app.setProperty("email", "cartesianpixels@gmail.com")
    
    # Apply default dark theme
    ThemeManager.apply_theme(app, "dark")
    
    # Create and show main window
    window = MainWindow(app)
    window.show()
    
    # Run event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
