from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from sqlalchemy import Column, DateTime

class PassWindow(SQLModel, table=True):
    __tablename__ = "pass_windows"

 
    id: Optional[int] = Field(default=None, primary_key=True)    
    satellite_name: str
     
    start_time: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    end_time: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    
    available_duration_secs: float
    max_elevation_deg: float    
 
    status: str = Field(default="PENDING")
