from sqlalchemy import Column, Integer, String, Enum, DateTime, func
from base import Base
from enum import Enum as PyEnum
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TaskStatus(PyEnum):
    pending = "pending"
    in_progress = "in_progress"
    done = "done"

class Task(Base):
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(Enum(TaskStatus), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str
    created_at: datetime
    
class TaskCreate(BaseModel):
    title: str
    description: str = None
    status: TaskStatus

class TaskUpdate(BaseModel):
    title: str = None
    description: str = None
    status: TaskStatus = None
