"""
Setup Wizard for First-Run Configuration
"""

import os
import sys
from typing import Optional
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QCheckBox, QGroupBox, QRadioButton, QButtonGroup,
    QProgressBar, QTextEdit, QStackedWidget, QFrame, QMessageBox,
    QFileDialog, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QPalette

class WelcomePage(QFrame):
    """Welcome page of setup wizard"""
    
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Welcome to Spanish Conjugation Trainer")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin: 20px;")
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Professional Language Learning Made Easy")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Arial", 14))
        subtitle.setStyleSheet("color: #7f8c8d; margin-bottom: 30px;")
        layout.addWidget(subtitle)
        
        # Features list
        features_group = QGroupBox("What You'll Get:")
        features_layout = QVBoxLayout(features_group)
        
        features = [
            "🎯 AI-Powered Conjugation Practice",
            "📊 Progress Tracking & Analytics", 
            "⚡ Speed Mode for Conversational Fluency",
            "🎨 Customizable Practice Sessions",
            "📝 Task-Based Real-World Scenarios",
            "🌙 Dark Mode Support"
        ]
        
        for feature in features:
            label = QLabel(feature)
            label.setFont(QFont("Arial", 12))
            label.setStyleSheet("padding: 5px; color: #34495e;")
            features_layout.addWidget(label)
        
        layout.addWidget(features_group)
        
        # Footer
        footer = QLabel("This wizard will help you configure your learning experience")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #95a5a6; font-style: italic;")
        layout.addWidget(footer)
        
        layout.addStretch()

class APIConfigPage(QFrame):
    """API Configuration page"""
    
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("AI Assistant Configuration")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # API Key section
        api_group = QGroupBox("OpenAI API Configuration")
        api_layout = QVBoxLayout(api_group)
        
        # Instructions
        instructions = QLabel(
            "To enable AI-powered explanations and exercise generation, "
            "you'll need an OpenAI API key. Don't worry - you can skip this "
            "and use offline mode if preferred."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #7f8c8d; margin-bottom: 10px;")
        api_layout.addWidget(instructions)
        
        # API Key input
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("sk-...")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        key_layout.addWidget(self.api_key_input)
        
        # Show/Hide button
        self.show_key_btn = QPushButton("Show")
        self.show_key_btn.clicked.connect(self.toggleKeyVisibility)
        key_layout.addWidget(self.show_key_btn)
        
        api_layout.addLayout(key_layout)
        
        # Test button
        self.test_btn = QPushButton("Test Connection")
        self.test_btn.clicked.connect(self.testAPIKey)
        api_layout.addWidget(self.test_btn)
        
        # Status label
        self.status_label = QLabel("")
        api_layout.addWidget(self.status_label)
        
        layout.addWidget(api_group)
        
        # Model selection
        model_group = QGroupBox("AI Model Selection")
        model_layout = QVBoxLayout(model_group)
        
        model_layout.addWidget(QLabel("Choose your preferred AI model:"))
        
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "gpt-4o (Recommended - Most Accurate)",
            "gpt-4 (High Quality)",
            "gpt-3.5-turbo (Fast & Economical)"
        ])
        model_layout.addWidget(self.model_combo)
        
        layout.addWidget(model_group)
        
        # Offline option
        offline_group = QGroupBox("Offline Mode")
        offline_layout = QVBoxLayout(offline_group)
        
        self.offline_checkbox = QCheckBox("Start in offline mode (no AI features)")
        offline_layout.addWidget(self.offline_checkbox)
        
        offline_desc = QLabel(
            "Offline mode uses local exercise generation. You can always "
            "switch to online mode later from the settings."
        )
        offline_desc.setWordWrap(True)
        offline_desc.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        offline_layout.addWidget(offline_desc)
        
        layout.addWidget(offline_group)
        
        layout.addStretch()
    
    def toggleKeyVisibility(self):
        if self.api_key_input.echoMode() == QLineEdit.Password:
            self.api_key_input.setEchoMode(QLineEdit.Normal)
            self.show_key_btn.setText("Hide")
        else:
            self.api_key_input.setEchoMode(QLineEdit.Password)
            self.show_key_btn.setText("Show")
    
    def testAPIKey(self):
        # Simple API key validation
        api_key = self.api_key_input.text().strip()
        if not api_key:
            self.status_label.setText("❌ Please enter an API key")
            self.status_label.setStyleSheet("color: #e74c3c;")
            return
        
        if not api_key.startswith("sk-"):
            self.status_label.setText("❌ Invalid API key format")
            self.status_label.setStyleSheet("color: #e74c3c;")
            return
        
        # In a real implementation, you'd test the actual API
        self.status_label.setText("✅ API key format looks correct")
        self.status_label.setStyleSheet("color: #27ae60;")
    
    def getConfiguration(self):
        """Get the API configuration"""
        model_text = self.model_combo.currentText()
        model = "gpt-4o"
        if "gpt-4" in model_text and "gpt-4o" not in model_text:
            model = "gpt-4"
        elif "gpt-3.5-turbo" in model_text:
            model = "gpt-3.5-turbo"
        
        return {
            "api_key": self.api_key_input.text().strip(),
            "model": model,
            "offline_mode": self.offline_checkbox.isChecked()
        }

class PreferencesPage(QFrame):
    """Learning preferences configuration"""
    
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Learning Preferences")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Appearance
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QVBoxLayout(appearance_group)
        
        self.dark_mode_checkbox = QCheckBox("Enable dark mode")
        appearance_layout.addWidget(self.dark_mode_checkbox)
        
        self.show_translations_checkbox = QCheckBox("Show English translations by default")
        self.show_translations_checkbox.setChecked(True)
        appearance_layout.addWidget(self.show_translations_checkbox)
        
        layout.addWidget(appearance_group)
        
        # Learning settings
        learning_group = QGroupBox("Learning Settings")
        learning_layout = QVBoxLayout(learning_group)
        
        # Difficulty
        diff_layout = QHBoxLayout()
        diff_layout.addWidget(QLabel("Default difficulty:"))
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["Beginner", "Intermediate", "Advanced"])
        self.difficulty_combo.setCurrentText("Intermediate")
        diff_layout.addWidget(self.difficulty_combo)
        learning_layout.addLayout(diff_layout)
        
        # Exercise count
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("Exercises per session:"))
        self.exercise_count_combo = QComboBox()
        self.exercise_count_combo.addItems(["3", "5", "8", "10", "15", "20"])
        self.exercise_count_combo.setCurrentText("5")
        count_layout.addWidget(self.exercise_count_combo)
        learning_layout.addLayout(count_layout)
        
        # Answer strictness
        strict_layout = QHBoxLayout()
        strict_layout.addWidget(QLabel("Answer checking:"))
        self.strictness_combo = QComboBox()
        self.strictness_combo.addItems([
            "Lenient (typos allowed)",
            "Normal (accent flexible)", 
            "Strict (exact match)"
        ])
        self.strictness_combo.setCurrentText("Normal (accent flexible)")
        strict_layout.addWidget(self.strictness_combo)
        learning_layout.addLayout(strict_layout)
        
        layout.addWidget(learning_group)
        
        # Focus areas
        focus_group = QGroupBox("Focus Areas")
        focus_layout = QVBoxLayout(focus_group)
        
        focus_layout.addWidget(QLabel("Which tenses would you like to focus on initially?"))
        
        self.tense_checkboxes = {}
        tenses = ["Present", "Preterite", "Imperfect", "Future", "Conditional", "Subjunctive"]
        
        for tense in tenses:
            cb = QCheckBox(tense)
            if tense in ["Present", "Preterite"]:  # Default selections
                cb.setChecked(True)
            self.tense_checkboxes[tense] = cb
            focus_layout.addWidget(cb)
        
        layout.addWidget(focus_group)
        
        layout.addStretch()
    
    def getPreferences(self):
        """Get user preferences"""
        strictness_map = {
            "Lenient (typos allowed)": "lenient",
            "Normal (accent flexible)": "normal",
            "Strict (exact match)": "strict"
        }
        
        selected_tenses = [
            tense for tense, cb in self.tense_checkboxes.items() 
            if cb.isChecked()
        ]
        
        return {
            "dark_mode": self.dark_mode_checkbox.isChecked(),
            "show_translation": self.show_translations_checkbox.isChecked(),
            "difficulty": self.difficulty_combo.currentText().lower(),
            "exercise_count": int(self.exercise_count_combo.currentText()),
            "answer_strictness": strictness_map[self.strictness_combo.currentText()],
            "preferred_tenses": selected_tenses
        }

class CompletionPage(QFrame):
    """Setup completion page"""
    
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Success icon (text-based)
        success_label = QLabel("🎉")
        success_label.setAlignment(Qt.AlignCenter)
        success_label.setFont(QFont("Arial", 48))
        layout.addWidget(success_label)
        
        # Title
        title = QLabel("Setup Complete!")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: #27ae60; margin: 20px;")
        layout.addWidget(title)
        
        # Message
        message = QLabel(
            "Your Spanish Conjugation Trainer is now ready to use!\n\n"
            "You can always change these settings later from the\n"
            "Settings menu in the main application."
        )
        message.setAlignment(Qt.AlignCenter)
        message.setFont(QFont("Arial", 12))
        message.setStyleSheet("color: #34495e; line-height: 1.4;")
        layout.addWidget(message)
        
        # Tips
        tips_group = QGroupBox("💡 Quick Tips to Get Started")
        tips_layout = QVBoxLayout(tips_group)
        
        tips = [
            "Click 'New Exercise' to generate your first practice session",
            "Try Speed Mode (⚡) to build conversational fluency",
            "Use Task Mode for real-world scenarios",
            "Check your progress in the Statistics view"
        ]
        
        for tip in tips:
            label = QLabel(f"• {tip}")
            label.setStyleSheet("padding: 3px; color: #2c3e50;")
            tips_layout.addWidget(label)
        
        layout.addWidget(tips_group)
        
        layout.addStretch()

class SetupWizard(QDialog):
    """Main setup wizard dialog"""
    
    configuration_complete = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Setup Wizard - Spanish Conjugation Trainer")
        self.setFixedSize(700, 550)
        self.setWindowFlags(Qt.Dialog | Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
        
        # Store configuration
        self.config = {}
        
        self.initUI()
        self.applyProfessionalStyling()
    
    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(4)
        self.progress_bar.setValue(1)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #ecf0f1;
                height: 6px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
            }
        """)
        main_layout.addWidget(self.progress_bar)
        
        # Content area
        self.stacked_widget = QStackedWidget()
        
        # Add pages
        self.welcome_page = WelcomePage()
        self.api_page = APIConfigPage()
        self.preferences_page = PreferencesPage()
        self.completion_page = CompletionPage()
        
        self.stacked_widget.addWidget(self.welcome_page)
        self.stacked_widget.addWidget(self.api_page)
        self.stacked_widget.addWidget(self.preferences_page)
        self.stacked_widget.addWidget(self.completion_page)
        
        main_layout.addWidget(self.stacked_widget)
        
        # Navigation buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(20, 10, 20, 20)
        
        self.back_btn = QPushButton("Back")
        self.back_btn.clicked.connect(self.goBack)
        self.back_btn.setEnabled(False)
        
        button_layout.addWidget(self.back_btn)
        button_layout.addStretch()
        
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.goNext)
        self.next_btn.setDefault(True)
        
        self.finish_btn = QPushButton("Finish")
        self.finish_btn.clicked.connect(self.finish)
        self.finish_btn.setVisible(False)
        
        button_layout.addWidget(self.next_btn)
        button_layout.addWidget(self.finish_btn)
        
        main_layout.addLayout(button_layout)
        
        self.current_page = 0
        self.updateNavigationButtons()
    
    def applyProfessionalStyling(self):
        """Apply professional styling to the wizard"""
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2c3e50;
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
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
            QLineEdit, QComboBox {
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                padding: 6px;
                font-size: 12px;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #3498db;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 2px solid #bdc3c7;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border-color: #3498db;
            }
        """)
    
    def goNext(self):
        """Go to next page"""
        if self.current_page < 3:
            self.current_page += 1
            self.stacked_widget.setCurrentIndex(self.current_page)
            self.progress_bar.setValue(self.current_page + 1)
            self.updateNavigationButtons()
    
    def goBack(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.stacked_widget.setCurrentIndex(self.current_page)
            self.progress_bar.setValue(self.current_page + 1)
            self.updateNavigationButtons()
    
    def updateNavigationButtons(self):
        """Update navigation button states"""
        self.back_btn.setEnabled(self.current_page > 0)
        
        if self.current_page == 3:  # Completion page
            self.next_btn.setVisible(False)
            self.finish_btn.setVisible(True)
            self.finish_btn.setDefault(True)
        else:
            self.next_btn.setVisible(True)
            self.finish_btn.setVisible(False)
            self.next_btn.setDefault(True)
    
    def finish(self):
        """Complete setup and emit configuration"""
        # Gather all configuration
        api_config = self.api_page.getConfiguration()
        preferences = self.preferences_page.getPreferences()
        
        self.config.update(api_config)
        self.config.update(preferences)
        
        # Mark setup as complete
        self.config["setup_complete"] = True
        
        self.configuration_complete.emit(self.config)
        self.accept()
    
    @staticmethod
    def runSetup(parent=None):
        """Static method to run the setup wizard"""
        wizard = SetupWizard(parent)
        return wizard.exec_() == QDialog.Accepted, wizard.config if hasattr(wizard, 'config') else {}