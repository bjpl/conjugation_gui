# Spanish Conjugation Practice App - Developer Guide 👨‍💻

This guide provides comprehensive information for developers who want to build, modify, or contribute to the Spanish Conjugation Practice application.

## 🏗️ Architecture Overview

### Application Structure

```
conjugation_gui/
├── main.py                     # Main application entry point
├── conjugation_engine.py       # Core verb conjugation logic
├── exercise_generator.py       # Exercise creation and management
├── progress_tracker.py         # SQLite database and progress tracking
├── task_scenarios.py          # Task-based learning scenarios
├── speed_practice.py          # Speed mode implementation
├── learning_path.py           # Adaptive learning algorithms
├── build_exe.py               # PyInstaller build script
├── requirements.txt           # Python dependencies
├── pyproject.toml            # Poetry configuration
├── app_config.json           # Application configuration
├── .env.example              # Environment template
└── docs/                     # Documentation
    ├── USER_GUIDE.md         # End-user documentation
    ├── DEVELOPER_GUIDE.md    # This file
    └── API_REFERENCE.md      # Code API documentation
```

### Technology Stack

#### Core Framework
- **GUI Framework**: PyQt5 5.15.7
- **Python Version**: 3.8+ (tested up to 3.11)
- **Database**: SQLite3 (via Python standard library)
- **AI Integration**: OpenAI GPT-4 API (optional)

#### Key Dependencies
```python
PyQt5==5.15.7              # Main GUI framework
PyQtWebEngine==5.15.7       # Web engine for advanced features
python-dotenv>=1.0.0        # Environment variable management
openai>=1.0.0               # OpenAI API client
requests>=2.32.0            # HTTP requests
pillow==10.0.0              # Image processing
```

#### Build Tools
- **PyInstaller**: Executable creation
- **Poetry**: Dependency management (optional)
- **pip**: Standard package manager

### Component Architecture

#### 1. Main Application (main.py)
```python
class ConjugationApp(QMainWindow):
    """Main application window and controller."""
    
    # Key responsibilities:
    # - GUI initialization and layout
    # - Event handling and user interactions
    # - Coordination between components
    # - API key management and validation
```

#### 2. Conjugation Engine (conjugation_engine.py)
```python
class SpanishConjugator:
    """Core logic for Spanish verb conjugation."""
    
    # Features:
    # - Regular and irregular verb handling
    # - All major tenses and moods
    # - Validation and error checking
    # - Extensible verb database
```

#### 3. Exercise Generator (exercise_generator.py)
```python
class ExerciseGenerator:
    """Creates and manages practice exercises."""
    
    # Capabilities:
    # - Multiple exercise types
    # - Difficulty scaling
    # - Context-aware generation
    # - AI-powered content (optional)
```

#### 4. Progress Tracker (progress_tracker.py)
```python
class ProgressTracker:
    """SQLite-based progress and statistics management."""
    
    # Data tracked:
    # - Individual verb performance
    # - Tense-specific accuracy
    # - Learning velocity metrics
    # - Spaced repetition scheduling
```

## 🛠️ Development Environment Setup

### Prerequisites

#### System Requirements
- **Python**: 3.8 or higher (3.9-3.11 recommended)
- **pip**: Latest version
- **Git**: For version control
- **Virtual Environment**: Recommended for isolation

#### Platform-Specific Setup

**Windows:**
```cmd
# Install Python from python.org or Microsoft Store
# Ensure pip is included and updated
python -m pip install --upgrade pip

# Install Git from git-scm.com
# Recommended: Windows Terminal for better CLI experience
```

**macOS:**
```bash
# Install Python via Homebrew (recommended)
brew install python@3.11

# Or use pyenv for version management
brew install pyenv
pyenv install 3.11.5
pyenv local 3.11.5

# Install Xcode Command Line Tools
xcode-select --install
```

**Linux (Ubuntu/Debian):**
```bash
# Install Python and development tools
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
sudo apt install build-essential python3-dev

# Install Qt development libraries
sudo apt install qtbase5-dev qttools5-dev-tools
```

### Project Setup

#### 1. Clone and Setup Repository
```bash
# Clone the repository
git clone https://github.com/yourusername/conjugation_gui.git
cd conjugation_gui

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Verify Python version
python --version  # Should be 3.8+
```

#### 2. Install Dependencies
```bash
# Install core dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify PyQt5 installation
python -c "from PyQt5.QtWidgets import QApplication; print('PyQt5 installed successfully')"

# Optional: Install development tools
pip install pytest black flake8 mypy
```

#### 3. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit with your configuration
# Windows: notepad .env
# macOS/Linux: nano .env

# Example .env content:
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o
OPENAI_MAX_TOKENS=600
OPENAI_TEMPERATURE=0.5
DEBUG=True
LOG_LEVEL=INFO
```

#### 4. Initial Testing
```bash
# Run the application in development mode
python main.py

# Run basic tests (if available)
python -m pytest tests/ -v

# Check code style
black --check .
flake8 .
mypy main.py
```

### Development Workflow

#### 1. Code Style and Standards
```bash
# Format code with Black
black . --line-length 88

# Lint with flake8
flake8 . --max-line-length=88 --ignore=E203,W503

# Type checking with mypy
mypy --strict main.py conjugation_engine.py
```

#### 2. Testing Strategy
```python
# Example unit test structure
import pytest
from conjugation_engine import SpanishConjugator

class TestSpanishConjugator:
    def setup_method(self):
        self.conjugator = SpanishConjugator()
    
    def test_present_tense_regular(self):
        result = self.conjugator.conjugate("hablar", "present", "yo")
        assert result == "hablo"
    
    def test_irregular_verb_ser(self):
        result = self.conjugator.conjugate("ser", "present", "yo")
        assert result == "soy"
```

#### 3. Debugging and Logging
```python
import logging

# Configure logging for development
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

## 🔨 Building the Application

### Creating Executable Files

#### Using the Build Script
```bash
# Use the provided build script (recommended)
python build_exe.py

# This will:
# 1. Install PyInstaller if needed
# 2. Create executable with proper configuration
# 3. Bundle necessary files
# 4. Create distribution folder
```

#### Manual PyInstaller Command
```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --name SpanishConjugation \
           --windowed \
           --onefile \
           --add-data "app_config.json:." \
           --add-data ".env.example:." \
           --hidden-import PyQt5.QtCore \
           --hidden-import PyQt5.QtGui \
           --hidden-import PyQt5.QtWidgets \
           --hidden-import openai \
           --hidden-import dotenv \
           --clean \
           main.py
```

#### Build Configuration Options

**Single File vs Directory:**
```bash
# Single executable file (larger, slower startup)
--onefile

# Directory with dependencies (smaller main file, faster)
--onedir
```

**Console vs Windowed:**
```bash
# No console window (for GUI apps)
--windowed

# Show console window (for debugging)
--console
```

**Icon and Metadata:**
```bash
# Add application icon
--icon=app_icon.ico

# Add version information (Windows)
--version-file=version.txt
```

### Platform-Specific Building

#### Windows
```bash
# Install Windows-specific dependencies
pip install pywin32

# Build with Windows optimizations
pyinstaller --windowed --onefile \
           --distpath dist_windows \
           --workpath build_windows \
           main.py

# Create installer (optional)
# Use tools like NSIS, Inno Setup, or WiX
```

#### macOS
```bash
# Build macOS app bundle
pyinstaller --windowed --onefile \
           --distpath dist_macos \
           --osx-bundle-identifier com.yourcompany.spanishconjugation \
           main.py

# Sign the application (for distribution)
codesign --force --verify --verbose --sign "Developer ID Application" \
         "dist/SpanishConjugation.app"

# Create DMG installer
hdiutil create -srcfolder dist/SpanishConjugation.app \
              -volname "Spanish Conjugation" \
              SpanishConjugation.dmg
```

#### Linux
```bash
# Build Linux executable
pyinstaller --onefile \
           --distpath dist_linux \
           main.py

# Create AppImage (optional)
# Use linuxdeploy or AppImageKit

# Create .deb package (Ubuntu/Debian)
# Use fpm or create debian/ directory structure
```

### Build Optimization

#### Reducing File Size
```python
# In build_exe.py, add exclusions:
excludes = [
    'tkinter', 'matplotlib', 'numpy', 'scipy',
    'pandas', 'jupyter', 'IPython'
]

# Add to PyInstaller command:
--exclude-module tkinter \
--exclude-module matplotlib
```

#### Improving Startup Time
```python
# Use lazy imports in code
def get_openai_client():
    import openai  # Import only when needed
    return openai.OpenAI(api_key=get_api_key())

# Precompile Python modules
python -m compileall .
```

## 🧪 Testing Framework

### Unit Testing Setup
```python
# conftest.py - pytest configuration
import pytest
import sys
import os
from PyQt5.QtWidgets import QApplication

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for GUI tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    app.quit()
```

### Test Categories

#### 1. Conjugation Engine Tests
```python
# tests/test_conjugation_engine.py
import pytest
from conjugation_engine import SpanishConjugator, TENSE_NAMES

class TestSpanishConjugator:
    @pytest.fixture
    def conjugator(self):
        return SpanishConjugator()
    
    @pytest.mark.parametrize("verb,tense,person,expected", [
        ("hablar", "present", "yo", "hablo"),
        ("ser", "present", "tú", "eres"),
        ("tener", "preterite", "él", "tuvo"),
    ])
    def test_conjugations(self, conjugator, verb, tense, person, expected):
        result = conjugator.conjugate(verb, tense, person)
        assert result == expected
```

#### 2. GUI Component Tests
```python
# tests/test_gui.py
import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from main import ConjugationApp

class TestConjugationApp:
    @pytest.fixture
    def app(self, qapp):
        return ConjugationApp()
    
    def test_initial_state(self, app):
        assert app.windowTitle() == "Spanish Conjugation Practice"
        assert app.exercise_text.text() == ""
    
    def test_new_exercise_button(self, app):
        QTest.mouseClick(app.new_exercise_btn, Qt.LeftButton)
        # Verify exercise was generated
        assert app.exercise_text.text() != ""
```

#### 3. Database Tests
```python
# tests/test_progress_tracker.py
import pytest
import tempfile
import os
from progress_tracker import ProgressTracker

class TestProgressTracker:
    @pytest.fixture
    def temp_db(self):
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        os.unlink(path)
    
    @pytest.fixture
    def tracker(self, temp_db):
        return ProgressTracker(db_path=temp_db)
    
    def test_record_attempt(self, tracker):
        tracker.record_attempt("hablar", "present", "yo", True, 1.5)
        stats = tracker.get_verb_stats("hablar")
        assert stats['total_attempts'] == 1
        assert stats['correct_attempts'] == 1
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_conjugation_engine.py -v

# Run with GUI (for GUI tests)
pytest --no-cov -s tests/test_gui.py
```

## 🔧 Configuration Management

### Application Configuration (app_config.json)
```json
{
  "version": "1.0.0",
  "default_settings": {
    "difficulty": "intermediate",
    "tenses": ["present", "preterite", "imperfect"],
    "persons": ["yo", "tú", "él", "nosotros", "vosotros", "ellos"],
    "show_hints": true,
    "auto_advance": false,
    "speed_mode_timer": 5
  },
  "ui_settings": {
    "window_size": [1000, 700],
    "font_size": 12,
    "theme": "light"
  },
  "api_settings": {
    "model": "gpt-4o",
    "max_tokens": 600,
    "temperature": 0.5,
    "timeout": 30
  }
}
```

### Environment Variables
```bash
# Development vs Production
ENVIRONMENT=development|production

# API Configuration
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o
CLAUDE_API_KEY=your-claude-key  # Future support

# Database Configuration
DATABASE_PATH=./progress.db
BACKUP_ENABLED=true
BACKUP_INTERVAL=3600  # seconds

# Logging Configuration
LOG_LEVEL=INFO|DEBUG|WARNING|ERROR
LOG_TO_FILE=true
LOG_FILE_PATH=./logs/application.log

# Feature Flags
ENABLE_AI_FEATURES=true
ENABLE_TELEMETRY=false
ENABLE_EXPERIMENTAL=false
```

### Configuration Loading Pattern
```python
# config.py
import json
import os
from typing import Dict, Any
from dotenv import load_dotenv

class ConfigManager:
    def __init__(self, config_file: str = "app_config.json"):
        load_dotenv()
        self.config = self._load_config(config_file)
        self._apply_env_overrides()
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        with open(config_file, 'r') as f:
            return json.load(f)
    
    def _apply_env_overrides(self):
        # Override with environment variables
        if api_key := os.getenv('OPENAI_API_KEY'):
            self.config['api_settings']['api_key'] = api_key
        
        if model := os.getenv('OPENAI_MODEL'):
            self.config['api_settings']['model'] = model
    
    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k)
            if value is None:
                return default
        return value
```

## 🚀 Deployment and Distribution

### Release Process

#### 1. Version Management
```bash
# Update version in all relevant files
# - app_config.json
# - setup.py (if using)
# - main.py (__version__)

# Create git tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

#### 2. Multi-Platform Builds
```bash
# Use GitHub Actions or similar CI/CD
# .github/workflows/build.yml

name: Build and Release
on:
  push:
    tags: ['v*']

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt pyinstaller
      - name: Build executable
        run: python build_exe.py
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: windows-build
          path: SpanishConjugation_Distribution/
```

#### 3. Distribution Packages

**Windows Installer:**
```nsis
; installer.nsi - NSIS script
!define APPNAME "Spanish Conjugation Practice"
!define COMPANYNAME "YourCompany"
!define DESCRIPTION "Learn Spanish verb conjugations"

; Include modern UI
!include "MUI2.nsh"

; Installer configuration
OutFile "SpanishConjugation-Setup.exe"
InstallDir "$PROGRAMFILES\SpanishConjugation"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Installation section
Section "Install"
  SetOutPath $INSTDIR
  File /r "SpanishConjugation_Distribution\*"
  
  ; Create shortcuts
  CreateShortCut "$DESKTOP\Spanish Conjugation.lnk" \
                 "$INSTDIR\SpanishConjugation.exe"
  
  ; Register uninstaller
  WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd
```

**macOS DMG:**
```bash
#!/bin/bash
# create_dmg.sh

# Create temporary directory
tmp_dir=$(mktemp -d)
app_dir="$tmp_dir/Spanish Conjugation Practice"

# Copy application
mkdir -p "$app_dir"
cp -R "dist/SpanishConjugation.app" "$app_dir/"

# Create symbolic link to Applications
ln -s "/Applications" "$app_dir/Applications"

# Create DMG
hdiutil create -srcfolder "$tmp_dir" \
              -volname "Spanish Conjugation Practice" \
              -fs HFS+ \
              -fsargs "-c c=64,a=16,e=16" \
              -format UDBZ \
              -size 100m \
              "SpanishConjugation.dmg"

# Clean up
rm -rf "$tmp_dir"
```

#### 4. Auto-Update System (Future Enhancement)
```python
# update_manager.py
import requests
import json
from packaging import version

class UpdateManager:
    def __init__(self, current_version: str, update_url: str):
        self.current_version = current_version
        self.update_url = update_url
    
    def check_for_updates(self) -> Dict[str, Any]:
        try:
            response = requests.get(self.update_url, timeout=10)
            update_info = response.json()
            
            latest_version = update_info['version']
            if version.parse(latest_version) > version.parse(self.current_version):
                return {
                    'update_available': True,
                    'version': latest_version,
                    'download_url': update_info['download_url'],
                    'release_notes': update_info['release_notes']
                }
        except Exception as e:
            logger.warning(f"Update check failed: {e}")
        
        return {'update_available': False}
```

## 🤝 Contributing Guidelines

### Development Workflow

#### 1. Fork and Branch Strategy
```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/yourusername/conjugation_gui.git

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "Add: your feature description"

# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
```

#### 2. Code Review Process
- All changes require pull request review
- Automated tests must pass
- Code style checks must pass
- Documentation updates required for new features

#### 3. Issue Templates
```markdown
<!-- Bug Report Template -->
## Bug Description
Brief description of the bug

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What you expected to happen

## Actual Behavior
What actually happened

## Environment
- OS: [Windows 10, macOS 12, Ubuntu 20.04]
- Python Version: [3.9, 3.10, 3.11]
- Application Version: [1.0.0]

## Additional Context
Any additional information or screenshots
```

### Code Standards

#### 1. Python Style Guide
```python
# Follow PEP 8 with these exceptions:
# - Line length: 88 characters (Black default)
# - String quotes: Double quotes preferred

# Type hints required for public methods
def conjugate_verb(
    self, 
    verb: str, 
    tense: str, 
    person: str
) -> str:
    """
    Conjugate a Spanish verb.
    
    Args:
        verb: Infinitive form of the verb
        tense: Tense to conjugate to
        person: Person (yo, tú, él, etc.)
    
    Returns:
        Conjugated form of the verb
    
    Raises:
        ValueError: If verb or tense is invalid
    """
    pass
```

#### 2. Documentation Standards
```python
# Module docstring
"""
Spanish Conjugation Engine

This module provides the core functionality for conjugating Spanish verbs
across different tenses and persons. It handles both regular and irregular
verbs with comprehensive validation.

Example:
    >>> conjugator = SpanishConjugator()
    >>> result = conjugator.conjugate("hablar", "present", "yo")
    >>> print(result)
    "hablo"

Dependencies:
    - json: For verb data loading
    - re: For pattern matching
    - typing: For type hints
"""
```

#### 3. Testing Standards
```python
# Test naming convention
def test_should_conjugate_regular_verb_in_present_tense():
    """Test regular verb conjugation in present tense."""
    pass

def test_should_raise_error_for_invalid_verb():
    """Test error handling for invalid verb input."""
    pass

# Test categories
# - Unit tests: Individual component testing
# - Integration tests: Component interaction testing
# - GUI tests: User interface testing
# - Performance tests: Speed and memory usage
```

### Performance Guidelines

#### 1. Memory Management
```python
# Use generators for large datasets
def get_all_verbs():
    """Yield verbs one at a time instead of loading all."""
    for verb in verb_database:
        yield verb

# Close resources properly
class DatabaseManager:
    def __enter__(self):
        self.connection = sqlite3.connect(self.db_path)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
```

#### 2. Optimization Patterns
```python
# Cache expensive operations
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_conjugation_rules(tense: str) -> Dict[str, str]:
    """Cache conjugation rules to avoid repeated parsing."""
    return load_rules_from_file(tense)

# Use sets for O(1) lookup
IRREGULAR_VERBS = {
    "ser", "estar", "tener", "hacer", "poder", 
    "decir", "ir", "ver", "dar", "saber"
}

def is_irregular(verb: str) -> bool:
    return verb in IRREGULAR_VERBS  # O(1) instead of O(n)
```

## 📊 Monitoring and Analytics

### Performance Monitoring
```python
# performance_monitor.py
import time
import psutil
from typing import Dict, Any

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
    
    def track_function_performance(self, func_name: str):
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss
                
                result = func(*args, **kwargs)
                
                end_time = time.time()
                end_memory = psutil.Process().memory_info().rss
                
                self.metrics[func_name] = {
                    'execution_time': end_time - start_time,
                    'memory_delta': end_memory - start_memory,
                    'timestamp': time.time()
                }
                
                return result
            return wrapper
        return decorator
    
    def get_performance_report(self) -> Dict[str, Any]:
        return self.metrics.copy()
```

### Error Tracking
```python
# error_tracker.py
import logging
import traceback
import json
from datetime import datetime

class ErrorTracker:
    def __init__(self, log_file: str = "errors.log"):
        self.log_file = log_file
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(
            filename=self.log_file,
            level=logging.ERROR,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def track_error(self, error: Exception, context: Dict[str, Any] = None):
        error_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'context': context or {}
        }
        
        logging.error(json.dumps(error_data, indent=2))
        return error_data
```

## 🔒 Security Considerations

### API Key Security
```python
# secure_storage.py
import base64
import os
from cryptography.fernet import Fernet

class SecureStorage:
    def __init__(self, key_file: str = ".app_key"):
        self.key_file = key_file
        self.cipher = self._get_or_create_cipher()
    
    def _get_or_create_cipher(self) -> Fernet:
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
        
        return Fernet(key)
    
    def encrypt_api_key(self, api_key: str) -> str:
        encrypted = self.cipher.encrypt(api_key.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        encrypted_bytes = base64.b64decode(encrypted_key.encode())
        decrypted = self.cipher.decrypt(encrypted_bytes)
        return decrypted.decode()
```

### Input Validation
```python
# validators.py
import re
from typing import List

class InputValidator:
    VALID_TENSES = {
        'present', 'preterite', 'imperfect', 'future', 
        'conditional', 'present_subjunctive', 'imperfect_subjunctive'
    }
    
    VALID_PERSONS = {
        'yo', 'tú', 'él', 'ella', 'usted',
        'nosotros', 'nosotras', 'vosotros', 'vosotras',
        'ellos', 'ellas', 'ustedes'
    }
    
    @staticmethod
    def validate_verb(verb: str) -> bool:
        """Validate Spanish verb format."""
        if not isinstance(verb, str) or len(verb) < 2:
            return False
        
        # Must end in -ar, -er, or -ir
        return re.match(r'^[a-záéíóúñü]+[aei]r$', verb.lower()) is not None
    
    @staticmethod
    def validate_tense(tense: str) -> bool:
        """Validate tense name."""
        return tense in InputValidator.VALID_TENSES
    
    @staticmethod
    def sanitize_user_input(text: str) -> str:
        """Sanitize user input to prevent injection attacks."""
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\';]', '', text)
        return sanitized.strip()[:100]  # Limit length
```

## 🔄 Continuous Integration

### GitHub Actions Workflow
```yaml
# .github/workflows/ci.yml
name: Continuous Integration

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: [3.8, 3.9, '3.10', 3.11]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov black flake8
    
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88
    
    - name: Check code formatting
      run: black --check .
    
    - name: Test with pytest
      run: |
        pytest --cov=. --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      if: matrix.os == 'ubuntu-latest' && matrix.python-version == '3.11'

  build:
    needs: test
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pyinstaller
    
    - name: Build executable
      run: python build_exe.py
    
    - name: Upload build artifacts
      uses: actions/upload-artifact@v3
      with:
        name: build-${{ matrix.os }}
        path: SpanishConjugation_Distribution/
```

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 22.10.0
    hooks:
      - id: black
        args: [--line-length=88]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --ignore=E203,W503]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.991
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
```

## 📚 Additional Resources

### Learning Resources
- **PyQt5 Documentation**: https://doc.qt.io/qtforpython/
- **Python Packaging**: https://packaging.python.org/
- **OpenAI API Docs**: https://platform.openai.com/docs
- **SQLite Tutorial**: https://sqlite.org/lang.html

### Development Tools
- **IDEs**: PyCharm, VS Code, Sublime Text
- **GUI Designers**: Qt Designer, Qt Creator
- **Profiling**: cProfile, py-spy, memory_profiler
- **Documentation**: Sphinx, MkDocs

### Community
- **GitHub Discussions**: For questions and ideas
- **Stack Overflow**: Tag with `pyqt5` and `spanish-conjugation`
- **Python Discord**: General Python help
- **Qt Forum**: PyQt-specific questions

---

## 🤝 Getting Help

### Documentation Hierarchy
1. **This Developer Guide**: Architecture and development info
2. **User Guide**: End-user instructions and troubleshooting
3. **API Reference**: Code documentation and examples
4. **GitHub Wiki**: Additional tutorials and examples

### Contact and Support
- 📧 **Development Questions**: dev@yourcompany.com
- 🐛 **Bug Reports**: GitHub Issues
- 💡 **Feature Requests**: GitHub Discussions
- 🤝 **Contributions**: See CONTRIBUTING.md

---

**Happy coding! 🚀**

Remember: Good code is not just working code, it's maintainable, testable, and well-documented code that others (including future you) can understand and improve.