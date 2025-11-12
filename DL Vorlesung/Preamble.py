# imports
import sys
from pathlib import Path

from matplotlib import pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
# for plotting
from tueplots import bundles
from tueplots.constants.color import rgb

plt.rcParams.update(bundles.beamer_moml())
plt.rcParams.update({"figure.dpi": 200})
# plt.rcParams.update({'font.sans-serif': ['DejaVu Sans Mono'],'figure.dpi': 200})

# Get my_package directory path from Notebook
parent_dir = str(Path().resolve().parents[1])

# Add to sys.path
sys.path.insert(0, parent_dir)

cmap_wd = LinearSegmentedColormap.from_list("ow", ['w', rgb.tue_dark], N=1024)
cmap_wo = LinearSegmentedColormap.from_list("ow", ['w', rgb.tue_orange], N=1024)
cmap_wb = LinearSegmentedColormap.from_list("ow", ['w', rgb.tue_blue], N=1024)  
cmap_wg = LinearSegmentedColormap.from_list("ow", ['w', rgb.tue_green], N=1024)
cmap_wr = LinearSegmentedColormap.from_list("ow", ['w', rgb.tue_red], N=1024)

# plotly rgb color strings:
def color_from_rgb(color):
    return f"rgb({int(255*color[0])}, {int(255*color[1])}, {int(255*color[2])})"


plt_width, plt_height = plt.rcParams["figure.figsize"]
dpi = plt.rcParams["figure.dpi"]

# Define a custom template for plotly
custom_template = dict(
    layout=dict(
        # Background colors
        plot_bgcolor="white",
        paper_bgcolor="white",
        # Font settings
        font=dict(
            family="Roboto Condensed Light, sans-serif", size=20, color=color_from_rgb(rgb.tue_dark)
        ),
        # Axis styling
        xaxis=dict(
            showgrid=True,
            gridwidth=0.5,
            gridcolor=color_from_rgb(rgb.tue_gray),
            zeroline=True,
            zerolinewidth=1,
            zerolinecolor=color_from_rgb(rgb.tue_dark),
            showline=True,
            linewidth=1,
            mirror=True,
            linecolor=color_from_rgb(rgb.tue_dark),
            tickfont=dict(size=18),
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=0.5,
            gridcolor=color_from_rgb(rgb.tue_gray),
            zeroline=True,
            zerolinewidth=1,
            zerolinecolor=color_from_rgb(rgb.tue_dark),
            showline=True,
            linewidth=1,
            mirror=True,
            linecolor=color_from_rgb(rgb.tue_dark),
            tickfont=dict(size=18),
        ),
        # Legend styling
        showlegend=True,
        legend=dict(
            bgcolor="white",
            bordercolor=color_from_rgb(rgb.tue_dark),
            borderwidth=1,
            font=dict(size=18),
        ),
        # Margins
        margin=dict(l=60, r=30, t=60, b=60),
    )
)

# Calculate plotly dimensions from matplotlib settings
plotly_width = int(plt_width * dpi)
plotly_height = int(plt_height * dpi)