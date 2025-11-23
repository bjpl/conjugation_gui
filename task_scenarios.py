"""
Simple Task-Based Scenarios for Spanish Practice
Minimal TBLT implementation without overengineering
"""

import random
from typing import Dict, List, Any, Optional
from conjugation_engine import SpanishConjugator, PERSON_LABELS

class TaskScenario:
    """Simple task-based learning scenarios."""
    
    def __init__(self):
        self.conjugator = SpanishConjugator()
        
        # Simple real-world scenarios (not abstract grammar)
        self.scenarios = {
            'restaurant': {
                'title': '🍽️ At a Restaurant',
                'context': 'You are ordering food with friends',
                'tasks': [
                    {
                        'goal': 'Order your meal',
                        'prompt': 'Tell the waiter what you want to eat',
                        'template': 'Yo ______ (querer) la paella, por favor.',
                        'verb': 'querer',
                        'tense': 'present',
                        'person': 0,
                        'success_criteria': 'communicates desire for food',
                        'follow_up': '¿Y para beber?'
                    },
                    {
                        'goal': 'Ask about ingredients',
                        'prompt': 'You have allergies - ask what the dish contains',
                        'template': '¿Qué ______ (tener) este plato?',
                        'verb': 'tener',
                        'tense': 'present',
                        'person': 2,
                        'success_criteria': 'successfully inquires about contents'
                    },
                    {
                        'goal': 'Request the bill',
                        'prompt': 'You finished eating and want to pay',
                        'template': '¿______ (poder) traer la cuenta?',
                        'verb': 'poder',
                        'tense': 'present',
                        'person': 2,
                        'success_criteria': 'politely requests bill'
                    }
                ]
            },
            'travel': {
                'title': '✈️ Planning a Trip',
                'context': 'Discussing vacation plans with a friend',
                'tasks': [
                    {
                        'goal': 'Suggest a destination',
                        'prompt': 'Propose where to go for vacation',
                        'template': '¿Por qué no ______ (ir) a Costa Rica?',
                        'verb': 'ir',
                        'tense': 'present',
                        'person': 3,
                        'success_criteria': 'makes travel suggestion'
                    },
                    {
                        'goal': 'Discuss dates',
                        'prompt': 'Say when you can travel',
                        'template': 'Yo ______ (poder) viajar en julio.',
                        'verb': 'poder',
                        'tense': 'present',
                        'person': 0,
                        'success_criteria': 'communicates availability'
                    },
                    {
                        'goal': 'Express preferences',
                        'prompt': 'Say what you prefer to do on vacation',
                        'template': 'Prefiero ______ (estar) cerca de la playa.',
                        'verb': 'estar',
                        'tense': 'present',
                        'person': 0,
                        'success_criteria': 'expresses preference clearly'
                    }
                ]
            },
            'daily_routine': {
                'title': '🌅 Daily Routine',
                'context': 'Describing your typical day to a new friend',
                'tasks': [
                    {
                        'goal': 'Describe morning routine',
                        'prompt': 'Tell what time you wake up',
                        'template': 'Normalmente ______ (levantarse) a las siete.',
                        'verb': 'levantarse',
                        'tense': 'present',
                        'person': 0,
                        'success_criteria': 'shares routine information'
                    },
                    {
                        'goal': 'Talk about work/study',
                        'prompt': 'Explain what you do during the day',
                        'template': '______ (trabajar) en una oficina.',
                        'verb': 'trabajar',
                        'tense': 'present',
                        'person': 0,
                        'success_criteria': 'describes occupation/activity'
                    }
                ]
            },
            'making_plans': {
                'title': '📅 Making Plans',
                'context': 'Arranging to meet friends this weekend',
                'tasks': [
                    {
                        'goal': 'Suggest an activity',
                        'prompt': 'Propose something fun to do',
                        'template': '¿______ (querer) ir al cine el sábado?',
                        'verb': 'querer',
                        'tense': 'present',
                        'person': 1,
                        'success_criteria': 'makes social invitation'
                    },
                    {
                        'goal': 'Confirm availability',
                        'prompt': 'Say if you can make it',
                        'template': 'Sí, ______ (poder) a las ocho.',
                        'verb': 'poder',
                        'tense': 'present',
                        'person': 0,
                        'success_criteria': 'confirms attendance'
                    }
                ]
            },
            'shopping': {
                'title': '🛍️ At the Store',
                'context': 'Buying clothes at a shop',
                'tasks': [
                    {
                        'goal': 'Ask for help',
                        'prompt': 'Get assistance from store clerk',
                        'template': '¿______ (tener) esta camisa en talla M?',
                        'verb': 'tener',
                        'tense': 'present',
                        'person': 5,
                        'success_criteria': 'requests specific item'
                    },
                    {
                        'goal': 'Express opinion',
                        'prompt': 'Say what you think about an item',
                        'template': 'Me ______ (gustar) el color azul.',
                        'verb': 'gustar',
                        'tense': 'present',
                        'person': 2,
                        'success_criteria': 'expresses preference'
                    }
                ]
            },
            'health': {
                'title': '🏥 At the Doctor',
                'context': 'Explaining symptoms to a doctor',
                'tasks': [
                    {
                        'goal': 'Describe symptoms',
                        'prompt': 'Tell the doctor how you feel',
                        'template': 'Me ______ (doler) la cabeza desde ayer.',
                        'verb': 'doler',
                        'tense': 'present',
                        'person': 2,
                        'success_criteria': 'communicates health issue'
                    },
                    {
                        'goal': 'Explain duration',
                        'prompt': 'Say how long you have been sick',
                        'template': '______ (estar) enfermo por tres días.',
                        'verb': 'estar',
                        'tense': 'present',
                        'person': 0,
                        'success_criteria': 'provides timeline'
                    }
                ]
            }
        }
        
        # Track completed tasks for progress
        self.completed_scenarios = set()
    
    def get_scenario(self, scenario_type: Optional[str] = None) -> Dict[str, Any]:
        """Get a complete scenario with multiple tasks."""
        if scenario_type and scenario_type in self.scenarios:
            return self.scenarios[scenario_type]
        return random.choice(list(self.scenarios.values()))
    
    def get_task_sequence(self, scenario_type: str, count: int = 3) -> List[Dict[str, Any]]:
        """Get a sequence of related tasks from a scenario."""
        if scenario_type not in self.scenarios:
            scenario_type = random.choice(list(self.scenarios.keys()))
        
        scenario = self.scenarios[scenario_type]
        tasks = scenario['tasks'][:count] if len(scenario['tasks']) >= count else scenario['tasks']
        
        # Add scenario context to each task
        for task in tasks:
            task['scenario_title'] = scenario['title']
            task['scenario_context'] = scenario['context']
        
        return tasks
    
    def evaluate_response(self, user_answer: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate response based on communicative success, not just accuracy.
        Returns both grammatical accuracy and communicative effectiveness.
        """
        verb = task['verb']
        tense = task['tense']
        person = task['person']
        
        # Get correct conjugation
        correct_form = self.conjugator.conjugate(verb, tense, person)
        
        # Check grammatical accuracy
        grammatical_accuracy = user_answer.strip().lower() == correct_form.lower()
        
        # Check communicative success (simplified - in reality would need NLP)
        # For now, we check if the answer is close enough to convey meaning
        communicative_success = self._check_communicative_success(
            user_answer, correct_form, task['success_criteria']
        )
        
        return {
            'grammatically_correct': grammatical_accuracy,
            'communicatively_successful': communicative_success,
            'correct_form': correct_form,
            'feedback': self._generate_feedback(
                grammatical_accuracy, 
                communicative_success,
                task['goal']
            )
        }
    
    def _check_communicative_success(self, user_answer: str, correct_form: str, criteria: str) -> bool:
        """
        Simple heuristic for communicative success.
        In a real app, this would use NLP to check if meaning is conveyed.
        """
        user_clean = user_answer.strip().lower()
        correct_clean = correct_form.lower()
        
        # If completely correct, it's communicatively successful
        if user_clean == correct_clean:
            return True
        
        # Check if stem is correct (communicates basic meaning)
        if len(user_clean) > 3 and len(correct_clean) > 3:
            if user_clean[:3] == correct_clean[:3]:
                return True
        
        # Check Levenshtein distance (allows minor spelling errors)
        if self._levenshtein_distance(user_clean, correct_clean) <= 2:
            return True
        
        return False
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Simple edit distance calculation."""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _generate_feedback(self, grammatical: bool, communicative: bool, goal: str) -> str:
        """Generate appropriate feedback based on performance."""
        if grammatical and communicative:
            return f"✅ Excellent! You successfully achieved the goal: {goal}"
        elif communicative and not grammatical:
            return f"🔄 Good communication! Your message was understood, though the form wasn't perfect. Goal achieved: {goal}"
        elif grammatical and not communicative:
            return f"⚠️ Grammatically correct, but the message wasn't clear for the situation."
        else:
            return f"❌ Let's try again. Remember the goal: {goal}"
    
    def get_scenario_list(self) -> List[str]:
        """Get list of available scenarios."""
        return list(self.scenarios.keys())
    
    def mark_scenario_complete(self, scenario_type: str):
        """Mark a scenario as completed."""
        self.completed_scenarios.add(scenario_type)
    
    def get_progress(self) -> Dict[str, Any]:
        """Get user's progress through scenarios."""
        total_scenarios = len(self.scenarios)
        completed = len(self.completed_scenarios)
        
        return {
            'total_scenarios': total_scenarios,
            'completed_scenarios': completed,
            'percentage': (completed / total_scenarios) * 100 if total_scenarios > 0 else 0,
            'completed_list': list(self.completed_scenarios)
        }