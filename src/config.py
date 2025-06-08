from themes import THEMES

THEME_NAME = "Forest"  # Options: "Default", "Dark", "Forest"

SELECTED_THEME = THEMES.get(THEME_NAME, THEMES["Default"])

CONFIG = {
    "questions_per_minute": 17,  # 75 questions / 5 minutes seems to be the test pace. Here I have it higher for practice
     "wrong_penalty": {
        "Reasoning": -1.0,
        "Perceptual Speed": -0.25,
        "Number Speed & Accuracy": -0.5,
        "Word Meaning": -0.5,
        "Spatial Visualisation": -0.5,
    },
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
    # The 'colors' dict is replaced by SELECTED_THEME
    "fonts": {
        "button": ('Helvetica', 16, 'bold'),
        "title": ('Helvetica', 28, 'bold'),
        "header": ('Helvetica', 16),
        "small": ('Helvetica', 12),
        "italic": ('Helvetica', 11, 'italic'),
        "timer": ('Helvetica', 14, 'bold'),
        "mono_large": ('Courier', 40, 'bold'),
        "spatial_font": "arial.ttf",
    },
}