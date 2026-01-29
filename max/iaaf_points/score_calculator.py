import json
import math
import pandas as pd
from pathlib import Path

DISCIPLINE_TO_EVENT = {
    # meter
    'Dreisprung': 'TJ',
    'Hochsprung': 'HJ',
    'Stabhochsprung': 'PV',
    'Weitsprung': 'LJ',
    'Kugelstoss': 'SP',
    'Diskuswurf': 'DT',
    'Hammerwurf': 'HT',
    'Speerwurf': 'JT',

    # points
    'Siebenkampf': 'Hept.',
    'Zehnkampf': 'Dec.',

    # time
    '100 m': '100m',
    '200 m': '200m',
    '300 m': '300m',
    '400 m': '400m',
    '800 m': '800m',
    '1000 m': '1000m',
    '1500 m': '1500m',
    '3000 m': '3000m',
    '5000 m': '5000m',
    '10 000 m': '10000m',

    # hurdles
    '100 m Huerden': '100mH',
    '110 m Huerden': '110mH',
    '400 m Huerden': '400mH',

    # steeple
    '1500 m Hindernis': '1500m sh',
    '2000 m Hindernis': '2000m SC',
    '3000 m Hindernis': '3000m SC',

    # walks
    '3000 m Gehen': '3000mW',
    '10 000 m Gehen': '10,000mW',
    '50 km Gehen': '50,000mW',

    # road events
    'Halbmarathon': 'Road HM',
    '5 km': 'Road 5 km',
    '10 km': 'Road 10 km',
    '50 km Gehen (Road)': 'Road 50kmW',
    '100 km': 'Road 100 km',
    'Marathon': 'Road Marathon'
}

def get_iaaf_coeffs():
    base_path = Path(__file__).resolve().parent

    json_path = base_path / "IAAF_Coefficients_2025.json"
    coeffs = pd.read_json(json_path)
    return coeffs



def score_from_mark(gender, event, mark, coeffs, cutoff='larger', func=None):
    if mark is None:
        return None

    if type(coeffs) == dict:
        a, b, c = coeffs[gender][event]
    else:
        a, b, c = coeffs.loc[event, gender]

    xs = -b / (2*a)
    # if cutoff == 'larger' and mark > xs:
    #     return 0
    # elif cutoff == 'smaller' and mark < xs:
    #     return 0
    points = a * mark * mark + b * mark + c
    if func is None:
        return round(points)
    elif func == 'ceil':
        return int(math.ceil(points))
    elif func == 'floor':
        return int(math.floor(points))
    

if __name__ == "__main__":

    with open("max/iaaf_points/IAAF_2025.json") as f:
        points_data = json.load(f)

    with open("max/iaaf_points/IAAF_Coefficients_2025.json") as f:
        coeffs = json.load(f)

    example_mark = 40
    pts = score_from_mark("women", "TJ", example_mark, coeffs, cutoff='smaller')
    print(f"5km {example_mark} → {pts} Punkte")