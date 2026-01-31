import streamlit as st
import pandas as pd
import sys
import os
import plotly.express as px
import plotly.graph_objects as go

# Add project root to path to allow imports from util
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

import util

# Page Config
st.set_page_config(
    page_title="DLV Athletics Data Explorer",
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

# Filter data for Discipline selection context
temp_filtered = df[
    (df['altersklasse'].isin(selected_ages)) & 
    (df['geschlecht'].isin(selected_genders))
]

# 2.3 Discipline Filter
available_disciplines = sorted(temp_filtered['disziplin'].unique())
selected_disciplines = st.sidebar.multiselect(
    "Select Disciplines",
    options=available_disciplines,
    default=available_disciplines[:1] if available_disciplines else None
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

# Shared Plotting Config
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
tab_trends, tab_dist, tab_data, tab_athlete = st.tabs(["📈 Trends over Time", "📊 Distributions", "📄 Raw Data", "👤 Athlete Search"])

# === TAB 1: Trends ===
with tab_trends:
    st.subheader("Performance Trends")
    
    agg_col, chart_col = st.columns([1, 4])
    
    with agg_col:
        aggregation = st.selectbox(
            "Aggregation",
            ["Mean", "Median", "Max (Best)", "None (Scatter)"],
            help="Choose how to summarize data per year."
        )

    with chart_col:
        if aggregation != "None (Scatter)":
            # Aggregated Plot
            agg_func = aggregation.split()[0].lower() # mean, median, max
            
            # Group by Year, Discipline, Gender
            groups = filtered_df.groupby(['jahr', 'disziplin', 'geschlecht'])[metric_col].agg(agg_func).reset_index()
            
            fig = px.line(
                groups, 
                x='jahr', 
                y=metric_col, 
                color='disziplin', 
                line_dash='geschlecht',
                markers=True,
                title=f"{aggregation} {y_axis_option} per Year",
                labels={metric_col: f"{y_axis_option}{unit_info}", "jahr": "Year"}
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

# === TAB 3: Data ===
with tab_data:
    st.subheader("Raw Data View")
    st.dataframe(filtered_df[['jahr', 'geschlecht', 'altersklasse', 'disziplin', 'name', 'leistung', 'iaaf_score', 'ort', 'datum', 'verein']])

# === TAB 4: Athlete Search ===
with tab_athlete:
    st.subheader("Athlete Career Explorer")
    st.markdown("Search for an athlete to visualize their career progression.")
    
    # 1. Search Box
    # Get all unique names from the *full* dataset (not filtered by sidebar) to allow global search
    all_names = sorted(df['name'].dropna().unique())
    selected_name = st.selectbox("Search Athlete Name", options=[""] + all_names)
    
    if selected_name:
        # Filter for this athlete
        athlete_df = df[df['name'] == selected_name].sort_values('jahr')
        
        if athlete_df.empty:
            st.warning("No data found for this athlete.")
        else:
            # 2. Athlete Metadata
            # Get most frequent club and birth year
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
            # Add scatter points on top to make single-year data visible
            fig_career.add_traces(
                px.scatter(
                    athlete_df, x='jahr', y='iaaf_score', color='disziplin'
                ).data
            )
            st.plotly_chart(fig_career, use_container_width=True)
            
            # 4. Detailed Data
            st.markdown("### Detailed Results")
            st.dataframe(athlete_df[['jahr', 'disziplin', 'leistung', 'iaaf_score', 'altersklasse', 'ort', 'datum', 'verein']])