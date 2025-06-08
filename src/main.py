import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
import time
import copy
import json
from PIL import Image, ImageDraw, ImageFont, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from config import CONFIG, SELECTED_THEME
from data_manager import DataManager
from question_factory import QuestionFactory
from ui_helpers import ScrollableFrame

class GiaApp(tk.Tk):
    """The main application window with a modern, clean UI."""

    def __init__(self):
        super().__init__()
        self.theme = SELECTED_THEME

        # State Management
        self.settings = copy.deepcopy(CONFIG) # <<< Use a mutable copy for settings
        self.settings['debug_logging_enabled'] = False # Default to off
        self.factory = QuestionFactory()
        self.data_manager = DataManager(
            CONFIG["files"]["results_log"],
            CONFIG["files"]["summary_log"]
        )
        self.question_bank_size = 0
        self.questions_answered_in_task = 0
        self.is_practice_mode = False
        self.current_task_name = None
        self.current_question = None
        self.question_start_time = 0
        self.current_task_results = []
        self.series_results = []
        self.task_order = []
        self.current_task_index = -1
        self.time_left = 0
        self._task_timer_id, self._update_timer_id = None, None
        self.timer_label, self.task_frame = None, None
        self.spatial_images = []

        self.duration_entries = {}
        self.debug_log_var = tk.BooleanVar()

        self._configure_window()
        self.create_welcome_screen()
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _configure_window(self):
        self.title("GIA Practice Tool")
        self.geometry("900x750")
        self.configure(bg=self.theme["app_bg"])

    def _clear_frame(self, frame=None):
        target = frame if frame else self
        for widget in target.winfo_children():
            widget.destroy()

    # --- UI Creation Methods ---

    def create_welcome_screen(self):
        self._clear_frame()
        
        main_frame = tk.Frame(self, bg=self.theme["app_bg"])
        main_frame.pack(expand=True, pady=20)

        # Settings button
        settings_button = tk.Button(self, text="⚙️ Settings", font=CONFIG["fonts"]["small"], bg=self.theme["button_bg"], fg=self.theme["button_fg"], activebackground=self.theme["button_active_bg"], activeforeground=self.theme["button_fg"], relief='flat', command=self.create_settings_screen)
        settings_button.place(relx=1.0, rely=0.0, x=-15, y=15, anchor='ne')

        tk.Label(main_frame, text="GIA Practice Tool", font=CONFIG["fonts"]["title"], bg=self.theme["app_bg"], fg=self.theme["label_fg"]).pack(pady=(0, 20))
        tk.Label(main_frame, text="Take a full, timed test series to log your performance.", font=CONFIG["fonts"]["header"], bg=self.theme["app_bg"], fg=self.theme["label_fg"]).pack(pady=5)
        
        tk.Button(main_frame, text="Start Full Test Series", font=CONFIG["fonts"]["button"], bg=self.theme["button_bg"], fg=self.theme["button_fg"], activebackground=self.theme["button_active_bg"], activeforeground=self.theme["button_fg"], relief='flat', padx=20, pady=10, command=self.start_series).pack(pady=15)
        
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', padx=100, pady=20)

        practice_label = "Or, Practice a Single Task (results are not logged):"
        tk.Label(main_frame, text=practice_label, font=CONFIG["fonts"]["header"], bg=self.theme["app_bg"], fg=self.theme["label_fg"]).pack(pady=5)
        
        practice_frame = tk.Frame(main_frame, bg=self.theme["app_bg"])
        practice_frame.pack(pady=10)
        
        for i, task_name in enumerate(CONFIG["task_durations"].keys()):
            btn = tk.Button(practice_frame, text=task_name, font=CONFIG["fonts"]["small"], bg=self.theme["button_bg"], fg=self.theme["button_fg"], activebackground=self.theme["button_active_bg"], activeforeground=self.theme["button_fg"], relief='flat', padx=10, pady=5, command=lambda name=task_name: self.start_practice_session(name))
            btn.grid(row=i, column=0, padx=5, pady=5)

        summary_df = self.data_manager.load_summary_data()
        if not summary_df.empty:
            ### FIX: Replace the faulty tk.Frame with a proper ttk.Separator ###
            ttk.Separator(main_frame, orient='horizontal').pack(fill='x', padx=100, pady=20)
            
            avg_performance = summary_df.groupby('task_name')[['accuracy', 'seconds_per_question']].mean().reset_index()
            
            tk.Label(main_frame, text="Average Logged Performance:", font=CONFIG["fonts"]["header"], bg=self.theme["app_bg"], fg=self.theme["label_fg"]).pack(pady=(0, 5))
            for _, row in avg_performance.iterrows():
                text = (f"{row['task_name']}: Avg Accuracy {row['accuracy']:.1f}%, "
                        f"Avg Time/Q {row['seconds_per_question']:.3f} s/Q")
                tk.Label(main_frame, text=text, font=CONFIG["fonts"]["small"], bg=self.theme["app_bg"], fg=self.theme["label_fg"]).pack()

    def create_settings_screen(self):
        self._clear_frame()
        main_frame = tk.Frame(self, bg=self.theme["app_bg"])
        main_frame.pack(expand=True, pady=20)
        
        tk.Label(main_frame, text="Settings", font=CONFIG["fonts"]["title"], bg=self.theme["app_bg"], fg=self.theme["label_fg"]).pack(pady=(0, 30))

        # --- Task Duration Settings ---
        tk.Label(main_frame, text="Task Durations (seconds)", font=CONFIG["fonts"]["header"], bg=self.theme["app_bg"], fg=self.theme["label_fg"]).pack(pady=(10, 5))
        
        durations_frame = tk.Frame(main_frame, bg=self.theme["app_bg"])
        durations_frame.pack(pady=10)
        
        self.duration_entries = {} # Clear old entries
        for i, (task_name, duration) in enumerate(self.settings["task_durations"].items()):
            tk.Label(durations_frame, text=f"{task_name}:", font=CONFIG["fonts"]["small"], bg=self.theme["app_bg"], fg=self.theme["label_fg"]).grid(row=i, column=0, padx=10, pady=5, sticky='e')
            entry = tk.Entry(durations_frame, font=CONFIG["fonts"]["small"], width=5, justify='center')
            entry.insert(0, str(duration))
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.duration_entries[task_name] = entry

        # --- Debug Log Settings ---
        tk.Label(main_frame, text="Logging", font=CONFIG["fonts"]["header"], bg=self.theme["app_bg"], fg=self.theme["label_fg"]).pack(pady=(20, 5))
        
        self.debug_log_var.set(self.settings['debug_logging_enabled'])
        log_check = tk.Checkbutton(main_frame, text="Enable Detailed Debug Log (for full tests)", font=CONFIG["fonts"]["small"], bg=self.theme["app_bg"], fg=self.theme["label_fg"], variable=self.debug_log_var, selectcolor=self.theme["app_bg"])
        log_check.pack()

        # --- Action Buttons ---
        buttons_frame = tk.Frame(main_frame, bg=self.theme["app_bg"])
        buttons_frame.pack(pady=40)
        
        tk.Button(buttons_frame, text="Save and Back", font=CONFIG["fonts"]["button"], bg=self.theme["button_bg"], fg=self.theme["button_fg"], activebackground=self.theme["button_active_bg"], activeforeground=self.theme["button_fg"], relief='flat', padx=20, pady=10, command=self._save_settings).pack(side='left', padx=10)
        tk.Button(buttons_frame, text="Cancel", font=CONFIG["fonts"]["button"], bg=self.theme["button_bg"], fg=self.theme["button_fg"], activebackground=self.theme["button_active_bg"], activeforeground=self.theme["button_fg"], relief='flat', padx=20, pady=10, command=self.create_welcome_screen).pack(side='left', padx=10)

    def _save_settings(self):
        # Save task durations
        for task_name, entry_widget in self.duration_entries.items():
            try:
                # Validate that the input is a positive integer
                new_duration = int(entry_widget.get())
                if new_duration > 0:
                    self.settings["task_durations"][task_name] = new_duration
            except ValueError:
                # If input is invalid, just ignore it and keep the old value
                print(f"Invalid input for {task_name} duration. Not saved.")
        
        # Save debug log setting
        self.settings['debug_logging_enabled'] = self.debug_log_var.get()
        print("Settings saved.")
        self.create_welcome_screen()

    def _show_task_intro(self):
        self._clear_frame()
        main_frame = tk.Frame(self, bg=self.theme["app_bg"])
        main_frame.pack(expand=True)

        duration = self.settings["task_durations"][self.current_task_name]
        title_text = f"Practice: {self.current_task_name}" if self.is_practice_mode else f"Task: {self.current_task_name}"
        
        tk.Label(main_frame, text=title_text, font=CONFIG["fonts"]["title"], bg=self.theme["app_bg"], fg=self.theme["label_fg"]).pack(pady=(0, 20))
        tk.Label(main_frame, text=f"You will have {duration} seconds.", font=CONFIG["fonts"]["header"], bg=self.theme["app_bg"], fg=self.theme["label_fg"]).pack(pady=10)
        
        if self.is_practice_mode:
            note = "Note: Performance in practice mode is not saved."
            tk.Label(main_frame, text=note, font=CONFIG["fonts"]["italic"], bg=self.theme["app_bg"], fg="blue").pack(pady=20)

        tk.Button(main_frame, text="Start Task", font=CONFIG["fonts"]["button"], bg=self.theme["button_bg"], fg=self.theme["button_fg"], activebackground=self.theme["button_active_bg"], activeforeground=self.theme["button_fg"], relief='flat', padx=20, pady=10, command=self.start_current_task).pack(pady=20)

    # --- Question Display Methods ---

    def _display_question_ui(self, q):
        self.task_frame.configure(bg=self.theme["app_bg"])
        if q['type'] == 'Reasoning': self._display_reasoning_step1(q)
        elif q['type'] == 'Perceptual Speed': self._display_perceptual_speed(q)
        elif q['type'] in ['Number Speed & Accuracy', 'Word Meaning']: self._display_number_or_word(q)
        elif q['type'] == 'Spatial Visualisation': self._display_spatial(q)

    def _display_reasoning_step1(self, q):
        main_frame = tk.Frame(self.task_frame, bg=self.theme["app_bg"])
        main_frame.pack(expand=True)

        card_frame = tk.Frame(main_frame, bg=self.theme["card_bg"], padx=40, pady=20)
        card_frame.pack(pady=20)
        tk.Label(card_frame, text=q['statement'], font=CONFIG["fonts"]["header"], bg=self.theme["card_bg"], fg=self.theme["label_fg"]).pack()
        
        # Click anywhere to continue
        tk.Label(main_frame, text="Click the screen when ready to continue", font=CONFIG["fonts"]["italic"], bg=self.theme["app_bg"], fg=self.theme["label_fg"]).pack(pady=30)
        self._bind_all_for_next_step(self._display_reasoning_step2)

    def _display_reasoning_step2(self):
        self._clear_frame(self.task_frame)
        q = self.current_question
        
        main_frame = tk.Frame(self.task_frame, bg=self.theme["app_bg"])
        main_frame.pack(expand=True)
        
        ### FIX: Add the question label back in ###
        tk.Label(main_frame, text=q['question'], font=CONFIG["fonts"]["title"], bg=self.theme["app_bg"], fg=self.theme["label_fg"]).pack(pady=(0, 40))

        options_frame = tk.Frame(main_frame, bg=self.theme["app_bg"])
        options_frame.pack(pady=20)

        for option in q['options']:
            btn = tk.Button(options_frame, text=str(option), font=CONFIG["fonts"]["button"], bg=self.theme["button_bg"], fg=self.theme["button_fg"], activebackground=self.theme["button_active_bg"], activeforeground=self.theme["button_fg"], relief='flat', width=12, height=2, command=lambda o=option: self._check_answer(o))
            btn.pack(side='left', padx=15)

    def _display_perceptual_speed(self, q):
        main_frame = tk.Frame(self.task_frame, bg=self.theme["app_bg"])
        main_frame.pack(expand=True)
        
        # Character display
        char_frame = tk.Frame(main_frame, bg=self.theme["app_bg"])
        char_frame.pack(pady=20)
        top_frame = tk.Frame(char_frame, bg=self.theme["app_bg"]); top_frame.pack()
        bot_frame = tk.Frame(char_frame, bg=self.theme["app_bg"]); bot_frame.pack()
        for char_top, char_bot in zip([p[0] for p in q['pairs']], [p[1] for p in q['pairs']]):
            tk.Label(top_frame, text=char_top, font=CONFIG["fonts"]["mono_large"], bg=self.theme["app_bg"], fg=self.theme["label_fg"]).pack(side='left', padx=10)
            tk.Label(bot_frame, text=char_bot, font=CONFIG["fonts"]["mono_large"], bg=self.theme["app_bg"], fg=self.theme["label_fg"]).pack(side='left', padx=10)

        # Options display
        options_frame = tk.Frame(main_frame, bg=self.theme["app_bg"])
        options_frame.pack(pady=30)
        for option in q['options']:
            btn = tk.Button(options_frame, text=str(option), font=CONFIG["fonts"]["button"], bg=self.theme["button_bg"], fg=self.theme["button_fg"], activebackground=self.theme["button_active_bg"], activeforeground=self.theme["button_fg"], relief='flat', width=4, height=2, command=lambda o=option: self._check_answer(o))
            btn.pack(side='left', padx=10)

    def _display_number_or_word(self, q):
        main_frame = tk.Frame(self.task_frame, bg=self.theme["app_bg"])
        main_frame.pack(expand=True)
        
        options_frame = tk.Frame(main_frame, bg=self.theme["app_bg"])
        options_frame.pack(pady=20)
        
        button_font = tkFont.Font(font=CONFIG["fonts"]["button"])
        max_pixel_width = max(button_font.measure(str(o)) for o in q['options'])
        wrap_length = min(max_pixel_width + 40, 500)

        for option in q['options']:
            btn = tk.Button(options_frame, text=str(option), wraplength=wrap_length, font=CONFIG["fonts"]["button"], bg=self.theme["button_bg"], fg=self.theme["button_fg"], activebackground=self.theme["button_active_bg"], activeforeground=self.theme["button_fg"], relief='flat', padx=20, pady=10, command=lambda o=option: self._check_answer(o))
            btn.pack(side='left', padx=15)
            
    def _display_spatial(self, q):
        main_frame = tk.Frame(self.task_frame, bg=self.theme["app_bg"])
        main_frame.pack(expand=True)
        
        pairs_frame = tk.Frame(main_frame, bg=self.theme["app_bg"])
        pairs_frame.pack(pady=20)

        self.spatial_images = []
        for i, pair_data in enumerate(q['pairs']):
            card = tk.Frame(pairs_frame, bg=self.theme["card_bg"], width=120, height=260)
            card.grid(row=0, column=i, padx=15)
            card.pack_propagate(False) # Prevent card from shrinking to fit content

            top_img = self._make_spatial_image(pair_data['letter'], pair_data['top_is_mirror'], pair_data['top_rot'])
            bot_img = self._make_spatial_image(pair_data['letter'], pair_data['bottom_is_mirror'], pair_data['bottom_rot'])
            self.spatial_images.extend([top_img, bot_img])
            
            tk.Label(card, image=top_img, bg=self.theme["card_bg"]).pack(pady=(20, 10))
            tk.Label(card, image=bot_img, bg=self.theme["card_bg"]).pack(pady=(10, 20))

        options_frame = tk.Frame(main_frame, bg=self.theme["app_bg"])
        options_frame.pack(pady=30)
        # Options are 0, 1, 2 since there are only 2 pairs
        for option in range(3):
            btn = tk.Button(options_frame, text=str(option), font=CONFIG["fonts"]["button"], bg=self.theme["button_bg"], fg=self.theme["button_fg"], activebackground=self.theme["button_active_bg"], activeforeground=self.theme["button_fg"], relief='flat', width=4, height=2, command=lambda o=option: self._check_answer(o))
            btn.pack(side='left', padx=10)
    
    # --- Helper and Logic Methods ---

    def _go_back_to_menu(self):
        """Cancels the current task and returns to the welcome screen without saving."""
        self._cancel_timers()
        self.create_welcome_screen()

    def _make_spatial_image(self, char, is_mirrored, angle, size=80):
        try: font = ImageFont.truetype(CONFIG["fonts"]["spatial_font"], size)
        except IOError: font = ImageFont.load_default()
        img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        draw.text((size / 2, size / 2), char, font=font, fill=self.theme["label_fg"], anchor="mm")
        if is_mirrored: img = img.transpose(Image.FLIP_LEFT_RIGHT)
        rotated_img = img.rotate(angle, expand=True, resample=Image.BICUBIC)
        return ImageTk.PhotoImage(rotated_img)

    def _bind_all_for_next_step(self, callback):
        """Binds the next click to a callback, using self.after to avoid capturing the current event."""
        def on_click(event):
            # This function will run on the *next* user click.
            self.unbind_all("<Button-1>")
            callback()

        # Use self.after to delay the binding. This pushes the action to the end
        # of the current event loop cycle, ensuring the click that triggered this
        # screen is not immediately captured. A 10ms delay is more than enough.
        self.after(10, lambda: self.bind_all("<Button-1>", on_click))
        
    def start_current_task(self):
        self._clear_frame()
        self.task_frame = tk.Frame(self, bg=self.theme["app_bg"])
        self.task_frame.pack(expand=True, fill='both')

        self.task_is_ending = False

        # Calculate question bank size for this task ---
        duration_seconds = self.settings["task_durations"][self.current_task_name]
        duration_minutes = duration_seconds / 60.0
        qpm = self.settings["questions_per_minute"]
        
        self.question_bank_size = max(1, round(duration_minutes * qpm))
        self.questions_answered_in_task = 0

        back_button = tk.Button(
                self,
                text="< Menu",
                font=CONFIG["fonts"]["small"],
                bg=self.theme["button_bg"],
                fg=self.theme["button_fg"],
                activebackground=self.theme["button_active_bg"],
                activeforeground=self.theme["button_fg"],
                relief='flat',
                padx=10,
                pady=5,
                command=self._go_back_to_menu  # Call our new method
            )
        # Place it in the top-left corner
        back_button.place(relx=0.0, rely=0.0, x=15, y=15, anchor='nw')

        self.current_task_results = []
        self.time_left = self.settings["task_durations"][self.current_task_name]
        self.timer_label = tk.Label(self, text=f"Time: {self.time_left}", font=CONFIG["fonts"]["timer"], bg=self.theme["app_bg"], fg=self.theme["label_fg"])
        self.timer_label.place(relx=1.0, rely=1.0, x=-10, y=-10, anchor='se')
        self._update_timer()
        self._task_timer_id = self.after(self.time_left * 1000, self.end_task)
        self.show_next_question()

    def _update_timer(self):
        if self.time_left >= 0:
            self.timer_label.config(text=f"Time: {self.time_left}")
            self.time_left -= 1
            self._update_timer_id = self.after(1000, self._update_timer)

    def _show_task_summary_screen(self, task_name, stats):
        self._clear_frame()
        main_frame = tk.Frame(self, bg=self.theme["app_bg"])
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)

        tk.Label(main_frame, text=f"Results for: {task_name}", font=self.settings["fonts"]["title"], bg=self.theme["app_bg"], fg=self.theme["label_fg"]).pack(pady=10)

        # --- Display Key Metrics ---
        # Time
        time_text = f"Time Taken: {stats['time_elapsed']:.1f}s / {stats['max_time']}s"
        tk.Label(main_frame, text=time_text, font=self.settings["fonts"]["header"], bg=self.theme["app_bg"], fg=self.theme["label_fg"]).pack(pady=5)
        
        # Accuracy
        accuracy_text = f"Accuracy: {stats['accuracy']:.1f}% ({stats['answered_correct']} / {stats['total_answered']})"
        tk.Label(main_frame, text=accuracy_text, font=self.settings["fonts"]["header"], bg=self.theme["app_bg"], fg=self.theme["label_fg"]).pack(pady=5)

        # Adjusted Score
        if isinstance(stats.get('adjusted_score'), (int, float)):
            score_text = f"Adjusted Score: {stats['adjusted_score']:.2f}"
            percentage_text = f"Score Percentage: {stats['score_percentage']:.1f}% (of max {stats['question_bank_size']})"
            tk.Label(main_frame, text=score_text, font=self.settings["fonts"]["header"], bg=self.theme["app_bg"], fg=self.theme["label_fg"]).pack(pady=(15, 5))
            tk.Label(main_frame, text=percentage_text, font=self.settings["fonts"]["header"], bg=self.theme["app_bg"], fg=self.theme["label_fg"]).pack(pady=5)

        # Plotting logic
        summary_df = self.data_manager.load_summary_data()
        history_df = summary_df[summary_df['task_name'] == task_name]

        fig, ax = plt.subplots(figsize=(5, 5))
        fig.patch.set_facecolor(self.theme["app_bg"])
        ax.set_facecolor(self.theme["card_bg"])

        if not history_df.empty:
            ax.scatter(history_df['accuracy'], history_df['seconds_per_question'], alpha=0.6, s=50, label='Past Logged Attempts', color="#3498db")
        if stats['total_answered'] > 0:
            ax.scatter(stats['accuracy'], stats['spq'], color="#e74c3c", edgecolors='black', s=120, marker='*', label='This Attempt')
        
        ax.set_title('Accuracy vs. Time per Question', color=self.theme["label_fg"])
        ax.set_xlabel('Accuracy (%)', color=self.theme["label_fg"])
        ax.set_ylabel('Seconds per Question (s/Q)', color=self.theme["label_fg"])
        ax.legend()
        ax.grid(True, alpha=0.2)
        ax.tick_params(colors=self.theme["label_fg"])
        fig.tight_layout(pad=2.0)
        
        canvas = FigureCanvasTkAgg(fig, master=main_frame)
        canvas.get_tk_widget().pack(side='top', fill='both', expand=True, pady=10)
        
        button_text, command = ("Back to Home", self.create_welcome_screen) if self.is_practice_mode else ("Continue", self.next_task)
        tk.Button(main_frame, text=button_text, font=CONFIG["fonts"]["button"], bg=self.theme["button_bg"], fg=self.theme["button_fg"], relief='flat', padx=20, pady=10, command=command).pack(pady=20)

    def _show_final_results(self):
        self._clear_frame()
        # Main content area that will be scrollable
        scrollable_frame = ScrollableFrame(self, bg=self.theme["app_bg"])
        scrollable_frame.pack(side="top", fill="both", expand=True)
        main_frame = scrollable_frame.interior
        
        tk.Label(main_frame, text="Test Series Complete!", font=self.settings["fonts"]["title"], bg=self.theme["app_bg"], fg=self.theme["label_fg"]).pack(pady=(40, 20))
        
        summary_text = ""
        for task_summary in self.series_results:
            task_name = task_summary['task_name']
            
            summary_text += (
                f"{task_name}:\n"
                f"  - Questions in Bank: {task_summary['question_bank_size']}\n"
                f"  - Answered: {task_summary['total_answered']} ({task_summary['answered_correct']} ✓, {task_summary['answered_wrong']} ✗, {task_summary['not_answered']} ?)\n"
                f"  - Accuracy: {task_summary['accuracy']:.1f}%\n"
                f"  - Adjusted Score: {task_summary['adjusted_score']:.2f}\n"
                f"  - Score Percentage: {task_summary['score_percentage']:.1f}%\n"
                f"  - Time Taken: {task_summary['time_elapsed']:.1f}s / {task_summary['max_time']}s\n\n"
            )
            
        tk.Label(main_frame, text=summary_text, font=self.settings["fonts"]["small"], justify='left', bg=self.theme["app_bg"], fg=self.theme["label_fg"]).pack(pady=20, padx=50)
        
        # The button is now a direct child of the main window, so it's not scrolled
        tk.Button(self, text="Practice Again", font=self.settings["fonts"]["button"], bg=self.theme["button_bg"], fg=self.theme["button_fg"], relief='flat', command=self.create_welcome_screen).pack(pady=20, ipady=5)
    
    def start_series(self):
        self.is_practice_mode = False
        self.task_order = list(self.settings["task_durations"].keys())
        self.current_task_index = -1
        self.series_results = [] # This stores summary dicts per task
        self.next_task()

    def start_practice_session(self, task_name):
        self.is_practice_mode = True; self.current_task_name = task_name; self.current_task_index = -1; self.series_results = []; self._show_task_intro()

    def next_task(self):
        self.current_task_index += 1
        if self.current_task_index < len(self.task_order): self.current_task_name = self.task_order[self.current_task_index]; self._show_task_intro()
        else: self._show_final_results()

    def end_task(self):
        if hasattr(self, 'task_is_ending') and self.task_is_ending:
            return
        self.task_is_ending = True
        
        self._cancel_timers()

        # --- UNIFIED SCORING LOGIC ---
        stats = {}
        bank_size = self.question_bank_size
        answered_correct = sum(r['correct'] for r in self.current_task_results)
        total_answered = len(self.current_task_results)
        answered_wrong = total_answered - answered_correct
        not_answered = bank_size - total_answered
        
        max_time = self.settings["task_durations"][self.current_task_name]
        time_elapsed = max_time - max(0, self.time_left)

        stats['question_bank_size'] = bank_size
        stats['total_answered'] = total_answered
        stats['answered_correct'] = answered_correct
        stats['answered_wrong'] = answered_wrong
        stats['not_answered'] = not_answered
        stats['max_time'] = max_time
        stats['time_elapsed'] = time_elapsed
        stats['accuracy'] = (answered_correct / total_answered * 100) if total_answered > 0 else 0
        stats['spq'] = (time_elapsed / total_answered) if total_answered > 0 else 0

        if self.is_practice_mode:
            stats['adjusted_score'] = 'N/A'
            stats['score_percentage'] = 'N/A'
        else:
            penalty = self.settings["wrong_penalty"][self.current_task_name]
            # Adjusted score penalizes wrong AND unanswered questions
            stats['adjusted_score'] = answered_correct + (answered_wrong + not_answered) * penalty
            stats['score_percentage'] = (max(0, stats['adjusted_score']) / bank_size * 100) if bank_size > 0 else 0
            
            # Log to CSV
            self.data_manager.log_summary_stats(self.current_task_name, bank_size, answered_correct, time_elapsed, penalty)
            
            # Store this complete summary for the final report screen
            task_summary = stats.copy()
            task_summary['task_name'] = self.current_task_name
            self.series_results.append(task_summary)

        if total_answered > 0 or not self.is_practice_mode:
            self._show_task_summary_screen(self.current_task_name, stats)
        else:
            # If nothing was answered in practice mode, just go back
            self.create_welcome_screen()

    def show_next_question(self):
        self._clear_frame(self.task_frame)
        gens = {'Reasoning': self.factory.generate_reasoning, 'Perceptual Speed': self.factory.generate_perceptual_speed, 'Number Speed & Accuracy': self.factory.generate_number_speed, 'Word Meaning': self.factory.generate_word_meaning, 'Spatial Visualisation': self.factory.generate_spatial_visualisation}
        self.current_question = gens[self.current_task_name](); self._display_question_ui(self.current_question); self.question_start_time = time.time()

    def _check_answer(self, selected_answer):
        """
        Processes the user's answer, logs it, and decides whether to
        show the next question or end the task.
        """
        # 1. Calculate the result of this single question
        time_taken_ms = (time.time() - self.question_start_time) * 1000
        is_correct = (selected_answer == self.current_question['answer'])

        # 2. Handle detailed debug logging if enabled
        if self.settings['debug_logging_enabled'] and not self.is_practice_mode:
            self.data_manager.log_debug_event(
                task_name=self.current_task_name,
                question_data=self.current_question,
                selected_answer=selected_answer,
                correct_answer=self.current_question['answer'],
                time_ms=time_taken_ms,
                is_correct=is_correct
            )
        
        # 3. Store the simple result (correct/incorrect) for the current task's stats.
        # This list is used by end_task() to calculate the summary.
        self.current_task_results.append({'correct': is_correct})

        # 4. Increment the count of questions answered in this task.
        self.questions_answered_in_task += 1

        # 5. Determine the next action: continue the task or end it.
        # This check only applies in the full test mode. Practice mode always continues until the timer runs out.
        if not self.is_practice_mode and self.questions_answered_in_task >= self.question_bank_size:
            # The question limit has been reached, so the task must end.
            print(f"Question limit of {self.question_bank_size} reached. Ending task.")
            self.end_task()
        else:
            # The task is not over, so proceed to the next question.
            self.show_next_question()

    def _cancel_timers(self):
        if self._task_timer_id: self.after_cancel(self._task_timer_id); self._task_timer_id = None
        if self._update_timer_id: self.after_cancel(self._update_timer_id); self._update_timer_id = None

    def _on_closing(self):
        self._cancel_timers(); self.quit(); self.destroy()



if __name__ == "__main__":
    app = GiaApp()
    app.mainloop()
