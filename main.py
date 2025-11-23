"""
Spanish Conjugation Practice App
================================

This script implements a PyQt5 GUI for practicing Spanish verb conjugations,
applying best practices and enhancements based on a recent code review.

Improvements Addressed (based on 'B'):
--------------------------------------
1. Logging Configuration Cleanup
2. Type Hint Standardization
3. UI Constants Extraction
4. Comprehensive Documentation
5. OpenAI Error Handling Enhancement
6. Fix OpenAI Role Parameter
7. Memory Management Implementation
8. Prompting Strategy Refinement (stub for difficulty, count)
9. JSON Handling Improvement
10. Unit Test Implementation (see external test file example)
11. Resource Cleanup Enhancement
12. Answer Validation Flexibility
13. Configuration Management (stub class: AppConfig)
14. Progress Tracking Enhancement (stub class: ProgressStats)
15. API Credential Management (stub class: CredentialsManager)
"""

import sys
import os
import json
import logging
import random
import time
from typing import (
    List, Dict, Union, Optional, Any, Tuple, Callable
)

from dotenv import load_dotenv
load_dotenv()

# Local modules
from exercise_generator import ExerciseGenerator
from progress_tracker import ProgressTracker
from conjugation_engine import PERSON_LABELS, TENSE_NAMES, SpanishConjugator
from task_scenarios import TaskScenario
from speed_practice import SpeedPractice
from learning_path import LearningPath

# Security modules
try:
    from src.security import (
        APIConfig, CredentialsManager, SetupWizard, 
        run_setup_wizard, check_first_run
    )
    SECURITY_AVAILABLE = True
except ImportError as e:
    # Fallback for backward compatibility
    print(f"Warning: Security modules not available: {e}")
    SECURITY_AVAILABLE = False
    APIConfig = None
    CredentialsManager = None

# PyQt5 imports
from PyQt5.QtCore import (
    Qt, QRunnable, QObject, pyqtSignal, QThreadPool
)
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QLineEdit, QPushButton, QProgressBar, QTextEdit, QComboBox,
    QStackedWidget, QRadioButton, QButtonGroup, QStatusBar, QAction, QGroupBox,
    QCheckBox, QMessageBox, QToolBar, QSpinBox
)

# OpenAI imports
import openai
from openai import OpenAI

# For newer OpenAI versions (1.x), errors are handled differently
# We'll use generic exception handling to be compatible


# -------------------------------------------------------
# (1) LOGGING CONFIGURATION CLEANUP
# -------------------------------------------------------
def setup_logging() -> logging.Logger:
    """
    Configure application logging with both file and console handlers.
    Returns the root logger.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Clear any existing handlers to avoid duplication
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Define formatter
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler("logging_doc.txt", mode="a", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = setup_logging()


# -------------------------------------------------------
# (3) UI CONSTANTS EXTRACTION
# -------------------------------------------------------
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 700
WINDOW_POS_X = 100
WINDOW_POS_Y = 100

FONT_SIZE_LARGE = "20px"
FONT_SIZE_MEDIUM = "16px"
FONT_SIZE_SMALL = "14px"
PADDING_LARGE = "20px"
PADDING_MEDIUM = "10px"
PADDING_SMALL = "8px"

SPLITTER_SIZES = [450, 650]  # Left vs right pane ratio
PROGRESS_BAR_HEIGHT = "25px"

# Number of exercises to request from GPT by default
DEFAULT_EXERCISE_BATCH_SIZE = 5


# -------------------------------------------------------
# CONFIGURATION MANAGEMENT
# -------------------------------------------------------
class AppConfig:
    """
    Configuration manager for application settings.

    Handles saving, loading, and accessing application configuration. 
    This stub demonstrates how you might expand or integrate user-defined
    preferences.
    """
    def __init__(self, config_file: str = "app_config.json") -> None:
        self.config_file = config_file
        # Default configuration
        self.default_config = {
            "dark_mode": False,
            "show_translation": False,
            "api_model": "gpt-4o",
            "max_tokens": 600,
            "temperature": 0.5,
            "max_stored_responses": 100,
            "exercise_count": DEFAULT_EXERCISE_BATCH_SIZE,
            "answer_strictness": "normal",
            "window_geometry": {
                "width": WINDOW_WIDTH,
                "height": WINDOW_HEIGHT,
                "x": WINDOW_POS_X,
                "y": WINDOW_POS_Y
            },
            "splitter_sizes": SPLITTER_SIZES
        }
        # Current configuration
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self.default_config.copy()
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            return self.default_config.copy()

    def save_config(self) -> bool:
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            logging.error(f"Error saving config: {e}")
            return False

    def get(self, key: str, default=None) -> Any:
        """Get configuration value by key."""
        return self.config.get(key, self.default_config.get(key, default))

    def set(self, key: str, value: Any) -> None:
        """Set configuration value and save."""
        self.config[key] = value
        self.save_config()


# Global config instance (could also be passed around if needed)
if SECURITY_AVAILABLE and api_config:
    # Use secure configuration
    app_config = api_config
else:
    # Fallback to legacy configuration
    app_config = AppConfig()


# -------------------------------------------------------
# PROGRESS TRACKING
# -------------------------------------------------------
class ProgressStats:
    """
    Track and manage user progress statistics.
    This class can be expanded to track performance by tense, person, etc.
    """
    def __init__(self) -> None:
        self.total_attempted = 0
        self.total_correct = 0
        self.history: List[Dict[str, Any]] = []

    def record_attempt(self, exercise: Dict[str, Any], user_answer: str, is_correct: bool) -> None:
        """Record an exercise attempt in the statistics."""
        self.total_attempted += 1
        if is_correct:
            self.total_correct += 1

        from datetime import datetime
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "exercise": exercise,
            "user_answer": user_answer,
            "correct_answer": exercise.get("answer", ""),
            "is_correct": is_correct
        })

    def get_accuracy(self) -> float:
        """Get overall accuracy percentage."""
        if self.total_attempted == 0:
            return 0.0
        return (self.total_correct / self.total_attempted) * 100.0


# Initialize secure API configuration
api_config = None
credentials_manager = None
api_key = ""
client = None

if SECURITY_AVAILABLE:
    # Use secure API configuration
    try:
        api_config = APIConfig()
        credentials_manager = api_config.credentials_manager
        api_key = api_config.get_api_key()
        
        if api_key:
            openai.api_key = api_key
            client = OpenAI(api_key=api_key)
            logging.info("API configuration loaded successfully")
        else:
            logging.warning("No API key found. Application will run in offline mode.")
    except Exception as e:
        logging.error(f"Failed to initialize secure API configuration: {e}")
        SECURITY_AVAILABLE = False

# Fallback to simple environment variable method
if not SECURITY_AVAILABLE or not api_key:
    api_key = os.getenv("OPENAI_API_KEY", "")
    if api_key:
        openai.api_key = api_key
        client = OpenAI(api_key=api_key)
        logging.info("Using API key from environment variables")
    else:
        logging.warning("OPENAI_API_KEY not found. Application will run in offline mode.")


# -------------------------------------------------------
# (4) COMPREHENSIVE DOCUMENTATION
# -------------------------------------------------------
class WorkerSignals(QObject):
    """
    Signals for worker threads.
    """
    result = pyqtSignal(str)


# -------------------------------------------------------
# (5) OPENAI ERROR HANDLING ENHANCEMENT
#     (6) FIX OPENAI ROLE PARAMETER
# -------------------------------------------------------
class GPTWorkerRunnable(QRunnable):
    """
    Worker thread for calling GPT asynchronously using the updated ChatCompletion interface.
    
    Attributes:
        prompt (str): The content of the user prompt.
        model (str): The GPT model ID.
        max_tokens (int): Maximum tokens for GPT response.
        temperature (float): Sampling temperature.
        signals (WorkerSignals): PyQt signals to emit the GPT result.
    """
    def __init__(self,
                 prompt: str,
                 model: str = "gpt-4o",
                 max_tokens: int = 600,
                 temperature: float = 0.5) -> None:
        super().__init__()
        self.prompt = prompt
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.signals = WorkerSignals()

    def run(self) -> None:
        try:
            response = client.chat.completions.create(
                model=self.model,
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
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            output = response.choices[0].message.content.strip()
            logging.info("GPT response received.")
        except Exception as e:
            error_msg = str(e)
            if "rate_limit" in error_msg.lower():
                output = "Rate limit exceeded. Please try again in a few minutes."
                logging.error("OpenAI rate limit exceeded: %s", e)
            elif "authentication" in error_msg.lower() or "api_key" in error_msg.lower():
                output = "API authentication error. Please check your API key in the .env file."
                logging.error("OpenAI authentication error: %s", e)
            elif "api" in error_msg.lower():
                output = "API service error. Please try again later."
                logging.error("OpenAI API error: %s", e)
            else:
                output = f"Error: {error_msg}"
                logging.error("Error in GPTWorkerRunnable: %s", e)

        self.signals.result.emit(output)


# -------------------------------------------------------
# (9) JSON HANDLING IMPROVEMENT (Utility Function)
# -------------------------------------------------------
def parse_gpt_json(text: str) -> List[Dict[str, Any]]:
    """
    Parse JSON from GPT output with robust error handling.

    Args:
        text: Raw text from GPT that should contain JSON

    Returns:
        Parsed list of exercise dictionaries or empty list on failure.
    """
    # Strip markdown code fences if present
    if text.startswith("```"):
        try:
            # Find the first and last code block markers
            start_idx = text.find("\n", text.find("```")) + 1
            end_idx = text.rfind("```")
            if start_idx > 0 and end_idx > start_idx:
                text = text[start_idx:end_idx].strip()
        except Exception as e:
            logging.error("Error cleaning code blocks: %s", e)

    # Try to parse the JSON
    try:
        data = json.loads(text)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError as e:
        logging.error("JSON parse error: %s", e)
        # Attempt a more manual recovery
        try:
            array_start = text.find("[")
            array_end = text.rfind("]") + 1
            if array_start >= 0 and array_end > array_start:
                return json.loads(text[array_start:array_end])
        except Exception as recovery_e:
            logging.error("JSON recovery failed: %s", recovery_e)
        return []


# -------------------------------------------------------
# (12) ANSWER VALIDATION FLEXIBILITY
# -------------------------------------------------------
def check_answer(user_answer: str,
                 correct_answer: str,
                 strictness: str = "normal") -> Tuple[bool, str]:
    """
    Check if the user's answer is correct using flexible matching.

    Args:
        user_answer: The answer provided by the user
        correct_answer: The expected correct answer
        strictness: Matching strictness level ("strict", "normal", or "lenient")

    Returns:
        (is_correct, feedback_message)
    """
    user_norm = user_answer.strip().lower()
    correct_norm = correct_answer.strip().lower()

    # Direct match check
    if user_norm == correct_norm:
        return True, "Correct! Great job!"

    # Accent insensitive check (for "normal" and "lenient")
    if strictness in ["normal", "lenient"]:
        import unicodedata
        def remove_accents(text: str) -> str:
            return ''.join(
                c for c in unicodedata.normalize('NFKD', text)
                if not unicodedata.combining(c)
            )
        if remove_accents(user_norm) == remove_accents(correct_norm):
            return True, "Correct! (Accent marks differ)"

    # Lenient mode additional checks (typos)
    if strictness == "lenient":
        import difflib
        # Check similarity
        similarity = difflib.SequenceMatcher(None, user_norm, correct_norm).ratio()
        if similarity > 0.85:
            return True, f"Close enough! The exact answer is '{correct_answer}'."

    return False, f"Incorrect. The correct answer is '{correct_answer}'."


# -------------------------------------------------------
# MAIN GUI CLASS
# -------------------------------------------------------
class SpanishConjugationGUI(QMainWindow):
    """
    A GUI application for Spanish conjugation practice.

    This application allows users to practice Spanish verb conjugations with
    customizable options for verb tenses, grammatical persons, and themes.
    It can generate exercises locally or using the OpenAI API.

    Attributes:
        responses (List[dict]): Records of user responses for session summary
        exercises (List[dict]): Current batch of exercises
        current_exercise (int): Index of the current exercise being displayed
        stats (ProgressStats): Tracks number of attempts and correct answers
        progress_tracker (ProgressTracker): SQLite-based progress tracking
        exercise_generator (ExerciseGenerator): Local exercise generation
        threadpool (QThreadPool): Thread pool for asynchronous operations
        dark_mode (bool): Whether dark mode is enabled
        show_translation (bool): Whether English translations are displayed
        offline_mode (bool): Whether to use local generation instead of GPT
    """
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Spanish Conjugation Practice")

        # Check for first run and show setup wizard if needed
        if SECURITY_AVAILABLE and check_first_run():
            self.show_setup_wizard()

        # Retrieve some settings from AppConfig
        if hasattr(app_config, 'get'):
            geometry = app_config.get("window_geometry", {
                "x": WINDOW_POS_X, "y": WINDOW_POS_Y,
                "width": WINDOW_WIDTH, "height": WINDOW_HEIGHT
            })
        else:
            geometry = {
                "x": WINDOW_POS_X, "y": WINDOW_POS_Y,
                "width": WINDOW_WIDTH, "height": WINDOW_HEIGHT
            }
        
        self.setGeometry(
            geometry["x"], geometry["y"],
            geometry["width"], geometry["height"]
        )

        self.responses: List[Dict[str, Any]] = []
        self.exercises: List[Dict[str, Any]] = []
        self.current_exercise: int = 0

        self.stats = ProgressStats()
        self.progress_tracker = ProgressTracker()
        self.exercise_generator = ExerciseGenerator()
        self.task_scenarios = TaskScenario()
        self.speed_practice = SpeedPractice()
        self.learning_path = LearningPath()
        self.conjugator = SpanishConjugator()
        self.session_id = self.progress_tracker.start_session()
        self.threadpool = QThreadPool()
        self.offline_mode = False  # Start in online mode by default
        self.task_mode = False  # Toggle between grammar drills and tasks
        self.speed_mode = False  # Speed practice mode
        self.start_time = None  # For timing responses

        # Load initial states from config
        if hasattr(app_config, 'get'):
            self.dark_mode: bool = app_config.get("dark_mode", False)
            self.show_translation: bool = app_config.get("show_translation", False)
            self.max_stored_responses: int = app_config.get("max_stored_responses", 100)
        else:
            self.dark_mode: bool = False
            self.show_translation: bool = False
            self.max_stored_responses: int = 100

        # Initialize API client if available
        self.api_client = client

        self.initUI()

        # Do not auto-generate on startup; user must click "New Exercise"
        self.exercises = []
        self.total_exercises: int = 0
        self.updateSessionStats()

    def initUI(self) -> None:
        """
        Initialize the GUI elements and layout.
        """
        self.createToolBar()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Left Pane: Sentence & Translation
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        self.sentence_label = QLabel("Sentence will appear here.")
        self.sentence_label.setWordWrap(True)
        self.sentence_label.setStyleSheet(f"font-size: {FONT_SIZE_LARGE}; padding: {PADDING_LARGE};")
        left_layout.addWidget(self.sentence_label)

        self.translation_label = QLabel("")
        self.translation_label.setWordWrap(True)
        self.translation_label.setStyleSheet(f"font-size: {FONT_SIZE_MEDIUM}; padding: {PADDING_MEDIUM}; color: gray;")
        self.translation_label.setVisible(self.show_translation)
        left_layout.addWidget(self.translation_label)

        self.stats_label = QLabel("Exercises: 0 | Correct: 0")
        self.stats_label.setStyleSheet(f"font-size: {FONT_SIZE_SMALL}; color: gray; padding: {PADDING_MEDIUM};")
        left_layout.addWidget(self.stats_label)
        left_layout.addStretch()
        splitter.addWidget(left_widget)

        # Right Pane: Options and Interaction
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # -------- Practice Options Panel --------
        self.practice_options_box = QGroupBox("Practice Options")
        po_layout = QVBoxLayout(self.practice_options_box)

        # Tenses
        tense_box = QGroupBox("Verb Tenses/Aspects")
        tense_layout = QHBoxLayout(tense_box)
        self.tense_checkboxes: Dict[str, QCheckBox] = {}
        for tense in ["Present", "Preterite", "Imperfect", "Future", "Conditional", "Subjunctive"]:
            cb = QCheckBox(tense)
            if tense == "Present":
                cb.setChecked(True)
            self.tense_checkboxes[tense] = cb
            tense_layout.addWidget(cb)
        po_layout.addWidget(tense_box)

        # Persons
        form_box = QGroupBox("Target Forms")
        form_layout = QHBoxLayout(form_box)
        self.person_checkboxes: Dict[str, QCheckBox] = {}
        for form in [
            "1st person singular", "2nd person singular", "3rd person singular",
            "1st person plural", "2nd person plural", "3rd person plural"
        ]:
            cb = QCheckBox(form)
            if form == "1st person singular":
                cb.setChecked(True)
            self.person_checkboxes[form] = cb
            form_layout.addWidget(cb)
        po_layout.addWidget(form_box)

        # Specific verbs
        verb_box = QGroupBox("Specific Verbs (optional, comma-separated)")
        verb_layout = QHBoxLayout(verb_box)
        self.specific_verbs_input = QLineEdit()
        self.specific_verbs_input.setPlaceholderText("e.g., hablar, comer, vivir")
        verb_layout.addWidget(self.specific_verbs_input)
        po_layout.addWidget(verb_box)

        # Theme/Context
        theme_box = QGroupBox("Theme/Topic/Context (optional)")
        theme_layout = QHBoxLayout(theme_box)
        self.theme_input = QLineEdit()
        self.theme_input.setPlaceholderText("e.g., travel, food, work")
        theme_layout.addWidget(self.theme_input)
        po_layout.addWidget(theme_box)

        # Difficulty & Exercise Count (8) Prompting Refinement (stub)
        difficulty_box = QGroupBox("Difficulty Level")
        difficulty_layout = QHBoxLayout(difficulty_box)
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["Beginner", "Intermediate", "Advanced"])
        difficulty_layout.addWidget(self.difficulty_combo)
        po_layout.addWidget(difficulty_box)

        count_box = QGroupBox("Number of Exercises")
        count_layout = QHBoxLayout(count_box)
        self.exercise_count_spin = QSpinBox()
        self.exercise_count_spin.setRange(1, 50)  # More flexibility
        default_count = 5
        if hasattr(app_config, 'get'):
            default_count = app_config.get("exercise_count", 5)
        self.exercise_count_spin.setValue(default_count)
        count_layout.addWidget(self.exercise_count_spin)
        po_layout.addWidget(count_box)
        
        # Add speed control for Speed Mode
        speed_box = QGroupBox("Speed Mode Timer (seconds)")
        speed_layout = QHBoxLayout(speed_box)
        self.speed_timer_spin = QSpinBox()
        self.speed_timer_spin.setRange(1, 10)
        self.speed_timer_spin.setValue(3)  # Default 3 seconds
        speed_layout.addWidget(self.speed_timer_spin)
        po_layout.addWidget(speed_box)

        right_layout.addWidget(self.practice_options_box)

        # -------- Mode Selection --------
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Select Mode:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Free Response", "Multiple Choice"])
        self.mode_combo.setStyleSheet(f"font-size: {FONT_SIZE_MEDIUM}; padding: 4px;")
        self.mode_combo.currentIndexChanged.connect(self.switchMode)
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)
        right_layout.addLayout(mode_layout)

        # -------- Answer Input Stack --------
        self.input_stack = QStackedWidget()
        free_response_page = QWidget()
        fr_layout = QVBoxLayout(free_response_page)
        self.free_response_input = QLineEdit()
        self.free_response_input.setPlaceholderText("Type your answer here...")
        self.free_response_input.setStyleSheet(f"font-size: {FONT_SIZE_LARGE}; padding: {PADDING_SMALL};")
        fr_layout.addWidget(self.free_response_input)
        self.input_stack.addWidget(free_response_page)

        multiple_choice_page = QWidget()
        mc_layout = QVBoxLayout(multiple_choice_page)
        self.mc_button_group = QButtonGroup(multiple_choice_page)
        self.mc_options_layout = QVBoxLayout()
        mc_layout.addLayout(self.mc_options_layout)
        self.input_stack.addWidget(multiple_choice_page)

        right_layout.addWidget(self.input_stack)

        # -------- Navigation Buttons --------
        buttons_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous")
        self.hint_button = QPushButton("Hint")
        self.submit_button = QPushButton("Submit")
        self.next_button = QPushButton("Next")
        for btn in (self.prev_button, self.hint_button, self.submit_button, self.next_button):
            btn.setStyleSheet(f"font-size: {FONT_SIZE_MEDIUM}; padding: {PADDING_SMALL};")
        buttons_layout.addWidget(self.prev_button)
        buttons_layout.addWidget(self.hint_button)
        buttons_layout.addWidget(self.submit_button)
        buttons_layout.addWidget(self.next_button)
        right_layout.addLayout(buttons_layout)

        self.feedback_text = QTextEdit()
        self.feedback_text.setReadOnly(True)
        self.feedback_text.setStyleSheet(f"font-size: {FONT_SIZE_MEDIUM}; padding: {PADDING_MEDIUM};")
        right_layout.addWidget(self.feedback_text)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet(f"height: {PROGRESS_BAR_HEIGHT};")
        right_layout.addWidget(self.progress_bar)

        splitter.addWidget(right_widget)
        # Set splitter sizes
        default_sizes = SPLITTER_SIZES
        if hasattr(app_config, 'get'):
            default_sizes = app_config.get("splitter_sizes", SPLITTER_SIZES)
        splitter.setSizes(default_sizes)

        # Connect buttons
        self.submit_button.clicked.connect(self.submitAnswer)
        self.next_button.clicked.connect(self.nextExercise)
        self.prev_button.clicked.connect(self.prevExercise)
        self.hint_button.clicked.connect(self.provideHint)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.updateStatus("Welcome! Click 'New Exercise' to generate exercises.")

        # Apply dark mode if the config says so
        if self.dark_mode:
            self.applyDarkTheme()

    def createToolBar(self) -> None:
        """
        Create the main toolbar with actions for Reset, New Exercise, Summary, etc.
        """
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        reset_action = QAction("Reset", self)
        reset_action.setToolTip("Reset progress (Ctrl+R)")
        reset_action.triggered.connect(self.resetProgress)
        toolbar.addAction(reset_action)

        new_ex_action = QAction("New Exercise", self)
        new_ex_action.setToolTip("Generate new exercises (Ctrl+N)")
        new_ex_action.triggered.connect(self.generateNewExercise)
        toolbar.addAction(new_ex_action)

        summary_action = QAction("Summary", self)
        summary_action.setToolTip("Generate session summary (Ctrl+S)")
        summary_action.triggered.connect(self.generateSessionSummary)
        toolbar.addAction(summary_action)

        theme_action = QAction("Toggle Theme", self)
        theme_action.setToolTip("Toggle Light/Dark themes (Ctrl+T)")
        theme_action.triggered.connect(self.toggleTheme)
        toolbar.addAction(theme_action)

        translation_action = QAction("Toggle Translation", self)
        translation_action.setToolTip("Show/hide English translation")
        translation_action.triggered.connect(self.toggleTranslation)
        toolbar.addAction(translation_action)
        
        offline_action = QAction("Toggle Offline Mode", self)
        offline_action.setToolTip("Switch between local and GPT generation")
        offline_action.triggered.connect(self.toggleOfflineMode)
        toolbar.addAction(offline_action)
        
        review_action = QAction("Review Mistakes", self)
        review_action.setToolTip("Practice verbs you struggle with")
        review_action.triggered.connect(self.startReviewMode)
        toolbar.addAction(review_action)
        
        stats_action = QAction("View Statistics", self)
        stats_action.setToolTip("See your learning progress")
        stats_action.triggered.connect(self.showStatistics)
        toolbar.addAction(stats_action)
        
        task_mode_action = QAction("Task Mode", self)
        task_mode_action.setToolTip("Practice with real-world scenarios")
        task_mode_action.triggered.connect(self.startTaskMode)
        toolbar.addAction(task_mode_action)
        
        story_mode_action = QAction("Story Mode", self)
        story_mode_action.setToolTip("Practice with connected stories")
        story_mode_action.triggered.connect(self.startStoryMode)
        toolbar.addAction(story_mode_action)
        
        speed_action = QAction("⚡ Speed Mode", self)
        speed_action.setToolTip("Build conversational fluency with timed practice")
        speed_action.triggered.connect(self.startSpeedMode)
        toolbar.addAction(speed_action)
        
        cheat_sheet_action = QAction("📋 Verb Reference", self)
        cheat_sheet_action.setToolTip("Quick conjugation reference")
        cheat_sheet_action.triggered.connect(self.showCheatSheet)
        toolbar.addAction(cheat_sheet_action)
        
        custom_action = QAction("🎨 Custom Practice", self)
        custom_action.setToolTip("Create your own practice session")
        custom_action.triggered.connect(self.startCustomPractice)
        toolbar.addAction(custom_action)
        
        export_action = QAction("💾 Export Progress", self)
        export_action.setToolTip("Save your progress and settings")
        export_action.triggered.connect(self.exportProgress)
        toolbar.addAction(export_action)

    def toggleOfflineMode(self) -> None:
        """Toggle between offline and online exercise generation."""
        self.offline_mode = not self.offline_mode
        mode = "offline (local)" if self.offline_mode else "online (GPT)"
        self.updateStatus(f"Switched to {mode} mode")
        
    def startReviewMode(self) -> None:
        """Start review mode with problematic verbs."""
        review_items = self.progress_tracker.get_verbs_for_review(10)
        if not review_items:
            self.updateStatus("No items need review yet. Keep practicing!")
            return
            
        # Generate exercises for review items
        exercises = []
        for item in review_items[:5]:
            exercise = self.exercise_generator.generate_exercise(
                verb=item['verb'],
                tense=item['tense'],
                person=item['person']
            )
            exercises.append(exercise)
        
        self.exercises = exercises
        self.total_exercises = len(exercises)
        self.current_exercise = 0
        self.progress_bar.setMaximum(self.total_exercises)
        self.updateExercise()
        self.updateStatus("Review mode: Practicing your weak areas")
    
    def startTaskMode(self) -> None:
        """Start task-based learning mode with scenarios."""
        self.task_mode = True
        self.updateStatus("Task Mode: Practice with real-world scenarios")
        
        # Get available scenarios
        scenarios = self.task_scenarios.get_scenario_list()
        scenario_type = random.choice(scenarios)
        
        # Get task sequence
        tasks = self.task_scenarios.get_task_sequence(scenario_type, 5)
        
        # Convert to exercise format
        exercises = []
        for task in tasks:
            exercise = {
                'sentence': f"{task['scenario_title']}\n{task['scenario_context']}\n\n{task['goal']}:\n{task['template']}",
                'answer': self.task_scenarios.conjugator.conjugate(task['verb'], task['tense'], task['person']),
                'verb': task['verb'],
                'tense': task['tense'],
                'person': task['person'],
                'choices': self._generate_task_choices(task),
                'translation': task['prompt'],
                'context': task['scenario_context'],
                'goal': task['goal'],
                'task_data': task
            }
            exercises.append(exercise)
        
        self.exercises = exercises
        self.total_exercises = len(exercises)
        self.current_exercise = 0
        self.progress_bar.setMaximum(self.total_exercises)
        self.updateExercise()
    
    def startStoryMode(self) -> None:
        """Start story mode with connected discourse."""
        self.updateStatus("Story Mode: Practice with connected narratives")
        
        # Get selected tenses
        selected_tenses = self.getSelectedTenses()
        tense_map = {
            'Present': 'present',
            'Preterite': 'preterite',
            'Imperfect': 'imperfect'
        }
        
        # Choose appropriate tense for story
        story_tense = 'preterite'  # Default
        for gui_tense in selected_tenses:
            if gui_tense in tense_map:
                story_tense = tense_map[gui_tense]
                break
        
        # Generate story sequence
        exercises = self.exercise_generator.generate_story_sequence(story_tense, 5)
        
        self.exercises = exercises
        self.total_exercises = len(exercises)
        self.current_exercise = 0
        self.progress_bar.setMaximum(self.total_exercises)
        self.updateExercise()
        self.updateStatus(f"Story: {exercises[0].get('story_title', 'Connected Story')}")
    
    def _generate_task_choices(self, task: Dict[str, Any]) -> List[str]:
        """Generate choices for task-based exercise."""
        correct = self.task_scenarios.conjugator.conjugate(task['verb'], task['tense'], task['person'])
        choices = [correct]
        
        # Add related forms
        for person in range(6):
            if person != task['person']:
                form = self.task_scenarios.conjugator.conjugate(task['verb'], task['tense'], person)
                if form and form not in choices:
                    choices.append(form)
                    if len(choices) >= 4:
                        break
        
        return choices[:4]
    
    def startSpeedMode(self) -> None:
        """Start speed practice mode for conversational fluency."""
        self.speed_mode = True
        
        # Get user preferences
        time_limit = self.speed_timer_spin.value()
        exercise_count = self.exercise_count_spin.value()
        selected_verbs = self.specific_verbs_input.text().strip()
        
        self.updateStatus(f"⚡ Speed Mode: {time_limit} seconds per verb! Build conversational fluency.")
        
        # Generate speed round with user settings
        if selected_verbs:
            # Use user's specific verbs
            verbs = [v.strip() for v in selected_verbs.split(',')]
            self.speed_practice.essential_verbs = verbs
        
        # Calculate duration based on user settings
        duration = exercise_count * time_limit
        exercises = self.speed_practice.generate_speed_round(duration)
        
        # Convert to exercise format
        for ex in exercises:
            ex['sentence'] = f"{ex['trigger']}\n\n{ex['scenario']}"
            ex['translation'] = f"Time limit: {ex['time_limit']} seconds"
        
        self.exercises = exercises
        self.total_exercises = len(exercises)
        self.current_exercise = 0
        self.progress_bar.setMaximum(self.total_exercises)
        
        # Start timer for first exercise
        self.start_time = time.time()
        self.updateExercise()
        
        # Show speed tips
        QMessageBox.information(self, "Speed Mode Tips",
            "⚡ SPEED MODE - Build Conversational Fluency\n\n"
            "• You have 3 seconds per verb\n"
            "• Focus on SPEED, not perfection\n"
            "• This trains automatic recall\n"
            "• In real conversation, slow = awkward\n\n"
            "Ready? Go!")
    
    def startCustomPractice(self) -> None:
        """Let user create completely custom practice session."""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("🎨 Custom Practice Creator")
        dialog.setGeometry(200, 200, 600, 400)
        
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            "Create your own practice sentences!\n"
            "Format: sentence with _____ (verb, tense, person)\n"
            "Example: Mañana _____ al médico (ir, future, yo)"
        )
        layout.addWidget(instructions)
        
        # Text area for custom exercises
        self.custom_text = QTextEdit()
        self.custom_text.setPlainText(
            "# Custom Practice Sentences\n"
            "Ayer _____ una película (ver, preterite, yo)\n"
            "¿_____ conmigo? (venir, present, tú)\n"
            "Ellos _____ muy cansados (estar, imperfect, ellos)\n"
        )
        layout.addWidget(self.custom_text)
        
        # Process button
        process_btn = QPushButton("Create Practice Session")
        process_btn.clicked.connect(lambda: self.processCustomExercises(dialog))
        layout.addWidget(process_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def processCustomExercises(self, dialog):
        """Process user's custom exercises."""
        import re
        
        text = self.custom_text.toPlainText()
        lines = [line.strip() for line in text.split('\n') if line.strip() and not line.startswith('#')]
        
        exercises = []
        person_map = {
            'yo': 0, 'tú': 1, 'él': 2, 'ella': 2, 'usted': 2,
            'nosotros': 3, 'vosotros': 4, 'ellos': 5, 'ellas': 5, 'ustedes': 5
        }
        
        tense_map = {
            'present': 'present', 'presente': 'present',
            'preterite': 'preterite', 'pretérito': 'preterite',
            'imperfect': 'imperfect', 'imperfecto': 'imperfect',
            'future': 'future', 'futuro': 'future',
            'conditional': 'conditional', 'condicional': 'conditional',
            'subjunctive': 'present_subjunctive', 'subjuntivo': 'present_subjunctive'
        }
        
        for line in lines:
            # Parse format: sentence _____ (verb, tense, person)
            match = re.search(r'(.*?)_+\s*\((.*?)\)', line)
            if match:
                sentence_part = match.group(1)
                params = match.group(2).split(',')
                
                if len(params) >= 3:
                    verb = params[0].strip()
                    tense = tense_map.get(params[1].strip().lower(), 'present')
                    person_str = params[2].strip().lower()
                    person = person_map.get(person_str, 0)
                    
                    answer = self.conjugator.conjugate(verb, tense, person)
                    if answer:
                        # Generate choices
                        choices = [answer]
                        for p in range(6):
                            if p != person:
                                form = self.conjugator.conjugate(verb, tense, p)
                                if form and form not in choices:
                                    choices.append(form)
                                    if len(choices) >= 4:
                                        break
                        
                        exercises.append({
                            'sentence': line.replace(match.group(0), sentence_part + "_____"),
                            'answer': answer,
                            'choices': choices[:4],
                            'verb': verb,
                            'tense': tense,
                            'person': person,
                            'translation': f"Custom: {verb} ({tense}, {person_str})",
                            'context': 'User-created exercise'
                        })
        
        if exercises:
            self.exercises = exercises
            self.total_exercises = len(exercises)
            self.current_exercise = 0
            self.progress_bar.setMaximum(self.total_exercises)
            self.updateExercise()
            self.updateStatus(f"Created {len(exercises)} custom exercises!")
            dialog.accept()
        else:
            QMessageBox.warning(dialog, "No Valid Exercises", 
                               "Could not parse any valid exercises. Check format.")
    
    def showCheatSheet(self) -> None:
        """Show quick conjugation reference for current verb or common verbs."""
        # Create a simple reference table
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Quick Verb Reference")
        dialog.setGeometry(200, 200, 600, 400)
        
        layout = QVBoxLayout()
        table = QTableWidget()
        
        # Show current verb if in exercise, otherwise show ser/estar/tener
        if self.exercises and 0 <= self.current_exercise < len(self.exercises):
            verb = self.exercises[self.current_exercise].get('verb', 'ser')
        else:
            verb = 'ser'  # Default to most important verb
        
        # Get all conjugations
        table.setRowCount(6)
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(['Person', 'Present', 'Preterite', 'Imperfect'])
        
        persons = ['yo', 'tú', 'él/ella', 'nosotros', 'vosotros', 'ellos']
        for i, person in enumerate(persons):
            table.setItem(i, 0, QTableWidgetItem(person))
            
            # Present
            form = self.conjugator.conjugate(verb, 'present', i)
            table.setItem(i, 1, QTableWidgetItem(form or '-'))
            
            # Preterite
            form = self.conjugator.conjugate(verb, 'preterite', i)
            table.setItem(i, 2, QTableWidgetItem(form or '-'))
            
            # Imperfect
            form = self.conjugator.conjugate(verb, 'imperfect', i)
            table.setItem(i, 3, QTableWidgetItem(form or '-'))
        
        table.resizeColumnsToContents()
        layout.addWidget(QLabel(f"Conjugation for: {verb}"))
        layout.addWidget(table)
        
        # Add quick tips
        tips = QLabel(
            "💡 Quick Tips:\n"
            "• Regular -AR: o, as, a, amos, áis, an\n"
            "• Regular -ER: o, es, e, emos, éis, en\n"
            "• Regular -IR: o, es, e, imos, ís, en"
        )
        layout.addWidget(tips)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def exportProgress(self) -> None:
        """Export user progress and custom exercises to JSON."""
        from PyQt5.QtWidgets import QFileDialog
        import json
        from datetime import datetime
        
        # Gather all data
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'statistics': self.progress_tracker.get_statistics(),
            'weak_areas': self.progress_tracker.get_weak_areas(10),
            'speed_practice': {
                'response_times': self.speed_practice.response_times,
                'weak_spots': self.speed_practice.get_weak_spots()
            },
            'current_exercises': self.exercises,
            'settings': {
                'offline_mode': self.offline_mode,
                'dark_mode': self.dark_mode,
                'show_translation': self.show_translation
            }
        }
        
        # Save to file
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Progress", 
            f"spanish_progress_{datetime.now().strftime('%Y%m%d')}.json",
            "JSON Files (*.json)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                self.updateStatus(f"Progress exported to {filename}")
                QMessageBox.information(self, "Export Successful", 
                                      f"Your progress has been saved to:\n{filename}")
            except Exception as e:
                QMessageBox.warning(self, "Export Failed", f"Could not export: {str(e)}")
    
    def showStatistics(self) -> None:
        """Show learning statistics dialog."""
        stats = self.progress_tracker.get_statistics()
        weak_areas = self.progress_tracker.get_weak_areas(5)
        
        message = f"📊 Your Progress Statistics\n\n"
        message += f"Total Attempts: {stats['total_attempts']}\n"
        message += f"Correct: {stats['correct_attempts']}\n"
        message += f"Accuracy: {stats['accuracy']:.1f}%\n"
        message += f"Unique Verbs Practiced: {stats['unique_verbs']}\n\n"
        
        if weak_areas:
            message += "Areas to Focus On:\n"
            for area in weak_areas[:3]:
                accuracy = (area['correct_count'] / (area['correct_count'] + area['incorrect_count'])) * 100
                message += f"• {area['verb']} ({area['tense']}): {accuracy:.0f}% accuracy\n"
        
        QMessageBox.information(self, "Learning Statistics", message)
    
    def toggleTranslation(self) -> None:
        """
        Toggle the visibility of the English translation label.
        """
        self.show_translation = not self.show_translation
        app_config.set("show_translation", self.show_translation)

        self.translation_label.setVisible(self.show_translation)
        self.updateExercise()
        self.updateStatus("Translation " + ("displayed." if self.show_translation else "hidden."))

    def toggleTheme(self) -> None:
        """
        Toggle between dark mode and light mode. Saves setting to config.
        """
        if self.dark_mode:
            # Switch to light theme
            self.setStyleSheet("")
            self.dark_mode = False
            app_config.set("dark_mode", False)
            self.updateStatus("Switched to light theme.")
        else:
            # Switch to dark theme
            self.applyDarkTheme()
            self.dark_mode = True
            app_config.set("dark_mode", True)
            self.updateStatus("Switched to dark theme.")

    def applyDarkTheme(self) -> None:
        """
        Apply a basic dark stylesheet to the entire app.
        """
        dark_stylesheet = """
            QMainWindow { background-color: #2b2b2b; color: #ffffff; }
            QLabel, QGroupBox, QStatusBar, QToolBar { color: #ffffff; }
            QLineEdit, QTextEdit, QComboBox, QProgressBar { background-color: #3c3f41; color: #ffffff; }
            QPushButton { background-color: #3c3f41; color: #ffffff; }
            QPushButton:hover { background-color: #4c5052; }
        """
        self.setStyleSheet(dark_stylesheet)

    def updateSessionStats(self) -> None:
        """
        Update the stats label based on current exercise index and correctness stats.
        """
        if self.total_exercises > 0:
            label_text = (f"Exercises: {self.current_exercise + 1}/{self.total_exercises} | "
                          f"Correct: {self.stats.total_correct}")
        else:
            label_text = "Exercises: 0 | Correct: 0"
        self.stats_label.setText(label_text)

    def updateStatus(self, message: str) -> None:
        """
        Display a temporary message in the status bar.
        """
        self.status_bar.showMessage(message, 5000)

    def updateExercise(self) -> None:
        """
        Display the current exercise data in the UI.
        """
        if self.total_exercises == 0 or not (0 <= self.current_exercise < self.total_exercises):
            return

        exercise = self.exercises[self.current_exercise]
        # Combine context and sentence if context is provided
        context_text = exercise.get("context", "")
        sentence_text = exercise.get("sentence", "")
        if context_text:
            full_text = context_text + "\n\n" + sentence_text
        else:
            full_text = sentence_text

        self.sentence_label.setText(full_text)

        # Show translation if enabled
        if self.show_translation and "translation" in exercise:
            self.translation_label.setText(exercise["translation"])
        else:
            self.translation_label.setText("")

        self.feedback_text.clear()
        self.progress_bar.setValue(self.current_exercise + 1)
        self.updateStatus(f"Exercise {self.current_exercise + 1} of {self.total_exercises}")

        mode = self.mode_combo.currentText()
        if mode == "Free Response":
            self.free_response_input.clear()
        else:
            # Multiple Choice
            choices = list(exercise["choices"])
            random.shuffle(choices)
            self.populateMultipleChoice(choices)

        self.updateSessionStats()

    def populateMultipleChoice(self, choices: List[str]) -> None:
        """
        Populate multiple choice options in the dedicated layout.
        """
        while self.mc_options_layout.count():
            child = self.mc_options_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.mc_button_group = QButtonGroup()
        for choice in choices:
            radio = QRadioButton(choice)
            self.mc_button_group.addButton(radio)
            self.mc_options_layout.addWidget(radio)

        # Optionally select the first radio button
        if self.mc_button_group.buttons():
            self.mc_button_group.buttons()[0].setChecked(True)

    def switchMode(self) -> None:
        """
        Switch between Free Response and Multiple Choice modes in the UI stack.
        """
        mode = self.mode_combo.currentText()
        if mode == "Free Response":
            self.input_stack.setCurrentIndex(0)
        else:
            self.input_stack.setCurrentIndex(1)
        self.updateExercise()

    def getSelectedTenses(self) -> List[str]:
        """
        Return a list of selected verb tenses from the UI checkboxes.
        """
        return [tense for tense, cb in self.tense_checkboxes.items() if cb.isChecked()]

    def getSelectedPersons(self) -> List[str]:
        """
        Return a list of selected grammatical persons from the UI checkboxes.
        """
        return [form for form, cb in self.person_checkboxes.items() if cb.isChecked()]

    def getUserAnswer(self) -> str:
        """
        Retrieve the user's current answer from the active mode (Free or MC).
        """
        mode = self.mode_combo.currentText()
        if mode == "Free Response":
            return self.free_response_input.text().strip()
        else:
            for button in self.mc_button_group.buttons():
                if button.isChecked():
                    return button.text().strip()
        return ""

    def submitAnswer(self) -> None:
        """
        Validate the user's answer and request a GPT explanation.
        """
        if self.total_exercises == 0:
            self.updateStatus("No exercise available. Please generate new exercises.")
            return

        exercise = self.exercises[self.current_exercise]
        user_answer = self.getUserAnswer()
        if not user_answer:
            self.updateStatus("Please enter an answer before submitting.")
            return

        correct_answer = exercise["answer"].strip()
        strictness = app_config.get("answer_strictness", "normal")
        is_correct, base_feedback = check_answer(user_answer, correct_answer, strictness)

        # Record attempt in stats
        self.stats.record_attempt(exercise, user_answer, is_correct)
        
        # Record in progress tracker if we have verb info
        if 'verb' in exercise and 'tense' in exercise and 'person' in exercise:
            # Map person label to index
            person_index = 0
            for i, label in enumerate(PERSON_LABELS):
                if label == exercise.get('person', ''):
                    person_index = i
                    break
            
            self.progress_tracker.record_attempt(
                exercise['verb'],
                exercise['tense'],
                person_index,
                user_answer,
                correct_answer,
                is_correct
            )

        # Check if this is speed mode
        if self.speed_mode and self.start_time:
            response_time = time.time() - self.start_time
            speed_result = self.speed_practice.evaluate_speed_response(
                exercise['verb'], 
                exercise.get('person', 0),
                user_answer,
                response_time
            )
            
            feedback = speed_result['feedback']
            feedback += f"\n\nTime: {response_time:.1f}s - {speed_result['speed_rating']}"
            if speed_result['improvement']:
                feedback += f"\n{speed_result['improvement']:.1f}s faster than average!"
            
            self.feedback_text.setText(feedback)
            self.updateStatus(speed_result['speed_rating'])
            
            # Reset timer for next exercise
            self.start_time = time.time()
            
        # Check if this is a task-based exercise
        elif 'task_data' in exercise:
            # Evaluate communicative success
            task_result = self.task_scenarios.evaluate_response(user_answer, exercise['task_data'])
            
            # Enhanced feedback for task mode
            feedback = task_result['feedback']
            if task_result['communicatively_successful']:
                feedback += f"\n\n✅ Task goal achieved: {exercise['goal']}"
            else:
                feedback += f"\n\n📝 Correct form: {task_result['correct_form']}"
            
            self.feedback_text.setText(feedback)
            self.updateStatus("Task evaluated - focus on communication!")
        elif self.offline_mode:
            # Provide simple feedback in offline mode
            self.feedback_text.setText(base_feedback)
            self.updateStatus("Answer submitted.")
        else:
            self.generateGPTExplanationAsync(
                user_answer, correct_answer, is_correct,
                exercise.get("sentence", ""), base_feedback
            )

    def generateGPTExplanationAsync(
        self,
        user_answer: str,
        correct_answer: str,
        is_correct: bool,
        sentence: str,
        base_feedback: str
    ) -> None:
        """
        Trigger an asynchronous GPT call to provide a grammar-focused explanation.
        """
        prompt = (
            "You are an expert Spanish tutor specializing in LATAM Spanish. "
            f"Sentence: \"{sentence}\"\n"
            f"Correct Answer: \"{correct_answer}\"\n"
            f"Learner's Answer: \"{user_answer}\"\n"
            f"Is the learner's answer correct? {'Yes' if is_correct else 'No'}\n\n"
            "Provide a concise explanation in LATAM Spanish that focuses strictly on the grammatical structure. "
            "Do not include extra praise or filler. "
        )
        worker = GPTWorkerRunnable(
            prompt,
            model=app_config.get("api_model", "gpt-4o"),
            max_tokens=app_config.get("max_tokens", 600),
            temperature=app_config.get("temperature", 0.5)
        )
        worker.signals.result.connect(lambda result: self.handleExplanationResult(result, base_feedback, user_answer))
        self.threadpool.start(worker)

    def handleExplanationResult(self, result: str, base_feedback: str, user_answer: str) -> None:
        """
        Combine the GPT explanation with base feedback and display it.
        Also append to self.responses with memory management.
        """
        full_feedback = base_feedback + "\n\n" + result
        self.feedback_text.setText(full_feedback)

        entry = {
            "exercise": self.current_exercise,
            "sentence": self.exercises[self.current_exercise].get("sentence", ""),
            "translation": self.exercises[self.current_exercise].get("translation", ""),
            "user_answer": user_answer,
            "correct": full_feedback.startswith("Correct"),
            "explanation": result
        }
        self.responses.append(entry)

        # (7) Trim stored responses if exceeding max
        if len(self.responses) > self.max_stored_responses:
            self.responses = self.responses[-self.max_stored_responses:]

        self.updateStatus("Answer submitted.")
        self.updateSessionStats()

    def provideHint(self) -> None:
        """
        Provide a subtle hint about the current exercise via GPT.
        """
        if self.total_exercises == 0:
            self.updateStatus("No exercise available to hint. Please generate new exercises.")
            return

        exercise = self.exercises[self.current_exercise]
        prompt = (
            f"You are an expert Spanish tutor specializing in LATAM Spanish. "
            f"Given the following realistic scenario where a verb is missing:\n"
            f"Sentence: \"{exercise.get('sentence', '')}\"\n"
            f"Correct Conjugation: \"{exercise['answer']}\"\n\n"
            "Please provide a subtle, context-based hint in LATAM Spanish "
            "that gently guides the learner toward the correct verb form, "
            "without revealing the answer directly."
        )
        worker = GPTWorkerRunnable(
            prompt,
            model=app_config.get("api_model", "gpt-4o"),
            max_tokens=100,
            temperature=app_config.get("temperature", 0.5)
        )
        worker.signals.result.connect(self.handleHintResult)
        self.threadpool.start(worker)

    def handleHintResult(self, result: str) -> None:
        """
        Display the hint from GPT in the feedback text box.
        """
        self.feedback_text.setText("Hint: " + result)
        self.updateStatus("Hint provided.")

    def nextExercise(self) -> None:
        """
        Move to the next exercise if available.
        """
        if self.total_exercises == 0:
            self.updateStatus("No exercise available. Please generate new exercises.")
            return

        if self.current_exercise < self.total_exercises - 1:
            self.current_exercise += 1
            self.updateExercise()
        else:
            self.updateStatus("You have completed all exercises!")
        self.updateSessionStats()

    def prevExercise(self) -> None:
        """
        Move to the previous exercise if available.
        """
        if self.total_exercises == 0:
            self.updateStatus("No exercise available. Please generate new exercises.")
            return

        if self.current_exercise > 0:
            self.current_exercise -= 1
            self.updateExercise()
        self.updateSessionStats()

    def resetProgress(self) -> None:
        """
        Reset the current exercise index, correct count, and responses.
        """
        self.current_exercise = 0
        self.stats.total_correct = 0
        self.stats.total_attempted = 0
        self.responses.clear()
        self.updateExercise()
        self.updateStatus("Progress has been reset.")
        self.updateSessionStats()

    def generateNewExercise(self) -> None:
        """
        Generate new exercises either locally or from GPT API based on mode.
        """
        selected_tenses = self.getSelectedTenses()
        selected_persons = self.getSelectedPersons()
        difficulty = self.difficulty_combo.currentText().lower()
        count = self.exercise_count_spin.value()
        specific_verbs = self.specific_verbs_input.text().strip()
        
        if self.offline_mode:
            # Generate exercises locally
            self.updateStatus("Generating exercises locally...")
            
            # Map GUI tense names to internal tense names
            tense_map = {
                'Present': 'present',
                'Preterite': 'preterite',
                'Imperfect': 'imperfect',
                'Future': 'future',
                'Conditional': 'conditional',
                'Subjunctive': 'present_subjunctive'
            }
            
            # Map person labels to indices
            person_map = {
                '1st person singular': 0,
                '2nd person singular': 1,
                '3rd person singular': 2,
                '1st person plural': 3,
                '2nd person plural': 4,
                '3rd person plural': 5
            }
            
            tenses = [tense_map[t] for t in selected_tenses if t in tense_map] or None
            persons = [person_map[p] for p in selected_persons if p in person_map] or None
            verbs = [v.strip() for v in specific_verbs.split(',')] if specific_verbs else None
            
            exercises = self.exercise_generator.generate_batch(
                count=count,
                verbs=verbs,
                tenses=tenses,
                persons=persons,
                difficulty=difficulty
            )
            
            self.exercises = exercises
            self.total_exercises = len(exercises)
            self.progress_bar.setMaximum(self.total_exercises)
            self.current_exercise = 0
            self.updateExercise()
            self.updateStatus(f"Generated {len(exercises)} exercises locally!")
            return
        
        # Online mode - use GPT
        tense_text = ", ".join(selected_tenses) if selected_tenses else "any common tense"
        person_text = ", ".join(selected_persons) if selected_persons else "any form"
        theme_context = self.theme_input.text().strip()

        prompt = (
            f"Generate {count} unique Spanish exercises at {difficulty} level that reflect authentic, everyday "
            f"interactions in LATAM contexts. Each exercise should include:\n\n"
            "1. \"context\": Two or three sentences of natural text.\n"
            "2. \"sentence\": A passage with a blank for a missing verb.\n"
            "3. \"answer\": The correct verb form.\n"
            "4. \"choices\": An array of four options (including the correct one).\n"
            "5. \"translation\": English translation with the blank.\n\n"
            "Context Instructions:\n"
            f"- Use ONLY these verb tenses/aspects: {tense_text}.\n"
            f"- Use ONLY these grammatical persons: {person_text}.\n"
        )
        if specific_verbs:
            prompt += f"- Use only these verbs for the blank: {specific_verbs}.\n"
        if theme_context:
            prompt += f"- Theme/Context: {theme_context}.\n"

        prompt += (
            "\nEnsure the examples reflect natural LATAM Spanish. Return a strictly valid JSON array "
            "of objects with no extra formatting."
        )

        # Get model settings
        model = "gpt-4o"
        max_tokens = 600
        temperature = 0.5
        
        if hasattr(app_config, 'get'):
            model = app_config.get("api_model", "gpt-4o")
            max_tokens = app_config.get("max_tokens", 600)
            temperature = app_config.get("temperature", 0.5)
        
        worker = GPTWorkerRunnable(
            prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature
        )
        worker.signals.result.connect(self.handleNewExerciseResult)
        self.threadpool.start(worker)

    def handleNewExerciseResult(self, result: str) -> None:
        """
        Process the exercise generation result from the GPT API.
        """
        logging.info("Raw GPT response for new exercise:\n%s", result)
        exercises_batch = parse_gpt_json(result)

        if not exercises_batch:
            self.updateStatus("Error parsing new exercise. Regenerating...")
            logging.error("Empty or invalid exercise data.")
            self.generateNewExercise()
            return

        # Filter out duplicates based on sentence text
        new_exercises = []
        exercise_log_file = "exercise_log.txt"
        logged_sentences: List[str] = []
        if os.path.exists(exercise_log_file):
            with open(exercise_log_file, "r", encoding="utf-8") as f:
                logged_sentences = [line.strip() for line in f if line.strip()]

        for ex in exercises_batch:
            # Must have required keys
            if ("sentence" in ex or "exercise" in ex) and \
               "answer" in ex and "choices" in ex and "translation" in ex:
                sentence_text = ex.get("sentence", ex.get("exercise"))
                if sentence_text not in logged_sentences:
                    new_exercises.append(ex)
                else:
                    logging.info("Duplicate exercise detected: %s", sentence_text)

        if not new_exercises:
            logging.info("No new unique exercises generated, trying again.")
            self.generateNewExercise()
            return

        self.exercises = new_exercises
        with open(exercise_log_file, "a", encoding="utf-8") as f:
            for ex in new_exercises:
                sentence_text = ex.get("sentence", ex.get("exercise"))
                f.write(sentence_text + "\n")

        self.total_exercises = len(self.exercises)
        self.progress_bar.setMaximum(self.total_exercises)
        self.current_exercise = 0
        self.updateExercise()
        self.updateStatus("New exercises generated!")
        logging.info("New exercises generated: %s", ", ".join(
            [ex.get("sentence", ex.get("exercise", "")) for ex in new_exercises]
        ))

    def generateSessionSummary(self) -> None:
        """
        Summarize the user's performance using GPT.
        """
        session_data = "\n".join(
            f"Exercise {entry['exercise']+1}: Sentence: {entry['sentence']} | "
            f"Your answer: {entry['user_answer']} | Correct: {entry['correct']} | "
            f"Explanation: {entry['explanation']}"
            for entry in self.responses
        )
        prompt = (
            "You are an expert Spanish tutor reviewing a student's practice session:\n"
            f"{session_data}\n\n"
            "Provide a concise summary highlighting correct/incorrect items. "
            "Use clear, encouraging language, but be concise."
        )
        worker = GPTWorkerRunnable(prompt, max_tokens=200)
        worker.signals.result.connect(self.handleSummaryResult)
        self.threadpool.start(worker)

    def handleSummaryResult(self, result: str) -> None:
        """
        Display the generated session summary.
        """
        QMessageBox.information(self, "Session Summary", result)
        self.updateStatus("Session summary generated.")

    # -------------------------------------------------------
    # (11) RESOURCE CLEANUP ENHANCEMENT
    # -------------------------------------------------------
    def closeEvent(self, event) -> None:
        """
        Handle application close event with proper cleanup.
        """
        # Wait for all threads to complete (with a timeout).
        if not self.threadpool.waitForDone(3000):
            logging.warning("Some background threads did not complete in time.")
        
        # Update session in database
        if hasattr(self, 'progress_tracker'):
            verbs_practiced = list(set([ex.get('verb', '') for ex in self.exercises if 'verb' in ex]))
            self.progress_tracker.update_session(
                self.session_id,
                self.stats.total_attempted,
                self.stats.total_correct,
                verbs_practiced
            )
            self.progress_tracker.close()

        # Save session log
        try:
            with open("session_log.txt", "a", encoding="utf-8") as log_file:
                log_file.write("=== Session Log ===\n")
                for entry in self.responses:
                    log_file.write(
                        f"Exercise {entry['exercise']+1}:\n"
                        f"  Sentence: {entry['sentence']}\n"
                        f"  Translation: {entry.get('translation', '')}\n"
                        f"  Your answer: {entry['user_answer']}\n"
                        f"  Correct: {entry['correct']}\n"
                        f"  Explanation: {entry['explanation']}\n\n"
                    )
                log_file.write("=== End Session ===\n\n")
            logging.info("Session log written successfully.")
        except Exception as e:
            logging.error("Error writing session log file: %s", e)

        event.accept()

    def show_setup_wizard(self) -> None:
        """
        Show the first-run setup wizard.
        """
        if SECURITY_AVAILABLE:
            try:
                success = run_setup_wizard(self)
                if success:
                    # Reinitialize API configuration
                    global api_config, api_key, client
                    api_config = APIConfig()
                    api_key = api_config.get_api_key()
                    
                    if api_key:
                        openai.api_key = api_key
                        client = OpenAI(api_key=api_key)
                        self.api_client = client
                        self.updateStatus("Setup completed! API key configured successfully.")
                    else:
                        self.updateStatus("Setup completed in offline mode.")
                else:
                    self.updateStatus("Setup cancelled. Running in offline mode.")
            except Exception as e:
                logging.error(f"Setup wizard error: {e}")
                QMessageBox.warning(self, "Setup Error", 
                                   f"Setup wizard encountered an error: {str(e)}")
    
    def show_security_settings(self) -> None:
        """
        Show security settings dialog.
        """
        if not SECURITY_AVAILABLE:
            QMessageBox.information(self, "Security Settings", 
                                   "Security modules are not available.")
            return
        
        try:
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTabWidget
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Security Settings")
            dialog.setGeometry(200, 200, 600, 400)
            
            layout = QVBoxLayout()
            tabs = QTabWidget()
            
            # API Keys tab
            api_tab = self._create_api_keys_tab()
            tabs.addTab(api_tab, "API Keys")
            
            # Security tab
            security_tab = self._create_security_tab()
            tabs.addTab(security_tab, "Security")
            
            # Backup tab
            backup_tab = self._create_backup_tab()
            tabs.addTab(backup_tab, "Backup")
            
            layout.addWidget(tabs)
            dialog.setLayout(layout)
            dialog.exec_()
            
        except Exception as e:
            logging.error(f"Security settings error: {e}")
            QMessageBox.warning(self, "Error", f"Failed to open security settings: {str(e)}")
    
    def _create_api_keys_tab(self) -> QWidget:
        """
        Create API keys management tab.
        """
        from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QFormLayout, QPushButton, QTextEdit
        
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Current API key info
        info_group = QGroupBox("Current API Configuration")
        info_layout = QFormLayout()
        
        current_key = api_config.get_api_key() if api_config else "Not configured"
        if current_key and len(current_key) > 10:
            display_key = current_key[:6] + "*" * (len(current_key) - 10) + current_key[-4:]
        else:
            display_key = current_key or "None"
        
        info_layout.addRow("API Key:", QLabel(display_key))
        info_layout.addRow("Provider:", QLabel(api_config.get('api.provider', 'openai') if api_config else 'N/A'))
        info_layout.addRow("Model:", QLabel(api_config.get('api.model', 'gpt-4o') if api_config else 'N/A'))
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Actions
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout()
        
        test_button = QPushButton("Test API Key")
        test_button.clicked.connect(self._test_api_key)
        actions_layout.addWidget(test_button)
        
        change_button = QPushButton("Change API Key")
        change_button.clicked.connect(self._change_api_key)
        actions_layout.addWidget(change_button)
        
        remove_button = QPushButton("Remove API Key")
        remove_button.clicked.connect(self._remove_api_key)
        actions_layout.addWidget(remove_button)
        
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        # Status display
        self.api_status_text = QTextEdit()
        self.api_status_text.setMaximumHeight(100)
        self.api_status_text.setReadOnly(True)
        layout.addWidget(QLabel("Status:"))
        layout.addWidget(self.api_status_text)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_security_tab(self) -> QWidget:
        """
        Create security settings tab.
        """
        from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QComboBox, QFormLayout
        
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Storage settings
        storage_group = QGroupBox("Credential Storage")
        storage_layout = QFormLayout()
        
        storage_combo = QComboBox()
        if credentials_manager:
            storage_info = credentials_manager.get_storage_info()
            methods = storage_info.get('supported_methods', [])
            storage_combo.addItems(methods)
            current_method = api_config.get('security.storage_preference', 'auto') if api_config else 'auto'
            if current_method in methods:
                storage_combo.setCurrentText(current_method)
        
        storage_layout.addRow("Storage Method:", storage_combo)
        storage_group.setLayout(storage_layout)
        layout.addWidget(storage_group)
        
        # Security options
        options_group = QGroupBox("Security Options")
        options_layout = QVBoxLayout()
        
        validate_checkbox = QCheckBox("Validate API keys before storing")
        validate_checkbox.setChecked(api_config.get('security.validate_api_keys', True) if api_config else True)
        options_layout.addWidget(validate_checkbox)
        
        audit_checkbox = QCheckBox("Enable security audit logging")
        audit_checkbox.setChecked(api_config.get('security.audit_logging', True) if api_config else True)
        options_layout.addWidget(audit_checkbox)
        
        backup_checkbox = QCheckBox("Create automatic backups")
        backup_checkbox.setChecked(api_config.get('security.backup_enabled', True) if api_config else True)
        options_layout.addWidget(backup_checkbox)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_backup_tab(self) -> QWidget:
        """
        Create backup management tab.
        """
        from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout
        
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Backup list
        layout.addWidget(QLabel("Available Backups:"))
        backup_list = QListWidget()
        layout.addWidget(backup_list)
        
        # Backup actions
        actions_layout = QHBoxLayout()
        
        create_backup_button = QPushButton("Create Backup")
        create_backup_button.clicked.connect(self._create_backup)
        actions_layout.addWidget(create_backup_button)
        
        restore_button = QPushButton("Restore Backup")
        restore_button.clicked.connect(self._restore_backup)
        actions_layout.addWidget(restore_button)
        
        delete_backup_button = QPushButton("Delete Backup")
        delete_backup_button.clicked.connect(self._delete_backup)
        actions_layout.addWidget(delete_backup_button)
        
        layout.addLayout(actions_layout)
        
        widget.setLayout(layout)
        return widget
    
    def _test_api_key(self) -> None:
        """
        Test the current API key.
        """
        if not api_config:
            self.api_status_text.setText("API configuration not available.")
            return
        
        self.api_status_text.setText("Testing API key...")
        QApplication.processEvents()
        
        try:
            test_result = api_config.test_api_key()
            if test_result.get('success'):
                self.api_status_text.setText(f"✅ API key test successful!\nModel: {test_result.get('info', {}).get('model_used', 'Unknown')}")
            else:
                error = test_result.get('error', 'Unknown error')
                self.api_status_text.setText(f"❌ API key test failed:\n{error}")
        except Exception as e:
            self.api_status_text.setText(f"❌ Test error: {str(e)}")
    
    def _change_api_key(self) -> None:
        """
        Change the API key.
        """
        from PyQt5.QtWidgets import QInputDialog
        
        text, ok = QInputDialog.getText(self, 'Change API Key', 'Enter new API key:', QLineEdit.Password)
        
        if ok and text:
            try:
                success = api_config.set_api_key(text)
                if success:
                    # Update global client
                    global api_key, client
                    api_key = text
                    openai.api_key = text
                    client = OpenAI(api_key=text)
                    self.api_client = client
                    
                    self.api_status_text.setText("✅ API key updated successfully!")
                    self.updateStatus("API key updated")
                else:
                    self.api_status_text.setText("❌ Failed to update API key")
            except Exception as e:
                self.api_status_text.setText(f"❌ Error updating API key: {str(e)}")
    
    def _remove_api_key(self) -> None:
        """
        Remove the current API key.
        """
        reply = QMessageBox.question(self, 'Remove API Key', 
                                   'Are you sure you want to remove the API key?\nThe application will run in offline mode.',
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                if credentials_manager:
                    success = credentials_manager.delete_credential('openai_api_key')
                    if success:
                        # Update global state
                        global api_key, client
                        api_key = ""
                        client = None
                        self.api_client = None
                        
                        self.api_status_text.setText("✅ API key removed. Running in offline mode.")
                        self.updateStatus("Switched to offline mode")
                    else:
                        self.api_status_text.setText("❌ Failed to remove API key")
                else:
                    self.api_status_text.setText("❌ Credentials manager not available")
            except Exception as e:
                self.api_status_text.setText(f"❌ Error removing API key: {str(e)}")
    
    def _create_backup(self) -> None:
        """
        Create a backup.
        """
        QMessageBox.information(self, "Backup", "Backup functionality will be implemented.")
    
    def _restore_backup(self) -> None:
        """
        Restore from backup.
        """
        QMessageBox.information(self, "Restore", "Restore functionality will be implemented.")
    
    def _delete_backup(self) -> None:
        """
        Delete a backup.
        """
        QMessageBox.information(self, "Delete", "Delete backup functionality will be implemented.")


# -------------------------------------------------------
# MAIN ENTRY POINT
# (10) UNIT TESTS can be in a separate file `test_spanish_app.py`
# -------------------------------------------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SpanishConjugationGUI()
    window.show()
    sys.exit(app.exec_())
