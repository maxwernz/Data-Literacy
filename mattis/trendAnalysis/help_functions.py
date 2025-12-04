import pandas as pd

def collect_top_entries(data, num_entries=10):
    """
    Collect top-N entries per group and compute per-group stats.
    
    Parameters:
    - data: DataFrame containing ['jahr', 'geschlecht', 'altersklasse', 'disziplin', 'iaaf_score']
    - num_entries: int, number of top entries to consider per group
    
    Returns:
    - top_stats: DataFrame with per-group mean and std of top-N
    - top_raw: DataFrame with all top-N raw rows combined
    """
    
    # Ensure iaaf_score is numeric
    data["iaaf_score"] = pd.to_numeric(data["iaaf_score"], errors="coerce")
    
    top_rows = []   # will store complete top-N rows
    results = []    # will store aggregated stats per group
    
    group_cols = ["jahr", "geschlecht", "altersklasse", "disziplin"]
    
    for group_vals, group_df in data.groupby(group_cols):
        # Sort by iaaf_score descending (best first)
        sorted_df = group_df.sort_values("iaaf_score", ascending=False)
        top_n = sorted_df.head(num_entries)
        
        if len(top_n) == num_entries:
            # Save raw rows for overall stats later
            top_rows.append(top_n)
            
            # Compute per-group stats
            results.append({
                "jahr": group_vals[0],
                "geschlecht": group_vals[1],
                "altersklasse": group_vals[2],
                "disziplin": group_vals[3],
                "count_top": num_entries,
                "mean_top": top_n["iaaf_score"].mean(),
                "std_top": top_n["iaaf_score"].std()
            })
    
    # Convert results to a DataFrame
    top_stats = pd.DataFrame(results)
    
    # Combine all top-N rows for yearly overall stats
    top_raw = pd.concat(top_rows, ignore_index=True) if top_rows else pd.DataFrame()
    
    return top_stats, top_raw

# Example usage:
# top_stats, top_raw = collect_top_entries(data, num_entries=10)
