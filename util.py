import pandas as pd
import os

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

# --- Configuration for Filtering ---

# Allowed ages and their mapping to text file categories
ALLOWED_AGES = ['18', '20', 'U23', 'Frauen', 'Maenner']

# Mapping CSV age strings to 'rules' categories
AGE_CATEGORY_MAP = {
    '18': 'U18',
    '20': 'U20',
    'U23': 'U23',
    'Frauen': 'Adult',
    'Maenner': 'Adult'
}

# Base disciplines (Sprint, Wurf, Sprung, Mehrkampf) - available for ALL allowed ages
BASE_DISCIPLINES = {
    'M': [
        '100 m', '200 m', '400 m', '110 m Huerden', '400 m Huerden',
        'Kugelstoss', 'Diskuswurf', 'Hammerwurf', 'Speerwurf',
        'Hochsprung', 'Stabhochsprung', 'Weitsprung', 'Dreisprung'
    ],
    'W': [
        '100 m', '200 m', '400 m', '100 m Huerden', '400 m Huerden',
        'Kugelstoss', 'Diskuswurf', 'Hammerwurf', 'Speerwurf',
        'Hochsprung', 'Stabhochsprung', 'Weitsprung', 'Dreisprung'
    ]
}

# Lauf disciplines - Specific by Age Category
LAUF_DISCIPLINES = {
    'U18': ['800 m', '1500 m', '3000 m', '2000 m Hindernis'],
    'U20': ['800 m', '1500 m', '3000 m', '5000 m', '3000 m Hindernis'],
    'U23': ['800 m', '1500 m', '5000 m', '10 000 m', '10 km', '3000 m Hindernis'],
    'Adult': ['800 m', '1500 m', '5000 m', '10 000 m', '10 km', '3000 m Hindernis', 'Marathon']
}

GROUP_MAPPING = {
    **{d: 'Run' for d in ['800 m', '1500 m', '3000 m', '5000 m', '10 km', 'Marathon', '2000 m Hindernis', '3000 m Hindernis']},
    **{d: 'Sprint' for d in ['100 m', '200 m', '400 m', '100 m Huerden', '110 m Huerden', '400 m Huerden']},
    **{d: 'Throw' for d in ['Kugelstoss', 'Diskuswurf', 'Speerwurf', 'Hammerwurf']}, 
    **{d: 'Jump' for d in ['Hochsprung', 'Stabhochsprung', 'Weitsprung', 'Dreisprung']},
    **{d: 'Combined' for d in ['Zehnkampf', 'Siebenkampf']}
}

def filter_relevant_data(df, youth):
    """
    Filters the DataFrame based on the funded disciplines and age groups.
    """

    if youth:
        allowed_ages = ALLOWED_AGES + ['16', '14']
    else:
        allowed_ages = ALLOWED_AGES
    # 1. Filter allowed ages
    df = df[df['altersklasse'].isin(allowed_ages)].copy()
    
    # 2. Apply discipline filter based on Age and Gender
    mask = pd.Series(False, index=df.index)
    
    for gender in ['M', 'W']:
        for age_csv in allowed_ages:
            age_cat = AGE_CATEGORY_MAP.get(age_csv)
            
            # Get allowed base disciplines for this gender
            allowed = set(BASE_DISCIPLINES.get(gender, []))
            
            # Add Lauf disciplines for this age category
            if age_cat in LAUF_DISCIPLINES:
                allowed.update(LAUF_DISCIPLINES[age_cat])
                
            # Create sub-mask
            sub_mask = (df['geschlecht'] == gender) & \
                       (df['altersklasse'] == age_csv) & \
                       (df['disziplin'].isin(allowed))
            
            mask = mask | sub_mask
            
    return df[mask]

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
    
def set_wind(value):
    """Wandelt Windangabe in float um"""
    if pd.isna(value):
        return None
    
    wind_str = str(value)
    if wind_str.startswith('+'):
        positive = True
    else:
        positive = False

    
    value = float(str(value).replace(',', '.').replace('+', '').replace('-', ''))
    if not positive:
        value *= -1

    try:
        return value
    except ValueError:
        return None


_PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
_DATA_DIR = os.path.join(_PROJECT_ROOT, "data_csv")

def load_data(path_file=os.path.join(_DATA_DIR, "final_Data_iaaf_scores_neu.csv"), filter=True, youth=False):
    df = pd.read_csv(path_file, sep=";")

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
        
    df['group'] = df['disziplin'].map(GROUP_MAPPING)

    # Spalte 'leistung' entsprechend anpassen
    df['leistung'] = df.apply(convert_leistung, axis=1)
    df['wind'] = df['wind'].apply(set_wind)

    if filter:
        df = filter_relevant_data(df, youth=youth)

    return df
