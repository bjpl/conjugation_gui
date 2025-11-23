"""
Professional Styling and Branding for the Application
"""

from typing import Dict, Any, Optional
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtWidgets import QApplication

class ProfessionalTheme:
    """Professional theme manager with light and dark modes"""
    
    # Color palettes
    LIGHT_THEME = {
        'primary': '#3498db',           # Professional blue
        'primary_dark': '#2980b9',      # Darker blue for hover
        'primary_light': '#5dade2',     # Lighter blue for accents
        'secondary': '#e74c3c',         # Spanish red accent
        'secondary_dark': '#c0392b',    # Darker red
        'success': '#27ae60',           # Success green
        'warning': '#f39c12',           # Warning orange
        'danger': '#e74c3c',            # Danger red
        'background': '#ffffff',        # Main background
        'surface': '#f8f9fa',           # Card/surface background
        'surface_hover': '#e9ecef',     # Hover state
        'border': '#dee2e6',            # Border color
        'text_primary': '#2c3e50',      # Primary text
        'text_secondary': '#6c757d',    # Secondary text
        'text_muted': '#adb5bd',        # Muted text
        'shadow': 'rgba(0,0,0,0.1)'     # Shadow color
    }
    
    DARK_THEME = {
        'primary': '#3498db',           # Same blue works in dark
        'primary_dark': '#2980b9',      
        'primary_light': '#5dade2',     
        'secondary': '#e74c3c',         # Spanish red
        'secondary_dark': '#c0392b',    
        'success': '#2ecc71',           # Brighter green for dark
        'warning': '#f1c40f',           # Brighter yellow
        'danger': '#e74c3c',            
        'background': '#2c3e50',        # Dark background
        'surface': '#34495e',           # Card background
        'surface_hover': '#4a5f7a',     # Hover state
        'border': '#4a5f7a',            # Border color
        'text_primary': '#ecf0f1',      # Light text
        'text_secondary': '#bdc3c7',    # Secondary text
        'text_muted': '#95a5a6',        # Muted text
        'shadow': 'rgba(0,0,0,0.3)'     # Stronger shadow
    }

class StyleSheetBuilder:
    """Builds professional stylesheets for different components"""
    
    @staticmethod
    def get_main_window_style(theme: Dict[str, str]) -> str:
        """Get main window stylesheet"""
        return f"""
        QMainWindow {{
            background-color: {theme['background']};
            color: {theme['text_primary']};
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', 'Helvetica Neue', Arial, sans-serif;
            font-size: 12px;
        }}
        
        QMainWindow::separator {{
            background-color: {theme['border']};
            width: 1px;
            height: 1px;
        }}
        """
    
    @staticmethod
    def get_toolbar_style(theme: Dict[str, str]) -> str:
        """Get toolbar stylesheet"""
        return f"""
        QToolBar {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 {theme['surface']}, stop: 1 {theme['surface_hover']});
            border: none;
            border-bottom: 1px solid {theme['border']};
            spacing: 3px;
            padding: 4px;
        }}
        
        QToolBar::separator {{
            background-color: {theme['border']};
            width: 1px;
            margin: 2px 4px;
        }}
        
        QToolBar QToolButton {{
            background-color: transparent;
            border: 1px solid transparent;
            border-radius: 6px;
            padding: 6px 12px;
            margin: 1px;
            color: {theme['text_primary']};
            font-weight: 500;
        }}
        
        QToolBar QToolButton:hover {{
            background-color: {theme['primary_light']};
            color: white;
            border-color: {theme['primary']};
        }}
        
        QToolBar QToolButton:pressed {{
            background-color: {theme['primary_dark']};
            color: white;
        }}
        
        QToolBar QToolButton:checked {{
            background-color: {theme['primary']};
            color: white;
            border-color: {theme['primary_dark']};
        }}
        """
    
    @staticmethod
    def get_button_style(theme: Dict[str, str]) -> str:
        """Get button stylesheet"""
        return f"""
        QPushButton {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 {theme['primary']}, stop: 1 {theme['primary_dark']});
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 600;
            font-size: 12px;
            min-width: 80px;
        }}
        
        QPushButton:hover {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 {theme['primary_light']}, stop: 1 {theme['primary']});
        }}
        
        QPushButton:pressed {{
            background: {theme['primary_dark']};
        }}
        
        QPushButton:disabled {{
            background-color: {theme['text_muted']};
            color: {theme['surface']};
        }}
        
        QPushButton:default {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 {theme['success']}, stop: 1 #1e8449);
            border: 2px solid #1e8449;
        }}
        
        /* Secondary button style */
        QPushButton[buttonType="secondary"] {{
            background: {theme['surface']};
            color: {theme['text_primary']};
            border: 2px solid {theme['border']};
        }}
        
        QPushButton[buttonType="secondary"]:hover {{
            background: {theme['surface_hover']};
            border-color: {theme['primary']};
        }}
        
        /* Danger button style */
        QPushButton[buttonType="danger"] {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 {theme['danger']}, stop: 1 {theme['secondary_dark']});
        }}
        """
    
    @staticmethod
    def get_input_style(theme: Dict[str, str]) -> str:
        """Get input field stylesheet"""
        return f"""
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {theme['background']};
            border: 2px solid {theme['border']};
            border-radius: 6px;
            padding: 8px 12px;
            color: {theme['text_primary']};
            font-size: 12px;
            selection-background-color: {theme['primary']};
            selection-color: white;
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {theme['primary']};
            outline: none;
        }}
        
        QLineEdit:disabled, QTextEdit:disabled {{
            background-color: {theme['surface']};
            color: {theme['text_muted']};
            border-color: {theme['surface_hover']};
        }}
        
        QComboBox {{
            background-color: {theme['background']};
            border: 2px solid {theme['border']};
            border-radius: 6px;
            padding: 6px 12px;
            color: {theme['text_primary']};
            font-size: 12px;
            min-width: 100px;
        }}
        
        QComboBox:focus {{
            border-color: {theme['primary']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border: 2px solid {theme['text_secondary']};
            width: 6px;
            height: 6px;
            border-top: none;
            border-left: none;
            transform: rotate(45deg);
            margin-right: 8px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {theme['background']};
            border: 1px solid {theme['border']};
            selection-background-color: {theme['primary_light']};
            selection-color: white;
            outline: none;
        }}
        """
    
    @staticmethod
    def get_groupbox_style(theme: Dict[str, str]) -> str:
        """Get group box stylesheet"""
        return f"""
        QGroupBox {{
            font-weight: 600;
            border: 2px solid {theme['border']};
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 12px;
            background-color: {theme['surface']};
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 8px 0 8px;
            color: {theme['text_primary']};
            background-color: {theme['surface']};
        }}
        
        QGroupBox::indicator {{
            width: 16px;
            height: 16px;
            border-radius: 3px;
            border: 2px solid {theme['border']};
            background-color: {theme['background']};
        }}
        
        QGroupBox::indicator:checked {{
            background-color: {theme['primary']};
            border-color: {theme['primary']};
            image: url(checkmark.png); /* Would need actual checkmark icon */
        }}
        """
    
    @staticmethod
    def get_checkbox_style(theme: Dict[str, str]) -> str:
        """Get checkbox stylesheet"""
        return f"""
        QCheckBox {{
            color: {theme['text_primary']};
            font-size: 12px;
            spacing: 8px;
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 2px solid {theme['border']};
            background-color: {theme['background']};
        }}
        
        QCheckBox::indicator:hover {{
            border-color: {theme['primary']};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {theme['primary']};
            border-color: {theme['primary']};
        }}
        
        QCheckBox::indicator:checked:hover {{
            background-color: {theme['primary_light']};
        }}
        
        QRadioButton {{
            color: {theme['text_primary']};
            font-size: 12px;
            spacing: 8px;
        }}
        
        QRadioButton::indicator {{
            width: 16px;
            height: 16px;
            border-radius: 8px;
            border: 2px solid {theme['border']};
            background-color: {theme['background']};
        }}
        
        QRadioButton::indicator:hover {{
            border-color: {theme['primary']};
        }}
        
        QRadioButton::indicator:checked {{
            background-color: {theme['primary']};
            border-color: {theme['primary']};
        }}
        """
    
    @staticmethod
    def get_progress_style(theme: Dict[str, str]) -> str:
        """Get progress bar stylesheet"""
        return f"""
        QProgressBar {{
            background-color: {theme['surface']};
            border: 1px solid {theme['border']};
            border-radius: 8px;
            text-align: center;
            font-weight: 600;
            color: {theme['text_primary']};
            height: 20px;
        }}
        
        QProgressBar::chunk {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 {theme['primary_light']}, stop: 1 {theme['primary']});
            border-radius: 6px;
        }}
        """
    
    @staticmethod
    def get_statusbar_style(theme: Dict[str, str]) -> str:
        """Get status bar stylesheet"""
        return f"""
        QStatusBar {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 {theme['surface']}, stop: 1 {theme['surface_hover']});
            border-top: 1px solid {theme['border']};
            color: {theme['text_secondary']};
            font-size: 11px;
            padding: 4px;
        }}
        
        QStatusBar::item {{
            border: none;
        }}
        """
    
    @staticmethod
    def get_splitter_style(theme: Dict[str, str]) -> str:
        """Get splitter stylesheet"""
        return f"""
        QSplitter::handle {{
            background-color: {theme['border']};
        }}
        
        QSplitter::handle:horizontal {{
            width: 1px;
        }}
        
        QSplitter::handle:vertical {{
            height: 1px;
        }}
        
        QSplitter::handle:hover {{
            background-color: {theme['primary']};
        }}
        """

class ProfessionalStyling:
    """Main styling manager for the application"""
    
    def __init__(self):
        self.current_theme = "light"
        self.themes = {
            'light': ProfessionalTheme.LIGHT_THEME,
            'dark': ProfessionalTheme.DARK_THEME
        }
    
    def apply_theme(self, app: QApplication, theme_name: str = "light"):
        """Apply a complete theme to the application"""
        if theme_name not in self.themes:
            theme_name = "light"
        
        self.current_theme = theme_name
        theme = self.themes[theme_name]
        
        # Build complete stylesheet
        stylesheet_parts = [
            StyleSheetBuilder.get_main_window_style(theme),
            StyleSheetBuilder.get_toolbar_style(theme),
            StyleSheetBuilder.get_button_style(theme),
            StyleSheetBuilder.get_input_style(theme),
            StyleSheetBuilder.get_groupbox_style(theme),
            StyleSheetBuilder.get_checkbox_style(theme),
            StyleSheetBuilder.get_progress_style(theme),
            StyleSheetBuilder.get_statusbar_style(theme),
            StyleSheetBuilder.get_splitter_style(theme),
        ]
        
        complete_stylesheet = "\n".join(stylesheet_parts)
        app.setStyleSheet(complete_stylesheet)
        
        # Set application-wide font
        font = QFont("Segoe UI", 10)
        font.setStyleHint(QFont.SansSerif)
        app.setFont(font)
    
    def get_theme_colors(self, theme_name: str = None) -> Dict[str, str]:
        """Get theme colors"""
        if theme_name is None:
            theme_name = self.current_theme
        return self.themes.get(theme_name, self.themes['light'])
    
    def is_dark_theme(self) -> bool:
        """Check if current theme is dark"""
        return self.current_theme == "dark"
    
    def toggle_theme(self, app: QApplication) -> str:
        """Toggle between light and dark themes"""
        new_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme(app, new_theme)
        return new_theme
    
    @staticmethod
    def get_accent_color(color_name: str, theme: Dict[str, str]) -> str:
        """Get accent color for highlights"""
        accent_colors = {
            'spanish_red': '#e74c3c',
            'success': theme.get('success', '#27ae60'),
            'warning': theme.get('warning', '#f39c12'),
            'info': theme.get('primary', '#3498db')
        }
        return accent_colors.get(color_name, theme.get('primary', '#3498db'))
    
    @staticmethod
    def apply_card_styling(widget, theme: Dict[str, str]):
        """Apply card-like styling to a widget"""
        widget.setStyleSheet(f"""
            background-color: {theme['surface']};
            border: 1px solid {theme['border']};
            border-radius: 8px;
            padding: 12px;
        """)
    
    @staticmethod
    def apply_emphasis_styling(widget, theme: Dict[str, str], style_type: str = "primary"):
        """Apply emphasis styling (primary, secondary, success, warning, danger)"""
        styles = {
            'primary': theme['primary'],
            'secondary': theme['secondary'],
            'success': theme['success'],
            'warning': theme['warning'],
            'danger': theme['danger']
        }
        
        color = styles.get(style_type, theme['primary'])
        widget.setStyleSheet(f"""
            background-color: {color};
            color: white;
            border-radius: 4px;
            padding: 4px 8px;
            font-weight: bold;
        """)

# Global styling instance
professional_styling = ProfessionalStyling()