import random

class QuestionFactory:
    """Generates questions for the different GIA task types."""

    def __init__(self):
        self._names = [
            'Alex', 'Anna', 'Ben', 'Chloe', 'David', 'Emily', 'Ethan', 'Eva', 
            'Frank', 'Grace', 'Harry', 'Henry', 'Isla', 'Jack', 'James', 'Leo', 
            'Liam', 'Lily', 'Lucy', 'Max', 'Maya', 'Mia', 'Noah', 'Nora', 
            'Oliver', 'Olivia', 'Ruby', 'Sam', 'Sophia', 'Tom', 'Zoe'
        ]

        self._adjective_pairs = [
            # Original Pairs
            ('heavier', 'lighter'), ('stronger', 'weaker'), ('faster', 'slower'),
            ('taller', 'shorter'), ('brighter', 'duller'), ('happier', 'sadder'),
            ('older', 'younger'), ('richer', 'poorer'), ('simpler', 'more complex'),
            ('calmer', 'more anxious'), ('rarer', 'more common'), ('warmer', 'colder'),
            ('wiser', 'more foolish'), ('braver', 'more timid'), ('louder', 'quieter'),
            ('sharper', 'blunter'), ('smoother', 'rougher'), ('neater', 'messier'),
            ('cheaper', 'more expensive'), ('darker', 'lighter'), ('earlier', 'later'),
            
            # New Pairs
            ('wider', 'narrower'), ('deeper', 'shallower'), ('thicker', 'thinner'),
            ('kinder', 'meaner'), ('busier', 'freer'), ('luckier', 'unluckier'),
            ('more patient', 'less patient'), ('more careful', 'more careless'),
            ('more generous', 'stingier'), ('more skilled', 'less skilled'),
            ('more polite', 'ruder'), ('more flexible', 'stiffer'),
            ('more honest', 'more dishonest'), ('more talkative', 'more reserved'),
            ('more optimistic', 'more pessimistic')
        ]
        
        self._comparative_to_base = {
            # Original Mappings
            'heavier': 'heavy', 'lighter': 'light', 'stronger': 'strong', 'weaker': 'weak',
            'faster': 'fast', 'slower': 'slow', 'taller': 'tall', 'shorter': 'short',
            'brighter': 'bright', 'duller': 'dull', 'happier': 'happy', 'sadder': 'sad',
            'older': 'old', 'younger': 'young', 'richer': 'rich', 'poorer': 'poor',
            'simpler': 'simple', 'more complex': 'complex', 'calmer': 'calm',
            'more anxious': 'anxious', 'rarer': 'rare', 'more common': 'common',
            'warmer': 'warm', 'colder': 'cold', 'wiser': 'wise', 'more foolish': 'foolish',
            'braver': 'brave', 'more timid': 'timid', 'louder': 'loud', 'quieter': 'quiet',
            'sharper': 'sharp', 'blunter': 'blunt', 'smoother': 'smooth', 'rougher': 'rough',
            'neater': 'neat', 'messier': 'messy', 'cheaper': 'cheap',
            'more expensive': 'expensive', 'darker': 'dark', 'earlier': 'early', 'later': 'late',
            
            # New Mappings (must correspond to the new pairs above)
            'wider': 'wide', 'narrower': 'narrow',
            'deeper': 'deep', 'shallower': 'shallow',
            'thicker': 'thick', 'thinner': 'thin',
            'kinder': 'kind', 'meaner': 'mean',
            'busier': 'busy', 'freer': 'free',
            'luckier': 'lucky', 'unluckier': 'unlucky',
            'more patient': 'patient', 'less patient': 'patient',
            'more careful': 'careful', 'more careless': 'careless',
            'more generous': 'generous', 'stingier': 'stingy',
            'more skilled': 'skilled', 'less skilled': 'skilled',
            'more polite': 'polite', 'ruder': 'rude',
            'more flexible': 'flexible', 'stiffer': 'stiff',
            'more honest': 'honest', 'more dishonest': 'dishonest',
            'more talkative': 'talkative', 'more reserved': 'reserved',
            'more optimistic': 'optimistic', 'more pessimistic': 'pessimistic'
        }
        self._word_groups = [
            # --- Original Synonyms ---
            ('halt', 'stop', 'cold'), 
            ('fast', 'quick', 'chair'), 
            ('happy', 'joyful', 'river'),
            ('large', 'big', 'car'), 
            ('sofa', 'couch', 'apple'), 
            ('begin', 'start', 'end'),
            ('silent', 'quiet', 'loud'), 
            ('difficult', 'hard', 'easy'), 
            ('correct', 'right', 'wrong'),
            ('rich', 'wealthy', 'poor'), 
            ('unhappy', 'sad', 'glad'), 
            ('beautiful', 'pretty', 'ugly'),
            ('smart', 'intelligent', 'stupid'), 
            ('speak', 'talk', 'listen'),
            ('finish', 'complete', 'begin'), 
            ('idea', 'thought', 'action'),
            ('strange', 'unusual', 'normal'), 
            ('powerful', 'strong', 'weak'),
            ('annual', 'yearly', 'daily'), 
            ('choose', 'select', 'reject'),
            ('ancient', 'old', 'new'),

            # --- New Synonyms ---
            ('tiny', 'small', 'ocean'),
            ('angry', 'furious', 'book'),
            ('create', 'make', 'sky'),
            ('help', 'assist', 'tree'),
            ('job', 'work', 'cloud'),
            ('ask', 'inquire', 'shoe'),
            ('get', 'receive', 'give'),
            ('tell', 'inform', 'secret'),
            ('brave', 'courageous', 'table'),
            ('calm', 'peaceful', 'storm'),
            ('eager', 'keen', 'apathy'),
            ('true', 'correct', 'false'),
            ('story', 'tale', 'math'),
            ('error', 'mistake', 'truth'),
            ('gift', 'present', 'invoice'),
            ('ally', 'partner', 'foe'),

            # --- Tricky Synonyms ---
            ('obtain', 'acquire', 'lose'),
            ('lucid', 'clear', 'blanket'),
            ('pensive', 'thoughtful', 'hammer'),
            ('prudent', 'cautious', 'pillow'),
            ('garrulous', 'loquacious', 'fork'),
            ('adequate', 'sufficient', 'lacking'),
            ('ephemeral', 'transient', 'spoon'),
            ('taciturn', 'reserved', 'bottle'),
            ('meticulous', 'thorough', 'lamp'),
            ('ubiquitous', 'omnipresent', 'coin'),
            ('trivial', 'minor', 'major'),
            ('vital', 'essential', 'optional'),
            ('flexible', 'adaptable', 'rigid'),

            # --- Original Antonyms ---
            ('up', 'down', 'table'), 
            ('hot', 'cold', 'window'), 
            ('begin', 'end', 'apple'),
            ('good', 'bad', 'river'), 
            ('always', 'never', 'banana'), 
            ('accept', 'reject', 'carpet'),
            ('above', 'below', 'pencil'), 
            ('victory', 'defeat', 'bottle'),
            ('success', 'failure', 'candle'), 
            ('love', 'hate', 'truck'),
            ('buy', 'sell', 'mountain'), 
            ('push', 'pull', 'window'), 
            ('light', 'dark', 'cookie'),
            ('laugh', 'cry', 'forest'), 
            ('remember', 'forget', 'guitar'),
            ('friend', 'enemy', 'cloud'), 
            ('question', 'answer', 'bridge'),
            ('sunrise', 'sunset', 'elephant'),

            # --- New Antonyms ---
            ('arrive', 'depart', 'bread'),
            ('build', 'destroy', 'flower'),
            ('empty', 'full', 'paper'),
            ('wet', 'dry', 'stone'),
            ('enter', 'exit', 'music'),
            ('simple', 'complex', 'water'),
            ('lead', 'follow', 'path'),
            ('public', 'private', 'square'),
            ('find', 'lose', 'search'),
            ('wide', 'narrow', 'road'),
            ('smooth', 'rough', 'silk'),
            ('day', 'night', 'noon'),
            ('interior', 'exterior', 'wall'),
            ('major', 'minor', 'scale'),
            ('include', 'exclude', 'group'),

            # --- Tricky Antonyms ---
            ('expand', 'contract', 'phone'),
            ('permit', 'forbid', 'ring'),
            ('praise', 'criticize', 'key'),
            ('reveal', 'conceal', 'boat'),
            ('harmony', 'dissonance', 'mirror'),
            ('frugal', 'extravagant', 'ship'),
            ('optimist', 'pessimist', 'glove'),
            ('ascend', 'descend', 'train'),
            ('innocent', 'guilty', 'judge'),
            ('bravery', 'cowardice', 'medal'),
            ('chaos', 'order', 'mess'),
            ('permanent', 'temporary', 'job'),
            ('compulsory', 'voluntary', 'task')
        ]

        # Create a shuffled deck of word groups for the session.
        self._available_word_groups = self._word_groups.copy()
        random.shuffle(self._available_word_groups)

    def _reset_word_groups(self):
        """Resets and reshuffles the pool of available word meaning questions."""
        print("Word Meaning question pool exhausted. Resetting and reshuffling.")
        self._available_word_groups = self._word_groups.copy()
        random.shuffle(self._available_word_groups)

    def generate_reasoning(self):
        p1, p2 = random.sample(self._names, 2)
        adj1, adj2 = random.choice(self._adjective_pairs)
        if random.random() > 0.5:
            statement, answers = f"{p1} is {adj1} than {p2}.", {adj1: p1, adj2: p2}
        else:
            base = self._comparative_to_base.get(adj1, adj1)
            statement, answers = f"{p1} is not as {base} as {p2}.", {adj1: p2, adj2: p1}
        question_adj = random.choice([adj1, adj2])
        return {"type": "Reasoning", "statement": statement, "question": f"Who is {question_adj}?", "options": [p1, p2], "answer": answers[question_adj]}

    def generate_perceptual_speed(self):
        alphabet, pairs, match_count = 'abcdefghjkmnpqrstuvwxyz', [], 0
        top_upper = random.choice([True, False])
        top_fn, bot_fn = (str.upper, str.lower) if top_upper else (str.lower, str.upper)
        for _ in range(4):
            if random.random() < 0.6:
                char = random.choice(alphabet); pairs.append((top_fn(char), bot_fn(char))); match_count += 1
            else:
                a, b = random.sample(alphabet, 2); pairs.append((top_fn(a), bot_fn(b)))
        return {"type": "Perceptual Speed", "pairs": pairs, "options": list(range(5)), "answer": match_count}

    def generate_number_speed(self):
        mid = random.randint(10, 50); d1, d2 = random.randint(2, 15), random.randint(2, 15)
        while d1 == d2: d2 = random.randint(2, 15)
        low, high = mid - d1, mid + d2; answer = high if d2 > d1 else low
        nums = [low, mid, high]; random.shuffle(nums)
        return {"type": "Number Speed & Accuracy", "options": nums, "answer": answer}

    def generate_word_meaning(self):
        # If the deck of available questions is empty, reset it.
        if not self._available_word_groups:
            self._reset_word_groups()

        # Pop a question from the end of the shuffled list.
        group = self._available_word_groups.pop()
        
        options = list(group)
        random.shuffle(options)
        return {
            "type": "Word Meaning",
            "options": options,
            "answer": group[2] # The odd one out is always the 3rd item
        }

    def generate_spatial_visualisation(self):
        """
        Generates a spatial visualisation task with two pairs, both using the same letter.
        """
        base_letters = ['R', 'F', 'P']
        rotations = [0, 90, 180, 270]
        pairs = []
        match_count = 0
        # Choose one letter per task.
        task_letter = random.choice(base_letters)

        for _ in range(2):
            # Each pair will now use the same `task_letter`
            top_is_mirrored = random.choice([True, False])
            
            # 50% chance they are a rotatable match (both mirrored or both not)
            if random.random() < 0.5:
                bottom_is_mirrored = top_is_mirrored
                match_count += 1
            else:
                bottom_is_mirrored = not top_is_mirrored
            
            top_rotation = random.choice(rotations)
            bottom_rotation = random.choice(rotations)
            
            pairs.append({
                'letter': task_letter, # Using the single letter for the task
                'top_is_mirror': top_is_mirrored, 
                'top_rot': top_rotation, 
                'bottom_is_mirror': bottom_is_mirrored, 
                'bottom_rot': bottom_rotation
            })

        return {
            "type": "Spatial Visualisation",
            "pairs": pairs,
            "options": [0, 1, 2],
            "answer": match_count
        }