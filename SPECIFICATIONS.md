# Spanish Conjugation Practice Application - Technical Specifications

## Executive Summary

A comprehensive desktop application for Spanish verb conjugation practice that combines offline capabilities with AI-powered learning features. The application uses PyQt5 for the GUI, SQLite for progress tracking, and optionally integrates with OpenAI's GPT-4o model for enhanced contextual learning.

## System Architecture

### Technology Stack
- **Language**: Python 3.8+
- **GUI Framework**: PyQt5 5.15.7
- **Database**: SQLite3 (embedded)
- **AI Integration**: OpenAI API (GPT-4o model)
- **Build System**: PyInstaller for executable generation
- **Package Management**: Poetry/pip

### Core Components

#### 1. Main Application (`main.py`)
- **Class**: `SpanishConjugationGUI(QMainWindow)`
- **Responsibilities**:
  - Initialize and manage UI components
  - Handle user interactions and navigation
  - Coordinate between different modules
  - Manage application state and configuration
- **Key Features**:
  - Asynchronous API calls using QThreadPool
  - Dynamic UI mode switching (Free Response/Multiple Choice)
  - Theme management (Dark/Light modes)
  - Session management and cleanup

#### 2. Conjugation Engine (`conjugation_engine.py`)
- **Class**: `SpanishConjugator`
- **Capabilities**:
  - Regular verb conjugation (-ar, -er, -ir endings)
  - Irregular verb handling (ser, estar, tener, hacer, ir, etc.)
  - Stem-changing verbs (e→ie, o→ue, e→i)
  - Supports 6 tenses: Present, Preterite, Imperfect, Future, Conditional, Present Subjunctive
  - 6 grammatical persons for each tense

#### 3. Progress Tracking (`progress_tracker.py`)
- **Class**: `ProgressTracker`
- **Database Schema**:
  ```sql
  - attempts: Records every practice attempt
  - verb_performance: Tracks performance by verb/tense/person
  - sessions: Stores session summaries
  ```
- **Features**:
  - Spaced repetition algorithm
  - Difficulty scoring (0.1 to 1.0 scale)
  - Weak area identification
  - Performance statistics

#### 4. Exercise Generation (`exercise_generator.py`)
- **Class**: `ExerciseGenerator`
- **Capabilities**:
  - Contextual sentence generation
  - Difficulty-based content selection
  - Multiple choice option generation
  - Tense-specific templates
  - Story mode for connected discourse

#### 5. Task-Based Learning (`task_scenarios.py`)
- **Class**: `TaskScenario`
- **Features**:
  - Real-world scenario generation
  - Communicative success evaluation
  - Context-appropriate vocabulary
  - Progressive difficulty scenarios

#### 6. Speed Practice (`speed_practice.py`)
- **Class**: `SpeedPractice`
- **Purpose**: Build conversational fluency through timed exercises
- **Features**:
  - Response time tracking
  - Weak spot identification
  - Progressive speed targets

#### 7. Learning Path (`learning_path.py`)
- **Class**: `LearningPath`
- **Purpose**: Structured progression through conjugation mastery
- **Features**:
  - Adaptive difficulty adjustment
  - Prerequisite management
  - Achievement tracking

## Data Models

### Exercise Structure
```python
{
    'sentence': str,          # Sentence with blank
    'answer': str,           # Correct conjugation
    'choices': List[str],    # Multiple choice options
    'verb': str,             # Infinitive form
    'tense': str,            # Tense identifier
    'person': int,           # Person index (0-5)
    'translation': str,      # English translation
    'context': str,          # Additional context
    'difficulty': str        # beginner/intermediate/advanced
}
```

### Configuration Schema
```json
{
    "dark_mode": bool,
    "show_translation": bool,
    "api_model": "gpt-4o",
    "max_tokens": 600,
    "temperature": 0.5,
    "exercise_count": 5,
    "answer_strictness": "normal",
    "window_geometry": {...}
}
```

## User Interface

### Main Window Layout
- **Splitter Layout**: Resizable left/right panes
- **Left Pane**: 
  - Sentence display with context
  - Optional translation
  - Statistics label
- **Right Pane**:
  - Practice options (tenses, persons, verbs, themes)
  - Mode selection (Free Response/Multiple Choice)
  - Answer input area
  - Navigation buttons
  - Feedback display
  - Progress bar

### Toolbar Actions
- Reset Progress
- New Exercise
- Session Summary
- Toggle Theme
- Toggle Translation
- Toggle Offline Mode
- Review Mistakes
- View Statistics
- Task Mode
- Story Mode
- Speed Mode
- Verb Reference
- Custom Practice
- Export Progress

## API Integration

### OpenAI Configuration
- **Model**: GPT-4o (configurable)
- **Max Tokens**: 600 (default)
- **Temperature**: 0.5 (default)
- **System Prompt**: Expert Spanish tutor specializing in LATAM Spanish

### API Usage Patterns
1. **Exercise Generation**: Creates contextual exercises with cultural relevance
2. **Answer Explanation**: Provides grammatical explanations for answers
3. **Hint Generation**: Offers subtle guidance without revealing answers
4. **Session Summary**: Analyzes overall performance patterns

## Offline Capabilities

### Local Exercise Generation
- Template-based sentence construction
- Context-appropriate vocabulary selection
- Difficulty-based verb selection
- Support for all major tenses and persons

### Offline Database
- Complete progress tracking without internet
- Local spaced repetition calculations
- Session history maintenance
- Statistics generation

## Practice Modes

### 1. Standard Practice
- Customizable tense/person selection
- Theme-based exercises
- Difficulty levels

### 2. Review Mode
- Focus on weak areas
- Spaced repetition scheduling
- Mistake correction

### 3. Task Mode
- Real-world scenarios
- Communicative goals
- Practical application

### 4. Story Mode
- Connected narrative exercises
- Discourse coherence
- Progressive complexity

### 5. Speed Mode
- Timed responses (1-10 seconds)
- Fluency building
- Response time tracking

### 6. Custom Practice
- User-defined exercises
- Flexible format parsing
- Personal vocabulary focus

## Performance Features

### Progress Tracking
- Per-verb/tense/person accuracy
- Response time analysis
- Learning curve visualization
- Weakness identification

### Spaced Repetition
- Interval calculation (1, 2, 4, 8, 16, 30 days)
- Difficulty-based scheduling
- Performance-adaptive intervals

### Statistics
- Overall accuracy percentage
- Unique verbs practiced
- Tense distribution
- Best/worst performing areas

## Build & Distribution

### Executable Generation
- **Tool**: PyInstaller
- **Output**: Single-file executable
- **Platforms**: Windows (primary), macOS, Linux
- **Size**: ~50MB compressed

### Distribution Package
```
SpanishConjugation_Distribution/
├── SpanishConjugation.exe
├── Run.bat
├── README.txt
├── progress.db (generated)
├── session_log.txt (generated)
└── logging_doc.txt (generated)
```

## Security & Privacy

### API Key Management
- Environment variable storage (.env file)
- No hardcoded credentials
- Secure error handling for API failures

### Data Storage
- Local SQLite database
- No cloud sync by default
- User-controlled export functionality

## Error Handling

### API Errors
- Rate limit detection and messaging
- Authentication error handling
- Network failure fallback to offline mode
- Graceful degradation of features

### Application Errors
- Comprehensive logging system
- User-friendly error messages
- Automatic recovery mechanisms
- Session data preservation

## Future Enhancements

### Planned Features
- Voice input/output for pronunciation
- Mobile companion app sync
- Advanced analytics dashboard
- Community exercise sharing
- Additional language support
- Gamification elements

### Technical Improvements
- Cloud backup option
- Real-time collaboration
- Advanced NLP for answer validation
- Performance optimization for large datasets
- Plugin architecture for extensions

## System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, macOS 10.14+, Ubuntu 20.04+
- **RAM**: 2GB
- **Storage**: 100MB available space
- **Display**: 1280x720 resolution
- **Internet**: Required for online mode only

### Recommended Requirements
- **RAM**: 4GB
- **Storage**: 500MB available space
- **Display**: 1920x1080 resolution
- **Internet**: Broadband for optimal API response

## Maintenance & Support

### Logging
- Application logs: `logging_doc.txt`
- Session logs: `session_log.txt`
- Exercise history: `exercise_log.txt`

### Configuration Files
- User preferences: `app_config.json`
- Environment variables: `.env`
- Database: `progress.db`

### Update Mechanism
- Manual update via GitHub releases
- Configuration migration support
- Database schema versioning

---

*Version 1.0.0 - Last Updated: 2025*