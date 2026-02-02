# Data Literacy Project - Athletics Data Analysis

## Project Overview
This project analyzes German athletics performance data (DLV Bestenlisten) to investigate trends, performance gaps, and the impact of events like the COVID-19 pandemic. The analysis involves extracting data from PDF reports, cleaning and standardizing it, calculating IAAF/WA scores, and visualizing the results.

## Quick Start (Installation)

We recommend using **`uv`** for the easiest setup. It handles Python versions and dependencies automatically.

### Option 1: The Fast Way (Recommended)
1.  **Install `uv`** (if you don't have it):
    *   **Mac / Linux:**
        ```bash
        curl -LsSf https://astral.sh/uv/install.sh | sh
        ```
    *   **Windows:**
        ```powershell
        powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
        ```

2.  **Setup the Project:**
    Open your terminal in the project folder and run:
    ```bash
    uv sync
    ```
    *This creates a virtual environment and installs all necessary packages (pandas, matplotlib, etc.) exactly as defined in the lockfile.*

3.  **Run Jupyter:**
    ```bash
    uv run jupyter notebook
    ```

### Option 2: The Standard Way (pip)
If you prefer standard Python tools:
1.  Create a virtual environment:
    ```bash
    python -m venv .venv
    ```
2.  Activate it:
    *   **Mac/Linux:** `source .venv/bin/activate`
    *   **Windows:** `.venv\Scripts\activate`
3.  Install the project in editable mode:
    ```bash
    pip install -e .
    ```
4.  Start Jupyter:
    ```bash
    jupyter notebook
    ```

---

## Directory Structure

*   **`lib/`**: The core Python library for this project.
    *   `util.py`: Helper functions for loading and cleaning data.
    *   `plotting_style.py`: Central plotting configuration (Tübingen Corporate Design).
    *   `iaaf_points/`: Logic and data for calculating IAAF performance scores.
*   **`data_csv/`**: Processed data files (e.g., `final_Data_iaaf_scores_neu.csv`).
*   **`Data_pdf/`**: Raw source PDF files (DLV Bestenlisten).
*   **`Plots/`**: Destination folder where `plt.savefig()` saves figures.
*   **`report/`**: LaTeX source for the final report.

---

## Usage Guide (Coding Standards)

This project is configured as a Python package. This means you can import `lib` from **any notebook** in any folder without messing with system paths (`sys.path.append` is no longer needed!).

### 1. Imports
Always use this standard import block:

```python
import pandas as pd
import numpy as np

# Project-specific imports
from lib import util
from lib import plotting_style as plt
from lib.iaaf_points import score_calculator
```

### 2. Loading Data
Use `util.load_data()` to get the cleaned dataframe. It handles type conversions (time strings to seconds) automatically.

```python
# Load standard dataset (filtered for relevant age groups/disciplines)
df = util.load_data()

# Load raw dataset (no filters)
df_all = util.load_data(filter=False)
```

### 3. Plotting
We use a custom wrapper around `matplotlib` to ensure all plots look consistent (ICML paper style).

```python
# Create a plot
fig, ax = plt.subplots()
ax.plot(x, y)
ax.set_title("My Analysis")

# Save the plot
# This AUTOMATICALLY saves to the project's 'Plots/' folder.
# You can specify a sub-category folder.
plt.savefig("my_figure_name", category="Exploration") 
# Result: saved to -> Plots/Exploration/my_figure_name.pdf
```

### 4. Calculating IAAF Points
You can calculate points for any performance using the `iaaf_points` module.

```python
# 1. Load the scoring coefficients
coeffs = score_calculator.get_iaaf_coeffs()

# 2. Calculate points (e.g., Men's 100m, 9.58 seconds)
points = score_calculator.score_from_mark("men", "100m", 9.58, coeffs)
print(points)  # Output: ~1374
```

## Troubleshooting
*   **LaTeX Errors:** The plotting style uses LaTeX for professional fonts. If you get errors about missing latex, the code tries to fallback to standard fonts. To get the best results, ensure a TeX distribution (TeX Live, MacTeX, or MiKTeX) is installed and on your system PATH.