from flask import Flask, request, jsonify, send_from_directory
import geopandas as gpd
import pandas as pd
import ieee738
from ieee738 import ConductorParams

app = Flask(__name__, static_folder=".", template_folder=".")

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
            'RLo': float(cond['RES_25C']) / 5280,
            'RHi': float(cond['RES_50C']) / 5280,
            'Diameter': float(cond['CDRAD_in']) * 2,
            'Tc': float(row['MOT'])
        }
        cp = ConductorParams(**ambient, **acsr_props)
        con = ieee738.Conductor(cp)
        rating_amps = con.steady_state_thermal_rating()
        rating_mva = (3**0.5) * rating_amps * 69e3 * 1e-6
        s_nom_dynamic.append(float(rating_mva))

    for flow, rating in zip(fNominal['p0_nominal'], s_nom_dynamic):
        loading = (float(flow) / float(rating)) * 100
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

@app.route("/grid_data", methods=["POST"])
def grid_data():
    ambient_input = request.get_json() or {}
    ambient = {**default_ambient, **ambient_input}
    s_nom_dynamic, colors = compute_line_ratings(ambient)

    lines_json, buses_json, table_json = [], [], []

    for idx, row in lines.iterrows():
        flow = float(fNominal.iloc[idx]['p0_nominal'])
        rating = float(s_nom_dynamic[idx])
        loading = (flow / rating) * 100
        color = colors[idx]

        lines_json.append({
            "name": str(linesData.iloc[idx]['name']),
            "bus0": str(linesData.iloc[idx]['bus0']),
            "bus1": str(linesData.iloc[idx]['bus1']),
            "coords": [[float(c[0]), float(c[1])] for c in row['geometry'].coords],
            "flow": flow,
            "rating": rating,
            "loading": loading,
            "color": color
        })

        table_json.append({
            "name": str(linesData.iloc[idx]['name']),
            "from": str(linesData.iloc[idx]['bus0']),
            "to": str(linesData.iloc[idx]['bus1']),
            "load": round(float(loading), 1),
            "color": color
        })

    table_json.sort(key=lambda x: x["load"], reverse=True)

    for idx, row in buses.iterrows():
        buses_json.append({
            "name": str(row['BusName']),
            "coords": [float(row['geometry'].x), float(row['geometry'].y)]
        })

    return jsonify({"lines": lines_json, "buses": buses_json, "table": table_json})

if __name__ == "__main__":
    app.run(debug=True)
