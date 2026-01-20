import streamlit as st
import pandas as pd
import sys
import os
import matplotlib.pyplot as main_plt # Import standard matplotlib to clear figures if needed

# Add project root to path to allow imports from util and plotting
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

import util
import plotting.plotting_style as plt
from plotting.plotting_style import rgb

plt.rcParams.update(plt.bundles.beamer_moml())
plt.rcParams.update({"figure.figsize": (6, 3)})

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
st.subheader("Performance Trends")

plot_col1, plot_col2 = st.columns([1, 3])

with plot_col1:
    y_axis_option = st.radio(
        "Y-Axis Metric",
        ["IAAF Score", "Performance (Leistung)"],
        index=0
    )
    
    aggregation = st.selectbox(
        "Aggregation per Year",
        ["Mean", "Median", "Max (Best)", "None (Scatter)"]
    )

    # Check for unit consistency if Performance is selected
    if y_axis_option == "Performance (Leistung)":
        # Check measurement types
        types = set()
        for d in selected_disciplines:
            key = util.get_measurement_key(d)
            types.add(key)
        
        if len(types) > 1:
            st.error("⚠️ Warning: You have selected disciplines with different units (Time vs Distance). Please select only one type or switch to 'IAAF Score'.")
            st.stop()

# --- 6. Plotting Logic ---
metric_col = 'iaaf_score' if y_axis_option == "IAAF Score" else 'leistung'

# Determine Unit for Y-Axis Label
unit_info = ""
if y_axis_option == "Performance (Leistung)":
    m_type = util.get_measurement_key(selected_disciplines[0])
    unit_map = {"time": "in Seconds [s]", "meter": "in Meters [m]", "points": "Points"}
    unit_info = f" {unit_map.get(m_type, '')}"
else:
    unit_info = " (IAAF Points)"

# Display current configuration in a nice info box
st.info(f"**Plotting:** {aggregation} of **{y_axis_option}**{unit_info}")

# Prepare figure
fig, ax = plt.subplots()

if aggregation != "None (Scatter)":
    # Aggregated Plot
    agg_func = aggregation.split()[0].lower() # mean, median, max
    
    # Group by Year and (optionally) Discipline/Gender/Age to create lines
    groups = filtered_df.groupby(['jahr', 'disziplin', 'geschlecht'])[metric_col].agg(agg_func).reset_index()
    
    for (disc, gender), group_data in groups.groupby(['disziplin', 'geschlecht']):
        label = f"{disc} ({gender})"
        ax.plot(group_data['jahr'], group_data[metric_col], label=label, marker='.')

else:
    # Scatter Plot
    if len(filtered_df) > 5000:
        st.caption("⚠️ Downsampling data for scatter plot (max 5000 points displayed)")
        plot_data = filtered_df.sample(5000)
    else:
        plot_data = filtered_df
        
    for (disc, gender), group_data in plot_data.groupby(['disziplin', 'geschlecht']):
        label = f"{disc} ({gender})"
        ax.scatter(group_data['jahr'], group_data[metric_col], label=label, alpha=0.6, s=10)

# Styling
ax.set_xlabel("Year")
ax.set_ylabel(f"{y_axis_option}{unit_info}")
ax.set_title(f"{aggregation} {y_axis_option} over Time")
if len(selected_disciplines) <= 10:
    ax.legend()
else:
    st.caption("Legend hidden due to too many categories.")

ax.grid(True, alpha=0.3)

# Render Plot
st.pyplot(fig)

# --- 7. Data Table ---
with st.expander("View Raw Data"):
    st.dataframe(filtered_df[['jahr', 'geschlecht', 'altersklasse', 'disziplin', 'name', 'leistung', 'iaaf_score', 'ort', 'datum']])
