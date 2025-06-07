import tkinter as tk
from tkinter import ttk
import random
import time
import csv
import os
from datetime import datetime

# --- REQUIRED IMPORTS ---
# This script requires: Pillow, pandas, matplotlib, numpy
# You can install them with:
# pip install Pillow pandas matplotlib numpy
from PIL import Image, ImageDraw, ImageFont, ImageTk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- CONFIGURATION AND CONSTANTS ---
CONFIG = {
    "task_durations": {
        "Reasoning": 60,
        "Perceptual Speed": 60,
        "Number Speed & Accuracy": 60,
        "Word Meaning": 60,
        "Spatial Visualisation": 60,
    },
    "files": {
        "results_log": 'gia_practice_log.csv',
        "summary_log": 'gia_summary_log.csv',
    },
    "colors": {
        "background": "#f0f0f0",
        "plot_background": "#f0f0f0",
        "past_performance": "skyblue",
        "current_performance": "red",
    },
    "fonts": {
        "button": ('Helvetica', 16),
        "title": ('Helvetica', 24, 'bold'),
        "header": ('Helvetica', 14),
        "small": ('Helvetica', 10),
        "italic": ('Helvetica', 10, 'italic'),
        "timer": ('Helvetica', 12),
        "mono_large": ('Courier', 36, 'bold'),
        "spatial_font": "arial.ttf",
    },
}


# --- QUESTION GENERATORS ---
class QuestionFactory:
    """Generates questions for the different GIA task types."""

    def __init__(self):
        self._names = [
            'Alex', 'Ben', 'Chloe', 'David', 'Eva', 'Frank',
            'Grace', 'Harry', 'Isla', 'Jack', 'Mia', 'Noah'
        ]
        self._adjective_pairs = [
            ('heavier', 'lighter'), ('stronger', 'weaker'), ('faster', 'slower'),
            ('taller', 'shorter'), ('brighter', 'duller'), ('happier', 'sadder'),
            ('older', 'younger'), ('richer', 'poorer'), ('simpler', 'more complex'),
            ('calmer', 'more anxious'), ('rarer', 'more common'), ('warmer', 'colder'),
            ('wiser', 'more foolish'), ('braver', 'more timid'), ('louder', 'quieter'),
            ('sharper', 'blunter'), ('smoother', 'rougher'), ('neater', 'messier'),
            ('cheaper', 'more expensive'), ('darker', 'lighter'), ('earlier', 'later')
        ]
        self._comparative_to_base = {
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
            'more expensive': 'expensive', 'darker': 'dark', 'earlier': 'early', 'later': 'late'
        }
        self._word_groups = [
            # Synonyms
            ('halt', 'stop', 'cold'), ('fast', 'quick', 'chair'), ('happy', 'joyful', 'river'),
            ('large', 'big', 'car'), ('sofa', 'couch', 'apple'), ('begin', 'start', 'end'),
            ('silent', 'quiet', 'loud'), ('difficult', 'hard', 'easy'), ('correct', 'right', 'wrong'),
            ('rich', 'wealthy', 'poor'), ('unhappy', 'sad', 'glad'), ('beautiful', 'pretty', 'ugly'),
            ('smart', 'intelligent', 'stupid'), ('speak', 'talk', 'listen'),
            ('finish', 'complete', 'begin'), ('idea', 'thought', 'action'),
            ('strange', 'unusual', 'normal'), ('powerful', 'strong', 'weak'),
            ('annual', 'yearly', 'daily'), ('choose', 'select', 'reject'),
            ('ancient', 'old', 'new'),
            # Antonyms
            ('up', 'down', 'table'), ('hot', 'cold', 'window'), ('begin', 'end', 'apple'),
            ('good', 'bad', 'river'), ('always', 'never', 'banana'), ('accept', 'reject', 'carpet'),
            ('above', 'below', 'pencil'), ('victory', 'defeat', 'bottle'),
            ('success', 'failure', 'candle'), ('love', 'hate', 'truck'),
            ('buy', 'sell', 'mountain'), ('push', 'pull', 'window'), ('light', 'dark', 'cookie'),
            ('laugh', 'cry', 'forest'), ('remember', 'forget', 'guitar'),
            ('friend', 'enemy', 'cloud'), ('question', 'answer', 'bridge'),
            ('sunrise', 'sunset', 'elephant')
        ]

    def generate_reasoning(self):
        p1, p2 = random.sample(self._names, 2)
        adj1, adj2 = random.choice(self._adjective_pairs)

        if random.random() > 0.5:
            statement = f"{p1} is {adj1} than {p2}."
            answers = {adj1: p1, adj2: p2}
        else:
            base = self._comparative_to_base.get(adj1, adj1)
            statement = f"{p1} is not as {base} as {p2}."
            answers = {adj1: p2, adj2: p1}

        question_adj = random.choice([adj1, adj2])
        return {
            "type": "Reasoning",
            "statement": statement,
            "question": f"Who is {question_adj}?",
            "options": [p1, p2],
            "answer": answers[question_adj]
        }

    def generate_perceptual_speed(self):
        alphabet = 'abcdefghjkmnpqrstuvwxyz'
        pairs, match_count = [], 0
        top_upper = random.choice([True, False])
        top_fn, bot_fn = (str.upper, str.lower) if top_upper else (str.lower, str.upper)

        for _ in range(4):
            if random.random() < 0.6:  # 60% chance of a match
                char = random.choice(alphabet)
                pairs.append((top_fn(char), bot_fn(char)))
                match_count += 1
            else:
                a, b = random.sample(alphabet, 2)
                pairs.append((top_fn(a), bot_fn(b)))

        return {
            "type": "Perceptual Speed",
            "pairs": pairs,
            "options": list(range(5)),
            "answer": match_count
        }

    def generate_number_speed(self):
        mid = random.randint(10, 50)
        d1, d2 = random.randint(2, 15), random.randint(2, 15)
        while d1 == d2:
            d2 = random.randint(2, 15)

        low, high = mid - d1, mid + d2
        answer = high if d2 > d1 else low
        nums = [low, mid, high]
        random.shuffle(nums)
        return {
            "type": "Number Speed & Accuracy",
            "options": nums,
            "answer": answer
        }

    def generate_word_meaning(self):
        group = random.choice(self._word_groups)
        options = list(group)
        random.shuffle(options)
        return {
            "type": "Word Meaning",
            "options": options,
            "answer": group[2] # The odd one out is always the 3rd item
        }

    def generate_spatial_visualisation(self):
        base_letters = ['R', 'F', 'P']
        rotations = [0, 90, 180, 270]
        pairs, match_count = [], 0

        for _ in range(3):
            letter = random.choice(base_letters)
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
                'letter': letter,
                'top_is_mirror': top_is_mirrored,
                'top_rot': top_rotation,
                'bottom_is_mirror': bottom_is_mirrored,
                'bottom_rot': bottom_rotation
            })

        return {
            "type": "Spatial Visualisation",
            "pairs": pairs,
            "options": [0, 1, 2, 3],
            "answer": match_count
        }


# --- DATA HANDLING ---
class DataManager:
    """Handles reading from and writing to CSV log files."""

    def __init__(self, results_log, summary_log):
        self.results_log = results_log
        self.summary_log = summary_log
        self._setup_logging()

    def _setup_logging(self):
        if not os.path.exists(self.results_log):
            with open(self.results_log, 'w', newline='') as f:
                csv.writer(f).writerow(['timestamp', 'task_name', 'is_correct', 'time_taken_ms'])
        
        if not os.path.exists(self.summary_log):
            with open(self.summary_log, 'w', newline='') as f:
                csv.writer(f).writerow(['timestamp', 'task_name', 'total_questions',
                                        'correct_questions', 'accuracy', 'seconds_per_question'])
    
    def log_question_result(self, task_name, is_correct, time_taken_ms):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.results_log, 'a', newline='') as f:
            csv.writer(f).writerow([timestamp, task_name, int(is_correct), f"{time_taken_ms:.2f}"])

    def log_summary_stats(self, task_name, total, correct, duration):
        if total == 0:
            return None
            
        accuracy = (correct / total) * 100
        seconds_per_question = duration / total
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(self.summary_log, 'a', newline='') as f:
            csv.writer(f).writerow([timestamp, task_name, total, correct,
                                    f"{accuracy:.2f}", f"{seconds_per_question:.3f}"])
        
        return {'accuracy': accuracy, 'spq': seconds_per_question}

    def load_summary_data(self):
        if not os.path.exists(self.summary_log):
            return pd.DataFrame()
        try:
            df = pd.read_csv(self.summary_log)
            if df.empty:
                return pd.DataFrame()
            
            # Convert relevant columns to numeric, coercing errors
            df['accuracy'] = pd.to_numeric(df['accuracy'], errors='coerce')
            df['seconds_per_question'] = pd.to_numeric(df['seconds_per_question'], errors='coerce')
            df.dropna(subset=['accuracy', 'seconds_per_question'], inplace=True)
            return df
        except Exception as e:
            print(f"Error loading summary data: {e}")
            return pd.DataFrame()


# --- GUI APPLICATION ---
class GiaApp(tk.Tk):
    """The main application window and logic for the GIA Practice Tool."""

    def __init__(self):
        super().__init__()

        # --- State Management ---
        self.factory = QuestionFactory()
        self.data_manager = DataManager(
            CONFIG["files"]["results_log"],
            CONFIG["files"]["summary_log"]
        )
        self.current_task_name = None
        self.current_question = None
        self.question_start_time = 0
        self.current_task_results = []
        self.series_results = []
        self.task_order = []
        self.current_task_index = -1
        self.time_left = 0

        # --- Timers and UI Elements ---
        self._task_timer_id = None
        self._update_timer_id = None
        self.timer_label = None
        self.task_frame = None
        self.spatial_images = [] # Keep a reference to avoid garbage collection

        self._configure_styles()
        self._configure_window()
        
        self.create_welcome_screen()
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _configure_window(self):
        """Sets up the main window properties."""
        self.title("GIA Practice Tool")
        self.geometry("900x700")
        self.configure(bg=CONFIG["colors"]["background"])

    def _configure_styles(self):
        """Configures ttk styles for the application."""
        style = ttk.Style(self)
        style.theme_use('clam')
        bg_color = CONFIG["colors"]["background"]
        
        style.configure('TButton', font=CONFIG["fonts"]["button"], padding=(8, 4))
        style.configure('Title.TLabel', font=CONFIG["fonts"]["title"], background=bg_color)
        style.configure('Header.TLabel', font=CONFIG["fonts"]["header"], background=bg_color)
        style.configure('Small.TLabel', font=CONFIG["fonts"]["small"], background=bg_color)
        style.configure('Italic.TLabel', font=CONFIG["fonts"]["italic"], background=bg_color)
        style.configure('Timer.TLabel', font=CONFIG["fonts"]["timer"], background=bg_color)
        style.configure('MonoLarge.TLabel', font=CONFIG["fonts"]["mono_large"], background=bg_color)

    # --- Screen/Frame Management ---
    
    def _clear_frame(self, frame=None):
        """Destroys all widgets in the given frame or the main window."""
        target_frame = frame if frame else self
        for widget in target_frame.winfo_children():
            widget.destroy()

    def create_welcome_screen(self):
        """Displays the initial welcome screen with past performance."""
        self._clear_frame()
        
        ttk.Label(self, text="GIA Practice Tool", style='Title.TLabel').pack(pady=(50, 20))
        ttk.Label(self, text="Click below to start a new practice series.", style='Header.TLabel').pack(pady=10)
        ttk.Button(self, text="Start Test Series", command=self.start_series).pack(pady=40, ipady=10)
        
        # Display past performance
        summary_df = self.data_manager.load_summary_data()
        if not summary_df.empty:
            # *** BUG FIX: Explicitly select numeric columns for the mean calculation ***
            avg_performance = summary_df.groupby('task_name')[['accuracy', 'seconds_per_question']].mean().reset_index()
            
            ttk.Label(self, text="Average Past Performance:", style='Header.TLabel').pack(pady=(20, 5))
            for _, row in avg_performance.iterrows():
                text = (f"{row['task_name']}: Avg Accuracy {row['accuracy']:.1f}%, "
                        f"Avg Time/Q {row['seconds_per_question']:.3f} s/Q")
                ttk.Label(self, text=text, style='Small.TLabel').pack()
        else:
            ttk.Label(self, text="No past summary data available yet.", style='Small.TLabel').pack(pady=20)
            
        log_files_text = (f"Performance logs are stored in:\n"
                          f"{CONFIG['files']['results_log']}\n{CONFIG['files']['summary_log']}")
        ttk.Label(self, text=log_files_text, style='Italic.TLabel').pack(side='bottom', pady=10)

    def _show_task_intro(self):
        """Displays an introduction screen before each task begins."""
        self._clear_frame()
        duration = CONFIG["task_durations"][self.current_task_name]
        
        ttk.Label(self, text=f"Task {self.current_task_index + 1}: {self.current_task_name}", style='Title.TLabel').pack(pady=(50, 20))
        ttk.Label(self, text=f"You will have {duration} seconds for this task.", style='Header.TLabel').pack(pady=10)
        ttk.Label(self, text="Answer as many questions as you can. Work quickly and accurately.", style='Header.TLabel').pack(pady=10)
        ttk.Button(self, text="Start Task", command=self.start_current_task).pack(pady=40, ipady=10)

    def _show_task_summary_screen(self, task_name, stats):
        """Displays a summary plot after a task is completed."""
        self._clear_frame()
        ttk.Label(self, text=f"Results for: {task_name}", style='Title.TLabel').pack(pady=20)
        
        # Load all historical data for this task
        summary_df = self.data_manager.load_summary_data()
        history_df = summary_df[summary_df['task_name'] == task_name]

        # Create plot
        fig, ax = plt.subplots(figsize=(6, 6))
        fig.patch.set_facecolor(CONFIG["colors"]["plot_background"])
        ax.set_facecolor(CONFIG["colors"]["plot_background"])

        if not history_df.empty:
            ax.scatter(history_df['accuracy'], history_df['seconds_per_question'],
                       alpha=0.6, s=50, label='Past Attempts', color=CONFIG["colors"]["past_performance"])

        ax.scatter(stats['accuracy'], stats['spq'], color=CONFIG["colors"]["current_performance"],
                   edgecolors='black', s=120, marker='*', label='This Attempt')
        
        ax.set_title('Accuracy vs. Time per Question')
        ax.set_xlabel('Accuracy (%)')
        ax.set_ylabel('Seconds per Question (s/Q)')
        ax.legend()
        ax.grid(True, alpha=0.4)
        fig.tight_layout(pad=3.0)
        
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.get_tk_widget().pack(side='top', fill='both', expand=True)
        
        ttk.Button(self, text="Continue", command=self.next_task).pack(pady=20, ipady=10)

    def _show_final_results(self):
        """Displays a summary of the entire test series."""
        self._clear_frame()
        ttk.Label(self, text="Test Series Complete!", style='Title.TLabel').pack(pady=(40, 20))
        
        summary_text = "Overall Summary:\n\n"
        for task_name in self.task_order:
            results = [r for r in self.series_results if r['task'] == task_name]
            if not results:
                summary_text += f"{task_name}: No questions answered.\n\n"
                continue

            total = len(results)
            correct = sum(1 for r in results if r['correct'])
            accuracy = (correct / total) * 100
            spq = CONFIG["task_durations"][task_name] / total
            
            summary_text += (f"{task_name}:\n"
                             f"  - Answered: {total}\n"
                             f"  - Accuracy: {accuracy:.1f}%\n"
                             f"  - Time/Q: {spq:.3f} s/Q\n\n")
            
        ttk.Label(self, text=summary_text, style='Small.TLabel', justify='left').pack(pady=20, padx=50)
        ttk.Button(self, text="Practice Again", command=self.create_welcome_screen).pack(pady=20, ipady=10)

    # --- Task Flow ---

    def start_series(self):
        """Initializes a new test series."""
        self.task_order = list(CONFIG["task_durations"].keys())
        self.current_task_index = -1
        self.series_results = []
        self.next_task()

    def next_task(self):
        """Moves to the next task in the series or shows final results."""
        self.current_task_index += 1
        if self.current_task_index < len(self.task_order):
            self.current_task_name = self.task_order[self.current_task_index]
            self._show_task_intro()
        else:
            self._show_final_results()

    def start_current_task(self):
        """Starts the timer and shows the first question for the current task."""
        self._clear_frame()
        self.task_frame = tk.Frame(self, bg=CONFIG["colors"]["background"])
        self.task_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        self.current_task_results = []
        self.time_left = CONFIG["task_durations"][self.current_task_name]
        
        self.timer_label = ttk.Label(self, text=f"Time left: {self.time_left}", style='Timer.TLabel')
        self.timer_label.pack(side='bottom', pady=10)
        
        self._update_timer()
        self._task_timer_id = self.after(self.time_left * 1000, self.end_task)
        
        self.show_next_question()

    def end_task(self):
        """Ends the current task, cancels timers, and shows the summary."""
        self._cancel_timers()
        
        total = len(self.current_task_results)
        if total > 0:
            correct = sum(r['correct'] for r in self.current_task_results)
            duration = CONFIG["task_durations"][self.current_task_name]
            stats = self.data_manager.log_summary_stats(self.current_task_name, total, correct, duration)
            self._show_task_summary_screen(self.current_task_name, stats)
        else:
            # If no questions were answered, just move to the next task
            self.next_task()

    def show_next_question(self):
        """Generates and displays the next question for the current task."""
        self._clear_frame(self.task_frame)
        
        generator_map = {
            'Reasoning': self.factory.generate_reasoning,
            'Perceptual Speed': self.factory.generate_perceptual_speed,
            'Number Speed & Accuracy': self.factory.generate_number_speed,
            'Word Meaning': self.factory.generate_word_meaning,
            'Spatial Visualisation': self.factory.generate_spatial_visualisation
        }
        
        self.current_question = generator_map[self.current_task_name]()
        self._display_question_ui(self.current_question)
        self.question_start_time = time.time()

    def _check_answer(self, selected_answer):
        """Checks the user's answer, logs it, and shows the next question."""
        time_taken_ms = (time.time() - self.question_start_time) * 1000
        is_correct = (selected_answer == self.current_question['answer'])
        
        self.data_manager.log_question_result(self.current_task_name, is_correct, time_taken_ms)
        self.current_task_results.append({'correct': is_correct})
        self.series_results.append({
            'task': self.current_task_name,
            'correct': is_correct,
            'time': time_taken_ms
        })
        
        self.show_next_question()

    # --- UI Display Methods ---

    def _display_question_ui(self, question):
        """Routes to the correct UI display method based on question type."""
        q_type = question['type']
        if q_type == 'Reasoning':
            self._display_reasoning_step1(question)
        elif q_type == 'Perceptual Speed':
            self._display_perceptual_speed(question)
        elif q_type in ['Number Speed & Accuracy', 'Word Meaning']:
            self._display_number_or_word(question)
        elif q_type == 'Spatial Visualisation':
            self._display_spatial(question)

    def _display_reasoning_step1(self, question):
        ttk.Label(self.task_frame, text=question['statement'], style='Header.TLabel', wraplength=700).pack(pady=(100, 20))
        ttk.Button(self.task_frame, text="Click when ready to continue", command=self._display_reasoning_step2).pack(pady=20, ipady=10)

    def _display_reasoning_step2(self):
        self._clear_frame(self.task_frame)
        question = self.current_question
        
        ttk.Label(self.task_frame, text=question['question'], style='Header.TLabel').pack(pady=(100, 20))
        
        options_frame = tk.Frame(self.task_frame, bg=CONFIG["colors"]["background"])
        options_frame.pack(pady=20)
        
        for option in question['options']:
            btn = ttk.Button(options_frame, text=str(option), width=10, command=lambda o=option: self._check_answer(o))
            btn.pack(side='left', padx=10, ipady=10)

    def _display_perceptual_speed(self, question):
        container_frame = tk.Frame(self.task_frame, bg=CONFIG["colors"]["background"])
        container_frame.pack(pady=(50, 10))
        
        top_row_chars = [p[0] for p in question['pairs']]
        bottom_row_chars = [p[1] for p in question['pairs']]
        
        top_frame = tk.Frame(container_frame, bg=CONFIG["colors"]["background"])
        top_frame.pack()
        for char in top_row_chars:
            ttk.Label(top_frame, text=char, style='MonoLarge.TLabel').pack(side='left')
            
        bottom_frame = tk.Frame(container_frame, bg=CONFIG["colors"]["background"])
        bottom_frame.pack()
        for char in bottom_row_chars:
            ttk.Label(bottom_frame, text=char, style='MonoLarge.TLabel').pack(side='left')

        ttk.Label(self.task_frame, text="How many pairs are the same letter?", style='Header.TLabel').pack(pady=20)
        
        options_frame = tk.Frame(self.task_frame, bg=CONFIG["colors"]["background"])
        options_frame.pack(pady=20)
        for option in question['options']:
            btn = ttk.Button(options_frame, text=str(option), width=5, command=lambda o=option: self._check_answer(o))
            btn.pack(side='left', padx=5, ipady=10)

    def _display_number_or_word(self, question):
        # Use tk.Frame and tk.Button here to support wraplength
        options_frame = tk.Frame(self.task_frame, bg=CONFIG["colors"]["background"])
        options_frame.pack(pady=(100, 20))
        
        max_len = max(len(str(o)) for o in question['options'])
        btn_width = max(10, min(max_len + 2, 20))
        
        # Calculate wrap length based on approximate character width. 
        # You might need to adjust the multiplier (e.g., 8 or 10) depending on the font.
        wrap_length = btn_width * 8 
        
        for option in question['options']:
            # *** FIX: Use tk.Button which supports wraplength, not ttk.Button ***
            btn = tk.Button(options_frame, text=str(option), width=btn_width, wraplength=wrap_length,
                            justify='center', font=CONFIG["fonts"]["button"],
                            command=lambda o=option: self._check_answer(o))
            btn.pack(side='left', padx=10, ipady=4, pady=4)

    def _display_spatial(self, question):
        self.spatial_images = []  # Clear previous images
        
        container_frame = tk.Frame(self.task_frame, bg=CONFIG["colors"]["background"])
        container_frame.pack(pady=(30, 10))
        
        def make_image(char, is_mirrored, angle, size=80):
            try:
                font = ImageFont.truetype(CONFIG["fonts"]["spatial_font"], size)
            except IOError:
                font = ImageFont.load_default()

            img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            draw.text((size / 2, size / 2), char, font=font, fill="black", anchor="mm")
            
            if is_mirrored:
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
            
            rotated_img = img.rotate(angle, expand=True, resample=Image.BICUBIC)
            return ImageTk.PhotoImage(rotated_img)

        for i, pair_data in enumerate(question['pairs']):
            canvas = tk.Canvas(container_frame, width=100, height=220, bg="white", highlightthickness=1)
            canvas.grid(row=0, column=i, padx=10)
            
            top_img = make_image(pair_data['letter'], pair_data['top_is_mirror'], pair_data['top_rot'])
            self.spatial_images.append(top_img)
            canvas.create_image(50, 60, image=top_img)
            
            bottom_img = make_image(pair_data['letter'], pair_data['bottom_is_mirror'], pair_data['bottom_rot'])
            self.spatial_images.append(bottom_img)
            canvas.create_image(50, 160, image=bottom_img)

        ttk.Label(self.task_frame, text="How many pairs can be rotated to match exactly?", style='Header.TLabel').pack(pady=20)
        
        options_frame = tk.Frame(self.task_frame, bg=CONFIG["colors"]["background"])
        options_frame.pack(pady=20)
        for option in question['options']:
            btn = ttk.Button(options_frame, text=str(option), width=5, command=lambda o=option: self._check_answer(o))
            btn.pack(side='left', padx=5, ipady=10)

    # --- Timers and Closing ---
    
    def _update_timer(self):
        """Decrements the timer label every second."""
        if self.time_left > 0:
            self.timer_label.config(text=f"Time left: {self.time_left}")
            self.time_left -= 1
            self._update_timer_id = self.after(1000, self._update_timer)
    
    def _cancel_timers(self):
        """Safely cancels all active after() timers."""
        if self._task_timer_id:
            self.after_cancel(self._task_timer_id)
            self._task_timer_id = None
        if self._update_timer_id:
            self.after_cancel(self._update_timer_id)
            self._update_timer_id = None

    def _on_closing(self):
        """Handles window closing event to ensure timers are stopped."""
        self._cancel_timers()
        self.quit()
        self.destroy()


if __name__ == "__main__":
    app = GiaApp()
    app.mainloop()