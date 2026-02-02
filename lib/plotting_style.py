import matplotlib.pyplot as _plt
from tueplots import bundles, figsizes, fontsizes, axes, cycler
from tueplots.constants.color import rgb
from tueplots.constants import markers
from tueplots.constants.color import palettes
import os
import shutil

def ensure_latex_on_path():
    if shutil.which("latex") is not None:
        return

    # typische Installationspfade (je nach OS anpassen)
    candidates = [
        "/usr/bin",
        "/usr/local/bin",
        "/Library/TeX/texbin",      # macOS (MacTeX)
        "/usr/texbin",
    ]

    for p in candidates:
        if os.path.exists(os.path.join(p, "latex")):
            os.environ["PATH"] = p + os.pathsep + os.environ["PATH"]
            return
    
    _plt.rcParams.update({"text.usetex": False})

def plt_settings():
    _plt.rcParams.update(axes.lines())
    _plt.rcParams.update({"figure.dpi": 200})
    _plt.rcParams.update({"savefig.format": "pdf"})
    _plt.rcParams.update({"savefig.bbox": "tight"})
    _plt.rcParams.update({"grid.linestyle": "-", "grid.alpha": 0.7})
    _plt.rcParams.update(cycler.cycler(color=palettes.tue_plot))

def increase_figsize(factor: float):
    width = _plt.rcParams["figure.figsize"][0] * factor
    height = _plt.rcParams["figure.figsize"][1] * factor
    fontsize = _plt.rcParams['font.size'] * factor
    axes_labelsize = _plt.rcParams['axes.labelsize'] * factor
    legend_fontsize = _plt.rcParams['legend.fontsize'] * factor
    xtick_labelsize = _plt.rcParams['xtick.labelsize'] * factor
    ytick_labelsize = _plt.rcParams['ytick.labelsize'] * factor
    axes_titlesize = _plt.rcParams['axes.titlesize'] * factor

    return {"figure.figsize": (width, height),
            "font.size": fontsize,
            "axes.labelsize": axes_labelsize,
            "legend.fontsize": legend_fontsize,
            "xtick.labelsize": xtick_labelsize,
            "ytick.labelsize": ytick_labelsize,
            "axes.titlesize": axes_titlesize
            }

def set_column(column="half", nrows=1, cols=1):
    if column == "half":
        _plt.rcParams.update(bundles.icml2024(column="half", nrows=nrows, ncols=cols))
    elif column == "full":
        _plt.rcParams.update(bundles.icml2024(column="full", nrows=nrows, ncols=cols))
    else:
        raise ValueError("Column must be 'half' or 'full'")
    
    ensure_latex_on_path()

# Project root is one level up from the 'lib' directory
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_PLOTS_DIR = os.path.join(_PROJECT_ROOT, "Plots")

def savefig(fname: str, category=None, **kwargs):
    if category is not None:
        target_dir = os.path.join(_PLOTS_DIR, category)
    else:
        target_dir = _PLOTS_DIR
    
    os.makedirs(target_dir, exist_ok=True)
    full_path = os.path.join(target_dir, fname)
    _plt.savefig(full_path, dpi=300, **kwargs)



_plt.rcParams.update(bundles.icml2024(column="full"))
plt_settings()
ensure_latex_on_path()

def __getattr__(name):
    return getattr(_plt, name)


def __dir__():
    return dir(_plt)


