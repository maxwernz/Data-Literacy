# Data Literacy Project - Analyse von Leichtathletik-Daten

## Projektübersicht

Dieses Projekt beschäftigt sich mit der Analyse von Leistungsdaten der deutschen Leichtathletik (DLV Bestenlisten). Ziel ist es, Trends, Leistungslücken und den Einfluss von Ereignissen wie der COVID-19-Pandemie auf die sportliche Leistung zu untersuchen. Die Analyse umfasst die Datenextraktion aus PDF-Berichten, die Bereinigung und Standardisierung der Daten, die Berechnung von IAAF/WA-Punkten sowie die Visualisierung der Ergebnisse.

## Verzeichnisstruktur

Die Codebasis ist wie folgt strukturiert:

- **`data_csv/`**: Enthält die verarbeiteten Daten im CSV-Format.
  - `final_Data_iaaf_scores_neu.csv`: Der bereinigte Hauptdatensatz mit IAAF-Punkten.
  - `getCSV.ipynb`: Jupyter Notebook zur Extraktion der Daten aus den Roh-PDFs.
- **`Data_pdf/`**: Rohdaten. Enthält Unterordner (z.B. `data01-17/`) mit den ursprünglichen PDF-Dateien der DLV Bestenlisten.
- **`plotting/`**: Modul für das Plotting-Setup.
  - `plotting_style.py`: Konfiguriert `matplotlib` mit dem Corporate Design der Universität Tübingen (`tueplots`) und stellt Hilfsfunktionen bereit.
- **`report/`**: LaTeX-Quellcode für den finalen Projektbericht.
- **`util.py`**: Zentrales Utility-Modul zum Laden und Verarbeiten der Daten.
- **`Plots/`**: Automatisch generierter Ordner, in dem alle mit dem Plotting-Modul erstellten Grafiken gespeichert werden.
- **User-Ordner (`erik/`, `Luca/`, `mattis/`, `max/`)**: Persönliche Arbeitsbereiche für explorative Analysen und Notebooks.

## Daten laden (`util.py`)

Das Modul `util.py` stellt die zentrale Funktion `load_data` bereit, um die Daten konsistent zu laden. Dabei werden automatisch:

1.  Leistungen in ein einheitliches numerisches Format konvertiert (Zeitangaben in Sekunden, Weiten in Meter, Punkte als Integer).
2.  Winddaten in numerische Werte umgewandelt.
3.  **Filterung:** Standardmäßig werden nur relevante Altersklassen und Disziplinen geladen, die den Förderrichtlinien entsprechen.

### Verwendung

Um die Daten in einem Jupyter Notebook oder Skript zu laden, muss zunächst der Pfad zum Projektverzeichnis bekannt gemacht werden:

```python
import sys
import os
# Füge das Root-Verzeichnis zum Pfad hinzu (je nach Tiefe der Ordnerstruktur anpassen, z.B. "../../")
sys.path.append(os.path.abspath("../.."))

import util

# Laden der gefilterten Daten (Standard)
# Enthält nur geförderte Disziplinen und Altersklassen (U18, U20, U23, Erwachsene)
df = util.load_data()

# Laden aller Daten (ohne Filter)
df_all = util.load_data(filter=False)

# Laden inkl. jüngerer Jahrgänge (wenn im Filter implementiert, z.B. 14, 16)
df_youth = util.load_data(youth=True)
```

Die Filterlogik basiert auf den Definitionen für geförderte Disziplinen (Sprint, Lauf, Wurf, Sprung, Mehrkampf) pro Altersklasse.

## Plotting (`plotting/plotting_style.py`)

Für einheitliche und publikationsreife Grafiken wird ein eigenes Plotting-Modul verwendet, das auf `matplotlib` und `tueplots` basiert.

### Einrichtung

Importiere das Modul wie folgt. Es ist wichtig, `matplotlib.pyplot` **nicht** separat zu importieren (oder den Import danach zu platzieren), damit die Einstellungen übernommen werden.

```python
import plotting.plotting_style as plt
from plotting.plotting_style import rgb # Für Farben im Tübinger Design
```

### Verwendung

Das Modul verhält sich weitgehend wie `matplotlib.pyplot`.

**Wichtige Funktionen:**

- **Automatische Styles:** Das Layout (Schriftarten, Größen, Raster) ist automatisch für wissenschaftliche Paper (ICML-Style) konfiguriert.
- **Speichern (`savefig`):**
  Die Funktion `plt.savefig("dateiname")` speichert Grafiken **automatisch** in den zentralen Ordner `Plots/` im Hauptverzeichnis des Projekts. Man muss sich also keine Gedanken über relative Pfade machen.

  Optional kann eine Kategorie angegeben werden, um Unterordner zu erstellen:

  ```python
  plt.savefig("mein_plot", category="Analyse_X")
  # Speichert unter: Projekt_Root/Plots/Analyse_X/mein_plot.pdf
  ```

- **Plot-Größe anpassen:**
  Falls Elemente überlappen, kann die Plotgröße temporär skaliert werden (Werte zwischen 1.0 bis 2.0 funktionieren ganz gut):
  ```python
  with plt.rc_context(plt.increase_figsize(1.5)):
      plt.plot(x, y)
      plt.title("Größerer Plot")
      plt.savefig("large_plot.pdf")
  ```

Weitere Details finden sich in `plotting/plotting.md`.
