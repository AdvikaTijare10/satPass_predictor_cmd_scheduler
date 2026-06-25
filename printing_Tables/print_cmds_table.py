from sqlmodel import select, Session
from app.create_tables.cmds import Command
from app.database_connection import engine


def print_commands(session: Session):
    """
    Fetches all entries from the commands table in AWS RDS
    and prints them elegantly to the terminal.
    """

    print("\n🔍 Fetching commands from AWS RDS...")

    # SELECT * FROM commands
    statement = select(Command)
    results = session.exec(statement).all()

    if not results:
        print("📭 The commands table is currently empty.")
        return

    print("-" * 120)

    for cmd in results:
        print(
            f"ID: {cmd.id} | "
            f"Pass_ID: {cmd.pass_window_id} | "
            f"Type: {cmd.command_type} | "
            f"Status: {cmd.status} | "
            f"Priority: {cmd.priority} | "
            f"Created_At: {cmd.created_at} | "
            f"Execution_Log: {cmd.execution_log} |"
            f"scheduled_start_offset_sec: {cmd.scheduled_start_offset_sec} |"
            f"scheduled_end_offset_sec: {cmd.scheduled_end_offset_sec} "
        )

    print("-" * 120)


if __name__ == "__main__":

    with Session(engine) as session:
        print_commands(session)