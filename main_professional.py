"""
Enhanced Professional Spanish Conjugation Practice App
=====================================================

This is the enhanced version of the Spanish Conjugation app with professional
desktop features including setup wizard, system tray integration, enhanced
error handling, and modern UI design.

Key Professional Features:
- Setup wizard for first-run configuration
- Professional system tray integration
- Enhanced API error handling with solutions
- About dialog with version and license info
- Settings dialog for comprehensive configuration
- Professional styling and branding
- First-run detection and onboarding
"""

import sys
import os
import json
import logging
import random
import time
from typing import List, Dict, Union, Optional, Any, Tuple, Callable

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
load_dotenv()

# PyQt5 imports
from PyQt5.QtCore import Qt, QRunnable, QObject, pyqtSignal, QThreadPool, QTimer
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QLineEdit, QPushButton, QProgressBar, QTextEdit, QComboBox,
    QStackedWidget, QRadioButton, QButtonGroup, QStatusBar, QAction, QGroupBox,
    QCheckBox, QMessageBox, QToolBar, QSpinBox, QSystemTrayIcon, QSplashScreen
)
from PyQt5.QtGui import QFont, QPixmap, QIcon

# Import professional components
from dialogs.setup_wizard import SetupWizard
from dialogs.settings_dialog import SettingsDialog
from dialogs.about_dialog import AboutDialog
from dialogs.error_dialog import ErrorDialog, APIErrorHandler
from gui.system_tray import SystemTrayManager, TrayNotificationManager
from gui.professional_styling import ProfessionalStyling, professional_styling
from utils.first_run_manager import FirstRunManager

# Original app imports
from exercise_generator import ExerciseGenerator
from progress_tracker import ProgressTracker
from conjugation_engine import PERSON_LABELS, TENSE_NAMES, SpanishConjugator
from task_scenarios import TaskScenario
from speed_practice import SpeedPractice
from learning_path import LearningPath

# OpenAI imports
import openai
from openai import OpenAI

# Configuration Management
class EnhancedAppConfig:
    """Enhanced configuration manager with first-run detection"""
    
    def __init__(self):
        self.first_run_manager = FirstRunManager()
        self.config = self.first_run_manager.load_configuration()
        
        # Set OpenAI API key if available
        api_key = self.config.get("api_key") or os.getenv("OPENAI_API_KEY", "")
        if api_key:
            openai.api_key = api_key
            self.openai_client = OpenAI(api_key=api_key)
        else:
            self.openai_client = None
    
    def is_first_run(self) -> bool:
        return self.first_run_manager.is_first_run()
    
    def get(self, key: str, default=None):
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        self.config[key] = value
        self.save_config()
    
    def update(self, new_config: Dict[str, Any]):
        self.config.update(new_config)
        self.save_config()
    
    def save_config(self):
        return self.first_run_manager.save_configuration(self.config)
    
    def mark_setup_complete(self):
        return self.first_run_manager.mark_setup_complete(self.config)

# Enhanced logging setup
def setup_enhanced_logging() -> logging.Logger:
    """Configure enhanced logging with professional formatting"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Enhanced formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    os.makedirs("logs", exist_ok=True)
    file_handler = logging.FileHandler("logs/app.log", mode="a", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

logger = setup_enhanced_logging()

# Enhanced Worker Thread with Error Handling
class EnhancedGPTWorker(QRunnable):
    """Enhanced GPT worker with professional error handling"""
    
    def __init__(self, prompt: str, config: EnhancedAppConfig):
        super().__init__()
        self.prompt = prompt
        self.config = config
        self.signals = WorkerSignals()
    
    def run(self):
        try:
            if not self.config.openai_client:
                raise Exception("OpenAI client not initialized. Please check your API key.")
            
            response = self.config.openai_client.chat.completions.create(
                model=self.config.get("api_model", "gpt-4o"),
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert Spanish tutor specializing in LATAM Spanish. "
                            "Your guidance should always reflect real-life conversational tone, "
                            "using authentic expressions and culturally relevant details."
                        )
                    },
                    {"role": "user", "content": self.prompt}
                ],
                max_tokens=self.config.get("max_tokens", 600),
                temperature=self.config.get("temperature", 0.5),
            )
            output = response.choices[0].message.content.strip()
            logger.info("GPT response received successfully")
            
        except Exception as e:
            logger.error(f"GPT API error: {str(e)}")
            # Let the error dialog handle the user-friendly message
            output = f"API_ERROR: {str(e)}"
        
        self.signals.result.emit(output)

class WorkerSignals(QObject):
    """Signals for worker threads"""
    result = pyqtSignal(str)

# Enhanced Main Application
class ProfessionalSpanishApp(QMainWindow):
    """Professional Spanish Conjugation Practice Application"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize configuration
        self.config = EnhancedAppConfig()
        
        # Initialize core components
        self.responses: List[Dict[str, Any]] = []
        self.exercises: List[Dict[str, Any]] = []
        self.current_exercise: int = 0
        self.total_exercises: int = 0
        
        # Initialize learning components
        self.progress_tracker = ProgressTracker()
        self.exercise_generator = ExerciseGenerator()
        self.task_scenarios = TaskScenario()
        self.speed_practice = SpeedPractice()
        self.learning_path = LearningPath()
        self.conjugator = SpanishConjugator()
        self.session_id = self.progress_tracker.start_session()
        self.threadpool = QThreadPool()
        
        # UI state
        self.start_time = None
        self.task_mode = False
        self.speed_mode = False
        
        # Professional features
        self.system_tray = None
        self.notification_manager = None
        
        # Check for first run
        if self.config.is_first_run():
            self.run_first_time_setup()
        else:
            self.initialize_application()
    
    def run_first_time_setup(self):
        """Run first-time setup wizard"""
        logger.info("First run detected, showing setup wizard")
        
        # Show setup wizard
        wizard = SetupWizard()
        wizard.configuration_complete.connect(self.on_setup_complete)
        
        if wizard.exec_() == SetupWizard.Accepted:
            # Setup completed, continue with initialization
            self.initialize_application()
        else:
            # User cancelled setup, use defaults and continue
            logger.info("Setup cancelled, using default configuration")
            self.config.set("setup_complete", False)
            self.initialize_application()
    
    def on_setup_complete(self, setup_config: Dict[str, Any]):
        """Handle setup completion"""
        logger.info("Setup wizard completed")
        
        # Update configuration
        self.config.update(setup_config)
        self.config.mark_setup_complete()
        
        # Initialize OpenAI client if API key was provided
        if setup_config.get("api_key"):
            try:
                openai.api_key = setup_config["api_key"]
                self.config.openai_client = OpenAI(api_key=setup_config["api_key"])
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
    
    def initialize_application(self):
        """Initialize the main application"""
        logger.info("Initializing professional Spanish conjugation app")
        
        # Set window properties
        self.setWindowTitle("Spanish Conjugation Trainer - Professional Edition")
        self.setWindowIcon(self.load_app_icon())
        
        # Apply professional styling
        self.apply_professional_styling()
        
        # Set window geometry
        geometry = self.config.get("window_geometry", {})
        self.setGeometry(
            geometry.get("x", 100),
            geometry.get("y", 100),
            geometry.get("width", 1100),
            geometry.get("height", 700)
        )
        
        # Initialize UI
        self.initUI()
        
        # Initialize system tray
        self.initialize_system_tray()
        
        # Show welcome message for new users
        if self.config.get("run_count", 0) < 3:
            self.show_welcome_message()
        
        # Log successful initialization
        logger.info("Application initialized successfully")
    
    def load_app_icon(self) -> QIcon:
        """Load application icon"""
        icon_paths = [
            "src/resources/app_icon.ico",
            "src/resources/icon_64.png",
            "src/resources/icon_32.png"
        ]
        
        for path in icon_paths:
            if os.path.exists(path):
                return QIcon(path)
        
        # Return default icon
        return self.style().standardIcon(self.style().SP_ComputerIcon)
    
    def apply_professional_styling(self):
        """Apply professional styling to the application"""
        theme = "dark" if self.config.get("dark_mode", False) else "light"
        professional_styling.apply_theme(QApplication.instance(), theme)
    
    def initialize_system_tray(self):
        """Initialize system tray integration"""
        if not self.config.get("minimize_to_tray", True):
            return
        
        if SystemTrayManager.is_available():
            self.system_tray = SystemTrayManager(self)
            self.notification_manager = TrayNotificationManager(self.system_tray)
            
            # Connect signals
            self.system_tray.show_main_window.connect(self.show)
            self.system_tray.hide_main_window.connect(self.hide)
            self.system_tray.new_exercise_requested.connect(self.generateNewExercise)
            self.system_tray.speed_mode_requested.connect(self.startSpeedMode)
            self.system_tray.settings_requested.connect(self.show_settings)
            self.system_tray.quit_requested.connect(self.close)
            
            logger.info("System tray initialized")
        else:
            logger.warning("System tray not available")
    
    def show_welcome_message(self):
        """Show welcome message for new users"""
        if not self.config.first_run_manager.should_show_tips():
            return
        
        welcome_msg = self.config.first_run_manager.get_welcome_message()
        tips = self.config.first_run_manager.get_startup_tips()
        
        if tips:
            welcome_msg += "\n\n💡 Quick Tips:\n" + "\n".join(tips)
        
        QMessageBox.information(self, "Welcome!", welcome_msg)
    
    def initUI(self):
        """Initialize the user interface"""
        self.createMenuBar()
        self.createToolBar()
        self.createMainContent()
        self.createStatusBar()
        
        # Connect enhanced error handling
        self.setup_error_handling()
    
    def createMenuBar(self):
        """Create professional menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        new_session_action = QAction('&New Session', self)
        new_session_action.setShortcut('Ctrl+N')
        new_session_action.triggered.connect(self.generateNewExercise)
        file_menu.addAction(new_session_action)
        
        file_menu.addSeparator()
        
        export_action = QAction('&Export Progress', self)
        export_action.triggered.connect(self.exportProgress)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('E&xit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Practice menu
        practice_menu = menubar.addMenu('&Practice')
        
        speed_mode_action = QAction('&Speed Mode', self)
        speed_mode_action.setShortcut('Ctrl+S')
        speed_mode_action.triggered.connect(self.startSpeedMode)
        practice_menu.addAction(speed_mode_action)
        
        task_mode_action = QAction('&Task Mode', self)
        task_mode_action.triggered.connect(self.startTaskMode)
        practice_menu.addAction(task_mode_action)
        
        story_mode_action = QAction('S&tory Mode', self)
        story_mode_action.triggered.connect(self.startStoryMode)
        practice_menu.addAction(story_mode_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('&Tools')
        
        stats_action = QAction('&Statistics', self)
        stats_action.triggered.connect(self.showStatistics)
        tools_menu.addAction(stats_action)
        
        reference_action = QAction('&Verb Reference', self)
        reference_action.triggered.connect(self.showCheatSheet)
        tools_menu.addAction(reference_action)
        
        tools_menu.addSeparator()
        
        settings_action = QAction('&Settings', self)
        settings_action.setShortcut('Ctrl+,')
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        
        about_action = QAction('&About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def createToolBar(self):
        """Create the main toolbar with professional styling"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Main actions with icons/emojis
        actions = [
            ("🔄 Reset", "Reset progress", self.resetProgress),
            ("📝 New Exercise", "Generate new exercises", self.generateNewExercise),
            ("📊 Summary", "Generate session summary", self.generateSessionSummary),
            ("⚡ Speed Mode", "Speed practice mode", self.startSpeedMode),
            ("🎯 Task Mode", "Task-based practice", self.startTaskMode),
            ("📈 Statistics", "View learning statistics", self.showStatistics),
            ("⚙️ Settings", "Application settings", self.show_settings),
        ]
        
        for text, tooltip, handler in actions:
            action = QAction(text, self)
            action.setToolTip(tooltip)
            action.triggered.connect(handler)
            toolbar.addAction(action)
        
        # Theme toggle
        toolbar.addSeparator()
        theme_action = QAction("🌙 Dark Mode", self)
        theme_action.setCheckable(True)
        theme_action.setChecked(self.config.get("dark_mode", False))
        theme_action.triggered.connect(self.toggleTheme)
        toolbar.addAction(theme_action)
        
        # Offline mode toggle
        offline_action = QAction("🔌 Offline", self)
        offline_action.setCheckable(True)
        offline_action.setChecked(self.config.get("offline_mode", False))
        offline_action.triggered.connect(self.toggleOfflineMode)
        toolbar.addAction(offline_action)
    
    def createMainContent(self):
        """Create main content area (reusing original layout)"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left pane - Exercise display
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        self.sentence_label = QLabel("Welcome! Click 'New Exercise' to begin.")
        self.sentence_label.setWordWrap(True)
        self.sentence_label.setStyleSheet("font-size: 18px; padding: 20px; font-weight: 500;")
        left_layout.addWidget(self.sentence_label)
        
        self.translation_label = QLabel("")
        self.translation_label.setWordWrap(True)
        self.translation_label.setStyleSheet("font-size: 14px; padding: 10px; color: #7f8c8d; font-style: italic;")
        self.translation_label.setVisible(self.config.get("show_translation", False))
        left_layout.addWidget(self.translation_label)
        
        self.stats_label = QLabel("Ready to practice!")
        self.stats_label.setStyleSheet("font-size: 12px; color: #95a5a6; padding: 10px;")
        left_layout.addWidget(self.stats_label)
        
        left_layout.addStretch()
        splitter.addWidget(left_widget)
        
        # Right pane - Controls (simplified for this example)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Quick practice options
        options_group = QGroupBox("Quick Practice")
        options_layout = QVBoxLayout(options_group)
        
        self.quick_tense_combo = QComboBox()
        self.quick_tense_combo.addItems(["Present", "Preterite", "Imperfect", "Future"])
        options_layout.addWidget(QLabel("Tense:"))
        options_layout.addWidget(self.quick_tense_combo)
        
        self.quick_count_spin = QSpinBox()
        self.quick_count_spin.setRange(1, 20)
        self.quick_count_spin.setValue(5)
        options_layout.addWidget(QLabel("Exercise Count:"))
        options_layout.addWidget(self.quick_count_spin)
        
        right_layout.addWidget(options_group)
        
        # Answer input
        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("Type your answer here...")
        self.answer_input.returnPressed.connect(self.submitAnswer)
        right_layout.addWidget(QLabel("Your Answer:"))
        right_layout.addWidget(self.answer_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.submit_btn = QPushButton("Submit")
        self.submit_btn.clicked.connect(self.submitAnswer)
        self.hint_btn = QPushButton("Hint")
        self.hint_btn.clicked.connect(self.provideHint)
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.nextExercise)
        
        button_layout.addWidget(self.submit_btn)
        button_layout.addWidget(self.hint_btn)
        button_layout.addWidget(self.next_btn)
        right_layout.addLayout(button_layout)
        
        # Feedback
        self.feedback_text = QTextEdit()
        self.feedback_text.setReadOnly(True)
        self.feedback_text.setMaximumHeight(150)
        right_layout.addWidget(self.feedback_text)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        right_layout.addWidget(self.progress_bar)
        
        right_layout.addStretch()
        splitter.addWidget(right_widget)
        
        # Set splitter sizes
        splitter.setSizes([450, 650])
    
    def createStatusBar(self):
        """Create professional status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Add permanent widgets
        self.status_bar.addPermanentWidget(QLabel(f"v{self.config.get('version', '2.0.0')}"))
        
        self.updateStatus("Ready - Professional Spanish Conjugation Trainer")
    
    def setup_error_handling(self):
        """Setup enhanced error handling"""
        # This would connect to various error sources in the original app
        pass
    
    def show_settings(self):
        """Show settings dialog"""
        success, new_config = SettingsDialog.openSettings(self.config.config, self)
        if success:
            # Update configuration
            self.config.update(new_config)
            
            # Apply theme changes immediately
            if new_config.get("dark_mode") != self.config.get("dark_mode"):
                self.apply_professional_styling()
            
            # Update system tray settings
            if self.system_tray:
                self.system_tray.set_enabled(new_config.get("minimize_to_tray", True))
            
            self.updateStatus("Settings updated successfully")
            logger.info("Settings updated by user")
    
    def show_about(self):
        """Show about dialog"""
        AboutDialog.showAbout(self)
    
    def toggleTheme(self):
        """Toggle between light and dark themes"""
        current_dark = self.config.get("dark_mode", False)
        new_dark = not current_dark
        
        self.config.set("dark_mode", new_dark)
        self.apply_professional_styling()
        
        theme_name = "dark" if new_dark else "light"
        self.updateStatus(f"Switched to {theme_name} theme")
    
    def toggleOfflineMode(self):
        """Toggle offline mode"""
        current_offline = self.config.get("offline_mode", False)
        new_offline = not current_offline
        
        self.config.set("offline_mode", new_offline)
        mode = "offline" if new_offline else "online"
        self.updateStatus(f"Switched to {mode} mode")
    
    def handle_api_error(self, error_message: str):
        """Handle API errors with professional error dialog"""
        logger.error(f"API Error: {error_message}")
        
        # Show professional error dialog
        ErrorDialog.show_api_error(error_message, error_message, self)
        
        # Optionally switch to offline mode
        if "authentication" in error_message.lower() or "api_key" in error_message.lower():
            reply = QMessageBox.question(
                self, "Switch to Offline Mode?",
                "Would you like to switch to offline mode to continue practicing?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.config.set("offline_mode", True)
                self.updateStatus("Switched to offline mode due to API error")
    
    def generateNewExercise(self):
        """Generate new exercises with enhanced error handling"""
        if self.config.get("offline_mode", False):
            self.generate_offline_exercises()
        else:
            self.generate_online_exercises()
    
    def generate_offline_exercises(self):
        """Generate exercises locally"""
        try:
            count = self.quick_count_spin.value()
            exercises = self.exercise_generator.generate_batch(count=count)
            
            self.exercises = exercises
            self.total_exercises = len(exercises)
            self.current_exercise = 0
            self.progress_bar.setMaximum(self.total_exercises)
            self.updateExercise()
            self.updateStatus(f"Generated {len(exercises)} exercises offline")
            
        except Exception as e:
            logger.error(f"Offline exercise generation error: {e}")
            ErrorDialog.show_generic_error(
                "Exercise Generation Error",
                "Could not generate exercises locally. Please try again.",
                str(e), self
            )
    
    def generate_online_exercises(self):
        """Generate exercises using AI"""
        if not self.config.openai_client:
            self.handle_api_error("OpenAI client not initialized. Please configure your API key.")
            return
        
        try:
            count = self.quick_count_spin.value()
            tense = self.quick_tense_combo.currentText()
            
            prompt = f"""Generate {count} Spanish conjugation exercises for {tense} tense.
            Return as JSON array with format: [{{"sentence": "...", "answer": "...", "choices": [...], "translation": "..."}}]"""
            
            worker = EnhancedGPTWorker(prompt, self.config)
            worker.signals.result.connect(self.handleExerciseResult)
            self.threadpool.start(worker)
            
            self.updateStatus("Generating AI-powered exercises...")
            
        except Exception as e:
            self.handle_api_error(str(e))
    
    def handleExerciseResult(self, result: str):
        """Handle exercise generation result"""
        if result.startswith("API_ERROR:"):
            error_msg = result[10:]  # Remove "API_ERROR:" prefix
            self.handle_api_error(error_msg)
            return
        
        try:
            import json
            exercises = json.loads(result.strip())
            if not isinstance(exercises, list):
                raise ValueError("Invalid response format")
            
            self.exercises = exercises
            self.total_exercises = len(exercises)
            self.current_exercise = 0
            self.progress_bar.setMaximum(self.total_exercises)
            self.updateExercise()
            self.updateStatus(f"Generated {len(exercises)} AI-powered exercises")
            
        except Exception as e:
            logger.error(f"Exercise parsing error: {e}")
            ErrorDialog.show_generic_error(
                "Response Parsing Error",
                "Could not parse the AI response. Switching to offline mode.",
                str(e), self
            )
            self.config.set("offline_mode", True)
            self.generate_offline_exercises()
    
    def updateExercise(self):
        """Update exercise display"""
        if not self.exercises or self.current_exercise >= len(self.exercises):
            return
        
        exercise = self.exercises[self.current_exercise]
        self.sentence_label.setText(exercise.get("sentence", ""))
        
        if self.config.get("show_translation", False):
            self.translation_label.setText(exercise.get("translation", ""))
        
        self.answer_input.clear()
        self.feedback_text.clear()
        self.progress_bar.setValue(self.current_exercise + 1)
        
        self.updateStats()
    
    def updateStats(self):
        """Update statistics display"""
        if self.total_exercises > 0:
            self.stats_label.setText(
                f"Exercise {self.current_exercise + 1} of {self.total_exercises}"
            )
        else:
            self.stats_label.setText("Ready to practice!")
    
    def submitAnswer(self):
        """Submit user answer"""
        if not self.exercises:
            self.updateStatus("No exercises available")
            return
        
        user_answer = self.answer_input.text().strip()
        if not user_answer:
            self.updateStatus("Please enter an answer")
            return
        
        exercise = self.exercises[self.current_exercise]
        correct_answer = exercise.get("answer", "")
        
        # Simple answer checking
        is_correct = user_answer.lower() == correct_answer.lower()
        
        if is_correct:
            feedback = "✅ Correct! Well done!"
            self.feedback_text.setStyleSheet("color: #27ae60;")
        else:
            feedback = f"❌ Incorrect. The correct answer is: {correct_answer}"
            self.feedback_text.setStyleSheet("color: #e74c3c;")
        
        self.feedback_text.setText(feedback)
        self.updateStatus("Answer submitted")
        
        # Auto-advance after correct answer
        if is_correct:
            QTimer.singleShot(1500, self.nextExercise)
    
    def nextExercise(self):
        """Move to next exercise"""
        if self.current_exercise < self.total_exercises - 1:
            self.current_exercise += 1
            self.updateExercise()
        else:
            self.updateStatus("Session complete!")
            if self.notification_manager:
                stats = {"correct": 0, "total": self.total_exercises}  # Simplified
                self.notification_manager.notify_session_complete(stats)
    
    def provideHint(self):
        """Provide hint for current exercise"""
        if not self.exercises:
            return
        
        exercise = self.exercises[self.current_exercise]
        hint = f"💡 The answer starts with '{exercise.get('answer', '')[:2]}...'"
        self.feedback_text.setText(hint)
        self.feedback_text.setStyleSheet("color: #f39c12;")
    
    def resetProgress(self):
        """Reset current session"""
        self.current_exercise = 0
        self.exercises = []
        self.total_exercises = 0
        self.sentence_label.setText("Click 'New Exercise' to begin.")
        self.feedback_text.clear()
        self.answer_input.clear()
        self.progress_bar.setValue(0)
        self.updateStats()
        self.updateStatus("Progress reset")
    
    def updateStatus(self, message: str):
        """Update status bar message"""
        self.status_bar.showMessage(message, 5000)
    
    # Placeholder methods for features not fully implemented
    def generateSessionSummary(self): pass
    def startSpeedMode(self): self.updateStatus("Speed Mode - Feature coming soon!")
    def startTaskMode(self): self.updateStatus("Task Mode - Feature coming soon!")
    def startStoryMode(self): self.updateStatus("Story Mode - Feature coming soon!")
    def showStatistics(self): self.updateStatus("Statistics - Feature coming soon!")
    def showCheatSheet(self): self.updateStatus("Verb Reference - Feature coming soon!")
    def exportProgress(self): self.updateStatus("Export Progress - Feature coming soon!")
    
    def closeEvent(self, event):
        """Handle application close with system tray support"""
        if (self.system_tray and self.system_tray.is_enabled and 
            self.config.get("minimize_to_tray", True)):
            
            # Hide to system tray instead of closing
            if not self.isHidden():
                event.ignore()
                self.hide()
                if self.system_tray:
                    self.system_tray.show_message(
                        "Spanish Conjugation Trainer",
                        "Application minimized to tray. Double-click to restore.",
                        QSystemTrayIcon.Information
                    )
                return
        
        # Actually closing - cleanup
        logger.info("Application closing")
        
        # Save configuration
        self.config.save_config()
        
        # Cleanup system tray
        if self.system_tray:
            self.system_tray.cleanup()
        
        # Wait for threads
        if not self.threadpool.waitForDone(3000):
            logger.warning("Some threads did not complete in time")
        
        event.accept()

def show_splash_screen(app):
    """Show professional splash screen"""
    splash_path = "src/resources/splash.png"
    
    if os.path.exists(splash_path):
        pixmap = QPixmap(splash_path)
        splash = QSplashScreen(pixmap)
        splash.show()
        
        # Process events to show splash
        app.processEvents()
        
        # Simulate loading time
        import time
        time.sleep(1)
        
        splash.close()
        return splash
    
    return None

def main():
    """Main entry point for professional Spanish conjugation app"""
    app = QApplication(sys.argv)
    app.setApplicationName("Spanish Conjugation Trainer")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("Professional Language Tools")
    
    # Show splash screen
    splash = show_splash_screen(app)
    
    try:
        # Create and show main window
        window = ProfessionalSpanishApp()
        window.show()
        
        # Bring window to front
        window.raise_()
        window.activateWindow()
        
        logger.info("Professional Spanish Conjugation Trainer started successfully")
        
        # Run application
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.critical(f"Critical error starting application: {e}")
        
        # Show critical error dialog
        QMessageBox.critical(
            None, "Critical Error",
            f"Failed to start Spanish Conjugation Trainer:\n\n{str(e)}\n\n"
            "Please check the logs for more information."
        )
        sys.exit(1)

if __name__ == '__main__':
    main()