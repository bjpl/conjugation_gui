# Spanish Conjugation Practice App - API Reference 📖

This document provides comprehensive API documentation for developers working with the Spanish Conjugation Practice application codebase.

## 🏗️ Core Components

### 1. SpanishConjugator Class

The main engine for Spanish verb conjugation logic.

```python
class SpanishConjugator:
    """
    Core Spanish verb conjugation engine.
    
    Handles regular and irregular verbs across all major tenses and persons.
    Provides validation, error handling, and extensible verb management.
    """
```

#### Methods

##### `__init__(self, verb_data_file: str = None)`
Initialize the conjugator with optional custom verb data.

**Parameters:**
- `verb_data_file` (str, optional): Path to custom verb data JSON file

**Example:**
```python
# Use default verb data
conjugator = SpanishConjugator()

# Use custom verb data
conjugator = SpanishConjugator("custom_verbs.json")
```

##### `conjugate(self, verb: str, tense: str, person: str) -> str`
Conjugate a Spanish verb in the specified tense and person.

**Parameters:**
- `verb` (str): Infinitive form of the verb (e.g., "hablar", "ser")
- `tense` (str): Target tense (see TENSE_NAMES for valid options)
- `person` (str): Target person (see PERSON_LABELS for valid options)

**Returns:**
- `str`: Conjugated form of the verb

**Raises:**
- `ValueError`: If verb, tense, or person is invalid
- `ConjugationError`: If conjugation fails for any reason

**Example:**
```python
conjugator = SpanishConjugator()

# Regular verb
result = conjugator.conjugate("hablar", "present", "yo")
print(result)  # "hablo"

# Irregular verb
result = conjugator.conjugate("ser", "present", "tú")
print(result)  # "eres"
```

##### `is_irregular(self, verb: str) -> bool`
Check if a verb is irregular.

**Parameters:**
- `verb` (str): Infinitive form of the verb

**Returns:**
- `bool`: True if verb is irregular, False otherwise

**Example:**
```python
print(conjugator.is_irregular("hablar"))  # False
print(conjugator.is_irregular("ser"))     # True
```

##### `get_all_conjugations(self, verb: str) -> Dict[str, Dict[str, str]]`
Get all conjugations for a verb across all tenses and persons.

**Parameters:**
- `verb` (str): Infinitive form of the verb

**Returns:**
- `Dict[str, Dict[str, str]]`: Nested dictionary with tenses and persons as keys

**Example:**
```python
all_forms = conjugator.get_all_conjugations("hablar")
present_forms = all_forms["present"]
print(present_forms["yo"])    # "hablo"
print(present_forms["tú"])    # "hablas"
```

##### `validate_verb(self, verb: str) -> bool`
Validate if a string is a properly formatted Spanish verb.

**Parameters:**
- `verb` (str): String to validate

**Returns:**
- `bool`: True if valid Spanish verb format

**Example:**
```python
print(conjugator.validate_verb("hablar"))  # True
print(conjugator.validate_verb("hello"))   # False
```

#### Properties

##### `supported_tenses -> List[str]`
List of all supported tense names.

##### `supported_persons -> List[str]`
List of all supported person labels.

##### `irregular_verbs -> Set[str]`
Set of all irregular verbs in the database.

### 2. ExerciseGenerator Class

Generates practice exercises with various difficulty levels and types.

```python
class ExerciseGenerator:
    """
    Creates and manages Spanish conjugation practice exercises.
    
    Supports multiple exercise types, difficulty scaling, and AI-powered
    content generation when API keys are available.
    """
```

#### Methods

##### `__init__(self, conjugator: SpanishConjugator, api_client=None)`
Initialize exercise generator with conjugation engine and optional AI client.

**Parameters:**
- `conjugator` (SpanishConjugator): Instance of conjugation engine
- `api_client` (optional): OpenAI API client for enhanced features

##### `generate_exercise(self, **kwargs) -> Exercise`
Generate a new practice exercise based on specified parameters.

**Parameters (kwargs):**
- `tenses` (List[str]): List of tenses to include
- `persons` (List[str]): List of persons to include  
- `difficulty` (str): "beginner", "intermediate", or "advanced"
- `verbs` (List[str], optional): Specific verbs to use
- `theme` (str, optional): Thematic context (travel, food, etc.)
- `exercise_type` (str): "fill_blank", "multiple_choice", "translation"

**Returns:**
- `Exercise`: Generated exercise object

**Example:**
```python
generator = ExerciseGenerator(conjugator)

exercise = generator.generate_exercise(
    tenses=["present", "preterite"],
    persons=["yo", "tú"],
    difficulty="intermediate",
    theme="travel"
)
```

##### `create_speed_challenge(self, time_limit: int = 5) -> SpeedChallenge`
Create a speed-based practice challenge.

**Parameters:**
- `time_limit` (int): Time limit in seconds per question

**Returns:**
- `SpeedChallenge`: Speed challenge object

##### `generate_story_exercise(self, length: int = 5) -> StoryExercise`
Generate a narrative-based exercise with connected sentences.

**Parameters:**
- `length` (int): Number of sentences in the story

**Returns:**
- `StoryExercise`: Story-based exercise object

#### Exercise Types

##### `Exercise` Class
```python
@dataclass
class Exercise:
    id: str
    type: str
    question: str
    correct_answer: str
    distractors: List[str]  # For multiple choice
    hint: str
    explanation: str
    difficulty: str
    tense: str
    person: str
    verb: str
    context: str
```

##### `SpeedChallenge` Class
```python
@dataclass
class SpeedChallenge:
    exercises: List[Exercise]
    time_limit: int
    total_questions: int
    scoring_multiplier: float
```

##### `StoryExercise` Class
```python
@dataclass  
class StoryExercise:
    story_text: str
    blanks: List[Exercise]
    narrative_theme: str
    coherence_level: str
```

### 3. ProgressTracker Class

Manages user progress, statistics, and spaced repetition scheduling.

```python
class ProgressTracker:
    """
    SQLite-based progress tracking and analytics system.
    
    Implements spaced repetition algorithm, detailed statistics,
    and learning velocity analysis.
    """
```

#### Methods

##### `__init__(self, db_path: str = "progress.db")`
Initialize progress tracker with database.

**Parameters:**
- `db_path` (str): Path to SQLite database file

##### `record_attempt(self, verb: str, tense: str, person: str, correct: bool, response_time: float)`
Record a practice attempt.

**Parameters:**
- `verb` (str): The verb that was practiced
- `tense` (str): The tense used
- `person` (str): The person used
- `correct` (bool): Whether the answer was correct
- `response_time` (float): Time taken to respond in seconds

**Example:**
```python
tracker = ProgressTracker()
tracker.record_attempt("hablar", "present", "yo", True, 2.3)
```

##### `get_verb_stats(self, verb: str) -> Dict[str, Any]`
Get statistics for a specific verb.

**Parameters:**
- `verb` (str): Verb to get statistics for

**Returns:**
- `Dict[str, Any]`: Statistics including accuracy, attempts, last seen, etc.

**Example:**
```python
stats = tracker.get_verb_stats("hablar")
print(f"Accuracy: {stats['accuracy']:.1%}")
print(f"Total attempts: {stats['total_attempts']}")
```

##### `get_overall_stats(self) -> Dict[str, Any]`
Get overall learning statistics.

**Returns:**
- `Dict[str, Any]`: Comprehensive statistics across all practice

##### `get_due_verbs(self, limit: int = 10) -> List[str]`
Get verbs due for spaced repetition review.

**Parameters:**
- `limit` (int): Maximum number of verbs to return

**Returns:**
- `List[str]`: List of verbs due for review

##### `update_spaced_repetition(self, verb: str, tense: str, person: str, correct: bool)`
Update spaced repetition schedule based on performance.

**Parameters:**
- `verb` (str): Practiced verb
- `tense` (str): Practiced tense
- `person` (str): Practiced person
- `correct` (bool): Whether answer was correct

##### `export_progress(self, format: str = "json") -> str`
Export progress data for backup or analysis.

**Parameters:**
- `format` (str): Export format ("json", "csv", "xml")

**Returns:**
- `str`: Serialized progress data

##### `import_progress(self, data: str, format: str = "json")`
Import progress data from backup.

**Parameters:**
- `data` (str): Serialized progress data
- `format` (str): Data format ("json", "csv", "xml")

### 4. TaskScenario Class

Manages task-based learning scenarios for practical application.

```python
class TaskScenario:
    """
    Creates real-world communication scenarios for verb practice.
    
    Provides contextual learning through practical situations
    like ordering food, asking directions, making appointments.
    """
```

#### Methods

##### `__init__(self, scenario_data: Dict[str, Any])`
Initialize with scenario configuration data.

##### `generate_task(self, scenario_type: str) -> Task`
Generate a task-based exercise.

**Parameters:**
- `scenario_type` (str): Type of scenario ("restaurant", "travel", "work", etc.)

**Returns:**
- `Task`: Task-based exercise object

#### Task Types

Available scenario types:
- `"restaurant"`: Ordering food, asking about menu
- `"travel"`: Asking directions, booking hotels
- `"work"`: Office interactions, meetings
- `"shopping"`: Buying items, asking prices
- `"social"`: Meeting people, making plans
- `"medical"`: Doctor visits, describing symptoms
- `"education"`: Classroom interactions, asking questions

### 5. SpeedPractice Class

Implements timed practice sessions for fluency development.

```python
class SpeedPractice:
    """
    Speed-based practice mode for building automatic recall.
    
    Tracks response times, adjusts difficulty, and provides
    fluency-building exercises with real-time feedback.
    """
```

#### Methods

##### `start_session(self, time_limit: int, question_count: int) -> SpeedSession`
Start a new speed practice session.

**Parameters:**
- `time_limit` (int): Seconds allowed per question
- `question_count` (int): Number of questions in session

**Returns:**
- `SpeedSession`: Active speed session object

##### `submit_answer(self, session_id: str, answer: str) -> SpeedResult`
Submit an answer during speed practice.

**Parameters:**
- `session_id` (str): Active session identifier
- `answer` (str): User's answer

**Returns:**
- `SpeedResult`: Result with correctness, time taken, score

### 6. LearningPath Class

Manages adaptive learning progression and personalized curricula.

```python
class LearningPath:
    """
    Adaptive learning path management system.
    
    Analyzes user performance to suggest optimal learning
    sequences and adjust difficulty dynamically.
    """
```

#### Methods

##### `analyze_performance(self, user_stats: Dict[str, Any]) -> AnalysisResult`
Analyze user performance to identify strengths and weaknesses.

##### `suggest_next_topics(self, current_level: str) -> List[str]`
Suggest next topics to study based on learning progression.

##### `adjust_difficulty(self, current_difficulty: str, accuracy: float) -> str`
Automatically adjust difficulty based on recent performance.

## 🛠️ Utility Functions and Constants

### Constants

#### `TENSE_NAMES`
```python
TENSE_NAMES = {
    'present': 'Present',
    'preterite': 'Preterite', 
    'imperfect': 'Imperfect',
    'future': 'Future',
    'conditional': 'Conditional',
    'present_perfect': 'Present Perfect',
    'past_perfect': 'Past Perfect',
    'future_perfect': 'Future Perfect',
    'conditional_perfect': 'Conditional Perfect',
    'present_subjunctive': 'Present Subjunctive',
    'imperfect_subjunctive': 'Imperfect Subjunctive',
    'present_perfect_subjunctive': 'Present Perfect Subjunctive',
    'past_perfect_subjunctive': 'Past Perfect Subjunctive'
}
```

#### `PERSON_LABELS`
```python
PERSON_LABELS = {
    'yo': 'I',
    'tú': 'you (informal)',
    'él': 'he',
    'ella': 'she', 
    'usted': 'you (formal)',
    'nosotros': 'we (masculine)',
    'nosotras': 'we (feminine)',
    'vosotros': 'you all (informal, Spain)',
    'vosotras': 'you all (feminine, informal, Spain)',
    'ellos': 'they (masculine)',
    'ellas': 'they (feminine)',
    'ustedes': 'you all (formal)'
}
```

#### `DIFFICULTY_LEVELS`
```python
DIFFICULTY_LEVELS = {
    'beginner': {
        'tenses': ['present'],
        'persons': ['yo', 'tú', 'él'],
        'verbs': 'common_regular',
        'context': 'simple'
    },
    'intermediate': {
        'tenses': ['present', 'preterite', 'imperfect'],
        'persons': ['yo', 'tú', 'él', 'nosotros', 'ellos'],
        'verbs': 'mixed',
        'context': 'moderate'
    },
    'advanced': {
        'tenses': 'all',
        'persons': 'all', 
        'verbs': 'all',
        'context': 'complex'
    }
}
```

### Utility Functions

#### `validate_api_key(api_key: str) -> bool`
Validate OpenAI API key format.

#### `load_verb_database(file_path: str) -> Dict[str, Any]`
Load verb data from JSON file.

#### `sanitize_input(text: str) -> str`
Sanitize user input for security.

#### `format_conjugation_table(verb: str, conjugator: SpanishConjugator) -> str`
Generate formatted conjugation table for display.

## 🔌 API Integration

### OpenAI Integration

#### `OpenAIClient` Class
```python
class OpenAIClient:
    """
    Wrapper for OpenAI API integration.
    
    Handles authentication, rate limiting, error handling,
    and specialized prompts for Spanish learning content.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
    
    def generate_exercise_explanation(self, verb: str, tense: str, person: str) -> str:
        """Generate AI-powered explanation for conjugation."""
        
    def create_contextual_sentence(self, verb: str, tense: str, difficulty: str) -> str:
        """Create contextual sentence for practice."""
        
    def generate_story_continuation(self, current_story: str, next_verb: str) -> str:
        """Generate story continuation with specified verb."""
```

### Rate Limiting and Error Handling

#### `APIRateLimiter` Class
```python
class APIRateLimiter:
    """
    Handles API rate limiting and request queuing.
    
    Implements exponential backoff, request queuing,
    and automatic fallback to offline mode.
    """
    
    def __init__(self, requests_per_minute: int = 60):
        self.rpm_limit = requests_per_minute
        self.request_times = deque()
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        
    def can_make_request(self) -> bool:
        """Check if request can be made without waiting."""
```

## 🎨 GUI Components

### Main Application Window

#### `ConjugationApp` Class (PyQt5)
```python
class ConjugationApp(QMainWindow):
    """
    Main application window built with PyQt5.
    
    Manages the complete user interface including exercise display,
    controls, progress visualization, and settings management.
    """
```

#### Key UI Components

##### Exercise Display
- `QTextEdit exercise_display`: Shows current exercise
- `QLineEdit answer_input`: User input field
- `QPushButton submit_button`: Answer submission
- `QLabel feedback_label`: Immediate feedback

##### Control Panel
- `QPushButton new_exercise_btn`: Generate new exercise
- `QPushButton speed_mode_btn`: Enter speed mode
- `QPushButton story_mode_btn`: Enter story mode
- `QPushButton settings_btn`: Open settings

##### Progress Display
- `QProgressBar overall_progress`: Overall learning progress
- `QLabel accuracy_label`: Current accuracy percentage
- `QLabel streak_label`: Current correct streak
- `QTableWidget stats_table`: Detailed statistics

##### Settings Dialog
- `QComboBox difficulty_combo`: Difficulty selection
- `QListWidget tense_list`: Tense selection
- `QListWidget person_list`: Person selection
- `QLineEdit api_key_input`: API key configuration

## 🗄️ Database Schema

### SQLite Tables

#### `attempts` Table
```sql
CREATE TABLE attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    verb TEXT NOT NULL,
    tense TEXT NOT NULL, 
    person TEXT NOT NULL,
    user_answer TEXT,
    correct_answer TEXT,
    is_correct BOOLEAN,
    response_time REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    difficulty TEXT,
    exercise_type TEXT
);
```

#### `verb_stats` Table
```sql
CREATE TABLE verb_stats (
    verb TEXT PRIMARY KEY,
    total_attempts INTEGER DEFAULT 0,
    correct_attempts INTEGER DEFAULT 0,
    average_response_time REAL DEFAULT 0,
    last_seen DATETIME,
    next_review DATETIME,
    difficulty_level REAL DEFAULT 1.0,
    mastery_score REAL DEFAULT 0.0
);
```

#### `learning_sessions` Table
```sql
CREATE TABLE learning_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time DATETIME,
    end_time DATETIME,
    exercises_completed INTEGER,
    accuracy REAL,
    session_type TEXT,
    notes TEXT
);
```

#### `spaced_repetition` Table
```sql
CREATE TABLE spaced_repetition (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    verb TEXT,
    tense TEXT,
    person TEXT,
    ease_factor REAL DEFAULT 2.5,
    interval_days INTEGER DEFAULT 1,
    repetitions INTEGER DEFAULT 0,
    next_review DATE,
    last_quality INTEGER
);
```

## 🔧 Configuration Management

### Configuration Files

#### `app_config.json`
```json
{
  "version": "1.0.0",
  "database": {
    "path": "./progress.db",
    "backup_enabled": true,
    "backup_interval": 3600
  },
  "ui": {
    "theme": "light",
    "font_family": "Arial",
    "font_size": 12,
    "window_geometry": [1000, 700]
  },
  "learning": {
    "default_difficulty": "intermediate",
    "spaced_repetition_enabled": true,
    "show_hints": true,
    "auto_advance": false
  },
  "api": {
    "timeout": 30,
    "max_retries": 3,
    "rate_limit": 60
  }
}
```

#### Environment Variables
```bash
# API Configuration
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o
OPENAI_MAX_TOKENS=600
OPENAI_TEMPERATURE=0.5

# Application Settings
DEBUG=false
LOG_LEVEL=INFO
DATABASE_PATH=./progress.db

# Feature Flags
ENABLE_AI_FEATURES=true
ENABLE_TELEMETRY=false
ENABLE_SPEED_MODE=true
ENABLE_STORY_MODE=true
```

## 🧪 Testing Utilities

### Test Fixtures

#### `conjugator_fixture`
```python
@pytest.fixture
def conjugator():
    """Provide SpanishConjugator instance for testing."""
    return SpanishConjugator()
```

#### `sample_exercise_fixture`
```python
@pytest.fixture
def sample_exercise():
    """Provide sample exercise for testing."""
    return Exercise(
        id="test_1",
        type="fill_blank",
        question="Yo _____ español.",
        correct_answer="hablo",
        distractors=["hablas", "habla", "hablamos"],
        hint="Present tense, first person singular",
        explanation="'Hablar' conjugated for 'yo' in present tense",
        difficulty="beginner",
        tense="present",
        person="yo",
        verb="hablar",
        context="daily conversation"
    )
```

### Mock Objects

#### `MockOpenAIClient`
```python
class MockOpenAIClient:
    """Mock OpenAI client for testing without API calls."""
    
    def generate_exercise_explanation(self, verb: str, tense: str, person: str) -> str:
        return f"Mock explanation for {verb} in {tense} tense, {person} person"
    
    def create_contextual_sentence(self, verb: str, tense: str, difficulty: str) -> str:
        return f"Mock sentence with {verb} for {difficulty} level"
```

## 📊 Performance Monitoring

### Metrics Collection

#### `PerformanceTracker` Class
```python
class PerformanceTracker:
    """
    Tracks application performance metrics.
    
    Monitors response times, memory usage, database performance,
    and user interaction patterns for optimization.
    """
    
    def track_exercise_generation_time(self, duration: float):
        """Track time taken to generate exercises."""
        
    def track_database_query_time(self, query_type: str, duration: float):
        """Track database operation performance."""
        
    def track_api_request_time(self, endpoint: str, duration: float):
        """Track API request performance."""
```

### Analytics Events

#### User Actions
- `exercise_started`: User begins new exercise
- `exercise_completed`: User completes exercise
- `answer_submitted`: User submits answer
- `hint_requested`: User requests hint
- `difficulty_changed`: User changes difficulty setting

#### System Events
- `api_request_made`: API request initiated
- `database_query_executed`: Database operation performed
- `error_occurred`: Application error encountered
- `session_started`: User session begins
- `session_ended`: User session ends

## 🔐 Security Implementation

### Input Validation

#### `SecurityValidator` Class
```python
class SecurityValidator:
    """
    Comprehensive input validation and sanitization.
    
    Prevents injection attacks, validates data formats,
    and ensures secure handling of user inputs.
    """
    
    @staticmethod
    def validate_verb_input(verb: str) -> bool:
        """Validate Spanish verb format and prevent injection."""
        
    @staticmethod
    def sanitize_exercise_content(content: str) -> str:
        """Sanitize exercise content for safe display."""
        
    @staticmethod
    def validate_api_key_format(api_key: str) -> bool:
        """Validate API key format without exposing content."""
```

### Secure Storage

#### API Key Encryption
```python
from cryptography.fernet import Fernet
import base64

def encrypt_api_key(api_key: str, encryption_key: bytes) -> str:
    """Encrypt API key for secure local storage."""
    cipher = Fernet(encryption_key)
    encrypted = cipher.encrypt(api_key.encode())
    return base64.b64encode(encrypted).decode()

def decrypt_api_key(encrypted_key: str, encryption_key: bytes) -> str:
    """Decrypt API key for use."""
    cipher = Fernet(encryption_key)
    encrypted_bytes = base64.b64decode(encrypted_key.encode())
    decrypted = cipher.decrypt(encrypted_bytes)
    return decrypted.decode()
```

---

## 📝 Usage Examples

### Complete Exercise Generation Flow

```python
from conjugation_engine import SpanishConjugator
from exercise_generator import ExerciseGenerator
from progress_tracker import ProgressTracker

# Initialize components
conjugator = SpanishConjugator()
tracker = ProgressTracker()
generator = ExerciseGenerator(conjugator)

# Generate exercise based on user's weak areas
weak_verbs = tracker.get_due_verbs(limit=5)
exercise = generator.generate_exercise(
    verbs=weak_verbs,
    tenses=["present", "preterite"],
    difficulty="intermediate"
)

# Present exercise to user
print(f"Question: {exercise.question}")
user_answer = input("Your answer: ")

# Check answer and record result
is_correct = user_answer.strip().lower() == exercise.correct_answer.lower()
tracker.record_attempt(
    verb=exercise.verb,
    tense=exercise.tense, 
    person=exercise.person,
    correct=is_correct,
    response_time=2.5  # Would be measured in real app
)

# Update spaced repetition schedule
tracker.update_spaced_repetition(
    exercise.verb, exercise.tense, exercise.person, is_correct
)

# Show feedback
if is_correct:
    print("¡Correcto! " + exercise.explanation)
else:
    print(f"Incorrect. The correct answer is: {exercise.correct_answer}")
    print(f"Explanation: {exercise.explanation}")
```

### Speed Practice Session

```python
from speed_practice import SpeedPractice

# Start speed session
speed_practice = SpeedPractice(conjugator)
session = speed_practice.start_session(
    time_limit=5,  # 5 seconds per question
    question_count=10
)

# Simulate practice session
for i in range(session.question_count):
    exercise = session.get_next_exercise()
    print(f"Question {i+1}: {exercise.question}")
    
    # In real app, this would be timed user input
    import time
    start_time = time.time()
    user_answer = "hablo"  # Simulated answer
    response_time = time.time() - start_time
    
    result = speed_practice.submit_answer(session.id, user_answer)
    print(f"Result: {'Correct' if result.correct else 'Incorrect'}")
    print(f"Time: {result.response_time:.2f}s")
    print(f"Score: {result.score}")

# Get final session results
final_results = session.get_final_results()
print(f"Session complete! Final score: {final_results.total_score}")
print(f"Accuracy: {final_results.accuracy:.1%}")
print(f"Average time: {final_results.avg_response_time:.2f}s")
```

---

This API reference provides a comprehensive guide to the Spanish Conjugation Practice application's codebase. For specific implementation details, refer to the source code files and inline documentation.

**Need help?** 
- Check the [User Guide](USER_GUIDE.md) for application usage
- See the [Developer Guide](DEVELOPER_GUIDE.md) for setup and development workflow
- Open an issue on GitHub for specific questions about the API