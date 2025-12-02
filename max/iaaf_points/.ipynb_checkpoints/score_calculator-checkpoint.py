import json
import math

# # --- Load JSON ---
# with open("max/iaaf_points/IAAF_2025.json") as f:
#     points_data = json.load(f)

# with open("max/iaaf_points/IAAF_Coefficients_2025.json") as f:
#     coeffs = json.load(f)

# --- Score using polynomial formula ---
def score_from_mark(gender, event, mark, coeffs, func=None):
    if type(coeffs) == dict:
        a, b, c = coeffs[gender][event]
    else:
        a, b, c = coeffs.loc[event, gender]
    points = a * mark * mark + b * mark + c
    if func is None:
        return round(points)
    elif func == 'ceil':
        return int(math.ceil(points))
    elif func == 'floor':
        return int(math.floor(points))
    

# --- Example ---
if __name__ == "__main__":
    example_mark = 19.19
    pts = score_from_mark("men", "TJ", example_mark, coeffs, func='ceil')
    print(f"Triple Jump {example_mark} → {pts} Punkte")