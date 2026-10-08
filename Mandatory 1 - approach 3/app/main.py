from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional
from datetime import datetime

from app.models.task import TaskCreate, TaskUpdate, TaskResponse, Error

class TaskService:
    def create_task(self, task: TaskCreate) -> TaskResponse:
        """Create a new task and return the response"""
        ...

    def get_task(self, task_id: str) -> Optional[TaskResponse]:
        """Get a task by ID"""
        ...

    def update_task(self, task_id: str, task: TaskUpdate) -> TaskResponse:
        """Update a task by ID"""
        ...

    def delete_task(self, task_id: str) -> None:
        """Delete a task by ID"""
        ...

    def get_tasks(self) -> dict:
        """Get all tasks with total count"""
        ...

app = FastAPI()

def get_task_service():
    """Dependency to get the task service"""
    return TaskService()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(content={"status": "healthy", "message": "Task API is running"})

@app.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_task(task: TaskCreate, service: TaskService = Depends(get_task_service)):
    """Create a new task"""
    task_response = service.create_task(task)
    return task_response

@app.get("/tasks", response_model=dict)
async def get_tasks(service: TaskService = Depends(get_task_service)):
    """Get all tasks"""
    tasks_data = service.get_tasks()
    return {
        "tasks": tasks_data["tasks"],
        "total": tasks_data["total"]
    }

@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, service: TaskService = Depends(get_task_service)):
    """Get a task by ID"""
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task

@app.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task: TaskUpdate, service: TaskService = Depends(get_task_service)):
    """Update a task by ID"""
    task = service.update_task(task_id, task)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str, service: TaskService = Depends(get_task_service)):
    """Delete a task by ID"""
    service.delete_task(task_id)
    return None