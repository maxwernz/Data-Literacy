import pandas as pd

MEASUREMENT_TYPE = {
    "time": [
        '100 m', '200 m', '400 m', '800 m', '1500 m', '3000 m', '5000 m', '10 km',
        'Halbmarathon', 'Marathon', '100 km', '100 m Huerden', '400 m Huerden',
        '3000 m Hindernis', '110 m Huerden', '2000 m Hindernis', '300 m', '1000 m',
        '5 km', '3000 m Gehen', '50 km Gehen', '10 000 m Gehen', '1500 m Hindernis',
        '10 000 m'
    ],
    "meter": [
        'Hochsprung', 'Stabhochsprung', 'Weitsprung', 'Dreisprung', 'Kugelstoss',
        'Diskuswurf', 'Hammerwurf', 'Speerwurf'
    ],
    "points": [
        'Siebenkampf', 'Zehnkampf'
    ]
}

_patterns = {
    "HH:MM:SS,mS": r'^\d{1,2}(:\d{1,2}){1,2}(,\d{1,2})?$',
    "AA,BB": r'^\d{1,2},\d{1,2}$',
    "Numeric": r'^(?:\d{3,4}|\d{1}[.,]\d{3})$'
}

PERFORMANCE_PATTERNS = {
    "time": [_patterns["HH:MM:SS,mS"], _patterns["AA,BB"]],
    "meter": [_patterns["AA,BB"]],
    "points": [_patterns["Numeric"]]
}

def get_measurement_key(discipline):
    for key, values in MEASUREMENT_TYPE.items():
        if discipline in values:
            return key
    return None   # falls nicht gefunden

def convert_seconds_to_time_repr(seconds):
    """
    Wandelt Sekunden in ein Zeitformat wie 'SS,SS', 'MM:SS,SS' oder 'H:MM:SS,SS' um.
    """
    if seconds is None:
        return None
    
    try:
        seconds = float(seconds)
    except ValueError:
        return None

    hours = int(seconds // 3600)
    seconds %= 3600
    minutes = int(seconds // 60)
    secs = seconds % 60

    # Sekunden immer mit 2 Nachkommastellen
    secs_str = f"{secs:0.2f}".replace('.', ',')

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs_str}"
    elif minutes > 0:
        return f"{minutes}:{secs_str}"
    else:
        return secs_str

def convert_time_to_seconds(value):
    """Wandelt 'MM:SS,SS' oder 'SS,SS' in Sekunden um"""
    if pd.isna(value):
        return None
    value = str(value).replace(',', '.')
    parts = value.split(':')
    try:
        if len(parts) == 1:
            return float(parts[0])
        elif len(parts) == 2:
            minutes, seconds = parts
            return int(minutes) * 60 + float(seconds)
        elif len(parts) == 3:
            hours, minutes, seconds = parts
            return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    except ValueError:
        return None
    
def convert_points_to_int(value):
    """Wandelt 'AA,BB' in float um"""
    if pd.isna(value):
        return None
    value = str(value).replace('.', '')
    try:
        return float(value)
    except ValueError:
        return None
    
def convert_meters_to_float(value):
    """Wandelt 'AA,BB' in float um"""
    if pd.isna(value):
        return None
    value = str(value).replace(',', '.')
    try:
        return float(value)
    except ValueError:
        return None
    

def load_data():
    df = pd.read_csv("Data.csv", sep=";")

    # Funktion, die je nach Disziplin den passenden Converter wählt
    def convert_leistung(row):
        disziplin = row['disziplin']
        leistung = row['leistung']

        if disziplin in MEASUREMENT_TYPE['time']:
            return convert_time_to_seconds(leistung)
        elif disziplin in MEASUREMENT_TYPE['meter']:
            return convert_meters_to_float(leistung)
        elif disziplin in MEASUREMENT_TYPE['points']:
            return convert_points_to_int(leistung)
        else:
            return leistung  # falls Disziplin unbekannt, originalwert zurückgeben

    # Spalte 'leistung' entsprechend anpassen
    df['leistung'] = df.apply(convert_leistung, axis=1)

    return df
