"""
Theme Manager for IVAO Weather Tool.
Provides dark and light theme stylesheets.
"""

class ThemeManager:
    """Manages application themes."""
    
    @staticmethod
    def get_dark_theme() -> str:
        """Get dark theme stylesheet."""
        return """
        /* Main Window */
        QMainWindow {
            background-color: #1e1e1e;
            color: #e0e0e0;
        }
        
        /* Central Widget */
        QWidget {
            background-color: #1e1e1e;
            color: #e0e0e0;
        }
        
        /* Menu Bar */
        QMenuBar {
            background-color: #2d2d2d;
            color: #e0e0e0;
            border-bottom: 1px solid #3d3d3d;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 4px 12px;
        }
        
        QMenuBar::item:selected {
            background-color: #3d3d3d;
        }
        
        QMenuBar::item:pressed {
            background-color: #4d4d4d;
        }
        
        /* Menu */
        QMenu {
            background-color: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #3d3d3d;
        }
        
        QMenu::item {
            padding: 6px 24px;
        }
        
        QMenu::item:selected {
            background-color: #3d3d3d;
        }
        
        /* Toolbar */
        QToolBar {
            background-color: #2d2d2d;
            border-bottom: 1px solid #3d3d3d;
            spacing: 3px;
            padding: 4px;
        }
        
        QToolButton {
            background-color: transparent;
            color: #e0e0e0;
            border: none;
            padding: 6px;
            border-radius: 4px;
        }
        
        QToolButton:hover {
            background-color: #3d3d3d;
        }
        
        QToolButton:pressed {
            background-color: #4d4d4d;
        }
        
        /* Status Bar */
        QStatusBar {
            background-color: #2d2d2d;
            color: #b0b0b0;
            border-top: 1px solid #3d3d3d;
        }
        
        /* Line Edit */
        QLineEdit {
            background-color: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #3d3d3d;
            border-radius: 4px;
            padding: 6px;
            selection-background-color: #0d47a1;
        }
        
        QLineEdit:focus {
            border: 1px solid #2196F3;
        }
        
        /* Text Edit */
        QTextEdit {
            background-color: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #3d3d3d;
            border-radius: 4px;
            selection-background-color: #0d47a1;
        }
        
        QTextEdit:focus {
            border: 1px solid #2196F3;
        }
        
        /* Push Button */
        QPushButton {
            background-color: #3d3d3d;
            color: #e0e0e0;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }
        
        QPushButton:hover {
            background-color: #4d4d4d;
        }
        
        QPushButton:pressed {
            background-color: #5d5d5d;
        }
        
        QPushButton:disabled {
            background-color: #2d2d2d;
            color: #666666;
        }
        
        /* Group Box */
        QGroupBox {
            color: #e0e0e0;
            border: 2px solid #3d3d3d;
            border-radius: 6px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        
        /* Label */
        QLabel {
            color: #e0e0e0;
            background-color: transparent;
        }
        
        /* Scroll Area */
        QScrollArea {
            background-color: #1e1e1e;
            border: none;
        }
        
        /* Scroll Bar */
        QScrollBar:vertical {
            background-color: #2d2d2d;
            width: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #4d4d4d;
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #5d5d5d;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        QScrollBar:horizontal {
            background-color: #2d2d2d;
            height: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #4d4d4d;
            border-radius: 6px;
            min-width: 20px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #5d5d5d;
        }
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        
        /* Combo Box */
        QComboBox {
            background-color: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #3d3d3d;
            border-radius: 4px;
            padding: 6px;
        }
        
        QComboBox:hover {
            border: 1px solid #4d4d4d;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        
        QComboBox::down-arrow {
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 6px solid #e0e0e0;
            margin-right: 6px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #3d3d3d;
            selection-background-color: #3d3d3d;
        }
        
        /* Spin Box */
        QSpinBox {
            background-color: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #3d3d3d;
            border-radius: 4px;
            padding: 6px;
        }
        
        QSpinBox:focus {
            border: 1px solid #2196F3;
        }
        
        QSpinBox::up-button, QSpinBox::down-button {
            background-color: #3d3d3d;
            border: none;
            width: 16px;
        }
        
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {
            background-color: #4d4d4d;
        }
        
        /* Tab Widget */
        QTabWidget::pane {
            border: 1px solid #3d3d3d;
            background-color: #1e1e1e;
        }
        
        QTabBar::tab {
            background-color: #2d2d2d;
            color: #b0b0b0;
            border: 1px solid #3d3d3d;
            padding: 8px 16px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background-color: #1e1e1e;
            color: #e0e0e0;
            border-bottom: 2px solid #2196F3;
        }
        
        QTabBar::tab:hover:!selected {
            background-color: #3d3d3d;
        }
        
        /* List Widget */
        QListWidget {
            background-color: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #3d3d3d;
            border-radius: 4px;
        }
        
        QListWidget::item {
            padding: 6px;
        }
        
        QListWidget::item:selected {
            background-color: #3d3d3d;
        }
        
        QListWidget::item:hover {
            background-color: #353535;
        }
        
        /* Dialog */
        QDialog {
            background-color: #1e1e1e;
            color: #e0e0e0;
        }
        """
    
    @staticmethod
    def get_light_theme() -> str:
        """Get light theme stylesheet."""
        return """
        /* Main Window */
        QMainWindow {
            background-color: #ffffff;
            color: #212121;
        }
        
        /* Central Widget */
        QWidget {
            background-color: #ffffff;
            color: #212121;
        }
        
        /* Menu Bar */
        QMenuBar {
            background-color: #f5f5f5;
            color: #212121;
            border-bottom: 1px solid #e0e0e0;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 4px 12px;
        }
        
        QMenuBar::item:selected {
            background-color: #e0e0e0;
        }
        
        QMenuBar::item:pressed {
            background-color: #d0d0d0;
        }
        
        /* Menu */
        QMenu {
            background-color: #ffffff;
            color: #212121;
            border: 1px solid #e0e0e0;
        }
        
        QMenu::item {
            padding: 6px 24px;
        }
        
        QMenu::item:selected {
            background-color: #e3f2fd;
        }
        
        /* Toolbar */
        QToolBar {
            background-color: #f5f5f5;
            border-bottom: 1px solid #e0e0e0;
            spacing: 3px;
            padding: 4px;
        }
        
        QToolButton {
            background-color: transparent;
            color: #212121;
            border: none;
            padding: 6px;
            border-radius: 4px;
        }
        
        QToolButton:hover {
            background-color: #e0e0e0;
        }
        
        QToolButton:pressed {
            background-color: #d0d0d0;
        }
        
        /* Status Bar */
        QStatusBar {
            background-color: #f5f5f5;
            color: #666666;
            border-top: 1px solid #e0e0e0;
        }
        
        /* Line Edit */
        QLineEdit {
            background-color: #ffffff;
            color: #212121;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            padding: 6px;
            selection-background-color: #2196F3;
        }
        
        QLineEdit:focus {
            border: 1px solid #2196F3;
        }
        
        /* Text Edit */
        QTextEdit {
            background-color: #ffffff;
            color: #212121;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            selection-background-color: #2196F3;
        }
        
        QTextEdit:focus {
            border: 1px solid #2196F3;
        }
        
        /* Push Button */
        QPushButton {
            background-color: #f5f5f5;
            color: #212121;
            border: 1px solid #e0e0e0;
            padding: 8px 16px;
            border-radius: 4px;
        }
        
        QPushButton:hover {
            background-color: #e0e0e0;
        }
        
        QPushButton:pressed {
            background-color: #d0d0d0;
        }
        
        QPushButton:disabled {
            background-color: #f5f5f5;
            color: #999999;
        }
        
        /* Group Box */
        QGroupBox {
            color: #212121;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        
        /* Label */
        QLabel {
            color: #212121;
            background-color: transparent;
        }
        
        /* Scroll Area */
        QScrollArea {
            background-color: #ffffff;
            border: none;
        }
        
        /* Scroll Bar */
        QScrollBar:vertical {
            background-color: #f5f5f5;
            width: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #c0c0c0;
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #a0a0a0;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        QScrollBar:horizontal {
            background-color: #f5f5f5;
            height: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #c0c0c0;
            border-radius: 6px;
            min-width: 20px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #a0a0a0;
        }
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        
        /* Combo Box */
        QComboBox {
            background-color: #ffffff;
            color: #212121;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            padding: 6px;
        }
        
        QComboBox:hover {
            border: 1px solid #c0c0c0;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        
        QComboBox::down-arrow {
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 6px solid #212121;
            margin-right: 6px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #ffffff;
            color: #212121;
            border: 1px solid #e0e0e0;
            selection-background-color: #e3f2fd;
        }
        
        /* Spin Box */
        QSpinBox {
            background-color: #ffffff;
            color: #212121;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            padding: 6px;
        }
        
        QSpinBox:focus {
            border: 1px solid #2196F3;
        }
        
        QSpinBox::up-button, QSpinBox::down-button {
            background-color: #f5f5f5;
            border: none;
            width: 16px;
        }
        
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {
            background-color: #e0e0e0;
        }
        
        /* Tab Widget */
        QTabWidget::pane {
            border: 1px solid #e0e0e0;
            background-color: #ffffff;
        }
        
        QTabBar::tab {
            background-color: #f5f5f5;
            color: #666666;
            border: 1px solid #e0e0e0;
            padding: 8px 16px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background-color: #ffffff;
            color: #212121;
            border-bottom: 2px solid #2196F3;
        }
        
        QTabBar::tab:hover:!selected {
            background-color: #e0e0e0;
        }
        
        /* List Widget */
        QListWidget {
            background-color: #ffffff;
            color: #212121;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
        }
        
        QListWidget::item {
            padding: 6px;
        }
        
        QListWidget::item:selected {
            background-color: #e3f2fd;
        }
        
        QListWidget::item:hover {
            background-color: #f5f5f5;
        }
        
        /* Dialog */
        QDialog {
            background-color: #ffffff;
            color: #212121;
        }
        """
    
    @staticmethod
    def apply_theme(app, theme: str):
        """
        Apply theme to application.
        
        Args:
            app: QApplication instance
            theme: "dark" or "light"
        """
        if theme == "dark":
            app.setStyleSheet(ThemeManager.get_dark_theme())
        else:
            app.setStyleSheet(ThemeManager.get_light_theme())
