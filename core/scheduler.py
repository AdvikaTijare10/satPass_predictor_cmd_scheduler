
from datetime import datetime, timezone
from sqlmodel import Session, select

from app.database_connection import engine
from app.create_tables.pass_window import PassWindow
from app.create_tables.cmds import Command


COMMAND_DURATIONS = {
    "PING_BEACON": 15,
    "FETCH_TELEMETRY": 60,
    "TRIGGER_CAMERA_PAYLOAD": 120,
}


def run_scheduler_engine():

    with Session(engine) as session:

        now = datetime.now(timezone.utc)

        # ------------------------------------------------------------------
        # Fetch all future passes
        # ------------------------------------------------------------------
        future_passes = session.exec(
            select(PassWindow)
            .where(PassWindow.end_time > now)
            .order_by(PassWindow.start_time.asc())
        ).all()

        if not future_passes:
            print("❌ No future passes available.")
            return

        # ------------------------------------------------------------------
        # Fetch commands waiting to be scheduled
        # ------------------------------------------------------------------
        command_pool = session.exec(
            select(Command)
            .where(
                (Command.status == "PENDING") |
                (Command.status == "DEFERRED")
            )
            .where(Command.pass_window_id == None)
            .order_by(Command.created_at.asc())
        ).all()

        if not command_pool:
            print("📭 No commands waiting for scheduling.")
            return

        # ------------------------------------------------------------------
        # Sort by Priority -> Created Time -> ID
        # ------------------------------------------------------------------
        sorted_commands = sorted(
            command_pool,
            key=lambda cmd: (-cmd.priority, cmd.created_at, cmd.id)
        )

        # ------------------------------------------------------------------
        # Calculate used time in every pass
        # ------------------------------------------------------------------
        pass_used_time = {}

        for p in future_passes:

            scheduled_cmds = session.exec(
                select(Command)
                .where(Command.pass_window_id == p.id)
                .where(Command.status == "SCHEDULED")
            ).all()

            used = 0

            for cmd in scheduled_cmds:

                if (
                    cmd.scheduled_start_offset_sec is not None and
                    cmd.scheduled_end_offset_sec is not None
                ):
                    used += (
                        cmd.scheduled_end_offset_sec -
                        cmd.scheduled_start_offset_sec
                    )

            pass_used_time[p.id] = used

        scheduled_count = 0
        deferred_count = 0

        print("\n🚀 Scheduling Started\n")

        # ------------------------------------------------------------------
        # Try to place every command into earliest pass that fits
        # ------------------------------------------------------------------
        for cmd in sorted_commands:

            duration = COMMAND_DURATIONS.get(
                cmd.command_type,
                30
            )

            assigned = False

            for p in future_passes:

                used = pass_used_time[p.id]

                remaining = p.available_duration_secs - used

                if duration <= remaining:

                    cmd.pass_window_id = p.id
                    cmd.status = "SCHEDULED"

                    cmd.scheduled_start_offset_sec = int(used)
                    cmd.scheduled_end_offset_sec = int(used + duration)

                    cmd.execution_log = (
                        f"Allocated to Pass {p.id} | "
                        f"T+{int(used)}s -> "
                        f"T+{int(used + duration)}s"
                    )

                    pass_used_time[p.id] += duration

                    scheduled_count += 1
                    assigned = True

                    print(
                        f"✅ Command {cmd.id} "
                        f"({cmd.command_type}) "
                        f"-> Pass {p.id} "
                        f"[T+{int(used)}s -> T+{int(used+duration)}s]"
                    )

                    break

            if not assigned:

                cmd.status = "DEFERRED"
                cmd.pass_window_id = None

                cmd.execution_log = (
                    "No future pass has enough remaining duration."
                )

                deferred_count += 1

                print(
                    f"❌ Command {cmd.id} "
                    f"({cmd.command_type}) deferred."
                )

        session.commit()

        print("\n---------------- Scheduler Summary ----------------")
        print(f"Scheduled : {scheduled_count}")
        print(f"Deferred  : {deferred_count}")
        print("---------------------------------------------------")
        print("✅ Scheduler Finished.")


if __name__ == "__main__":
    run_scheduler_engine()
