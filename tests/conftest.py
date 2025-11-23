"""
Pytest configuration and shared fixtures for the testing suite.
"""

import pytest
import os
import sys
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

@pytest.fixture(scope="session")
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = tempfile.mkdtemp(prefix="conjugation_test_")
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)

@pytest.fixture
def mock_env_file(temp_dir):
    """Create a mock .env file for testing."""
    env_path = os.path.join(temp_dir, ".env")
    with open(env_path, "w") as f:
        f.write("OPENAI_API_KEY=sk-test-1234567890abcdef\n")
    return env_path

@pytest.fixture
def mock_env_example(temp_dir):
    """Create a mock .env.example file."""
    env_example_path = os.path.join(temp_dir, ".env.example")
    with open(env_example_path, "w") as f:
        f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
    return env_example_path

@pytest.fixture
def mock_config_file(temp_dir):
    """Create a mock app configuration file."""
    config_path = os.path.join(temp_dir, "app_config.json")
    default_config = {
        "dark_mode": False,
        "show_translation": False,
        "api_model": "gpt-4o",
        "max_tokens": 600,
        "temperature": 0.5,
        "max_stored_responses": 100,
        "exercise_count": 5,
        "answer_strictness": "normal",
        "window_geometry": {
            "width": 1100,
            "height": 700,
            "x": 100,
            "y": 100
        },
        "splitter_sizes": [450, 650]
    }
    with open(config_path, "w") as f:
        json.dump(default_config, f, indent=2)
    return config_path

@pytest.fixture
def mock_distribution_dir(temp_dir):
    """Create a mock distribution directory structure."""
    dist_dir = os.path.join(temp_dir, "SpanishConjugation_Distribution")
    os.makedirs(dist_dir, exist_ok=True)
    
    # Create mock executable
    exe_path = os.path.join(dist_dir, "SpanishConjugation.exe")
    with open(exe_path, "wb") as f:
        f.write(b"MOCK_EXECUTABLE_DATA")
    
    # Create README
    readme_path = os.path.join(dist_dir, "README.txt")
    with open(readme_path, "w") as f:
        f.write("Spanish Conjugation Practice - Quick Start\n")
    
    # Create batch file
    batch_path = os.path.join(dist_dir, "Run.bat")
    with open(batch_path, "w") as f:
        f.write("@echo off\nSpanishConjugation.exe\n")
    
    # Create .env.example
    env_example = os.path.join(dist_dir, ".env.example")
    with open(env_example, "w") as f:
        f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
    
    return dist_dir

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    with patch('openai.OpenAI') as mock_client:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Mocked GPT response"
        
        mock_client_instance = MagicMock()
        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_client.return_value = mock_client_instance
        
        yield mock_client_instance

@pytest.fixture
def clean_environment():
    """Ensure clean test environment by backing up and restoring env vars."""
    original_env = os.environ.copy()
    # Clear OpenAI related env vars for testing
    for key in list(os.environ.keys()):
        if key.startswith('OPENAI_'):
            del os.environ[key]
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)

@pytest.fixture
def mock_pyqt_app():
    """Mock PyQt5 application for headless testing."""
    with patch('PyQt5.QtWidgets.QApplication') as mock_app:
        mock_app_instance = MagicMock()
        mock_app.return_value = mock_app_instance
        yield mock_app_instance