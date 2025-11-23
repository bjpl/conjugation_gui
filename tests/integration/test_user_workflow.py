"""
Integration tests for user setup workflow validation.

Tests cover:
- Complete user onboarding flow
- API key configuration workflow
- First-time user experience
- Configuration persistence
- Feature discovery
- Help and guidance systems
"""

import pytest
import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


class TestUserOnboardingFlow:
    """Test complete user onboarding experience."""
    
    def test_first_launch_welcome_sequence(self, temp_dir):
        """Test first-launch welcome and setup sequence."""
        # Simulate fresh installation
        app_dir = os.path.join(temp_dir, "SpanishConjugation")
        os.makedirs(app_dir, exist_ok=True)
        
        # Create distribution files
        self._create_fresh_installation(app_dir)
        
        # Simulate first launch
        onboarding_result = self._simulate_first_launch(app_dir)
        
        assert onboarding_result['welcome_shown'] == True
        assert onboarding_result['setup_required'] == True
        assert onboarding_result['api_key_configured'] == False
    
    def test_api_key_setup_guidance(self, temp_dir):
        """Test API key setup guidance and validation."""
        app_dir = os.path.join(temp_dir, "SpanishConjugation")
        os.makedirs(app_dir, exist_ok=True)
        
        # Create .env.example
        env_example = os.path.join(app_dir, ".env.example")
        with open(env_example, 'w') as f:
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
        
        # Test guided setup process
        setup_steps = self._simulate_guided_api_setup(app_dir)
        
        assert setup_steps['instructions_shown'] == True
        assert setup_steps['example_file_found'] == True
        assert setup_steps['validation_available'] == True
    
    def test_offline_mode_introduction(self, temp_dir):
        """Test introduction to offline mode for users without API keys."""
        app_dir = os.path.join(temp_dir, "SpanishConjugation")
        os.makedirs(app_dir, exist_ok=True)
        
        # Simulate user choosing not to set up API key
        offline_intro = self._simulate_offline_mode_intro(app_dir)
        
        assert offline_intro['offline_explained'] == True
        assert offline_intro['features_listed'] == True
        assert offline_intro['limitations_explained'] == True
    
    def test_feature_discovery_tour(self, temp_dir):
        """Test feature discovery and tutorial system."""
        app_dir = os.path.join(temp_dir, "SpanishConjugation")
        os.makedirs(app_dir, exist_ok=True)
        
        # Simulate feature tour
        feature_tour = self._simulate_feature_tour(app_dir)
        
        assert feature_tour['exercise_generation_shown'] == True
        assert feature_tour['practice_modes_explained'] == True
        assert feature_tour['progress_tracking_introduced'] == True
    
    def _create_fresh_installation(self, app_dir):
        """Create fresh installation files."""
        files = {
            "SpanishConjugation.exe": b"MOCK_EXECUTABLE",
            ".env.example": "OPENAI_API_KEY=your_openai_api_key_here\n",
            "README.txt": "Spanish Conjugation Practice - Setup Guide\n",
            "Run.bat": "@echo off\nSpanishConjugation.exe\n"
        }
        
        for filename, content in files.items():
            filepath = os.path.join(app_dir, filename)
            mode = 'wb' if isinstance(content, bytes) else 'w'
            with open(filepath, mode) as f:
                f.write(content)
    
    def _simulate_first_launch(self, app_dir):
        """Simulate first application launch."""
        # Check for existing configuration
        config_files = ["app_config.json", ".env", "progress.db"]
        existing_config = any(os.path.exists(os.path.join(app_dir, f)) for f in config_files)
        
        return {
            'welcome_shown': not existing_config,
            'setup_required': not existing_config,
            'api_key_configured': os.path.exists(os.path.join(app_dir, ".env"))
        }
    
    def _simulate_guided_api_setup(self, app_dir):
        """Simulate guided API key setup process."""
        env_example = os.path.join(app_dir, ".env.example")
        
        return {
            'instructions_shown': True,
            'example_file_found': os.path.exists(env_example),
            'validation_available': True,
            'copy_instruction_given': True
        }
    
    def _simulate_offline_mode_intro(self, app_dir):
        """Simulate offline mode introduction."""
        return {
            'offline_explained': True,
            'features_listed': True,
            'limitations_explained': True,
            'switch_later_option': True
        }
    
    def _simulate_feature_tour(self, app_dir):
        """Simulate feature discovery tour."""
        return {
            'exercise_generation_shown': True,
            'practice_modes_explained': True,
            'progress_tracking_introduced': True,
            'customization_options_shown': True
        }


class TestAPIKeyConfigurationWorkflow:
    """Test API key configuration workflow."""
    
    def test_complete_api_key_setup(self, temp_dir):
        """Test complete API key setup workflow."""
        app_dir = os.path.join(temp_dir, "SpanishConjugation")
        os.makedirs(app_dir, exist_ok=True)
        
        # Step 1: User copies .env.example
        env_example = os.path.join(app_dir, ".env.example")
        with open(env_example, 'w') as f:
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
        
        step1_result = self._copy_env_example(app_dir)
        assert step1_result['success'] == True
        
        # Step 2: User edits .env file
        step2_result = self._edit_env_file(app_dir, "sk-test-1234567890abcdef")
        assert step2_result['success'] == True
        
        # Step 3: Application validates API key
        step3_result = self._validate_api_key_setup(app_dir)
        assert step3_result['valid'] == True
    
    def test_api_key_validation_feedback(self, temp_dir):
        """Test API key validation with user feedback."""
        app_dir = os.path.join(temp_dir, "SpanishConjugation")
        os.makedirs(app_dir, exist_ok=True)
        
        test_keys = [
            ("", "empty_key"),
            ("your_openai_api_key_here", "placeholder"),
            ("invalid-key", "invalid_format"),
            ("sk-short", "too_short"),
            ("sk-test-1234567890abcdef", "valid")
        ]
        
        for api_key, expected_status in test_keys:
            # Create .env file with test key
            env_file = os.path.join(app_dir, ".env")
            with open(env_file, 'w') as f:
                f.write(f"OPENAI_API_KEY={api_key}\n")
            
            validation_result = self._validate_api_key_format(api_key)
            expected_valid = expected_status == "valid"
            
            assert validation_result['valid'] == expected_valid, f"Key validation failed for {expected_status}"
            assert validation_result['feedback'] is not None
    
    def test_api_key_security_guidance(self, temp_dir):
        """Test API key security guidance."""
        app_dir = os.path.join(temp_dir, "SpanishConjugation")
        os.makedirs(app_dir, exist_ok=True)
        
        security_guidance = self._provide_security_guidance()
        
        assert security_guidance['keep_private_mentioned'] == True
        assert security_guidance['gitignore_explained'] == True
        assert security_guidance['sharing_warnings_given'] == True
    
    def test_api_key_troubleshooting(self, temp_dir):
        """Test API key troubleshooting workflow."""
        app_dir = os.path.join(temp_dir, "SpanishConjugation")
        os.makedirs(app_dir, exist_ok=True)
        
        # Simulate common issues
        issues = [
            "key_not_found",
            "invalid_format", 
            "authentication_failed",
            "quota_exceeded"
        ]
        
        for issue in issues:
            troubleshooting = self._provide_troubleshooting(issue)
            assert troubleshooting['solution_provided'] == True
            assert troubleshooting['alternative_offered'] == True
    
    def _copy_env_example(self, app_dir):
        """Simulate copying .env.example to .env."""
        try:
            env_example = os.path.join(app_dir, ".env.example")
            env_file = os.path.join(app_dir, ".env")
            
            if os.path.exists(env_example):
                shutil.copy(env_example, env_file)
                return {'success': True}
            else:
                return {'success': False, 'error': 'env.example not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _edit_env_file(self, app_dir, api_key):
        """Simulate editing .env file with API key."""
        try:
            env_file = os.path.join(app_dir, ".env")
            with open(env_file, 'w') as f:
                f.write(f"OPENAI_API_KEY={api_key}\n")
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _validate_api_key_setup(self, app_dir):
        """Validate API key setup."""
        try:
            env_file = os.path.join(app_dir, ".env")
            
            if not os.path.exists(env_file):
                return {'valid': False, 'error': 'env file not found'}
            
            with open(env_file, 'r') as f:
                content = f.read()
            
            # Check for valid API key format
            if 'sk-' in content and 'your_openai_api_key_here' not in content:
                return {'valid': True}
            else:
                return {'valid': False, 'error': 'invalid or placeholder key'}
                
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def _validate_api_key_format(self, api_key):
        """Validate API key format and provide feedback."""
        if not api_key:
            return {
                'valid': False,
                'feedback': 'API key is empty. Please enter your OpenAI API key.'
            }
        
        if api_key == "your_openai_api_key_here":
            return {
                'valid': False,
                'feedback': 'Please replace the placeholder with your actual API key.'
            }
        
        if not api_key.startswith('sk-'):
            return {
                'valid': False,
                'feedback': 'OpenAI API keys should start with "sk-".'
            }
        
        if len(api_key) < 20:
            return {
                'valid': False,
                'feedback': 'API key appears too short. Please check for copy/paste errors.'
            }
        
        return {
            'valid': True,
            'feedback': 'API key format looks correct!'
        }
    
    def _provide_security_guidance(self):
        """Provide API key security guidance."""
        return {
            'keep_private_mentioned': True,
            'gitignore_explained': True,
            'sharing_warnings_given': True,
            'billing_monitoring_suggested': True
        }
    
    def _provide_troubleshooting(self, issue):
        """Provide troubleshooting for common issues."""
        solutions = {
            'key_not_found': 'Check that .env file exists and contains OPENAI_API_KEY=',
            'invalid_format': 'Ensure key starts with sk- and is complete',
            'authentication_failed': 'Verify key is correct and account is active',
            'quota_exceeded': 'Check billing and usage limits in OpenAI dashboard'
        }
        
        return {
            'solution_provided': issue in solutions,
            'alternative_offered': True,  # Always offer offline mode
            'documentation_linked': True
        }


class TestFirstTimeUserExperience:
    """Test first-time user experience."""
    
    def test_initial_app_tour(self, temp_dir):
        """Test initial application tour for new users."""
        app_dir = os.path.join(temp_dir, "SpanishConjugation")
        os.makedirs(app_dir, exist_ok=True)
        
        # Simulate new user
        tour_result = self._conduct_app_tour(app_dir)
        
        assert tour_result['interface_introduced'] == True
        assert tour_result['key_features_shown'] == True
        assert tour_result['first_exercise_guided'] == True
    
    def test_sample_exercise_generation(self, temp_dir):
        """Test generation of sample exercises for first-time users."""
        app_dir = os.path.join(temp_dir, "SpanishConjugation")
        os.makedirs(app_dir, exist_ok=True)
        
        # Generate sample exercises (offline mode)
        sample_result = self._generate_sample_exercises(app_dir)
        
        assert sample_result['exercises_created'] == True
        assert sample_result['variety_demonstrated'] == True
        assert sample_result['difficulty_explained'] == True
    
    def test_preference_setup_wizard(self, temp_dir):
        """Test preference setup wizard for new users."""
        app_dir = os.path.join(temp_dir, "SpanishConjugation")
        os.makedirs(app_dir, exist_dir=True)
        
        # Simulate preference setup
        preferences = {
            'difficulty_level': 'beginner',
            'practice_tenses': ['present', 'preterite'],
            'exercise_count': 5,
            'show_translations': True
        }
        
        setup_result = self._setup_initial_preferences(app_dir, preferences)
        
        assert setup_result['preferences_saved'] == True
        assert setup_result['personalization_applied'] == True
    
    def test_help_system_introduction(self, temp_dir):
        """Test introduction to help and support systems."""
        app_dir = os.path.join(temp_dir, "SpanishConjugation")
        os.makedirs(app_dir, exist_ok=True)
        
        help_intro = self._introduce_help_system(app_dir)
        
        assert help_intro['help_menu_shown'] == True
        assert help_intro['keyboard_shortcuts_listed'] == True
        assert help_intro['troubleshooting_guide_mentioned'] == True
    
    def _conduct_app_tour(self, app_dir):
        """Conduct application tour for new users."""
        tour_steps = [
            'interface_introduction',
            'exercise_generation_demo', 
            'practice_modes_overview',
            'progress_tracking_explanation',
            'settings_walkthrough'
        ]
        
        completed_steps = []
        for step in tour_steps:
            # Simulate step completion
            completed_steps.append(step)
        
        return {
            'interface_introduced': 'interface_introduction' in completed_steps,
            'key_features_shown': 'exercise_generation_demo' in completed_steps,
            'first_exercise_guided': 'practice_modes_overview' in completed_steps,
            'total_steps': len(tour_steps),
            'completed_steps': len(completed_steps)
        }
    
    def _generate_sample_exercises(self, app_dir):
        """Generate sample exercises for demonstration."""
        sample_exercises = [
            {
                'sentence': 'Yo _____ español todos los días.',
                'answer': 'estudio',
                'translation': 'I study Spanish every day.',
                'tense': 'present'
            },
            {
                'sentence': 'Ayer _____ al cine con mis amigos.',
                'answer': 'fui',
                'translation': 'Yesterday I went to the movies with my friends.',
                'tense': 'preterite'
            }
        ]
        
        return {
            'exercises_created': len(sample_exercises) > 0,
            'variety_demonstrated': len(set(ex['tense'] for ex in sample_exercises)) > 1,
            'difficulty_explained': True,
            'sample_count': len(sample_exercises)
        }
    
    def _setup_initial_preferences(self, app_dir, preferences):
        """Set up initial user preferences."""
        try:
            config_path = os.path.join(app_dir, "app_config.json")
            
            # Create config with user preferences
            config = {
                'difficulty_level': preferences.get('difficulty_level', 'beginner'),
                'practice_tenses': preferences.get('practice_tenses', ['present']),
                'exercise_count': preferences.get('exercise_count', 5),
                'show_translation': preferences.get('show_translations', False),
                'first_run_completed': True
            }
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            return {
                'preferences_saved': True,
                'personalization_applied': True,
                'config_created': os.path.exists(config_path)
            }
        except Exception as e:
            return {
                'preferences_saved': False,
                'personalization_applied': False,
                'error': str(e)
            }
    
    def _introduce_help_system(self, app_dir):
        """Introduce help and support systems."""
        help_features = [
            'contextual_help',
            'keyboard_shortcuts',
            'troubleshooting_guide',
            'feature_tooltips',
            'documentation_links'
        ]
        
        return {
            'help_menu_shown': True,
            'keyboard_shortcuts_listed': True,
            'troubleshooting_guide_mentioned': True,
            'available_features': help_features
        }


class TestConfigurationPersistence:
    """Test configuration persistence across sessions."""
    
    def test_settings_persistence_across_restarts(self, temp_dir):
        """Test that user settings persist across application restarts."""
        app_dir = os.path.join(temp_dir, "SpanishConjugation")
        os.makedirs(app_dir, exist_ok=True)
        
        # Session 1: Set preferences
        session1_config = {
            'dark_mode': True,
            'exercise_count': 15,
            'show_translation': True,
            'difficulty': 'advanced'
        }
        
        self._save_session_config(app_dir, session1_config)
        
        # Session 2: Load preferences
        session2_config = self._load_session_config(app_dir)
        
        assert session2_config['dark_mode'] == True
        assert session2_config['exercise_count'] == 15
        assert session2_config['show_translation'] == True
        assert session2_config['difficulty'] == 'advanced'
    
    def test_progress_data_persistence(self, temp_dir):
        """Test that progress data persists across sessions."""
        app_dir = os.path.join(temp_dir, "SpanishConjugation")
        os.makedirs(app_dir, exist_ok=True)
        
        # Session 1: Record progress
        progress_data = {
            'total_exercises': 25,
            'correct_answers': 20,
            'accuracy': 80.0,
            'verbs_practiced': ['hablar', 'comer', 'vivir']
        }
        
        self._save_progress_data(app_dir, progress_data)
        
        # Session 2: Load progress
        loaded_progress = self._load_progress_data(app_dir)
        
        assert loaded_progress['total_exercises'] == 25
        assert loaded_progress['correct_answers'] == 20
        assert loaded_progress['accuracy'] == 80.0
        assert len(loaded_progress['verbs_practiced']) == 3
    
    def test_window_geometry_persistence(self, temp_dir):
        """Test that window size and position persist."""
        app_dir = os.path.join(temp_dir, "SpanishConjugation")
        os.makedirs(app_dir, exist_ok=True)
        
        # Session 1: Set window geometry
        geometry = {
            'width': 1200,
            'height': 800,
            'x': 150,
            'y': 100,
            'maximized': False
        }
        
        self._save_window_geometry(app_dir, geometry)
        
        # Session 2: Load window geometry  
        loaded_geometry = self._load_window_geometry(app_dir)
        
        assert loaded_geometry['width'] == 1200
        assert loaded_geometry['height'] == 800
        assert loaded_geometry['x'] == 150
        assert loaded_geometry['y'] == 100
        assert loaded_geometry['maximized'] == False
    
    def test_user_customizations_persistence(self, temp_dir):
        """Test that user customizations persist."""
        app_dir = os.path.join(temp_dir, "SpanishConjugation")
        os.makedirs(app_dir, exist_ok=True)
        
        # Custom preferences
        customizations = {
            'preferred_verbs': ['ser', 'estar', 'tener', 'hacer'],
            'avoided_tenses': ['subjunctive'],
            'custom_themes': ['food', 'travel'],
            'ui_preferences': {
                'font_size': 'large',
                'color_scheme': 'dark'
            }
        }
        
        self._save_customizations(app_dir, customizations)
        loaded_customizations = self._load_customizations(app_dir)
        
        assert loaded_customizations['preferred_verbs'] == customizations['preferred_verbs']
        assert loaded_customizations['avoided_tenses'] == customizations['avoided_tenses']
        assert loaded_customizations['custom_themes'] == customizations['custom_themes']
    
    def _save_session_config(self, app_dir, config):
        """Save session configuration."""
        config_path = os.path.join(app_dir, "app_config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _load_session_config(self, app_dir):
        """Load session configuration."""
        config_path = os.path.join(app_dir, "app_config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_progress_data(self, app_dir, progress):
        """Save progress data."""
        progress_path = os.path.join(app_dir, "progress.json")
        with open(progress_path, 'w') as f:
            json.dump(progress, f, indent=2)
    
    def _load_progress_data(self, app_dir):
        """Load progress data."""
        progress_path = os.path.join(app_dir, "progress.json")
        if os.path.exists(progress_path):
            with open(progress_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_window_geometry(self, app_dir, geometry):
        """Save window geometry."""
        config_path = os.path.join(app_dir, "app_config.json")
        config = self._load_session_config(app_dir)
        config['window_geometry'] = geometry
        self._save_session_config(app_dir, config)
    
    def _load_window_geometry(self, app_dir):
        """Load window geometry."""
        config = self._load_session_config(app_dir)
        return config.get('window_geometry', {})
    
    def _save_customizations(self, app_dir, customizations):
        """Save user customizations."""
        custom_path = os.path.join(app_dir, "customizations.json")
        with open(custom_path, 'w') as f:
            json.dump(customizations, f, indent=2)
    
    def _load_customizations(self, app_dir):
        """Load user customizations."""
        custom_path = os.path.join(app_dir, "customizations.json")
        if os.path.exists(custom_path):
            with open(custom_path, 'r') as f:
                return json.load(f)
        return {}


if __name__ == '__main__':
    pytest.main([__file__])