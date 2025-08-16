"""
Simple Spanish Conjugation Engine
Handles regular and common irregular verbs offline without external dependencies
"""

class SpanishConjugator:
    """Lightweight Spanish verb conjugation engine."""
    
    def __init__(self):
        # Regular verb endings
        self.regular_endings = {
            'present': {
                'ar': ['o', 'as', 'a', 'amos', 'áis', 'an'],
                'er': ['o', 'es', 'e', 'emos', 'éis', 'en'],
                'ir': ['o', 'es', 'e', 'imos', 'ís', 'en']
            },
            'preterite': {
                'ar': ['é', 'aste', 'ó', 'amos', 'asteis', 'aron'],
                'er': ['í', 'iste', 'ió', 'imos', 'isteis', 'ieron'],
                'ir': ['í', 'iste', 'ió', 'imos', 'isteis', 'ieron']
            },
            'imperfect': {
                'ar': ['aba', 'abas', 'aba', 'ábamos', 'abais', 'aban'],
                'er': ['ía', 'ías', 'ía', 'íamos', 'íais', 'ían'],
                'ir': ['ía', 'ías', 'ía', 'íamos', 'íais', 'ían']
            },
            'future': {
                'ar': ['é', 'ás', 'á', 'emos', 'éis', 'án'],
                'er': ['é', 'ás', 'á', 'emos', 'éis', 'án'],
                'ir': ['é', 'ás', 'á', 'emos', 'éis', 'án']
            },
            'conditional': {
                'ar': ['ía', 'ías', 'ía', 'íamos', 'íais', 'ían'],
                'er': ['ía', 'ías', 'ía', 'íamos', 'íais', 'ían'],
                'ir': ['ía', 'ías', 'ía', 'íamos', 'íais', 'ían']
            },
            'present_subjunctive': {
                'ar': ['e', 'es', 'e', 'emos', 'éis', 'en'],
                'er': ['a', 'as', 'a', 'amos', 'áis', 'an'],
                'ir': ['a', 'as', 'a', 'amos', 'áis', 'an']
            }
        }
        
        # Common irregular verbs (present tense only for simplicity)
        self.irregular_verbs = {
            'ser': {
                'present': ['soy', 'eres', 'es', 'somos', 'sois', 'son'],
                'preterite': ['fui', 'fuiste', 'fue', 'fuimos', 'fuisteis', 'fueron'],
                'imperfect': ['era', 'eras', 'era', 'éramos', 'erais', 'eran']
            },
            'estar': {
                'present': ['estoy', 'estás', 'está', 'estamos', 'estáis', 'están'],
                'preterite': ['estuve', 'estuviste', 'estuvo', 'estuvimos', 'estuvisteis', 'estuvieron']
            },
            'tener': {
                'present': ['tengo', 'tienes', 'tiene', 'tenemos', 'tenéis', 'tienen'],
                'preterite': ['tuve', 'tuviste', 'tuvo', 'tuvimos', 'tuvisteis', 'tuvieron']
            },
            'hacer': {
                'present': ['hago', 'haces', 'hace', 'hacemos', 'hacéis', 'hacen'],
                'preterite': ['hice', 'hiciste', 'hizo', 'hicimos', 'hicisteis', 'hicieron']
            },
            'ir': {
                'present': ['voy', 'vas', 'va', 'vamos', 'vais', 'van'],
                'preterite': ['fui', 'fuiste', 'fue', 'fuimos', 'fuisteis', 'fueron'],
                'imperfect': ['iba', 'ibas', 'iba', 'íbamos', 'ibais', 'iban']
            },
            'poder': {
                'present': ['puedo', 'puedes', 'puede', 'podemos', 'podéis', 'pueden'],
                'preterite': ['pude', 'pudiste', 'pudo', 'pudimos', 'pudisteis', 'pudieron']
            },
            'saber': {
                'present': ['sé', 'sabes', 'sabe', 'sabemos', 'sabéis', 'saben'],
                'preterite': ['supe', 'supiste', 'supo', 'supimos', 'supisteis', 'supieron']
            },
            'dar': {
                'present': ['doy', 'das', 'da', 'damos', 'dais', 'dan'],
                'preterite': ['di', 'diste', 'dio', 'dimos', 'disteis', 'dieron']
            },
            'ver': {
                'present': ['veo', 'ves', 've', 'vemos', 'veis', 'ven'],
                'preterite': ['vi', 'viste', 'vio', 'vimos', 'visteis', 'vieron'],
                'imperfect': ['veía', 'veías', 'veía', 'veíamos', 'veíais', 'veían']
            },
            'decir': {
                'present': ['digo', 'dices', 'dice', 'decimos', 'decís', 'dicen'],
                'preterite': ['dije', 'dijiste', 'dijo', 'dijimos', 'dijisteis', 'dijeron']
            }
        }
        
        # Stem-changing verbs (e->ie, o->ue, e->i)
        self.stem_changes = {
            'pensar': {'type': 'e->ie', 'present': ['pienso', 'piensas', 'piensa', 'pensamos', 'pensáis', 'piensan']},
            'querer': {'type': 'e->ie', 'present': ['quiero', 'quieres', 'quiere', 'queremos', 'queréis', 'quieren']},
            'dormir': {'type': 'o->ue', 'present': ['duermo', 'duermes', 'duerme', 'dormimos', 'dormís', 'duermen']},
            'volver': {'type': 'o->ue', 'present': ['vuelvo', 'vuelves', 'vuelve', 'volvemos', 'volvéis', 'vuelven']},
            'pedir': {'type': 'e->i', 'present': ['pido', 'pides', 'pide', 'pedimos', 'pedís', 'piden']}
        }
    
    def conjugate(self, infinitive, tense, person):
        """
        Conjugate a Spanish verb.
        
        Args:
            infinitive: The infinitive form (e.g., 'hablar')
            tense: The tense ('present', 'preterite', 'imperfect', 'future', 'conditional', 'present_subjunctive')
            person: The person number (0-5 for yo, tú, él/ella, nosotros, vosotros, ellos)
        
        Returns:
            Conjugated form or None if unable to conjugate
        """
        # Check irregular verbs first
        if infinitive in self.irregular_verbs:
            if tense in self.irregular_verbs[infinitive]:
                return self.irregular_verbs[infinitive][tense][person]
        
        # Check stem-changing verbs
        if infinitive in self.stem_changes and tense == 'present':
            return self.stem_changes[infinitive]['present'][person]
        
        # Handle regular verbs
        if len(infinitive) < 3:
            return None
            
        ending = infinitive[-2:]
        if ending not in ['ar', 'er', 'ir']:
            return None
            
        stem = infinitive[:-2]
        
        # Future and conditional use full infinitive
        if tense in ['future', 'conditional']:
            stem = infinitive
            ending = 'ar'  # All verbs use same endings
        
        if tense in self.regular_endings and ending in self.regular_endings[tense]:
            return stem + self.regular_endings[tense][ending][person]
        
        return None
    
    def get_all_conjugations(self, infinitive, tense):
        """Get all 6 conjugations for a verb in a given tense."""
        forms = []
        for person in range(6):
            form = self.conjugate(infinitive, tense, person)
            if form:
                forms.append(form)
        return forms if len(forms) == 6 else None

# Common verbs for practice
COMMON_VERBS = {
    'regular': {
        'ar': ['hablar', 'trabajar', 'estudiar', 'caminar', 'bailar', 'cantar', 'comprar', 'escuchar', 'mirar', 'nadar'],
        'er': ['comer', 'beber', 'leer', 'correr', 'aprender', 'vender', 'comprender', 'creer', 'responder'],
        'ir': ['vivir', 'escribir', 'abrir', 'recibir', 'subir', 'decidir', 'permitir', 'discutir', 'compartir']
    },
    'irregular': ['ser', 'estar', 'tener', 'hacer', 'ir', 'poder', 'saber', 'dar', 'ver', 'decir'],
    'stem_changing': ['pensar', 'querer', 'dormir', 'volver', 'pedir']
}

# Person labels for reference
PERSON_LABELS = ['yo', 'tú', 'él/ella/usted', 'nosotros/nosotras', 'vosotros/vosotras', 'ellos/ellas/ustedes']

# Tense translations
TENSE_NAMES = {
    'present': 'Present',
    'preterite': 'Preterite',
    'imperfect': 'Imperfect',
    'future': 'Future',
    'conditional': 'Conditional',
    'present_subjunctive': 'Present Subjunctive'
}