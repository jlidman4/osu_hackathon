import geopandas as gpd
import csv
import pandas as pd

import importWData
import visualize_grid
from datetime import datetime 

hourlyWeather = importWData.returnDataFrame()
print(hourlyWeather)
def returnMonthYear(index):
    month = datetime.fromisoformat(hourlyWeather[index, 'date']).month
    day = datetime.fromisoformat(hourlyWeather[index, 'date']).day
    printedDate = ''
    match month:
        case 1:
            printedDate = day + ' Jan'
        case 2:
            printedDate = day + ' Feb'
        case 3:
            printedDate = day + ' Mar'
        case 4:
            printedDate = day + ' Apr'
        case 5:
            printedDate = day + ' May'
        case 6:
            printedDate = day + ' Jun'
        case 7:
            printedDate = day + ' Jul'
        case 8:
            printedDate = day + ' Aug'
        case 9:
            printedDate = day + ' Sep'
        case 10:
            printedDate = day + ' Oct'
        case 11:
            printedDate = day + ' Nov'
        case 12:
            printedDate = day + ' Dec'
    return printedDate
        
def returnAmbDefaults(index):
    ambientDefaults = {
    'Ta': hourlyWeather[index, 'temperature_2m'],
    'WindVelocity': hourlyWeather[index, 'wind_speed_10m'], 
    'WindAngleDeg': 90,
    'SunTime': datetime.fromisoformat(hourlyWeather[index, 'date']).month,
    'Date': returnMonthYear(index),
    'Emissivity': 0.8,
    'Absorptivity': 0.8,
    'Direction': 'EastWest',
    'Atmosphere': 'Clear',
    'Elevation': 1000,
    'Latitude': 27,
    }
extremeTemperatures = lambda x : [max(x['temperature_2m']), min(x['temperature_2m'])]
extremeTemperatures = lambda x : [max(x['wind_speed_10m']), min(x['wind_speed_10m'])] 



