"""
Local Exercise Generator
Creates Spanish conjugation exercises without API calls
Enhanced with discourse coherence and communicative context
"""

import random
from typing import List, Dict, Any, Optional
from conjugation_engine import SpanishConjugator, COMMON_VERBS, PERSON_LABELS, TENSE_NAMES

class ExerciseGenerator:
    """Generate conjugation exercises locally."""
    
    def __init__(self):
        self.conjugator = SpanishConjugator()
        
        # Sentence templates by person
        self.templates = {
            0: [  # yo
                "______ {context} todos los días.",
                "Siempre ______ {context}.",
                "Normalmente ______ {context}.",
                "______ {context} con frecuencia."
            ],
            1: [  # tú
                "¿______ {context}?",
                "Tú ______ {context}.",
                "¿Por qué ______ {context}?",
                "Cuando ______ {context}, me avisas."
            ],
            2: [  # él/ella/usted
                "Ella ______ {context}.",
                "Mi hermano ______ {context}.",
                "El profesor ______ {context}.",
                "María ______ {context} los lunes."
            ],
            3: [  # nosotros
                "______ {context} juntos.",
                "Nosotros ______ {context}.",
                "______ {context} en equipo.",
                "Siempre ______ {context} los domingos."
            ],
            4: [  # vosotros
                "Vosotros ______ {context}.",
                "¿______ {context} mañana?",
                "______ {context} muy bien.",
                "Cuando ______ {context}, decidme."
            ],
            5: [  # ellos/ellas/ustedes
                "Ellos ______ {context}.",
                "Mis amigos ______ {context}.",
                "Los estudiantes ______ {context}.",
                "______ {context} todas las semanas."
            ]
        }
        
        # Preterite templates
        self.preterite_templates = {
            0: ["Ayer ______ {context}.", "La semana pasada ______ {context}."],
            1: ["¿______ {context} ayer?", "______ {context} el lunes pasado."],
            2: ["Ella ______ {context} anoche.", "Juan ______ {context} el año pasado."],
            3: ["______ {context} juntos el mes pasado.", "Nosotros ______ {context} ayer."],
            4: ["¿______ {context} el fin de semana?", "Vosotros ______ {context} anoche."],
            5: ["Ellos ______ {context} la semana pasada.", "______ {context} hace dos días."]
        }
        
        # Imperfect templates
        self.imperfect_templates = {
            0: ["Cuando era niño, ______ {context}.", "Antes ______ {context} más."],
            1: ["Cuando eras joven, ¿______ {context}?", "Tú siempre ______ {context}."],
            2: ["Mi abuelo ______ {context} todos los días.", "Ella ______ {context} cuando vivía allí."],
            3: ["______ {context} cada verano.", "Nosotros ______ {context} juntos."],
            4: ["Vosotros ______ {context} mucho.", "¿______ {context} en aquella época?"],
            5: ["Ellos ______ {context} frecuentemente.", "Mis padres ______ {context} siempre."]
        }
        
        # Future templates
        self.future_templates = {
            0: ["Mañana ______ {context}.", "______ {context} la próxima semana."],
            1: ["¿______ {context} conmigo?", "______ {context} el domingo."],
            2: ["Ella ______ {context} pronto.", "Mi jefe ______ {context} mañana."],
            3: ["______ {context} juntos.", "Nosotros ______ {context} el próximo mes."],
            4: ["¿______ {context} en verano?", "Vosotros ______ {context} mañana."],
            5: ["Ellos ______ {context} el año que viene.", "Mis amigos ______ {context} pronto."]
        }
        
        # Subjunctive templates
        self.subjunctive_templates = {
            0: ["Es importante que ______ {context}.", "Espero que ______ {context}."],
            1: ["Es necesario que ______ {context}.", "Quiero que ______ {context}."],
            2: ["Es posible que ella ______ {context}.", "Dudo que él ______ {context}."],
            3: ["Es mejor que ______ {context}.", "Ojalá ______ {context}."],
            4: ["Es importante que ______ {context}.", "Prefiero que ______ {context}."],
            5: ["Es probable que ellos ______ {context}.", "No creo que ______ {context}."]
        }
        
        # Verb contexts (what comes after the verb)
        self.verb_contexts = {
            'hablar': ['español', 'con mis amigos', 'por teléfono', 'en clase'],
            'trabajar': ['en la oficina', 'desde casa', 'mucho', 'en equipo'],
            'estudiar': ['para el examen', 'matemáticas', 'en la biblioteca', 'medicina'],
            'comer': ['en el restaurante', 'pizza', 'con la familia', 'tarde'],
            'vivir': ['en Madrid', 'cerca del parque', 'solo', 'en un apartamento'],
            'escribir': ['un libro', 'cartas', 'en el diario', 'poemas'],
            'ser': ['feliz', 'profesor', 'importante', 'amable'],
            'estar': ['en casa', 'cansado', 'ocupado', 'contento'],
            'tener': ['tiempo', 'hambre', 'un coche nuevo', 'razón'],
            'hacer': ['ejercicio', 'la tarea', 'un pastel', 'deporte'],
            'ir': ['al parque', 'de compras', 'a la playa', 'al cine'],
            'poder': ['ayudarte', 'venir mañana', 'hacerlo', 'entender'],
            'saber': ['la respuesta', 'cocinar', 'la verdad', 'nadar'],
            'dar': ['un regalo', 'las gracias', 'un consejo', 'clases'],
            'ver': ['la película', 'a mis amigos', 'el partido', 'las noticias'],
            'decir': ['la verdad', 'algo importante', 'que sí', 'adiós']
        }
    
    def get_template_for_tense(self, tense, person):
        """Get appropriate template based on tense."""
        if tense == 'preterite':
            return random.choice(self.preterite_templates.get(person, self.templates[person]))
        elif tense == 'imperfect':
            return random.choice(self.imperfect_templates.get(person, self.templates[person]))
        elif tense == 'future':
            return random.choice(self.future_templates.get(person, self.templates[person]))
        elif tense == 'present_subjunctive':
            return random.choice(self.subjunctive_templates.get(person, self.templates[person]))
        else:
            return random.choice(self.templates[person])
    
    def generate_exercise(self, 
                         verb: Optional[str] = None,
                         tense: Optional[str] = None,
                         person: Optional[int] = None,
                         difficulty: str = 'intermediate') -> Dict[str, Any]:
        """
        Generate a single exercise.
        
        Args:
            verb: Specific verb to use (or None for random)
            tense: Specific tense to use (or None for random)
            person: Specific person to use (or None for random)
            difficulty: 'beginner', 'intermediate', or 'advanced'
        
        Returns:
            Dictionary with exercise data
        """
        # Select verb
        if verb is None:
            if difficulty == 'beginner':
                verb_type = random.choice(['regular', 'irregular'])
                if verb_type == 'regular':
                    ending = random.choice(['ar', 'er', 'ir'])
                    verb = random.choice(COMMON_VERBS['regular'][ending])
                else:
                    verb = random.choice(COMMON_VERBS['irregular'][:5])  # Basic irregular verbs
            elif difficulty == 'advanced':
                verb = random.choice(COMMON_VERBS['irregular'] + COMMON_VERBS['stem_changing'])
            else:  # intermediate
                all_verbs = []
                for ending in ['ar', 'er', 'ir']:
                    all_verbs.extend(COMMON_VERBS['regular'][ending])
                all_verbs.extend(COMMON_VERBS['irregular'])
                verb = random.choice(all_verbs)
        
        # Select tense
        if tense is None:
            if difficulty == 'beginner':
                tense = random.choice(['present', 'preterite'])
            elif difficulty == 'advanced':
                tense = random.choice(['present', 'preterite', 'imperfect', 'future', 'conditional', 'present_subjunctive'])
            else:
                tense = random.choice(['present', 'preterite', 'imperfect', 'future'])
        
        # Select person
        if person is None:
            person = random.randint(0, 5)
        
        # Get correct answer
        correct_answer = self.conjugator.conjugate(verb, tense, person)
        if not correct_answer:
            # Fallback if conjugation fails
            return self.generate_exercise(difficulty=difficulty)
        
        # Get context
        context = random.choice(self.verb_contexts.get(verb, ['']))
        
        # Get sentence template
        template = self.get_template_for_tense(tense, person)
        sentence = template.format(context=context)
        
        # Generate wrong choices
        choices = [correct_answer]
        
        # Add other conjugations of same verb
        for other_person in range(6):
            if other_person != person:
                other_form = self.conjugator.conjugate(verb, tense, other_person)
                if other_form and other_form not in choices:
                    choices.append(other_form)
                    if len(choices) >= 4:
                        break
        
        # Add conjugations from other tenses if needed
        if len(choices) < 4:
            other_tenses = [t for t in ['present', 'preterite', 'imperfect'] if t != tense]
            for other_tense in other_tenses:
                form = self.conjugator.conjugate(verb, other_tense, person)
                if form and form not in choices:
                    choices.append(form)
                    if len(choices) >= 4:
                        break
        
        # Ensure we have 4 choices
        while len(choices) < 4:
            choices.append(f"{verb[:-2]}ando")  # Fake gerund form
        
        # Create exercise dictionary
        exercise = {
            'sentence': sentence,
            'answer': correct_answer,
            'choices': choices[:4],
            'verb': verb,
            'tense': TENSE_NAMES.get(tense, tense),
            'person': PERSON_LABELS[person],
            'translation': f"[{PERSON_LABELS[person]}] {verb} ({TENSE_NAMES.get(tense, tense)})",
            'context': f"Verb: {verb} | Tense: {TENSE_NAMES.get(tense, tense)} | Person: {PERSON_LABELS[person]}"
        }
        
        return exercise
    
    def generate_batch(self, 
                      count: int = 5,
                      verbs: List[str] = None,
                      tenses: List[str] = None,
                      persons: List[int] = None,
                      difficulty: str = 'intermediate') -> List[Dict[str, Any]]:
        """Generate a batch of exercises."""
        exercises = []
        
        for _ in range(count):
            # Select from provided options or use None for random
            verb = random.choice(verbs) if verbs else None
            tense = random.choice(tenses) if tenses else None
            person = random.choice(persons) if persons else None
            
            exercise = self.generate_exercise(verb, tense, person, difficulty)
            exercises.append(exercise)
        
        return exercises
    
    def generate_story_sequence(self, tense: str = 'preterite', length: int = 5) -> List[Dict[str, Any]]:
        """
        Generate a connected story with multiple blanks.
        This provides discourse coherence - verbs relate to each other.
        """
        stories = {
            'preterite': [
                {
                    'title': 'Un día en la playa',
                    'sentences': [
                        ('Ayer mi familia y yo ______ a la playa.', 'ir', 3),
                        ('______ muy temprano por la mañana.', 'salir', 3),
                        ('Mi hermana ______ sandwiches para todos.', 'preparar', 2),
                        ('Los niños ______ en el mar todo el día.', 'nadar', 5),
                        ('Por la tarde, ______ helados y descansamos.', 'comer', 3)
                    ]
                },
                {
                    'title': 'Mi primer día de trabajo',
                    'sentences': [
                        ('______ muy nervioso esa mañana.', 'estar', 0),
                        ('______ a la oficina media hora antes.', 'llegar', 0),
                        ('Mi jefe me ______ a todo el equipo.', 'presentar', 2),
                        ('Todos ______ muy amables conmigo.', 'ser', 5),
                        ('Al final del día, me ______ muy contento.', 'sentir', 0)
                    ]
                }
            ],
            'present': [
                {
                    'title': 'Mi rutina diaria',
                    'sentences': [
                        ('Todos los días ______ a las 7 de la mañana.', 'levantarse', 0),
                        ('Primero ______ un café bien fuerte.', 'tomar', 0),
                        ('Después ______ el periódico en línea.', 'leer', 0),
                        ('Mi esposa ______ el desayuno mientras yo me ducho.', 'preparar', 2),
                        ('Los dos ______ de casa a las 8:30.', 'salir', 3)
                    ]
                }
            ],
            'imperfect': [
                {
                    'title': 'Cuando era niño',
                    'sentences': [
                        ('Cuando era niño, ______ en un pueblo pequeño.', 'vivir', 0),
                        ('Mi abuela siempre ______ historias fascinantes.', 'contar', 2),
                        ('Mis hermanos y yo ______ en el jardín.', 'jugar', 3),
                        ('Los domingos ______ a visitar a los primos.', 'ir', 3),
                        ('______ una vida muy tranquila y feliz.', 'ser', 2)
                    ]
                }
            ]
        }
        
        # Select a story for the given tense
        if tense not in stories:
            tense = 'present'
        
        story_data = random.choice(stories[tense])
        exercises = []
        
        for i, (sentence, verb, person) in enumerate(story_data['sentences'][:length]):
            correct_answer = self.conjugator.conjugate(verb, tense, person)
            
            # Generate distractors from same story context
            choices = [correct_answer]
            for _, other_verb, other_person in story_data['sentences']:
                if other_verb != verb or other_person != person:
                    other_form = self.conjugator.conjugate(other_verb, tense, other_person)
                    if other_form and other_form not in choices:
                        choices.append(other_form)
                        if len(choices) >= 4:
                            break
            
            exercise = {
                'sentence': sentence,
                'answer': correct_answer,
                'choices': choices[:4],
                'verb': verb,
                'tense': TENSE_NAMES.get(tense, tense),
                'person': PERSON_LABELS[person],
                'story_title': story_data['title'],
                'story_position': i + 1,
                'story_total': min(length, len(story_data['sentences'])),
                'context': f"Part {i+1} of story: {story_data['title']}"
            }
            exercises.append(exercise)
        
        return exercises