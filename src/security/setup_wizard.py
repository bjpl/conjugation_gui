"""
First-Run Setup Wizard for Spanish Conjugation GUI
=================================================

This module provides a comprehensive setup wizard for first-time users,
guiding them through secure API key configuration and initial application setup.

Features:
- Step-by-step guided setup
- API key validation and testing
- Multiple storage option selection
- Configuration import/export
- Security recommendations
- User-friendly error handling and recovery

Author: Brand
Version: 1.0.0
"""

import os
import sys
import json
import logging
from typing import Dict, Optional, Any, List, Callable
from pathlib import Path

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import (
    QApplication, QDialog, QWizard, QWizardPage, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox, QCheckBox,
    QProgressBar, QGroupBox, QRadioButton, QButtonGroup, QMessageBox,
    QFileDialog, QStackedWidget, QFormLayout, QScrollArea, QFrame,
    QSpacerItem, QSizePolicy, QTabWidget, QPlainTextEdit
)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPalette

from .credentials_manager import CredentialsManager, CredentialsError
from .api_config import APIConfig, ConfigError


class ValidationWorker(QThread):
    """Worker thread for API key validation and testing."""
    
    validation_complete = pyqtSignal(dict)
    progress_update = pyqtSignal(str, int)
    
    def __init__(self, api_config: APIConfig, api_key: str, provider: str):
        super().__init__()
        self.api_config = api_config
        self.api_key = api_key
        self.provider = provider
    
    def run(self):
        """Run validation in background."""
        try:
            # Step 1: Basic validation
            self.progress_update.emit("Validating API key format...", 25)
            validation_result = self.api_config.validate_api_key(self.api_key, self.provider)
            
            if not validation_result['valid']:
                self.validation_complete.emit({
                    'success': False,
                    'step': 'validation',
                    'result': validation_result
                })
                return
            
            # Step 2: API test
            self.progress_update.emit("Testing API connection...", 75)
            test_result = self.api_config.test_api_key(self.api_key, self.provider)
            
            # Step 3: Complete
            self.progress_update.emit("Validation complete!", 100)
            
            self.validation_complete.emit({
                'success': test_result['success'],
                'step': 'test',
                'validation': validation_result,
                'test': test_result
            })
            
        except Exception as e:
            self.validation_complete.emit({
                'success': False,
                'step': 'error',
                'error': str(e)
            })


class WelcomePage(QWizardPage):
    """Welcome page for the setup wizard."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Welcome to Spanish Conjugation GUI")
        self.setSubTitle("Let's set up your application for the first time")
        
        layout = QVBoxLayout()
        
        # Welcome message
        welcome_text = QLabel("""
        <h2>Welcome!</h2>
        <p>This wizard will guide you through setting up your Spanish Conjugation Practice application.</p>
        <p>We'll help you:</p>
        <ul>
        <li><b>Configure your API key securely</b> - Your API key will be stored using your system's secure keyring</li>
        <li><b>Choose your preferences</b> - Customize the app to your learning style</li>
        <li><b>Test your setup</b> - Ensure everything works before you start practicing</li>
        </ul>
        <p>This setup takes about 2-3 minutes and you only need to do it once.</p>
        """)
        welcome_text.setWordWrap(True)
        layout.addWidget(welcome_text)
        
        # Security note
        security_frame = QFrame()
        security_frame.setFrameStyle(QFrame.Box)
        security_frame.setStyleSheet("background-color: #e8f4f8; padding: 10px; border: 1px solid #bee5eb;")
        security_layout = QHBoxLayout(security_frame)
        
        security_icon = QLabel("🔒")
        security_icon.setFont(QFont("Arial", 16))
        security_text = QLabel("""
        <b>Security First:</b> Your API key will be stored securely using your operating system's
        built-in credential management. We never store your API key in plain text files.
        """)
        security_text.setWordWrap(True)
        
        security_layout.addWidget(security_icon)
        security_layout.addWidget(security_text)
        layout.addWidget(security_frame)
        
        layout.addStretch()
        
        # App info
        info_text = QLabel("<small>Spanish Conjugation GUI v1.0 - Secure API Configuration</small>")
        info_text.setAlignment(Qt.AlignCenter)
        info_text.setStyleSheet("color: #666;")
        layout.addWidget(info_text)
        
        self.setLayout(layout)


class APIProviderPage(QWizardPage):
    """API provider selection page."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Choose Your AI Provider")
        self.setSubTitle("Select which AI service you'd like to use for exercise generation")
        
        layout = QVBoxLayout()
        
        # Provider selection
        provider_group = QGroupBox("Available Providers")
        provider_layout = QVBoxLayout()
        
        self.provider_group = QButtonGroup()
        
        # OpenAI option
        openai_radio = QRadioButton("OpenAI (GPT-4o)")
        openai_radio.setChecked(True)
        openai_info = QLabel("""
        <b>Recommended for most users</b><br>
        • Excellent Spanish language support<br>
        • High-quality, contextual exercises<br>
        • Reliable and fast responses<br>
        • Requires OpenAI API key (pay-per-use)
        """)
        openai_info.setContentsMargins(30, 0, 0, 10)
        openai_info.setStyleSheet("color: #555;")
        
        self.provider_group.addButton(openai_radio, 0)
        provider_layout.addWidget(openai_radio)
        provider_layout.addWidget(openai_info)
        
        # Future providers (placeholder)
        other_radio = QRadioButton("Other Providers (Coming Soon)")
        other_radio.setEnabled(False)
        other_info = QLabel("""
        Support for additional AI providers like Anthropic Claude, 
        Google Gemini, and local models will be added in future updates.
        """)
        other_info.setContentsMargins(30, 0, 0, 10)
        other_info.setStyleSheet("color: #999;")
        
        self.provider_group.addButton(other_radio, 1)
        provider_layout.addWidget(other_radio)
        provider_layout.addWidget(other_info)
        
        provider_group.setLayout(provider_layout)
        layout.addWidget(provider_group)
        
        # Offline mode option
        offline_group = QGroupBox("Offline Mode")
        offline_layout = QVBoxLayout()
        
        self.offline_checkbox = QCheckBox("Enable offline mode for basic practice")
        offline_description = QLabel("""
        When enabled, you can practice with pre-built exercises even without an internet connection
        or API key. Online mode with AI-generated exercises will still be available when configured.
        """)
        offline_description.setWordWrap(True)
        offline_description.setStyleSheet("color: #555;")
        
        offline_layout.addWidget(self.offline_checkbox)
        offline_layout.addWidget(offline_description)
        offline_group.setLayout(offline_layout)
        layout.addWidget(offline_group)
        
        self.setLayout(layout)
    
    def get_selected_provider(self) -> str:
        """Get the selected API provider."""
        button_id = self.provider_group.checkedId()
        if button_id == 0:
            return "openai"
        else:
            return "other"
    
    def is_offline_enabled(self) -> bool:
        """Check if offline mode is enabled."""
        return self.offline_checkbox.isChecked()


class APIKeyPage(QWizardPage):
    """API key configuration page."""
    
    def __init__(self, api_config: APIConfig):
        super().__init__()
        self.api_config = api_config
        self.setTitle("Configure Your API Key")
        self.setSubTitle("Enter your OpenAI API key for AI-powered exercise generation")
        
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel("""
        <h3>Setting up your OpenAI API Key</h3>
        <p>To use AI-powered exercise generation, you'll need an OpenAI API key:</p>
        <ol>
        <li>Go to <a href="https://platform.openai.com/api-keys">platform.openai.com/api-keys</a></li>
        <li>Sign up or log in to your OpenAI account</li>
        <li>Click "Create new secret key"</li>
        <li>Copy the key and paste it below</li>
        </ol>
        <p><b>Note:</b> You'll need billing set up on your OpenAI account, but usage costs are typically very low 
        (usually under $1 for hundreds of exercises).</p>
        """)
        instructions.setWordWrap(True)
        instructions.setOpenExternalLinks(True)
        layout.addWidget(instructions)
        
        # API key input
        key_group = QGroupBox("API Key Configuration")
        key_layout = QFormLayout()
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("sk-...")
        self.api_key_input.textChanged.connect(self.validate_key_format)
        
        self.show_key_checkbox = QCheckBox("Show API key")
        self.show_key_checkbox.toggled.connect(self.toggle_key_visibility)
        
        key_layout.addRow("API Key:", self.api_key_input)
        key_layout.addRow("", self.show_key_checkbox)
        
        key_group.setLayout(key_layout)
        layout.addWidget(key_group)
        
        # Validation status
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #666;")
        layout.addWidget(self.status_label)
        
        # Test button and progress
        test_layout = QHBoxLayout()
        self.test_button = QPushButton("Test API Key")
        self.test_button.clicked.connect(self.test_api_key)
        self.test_button.setEnabled(False)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        test_layout.addWidget(self.test_button)
        test_layout.addWidget(self.progress_bar)
        test_layout.addStretch()
        
        layout.addLayout(test_layout)
        
        # Results area
        self.results_area = QTextEdit()
        self.results_area.setMaximumHeight(100)
        self.results_area.setVisible(False)
        layout.addWidget(self.results_area)
        
        # Skip option
        skip_frame = QFrame()
        skip_frame.setFrameStyle(QFrame.Box)
        skip_frame.setStyleSheet("background-color: #fff3cd; padding: 10px; border: 1px solid #ffeaa7;")
        skip_layout = QVBoxLayout(skip_frame)
        
        self.skip_checkbox = QCheckBox("Skip API key setup for now (offline mode only)")
        skip_info = QLabel("You can always add your API key later in the application settings.")
        skip_info.setStyleSheet("color: #856404; font-size: 10px;")
        
        skip_layout.addWidget(self.skip_checkbox)
        skip_layout.addWidget(skip_info)
        layout.addWidget(skip_frame)
        
        self.setLayout(layout)
        
        # Validation worker
        self.validation_worker = None
    
    def validate_key_format(self):
        """Validate API key format as user types."""
        key = self.api_key_input.text()
        
        if not key:
            self.status_label.setText("")
            self.test_button.setEnabled(False)
        elif not key.startswith('sk-'):
            self.status_label.setText("❌ OpenAI API keys start with 'sk-'")
            self.status_label.setStyleSheet("color: #dc3545;")
            self.test_button.setEnabled(False)
        elif len(key) < 40:
            self.status_label.setText("⚠️ API key appears to be incomplete")
            self.status_label.setStyleSheet("color: #fd7e14;")
            self.test_button.setEnabled(False)
        else:
            self.status_label.setText("✅ API key format looks correct")
            self.status_label.setStyleSheet("color: #28a745;")
            self.test_button.setEnabled(True)
    
    def toggle_key_visibility(self, show: bool):
        """Toggle API key visibility."""
        if show:
            self.api_key_input.setEchoMode(QLineEdit.Normal)
        else:
            self.api_key_input.setEchoMode(QLineEdit.Password)
    
    def test_api_key(self):
        """Test the API key in a background thread."""
        api_key = self.api_key_input.text()
        
        if not api_key:
            return
        
        # Start validation
        self.test_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.results_area.setVisible(False)
        
        # Create and start worker thread
        self.validation_worker = ValidationWorker(self.api_config, api_key, "openai")
        self.validation_worker.validation_complete.connect(self.handle_validation_result)
        self.validation_worker.progress_update.connect(self.update_progress)
        self.validation_worker.start()
    
    def update_progress(self, message: str, progress: int):
        """Update progress bar and status."""
        self.progress_bar.setValue(progress)
        self.status_label.setText(message)
    
    def handle_validation_result(self, result: Dict[str, Any]):
        """Handle validation result from worker thread."""
        self.progress_bar.setVisible(False)
        self.test_button.setEnabled(True)
        self.results_area.setVisible(True)
        
        if result['success']:
            self.status_label.setText("✅ API key is valid and working!")
            self.status_label.setStyleSheet("color: #28a745;")
            
            # Show success info
            validation = result.get('validation', {})
            test = result.get('test', {})
            
            info_text = "🎉 <b>Success!</b><br><br>"
            info_text += f"• API key validated: {validation.get('info', {}).get('type', 'OpenAI API Key')}<br>"
            info_text += f"• Connection test: Passed<br>"
            info_text += f"• Model access: {test.get('info', {}).get('model_used', 'Confirmed')}<br>"
            info_text += "<br>Your API key will be stored securely."
            
            self.results_area.setHtml(info_text)
            self.results_area.setStyleSheet("background-color: #d4edda; border: 1px solid #c3e6cb;")
            
        else:
            self.status_label.setText("❌ API key validation failed")
            self.status_label.setStyleSheet("color: #dc3545;")
            
            # Show error info
            error_text = "❌ <b>Validation Failed</b><br><br>"
            
            if result['step'] == 'validation':
                validation = result['result']
                for error in validation.get('errors', []):
                    error_text += f"• {error}<br>"
                for warning in validation.get('warnings', []):
                    error_text += f"⚠️ {warning}<br>"
            elif result['step'] == 'test':
                test = result.get('test', {})
                error_text += f"• API Test Error: {test.get('error', 'Unknown error')}<br>"
            else:
                error_text += f"• Error: {result.get('error', 'Unknown error')}<br>"
            
            error_text += "<br>Please check your API key and try again."
            
            self.results_area.setHtml(error_text)
            self.results_area.setStyleSheet("background-color: #f8d7da; border: 1px solid #f5c6cb;")
        
        # Store result for wizard
        self.validation_result = result
    
    def get_api_key(self) -> Optional[str]:
        """Get the entered API key."""
        if self.skip_checkbox.isChecked():
            return None
        return self.api_key_input.text() or None
    
    def is_valid(self) -> bool:
        """Check if the page is valid."""
        if self.skip_checkbox.isChecked():
            return True
        
        key = self.api_key_input.text()
        if not key:
            return False
        
        # Check if we have a successful validation
        return hasattr(self, 'validation_result') and self.validation_result.get('success', False)


class SecurityPage(QWizardPage):
    """Security and storage options page."""
    
    def __init__(self, credentials_manager: CredentialsManager):
        super().__init__()
        self.credentials_manager = credentials_manager
        self.setTitle("Security Configuration")
        self.setSubTitle("Choose how to store your credentials securely")
        
        layout = QVBoxLayout()
        
        # Storage method selection
        storage_group = QGroupBox("Credential Storage Method")
        storage_layout = QVBoxLayout()
        
        self.storage_group = QButtonGroup()
        
        # Get available methods
        storage_info = credentials_manager.get_storage_info()
        
        # Keyring option
        keyring_radio = QRadioButton("System Keyring (Recommended)")
        keyring_radio.setChecked(storage_info['keyring_available'])
        keyring_info = QLabel("""
        <b>Most Secure:</b> Uses your operating system's built-in credential manager<br>
        • Windows: Windows Credential Manager<br>
        • macOS: Keychain<br>
        • Linux: Secret Service (GNOME Keyring, KWallet)
        """)
        keyring_info.setContentsMargins(30, 0, 0, 10)
        keyring_info.setStyleSheet("color: #555;")
        
        if not storage_info['keyring_available']:
            keyring_radio.setEnabled(False)
            keyring_info.setText("<b>⚠️ Not Available:</b> System keyring service not found")
            keyring_info.setStyleSheet("color: #dc3545;")
        
        self.storage_group.addButton(keyring_radio, 0)
        storage_layout.addWidget(keyring_radio)
        storage_layout.addWidget(keyring_info)
        
        # Encrypted file option
        encrypted_radio = QRadioButton("Encrypted File Storage")
        encrypted_radio.setChecked(not storage_info['keyring_available'] and storage_info['encryption_available'])
        encrypted_info = QLabel("""
        <b>Secure Alternative:</b> Stores credentials in an encrypted file<br>
        • Uses AES-256 encryption<br>
        • Protected by master password or key<br>
        • Stored in your user configuration directory
        """)
        encrypted_info.setContentsMargins(30, 0, 0, 10)
        encrypted_info.setStyleSheet("color: #555;")
        
        if not storage_info['encryption_available']:
            encrypted_radio.setEnabled(False)
            encrypted_info.setText("<b>⚠️ Not Available:</b> Cryptography library not installed")
            encrypted_info.setStyleSheet("color: #dc3545;")
        
        self.storage_group.addButton(encrypted_radio, 1)
        storage_layout.addWidget(encrypted_radio)
        storage_layout.addWidget(encrypted_info)
        
        # Environment only option
        env_radio = QRadioButton("Environment Variables Only")
        env_info = QLabel("""
        <b>Manual Setup Required:</b> You'll need to set environment variables yourself<br>
        • Set OPENAI_API_KEY in your system environment<br>
        • Less convenient but works on all systems<br>
        • API key stored in plain text environment
        """)
        env_info.setContentsMargins(30, 0, 0, 10)
        env_info.setStyleSheet("color: #fd7e14;")
        
        self.storage_group.addButton(env_radio, 2)
        storage_layout.addWidget(env_radio)
        storage_layout.addWidget(env_info)
        
        storage_group.setLayout(storage_layout)
        layout.addWidget(storage_group)
        
        # Additional security options
        extra_group = QGroupBox("Additional Security Options")
        extra_layout = QVBoxLayout()
        
        self.validate_keys_checkbox = QCheckBox("Validate API keys before storing")
        self.validate_keys_checkbox.setChecked(True)
        self.validate_keys_checkbox.setToolTip("Check API key format and test connection before saving")
        
        self.backup_checkbox = QCheckBox("Create configuration backups")
        self.backup_checkbox.setChecked(True)
        self.backup_checkbox.setToolTip("Automatically backup your configuration periodically")
        
        self.audit_log_checkbox = QCheckBox("Enable security audit logging")
        self.audit_log_checkbox.setChecked(True)
        self.audit_log_checkbox.setToolTip("Log security-related events for monitoring")
        
        extra_layout.addWidget(self.validate_keys_checkbox)
        extra_layout.addWidget(self.backup_checkbox)
        extra_layout.addWidget(self.audit_log_checkbox)
        
        extra_group.setLayout(extra_layout)
        layout.addWidget(extra_group)
        
        # Storage info display
        info_group = QGroupBox("System Information")
        info_layout = QFormLayout()
        
        config_dir = QLabel(str(credentials_manager.config_dir))
        config_dir.setStyleSheet("font-family: monospace; font-size: 9px;")
        
        backend_name = storage_info.get('keyring_backend', 'Not available')
        backend_label = QLabel(backend_name)
        
        info_layout.addRow("Configuration Directory:", config_dir)
        info_layout.addRow("Keyring Backend:", backend_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        self.setLayout(layout)
    
    def get_storage_method(self) -> str:
        """Get selected storage method."""
        button_id = self.storage_group.checkedId()
        if button_id == 0:
            return "keyring"
        elif button_id == 1:
            return "encrypted_file"
        else:
            return "environment"
    
    def get_security_options(self) -> Dict[str, bool]:
        """Get security option settings."""
        return {
            "validate_api_keys": self.validate_keys_checkbox.isChecked(),
            "backup_enabled": self.backup_checkbox.isChecked(),
            "audit_logging": self.audit_log_checkbox.isChecked()
        }


class PreferencesPage(QWizardPage):
    """User preferences configuration page."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Application Preferences")
        self.setSubTitle("Customize the application to your learning style")
        
        # Create scroll area for preferences
        scroll = QScrollArea()
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        
        # Learning preferences
        learning_group = QGroupBox("Learning Preferences")
        learning_layout = QFormLayout()
        
        self.exercise_count_spin = QComboBox()
        self.exercise_count_spin.addItems(["3", "5", "7", "10", "15", "20"])
        self.exercise_count_spin.setCurrentText("5")
        
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["Beginner", "Intermediate", "Advanced", "Mixed"])
        self.difficulty_combo.setCurrentText("Intermediate")
        
        self.strictness_combo = QComboBox()
        self.strictness_combo.addItems(["Lenient", "Normal", "Strict"])
        self.strictness_combo.setCurrentText("Normal")
        self.strictness_combo.setToolTip(
            "Lenient: Accepts close answers\n"
            "Normal: Standard matching\n"
            "Strict: Exact matches only"
        )
        
        learning_layout.addRow("Exercises per session:", self.exercise_count_spin)
        learning_layout.addRow("Default difficulty:", self.difficulty_combo)
        learning_layout.addRow("Answer checking:", self.strictness_combo)
        
        learning_group.setLayout(learning_layout)
        layout.addWidget(learning_group)
        
        # Interface preferences
        interface_group = QGroupBox("Interface Preferences")
        interface_layout = QVBoxLayout()
        
        self.dark_mode_checkbox = QCheckBox("Use dark theme")
        self.translations_checkbox = QCheckBox("Show English translations")
        self.translations_checkbox.setToolTip("Display English translations alongside Spanish exercises")
        
        self.offline_mode_checkbox = QCheckBox("Enable offline mode")
        self.offline_mode_checkbox.setChecked(True)
        self.offline_mode_checkbox.setToolTip("Allow practice with built-in exercises when no internet connection")
        
        interface_layout.addWidget(self.dark_mode_checkbox)
        interface_layout.addWidget(self.translations_checkbox)
        interface_layout.addWidget(self.offline_mode_checkbox)
        
        interface_group.setLayout(interface_layout)
        layout.addWidget(interface_group)
        
        # Practice options
        practice_group = QGroupBox("Practice Options")
        practice_layout = QVBoxLayout()
        
        self.tense_checkboxes = {}
        tense_frame = QFrame()
        tense_layout = QHBoxLayout(tense_frame)
        tense_layout.addWidget(QLabel("Default tenses:"))
        
        for tense in ["Present", "Preterite", "Imperfect", "Future"]:
            cb = QCheckBox(tense)
            if tense in ["Present", "Preterite"]:
                cb.setChecked(True)
            self.tense_checkboxes[tense] = cb
            tense_layout.addWidget(cb)
        
        self.person_checkboxes = {}
        person_frame = QFrame()
        person_layout = QHBoxLayout(person_frame)
        person_layout.addWidget(QLabel("Default persons:"))
        
        for person in ["1st sg", "2nd sg", "3rd sg", "1st pl", "2nd pl", "3rd pl"]:
            cb = QCheckBox(person)
            if person in ["1st sg", "3rd sg"]:
                cb.setChecked(True)
            self.person_checkboxes[person] = cb
            person_layout.addWidget(cb)
        
        practice_layout.addWidget(tense_frame)
        practice_layout.addWidget(person_frame)
        
        practice_group.setLayout(practice_layout)
        layout.addWidget(practice_group)
        
        # Performance options
        performance_group = QGroupBox("Performance & Data")
        performance_layout = QVBoxLayout()
        
        self.statistics_checkbox = QCheckBox("Track learning statistics")
        self.statistics_checkbox.setChecked(True)
        
        self.cache_exercises_checkbox = QCheckBox("Cache generated exercises")
        self.cache_exercises_checkbox.setChecked(True)
        self.cache_exercises_checkbox.setToolTip("Save generated exercises to reduce API calls")
        
        self.auto_backup_checkbox = QCheckBox("Automatic progress backup")
        self.auto_backup_checkbox.setChecked(True)
        
        performance_layout.addWidget(self.statistics_checkbox)
        performance_layout.addWidget(self.cache_exercises_checkbox)
        performance_layout.addWidget(self.auto_backup_checkbox)
        
        performance_group.setLayout(performance_layout)
        layout.addWidget(performance_group)
        
        scroll.setWidget(scroll_widget)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
    
    def get_preferences(self) -> Dict[str, Any]:
        """Get all preference settings."""
        selected_tenses = [tense for tense, cb in self.tense_checkboxes.items() if cb.isChecked()]
        selected_persons = [person for person, cb in self.person_checkboxes.items() if cb.isChecked()]
        
        return {
            "learning": {
                "exercise_count": int(self.exercise_count_spin.currentText()),
                "difficulty": self.difficulty_combo.currentText().lower(),
                "answer_strictness": self.strictness_combo.currentText().lower(),
                "default_tenses": selected_tenses,
                "default_persons": selected_persons
            },
            "interface": {
                "dark_mode": self.dark_mode_checkbox.isChecked(),
                "show_translations": self.translations_checkbox.isChecked(),
                "offline_mode": self.offline_mode_checkbox.isChecked()
            },
            "performance": {
                "track_statistics": self.statistics_checkbox.isChecked(),
                "cache_exercises": self.cache_exercises_checkbox.isChecked(),
                "auto_backup": self.auto_backup_checkbox.isChecked()
            }
        }


class CompletionPage(QWizardPage):
    """Setup completion and summary page."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Setup Complete!")
        self.setSubTitle("Your Spanish Conjugation GUI is ready to use")
        
        layout = QVBoxLayout()
        
        # Success message
        success_text = QLabel("""
        <h2>🎉 Congratulations!</h2>
        <p>Your Spanish Conjugation Practice application has been successfully configured.</p>
        """)
        success_text.setAlignment(Qt.AlignCenter)
        layout.addWidget(success_text)
        
        # Configuration summary
        self.summary_group = QGroupBox("Configuration Summary")
        self.summary_layout = QFormLayout()
        self.summary_group.setLayout(self.summary_layout)
        layout.addWidget(self.summary_group)
        
        # Next steps
        next_steps = QLabel("""
        <h3>What's Next?</h3>
        <ul>
        <li><b>Start practicing!</b> - Click 'New Exercise' to generate your first practice session</li>
        <li><b>Explore features</b> - Try different modes like Speed Practice, Task Mode, and Story Mode</li>
        <li><b>Track progress</b> - View your statistics and focus on areas that need improvement</li>
        <li><b>Customize further</b> - Adjust settings anytime through the application menu</li>
        </ul>
        """)
        next_steps.setWordWrap(True)
        layout.addWidget(next_steps)
        
        # Tips section
        tips_frame = QFrame()
        tips_frame.setFrameStyle(QFrame.Box)
        tips_frame.setStyleSheet("background-color: #e8f4f8; padding: 15px; border: 1px solid #bee5eb;")
        tips_layout = QVBoxLayout(tips_frame)
        
        tips_title = QLabel("<b>💡 Quick Tips for Effective Practice:</b>")
        tips_list = QLabel("""
        • Start with 5-10 exercises per session to build consistency
        • Focus on one tense at a time when beginning
        • Use Speed Mode to build conversational fluency
        • Enable translations if you're a beginner
        • Review your mistakes regularly in the Statistics view
        """)
        
        tips_layout.addWidget(tips_title)
        tips_layout.addWidget(tips_list)
        layout.addWidget(tips_frame)
        
        # Support section
        support_text = QLabel("""
        <small>
        <b>Need help?</b> Check the Help menu in the application or visit our documentation.<br>
        Your configuration is saved in: <span style="font-family: monospace;">{config_dir}</span>
        </small>
        """)
        support_text.setWordWrap(True)
        support_text.setAlignment(Qt.AlignCenter)
        support_text.setStyleSheet("color: #666;")
        layout.addWidget(support_text)
        
        self.setLayout(layout)
    
    def set_summary(self, summary: Dict[str, Any]):
        """Set the configuration summary."""
        # Clear existing summary
        while self.summary_layout.count():
            child = self.summary_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Add summary items
        if 'api_provider' in summary:
            provider = summary['api_provider'].title()
            if summary.get('api_configured'):
                status = f"{provider} (✅ Configured)"
            else:
                status = f"{provider} (⚠️ Offline mode only)"
            self.summary_layout.addRow("API Provider:", QLabel(status))
        
        if 'storage_method' in summary:
            method = summary['storage_method'].replace('_', ' ').title()
            self.summary_layout.addRow("Storage Method:", QLabel(method))
        
        if 'preferences' in summary:
            prefs = summary['preferences']
            self.summary_layout.addRow("Exercise Count:", QLabel(str(prefs.get('exercise_count', 5))))
            self.summary_layout.addRow("Difficulty:", QLabel(prefs.get('difficulty', 'Intermediate').title()))
            
            features = []
            if prefs.get('dark_mode'):
                features.append("Dark Mode")
            if prefs.get('offline_mode'):
                features.append("Offline Mode")
            if prefs.get('show_translations'):
                features.append("Translations")
            
            if features:
                self.summary_layout.addRow("Features:", QLabel(", ".join(features)))
        
        # Update support text with actual config directory
        if 'config_dir' in summary:
            for i in range(self.layout().count()):
                widget = self.layout().itemAt(i).widget()
                if isinstance(widget, QLabel) and 'config_dir' in widget.text():
                    widget.setText(widget.text().format(config_dir=summary['config_dir']))


class SetupWizard(QWizard):
    """Main setup wizard for first-run configuration."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Spanish Conjugation GUI - Setup Wizard")
        self.setWizardStyle(QWizard.ModernStyle)
        self.setPixmap(QWizard.WatermarkPixmap, QPixmap())  # Could add logo here
        
        # Initialize components
        self.api_config = APIConfig()
        self.credentials_manager = self.api_config.credentials_manager
        
        # Set up pages
        self.welcome_page = WelcomePage()
        self.provider_page = APIProviderPage()
        self.api_key_page = APIKeyPage(self.api_config)
        self.security_page = SecurityPage(self.credentials_manager)
        self.preferences_page = PreferencesPage()
        self.completion_page = CompletionPage()
        
        # Add pages
        self.addPage(self.welcome_page)
        self.addPage(self.provider_page)
        self.addPage(self.api_key_page)
        self.addPage(self.security_page)
        self.addPage(self.preferences_page)
        self.addPage(self.completion_page)
        
        # Connect signals
        self.currentIdChanged.connect(self.page_changed)
        
        # Set initial size
        self.resize(700, 500)
    
    def page_changed(self, page_id):
        """Handle page changes."""
        if page_id == self.pageIds()[-1]:  # Completion page
            self.setup_completion_summary()
    
    def setup_completion_summary(self):
        """Set up the completion page summary."""
        summary = {
            'api_provider': self.provider_page.get_selected_provider(),
            'api_configured': bool(self.api_key_page.get_api_key()),
            'storage_method': self.security_page.get_storage_method(),
            'preferences': self.preferences_page.get_preferences(),
            'config_dir': str(self.credentials_manager.config_dir)
        }
        
        # Flatten preferences for display
        prefs = summary['preferences']
        flat_prefs = {}
        for category, settings in prefs.items():
            flat_prefs.update(settings)
        summary['preferences'] = flat_prefs
        
        self.completion_page.set_summary(summary)
    
    def accept(self):
        """Handle wizard completion."""
        try:
            # Save API key if provided
            api_key = self.api_key_page.get_api_key()
            if api_key:
                provider = self.provider_page.get_selected_provider()
                storage_method = self.security_page.get_storage_method()
                
                # Set storage preference
                self.api_config.set('security.storage_preference', storage_method)
                
                # Store the API key
                success = self.api_config.set_api_key(api_key, provider)
                if not success:
                    QMessageBox.warning(self, "Storage Error", 
                                       "Failed to store API key. Please check your configuration.")
                    return
            
            # Save security options
            security_opts = self.security_page.get_security_options()
            for key, value in security_opts.items():
                self.api_config.set(f'security.{key}', value)
            
            # Save preferences
            preferences = self.preferences_page.get_preferences()
            for category, settings in preferences.items():
                for key, value in settings.items():
                    self.api_config.set(f'{category}.{key}', value)
            
            # Save configuration
            self.api_config.save_config()
            
            # Mark setup as complete
            self.api_config.set('setup.completed', True)
            self.api_config.set('setup.completed_at', datetime.now().isoformat())
            self.api_config.set('setup.wizard_version', '1.0')
            
            super().accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Setup Error", 
                               f"An error occurred during setup: {str(e)}")


def run_setup_wizard(parent=None) -> bool:
    """
    Run the setup wizard.
    
    Args:
        parent: Parent widget
        
    Returns:
        True if setup was completed successfully
    """
    wizard = SetupWizard(parent)
    result = wizard.exec_()
    
    return result == QDialog.Accepted


def check_first_run(app_name: str = "SpanishConjugationGUI") -> bool:
    """
    Check if this is the first run of the application.
    
    Args:
        app_name: Application name
        
    Returns:
        True if this is the first run
    """
    try:
        api_config = APIConfig(app_name)
        return not api_config.get('setup.completed', False)
    except:
        return True


if __name__ == "__main__":
    # Test the setup wizard
    app = QApplication(sys.argv)
    
    if run_setup_wizard():
        print("Setup completed successfully!")
    else:
        print("Setup cancelled or failed.")
    
    sys.exit(0)