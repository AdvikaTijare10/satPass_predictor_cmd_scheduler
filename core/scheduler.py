from datetime import datetime, timezone, timedelta
from sqlmodel import Session, select
from app.database_connection import engine
from app.create_tables.pass_window import PassWindow
from app.create_tables.cmds import Command

COMMAND_DURATIONS = {
    "PING_BEACON": 15,
    "FETCH_TELEMETRY": 60,
    "TRIGGER_CAMERA_PAYLOAD": 120,
}

def sync_mission_status():
    """Updates statuses: PENDING -> ACTIVE -> COMPLETED"""
    with Session(engine) as session:
        now = datetime.now(timezone.utc)
        
        # 1. Sync Pass Windows
        passes = session.exec(select(PassWindow)).all()
        for p in passes:
            if now > p.end_time:
                p.status = "COMPLETED"
            elif p.start_time <= now <= p.end_time:
                p.status = "ACTIVE"
            else:
                p.status = "PENDING"
            session.add(p)

        # 2. Sync Commands
        commands = session.exec(select(Command).where(Command.pass_window_id != None)).all()
        for cmd in commands:
            pass_win = session.get(PassWindow, cmd.pass_window_id)
            if not pass_win: continue
            
            cmd_start = pass_win.start_time + timedelta(seconds=cmd.scheduled_start_offset_sec or 0)
            cmd_end = pass_win.start_time + timedelta(seconds=cmd.scheduled_end_offset_sec or 0)
            
            if now > cmd_end:
                cmd.status = "COMPLETED"
            elif cmd_start <= now <= cmd_end:
                cmd.status = "ACTIVE"
            session.add(cmd)
        session.commit()

def run_scheduler_engine():
    with Session(engine) as session:
        now = datetime.now(timezone.utc)

        # 1. Fetch all future passes
        future_passes = session.exec(
            select(PassWindow)
            .where(PassWindow.end_time > now)
            .order_by(PassWindow.start_time.asc())
        ).all()

        if not future_passes:
            print("No future passes available.")
            return

        # 2. Reset scheduling for all commands that are currently SCHEDULED or DEFERRED
        all_relevant_cmds = session.exec(
            select(Command).where(
                (Command.status == "SCHEDULED") | (Command.status == "DEFERRED")
            )
        ).all()

        for cmd in all_relevant_cmds:
            cmd.pass_window_id = None
            cmd.status = "PENDING"
            cmd.scheduled_start_offset_sec = None
            cmd.scheduled_end_offset_sec = None
            cmd.execution_log = "Reset for re-optimization"
            session.add(cmd)
        
        # 3. Fetch all PENDING commands (includes those we just reset)
        command_pool = session.exec(select(Command).where(Command.status == "PENDING")).all()

        # 4. Sort by Priority (High to Low) -> Created Time (Oldest first)
        sorted_commands = sorted(
            command_pool,
            key=lambda cmd: (-cmd.priority, cmd.created_at, cmd.id)
        )

        # 5. Initialize pass usage tracking
        pass_used_time = {p.id: 0 for p in future_passes}

        print("\nScheduling Started (Priority Optimized)\n")

        # 6. Assign commands
        for cmd in sorted_commands:
            duration = COMMAND_DURATIONS.get(cmd.command_type, 30)
            assigned = False

            for p in future_passes:
                used = pass_used_time[p.id]
                remaining = p.available_duration_secs - used

                if duration <= remaining:
                    cmd.pass_window_id = p.id
                    cmd.status = "SCHEDULED"
                    cmd.scheduled_start_offset_sec = int(used)
                    cmd.scheduled_end_offset_sec = int(used + duration)
                    cmd.execution_log = f"Allocated to Pass {p.id} | T+{int(used)}s -> T+{int(used + duration)}s"
                    
                    pass_used_time[p.id] += duration
                    assigned = True
                    break

            if not assigned:
                cmd.status = "DEFERRED"
                cmd.execution_log = "No pass has enough capacity."

            session.add(cmd)

        session.commit()
        print("Scheduler Finished.")

if __name__ == "__main__":
    run_scheduler_engine()