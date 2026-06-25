from datetime import timedelta
from sqlmodel import Session, select
from app.database_connection import engine
from app.create_tables.pass_window import PassWindow
from core.orbital import get_pass

def populate_pass_window(raw_passes, sat, ground_station, sat_name):
    """
    Checks for duplicates against Postgres and writes unique passes to the database.
    """
    # We open our workspace session cleanly
    with Session(engine) as session:
        
        for p in raw_passes:
            aos_time = p["aos_time"]
            peak_time = p["peak_time"]
            los_time = p["los_time"]
            
            # 🔍 THE SAFETY CHECK: Search our Postgres database table
            time_buffer = timedelta(minutes=5)
            lower_bound = aos_time - time_buffer
            upper_bound = aos_time + time_buffer
            
            # 🔍 Look for any pass starting within this 5-minute window
            search_query = select(PassWindow).where(
                PassWindow.satellite_name == sat_name.strip(),
                PassWindow.start_time >= lower_bound,
                PassWindow.start_time <= upper_bound
            )
            
            search_result = session.exec(search_query).first()
            
            if search_result is not None:
                print(f"⏭️ Skipping duplicate pass matching window around {aos_time}")
                continue
            
            # Calculate peak elevation angle if it's a brand new pass
            diff = sat - ground_station
            topocentric = diff.at(peak_time)
            alt, az, dist = topocentric.altaz()
            
            duration_seconds = (los_time - aos_time).total_seconds()
            
            # 📦 PACK THE DATA
            db_pass = PassWindow(
                satellite_name=sat_name.strip(),
                start_time=aos_time,
                end_time=los_time,
                available_duration_secs=round(duration_seconds, 2),
                max_elevation_deg=round(float(alt.degrees), 2),
                status="PENDING"
            )
            
            # Place into workspace
            session.add(db_pass)
        
        # 🚚 THE COMMIT: Sent all new passes to Postgres at once
        session.commit()
        
    print("✨ Database population complete! All unique passes pushed to PostgreSQL.")


if __name__ == "__main__":
    
    raw_passes, sat, ground_station, sat_name = get_pass()
    populate_pass_window(raw_passes, sat, ground_station, sat_name)