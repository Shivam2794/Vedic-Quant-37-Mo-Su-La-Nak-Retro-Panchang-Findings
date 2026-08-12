import json
from vedic_engine_core import VedicAstrologyEngine
from shadbala_core import calc_shadbala
from vedha_engine import get_vedha_pairs

class UltimateVedicEngine(VedicAstrologyEngine):
    def get_transit_snapshots(self, dates, natal_planets=None):
        snapshots = {}
        for dt_str in dates:
            jd, dt_utc = self.get_jd(dt_str)
            planets = self.calculate_d1(jd)
            d1_rasi = {}
            for p, d in planets.items():
                if p == "MC": continue
                d1_rasi[p] = {"sign": d["sign"], "degrees": d["degrees"], "nakshatra": d["nakshatra"], "pada": d["pada"], "longitude": d["longitude"]}
            
            snap = {"D1_rasi": d1_rasi}
            
            if natal_planets:
                from vedha_engine import get_vedha_pairs
                snap["transit_vedhas"] = get_vedha_pairs(natal_planets, transit_planets=planets)
                
            snapshots[dt_str] = snap
        return snapshots

    def process_all(self, dt_str, transit_dates=[]):
        # Run core base features (D1, D9, D10, Ashtakvarga)
        base_features = self.process(dt_str)
        
        # We need the planetary objects and ascendant for advanced features
        jd, dt_utc = self.get_jd(dt_str)
        planets = self.calculate_d1(jd)
        
        asc_lon = planets["Ascendant"]["longitude"]
        sun_lon = planets["Sun"]["longitude"]
        moon_lon = planets["Moon"]["longitude"]
        mc_lon = planets.get("MC", {}).get("longitude", 0)
        
        # Calculate Shadbala
        shadbala = calc_shadbala(planets, asc_lon, sun_lon, moon_lon, jd, mc_lon)
        
        # Calculate Vedha Pairs
        vedhas = get_vedha_pairs(planets)
        
        # Calculate Panchang and Dasha
        from compute_full_features import calc_panchang, calc_dasha, get_3level_dasha, NAK_LORDS, NAK_SIZE
        panchang = calc_panchang(jd, dt_utc)
        
        from datetime import datetime
        import pytz
        birth_dt = datetime(dt_utc.year, dt_utc.month, dt_utc.day,
                            dt_utc.hour, dt_utc.minute, dt_utc.second, tzinfo=pytz.utc)
        sequence = calc_dasha(moon_lon, birth_dt)
        today = datetime(2026, 6, 4, 12, 0, 0, tzinfo=pytz.utc)
        
        dasha_at_birth = get_3level_dasha(sequence, birth_dt)
        dasha_today    = get_3level_dasha(sequence, today)
        
        dasha_full = {
            "birth_lord": NAK_LORDS[int(moon_lon / NAK_SIZE) % 9],
            "moon_nakshatra": planets["Moon"]["nakshatra"],
            "moon_pada": planets["Moon"]["pada"],
            "full_sequence": [{"lord": d["lord"], "start": d["start"].strftime("%Y-%m-%d"),
                                "end": d["end"].strftime("%Y-%m-%d"), "years": d["years"]} for d in sequence],
            "at_birth": dasha_at_birth,
            "at_2026_06_04": dasha_today
        }
        
        # Transit Snapshots
        transits = self.get_transit_snapshots(transit_dates, natal_planets=planets)
        
        # Return merged dict
        return {
            "birth_datetime": dt_str,
            "D1_rasi": base_features["D1_rasi"],
            "D9_navamsa": base_features["D9_navamsa"],
            "D10_dasamsa": base_features["D10_dasamsa"],
            "ashtakvarga": base_features["ashtakvarga"],
            "shadbala": shadbala,
            "natal_vedha_pairs": vedhas,
            "panchang": panchang,
            "vimshottari_dasha": dasha_full,
            "transit_snapshots": transits
        }

if __name__ == "__main__":
    engine = UltimateVedicEngine()
    
    # We will generate ALL data for the 4 specific events the user provided in the snippet
    events = {
        "Sector_ETFs_trading": "1998-12-22 09:30:00", # Using XLK as proxy
        "Sector_ETFs_conception": "1998-12-16 12:00:00",
        "SPY_trading": "1993-01-29 09:30:00",
        "QQQ_trading": "1999-03-10 09:30:00"
    }
    
    transit_dates = [
        "2020-01-15 09:30:00", "2020-06-15 09:30:00", "2021-01-15 09:30:00", "2021-06-15 09:30:00",
        "2022-01-15 09:30:00", "2022-06-15 09:30:00", "2023-01-15 09:30:00", "2023-06-15 09:30:00",
        "2024-01-15 09:30:00", "2024-06-15 09:30:00", "2025-01-15 09:30:00", "2025-06-15 09:30:00",
        "2026-01-15 09:30:00", "2026-06-15 09:30:00", "2027-01-15 09:30:00"
    ]
    
    full_output = {}
    for name, dt in events.items():
        print(f"Calculating {name}...")
        full_output[name] = engine.process_all(dt, transit_dates)
        
    with open("ultimate_features_output.json", "w", encoding="utf-8") as f:
        json.dump(full_output, f, indent=2)
        
    print("Done. Saved to ultimate_features_output.json")
