import tkinter as tk
from tkinter import ttk
import time
from PIL import Image, ImageDraw, ImageFont, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from config import CONFIG
from data_manager import DataManager
from question_factory import QuestionFactory

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
        self.is_practice_mode = False
        self.current_task_name = None
        self.current_question = None
        self.question_start_time = 0
        self.current_task_results = []
        self.series_results = []
        self.task_order = []
        self.current_task_index = -1
        self.time_left = 0

        # --- Timers and UI Elements ---
        self._task_timer_id, self._update_timer_id = None, None
        self.timer_label, self.task_frame = None, None
        self.spatial_images = []

        self._configure_styles()
        self._configure_window()
        
        self.create_welcome_screen()
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _configure_window(self):
        self.title("GIA Practice Tool")
        self.geometry("900x750") # Increased height slightly for new buttons
        self.configure(bg=CONFIG["colors"]["background"])

    def _configure_styles(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        bg_color = CONFIG["colors"]["background"]
        
        style.configure('TButton', font=CONFIG["fonts"]["button"], padding=(8, 4))
        style.configure('Practice.TButton', font=('Helvetica', 12), padding=(6, 3))
        style.configure('Title.TLabel', font=CONFIG["fonts"]["title"], background=bg_color)
        style.configure('Header.TLabel', font=CONFIG["fonts"]["header"], background=bg_color)
        style.configure('Small.TLabel', font=CONFIG["fonts"]["small"], background=bg_color)
        style.configure('Italic.TLabel', font=CONFIG["fonts"]["italic"], background=bg_color)
        style.configure('Timer.TLabel', font=CONFIG["fonts"]["timer"], background=bg_color)
        style.configure('MonoLarge.TLabel', font=CONFIG["fonts"]["mono_large"], background=bg_color)

    # --- Screen/Frame Management ---
    
    def _clear_frame(self, frame=None):
        target_frame = frame if frame else self
        for widget in target_frame.winfo_children():
            widget.destroy()

    def create_welcome_screen(self):
        self._clear_frame()
        
        # --- Full Test Series ---
        ttk.Label(self, text="GIA Practice Tool", style='Title.TLabel').pack(pady=(20, 10))
        ttk.Label(self, text="Take a full, timed test series to log your performance.", style='Header.TLabel').pack(pady=5)
        ttk.Button(self, text="Start Full Test Series", command=self.start_series).pack(pady=15, ipady=10)
        
        ttk.Separator(self, orient='horizontal').pack(fill='x', padx=50, pady=20)

        # --- Practice Mode ---
        practice_label_text = "Or, Practice a Single Task (results are not logged):"
        ttk.Label(self, text=practice_label_text, style='Header.TLabel').pack(pady=5)
        
        practice_frame = tk.Frame(self, bg=CONFIG["colors"]["background"])
        practice_frame.pack(pady=10)
        
        for task_name in CONFIG["task_durations"].keys():
            # Use a lambda with a default argument to correctly capture the task_name
            btn = ttk.Button(practice_frame, text=task_name, style='Practice.TButton',
                             command=lambda name=task_name: self.start_practice_session(name))
            btn.pack(pady=4)

        ttk.Separator(self, orient='horizontal').pack(fill='x', padx=50, pady=20)

        # --- Past Performance Display ---
        summary_df = self.data_manager.load_summary_data()
        if not summary_df.empty:
            avg_performance = summary_df.groupby('task_name')[['accuracy', 'seconds_per_question']].mean().reset_index()
            
            ttk.Label(self, text="Average Logged Performance:", style='Header.TLabel').pack(pady=(0, 5))
            for _, row in avg_performance.iterrows():
                text = (f"{row['task_name']}: Avg Accuracy {row['accuracy']:.1f}%, "
                        f"Avg Time/Q {row['seconds_per_question']:.3f} s/Q")
                ttk.Label(self, text=text, style='Small.TLabel').pack()
        else:
            ttk.Label(self, text="No past summary data available yet.", style='Small.TLabel').pack()

    def _show_task_intro(self):
        ### MODIFIED ### to show a note in practice mode
        self._clear_frame()
        duration = CONFIG["task_durations"][self.current_task_name]
        
        title_text = f"Task: {self.current_task_name}"
        if self.is_practice_mode:
            title_text = f"Practice Mode: {self.current_task_name}"
        
        ttk.Label(self, text=title_text, style='Title.TLabel').pack(pady=(50, 20))
        ttk.Label(self, text=f"You will have {duration} seconds for this task.", style='Header.TLabel').pack(pady=10)
        ttk.Button(self, text="Start Task", command=self.start_current_task).pack(pady=40, ipady=10)

        if self.is_practice_mode:
            note = "Note: Performance in practice mode is not saved."
            ttk.Label(self, text=note, style='Italic.TLabel', foreground="blue").pack(pady=20)

    def _show_task_summary_screen(self, task_name, stats):
        ### MODIFIED ### to handle different "Continue" actions
        self._clear_frame()
        ttk.Label(self, text=f"Results for: {task_name}", style='Title.TLabel').pack(pady=20)
        
        summary_df = self.data_manager.load_summary_data()
        history_df = summary_df[summary_df['task_name'] == task_name]

        fig, ax = plt.subplots(figsize=(6, 6))
        fig.patch.set_facecolor(CONFIG["colors"]["plot_background"])
        ax.set_facecolor(CONFIG["colors"]["plot_background"])

        if not history_df.empty:
            ax.scatter(history_df['accuracy'], history_df['seconds_per_question'],
                       alpha=0.6, s=50, label='Past Logged Attempts', color=CONFIG["colors"]["past_performance"])

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
        
        # Determine next action based on mode
        if self.is_practice_mode:
            button_text = "Back to Home"
            command = self.create_welcome_screen
        else:
            button_text = "Continue to Next Task"
            command = self.next_task
            
        ttk.Button(self, text=button_text, command=command).pack(pady=20, ipady=10)

    def _show_final_results(self):
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
        ### MODIFIED ### to set practice mode to False
        self.is_practice_mode = False
        self.task_order = list(CONFIG["task_durations"].keys())
        self.current_task_index = -1
        self.series_results = []
        self.next_task()

    def start_practice_session(self, task_name):
        ### NEW ### method to start a single practice task
        self.is_practice_mode = True
        self.current_task_name = task_name
        self.current_task_index = -1 # Not relevant but good to reset
        self.series_results = [] # Not used in practice mode but clear anyway
        self._show_task_intro()

    def next_task(self):
        self.current_task_index += 1
        if self.current_task_index < len(self.task_order):
            self.current_task_name = self.task_order[self.current_task_index]
            self._show_task_intro()
        else:
            self._show_final_results()

    def start_current_task(self):
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
        ### MODIFIED ### to handle logging conditionally
        self._cancel_timers()
        
        total = len(self.current_task_results)
        if total > 0:
            correct = sum(r['correct'] for r in self.current_task_results)
            duration = CONFIG["task_durations"][self.current_task_name]
            
            if self.is_practice_mode:
                # In practice mode, just calculate stats for the summary screen, don't log.
                accuracy = (correct / total) * 100
                spq = duration / total
                stats = {'accuracy': accuracy, 'spq': spq}
            else:
                # In full test mode, log the stats and get them back.
                stats = self.data_manager.log_summary_stats(self.current_task_name, total, correct, duration)
            
            self._show_task_summary_screen(self.current_task_name, stats)
        else:
            # If no questions were answered, decide where to go next
            if self.is_practice_mode:
                self.create_welcome_screen()
            else:
                self.next_task()

    def show_next_question(self):
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
        ### MODIFIED ### to log only if not in practice mode
        time_taken_ms = (time.time() - self.question_start_time) * 1000
        is_correct = (selected_answer == self.current_question['answer'])
        
        if not self.is_practice_mode:
            self.data_manager.log_question_result(self.current_task_name, is_correct, time_taken_ms)
            self.series_results.append({
                'task': self.current_task_name,
                'correct': is_correct,
                'time': time_taken_ms
            })
        
        self.current_task_results.append({'correct': is_correct})
        self.show_next_question()

    # --- UI Display Methods ---

    def _display_question_ui(self, question):
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
        options_frame = tk.Frame(self.task_frame, bg=CONFIG["colors"]["background"])
        options_frame.pack(pady=(100, 20))
        max_len = max(len(str(o)) for o in question['options'])
        btn_width = max(10, min(max_len + 2, 20))
        wrap_length = btn_width * 8 
        for option in question['options']:
            btn = tk.Button(options_frame, text=str(option), width=btn_width, wraplength=wrap_length,
                            justify='center', font=CONFIG["fonts"]["button"],
                            command=lambda o=option: self._check_answer(o))
            btn.pack(side='left', padx=10, ipady=4, pady=4)

    def _display_spatial(self, question):
        self.spatial_images = []
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
        if self.time_left > 0:
            self.timer_label.config(text=f"Time left: {self.time_left}")
            self.time_left -= 1
            self._update_timer_id = self.after(1000, self._update_timer)
    
    def _cancel_timers(self):
        if self._task_timer_id:
            self.after_cancel(self._task_timer_id)
            self._task_timer_id = None
        if self._update_timer_id:
            self.after_cancel(self._update_timer_id)
            self._update_timer_id = None

    def _on_closing(self):
        self._cancel_timers()
        self.quit()
        self.destroy()


if __name__ == "__main__":
    app = GiaApp()
    app.mainloop()