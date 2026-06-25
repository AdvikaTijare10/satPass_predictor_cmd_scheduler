from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


# 'table=True' tells SQLModel: "This isn't just a regular Python class. 
# Make a real database table out of this!"
class PassWindow(SQLModel, table=True):
    __tablename__ = "pass_windows" # This will be the actual name of the table in Postgres

    # id is a unique number (1, 2, 3...) assigned to every single pass automatically.
    # primary_key=True ensures no two rows ever share the same ID number.
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # These match your Skyfield tracking script perfectly:
    satellite_name: str
    start_time: datetime
    end_time: datetime
    available_duration_secs: float
    max_elevation_deg: float
    
    # Every pass starts as "PENDING". Later, our clock background engine 
    # will switch it to "ACTIVE" and "COMPLETED".
    status: str = Field(default="PENDING")

