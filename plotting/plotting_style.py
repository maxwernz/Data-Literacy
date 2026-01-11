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
    _plt.rcParams.update({"figure.dpi": 300})
    _plt.rcParams.update({"savefig.format": "pdf"})
    _plt.rcParams.update({"savefig.bbox": "tight"})
    _plt.rcParams.update({"grid.linestyle": "-", "grid.alpha": 0.7})
    _plt.rcParams.update(cycler.cycler(color=palettes.tue_plot))

def increase_figsze(factor: float):
    width = _plt.rcParams["figure.figsize"][0] * factor
    height = _plt.rcParams["figure.figsize"][1] * factor
    return {"figure.figsize": (width, height)}



_plt.rcParams.update(bundles.icml2024())
plt_settings()
ensure_latex_on_path()

def __getattr__(name):
    return getattr(_plt, name)


def __dir__():
    return dir(_plt)


