
from app.database_connection import engine

try:
    with engine.connect() as conn:
        print("Connected Successfully ")
except Exception as e:
    print("Connection Failed")
    print(e)

    