import ieee738
from ieee738 import ConductorParams
import logging
import putAllTogether
import importWData
import geopandas as gpd
import pandas as pd
from ieee738.conductor_defaults import conductor_defaults
from ieee738.ambient import ambient_defaults
import math

dataFrame = importWData.returnDataFrame

ambient_defaults = dataFrame.apply(lambda row: putAllTogether.returnAmbDefaults(row.name), axis=1)


def voltageToConductor(lines, buses):
    voltage_to_conductor = {
    69: "ACSR_336_MOOSE",
    115: "ACSR_477_HAWK",
    138: "ACSR_477_HAWK",
    230: "ACSR_795_DRAGON",
    345: "ACSR_1033_LINNET"
    }
    conductorType = []
    for i in range(len(lines)):
        busZero = lines[i, 'bus0']
        busOne = lines[i,'bus1']
        if buses[busZero, 'v_nom'] == buses[busOne, 'v_nom']:
            conductorType[i] = voltage_to_conductor[busZero]
    return conductorType
    

linesData = pd.read_csv("hawaii40_osu/csv/lines.csv")
busesData = pd.read_csv("hawaii40_osu/csv/buses.csv")
#list of conductor names
condType = voltageToConductor(linesData, busesData)
#loop through the conductor names and create a list of conductor objects
condObjects = []
for name in condType:
    conductor = conductor_defaults.get(name)
    if conductor:
        condObjects.append(conductor)
    else:
        print(f"Warning: {name} not found in conductor_defaults.")
ampacity = condObjects.ampacity(ambient_defaults)
conductor_to_voltage = {
    "ACSR_336_MOOSE": 69,
    "ACSR_477_HAWK": 115,
    "ACSR_477_HAWK": 138,
    "ACSR_795_DRAGON": 230,
    "ACSR_1033_LINNET": 345
    }

linesData['s_nom'] = math.sqrt(3) * ampacity * conductor_to_voltage[condType]
fNominal = pd.read_csv("hawaii40_osu/line_flows_nominal.csv")
newTable = pd.DataFrame({
    'Line Name': linesData['name'],
    'flow (p0)': fNominal['p0_nominal'],
    'rating (s_nom)': linesData['s_nom'],
    'loading': (fNominal['p0_nominal'] / linesData['s_nom'])*100
    })
def goodNot(loading):
    if loading >=90:
        return 'critical'
    elif loading>=60:
        return 'caution'
    else:
        return 'nominal'
newTable['status'] = newTable['loading'].apply(goodNot)




MOT = 75 # Maximum operating temperature of conductor in deg C