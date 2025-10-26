from ieee738 import ConductorParams

# Shared ambient defaults
ambient = {
    'Ta': 25,
    'WindVelocity': 2.0,
    'WindAngleDeg': 90,
    'SunTime': 12,
    'Elevation': 1000,
    'Latitude': 27,
    'Emissivity': 0.8,
    'Absorptivity': 0.8,
    'Direction': 'EastWest',
    'Atmosphere': 'Clear',
    'Date': '12 Jun',
    'TLo': 25,
    'THi': 50,
}

# Physical properties by conductor name
physical_props = {
    "3/0 ACSR 6/1 PIGEON":     {"RLo": 0.5405/5280, "RHi": 0.6638/5280, "Diameter": 0.2510*2, "GMR": 0.0161},
    "4/0 ACSR 6/1 PENGUIN":    {"RLo": 0.4288/5280, "RHi": 0.5446/5280, "Diameter": 0.2815*2, "GMR": 0.0180},
    "336.4 ACSR 30/7 ORIOLE":  {"RLo": 0.2708/5280, "RHi": 0.29740/5280, "Diameter": 0.3705*2, "GMR": 0.0255},
    "556.5 ACSR 26/7 DOVE":    {"RLo": 0.1655/5280, "RHi": 0.18160/5280, "Diameter": 0.4635*2, "GMR": 0.0313},
    "795 ACSR 26/7 DRAKE":     {"RLo": 0.1166/5280, "RHi": 0.12780/5280, "Diameter": 0.5540*2, "GMR": 0.0374},
    "954 ACSR 54/7 CARDINAL":  {"RLo": 0.09860/5280, "RHi": 0.1099/5280, "Diameter": 0.598*2, "GMR": 0.0404},
    "1272 ACSR 45/7 BITTERN":  {"RLo": 0.0761/5280, "RHi": 0.08440/5280, "Diameter": 0.6725*2, "GMR": 0.0445},
    "1590 ACSR 54/19 FALCON":  {"RLo": 0.0613/5280, "RHi": 0.06780/5280, "Diameter": 0.7725*2, "GMR": 0.0521},
}

# Temperature variants
mot_levels = [75, 80, 85, 90, 95]

# Final dictionary
conductor_defaults = {}

for name, props in physical_props.items():
    for mot in mot_levels:
        key = f"{name}_{mot}"
        conductor_defaults[key] = ConductorParams(**ambient, **props, Tc=mot)
__all__ = ['conductor_defaults']