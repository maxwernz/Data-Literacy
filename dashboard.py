import streamlit as st
import pandas as pd
import sys
import os
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from pathlib import Path

import lib.util as util
from lib.iaaf_points import score_calculator

# Page Config
st.set_page_config(
    page_title="Faster, Higher, Further Apart: Breakdown of the Top Rankings in German Athletics Over the Last 25 Years",
    page_icon="🏃",
    layout="wide"
)

# --- 1. Data Loading ---
@st.cache_data
def load_dataset():
    """Loads the dataset using util.py"""
    # Load data with default filters (funded disciplines)
    return util.load_data(filter=False)

try:
    df = load_dataset()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# --- 2. Sidebar Controls ---
st.sidebar.title("Configuration")

# 2.1 Age Group Filter
all_ages = sorted(df['altersklasse'].unique())
selected_ages = st.sidebar.multiselect(
    "Select Age Groups",
    options=all_ages,
    default=all_ages
)

# 2.2 Gender Filter
all_genders = sorted(df['geschlecht'].unique())
selected_genders = st.sidebar.multiselect(
    "Select Gender",
    options=all_genders,
    default=all_genders
)

# 2.3 Discipline Group Filter (NEW)
# Ensure 'group' column exists (util.py adds it)
all_groups = sorted(df['group'].dropna().unique())
selected_groups = st.sidebar.multiselect(
    "Select Discipline Groups",
    options=all_groups,
    default=all_groups
)

# Filter data for Discipline selection context
# We filter by Age, Gender AND Group to narrow down the specific disciplines
temp_filtered = df[
    (df['altersklasse'].isin(selected_ages)) & 
    (df['geschlecht'].isin(selected_genders)) &
    (df['group'].isin(selected_groups))
]

# 2.4 Discipline Filter
available_disciplines = sorted(temp_filtered['disziplin'].unique())
selected_disciplines = st.sidebar.multiselect(
    "Select Disciplines",
    options=available_disciplines,
    default="100 m" if "100 m" in available_disciplines else (available_disciplines[0] if available_disciplines else None)
)

# --- 3. Main Data Filtering ---
filtered_df = df[
    (df['altersklasse'].isin(selected_ages)) & 
    (df['geschlecht'].isin(selected_genders)) & 
    (df['disziplin'].isin(selected_disciplines))
]

# --- 4. Main Content Area ---
st.title("🏃 German Athletics Data Analysis")
st.markdown("Interactive exploration of the DLV Bestenlisten data.")

# Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Data Points", f"{len(filtered_df):,}")
col2.metric("Disciplines", len(selected_disciplines))
col3.metric("Year Range", f"{filtered_df['jahr'].min()} - {filtered_df['jahr'].max()}")

if filtered_df.empty:
    st.warning("No data found for the current selection. Please adjust filters.")
    st.stop()

# --- 5. Plotting Configuration ---
st.divider()

# Shared Plotting Config (for Tabs 1 & 2)
col_conf1, col_conf2 = st.columns([1, 3])
with col_conf1:
    y_axis_option = st.radio(
        "Y-Axis Metric",
        ["IAAF Score", "Performance (Leistung)"],
        index=0
    )
    
    # Check for unit consistency if Performance is selected
    metric_col = 'iaaf_score' if y_axis_option == "IAAF Score" else 'leistung'
    unit_info = " (Points)"
    
    if y_axis_option == "Performance (Leistung)":
        # Check measurement types
        types = set()
        for d in selected_disciplines:
            key = util.get_measurement_key(d)
            types.add(key)
        
        if len(types) > 1:
            st.error("⚠️ Warning: Mixed units (Time vs Distance). Please select only one type or switch to 'IAAF Score'.")
            st.stop()
        
        m_type = util.get_measurement_key(selected_disciplines[0])
        unit_map = {"time": " (s)", "meter": " (m)", "points": " (pts)"}
        unit_info = unit_map.get(m_type, "")

# --- 6. Tabs for Different Views ---
tab_trends, tab_dist, tab_radar, tab_athlete, tab_calc, tab_depth, tab_data = st.tabs([
    "📈 Trends", 
    "📊 Distributions", 
    "🕸️ Period Comparison", 
    "👤 Athlete Search",
    "🧮 Score Calculator",
    "🔥 Depth",
    "📄 Raw Data"
])

# === TAB 1: Trends ===
with tab_trends:
    st.subheader("Performance Trends")
    
    agg_col, chart_col = st.columns([1, 4])
    
    with agg_col:
        aggregation = st.selectbox(
            "Aggregation",
            ["Mean", "Median", "Max (Best)", "Gap (Top 3 - Low 3)", "None (Scatter)"],
            help="Choose how to summarize data per year. 'Gap' is the difference between the average of the Top 3 and Bottom 3 performers."
        )

    with chart_col:
        if aggregation != "None (Scatter)":
            # Aggregated Plot
            
            if aggregation == "Gap (Top 3 - Low 3)":
                # Custom Gap Calculation
                def gap_func(x):
                    # Ensure numeric
                    vals = pd.to_numeric(x, errors='coerce').dropna()
                    if len(vals) < 6: 
                        return np.nan
                    return vals.nlargest(3).mean() - vals.nsmallest(3).mean()

                # Group and Apply
                # We need to apply to metric_col
                # For apply to work nicely with multiple grouping keys, we group and then apply to the series
                groups = filtered_df.groupby(['jahr', 'disziplin', 'geschlecht'])[metric_col].apply(gap_func).reset_index(name=metric_col)
                
                title_text = f"Performance Gap (Top 3 - Low 3) per Year"
                y_label = f"Gap {unit_info}"
            
            else:
                # Standard Aggregations
                agg_func = aggregation.split()[0].lower() # mean, median, max
                groups = filtered_df.groupby(['jahr', 'disziplin', 'geschlecht'])[metric_col].agg(agg_func).reset_index()
                title_text = f"{aggregation} {y_axis_option} per Year"
                y_label = f"{y_axis_option}{unit_info}"
            
            fig = px.line(
                groups, 
                x='jahr', 
                y=metric_col, 
                color='disziplin', 
                line_dash='geschlecht',
                markers=True,
                title=title_text,
                labels={metric_col: y_label, "jahr": "Year"}
            )
            st.plotly_chart(fig, use_container_width=True)

        else:
            # Scatter Plot
            if len(filtered_df) > 5000:
                st.caption("⚠️ Downsampling data for scatter plot (max 5000 points displayed)")
                plot_data = filtered_df.sample(5000)
            else:
                plot_data = filtered_df
            
            fig = px.scatter(
                plot_data, 
                x='jahr', 
                y=metric_col, 
                color='disziplin', 
                symbol='geschlecht',
                hover_data=['name', 'verein', 'ort', 'datum'],
                title=f"Individual {y_axis_option} per Year",
                labels={metric_col: f"{y_axis_option}{unit_info}", "jahr": "Year"}
            )
            st.plotly_chart(fig, use_container_width=True)

# === TAB 2: Distributions ===
with tab_dist:
    st.subheader("Performance Distributions")
    st.markdown("Analyze the spread of performances within each year.")
    
    dist_type = st.radio("Chart Type", ["Box Plot", "Violin Plot"], horizontal=True)
    
    if dist_type == "Box Plot":
        fig = px.box(
            filtered_df, 
            x='jahr', 
            y=metric_col, 
            color='disziplin',
            title=f"Distribution of {y_axis_option} by Year",
            labels={metric_col: f"{y_axis_option}{unit_info}", "jahr": "Year"}
        )
    else:
        fig = px.violin(
            filtered_df, 
            x='jahr', 
            y=metric_col, 
            color='disziplin',
            box=True, # Show box inside violin
            points=False, # Don't show all points to keep it clean
            title=f"Distribution of {y_axis_option} by Year",
            labels={metric_col: f"{y_axis_option}{unit_info}", "jahr": "Year"}
        )
    
    st.plotly_chart(fig, use_container_width=True)

# === TAB 3: Period Comparison (Radar) ===
with tab_radar:
    st.subheader("Period Comparison (Radar Plot)")
    st.markdown("Compare metrics between two time periods to analyze structural changes in performance.")
    
    # Configuration for Radar
    r_col1, r_col2 = st.columns(2)
    
    with r_col1:
        st.markdown("#### Period 1 (Baseline)")
        p1_start, p1_end = st.slider("Select Range", 2001, 2024, (2001, 2004), key="p1")
        
    with r_col2:
        st.markdown("#### Period 2 (Comparison)")
        p2_start, p2_end = st.slider("Select Range", 2001, 2024, (2021, 2024), key="p2")

    # Toggle for Split/Aggregate
    radar_mode = st.radio(
        "Comparison Mode", 
        ["Aggregate Selected", "Separate by Discipline"], 
        horizontal=True,
        help="Choose 'Separate' to see one trace per discipline. Choose 'Aggregate' to combine all selected disciplines into one trace."
    )

    # Helper to calculate metrics
    def get_radar_metrics(data_slice):
        if len(data_slice) < 10:
            return None
        
        # Ensure int for ranking
        data_slice = data_slice.copy()
        data_slice['iaaf_score'] = pd.to_numeric(data_slice['iaaf_score'], errors='coerce')
        data_slice = data_slice.dropna(subset=['iaaf_score'])
        
        if data_slice.empty: return None

        # Metrics over the whole slice
        mean_score = data_slice['iaaf_score'].mean()
        median_score = data_slice['iaaf_score'].median()
        std_dev = data_slice['iaaf_score'].std()
        if pd.isna(std_dev): std_dev = 0
        
        top1_score = data_slice['iaaf_score'].max()
        
        # Gap Top 3 - Low 3 (Averaged per Year for robustness)
        yearly_gaps = []
        for y in data_slice['jahr'].unique():
            y_data = data_slice[data_slice['jahr'] == y]
            if len(y_data) >= 6:
                gap = y_data['iaaf_score'].nlargest(3).mean() - y_data['iaaf_score'].nsmallest(3).mean()
                yearly_gaps.append(gap)
        
        gap_top3_low3 = np.mean(yearly_gaps) if yearly_gaps else 0
        
        return {
            'Mean': mean_score,
            'Median': median_score,
            'Std Dev': std_dev,
            'Top 1 (Max)': top1_score,
            'Gap Top3-Low3': gap_top3_low3
        }

    # Filter Data for Radar (using global filters)
    radar_df = df[
        (df['altersklasse'].isin(selected_ages)) &
        (df['geschlecht'].isin(selected_genders)) &
        (df['disziplin'].isin(selected_disciplines))
    ]
    
    # Prepare data for plotting
    # Structure: List of dicts {'label': str, 'p1_df': df, 'p2_df': df}
    plot_items = []
    
    if radar_mode == "Aggregate Selected":
        plot_items.append({
            'label': "Aggregate",
            'p1_df': radar_df[(radar_df['jahr'] >= p1_start) & (radar_df['jahr'] <= p1_end)],
            'p2_df': radar_df[(radar_df['jahr'] >= p2_start) & (radar_df['jahr'] <= p2_end)]
        })
    else:
        # Separate by discipline
        active_disciplines = sorted(radar_df['disziplin'].unique())
        for d in active_disciplines:
            d_df = radar_df[radar_df['disziplin'] == d]
            plot_items.append({
                'label': d,
                'p1_df': d_df[(d_df['jahr'] >= p1_start) & (d_df['jahr'] <= p1_end)],
                'p2_df': d_df[(d_df['jahr'] >= p2_start) & (d_df['jahr'] <= p2_end)]
            })
    
    # Process Metrics
    final_traces = []
    abs_metrics_rows = []
    categories = ['Mean', 'Median', 'Top 1 (Max)', 'Std Dev', 'Gap Top3-Low3']
    
    for item in plot_items:
        m_p1 = get_radar_metrics(item['p1_df'])
        m_p2 = get_radar_metrics(item['p2_df'])
        
        if m_p1 and m_p2:
            # Add to Absolute Metrics Table
            abs_metrics_rows.append({'Context': f"{item['label']} (P1)", **m_p1})
            abs_metrics_rows.append({'Context': f"{item['label']} (P2)", **m_p2})
            
            # Calculate Ratios (P2 / P1)
            values = []
            
            # 1. Mean (Higher is better)
            values.append(m_p2['Mean'] / m_p1['Mean'] if m_p1['Mean'] != 0 else 0)
            # 2. Median (Higher is better)
            values.append(m_p2['Median'] / m_p1['Median'] if m_p1['Median'] != 0 else 0)
            # 3. Top 1 (Higher is better)
            values.append(m_p2['Top 1 (Max)'] / m_p1['Top 1 (Max)'] if m_p1['Top 1 (Max)'] != 0 else 0)
            
            # 4. Std Dev (Lower is better/tighter -> Invert: Old/New)
            if m_p2['Std Dev'] == 0:
                val_std = 1.0 
            else:
                val_std = m_p1['Std Dev'] / m_p2['Std Dev']
            values.append(val_std)
            
            # 5. Gap Top3-Low3 (Lower is better/tighter -> Invert: Old/New)
            if m_p2['Gap Top3-Low3'] == 0:
                val_gap = 1.0
            else:
                val_gap = m_p1['Gap Top3-Low3'] / m_p2['Gap Top3-Low3']
            values.append(val_gap)
            
            final_traces.append({
                'label': item['label'],
                'values': values
            })

    if final_traces:
        fig_radar = go.Figure()

        # Add Baseline Trace (Reference circle at 1.0)
        fig_radar.add_trace(go.Scatterpolar(
            r=[1.0] * 6, # Close loop
            theta=categories + [categories[0]],
            mode='lines',
            name='Baseline (No Change)',
            line_color='gray',
            line_dash='dot',
            opacity=0.5,
            hoverinfo='none'
        ))
        
        # Add Comparison Traces
        for trace in final_traces:
            # Determine styling
            # If Aggregate: Filled area. If Separate: Lines only (to avoid occlusion)
            fill_mode = 'toself' if radar_mode == "Aggregate Selected" else 'none'
            
            fig_radar.add_trace(go.Scatterpolar(
                r=trace['values'] + [trace['values'][0]], # Close loop
                theta=categories + [categories[0]],
                fill=fill_mode,
                name=f"{trace['label']} Change"
            ))

        # Dynamic Range
        # Find max value to scale axis nicely
        all_vals = [v for t in final_traces for v in t['values']]
        max_val = max(all_vals) if all_vals else 1.2
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max(max_val * 1.1, 1.2)]
                )
            ),
            title=f"Relative Change ({radar_mode})",
            showlegend=True
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
        
        # Metrics Table
        st.markdown("### Absolute Metrics")
        st.dataframe(pd.DataFrame(abs_metrics_rows).set_index('Context').style.format("{:.2f}"))
        
        st.info("ℹ️ **Interpretation:** \n" 
                "- **Values > 1.0**: Improvement (Higher Score) or Higher Density (Lower StdDev/Gap).\n" 
                "- **Values < 1.0**: Decline or Lower Density.\n"
                "- **Gap (Top 3 - Low 3)**: The average score difference between the top 3 and bottom 3 athletes. Smaller gap = Higher Density.")        
    else:
        st.warning("Insufficient data in the selected periods/disciplines to calculate metrics.")


# === TAB 4: Athlete Search ===
with tab_athlete:
    st.subheader("Athlete Career Explorer")
    st.markdown("Search for an athlete to visualize their career progression.")
    
    # 1. Search Box
    # Get all unique names from the *full* dataset
    all_names = sorted(df['name'].dropna().unique())
    selected_name = st.selectbox("Search Athlete Name", options=[""] + all_names)
    
    if selected_name:
        # Filter for this athlete
        athlete_df = df[df['name'] == selected_name].sort_values('jahr')
        
        if athlete_df.empty:
            st.warning("No data found for this athlete.")
        else:
            # 2. Athlete Metadata
            top_club = athlete_df['verein'].mode()[0] if not athlete_df['verein'].mode().empty else "Unknown"
            birth_year = int(athlete_df['geburtsjahr'].iloc[0]) if pd.notna(athlete_df['geburtsjahr'].iloc[0]) else "Unknown"
            
            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("Club (Most Frequent)", top_club)
            m_col2.metric("Year of Birth", str(birth_year))
            m_col3.metric("Total Entries", len(athlete_df))
            
            # 3. Career Plot
            st.markdown("### Career Progression (IAAF Score)")
            fig_career = px.line(
                athlete_df, 
                x='jahr', 
                y='iaaf_score', 
                color='disziplin',
                markers=True,
                hover_data=['leistung', 'ort', 'datum', 'altersklasse'],
                title=f"Career Progression: {selected_name}",
                labels={'iaaf_score': "IAAF Score", 'jahr': "Year"}
            )
            # Add scatter points
            fig_career.add_traces(
                px.scatter(
                    athlete_df, x='jahr', y='iaaf_score', color='disziplin'
                ).data
            )
            st.plotly_chart(fig_career, use_container_width=True)
            
            # 4. Detailed Data
            st.markdown("### Detailed Results")
            st.dataframe(athlete_df[['jahr', 'disziplin', 'leistung', 'iaaf_score', 'altersklasse', 'ort', 'datum', 'verein']])

# === TAB 5: Score Calculator ===
with tab_calc:
    st.subheader("🧮 IAAF Score Calculator (2025 Edition)")
    
    if score_calculator is None:
        st.error("Score calculator module not found.")
    else:
        try:
            coeffs = score_calculator.get_iaaf_coeffs()
            
            c_col1, c_col2 = st.columns(2)
            
            with c_col1:
                gender_input = st.radio("Gender", ["Male", "Female"], horizontal=True)
                gender_key = "men" if gender_input == "Male" else "women"
                
                # Filter disciplines available in DISCIPLINE_TO_EVENT
                valid_disciplines = [d for d in all_groups + available_disciplines if d in score_calculator.DISCIPLINE_TO_EVENT]
                # Better: Use the raw CSV discipline names that map to the calculator's keys
                valid_csv_disciplines = sorted(score_calculator.DISCIPLINE_TO_EVENT.keys())
                
                # make 100 m default if available
                if "100 m" in valid_csv_disciplines:
                    default_disc = "100 m"
                else:
                    default_disc = valid_csv_disciplines[0] if valid_csv_disciplines else None
                disc_input = st.selectbox("Discipline", valid_csv_disciplines, index=valid_csv_disciplines.index(default_disc) if default_disc in valid_csv_disciplines else 0)
                
                # Determine unit hint
                event_code = score_calculator.DISCIPLINE_TO_EVENT[disc_input]
                m_key = util.get_measurement_key(disc_input)
                unit_hint = "(Seconds)" if m_key == "time" else "(Meters)" if m_key == "meter" else "(Points)"
                
                perf_input = st.text_input(f"Performance {unit_hint}", value="10.00")
                
            with c_col2:
                st.markdown("### Result")
                if st.button("Calculate"):
                    # Convert input to float (handling time format mm:ss.ms if possible via util)
                    
                    val = None
                    if m_key == "time":
                        # Try simple float first, then util converter
                        try:
                            val = float(perf_input)
                        except ValueError:
                            val = util.convert_time_to_seconds(perf_input)
                    else:
                        try:
                            val = float(perf_input.replace(',', '.'))
                        except ValueError:
                            val = None
                            
                    if val is not None:
                        # Call calculator
                        try:
                            score = score_calculator.score_from_mark(gender_key, event_code, val, coeffs)
                            st.metric("IAAF Score", f"{score} pts")
                            st.success(f"Calculated for {disc_input} ({gender_input}): {val} -> {score}")
                        except Exception as e:
                            st.error(f"Calculation error: {e}")
                    else:
                        st.error("Invalid performance format. Please check your input.")

        except Exception as e:
            st.error(f"Failed to load coefficients: {e}")

# === TAB 6: Competition Depth ===
with tab_depth:
    st.subheader("Competition Depth Heatmap")
    st.markdown("Number of athletes per discipline and year.")

    # Group by Discipline and Year to get counts
    depth_data = filtered_df.groupby(['disziplin', 'jahr']).size().reset_index(name='count')
    
    # Create Heatmap
    pivot_depth = depth_data.pivot(index='disziplin', columns='jahr', values='count').fillna(0)
    
    fig_depth = px.imshow(
        pivot_depth,
        labels=dict(x="Year", y="Discipline", color="Count"),
        x=pivot_depth.columns,
        y=pivot_depth.index,
        aspect="auto",
        title="Number of Participants by Discipline and Year"
    )
    
    st.plotly_chart(fig_depth, use_container_width=True)

# === TAB 7: Data ===
with tab_data:
    st.subheader("Raw Data View")
    st.dataframe(filtered_df[['jahr', 'geschlecht', 'altersklasse', 'disziplin', 'name', 'leistung', 'iaaf_score', 'ort', 'datum', 'verein']])
