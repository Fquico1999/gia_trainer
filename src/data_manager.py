import os
import csv
import json
from datetime import datetime
import pandas as pd

class DataManager:
    """Handles reading from and writing to CSV log files."""
    def __init__(self, results_log, summary_log):
        self.results_log = results_log
        self.summary_log = summary_log
        self.debug_log = 'gia_debug_log.csv'
        self._setup_logging()

    def _setup_logging(self):
        if not os.path.exists(self.results_log):
            with open(self.results_log, 'w', newline='') as f:
                csv.writer(f).writerow(['timestamp', 'task_name', 'is_correct', 'time_taken_ms'])
        
        if not os.path.exists(self.summary_log):
            with open(self.summary_log, 'w', newline='') as f:
                csv.writer(f).writerow([
                    'timestamp', 'task_name', 'total_questions', 'correct_questions',
                    'accuracy', 'seconds_per_question', 'adjusted_score' # <<< ADDED
                ])

        if not os.path.exists(self.debug_log):
            with open(self.debug_log, 'w', newline='') as f:
                csv.writer(f).writerow([
                    'timestamp', 'task_name', 'question_details', 'selected_answer',
                    'correct_answer', 'time_taken_ms', 'is_correct'
                ])

    def log_debug_event(self, task_name, question_data, selected_answer, correct_answer, time_ms, is_correct):
        """Logs a highly detailed record of a single question event for debugging."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Use json.dumps to serialize the entire question dictionary into a string
        question_details_str = json.dumps(question_data)

        with open(self.debug_log, 'a', newline='') as f:
            csv.writer(f).writerow([
                timestamp,
                task_name,
                question_details_str,
                selected_answer,
                correct_answer,
                f"{time_ms:.2f}",
                is_correct
            ])

    def log_question_result(self, task_name, is_correct, time_taken_ms):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.results_log, 'a', newline='') as f:
            csv.writer(f).writerow([timestamp, task_name, int(is_correct), f"{time_taken_ms:.2f}"])

    def log_summary_stats(self, task_name, total, correct, duration, wrong_penalty):
        if total == 0:
            return None
            
        accuracy = (correct / total) * 100
        seconds_per_question = duration / total
        wrong_count = total - correct
        
        # Calculate the adjusted score - total here is the number of questions in the bank
        adjusted_score = correct + (wrong_count * wrong_penalty)
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.summary_log, 'a', newline='') as f:
            csv.writer(f).writerow([
                timestamp, task_name, total, correct, f"{accuracy:.2f}",
                f"{seconds_per_question:.3f}", f"{adjusted_score:.2f}" # <<< ADDED
            ])
        
        return {
            'accuracy': accuracy,
            'spq': seconds_per_question,
            'adjusted_score': adjusted_score
        }

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