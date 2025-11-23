"""
Speed Practice Mode - The Missing Piece
Builds conversational fluency through timed production
"""

import time
from typing import Dict, List, Tuple, Optional
from conjugation_engine import SpanishConjugator

class SpeedPractice:
    """
    Train instant verb production - the #1 skill for conversation.
    Simple but addresses the core problem.
    """
    
    def __init__(self):
        self.conjugator = SpanishConjugator()
        
        # Only the most essential verbs for conversation
        # These 20 verbs cover 50% of Spanish conversation
        self.essential_verbs = [
            'ser', 'estar', 'tener', 'hacer', 'poder',
            'decir', 'ir', 'ver', 'dar', 'saber',
            'querer', 'llegar', 'pasar', 'deber', 'poner',
            'parecer', 'quedar', 'creer', 'hablar', 'llevar'
        ]
        
        # Real conversation patterns (not academic sentences)
        self.conversation_triggers = {
            'yo': [
                "Someone asks '¿Qué haces?' You say:",
                "Your friend asks '¿Vienes?' You respond:",
                "They ask '¿Lo sabes?' You answer:",
                "Someone says '¿Puedes ayudarme?' You say:"
            ],
            'tú': [
                "Ask your friend what they want:",
                "Ask if they can come:",
                "Ask what they think:",
                "Ask where they're going:"
            ],
            'él/ella': [
                "Tell someone what Maria wants:",
                "Explain what your boss says:",
                "Describe what your friend does:",
                "Say where Juan is:"
            ]
        }
        
        # Track response times for each verb
        self.response_times = {}
        self.accuracy_under_pressure = {}
    
    def generate_speed_round(self, duration_seconds: int = 60) -> List[Dict]:
        """
        Generate rapid-fire exercises for X seconds.
        Focus: produce correct form FAST.
        """
        exercises = []
        prompts_per_round = duration_seconds // 3  # 3 seconds per verb
        
        import random
        for _ in range(prompts_per_round):
            verb = random.choice(self.essential_verbs)
            person = random.randint(0, 2)  # Focus on yo/tú/él (most used)
            
            # Always present tense for speed practice
            # (Master present before adding complexity)
            answer = self.conjugator.conjugate(verb, 'present', person)
            
            # Create pressure scenario
            person_labels = ['yo', 'tú', 'él/ella']
            trigger = random.choice(self.conversation_triggers[person_labels[person]])
            
            exercise = {
                'trigger': trigger,
                'verb': verb,
                'verb_english': self.get_verb_meaning(verb),
                'person': person,
                'answer': answer,
                'time_limit': 3.0,  # 3 seconds to answer
                'scenario': f"Quick! Use '{verb}' ({self.get_verb_meaning(verb)})"
            }
            exercises.append(exercise)
        
        return exercises
    
    def evaluate_speed_response(self, verb: str, person: int, 
                               user_answer: str, response_time: float) -> Dict:
        """
        Evaluate both accuracy AND speed.
        In conversation, slow correct answers = communication breakdown.
        """
        correct_answer = self.conjugator.conjugate(verb, 'present', person)
        is_correct = user_answer.strip().lower() == correct_answer.lower()
        
        # Speed categories (based on conversation flow)
        if response_time < 1.5:
            speed_rating = "⚡ Instant (Native-like)"
        elif response_time < 3.0:
            speed_rating = "✅ Conversational"
        elif response_time < 5.0:
            speed_rating = "🐢 Too slow (conversation breaks)"
        else:
            speed_rating = "❌ Not conversational"
        
        # Track performance
        if verb not in self.response_times:
            self.response_times[verb] = []
        self.response_times[verb].append(response_time)
        
        # Calculate improvement
        improvement = None
        if len(self.response_times[verb]) > 1:
            prev_avg = sum(self.response_times[verb][:-1]) / len(self.response_times[verb][:-1])
            improvement = prev_avg - response_time
        
        return {
            'correct': is_correct,
            'response_time': response_time,
            'speed_rating': speed_rating,
            'correct_answer': correct_answer,
            'conversational': response_time < 3.0 and is_correct,
            'improvement': improvement,
            'feedback': self.get_speed_feedback(is_correct, response_time)
        }
    
    def get_speed_feedback(self, correct: bool, time: float) -> str:
        """Simple, focused feedback on the real issue."""
        if correct and time < 1.5:
            return "Perfect! This is automatic for you."
        elif correct and time < 3.0:
            return "Good! Fast enough for conversation."
        elif correct:
            return "Correct but too slow. In real conversation, you'd lose the flow."
        elif time < 3.0:
            return "Fast but wrong. Slow down slightly and focus."
        else:
            return "Need more practice with this verb. Speed comes with repetition."
    
    def get_verb_meaning(self, verb: str) -> str:
        """Simple English meanings for context."""
        meanings = {
            'ser': 'to be (permanent)',
            'estar': 'to be (temporary)',
            'tener': 'to have',
            'hacer': 'to do/make',
            'poder': 'can/to be able',
            'decir': 'to say/tell',
            'ir': 'to go',
            'ver': 'to see',
            'dar': 'to give',
            'saber': 'to know (fact)',
            'querer': 'to want',
            'llegar': 'to arrive',
            'pasar': 'to happen/pass',
            'deber': 'should/must',
            'poner': 'to put',
            'parecer': 'to seem',
            'quedar': 'to stay/remain',
            'creer': 'to believe',
            'hablar': 'to speak',
            'llevar': 'to carry/wear'
        }
        return meanings.get(verb, verb)
    
    def get_weak_spots(self) -> List[Tuple[str, float]]:
        """Identify verbs that are too slow for conversation."""
        slow_verbs = []
        for verb, times in self.response_times.items():
            avg_time = sum(times) / len(times)
            if avg_time > 3.0:  # Not conversational
                slow_verbs.append((verb, avg_time))
        
        return sorted(slow_verbs, key=lambda x: x[1], reverse=True)
    
    def get_session_summary(self) -> Dict:
        """Focus on what matters: can you speak fluently?"""
        total_attempts = sum(len(times) for times in self.response_times.values())
        if total_attempts == 0:
            return {'ready': False, 'message': 'No practice data yet'}
        
        # Calculate conversational readiness
        conversational_verbs = []
        struggling_verbs = []
        
        for verb, times in self.response_times.items():
            avg_time = sum(times) / len(times)
            if avg_time < 3.0:
                conversational_verbs.append(verb)
            else:
                struggling_verbs.append((verb, avg_time))
        
        readiness_percent = (len(conversational_verbs) / len(self.essential_verbs)) * 100
        
        return {
            'ready': readiness_percent > 70,
            'readiness_percent': readiness_percent,
            'conversational_verbs': conversational_verbs,
            'need_work': struggling_verbs[:5],  # Top 5 to focus on
            'message': self.get_readiness_message(readiness_percent)
        }
    
    def get_readiness_message(self, percent: float) -> str:
        """Honest assessment of conversational readiness."""
        if percent > 80:
            return "You're ready for real conversations! Your verb recall is automatic."
        elif percent > 60:
            return "Getting there! A few more practice sessions and you'll be conversational."
        elif percent > 40:
            return "Building foundation. Focus on the verbs you're slow with."
        else:
            return "Keep practicing. Fluency comes from instant recall, not just knowing the rules."