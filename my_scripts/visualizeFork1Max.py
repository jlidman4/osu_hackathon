from flask import Flask, request, jsonify, send_from_directory
import geopandas as gpd
import pandas as pd
import ieee738
from ieee738 import ConductorParams

app = Flask(__name__, static_folder=".", template_folder=".")

# Load static files once
lines = gpd.read_file("hawaii40_osu/gis/oneline_lines.geojson")
buses = gpd.read_file("hawaii40_osu/gis/oneline_busses.geojson")
linesData = pd.read_csv("hawaii40_osu/csv/lines.csv")
fNominal = pd.read_csv("hawaii40_osu/line_flows_nominal.csv")
conductor_lib = pd.read_csv("ieee738/conductor_library.csv")

default_ambient = {
    'Ta': 25, 'WindVelocity': 2.0, 'WindAngleDeg': 90,
    'SunTime': 12, 'Date': '12 Jun', 'Emissivity': 0.8,
    'Absorptivity': 0.8, 'Direction': 'EastWest',
    'Atmosphere': 'Clear', 'Elevation': 1000, 'Latitude': 27
}

def compute_line_ratings(ambient):
    s_nom_dynamic, colors = [], []
    for idx, row in linesData.iterrows():
        cond = conductor_lib[conductor_lib['ConductorName'] == row['conductor']].iloc[0]
        acsr_props = {
            'TLo': 25, 'THi': 50,
            'RLo': cond['RES_25C']/5280,
            'RHi': cond['RES_50C']/5280,
            'Diameter': cond['CDRAD_IN']*2, 'Tc': row['MOT']
        }
        cp = ConductorParams(**ambient, **acsr_props)
        con = ieee738.Conductor(cp)
        rating_amps = con.steady_state_thermal_rating()
        rating_mva = (3**0.5) * rating_amps * 69e3 * 1e-6
        s_nom_dynamic.append(rating_mva)

    for flow, rating in zip(fNominal['p0_nominal'], s_nom_dynamic):
        loading = (flow / rating) * 100
        if loading >= 90: colors.append('red')
        elif loading >= 60: colors.append('yellow')
        else: colors.append('green')

    return s_nom_dynamic, colors

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/interactiveMap.js")
def js():
    return send_from_directory(".", "interactiveMap.js")

@app.route("/style.css")
def css():
    return send_from_directory(".", "style.css")

@app.route("/grid_data", methods=["GET", "POST"])
def grid_data():
    ambient = request.get_json() or default_ambient
    s_nom_dynamic, colors = compute_line_ratings(ambient)

    lines_json, buses_json = [], []

    for idx, row in lines.iterrows():
        lines_json.append({
            "name": linesData.iloc[idx]['name'],
            "bus0": linesData.iloc[idx]['bus0'],
            "bus1": linesData.iloc[idx]['bus1'],
            "coords": list(row['geometry'].coords),
            "flow": fNominal.iloc[idx]['p0_nominal'],
            "rating": s_nom_dynamic[idx],
            "loading": (fNominal.iloc[idx]['p0_nominal']/s_nom_dynamic[idx])*100,
            "color": colors[idx]
        })

    for idx, row in buses.iterrows():
        buses_json.append({"name": row['name'], "coords": [row['geometry'].x, row['geometry'].y]})

    return jsonify({"lines": lines_json, "buses": buses_json})

if __name__ == "__main__":
    app.run(debug=True)
