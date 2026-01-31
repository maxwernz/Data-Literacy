import util
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.pyplot as plt
import help_functions as hp


def filter_data(data:pd.DataFrame, discipline:str, gender:str, age_group:str):
    """
    Filter a performance dataset for a specific discipline, gender, and age group.

    Parameters
    ----------
    data : pd.DataFrame
        The full dataset containing at least the columns:
        ["disziplin", "geschlecht", "altersklasse"].
    discipline : str
        The discipline to filter for (e.g. "1500 m").
    gender : str
        The gender to filter for (e.g. "W", "M").
    age_group : str
        The age group to filter for (e.g. "U23", "20", "18", "Maenner", "Frauen", "15", "16").

    Returns
    -------
    pd.DataFrame
        A filtered subset of the data matching all conditions.
    """
    data_fil = data[(data["disziplin"] == discipline) & (data["geschlecht"] == gender) & (data["altersklasse"] == age_group)]
    return data_fil

def get_top_data(data:pd.DataFrame, top_performances:int, smoothing=1, track_discipline=False):
    """
    Compute yearly top performance statistics and optionally smooth them.

    Parameters
    ----------
    data : pd.DataFrame
        Dataset containing at least the columns ["jahr", "leistung"].
        Values in "leistung" must be numeric (lower = better for running,
        higher = better for throws/jumps if track_discipline=True).
    top_performances : int
        Number of top athletes to consider per year.
    smoothing : int, optional (default = 1)
        Rolling window size for smoothing the yearly mean.
        - smoothing = 1 → no smoothing
        - smoothing > 1 → centered rolling mean over given window size
    track_discipline : bool, optional (default = False)
        Defines how "best performance" is determined:
        - True: lower performance is better (e.g., running times)
        - False: higher performance is better (e.g., throws, jumps)

    Returns
    -------
    pd.Series
        A Series indexed by year containing the mean of the top performances
        (possibly smoothed).

    Notes
    -----
    - The `smoothing` applies a centered rolling window: a value for year Y
      uses values from Y−k ... Y ... Y+k.
    - NaN values appear at edges when smoothing.
    """
    topPerf = data.groupby("jahr", group_keys=False).apply(
        lambda x: x.sort_values(by="leistung", ascending=track_discipline).head(top_performances)
    ).reset_index(drop=True)

    mean_topPerf = topPerf.groupby("jahr")["leistung"].mean()
    if smoothing > 1:
        mean_topPerf = mean_topPerf.sort_index().rolling(window=smoothing, center=True).mean()
    return mean_topPerf

def compute_relative_gap(data:pd.DataFrame, mean_topPerf):
    """
    Compute the relative performance gap of each athlete to the mean of top performances per year.

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame containing at least the columns ["jahr", "leistung"].
        "leistung" must be numeric.
    mean_topPerf : pd.Series
        Series indexed by year containing the mean of top performances 
        (e.g., output from get_top_data()).

    Returns
    -------
    pd.DataFrame
        Original DataFrame with two additional columns:
        - "mean_topPerf": the mean of top performances for that year
        - "relGapAth": relative gap per athlete, computed as
          (leistung - mean_topPerf) / mean_topPerf

    """
    data = data.merge(mean_topPerf.rename("mean_topPerf"), how="left", left_on="jahr", right_index=True)
    data["relGapAth"] = (data["leistung"] - data["mean_topPerf"]) / data["mean_topPerf"]
    return data