import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy import stats

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

def calculate_enhanced_stats(df, group_cols, start_period=(2001, 2004), end_period=(2021, 2024)):
    """
    Calculate Welch's t-Test, Levene-Test und Cohen's d for two time periods.
    Vergleicht 2001-2004 vs. 2021-2024.
    """
    results_enhanced = []
    
    if not group_cols:
        grouped = [("Global", df)]
    else:
        grouped = df.groupby(group_cols)

    for names, subgroup in grouped:

        s_pool = subgroup[subgroup["jahr"].between(*start_period)]["iaaf_score"].dropna().values
        e_pool = subgroup[subgroup["jahr"].between(*end_period)]["iaaf_score"].dropna().values

        if len(s_pool) > 1 and len(e_pool) > 1:
            t_stat, p_mean = stats.ttest_ind(e_pool, s_pool, equal_var=False)

            _, p_std = stats.levene(e_pool, s_pool)

            n1, n2 = len(e_pool), len(s_pool)
            v1, v2 = np.var(e_pool, ddof=1), np.var(s_pool, ddof=1)
            pooled_sd = np.sqrt(((n1 - 1) * v1 + (n2 - 1) * v2) / (n1 + n2 - 2))
            
            mean_e, mean_s = np.mean(e_pool), np.mean(s_pool)
            cohen_d = (mean_e - mean_s) / pooled_sd if pooled_sd > 0 else 0

            m_diff_perc = (mean_e - mean_s) / mean_s * 100
            std_e, std_s = np.std(e_pool), np.std(s_pool)
            s_diff_perc = (std_e - std_s) / std_s * 100

            abs_d = abs(cohen_d)
            if abs_d > 0.8: interp = "Large"
            elif abs_d > 0.5: interp = "Med"
            elif abs_d > 0.2: interp = "Small"
            else: interp = "Negligible"

            res = {}
            if group_cols:
                res = {col: val for col, val in zip(group_cols, names)} if isinstance(names, tuple) else {group_cols[0]: names}
            else:
                res["Group"] = "Global"            
            
            res.update({
                "Mean_Diff_%": round(m_diff_perc, 2),
                "P_Val_Mean": round(p_mean, 4),
                "Cohen_d": round(cohen_d, 3),
                "STD_Diff_%": round(s_diff_perc, 2),
                "P_Val_STD": round(p_std, 4),
                "Interpretation": interp
            })
            results_enhanced.append(res)

    return pd.DataFrame(results_enhanced)

def calculate_rank_diff(df, group_cols, num_entries):
    """
    Berechnet die prozentuale Differenz der IAAF-Scores zwischen 
    2001-2004 und 2021-2024 pro Rang innerhalb definierter Gruppen.
    """
    results = []
    
    full_group_cols = group_cols + ["disziplin"]
    
    for names, subgroup in df.groupby(full_group_cols):
        S_gr = subgroup.pivot_table(index="jahr", columns="rank", values="iaaf_score")
        
        available_ranks = [r for r in range(1, num_entries + 1) if r in S_gr.columns]
        
        for r in available_ranks:
            start_vals = S_gr.loc[2001:2004, r]
            end_vals = S_gr.loc[2021:2024, r]
            
            if not start_vals.dropna().empty and not end_vals.dropna().empty:
                m_start = start_vals.mean()
                m_end = end_vals.mean()
                
                res = {col: val for col, val in zip(full_group_cols, names)}
                res.update({
                    "rank": r,
                    "m_start": m_start,
                    "m_end": m_end
                })
                results.append(res)
    
    res_df = pd.DataFrame(results)
    
    final = res_df.groupby(group_cols + ["rank"]).agg({
        "m_start": "mean",
        "m_end": "mean"
    }).reset_index()
    
    final["mean_diff_perc"] = (final["m_end"] - final["m_start"]) / final["m_start"] * 100
    return final
