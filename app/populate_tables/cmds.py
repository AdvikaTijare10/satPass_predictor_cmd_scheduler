# from sqlmodel import Session
# from app.database_connection import engine
# from app.create_tables.cmds import Command
# from app.create_tables.pass_window import PassWindow


# def simulate_user_commands(session: Session):

#     print("🛰️ Simulating command submissions...")

#     commands_to_queue = [

#         Command(
#             command_type="PING_BEACON",
#             priority=1
#         ),

#         Command(
#             command_type="FETCH_TELEMETRY",
#             priority=2
#         ),

#         Command(
#             command_type="TRIGGER_CAMERA_PAYLOAD",
#             priority=3
#         ),

#         Command(
#             command_type="PING_BEACON",
#             priority=5
#         ),

#         Command(
#             command_type="FETCH_TELEMETRY",
#             priority=4
#         )
#     ]

#     for cmd in commands_to_queue:
#         session.add(cmd)

#     session.commit()

#     print(f"✅ Added {len(commands_to_queue)} commands")


# if __name__ == "__main__":

#     with Session(engine) as session:
#         simulate_user_commands(session)



from fastapi import FastAPI, HTTPException
from sqlmodel import Session
from app.database_connection import engine
from app.create_tables.cmds import Command
from app.create_tables.pass_window import PassWindow

app = FastAPI(title="Satellite Ground Station API")

@app.get("/")
def read_root():
    return {"status": "Operational", "system": "Avionics Command Gateway"}

# 🔥 THIS REPLACES YOUR SIMULATION SCRIPT
@app.post("/commands")
def create_command(command_data: Command):
    """
    API Endpoint that accepts a command payload from the frontend
    and writes it directly to AWS RDS.
    """
    try:
        with Session(engine) as session:
            # Enforce that a fresh user-submitted command starts as PENDING
            command_data.status = "PENDING"
            
            # Since the frontend form doesn't pick a pass yet, 
            # make sure it satisfies your database constraint if needed, 
            # or matches how your scheduler query expects it.
            session.add(command_data)
            session.commit()
            session.refresh(command_data)
            
            return {
                "message": "✅ Command successfully queued to AWS RDS", 
                "command_id": command_data.id
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database insertion failed: {str(e)}")