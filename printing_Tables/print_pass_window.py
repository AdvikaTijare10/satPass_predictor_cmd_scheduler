from sqlmodel import select,Session
from app.create_tables.pass_window import PassWindow
from app.database_connection import engine

def print_pass_windows(session: Session):
    """
    Fetches all entries from the pass_windows table in AWS RDS
    and prints them elegantly to the terminal.
    """
    print("\n🔍 Fetching pass windows from AWS RDS...")
    
    # Run a SELECT * FROM pass_windows query
    statement = select(PassWindow)
    results = session.exec(statement).all()
    
    if not results:
        print("📭 The pass_windows table is currently empty.")
        return

    print("-" * 60)
    for p in results:
        print(f"ID: {p.id} | Sat: {p.satellite_name} | AOS: {p.start_time} | LOS: {p.end_time} | Available_Duration: {p.available_duration_secs} | Max El: {p.max_elevation_deg}° | Status: {p.status}")
    print("-" * 60)

if __name__ == "__main__":
    # Open a clean session to AWS RDS and run the printer
    with Session(engine) as session:
        print_pass_windows(session)
