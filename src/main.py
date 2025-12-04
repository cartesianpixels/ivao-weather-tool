#!/usr/bin/env python3
"""
IVAO Weather Tool - Main Entry Point
A cross-platform desktop application for aviation weather interpretation and training.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt


def main():
    """Main application entry point."""
    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("IVAO Weather Tool")
    app.setOrganizationName("IVAO")
    app.setApplicationVersion("0.1.0")
    
    # TODO: Initialize main window
    print("IVAO Weather Tool - Starting...")
    print("Main window will be initialized in Phase 4")
    
    # For now, just show a message
    from PySide6.QtWidgets import QMessageBox
    msg = QMessageBox()
    msg.setWindowTitle("IVAO Weather Tool")
    msg.setText("Welcome to IVAO Weather Tool!\n\nPhase 1 Complete: Project Setup")
    msg.setInformativeText("Next: Implementing Data Layer (Phase 2)")
    msg.exec()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
