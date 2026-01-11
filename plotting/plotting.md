# Erklärung Plotting

Ich habe jetzt mal ein kleines skript zum importieren gebastelt, welches alle Plots automatisch gleich aussehen lässt und and die Vorgaben anpasst (ist zumindest aktuell an den Style von der Overleaf vorgabe angepasst).

Um das ganze zu benutzen müsst ihr einfach wie auch für `util.py` 

```
from pathlib import Path
import sys
parent_path = Path().resolve().parent
sys.path.append(str(parent_path))
```
importieren (dort halt eben je nachdem wie viele Unterordner es sind parent anpassen, also eventuell noch .parent anhängen).
Danach könnt ihr einfach 

```
import plotting.plotting_style as plt
```
importieren und dann auf jeden Fall 

```
import matplotlib.pyplot as plt

```
auskommentieren, sonst wird das erste wieder überschrieben. Den restlichen Code könnt ihr einfach so lassen, das sollte alles automatisch funktionieren. Bei den Notebooks kann es sein dass ihr einmal vorher auf Restart klicken müsst.

Solltet ihr große Plots haben, wo sich jetzt Dinge überlappen, könnt ihr das so machen:

```
with plt.rc_context(plt.increase_figsze(factor)):

    restlicher plotting code hier dann eingerückt
```

und beim Faktor je nachdem etwas in Richtung 1.5 - 2 oder so eintragen.

Um Bilder zu speichern einfach `plt.savefig("Pfad")`, mehr nicht. Dadurch werden die Bilder automatisch mit der richigen Größe und allen Einstellungen als PDF gespeichert.