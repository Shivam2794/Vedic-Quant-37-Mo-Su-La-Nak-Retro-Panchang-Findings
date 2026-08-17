import uuid
from typing import Dict, List, TypedDict

class PlanetLongitude(TypedDict):
    planet: str
    longitude: float  # Absolute longitude 0-360

class KarakaResult(TypedDict):
    karaka: str
    karaka_abbr: str
    planet: str
    degree_in_sign: float
    formatted_degree: str

def format_degree(deg_decimal: float) -> str:
    """Converts decimal degrees to DD°MM'SS\" format to match AstroSage tables."""
    degrees = int(deg_decimal)
    minutes_decimal = (deg_decimal - degrees) * 60
    minutes = int(minutes_decimal)
    seconds = int((minutes_decimal - minutes) * 60)
    return f"{degrees:02d}°{minutes:02d}'{seconds:02d}\""

def calculate_jaimini_karakas(planets: List[PlanetLongitude]) -> List[KarakaResult]:
    """
    Calculates the 7 Jaimini Chara Karakas:
    Atma (AK), Amatya (AmK), Bhratru (BK), Matru (MK), Putra (PK), Gnati (GK), Dara (DK).
    
    Calculation is based on descending longitude within a sign (0-30 degrees)
    for the 7 visible planets (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn).
    Rahu and Ketu are excluded from the 7-karaka scheme, perfectly matching AstroSage.
    """
    valid_planets = {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"}
    
    # 1. Extract the 7 valid planets and calculate their degree within the sign (modulo 30)
    chara_planets = []
    for p in planets:
        if p["planet"] in valid_planets:
            degree_in_sign = p["longitude"] % 30.0
            chara_planets.append({
                "planet": p["planet"],
                "degree_in_sign": degree_in_sign,
                "formatted_degree": format_degree(degree_in_sign)
            })
            
    # 2. Sort descending by degree within the sign. NO ties allowed without resolution (resolved by planet name).
    chara_planets.sort(key=lambda x: (x["degree_in_sign"], x["planet"]), reverse=True)
    
    # 3. Assign Karakas based on the sorted order
    # Note: Using 'Matru' instead of 'Matrua' as it is the standard Sanskrit term used by AstroSage
    karakas = [
        {"name": "Atma", "abbr": "AK"},
        {"name": "Amatya", "abbr": "AmK"},
        {"name": "Bhratru", "abbr": "BK"},
        {"name": "Matru", "abbr": "MK"},
        {"name": "Putra", "abbr": "PK"},
        {"name": "Gnati", "abbr": "GK"},
        {"name": "Dara", "abbr": "DK"}
    ]
    
    results = []
    for i, kp in enumerate(chara_planets):
        if i < len(karakas):
            results.append({
                "karaka": karakas[i]["name"],
                "karaka_abbr": karakas[i]["abbr"],
                "planet": kp["planet"],
                "degree_in_sign": kp["degree_in_sign"],
                "formatted_degree": kp["formatted_degree"]
            })
            
    return results

def get_astrosage_karak_table(planets: List[PlanetLongitude]) -> Dict[str, KarakaResult]:
    """
    Returns a mapping of Planet to its assigned Karaka, which is often how
    AstroSage displays the Karak column in their planetary positions table.
    """
    karakas_list = calculate_jaimini_karakas(planets)
    # Return a dictionary mapped by planet name for easy table joining
    return {k["planet"]: k for k in karakas_list}
