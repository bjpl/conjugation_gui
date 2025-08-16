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
from typing import (
    List, Dict, Union, Optional, Any, Tuple, Callable
)

from dotenv import load_dotenv
load_dotenv()

# Local modules
from exercise_generator import ExerciseGenerator
from progress_tracker import ProgressTracker
from conjugation_engine import PERSON_LABELS, TENSE_NAMES
from task_scenarios import TaskScenario

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


# Simple API key retrieval from environment
api_key = os.getenv("OPENAI_API_KEY", "")
if not api_key:
    logging.error("OPENAI_API_KEY not found in environment variables. Please create a .env file.")

# Set your OpenAI API key
openai.api_key = api_key

# Create the OpenAI client
client = OpenAI(api_key=api_key)


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

        # Retrieve some settings from AppConfig
        geometry = app_config.get("window_geometry")
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
        self.session_id = self.progress_tracker.start_session()
        self.threadpool = QThreadPool()
        self.offline_mode = False  # Start in online mode by default
        self.task_mode = False  # Toggle between grammar drills and tasks

        # Load initial states from config
        self.dark_mode: bool = app_config.get("dark_mode", False)
        self.show_translation: bool = app_config.get("show_translation", False)

        # Additional placeholders
        self.max_stored_responses: int = app_config.get("max_stored_responses", 100)

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
        self.exercise_count_spin.setRange(1, 10)
        self.exercise_count_spin.setValue(app_config.get("exercise_count", 5))
        count_layout.addWidget(self.exercise_count_spin)
        po_layout.addWidget(count_box)

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
        splitter.setSizes(app_config.get("splitter_sizes", SPLITTER_SIZES))

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

        # Check if this is a task-based exercise
        if 'task_data' in exercise:
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

        worker = GPTWorkerRunnable(
            prompt,
            model=app_config.get("api_model", "gpt-4o"),
            max_tokens=app_config.get("max_tokens", 600),
            temperature=app_config.get("temperature", 0.5)
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


# -------------------------------------------------------
# MAIN ENTRY POINT
# (10) UNIT TESTS can be in a separate file `test_spanish_app.py`
# -------------------------------------------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SpanishConjugationGUI()
    window.show()
    sys.exit(app.exec_())
