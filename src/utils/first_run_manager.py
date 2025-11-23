"""
First-Run Detection and Configuration Flow Manager
"""

import os
import json
import sys
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

class FirstRunManager:
    """Manages first-run detection and configuration flow"""
    
    def __init__(self, config_file: str = "app_config.json"):
        self.config_file = config_file
        self.config_dir = Path.home() / ".spanish_conjugation_trainer"
        self.user_config_file = self.config_dir / "user_config.json"
        self.setup_complete_marker = self.config_dir / ".setup_complete"
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)
        
        self.default_config = {
            "setup_complete": False,
            "version": "2.0.0",
            "first_run_date": None,
            "last_run_date": None,
            "run_count": 0,
            
            # API Configuration
            "api_key": "",
            "api_model": "gpt-4o",
            "max_tokens": 600,
            "temperature": 0.5,
            "offline_mode": False,
            
            # Learning Settings
            "difficulty": "intermediate",
            "exercise_count": 5,
            "answer_strictness": "normal",
            "preferred_tenses": ["Present", "Preterite"],
            "speed_timer": 3,
            
            # Appearance Settings
            "dark_mode": False,
            "show_translation": False,
            "minimize_to_tray": True,
            "start_minimized": False,
            "window_geometry": {
                "width": 1100,
                "height": 700,
                "x": 100,
                "y": 100
            },
            "remember_position": True,
            
            # Advanced Settings
            "max_stored_responses": 100,
            "auto_backup": False,
            "notification_settings": {
                "session_complete": True,
                "achievements": True,
                "reminders": False,
                "errors": True
            }
        }
    
    def is_first_run(self) -> bool:
        """Check if this is the first run of the application"""
        # Check multiple indicators
        markers = [
            not self.setup_complete_marker.exists(),
            not self.user_config_file.exists(),
            not self.is_setup_completed()
        ]
        return any(markers)
    
    def is_setup_completed(self) -> bool:
        """Check if setup wizard has been completed"""
        try:
            if self.user_config_file.exists():
                with open(self.user_config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get("setup_complete", False)
        except Exception:
            pass
        return False
    
    def get_run_count(self) -> int:
        """Get the number of times the application has been run"""
        try:
            if self.user_config_file.exists():
                with open(self.user_config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get("run_count", 0)
        except Exception:
            pass
        return 0
    
    def load_configuration(self) -> Dict[str, Any]:
        """Load configuration, merging defaults with user settings"""
        config = self.default_config.copy()
        
        # Load from project config file (if exists)
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    project_config = json.load(f)
                    config.update(project_config)
            except Exception as e:
                print(f"Warning: Could not load project config: {e}")
        
        # Load from user config file (takes precedence)
        if self.user_config_file.exists():
            try:
                with open(self.user_config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    config.update(user_config)
            except Exception as e:
                print(f"Warning: Could not load user config: {e}")
        
        return config
    
    def save_configuration(self, config: Dict[str, Any]) -> bool:
        """Save configuration to user config file"""
        try:
            # Update timestamps and run count
            from datetime import datetime
            now = datetime.now().isoformat()
            
            if not config.get("first_run_date"):
                config["first_run_date"] = now
            
            config["last_run_date"] = now
            config["run_count"] = config.get("run_count", 0) + 1
            config["version"] = "2.0.0"
            
            # Save to user config
            with open(self.user_config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            # Also update project config for compatibility
            if os.path.exists(self.config_file):
                try:
                    with open(self.config_file, 'w', encoding='utf-8') as f:
                        json.dump(config, f, indent=2)
                except Exception:
                    pass  # Don't fail if we can't write to project config
            
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    def mark_setup_complete(self, config: Dict[str, Any]) -> bool:
        """Mark setup as complete and save final configuration"""
        config["setup_complete"] = True
        
        # Save configuration
        success = self.save_configuration(config)
        
        if success:
            # Create setup complete marker file
            try:
                with open(self.setup_complete_marker, 'w') as f:
                    f.write(f"Setup completed on: {config['last_run_date']}\n")
                return True
            except Exception as e:
                print(f"Warning: Could not create setup marker: {e}")
                return True  # Config save succeeded, marker failure is not critical
        
        return False
    
    def reset_setup(self) -> bool:
        """Reset setup status (for testing or reconfiguration)"""
        try:
            # Remove marker file
            if self.setup_complete_marker.exists():
                self.setup_complete_marker.unlink()
            
            # Reset setup_complete flag in config
            config = self.load_configuration()
            config["setup_complete"] = False
            self.save_configuration(config)
            
            return True
        except Exception as e:
            print(f"Error resetting setup: {e}")
            return False
    
    def backup_configuration(self) -> Optional[str]:
        """Create a backup of current configuration"""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.config_dir / f"config_backup_{timestamp}.json"
            
            config = self.load_configuration()
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            return str(backup_file)
        except Exception as e:
            print(f"Error creating config backup: {e}")
            return None
    
    def restore_configuration(self, backup_file: str) -> bool:
        """Restore configuration from backup"""
        try:
            if not os.path.exists(backup_file):
                return False
            
            with open(backup_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            return self.save_configuration(config)
        except Exception as e:
            print(f"Error restoring config backup: {e}")
            return False
    
    def get_welcome_message(self) -> str:
        """Get appropriate welcome message based on run status"""
        if self.is_first_run():
            return (
                "Welcome to Spanish Conjugation Trainer!\n\n"
                "This appears to be your first time using the application. "
                "Let's set up your learning preferences to get you started."
            )
        else:
            run_count = self.get_run_count()
            config = self.load_configuration()
            last_run = config.get("last_run_date", "")
            
            if run_count < 5:
                return (
                    f"Welcome back to Spanish Conjugation Trainer!\n\n"
                    f"This is your {run_count + 1} time using the app. "
                    "We're glad you're continuing your Spanish learning journey!"
                )
            else:
                return (
                    "Welcome back!\n\n"
                    "Ready to continue mastering Spanish verb conjugations?"
                )
    
    def should_show_tips(self) -> bool:
        """Determine if tips should be shown based on usage"""
        run_count = self.get_run_count()
        return run_count < 3  # Show tips for first few runs
    
    def get_startup_tips(self) -> list:
        """Get contextual startup tips"""
        run_count = self.get_run_count()
        
        if run_count == 0:
            return [
                "💡 Click 'New Exercise' to generate your first practice session",
                "🎯 Try different practice modes from the toolbar",
                "📊 Check your progress in the Statistics view",
            ]
        elif run_count == 1:
            return [
                "⚡ Try Speed Mode to build conversational fluency",
                "🌙 Toggle dark mode from the toolbar if you prefer",
                "🔧 Access Settings to customize your experience",
            ]
        elif run_count == 2:
            return [
                "📝 Create custom exercises with the Custom Practice tool",
                "📈 Export your progress to keep a backup",
                "💬 Use Task Mode for real-world conversation practice",
            ]
        else:
            return []
    
    def cleanup_old_backups(self, keep_count: int = 5):
        """Clean up old configuration backups"""
        try:
            backup_pattern = "config_backup_*.json"
            backup_files = list(self.config_dir.glob(backup_pattern))
            
            # Sort by modification time, newest first
            backup_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            # Remove old backups
            for backup_file in backup_files[keep_count:]:
                backup_file.unlink()
                print(f"Removed old backup: {backup_file.name}")
                
        except Exception as e:
            print(f"Error cleaning up backups: {e}")

class WelcomeMessage:
    """Handles welcome messages and onboarding"""
    
    @staticmethod
    def get_feature_highlights() -> list:
        """Get list of key features to highlight"""
        return [
            {
                'icon': '🤖',
                'title': 'AI-Powered Learning',
                'description': 'Get intelligent explanations and personalized exercises with GPT-4o'
            },
            {
                'icon': '⚡',
                'title': 'Speed Mode',
                'description': 'Build conversational fluency with timed practice sessions'
            },
            {
                'icon': '📊',
                'title': 'Progress Tracking',
                'description': 'Monitor your improvement with detailed statistics and analytics'
            },
            {
                'icon': '🎯',
                'title': 'Task-Based Learning',
                'description': 'Practice with real-world scenarios and conversational contexts'
            },
            {
                'icon': '🌙',
                'title': 'Professional Design',
                'description': 'Beautiful dark/light themes and professional user interface'
            },
            {
                'icon': '🔄',
                'title': 'Offline Capable',
                'description': 'Continue learning even without an internet connection'
            }
        ]
    
    @staticmethod
    def get_quick_start_steps() -> list:
        """Get quick start steps for new users"""
        return [
            {
                'step': 1,
                'title': 'Complete Setup',
                'description': 'Configure your API key and learning preferences',
                'action': 'Run the setup wizard'
            },
            {
                'step': 2,
                'title': 'Generate Exercises',
                'description': 'Click "New Exercise" to create your first practice session',
                'action': 'Try generating 5 exercises'
            },
            {
                'step': 3,
                'title': 'Explore Modes',
                'description': 'Try Speed Mode, Task Mode, and Story Mode',
                'action': 'Experiment with different practice styles'
            },
            {
                'step': 4,
                'title': 'Track Progress',
                'description': 'View your statistics and learning analytics',
                'action': 'Check the Statistics menu'
            }
        ]