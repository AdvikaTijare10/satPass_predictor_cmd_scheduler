import requests
from skyfield.api import EarthSatellite, load, wgs84
from datetime import datetime, timezone, timedelta


NORAD_ID = 51656
URL = f"https://celestrak.org/NORAD/elements/gp.php?CATNR={NORAD_ID}&FORMAT=TLE"

def fetch_sat_tle():
    """Fetches real-time orbital elements from CelesTrak"""
    response = requests.get(URL)
    lines = response.text.strip().splitlines()
    return lines[0], lines[1], lines[2]

def get_pass():
    """
    Calculates raw satellite passes using Skyfield.
    Returns a tuple: (raw_passes_list, sat_object, ground_station_object, sat_name)
    """
    sat_name, line1, line2 = fetch_sat_tle()
    
    sat = EarthSatellite(line1, line2, sat_name)
    ts = load.timescale()
    
    # Coordinates for your Bengaluru Ground Station
    ground_station = wgs84.latlon(13.03265, 77.51567, elevation_m=759)
    
    # Calculate passes from right now until 48 hours from now (days=2)
    start_dt = datetime.now(timezone.utc)
    end_dt = start_dt + timedelta(days=2)
    
    t0 = ts.from_datetime(start_dt)
    t1 = ts.from_datetime(end_dt)
    
    # Find events higher than 10 degrees on the horizon
    times, events = sat.find_events(ground_station, t0, t1, altitude_degrees=10.0)
    
    print(f"🛰️ Found {len(events)} orbital events. Processing passes...")

    raw_passes = []
    
    # Loop through events in chunks of 3 (AOS, Peak, LOS)
    for i in range(0, len(events), 3):
        # Safe boundary check
        if i + 2 >= len(events):
            break
            
        raw_passes.append({
            "aos_time": times[i].utc_datetime(),
            "peak_time": times[i+1],
            "los_time": times[i+2].utc_datetime()
        })
        
    return raw_passes, sat, ground_station, sat_name


