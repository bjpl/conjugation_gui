"""
Simple Learning Path System
Guides users through logical progression without complexity
"""

from typing import Dict, List, Any, Optional

class LearningPath:
    """Simple structured learning progression."""
    
    def __init__(self):
        # Logical progression from easy to complex
        self.paths = {
            'beginner': {
                'name': '🌱 Beginner Path',
                'description': 'Start with present tense regular verbs',
                'stages': [
                    {
                        'name': 'Present Regular -AR',
                        'verbs': ['hablar', 'caminar', 'estudiar'],
                        'tenses': ['present'],
                        'focus': 'Master -ar endings'
                    },
                    {
                        'name': 'Present Regular -ER/-IR', 
                        'verbs': ['comer', 'vivir', 'escribir'],
                        'tenses': ['present'],
                        'focus': 'Learn -er and -ir patterns'
                    },
                    {
                        'name': 'Essential Irregulars',
                        'verbs': ['ser', 'estar', 'tener', 'hacer'],
                        'tenses': ['present'],
                        'focus': 'Most common irregular verbs'
                    },
                    {
                        'name': 'Past Tense Introduction',
                        'verbs': ['hablar', 'comer', 'vivir'],
                        'tenses': ['preterite'],
                        'focus': 'Simple past actions'
                    }
                ]
            },
            'intermediate': {
                'name': '🎯 Intermediate Path',
                'description': 'Expand tenses and irregular patterns',
                'stages': [
                    {
                        'name': 'Preterite Mastery',
                        'verbs': ['ir', 'ser', 'hacer', 'tener', 'estar'],
                        'tenses': ['preterite'],
                        'focus': 'Irregular preterite forms'
                    },
                    {
                        'name': 'Imperfect vs Preterite',
                        'verbs': ['hablar', 'ser', 'estar', 'tener'],
                        'tenses': ['preterite', 'imperfect'],
                        'focus': 'Understand aspect differences'
                    },
                    {
                        'name': 'Future & Conditional',
                        'verbs': ['hablar', 'tener', 'poder', 'saber'],
                        'tenses': ['future', 'conditional'],
                        'focus': 'Express future and hypothetical'
                    },
                    {
                        'name': 'Stem-Changing Verbs',
                        'verbs': ['pensar', 'dormir', 'pedir', 'jugar'],
                        'tenses': ['present', 'preterite'],
                        'focus': 'e→ie, o→ue, e→i patterns'
                    }
                ]
            },
            'advanced': {
                'name': '🚀 Advanced Path',
                'description': 'Subjunctive and complex structures',
                'stages': [
                    {
                        'name': 'Present Subjunctive',
                        'verbs': ['hablar', 'ser', 'tener', 'hacer'],
                        'tenses': ['present_subjunctive'],
                        'focus': 'Wishes, doubts, emotions'
                    },
                    {
                        'name': 'All Tenses Integration',
                        'verbs': ['ser', 'estar', 'tener', 'hacer', 'poder'],
                        'tenses': ['present', 'preterite', 'imperfect', 'future', 'conditional', 'present_subjunctive'],
                        'focus': 'Fluent tense switching'
                    }
                ]
            }
        }
        
        # Track user's current position
        self.current_path = 'beginner'
        self.current_stage = 0
        self.stage_progress = {}  # Track completion per stage
    
    def get_current_stage(self) -> Dict[str, Any]:
        """Get the current learning stage."""
        path = self.paths[self.current_path]
        if self.current_stage < len(path['stages']):
            return path['stages'][self.current_stage]
        return None
    
    def get_stage_exercises(self) -> Dict[str, Any]:
        """Get exercise parameters for current stage."""
        stage = self.get_current_stage()
        if stage:
            return {
                'verbs': stage['verbs'],
                'tenses': stage['tenses'],
                'count': 10,
                'focus_message': stage['focus']
            }
        return None
    
    def complete_stage(self, accuracy: float):
        """Mark current stage as complete if accuracy is sufficient."""
        stage_key = f"{self.current_path}_{self.current_stage}"
        self.stage_progress[stage_key] = accuracy
        
        # Move to next stage if accuracy > 70%
        if accuracy >= 70:
            self.current_stage += 1
            path = self.paths[self.current_path]
            
            # Check if path is complete
            if self.current_stage >= len(path['stages']):
                return {'path_complete': True, 'message': f"Congratulations! You've completed the {path['name']}"}
            else:
                next_stage = path['stages'][self.current_stage]
                return {'path_complete': False, 'message': f"Moving to: {next_stage['name']}"}
        else:
            return {'path_complete': False, 'message': f"Keep practicing! Aim for 70% accuracy (current: {accuracy:.0f}%)"}
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get overall learning progress."""
        total_stages = sum(len(p['stages']) for p in self.paths.values())
        completed_stages = len([v for v in self.stage_progress.values() if v >= 70])
        
        return {
            'current_path': self.paths[self.current_path]['name'],
            'current_stage': self.current_stage + 1,
            'total_stages_in_path': len(self.paths[self.current_path]['stages']),
            'overall_completion': (completed_stages / total_stages) * 100 if total_stages > 0 else 0,
            'completed_stages': completed_stages,
            'total_stages': total_stages
        }
    
    def switch_path(self, path_name: str):
        """Switch to a different learning path."""
        if path_name in self.paths:
            self.current_path = path_name
            self.current_stage = 0
            return True
        return False
    
    def get_available_paths(self) -> List[Dict[str, str]]:
        """Get list of available learning paths."""
        return [
            {
                'id': key,
                'name': path['name'],
                'description': path['description'],
                'stages': len(path['stages'])
            }
            for key, path in self.paths.items()
        ]
    
    def recommend_path(self, user_level: Optional[str] = None) -> str:
        """Recommend a learning path based on user level."""
        if user_level:
            if user_level.lower() in self.paths:
                return user_level.lower()
        
        # Default recommendation based on progress
        if not self.stage_progress:
            return 'beginner'
        
        # Check beginner completion
        beginner_stages = len(self.paths['beginner']['stages'])
        beginner_complete = sum(1 for i in range(beginner_stages) 
                               if f"beginner_{i}" in self.stage_progress 
                               and self.stage_progress[f"beginner_{i}"] >= 70)
        
        if beginner_complete >= beginner_stages * 0.8:
            return 'intermediate'
        
        return 'beginner'