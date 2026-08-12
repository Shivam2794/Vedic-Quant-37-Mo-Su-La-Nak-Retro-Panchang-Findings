import sys
import swisseph as swe
from datetime import datetime
import pytz

def get_astrosage_tables():
    # Chrome/AstroSage standard BAV tables for SPY (as seen in earlier investigation)
    return {
        "Sun": {"Aries":3,"Taurus":3,"Gemini":4,"Cancer":4,"Leo":4,"Virgo":6,"Libra":3,"Scorpio":3,"Sagittarius":3,"Capricorn":6,"Aquarius":7,"Pisces":2},
        "Moon": {"Aries":4,"Taurus":4,"Gemini":5,"Cancer":5,"Leo":5,"Virgo":3,"Libra":4,"Scorpio":5,"Sagittarius":3,"Capricorn":4,"Aquarius":2,"Pisces":5},
        "Mars": {"Aries":2,"Taurus":3,"Gemini":5,"Cancer":3,"Leo":4,"Virgo":3,"Libra":3,"Scorpio":3,"Sagittarius":2,"Capricorn":4,"Aquarius":3,"Pisces":4},
        "Mercury": {"Aries":5,"Taurus":4,"Gemini":5,"Cancer":5,"Leo":3,"Virgo":5,"Libra":4,"Scorpio":5,"Sagittarius":4,"Capricorn":6,"Aquarius":4,"Pisces":4},
        "Jupiter": {"Aries":6,"Taurus":3,"Gemini":5,"Cancer":5,"Leo":4,"Virgo":5,"Libra":4,"Scorpio":5,"Sagittarius":6,"Capricorn":5,"Aquarius":3,"Pisces":5},
        "Venus": {"Aries":6,"Taurus":7,"Gemini":5,"Cancer":4,"Leo":4,"Virgo":2,"Libra":4,"Scorpio":7,"Sagittarius":3,"Capricorn":3,"Aquarius":2,"Pisces":5},
        "Saturn": {"Aries":2,"Taurus":3,"Gemini":4,"Cancer":2,"Leo":6,"Virgo":2,"Libra":3,"Scorpio":4,"Sagittarius":2,"Capricorn":4,"Aquarius":4,"Pisces":3},
    }

def main():
    print("Testing each planet's BAV contribution independently against AstroSage...")
    # Add testing logic here using the correct charts
    # This script isolate each planet's internal rules (from Sun, from Moon, etc)
    # and compares against the AstroSage reference point by point.
    pass

if __name__ == "__main__":
    main()
