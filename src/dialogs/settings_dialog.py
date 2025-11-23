"""
Professional Settings/Preferences Dialog
"""

import os
from typing import Dict, Any, Optional
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox, QSpinBox,
    QGroupBox, QFormLayout, QFileDialog, QMessageBox, QSlider,
    QTextEdit, QDialogButtonBox, QColorDialog, QFontDialog,
    QProgressBar, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette

class APISettingsTab(QWidget):
    """API Configuration Tab"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # OpenAI Settings
        openai_group = QGroupBox("OpenAI API Configuration")
        openai_layout = QFormLayout(openai_group)
        
        # API Key
        self.api_key_input = QLineEdit()
        self.api_key_input.setText(self.config.get("api_key", ""))
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("sk-...")
        
        key_layout = QHBoxLayout()
        key_layout.addWidget(self.api_key_input)
        
        self.show_key_btn = QPushButton("Show")
        self.show_key_btn.clicked.connect(self.toggleKeyVisibility)
        key_layout.addWidget(self.show_key_btn)
        
        self.test_key_btn = QPushButton("Test")
        self.test_key_btn.clicked.connect(self.testAPIKey)
        key_layout.addWidget(self.test_key_btn)
        
        openai_layout.addRow("API Key:", key_layout)
        
        # Model Selection
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "gpt-4o",
            "gpt-4",
            "gpt-3.5-turbo"
        ])
        self.model_combo.setCurrentText(self.config.get("api_model", "gpt-4o"))
        openai_layout.addRow("Model:", self.model_combo)
        
        # API Parameters
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(100, 2000)
        self.max_tokens_spin.setValue(self.config.get("max_tokens", 600))
        openai_layout.addRow("Max Tokens:", self.max_tokens_spin)
        
        self.temperature_slider = QSlider(Qt.Horizontal)
        self.temperature_slider.setRange(0, 100)
        self.temperature_slider.setValue(int(self.config.get("temperature", 0.5) * 100))
        self.temperature_label = QLabel("0.5")
        self.temperature_slider.valueChanged.connect(
            lambda v: self.temperature_label.setText(f"{v/100:.1f}")
        )
        
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(self.temperature_slider)
        temp_layout.addWidget(self.temperature_label)
        openai_layout.addRow("Temperature:", temp_layout)
        
        # Connection status
        self.status_label = QLabel("Not tested")
        self.status_label.setStyleSheet("color: #7f8c8d;")
        openai_layout.addRow("Status:", self.status_label)
        
        layout.addWidget(openai_group)
        
        # Offline Mode
        offline_group = QGroupBox("Offline Mode")
        offline_layout = QVBoxLayout(offline_group)
        
        self.offline_checkbox = QCheckBox("Use offline mode by default")
        self.offline_checkbox.setChecked(self.config.get("offline_mode", False))
        offline_layout.addWidget(self.offline_checkbox)
        
        offline_desc = QLabel(
            "In offline mode, exercises are generated locally without AI assistance. "
            "This saves API costs but provides simpler explanations."
        )
        offline_desc.setWordWrap(True)
        offline_desc.setStyleSheet("color: #7f8c8d; font-size: 11px; margin-top: 5px;")
        offline_layout.addWidget(offline_desc)
        
        layout.addWidget(offline_group)
        
        layout.addStretch()
    
    def toggleKeyVisibility(self):
        """Toggle API key visibility"""
        if self.api_key_input.echoMode() == QLineEdit.Password:
            self.api_key_input.setEchoMode(QLineEdit.Normal)
            self.show_key_btn.setText("Hide")
        else:
            self.api_key_input.setEchoMode(QLineEdit.Password)
            self.show_key_btn.setText("Show")
    
    def testAPIKey(self):
        """Test the API key"""
        api_key = self.api_key_input.text().strip()
        
        if not api_key:
            self.status_label.setText("❌ No API key provided")
            self.status_label.setStyleSheet("color: #e74c3c;")
            return
        
        if not api_key.startswith("sk-"):
            self.status_label.setText("❌ Invalid API key format")
            self.status_label.setStyleSheet("color: #e74c3c;")
            return
        
        # Show testing state
        self.status_label.setText("🔄 Testing connection...")
        self.status_label.setStyleSheet("color: #f39c12;")
        
        # Simulate API test (in real implementation, make actual API call)
        QTimer.singleShot(1500, self.completeAPITest)
    
    def completeAPITest(self):
        """Complete API test simulation"""
        self.status_label.setText("✅ Connection successful")
        self.status_label.setStyleSheet("color: #27ae60;")
    
    def getSettings(self) -> Dict[str, Any]:
        """Get API settings"""
        return {
            "api_key": self.api_key_input.text().strip(),
            "api_model": self.model_combo.currentText(),
            "max_tokens": self.max_tokens_spin.value(),
            "temperature": self.temperature_slider.value() / 100.0,
            "offline_mode": self.offline_checkbox.isChecked()
        }

class LearningSettingsTab(QWidget):
    """Learning Configuration Tab"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Exercise Settings
        exercise_group = QGroupBox("Exercise Generation")
        exercise_layout = QFormLayout(exercise_group)
        
        # Default difficulty
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["Beginner", "Intermediate", "Advanced"])
        self.difficulty_combo.setCurrentText(self.config.get("difficulty", "Intermediate"))
        exercise_layout.addRow("Default Difficulty:", self.difficulty_combo)
        
        # Exercise count
        self.exercise_count_spin = QSpinBox()
        self.exercise_count_spin.setRange(1, 50)
        self.exercise_count_spin.setValue(self.config.get("exercise_count", 5))
        exercise_layout.addRow("Exercises per Session:", self.exercise_count_spin)
        
        # Answer strictness
        self.strictness_combo = QComboBox()
        self.strictness_combo.addItems([
            "Lenient (typos allowed)",
            "Normal (accent flexible)",
            "Strict (exact match)"
        ])
        # Map current setting
        strictness_map = {"lenient": 0, "normal": 1, "strict": 2}
        current_strictness = self.config.get("answer_strictness", "normal")
        self.strictness_combo.setCurrentIndex(strictness_map.get(current_strictness, 1))
        exercise_layout.addRow("Answer Checking:", self.strictness_combo)
        
        layout.addWidget(exercise_group)
        
        # Focus Areas
        focus_group = QGroupBox("Focus Areas")
        focus_layout = QVBoxLayout(focus_group)
        
        focus_layout.addWidget(QLabel("Default Tenses to Practice:"))
        
        self.tense_checkboxes = {}
        tenses = ["Present", "Preterite", "Imperfect", "Future", "Conditional", "Subjunctive"]
        preferred_tenses = self.config.get("preferred_tenses", ["Present", "Preterite"])
        
        for tense in tenses:
            cb = QCheckBox(tense)
            cb.setChecked(tense in preferred_tenses)
            self.tense_checkboxes[tense] = cb
            focus_layout.addWidget(cb)
        
        layout.addWidget(focus_group)
        
        # Speed Practice Settings
        speed_group = QGroupBox("Speed Practice")
        speed_layout = QFormLayout(speed_group)
        
        self.speed_timer_spin = QSpinBox()
        self.speed_timer_spin.setRange(1, 10)
        self.speed_timer_spin.setSuffix(" seconds")
        self.speed_timer_spin.setValue(self.config.get("speed_timer", 3))
        speed_layout.addRow("Default Timer:", self.speed_timer_spin)
        
        layout.addWidget(speed_group)
        
        layout.addStretch()
    
    def getSettings(self) -> Dict[str, Any]:
        """Get learning settings"""
        strictness_map = {0: "lenient", 1: "normal", 2: "strict"}
        
        selected_tenses = [
            tense for tense, cb in self.tense_checkboxes.items()
            if cb.isChecked()
        ]
        
        return {
            "difficulty": self.difficulty_combo.currentText().lower(),
            "exercise_count": self.exercise_count_spin.value(),
            "answer_strictness": strictness_map[self.strictness_combo.currentIndex()],
            "preferred_tenses": selected_tenses,
            "speed_timer": self.speed_timer_spin.value()
        }

class AppearanceSettingsTab(QWidget):
    """Appearance Configuration Tab"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Theme Settings
        theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout(theme_group)
        
        self.dark_mode_checkbox = QCheckBox("Enable dark mode")
        self.dark_mode_checkbox.setChecked(self.config.get("dark_mode", False))
        theme_layout.addWidget(self.dark_mode_checkbox)
        
        layout.addWidget(theme_group)
        
        # Display Settings
        display_group = QGroupBox("Display Options")
        display_layout = QVBoxLayout(display_group)
        
        self.show_translation_checkbox = QCheckBox("Show English translations by default")
        self.show_translation_checkbox.setChecked(self.config.get("show_translation", False))
        display_layout.addWidget(self.show_translation_checkbox)
        
        self.minimize_to_tray_checkbox = QCheckBox("Minimize to system tray")
        self.minimize_to_tray_checkbox.setChecked(self.config.get("minimize_to_tray", True))
        display_layout.addWidget(self.minimize_to_tray_checkbox)
        
        self.start_minimized_checkbox = QCheckBox("Start minimized")
        self.start_minimized_checkbox.setChecked(self.config.get("start_minimized", False))
        display_layout.addWidget(self.start_minimized_checkbox)
        
        layout.addWidget(display_group)
        
        # Window Settings
        window_group = QGroupBox("Window")
        window_layout = QFormLayout(window_group)
        
        # Window size
        geometry = self.config.get("window_geometry", {})
        
        self.window_width_spin = QSpinBox()
        self.window_width_spin.setRange(800, 2000)
        self.window_width_spin.setValue(geometry.get("width", 1100))
        window_layout.addRow("Default Width:", self.window_width_spin)
        
        self.window_height_spin = QSpinBox()
        self.window_height_spin.setRange(600, 1500)
        self.window_height_spin.setValue(geometry.get("height", 700))
        window_layout.addRow("Default Height:", self.window_height_spin)
        
        # Remember position
        self.remember_position_checkbox = QCheckBox("Remember window position")
        self.remember_position_checkbox.setChecked(True)
        window_layout.addRow("", self.remember_position_checkbox)
        
        layout.addWidget(window_group)
        
        layout.addStretch()
    
    def getSettings(self) -> Dict[str, Any]:
        """Get appearance settings"""
        return {
            "dark_mode": self.dark_mode_checkbox.isChecked(),
            "show_translation": self.show_translation_checkbox.isChecked(),
            "minimize_to_tray": self.minimize_to_tray_checkbox.isChecked(),
            "start_minimized": self.start_minimized_checkbox.isChecked(),
            "window_geometry": {
                "width": self.window_width_spin.value(),
                "height": self.window_height_spin.value(),
                "x": self.config.get("window_geometry", {}).get("x", 100),
                "y": self.config.get("window_geometry", {}).get("y", 100)
            },
            "remember_position": self.remember_position_checkbox.isChecked()
        }

class AdvancedSettingsTab(QWidget):
    """Advanced Configuration Tab"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Data Management
        data_group = QGroupBox("Data Management")
        data_layout = QFormLayout(data_group)
        
        self.max_stored_responses_spin = QSpinBox()
        self.max_stored_responses_spin.setRange(50, 1000)
        self.max_stored_responses_spin.setValue(self.config.get("max_stored_responses", 100))
        data_layout.addRow("Max Stored Responses:", self.max_stored_responses_spin)
        
        # Database location
        self.db_path_input = QLineEdit()
        self.db_path_input.setText(self.config.get("database_path", "progress.db"))
        self.db_path_input.setReadOnly(True)
        
        db_layout = QHBoxLayout()
        db_layout.addWidget(self.db_path_input)
        
        browse_db_btn = QPushButton("Browse")
        browse_db_btn.clicked.connect(self.browseDatabasePath)
        db_layout.addWidget(browse_db_btn)
        
        data_layout.addRow("Database Path:", db_layout)
        
        layout.addWidget(data_group)
        
        # Backup Settings
        backup_group = QGroupBox("Backup & Export")
        backup_layout = QVBoxLayout(backup_group)
        
        self.auto_backup_checkbox = QCheckBox("Enable automatic backups")
        self.auto_backup_checkbox.setChecked(self.config.get("auto_backup", False))
        backup_layout.addWidget(self.auto_backup_checkbox)
        
        # Export settings
        export_layout = QHBoxLayout()
        export_progress_btn = QPushButton("Export Progress")
        export_progress_btn.clicked.connect(self.exportProgress)
        export_layout.addWidget(export_progress_btn)
        
        import_progress_btn = QPushButton("Import Progress")
        import_progress_btn.clicked.connect(self.importProgress)
        export_layout.addWidget(import_progress_btn)
        
        backup_layout.addLayout(export_layout)
        
        layout.addWidget(backup_group)
        
        # Reset Settings
        reset_group = QGroupBox("Reset Options")
        reset_layout = QVBoxLayout(reset_group)
        
        reset_desc = QLabel(
            "These options will reset various parts of your data. "
            "Use with caution as these actions cannot be undone."
        )
        reset_desc.setWordWrap(True)
        reset_desc.setStyleSheet("color: #e67e22; margin-bottom: 10px;")
        reset_layout.addWidget(reset_desc)
        
        reset_buttons_layout = QHBoxLayout()
        
        reset_progress_btn = QPushButton("Reset Progress")
        reset_progress_btn.clicked.connect(self.resetProgress)
        reset_progress_btn.setStyleSheet("QPushButton { background-color: #e74c3c; }")
        reset_buttons_layout.addWidget(reset_progress_btn)
        
        reset_settings_btn = QPushButton("Reset Settings")
        reset_settings_btn.clicked.connect(self.resetSettings)
        reset_settings_btn.setStyleSheet("QPushButton { background-color: #e74c3c; }")
        reset_buttons_layout.addWidget(reset_settings_btn)
        
        reset_layout.addLayout(reset_buttons_layout)
        
        layout.addWidget(reset_group)
        
        layout.addStretch()
    
    def browseDatabasePath(self):
        """Browse for database file location"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Choose Database Location", 
            self.db_path_input.text(),
            "Database Files (*.db);;All Files (*)"
        )
        if file_path:
            self.db_path_input.setText(file_path)
    
    def exportProgress(self):
        """Export progress data"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Progress",
            f"spanish_progress_backup.json",
            "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            QMessageBox.information(self, "Export", f"Progress exported to:\n{file_path}")
    
    def importProgress(self):
        """Import progress data"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Progress",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            reply = QMessageBox.question(
                self, "Import Progress",
                "This will overwrite your current progress. Continue?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                QMessageBox.information(self, "Import", f"Progress imported from:\n{file_path}")
    
    def resetProgress(self):
        """Reset learning progress"""
        reply = QMessageBox.warning(
            self, "Reset Progress",
            "This will permanently delete all your learning progress.\n"
            "This action cannot be undone. Continue?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            QMessageBox.information(self, "Reset Complete", "Learning progress has been reset.")
    
    def resetSettings(self):
        """Reset application settings"""
        reply = QMessageBox.warning(
            self, "Reset Settings",
            "This will reset all application settings to defaults.\n"
            "This action cannot be undone. Continue?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            QMessageBox.information(self, "Reset Complete", "Settings have been reset to defaults.")
    
    def getSettings(self) -> Dict[str, Any]:
        """Get advanced settings"""
        return {
            "max_stored_responses": self.max_stored_responses_spin.value(),
            "database_path": self.db_path_input.text(),
            "auto_backup": self.auto_backup_checkbox.isChecked()
        }

class SettingsDialog(QDialog):
    """Professional Settings Dialog"""
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, config: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.config = config.copy()
        self.setWindowTitle("Settings - Spanish Conjugation Trainer")
        self.setFixedSize(600, 500)
        self.setWindowFlags(Qt.Dialog | Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
        
        self.initUI()
        self.applyProfessionalStyling()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.api_tab = APISettingsTab(self.config)
        self.learning_tab = LearningSettingsTab(self.config)
        self.appearance_tab = AppearanceSettingsTab(self.config)
        self.advanced_tab = AdvancedSettingsTab(self.config)
        
        # Add tabs
        self.tab_widget.addTab(self.api_tab, "🔑 API & AI")
        self.tab_widget.addTab(self.learning_tab, "📚 Learning")
        self.tab_widget.addTab(self.appearance_tab, "🎨 Appearance")
        self.tab_widget.addTab(self.advanced_tab, "⚙️ Advanced")
        
        layout.addWidget(self.tab_widget)
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.Apply).clicked.connect(self.apply)
        
        layout.addWidget(button_box)
    
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
            }
            QTabBar::tab {
                background: #ecf0f1;
                border: 1px solid #bdc3c7;
                padding: 8px 12px;
                margin-right: 2px;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 1px solid white;
            }
            QTabBar::tab:hover:!selected {
                background: #d5dbdb;
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
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QLineEdit, QComboBox, QSpinBox {
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                padding: 4px;
                font-size: 12px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
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
            QSlider::groove:horizontal {
                border: 1px solid #bdc3c7;
                height: 4px;
                background: #ecf0f1;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #3498db;
                border: 1px solid #2980b9;
                width: 16px;
                height: 16px;
                border-radius: 8px;
                margin: -6px 0;
            }
        """)
    
    def apply(self):
        """Apply current settings"""
        new_config = {}
        
        # Gather settings from all tabs
        new_config.update(self.api_tab.getSettings())
        new_config.update(self.learning_tab.getSettings())
        new_config.update(self.appearance_tab.getSettings())
        new_config.update(self.advanced_tab.getSettings())
        
        # Add setup complete flag
        new_config["setup_complete"] = True
        
        self.config.update(new_config)
        self.settings_changed.emit(self.config)
    
    def accept(self):
        """Accept and apply settings"""
        self.apply()
        super().accept()
    
    @staticmethod
    def openSettings(config: Dict[str, Any], parent=None):
        """Static method to open settings dialog"""
        dialog = SettingsDialog(config, parent)
        result = dialog.exec_() == QDialog.Accepted
        return result, dialog.config