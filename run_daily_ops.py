from app.populate_tables.pass_window import populate_pass_window
from core.scheduler import run_scheduler_engine
from core.orbital import get_pass

def lambda_handler(event=None, context=None):
    """
    This function will be triggered by AWS EventBridge every 24 hours.
    """
    print("🚀 Starting Daily Mission Ops...")
    
    # 1. Update the database with new passes
    try:
        raw_passes, sat, ground_station, sat_name = get_pass()
        populate_pass_window(raw_passes, sat, ground_station, sat_name)
        print("✅ Passes populated successfully.")
    except Exception as e:
        print(f"❌ Error populating passes: {e}")
        return {"status": "error", "message": str(e)}

    # 2. Run the scheduler to pack those new passes
    try:
        run_scheduler_engine()
        print("✅ Scheduler engine finished.")
    except Exception as e:
        print(f"❌ Error running scheduler: {e}")
        return {"status": "error", "message": str(e)}

    return {"status": "success", "message": "Daily mission operations complete."}

if __name__ == "__main__":
    lambda_handler()