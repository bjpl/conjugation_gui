"""
Professional About Dialog with Version Info and Licenses
"""

import os
import sys
from typing import Dict, Any
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QTabWidget, QWidget, QScrollArea, QFrame,
    QDialogButtonBox, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from PyQt5.QtGui import QFont, QPixmap, QDesktopServices

class AboutTab(QWidget):
    """Main about information tab"""
    
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # App icon and title
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setAlignment(Qt.AlignCenter)
        
        # App icon (text-based for now)
        icon_label = QLabel("🎓")
        icon_label.setFont(QFont("Arial", 48))
        icon_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(icon_label)
        
        # App title
        title_label = QLabel("Spanish Conjugation Trainer")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin: 10px 0;")
        header_layout.addWidget(title_label)
        
        # Version
        version_label = QLabel("Version 2.0.0 Professional")
        version_label.setFont(QFont("Arial", 12))
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #3498db; margin-bottom: 20px;")
        header_layout.addWidget(version_label)
        
        layout.addWidget(header_frame)
        
        # Description
        desc_text = """
        <div style='text-align: center; line-height: 1.6;'>
        <p><strong>Professional Spanish Verb Conjugation Practice</strong></p>
        
        <p>An advanced desktop application designed to help you master Spanish verb conjugations
        through AI-powered exercises, real-world scenarios, and adaptive learning techniques.</p>
        
        <p><strong>Key Features:</strong></p>
        <ul style='text-align: left; margin: 0 40px;'>
        <li>🤖 AI-powered explanations with GPT-4o</li>
        <li>⚡ Speed Mode for conversational fluency</li>
        <li>📊 Advanced progress tracking</li>
        <li>🎯 Task-based learning scenarios</li>
        <li>🌙 Professional dark/light themes</li>
        <li>📝 Custom practice sessions</li>
        <li>🔄 Offline mode capability</li>
        <li>📈 Statistical analysis</li>
        </ul>
        </div>
        """
        
        desc_label = QLabel(desc_text)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #34495e; font-size: 11px;")
        layout.addWidget(desc_label)
        
        # Build info
        build_frame = QFrame()
        build_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        build_layout = QVBoxLayout(build_frame)
        
        build_info = f"""
        <strong>Build Information:</strong><br>
        • Built with PyQt5 and Python {sys.version.split()[0]}<br>
        • Platform: {sys.platform}<br>
        • Architecture: Professional Desktop Edition<br>
        • AI Integration: OpenAI GPT Models<br>
        • Database: SQLite for progress tracking
        """
        
        build_label = QLabel(build_info)
        build_label.setStyleSheet("color: #495057; font-size: 10px;")
        build_layout.addWidget(build_label)
        
        layout.addWidget(build_frame)
        
        layout.addStretch()

class CreditsTab(QWidget):
    """Credits and acknowledgments tab"""
    
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        
        credits_text = """
        <h3 style='color: #2c3e50;'>Development Team</h3>
        
        <p><strong>Lead Developer:</strong><br>
        Brand - Application Architecture & Implementation</p>
        
        <p><strong>AI Integration:</strong><br>
        OpenAI GPT-4o - Intelligent explanations and exercise generation</p>
        
        <h3 style='color: #2c3e50; margin-top: 25px;'>Special Thanks</h3>
        
        <p><strong>Language Expertise:</strong><br>
        Focus on Latin American Spanish (LATAM) usage patterns and authentic expressions</p>
        
        <p><strong>Educational Approach:</strong><br>
        Based on modern language learning methodologies including:</p>
        <ul>
        <li>Task-Based Language Teaching (TBLT)</li>
        <li>Communicative Language Teaching</li>
        <li>Spaced Repetition Systems</li>
        <li>Speed Practice for Fluency Building</li>
        </ul>
        
        <h3 style='color: #2c3e50; margin-top: 25px;'>Third-Party Libraries</h3>
        
        <p><strong>Core Framework:</strong><br>
        PyQt5 - Professional GUI framework</p>
        
        <p><strong>AI Services:</strong><br>
        OpenAI API - GPT-4o, GPT-4, GPT-3.5-turbo models</p>
        
        <p><strong>Database:</strong><br>
        SQLite - Local progress storage</p>
        
        <p><strong>Additional Libraries:</strong></p>
        <ul>
        <li>python-dotenv - Environment configuration</li>
        <li>Pillow - Image processing for icons</li>
        <li>requests - HTTP client</li>
        </ul>
        
        <h3 style='color: #2c3e50; margin-top: 25px;'>Inspiration</h3>
        
        <p>This application was inspired by the need for more effective Spanish conjugation
        practice tools that combine modern AI capabilities with proven language learning
        methodologies. Our goal is to make Spanish verb mastery both efficient and enjoyable.</p>
        """
        
        credits_label = QLabel(credits_text)
        credits_label.setWordWrap(True)
        credits_label.setStyleSheet("color: #34495e; font-size: 11px; line-height: 1.4;")
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(credits_label)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
            QScrollBar:vertical {
                background-color: #f1f3f4;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #c1c8d1;
                border-radius: 6px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a8b2bd;
            }
        """)
        
        layout.addWidget(scroll_area)

class LicenseTab(QWidget):
    """License information tab"""
    
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # License text
        license_text = """
MIT License

Copyright (c) 2024 Spanish Conjugation Trainer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


Third-Party Licenses:

PyQt5:
Licensed under the GPL v3 or commercial license. This application uses PyQt5
under the GPL v3 license for open-source distribution.

OpenAI API:
Usage subject to OpenAI's Terms of Service and API Usage Policies.
Visit: https://openai.com/policies/terms-of-use

SQLite:
SQLite is in the public domain and requires no license.

Additional dependencies may have their own licenses. Please refer to the
individual library documentation for complete license information.

PRIVACY NOTICE:
This application may send text to OpenAI's servers when using AI features.
No personal information is transmitted beyond the practice sentences and
your responses for educational purposes. You can use offline mode to
avoid any external data transmission.
        """
        
        license_edit = QTextEdit()
        license_edit.setPlainText(license_text)
        license_edit.setReadOnly(True)
        license_edit.setFont(QFont("Courier New", 9))
        license_edit.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                color: #495057;
                selection-background-color: #007bff;
                selection-color: white;
            }
        """)
        
        layout.addWidget(license_edit)

class SystemInfoTab(QWidget):
    """System information tab"""
    
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Gather system information
        try:
            import platform
            import PyQt5.QtCore
            
            system_info = f"""
System Information:

Operating System: {platform.system()} {platform.release()}
Architecture: {platform.machine()}
Processor: {platform.processor()}
Python Version: {platform.python_version()}
PyQt5 Version: {PyQt5.QtCore.PYQT_VERSION_STR}
Qt Version: {PyQt5.QtCore.QT_VERSION_STR}

Application Information:

Installation Path: {os.path.dirname(os.path.abspath(__file__))}
Working Directory: {os.getcwd()}
Python Executable: {sys.executable}

Environment:

Platform: {sys.platform}
Encoding: {sys.getdefaultencoding()}
File System Encoding: {sys.getfilesystemencoding()}

Memory Information:

Available: Use Task Manager or Activity Monitor to check system memory
            """
            
        except Exception as e:
            system_info = f"Error gathering system information: {str(e)}"
        
        system_edit = QTextEdit()
        system_edit.setPlainText(system_info)
        system_edit.setReadOnly(True)
        system_edit.setFont(QFont("Courier New", 9))
        system_edit.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                border: 1px solid #34495e;
                color: #ecf0f1;
                selection-background-color: #3498db;
                selection-color: white;
            }
        """)
        
        layout.addWidget(system_edit)

class AboutDialog(QDialog):
    """Professional About Dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About - Spanish Conjugation Trainer")
        self.setFixedSize(550, 450)
        self.setWindowFlags(Qt.Dialog | Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
        
        self.initUI()
        self.applyProfessionalStyling()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.about_tab = AboutTab()
        self.credits_tab = CreditsTab()
        self.license_tab = LicenseTab()
        self.system_tab = SystemInfoTab()
        
        # Add tabs
        self.tab_widget.addTab(self.about_tab, "About")
        self.tab_widget.addTab(self.credits_tab, "Credits")
        self.tab_widget.addTab(self.license_tab, "License")
        self.tab_widget.addTab(self.system_tab, "System")
        
        layout.addWidget(self.tab_widget)
        
        # Button area
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(15, 10, 15, 15)
        
        # Links
        website_btn = QPushButton("🌐 Website")
        website_btn.clicked.connect(self.openWebsite)
        button_layout.addWidget(website_btn)
        
        support_btn = QPushButton("❓ Support")
        support_btn.clicked.connect(self.openSupport)
        button_layout.addWidget(support_btn)
        
        button_layout.addStretch()
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setDefault(True)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def applyProfessionalStyling(self):
        """Apply professional styling"""
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                margin-top: -1px;
                background-color: white;
            }
            QTabBar::tab {
                background: #ecf0f1;
                border: 1px solid #bdc3c7;
                padding: 8px 16px;
                margin-right: 2px;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 1px solid white;
            }
            QTabBar::tab:hover:!selected {
                background: #d5dbdb;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:default {
                background-color: #27ae60;
            }
            QPushButton:default:hover {
                background-color: #229954;
            }
        """)
    
    def openWebsite(self):
        """Open project website"""
        QDesktopServices.openUrl(QUrl("https://github.com/spanish-conjugation-trainer"))
    
    def openSupport(self):
        """Open support page"""
        QDesktopServices.openUrl(QUrl("https://github.com/spanish-conjugation-trainer/issues"))
    
    @staticmethod
    def showAbout(parent=None):
        """Static method to show about dialog"""
        dialog = AboutDialog(parent)
        return dialog.exec_() == QDialog.Accepted