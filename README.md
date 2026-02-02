# Data Literacy Project - Athletics Data Analysis

## Project Overview
This project analyzes German athletics performance data (DLV Bestenlisten) to investigate trends, performance gaps, and the impact of events like the COVID-19 pandemic. The analysis involves extracting data from PDF reports, cleaning and standardizing it, calculating IAAF/WA scores, and visualizing the results.

## Installation & Setup

We use **`uv`** for dependency management and project isolation. 

1.  **Install `uv`**: Follow the instructions at [here](https://docs.astral.sh/uv/getting-started/installation/).
2.  **Setup the Project**: Open your terminal in the project folder and run:
    ```bash
    uv sync
    ```
    *This command creates a virtual environment and installs all necessary dependencies and the internal library automatically.*
3.  **Verify Setup**: Run the validation script to ensure everything is working:
    ```bash
    uv run check_setup.py
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

## Usage Guide

### 1. Imports
Always use this standard import block:

```python
from lib import util
from lib import plotting_style as plt
```

### 2. Loading Data
Use `util.load_data()` to get the cleaned dataframe.

```python
# Load standard dataset (filtered for relevant age groups/disciplines)
df = util.load_data()

# Load raw dataset (no filters)
df_all = util.load_data(filter=False)
```

### 3. Plotting
We use a custom wrapper around `matplotlib` to ensure all plots look consistent (ICML paper style). Therefore dont use `import matplotlib.pyplot as plt` for plotting.

```python
# Create a plot
fig, ax = plt.subplots()
ax.plot(x, y)
ax.set_title("My Analysis")

# Save the plot
# This AUTOMATICALLY saves to the project's 'Plots/' folder.
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
*   **LaTeX Errors:** The plotting style uses LaTeX for professional fonts. If TeX is not found on your system, the code will automatically fallback to standard fonts. For the best visual results, ensure a TeX distribution (TeX Live, MacTeX, or MiKTeX) is installed.
