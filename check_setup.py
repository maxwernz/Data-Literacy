import sys
import os

def test_step(name, func):
    print(f"Testing {name:.<40}", end="")
    try:
        func()
        print("OK")
        return True
    except Exception as e:
        print("FAILED")
        print(f"  Error: {e}")
        return False

def check_standard_imports():
    import pandas
    import numpy
    import matplotlib
    import scipy
    import tueplots

def check_lib_imports():
    from lib import util
    from lib import plotting_style
    from lib.iaaf_points import score_calculator

def check_data_loading():
    from lib import util
    df = util.load_data()
    if df.empty:
        raise ValueError("DataFrame is empty. Check data_csv folder.")

def check_iaaf_logic():
    from lib.iaaf_points import score_calculator
    coeffs = score_calculator.get_iaaf_coeffs()
    # Test a known mark: Men's 100m, 10.00s
    score = score_calculator.score_from_mark("men", "100m", 10.00, coeffs)
    if score is None or score <= 0:
        raise ValueError(f"IAAF calculation returned invalid score: {score}")

def check_plotting():
    from lib import plotting_style as plt
    import matplotlib.pyplot as real_plt
    
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    # Test saving (should create Plots/test_setup/ folder)
    plt.savefig("setup_test_plot.pdf", category="test_setup")
    real_plt.close(fig)

def main():
    print("="*50)
    print("      DATA LITERACY PROJECT SETUP CHECK")
    print("="*50)
    print(f"Python version: {sys.version.split()[0]}")
    print(f"Project root:   {os.getcwd()}")
    print("-"*50)

    results = []
    results.append(test_step("Standard Library Imports", check_standard_imports))
    results.append(test_step("Internal 'lib' Imports", check_lib_imports))
    results.append(test_step("Data Loading (util.py)", check_data_loading))
    results.append(test_step("IAAF Scoring (score_calculator.py)", check_iaaf_logic))
    results.append(test_step("Plotting & Styles (plotting_style.py)", check_plotting))

    print("-"*50)
    if all(results):
        print("SUCCESS: Your environment is perfectly set up!")
        print("You can now start working on the notebooks.")
    else:
        print("CRITICAL: Some checks failed.")
        print("Please ensure you have run 'uv sync' or 'pip install -e .'")
    print("="*50)

if __name__ == "__main__":
    main()
