"""
Test utilities and helper functions for comprehensive testing.

Provides:
- Mock data generators
- Test environment setup utilities
- Assertion helpers
- Performance measurement tools
- Test data validation functions
"""

import os
import sys
import json
import tempfile
import shutil
import time
import random
import string
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


class MockDataGenerator:
    """Generate realistic mock data for testing."""
    
    @staticmethod
    def generate_mock_exercises(count: int = 10) -> List[Dict[str, Any]]:
        """Generate mock Spanish conjugation exercises."""
        verbs = ['hablar', 'comer', 'vivir', 'ser', 'estar', 'tener', 'hacer', 'decir', 'ir', 'ver']
        tenses = ['present', 'preterite', 'imperfect', 'future', 'conditional']
        persons = ['yo', 'tú', 'él/ella', 'nosotros', 'vosotros', 'ellos/ellas']
        
        exercises = []
        for i in range(count):
            verb = random.choice(verbs)
            tense = random.choice(tenses)
            person = random.choice(persons)
            
            exercise = {
                'id': i + 1,
                'sentence': f'Ayer {person} _____ español en casa.',
                'answer': MockDataGenerator._get_mock_conjugation(verb, tense, person),
                'verb': verb,
                'tense': tense,
                'person': person,
                'choices': MockDataGenerator._generate_multiple_choice_options(verb, tense),
                'translation': f'Yesterday {person} _____ Spanish at home.',
                'context': 'Daily activities',
                'difficulty': random.choice(['beginner', 'intermediate', 'advanced']),
                'timestamp': time.time() - random.randint(0, 86400)  # Within last day
            }
            exercises.append(exercise)
        
        return exercises
    
    @staticmethod
    def _get_mock_conjugation(verb: str, tense: str, person: str) -> str:
        """Get mock conjugation for testing purposes."""
        # Simplified mock conjugations - not linguistically accurate
        conjugations = {
            ('hablar', 'present', 'yo'): 'hablo',
            ('hablar', 'preterite', 'yo'): 'hablé',
            ('comer', 'present', 'yo'): 'como',
            ('comer', 'preterite', 'yo'): 'comí',
            ('vivir', 'present', 'yo'): 'vivo',
            ('vivir', 'preterite', 'yo'): 'viví'
        }
        
        return conjugations.get((verb, tense, person), f'{verb}_mock')
    
    @staticmethod
    def _generate_multiple_choice_options(verb: str, tense: str) -> List[str]:
        """Generate multiple choice options."""
        correct = MockDataGenerator._get_mock_conjugation(verb, tense, 'yo')
        options = [correct]
        
        # Add distractors
        distractors = [f'{verb}é', f'{verb}o', f'{verb}a', f'{verb}amos']
        for distractor in distractors[:3]:
            if distractor != correct:
                options.append(distractor)
        
        return options[:4]
    
    @staticmethod
    def generate_mock_progress_data() -> Dict[str, Any]:
        """Generate mock user progress data."""
        return {
            'total_exercises': random.randint(50, 500),
            'correct_answers': random.randint(30, 400),
            'total_time_minutes': random.randint(30, 300),
            'verbs_practiced': random.sample(
                ['hablar', 'comer', 'vivir', 'ser', 'estar', 'tener', 'hacer'], 
                random.randint(3, 7)
            ),
            'favorite_tenses': random.sample(['present', 'preterite', 'imperfect'], 2),
            'difficulty_preference': random.choice(['beginner', 'intermediate', 'advanced']),
            'last_session': time.time() - random.randint(0, 604800),  # Within last week
            'streak_days': random.randint(0, 30),
            'achievements': random.sample(
                ['first_exercise', 'streak_7', 'perfect_score', 'verb_master'], 
                random.randint(1, 3)
            )
        }
    
    @staticmethod
    def generate_mock_config_data() -> Dict[str, Any]:
        """Generate mock configuration data."""
        return {
            'dark_mode': random.choice([True, False]),
            'show_translation': random.choice([True, False]),
            'api_model': random.choice(['gpt-4o', 'gpt-4', 'gpt-3.5-turbo']),
            'max_tokens': random.randint(200, 1000),
            'temperature': round(random.uniform(0.1, 1.0), 2),
            'exercise_count': random.randint(5, 20),
            'answer_strictness': random.choice(['strict', 'normal', 'lenient']),
            'window_geometry': {
                'width': random.randint(800, 1920),
                'height': random.randint(600, 1080),
                'x': random.randint(0, 100),
                'y': random.randint(0, 100)
            },
            'splitter_sizes': [random.randint(300, 600), random.randint(400, 800)],
            'last_modified': time.time()
        }
    
    @staticmethod
    def generate_mock_api_responses() -> Dict[str, str]:
        """Generate mock OpenAI API responses."""
        return {
            'exercise_generation': json.dumps([
                {
                    'sentence': 'Ayer yo _____ al mercado.',
                    'answer': 'fui',
                    'choices': ['fui', 'voy', 'iré', 'iba'],
                    'translation': 'Yesterday I went to the market.'
                }
            ]),
            'explanation': 'This uses the preterite tense because it describes a completed action in the past.',
            'hint': 'Think about which tense is used for completed past actions.',
            'error_response': 'I apologize, but I cannot generate exercises at this time.',
            'rate_limit_error': 'Rate limit exceeded. Please try again later.'
        }


class TestEnvironmentSetup:
    """Utilities for setting up test environments."""
    
    @staticmethod
    def create_test_directory(base_name: str = "test_conjugation") -> str:
        """Create a temporary test directory."""
        temp_dir = tempfile.mkdtemp(prefix=f"{base_name}_")
        return temp_dir
    
    @staticmethod
    def cleanup_test_directory(test_dir: str) -> bool:
        """Clean up test directory."""
        try:
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)
            return True
        except Exception:
            return False
    
    @staticmethod
    def create_mock_distribution(test_dir: str) -> str:
        """Create mock distribution structure."""
        dist_dir = os.path.join(test_dir, "SpanishConjugation_Distribution")
        os.makedirs(dist_dir, exist_ok=True)
        
        # Create mock files
        files = {
            "SpanishConjugation.exe": b"MOCK_EXECUTABLE_" + b"X" * 1024 * 1024,  # 1MB
            ".env.example": "OPENAI_API_KEY=your_openai_api_key_here\n",
            "README.txt": TestEnvironmentSetup._get_mock_readme(),
            "Run.bat": "@echo off\necho Starting Spanish Conjugation Practice...\nSpanishConjugation.exe\n"
        }
        
        for filename, content in files.items():
            filepath = os.path.join(dist_dir, filename)
            mode = 'wb' if isinstance(content, bytes) else 'w'
            with open(filepath, mode) as f:
                f.write(content)
        
        return dist_dir
    
    @staticmethod
    def _get_mock_readme() -> str:
        """Get mock README content."""
        return """Spanish Conjugation Practice - Quick Start

1. SETUP API KEY:
   - Rename '.env.example' to '.env'
   - Open .env and replace 'your_openai_api_key_here' with your actual OpenAI API key
   - Get your API key from: https://platform.openai.com/api-keys

2. RUN THE APPLICATION:
   - Double-click 'Run.bat' to start
   - Or double-click 'SpanishConjugation.exe' directly (if .env is configured)

3. FIRST TIME USE:
   - Click "New Exercise" to generate practice sentences
   - Select your preferred tenses and difficulty
   - Start practicing!

Troubleshooting:
- If the app doesn't start, ensure .env file exists with valid API key
- Windows may show a security warning on first run - click "Run anyway"
- The app works in offline mode without an API key
"""
    
    @staticmethod
    def setup_mock_environment_variables(api_key: Optional[str] = None) -> Dict[str, str]:
        """Set up mock environment variables."""
        original_env = os.environ.copy()
        
        # Clear existing OpenAI env vars
        for key in list(os.environ.keys()):
            if key.startswith('OPENAI_'):
                del os.environ[key]
        
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
        
        return original_env
    
    @staticmethod
    def restore_environment_variables(original_env: Dict[str, str]) -> None:
        """Restore original environment variables."""
        os.environ.clear()
        os.environ.update(original_env)
    
    @staticmethod
    def create_test_config_file(test_dir: str, config_data: Optional[Dict] = None) -> str:
        """Create test configuration file."""
        if config_data is None:
            config_data = MockDataGenerator.generate_mock_config_data()
        
        config_path = os.path.join(test_dir, "app_config.json")
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        return config_path


class AssertionHelpers:
    """Custom assertion helpers for testing."""
    
    @staticmethod
    def assert_file_exists(filepath: str, message: Optional[str] = None) -> None:
        """Assert that file exists."""
        if not os.path.exists(filepath):
            msg = message or f"File does not exist: {filepath}"
            raise AssertionError(msg)
    
    @staticmethod
    def assert_file_contains(filepath: str, content: str, message: Optional[str] = None) -> None:
        """Assert that file contains specific content."""
        AssertionHelpers.assert_file_exists(filepath)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        if content not in file_content:
            msg = message or f"File {filepath} does not contain: {content}"
            raise AssertionError(msg)
    
    @staticmethod
    def assert_json_structure(data: Any, expected_keys: List[str], message: Optional[str] = None) -> None:
        """Assert that JSON data has expected structure."""
        if not isinstance(data, dict):
            msg = message or f"Data is not a dictionary: {type(data)}"
            raise AssertionError(msg)
        
        missing_keys = [key for key in expected_keys if key not in data]
        if missing_keys:
            msg = message or f"Missing keys in JSON: {missing_keys}"
            raise AssertionError(msg)
    
    @staticmethod
    def assert_api_key_format(api_key: str, message: Optional[str] = None) -> None:
        """Assert that API key has correct format."""
        if not isinstance(api_key, str):
            msg = message or f"API key is not a string: {type(api_key)}"
            raise AssertionError(msg)
        
        if not api_key.startswith('sk-'):
            msg = message or f"API key does not start with 'sk-': {api_key[:10]}..."
            raise AssertionError(msg)
        
        if len(api_key) < 20:
            msg = message or f"API key too short: {len(api_key)} characters"
            raise AssertionError(msg)
    
    @staticmethod
    def assert_exercise_structure(exercise: Dict[str, Any], message: Optional[str] = None) -> None:
        """Assert that exercise has correct structure."""
        required_keys = ['sentence', 'answer', 'choices', 'translation']
        AssertionHelpers.assert_json_structure(exercise, required_keys, message)
        
        # Additional checks
        if not isinstance(exercise['choices'], list):
            msg = message or f"Exercise choices is not a list: {type(exercise['choices'])}"
            raise AssertionError(msg)
        
        if len(exercise['choices']) < 2:
            msg = message or f"Exercise needs at least 2 choices: {len(exercise['choices'])}"
            raise AssertionError(msg)
    
    @staticmethod
    def assert_config_values_valid(config: Dict[str, Any], message: Optional[str] = None) -> None:
        """Assert that configuration values are valid."""
        # Check boolean values
        boolean_keys = ['dark_mode', 'show_translation']
        for key in boolean_keys:
            if key in config and not isinstance(config[key], bool):
                msg = message or f"Config {key} is not boolean: {type(config[key])}"
                raise AssertionError(msg)
        
        # Check numeric ranges
        if 'max_tokens' in config:
            if not (50 <= config['max_tokens'] <= 4000):
                msg = message or f"Config max_tokens out of range: {config['max_tokens']}"
                raise AssertionError(msg)
        
        if 'temperature' in config:
            if not (0.0 <= config['temperature'] <= 2.0):
                msg = message or f"Config temperature out of range: {config['temperature']}"
                raise AssertionError(msg)


class PerformanceMeasurement:
    """Tools for measuring test performance."""
    
    def __init__(self):
        self.start_time = None
        self.measurements = {}
    
    def start_timer(self, operation_name: str = "default") -> None:
        """Start timing an operation."""
        self.start_time = time.time()
        self.current_operation = operation_name
    
    def end_timer(self, operation_name: Optional[str] = None) -> float:
        """End timing and return duration."""
        if self.start_time is None:
            raise ValueError("Timer not started")
        
        duration = time.time() - self.start_time
        op_name = operation_name or getattr(self, 'current_operation', 'default')
        
        self.measurements[op_name] = duration
        self.start_time = None
        
        return duration
    
    def get_measurement(self, operation_name: str) -> Optional[float]:
        """Get measurement for specific operation."""
        return self.measurements.get(operation_name)
    
    def get_all_measurements(self) -> Dict[str, float]:
        """Get all measurements."""
        return self.measurements.copy()
    
    @staticmethod
    def measure_function_performance(func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Measure performance of a function call."""
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)
        
        duration = time.time() - start_time
        
        return {
            'duration': duration,
            'success': success,
            'result': result,
            'error': error
        }
    
    @staticmethod
    def assert_performance_acceptable(duration: float, max_duration: float, operation: str = "operation") -> None:
        """Assert that performance is within acceptable limits."""
        if duration > max_duration:
            raise AssertionError(f"{operation} took too long: {duration:.2f}s > {max_duration:.2f}s")


class TestDataValidation:
    """Validation functions for test data."""
    
    @staticmethod
    def validate_exercise_data(exercises: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate exercise data structure and content."""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'stats': {
                'total_exercises': len(exercises),
                'unique_verbs': set(),
                'tense_distribution': {},
                'difficulty_distribution': {}
            }
        }
        
        for i, exercise in enumerate(exercises):
            # Check required fields
            required_fields = ['sentence', 'answer', 'choices', 'translation']
            missing_fields = [field for field in required_fields if field not in exercise]
            
            if missing_fields:
                validation_result['errors'].append(f"Exercise {i}: Missing fields {missing_fields}")
                validation_result['valid'] = False
            
            # Collect statistics
            if 'verb' in exercise:
                validation_result['stats']['unique_verbs'].add(exercise['verb'])
            
            if 'tense' in exercise:
                tense = exercise['tense']
                validation_result['stats']['tense_distribution'][tense] = \
                    validation_result['stats']['tense_distribution'].get(tense, 0) + 1
            
            if 'difficulty' in exercise:
                difficulty = exercise['difficulty']
                validation_result['stats']['difficulty_distribution'][difficulty] = \
                    validation_result['stats']['difficulty_distribution'].get(difficulty, 0) + 1
            
            # Check choices structure
            if 'choices' in exercise:
                choices = exercise['choices']
                if not isinstance(choices, list) or len(choices) < 2:
                    validation_result['errors'].append(f"Exercise {i}: Invalid choices structure")
                    validation_result['valid'] = False
                
                if 'answer' in exercise and exercise['answer'] not in choices:
                    validation_result['warnings'].append(f"Exercise {i}: Answer not in choices")
        
        # Convert set to list for JSON serialization
        validation_result['stats']['unique_verbs'] = list(validation_result['stats']['unique_verbs'])
        
        return validation_result
    
    @staticmethod
    def validate_config_data(config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration data."""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Type checks
        type_checks = {
            'dark_mode': bool,
            'show_translation': bool,
            'max_tokens': int,
            'temperature': (int, float),
            'exercise_count': int
        }
        
        for key, expected_type in type_checks.items():
            if key in config and not isinstance(config[key], expected_type):
                validation_result['errors'].append(f"Config {key} has wrong type: {type(config[key])}")
                validation_result['valid'] = False
        
        # Range checks
        range_checks = {
            'max_tokens': (1, 4000),
            'temperature': (0.0, 2.0),
            'exercise_count': (1, 100)
        }
        
        for key, (min_val, max_val) in range_checks.items():
            if key in config:
                value = config[key]
                if not (min_val <= value <= max_val):
                    validation_result['errors'].append(
                        f"Config {key} out of range: {value} not in [{min_val}, {max_val}]"
                    )
                    validation_result['valid'] = False
        
        return validation_result
    
    @staticmethod
    def validate_progress_data(progress: Dict[str, Any]) -> Dict[str, Any]:
        """Validate progress data."""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'calculated_accuracy': 0.0
        }
        
        # Check required fields
        required_fields = ['total_exercises', 'correct_answers']
        missing_fields = [field for field in required_fields if field not in progress]
        
        if missing_fields:
            validation_result['errors'].append(f"Missing progress fields: {missing_fields}")
            validation_result['valid'] = False
            return validation_result
        
        # Check logical consistency
        total = progress.get('total_exercises', 0)
        correct = progress.get('correct_answers', 0)
        
        if correct > total:
            validation_result['errors'].append(f"Correct answers ({correct}) > total exercises ({total})")
            validation_result['valid'] = False
        
        if total > 0:
            accuracy = (correct / total) * 100
            validation_result['calculated_accuracy'] = accuracy
            
            if accuracy > 100:
                validation_result['errors'].append(f"Calculated accuracy > 100%: {accuracy}")
                validation_result['valid'] = False
        
        return validation_result


# Convenience functions for common test operations
def create_test_environment(name: str = "test") -> str:
    """Create and return path to test environment."""
    return TestEnvironmentSetup.create_test_directory(name)

def generate_test_exercises(count: int = 5) -> List[Dict[str, Any]]:
    """Generate test exercises."""
    return MockDataGenerator.generate_mock_exercises(count)

def time_operation(func: Callable, *args, **kwargs) -> Dict[str, Any]:
    """Time a function operation."""
    return PerformanceMeasurement.measure_function_performance(func, *args, **kwargs)

def validate_test_data(data: Any, data_type: str = "exercise") -> Dict[str, Any]:
    """Validate test data based on type."""
    if data_type == "exercise" and isinstance(data, list):
        return TestDataValidation.validate_exercise_data(data)
    elif data_type == "config" and isinstance(data, dict):
        return TestDataValidation.validate_config_data(data)
    elif data_type == "progress" and isinstance(data, dict):
        return TestDataValidation.validate_progress_data(data)
    else:
        return {'valid': False, 'errors': [f'Unknown data type: {data_type}']}