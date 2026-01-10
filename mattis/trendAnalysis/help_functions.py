import pandas as pd
import numpy as np
import statsmodels.api as sm

def collect_top_entries(data, num_entries=10):
    """
    Get top-N entries per group and compute per-group stats.
    
    Parameters:
    :data: DataFrame
    :num_entries: int, number of top entries to consider per group
    
    Returns:
    :top_raw: DataFrame with all top-N raw rows combined
    """
    
    # Ensure iaaf_score is numeric
    data["iaaf_score"] = pd.to_numeric(data["iaaf_score"], errors="coerce")
    
    top_rows = []    

    for group_vals, group_df in data.groupby(["jahr", "geschlecht", "altersklasse", "disziplin"]):
        # Sort by iaaf_score descending (best first)
        sorted_df = group_df.sort_values("iaaf_score", ascending=False)
        top_n = sorted_df.head(num_entries)
        
        if len(top_n) == num_entries:
            top_rows.append(top_n)
    
    top_raw = pd.concat(top_rows, ignore_index=True) if top_rows else pd.DataFrame()
    
    return top_raw

def func_norm_per_group(data, func=np.mean):
    """
    Calculate for every subgroup diszipline x gender x age group

    1. A given function or population parameter
    2. Normalize results to the first year
    
    :param data: Description
    :param func: Description
    """
    subgroup_norm = []
    # For every group e.g. diszipline x gender x age group calculate the given function (mean, std ...) per year
    for (disc, gender, age), subdata in data.groupby(["disziplin", "geschlecht", "altersklasse"]):
        group = subdata.groupby("jahr")["iaaf_score"].agg(func)

        if 2001 not in group.index:
            continue

        norm = group / group.loc[2001]
        subgroup_norm.append(norm)
    
    norm_data = pd.concat(subgroup_norm, axis=1)
    mean_norm = norm_data.mean(axis=1)

    mean_norm = mean_norm.sort_index(ascending=True)
    
    return mean_norm

def func_norm_per_group(data, func=np.mean):
    """
    Calculate for every subgroup diszipline x gender x age group

    1. A given function or population parameter
    2. Normalize results to the first year
    
    :param data: Description
    :param func: Description
    """
    subgroup_norm = []
    # For every group e.g. diszipline x gender x age group calculate the given function (mean, std ...) per year
    for (disc, gender, age), subdata in data.groupby(["disziplin", "geschlecht", "altersklasse"]):
        group = subdata.groupby("jahr")["iaaf_score"].agg(func)

        if 2001 not in group.index:
            continue
        for year in group.index:
            subgroup_norm.append({
                            "func_value": group.loc[year],
                            "event": disc,
                            "gender": gender,
                            "age": age,
                            "year": year,
                        })
    
    return subgroup_norm



def linear_regression(data):
    """
    Generate linear regression for time series data, e.g. data over the years in our case
    
    :param data: Data over the years; years x parameter

    """
    years = data.index.values.astype(float)
    X = sm.add_constant(years)
    model = sm.OLS(data.values, X).fit()
    slope = model.params[1]
    r2_global = model.rsquared
    p_global = model.pvalues[1]

    return X, model, slope, r2_global, p_global
