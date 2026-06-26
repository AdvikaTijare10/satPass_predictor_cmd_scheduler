from sqlmodel import SQLModel, create_engine, Session
from app.config import settings



engine = create_engine(settings.DATABASE_URL, echo=True)

def init_db():
    """
    The Construction Worker:
    This function looks at our blueprints (models) and physically builds 
    the corresponding tables inside your Postgres 'ground_station' database.
    """
    from app.create_tables.pass_window import PassWindow
    from app.create_tables.cmds import Command

    SQLModel.metadata.create_all(engine)

def get_session():
    """
    The Mail Bin Provider:
    This creates a safe workspace (session) whenever a part of our app 
    needs to add or read data, ensuring it closes cleanly when done.
    """
    with Session(engine) as session:
        yield session


