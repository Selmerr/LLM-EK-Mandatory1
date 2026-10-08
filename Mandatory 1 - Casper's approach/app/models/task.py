from datetime import datetime

from pydantic import BaseModel

class TaskCreate(BaseModel):
    title: str
    description: str
    status: str
    priority: int
    due_date: str

class TaskUpdate(BaseModel):
    title: str
    description: str
    status: str
    priority: int
    due_date: str

class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    status: str
    priority: int
    due_date: str
    created_at: str
    updated_at: str

class Error(BaseModel):
    detail: str