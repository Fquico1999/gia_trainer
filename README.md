# GIA Practice Tool

A desktop application built with Python and Tkinter to practice for GIA-style cognitive aptitude tests. The interface now opens in a larger window with centered controls for easier use.

## Features

-   **Full Test Mode**: Simulate a full, timed test series across all five cognitive areas. Performance is logged and tracked over time.
-   **Practice Mode**: Practice any single task type without the pressure of logging results. Your performance is still compared against past logged attempts.
-   **Performance Analytics**: After each task, view a scatter plot of your accuracy vs. speed compared to your historical performance.
-   **Persistent Logging**: All test mode results are saved to local CSV files for tracking progress.
-   **Modern UI**: The application starts with a larger window and centered controls.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/gia-practice-tool.git
    cd gia-practice-tool
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To run the application, execute the `main.py` script from the root directory of the project:

```bash
python src/main.py
```
