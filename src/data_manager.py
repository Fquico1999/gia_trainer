import os
import csv
from datetime import datetime
import pandas as pd

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
                csv.writer(f).writerow(['timestamp', 'task_name', 'total_questions', 'correct_questions', 'accuracy', 'seconds_per_question'])
    
    def log_question_result(self, task_name, is_correct, time_taken_ms):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.results_log, 'a', newline='') as f:
            csv.writer(f).writerow([timestamp, task_name, int(is_correct), f"{time_taken_ms:.2f}"])

    def log_summary_stats(self, task_name, total, correct, duration):
        if total == 0: return None
        accuracy = (correct / total) * 100
        seconds_per_question = duration / total
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.summary_log, 'a', newline='') as f:
            csv.writer(f).writerow([timestamp, task_name, total, correct, f"{accuracy:.2f}", f"{seconds_per_question:.3f}"])
        return {'accuracy': accuracy, 'spq': seconds_per_question}

    def load_summary_data(self):
        if not os.path.exists(self.summary_log): return pd.DataFrame()
        try:
            df = pd.read_csv(self.summary_log)
            if df.empty: return pd.DataFrame()
            df['accuracy'] = pd.to_numeric(df['accuracy'], errors='coerce')
            df['seconds_per_question'] = pd.to_numeric(df['seconds_per_question'], errors='coerce')
            df.dropna(subset=['accuracy', 'seconds_per_question'], inplace=True)
            return df
        except Exception as e:
            print(f"Error loading summary data: {e}")
            return pd.DataFrame()