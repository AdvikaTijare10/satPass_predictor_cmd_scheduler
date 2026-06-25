from datetime import datetime,timezone
from typing import Optional
from sqlmodel import SQLModel,Field

class Command(SQLModel,table=True):
    __tablename__="commands"

    id: Optional[int] = Field(default=None, primary_key=True)
    pass_window_id: Optional[int] = Field(default=None, foreign_key="pass_windows.id")
    command_type: str
    # Starts as "PENDING". Will change to "EXECUTING", "SUCCESS", or "FAILED".
    status: str = Field(default="PENDING")
    priority: int = Field(default=1)
    # Keeps track of exactly when the user submitted this command
    created_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc))
    
    # Store text details or logs here if something goes wrong during execution
    execution_log: Optional[str] = Field(default=None)
    
    scheduled_start_offset_sec: Optional[int] = Field(default=None)

    scheduled_end_offset_sec: Optional[int] = Field(default=None)