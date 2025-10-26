import geopandas as gpd
import matplotlib.pyplot as plt
import csv
import pandas as pd


def color(loading):
    if loading >=90:
        return 'red'
    elif loading>=60:
        return 'yellow'
    else:
        return 'green'
def addColorColumn(newTable, linesData, fNominal):
    newTable['Color'] = newTable['loading'].apply(color)
    


def main():
    
    try:
        lines = gpd.read_file("hawaii40_osu/gis/oneline_lines.geojson")
        buses = gpd.read_file("hawaii40_osu/gis/oneline_busses.geojson")
        linesData = pd.read_csv("hawaii40_osu/csv/lines.csv")
        fNominal = pd.read_csv("hawaii40_osu/line_flows_nominal.csv")
    except Exception as e:
        print("Error loading files:", e)
        return
    
    
    newTable = pd.DataFrame({
    'Line Name': linesData['name'],
    'flow (p0)': fNominal['p0_nominal'],
    'rating (s_nom)': linesData['s_nom'],
    'loading': (fNominal['p0_nominal'] / linesData['s_nom'])*100
    })
    addColorColumn(newTable, linesData, fNominal)
    print(newTable)
    # Color lines safely
   # if 'length' in lines.columns:
     #   max_length = lines['length'].max()
     #   lines['color'] = lines['length'].apply(lambda x: x / max_length)
     #   line_colors = plt.cm.viridis(lines['color'])
  #  else:
    #line_colors = 'gray'

    # Plot
    fig, ax = plt.subplots(figsize=(10,10))
    lines.plot(ax=ax, color=newTable['Color'], linewidth=2, legend=True)
    buses.plot(ax=ax, color='red', markersize=20)
    plt.title("Hawaii40_OSU Synthetic Power Grid")
    plt.axis('off')
    plt.savefig("grid_map.png", dpi=150)
    print("Map saved to grid_map.png")
    
if __name__ == "__main__":
    main()
