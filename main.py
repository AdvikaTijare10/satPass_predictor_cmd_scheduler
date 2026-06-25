from fastapi import FastAPI, HTTPException
from sqlmodel import Session, select
from typing import List
from datetime import datetime, timezone

from app.database_connection import engine
from app.create_tables.cmds import Command
from app.create_tables.pass_window import PassWindow
from core.scheduler import run_scheduler_engine
from app.populate_tables.pass_window import populate_pass_window,get_pass

app = FastAPI(title="Satellite Ground Station API")

# 1. Root Check
@app.get("/")
def read_root():
    return {"status": "Operational", "system": "Avionics Command Gateway"}

# 2. Add a new command (POST)
@app.post("/commands")
def create_command(command_data: Command):
    try:
        with Session(engine) as session:
            command_data.status = "PENDING"
            session.add(command_data)
            session.commit()
            session.refresh(command_data)
            run_scheduler_engine()
            return {"message": "✅ Command queued", "command_id": command_data.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/calculate-passes")
def calculate_passes():
    # Call your orbital engine logic here
    # This is the exact same logic you were going to put in Lambda
    raw_passes, sat, ground_station, sat_name = get_pass()
    populate_pass_window(raw_passes, sat, ground_station, sat_name)
    return {"message": "Passes updated!"}

@app.post("/scheduler/run")
def trigger_scheduler():
    try:
        run_scheduler_engine()
        return {"status": "Success", "message": "Scheduler pipeline processed successfully."}
    except Exception as e:
        print(f"DEBUG ERROR: {e}") 
        raise HTTPException(status_code=500, detail=str(e))

# 3. Get upcoming passes (GET)
@app.get("/passes/future")
def get_future_passes():
    try:
        with Session(engine) as session:
            now = datetime.now(timezone.utc)
            statement = select(PassWindow).where(PassWindow.end_time > now).order_by(PassWindow.start_time.asc())
            results = session.exec(statement).all()
            return [p.model_dump() for p in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 4. Get scheduled timeline (GET)
@app.get("/commands/timeline")
def get_scheduled_timeline():
    try:
        with Session(engine) as session:
            statement = select(Command).where(Command.status == "SCHEDULED").order_by(Command.scheduled_start_offset_sec.asc())
            results = session.exec(statement).all()
            return [c.model_dump() for c in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


