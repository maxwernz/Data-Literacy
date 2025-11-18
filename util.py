import pandas as pd

# MEASUREMENT_TYPE = measurement = {
#         "time": ['100 m', '200 m', '400 m', '800 m', '1500 m', '3000 m', '5000 m',
#             '10 km', 'Halbmarathon', 'Marathon', '100 km', '100 m Huerden',
#             '400 m Huerden', '3000 m Hindernis', '5000 m Gehen', '10 km Gehen',
#             '20 km Gehen', '1000 m', '110 m Huerden', '10000 m',
#             '10000 m Bahngehen', '50 km Gehen', '5 km', '80 m Huerden',
#             '3000 m Bahngehen', '300 m', '300 m Huerden', '2000 m Hindernis',
#             '2000 m', '1500 m Hindernis', '50 km Strassengehen',
#             '10000 m Gehen', '1.500 m', '3.000 m', '5.000 m',
#             '10.000 m', '3.000 m Hindernis', '5.000 m Bahngehen', '1.000 m', '10.000 m Bahngehen', '3.000 m Bahngehen', '2.000 m Hindernis', '2.000 m',
#             '1.500 m Hindernis', '5.000 M'],
#         "meter": ['Hochsprung', 'Stabhochsprung', 'Weitsprung',
#         'Dreisprung', 'Kugelstoss', 'Diskuswurf', 'Hammerwurf',
#         'Speerwurf'],
#         "points": ['Fuenfkampf', 'Siebenkampf', 'Zehnkampf']
#     }

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

def load_data():
    df = pd.read_csv("Data.csv", sep=";")
    print(df[df['disziplin'].isin(MEASUREMENT_TYPE['time'])]['disziplin'].unique())
    print(df[df['disziplin'].isin(MEASUREMENT_TYPE['meter'])]['disziplin'].unique())
    print(df[df['disziplin'].isin(MEASUREMENT_TYPE['points'])]['disziplin'].unique())


load_data()

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
    
print(convert_time_to_seconds("2:30,50"))  # Beispielaufruf
print(convert_time_to_seconds("75,25"))    # Beispielaufruf
print(convert_time_to_seconds("1:02:30,50"))  # Beispielaufr
