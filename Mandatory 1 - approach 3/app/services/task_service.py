from typing import Dict, List, Optional
from app.models import TaskCreate, TaskUpdate, TaskResponse
from app.repositories.sqlite_repo import SQLiteRepo
import uuid
import datetime

class TaskService:
    def __init__(self):
        self.repo = SQLiteRepo()

    def create_task(self, task: TaskCreate) -> TaskResponse:
        task_data = task.dict()
        task_data["id"] = str(uuid.uuid4())
        task_data["created_at"] = datetime.datetime.now().isoformat()
        task_data["updated_at"] = datetime.datetime.now().isoformat()
        self.repo.create(task_data)
        return TaskResponse(**task_data)

    def get_task(self, task_id: str) -> Optional[TaskResponse]:
        task_data = self.repo.get(task_id)
        if not task_data:
            return None
        return TaskResponse(**task_data)

    def update_task(self, task_id: str, task: TaskUpdate) -> Optional[TaskResponse]:
        task_data = self.repo.get(task_id)
        if not task_data:
            return None
        update_data = task.dict(exclude_unset=True)
        task_data.update(update_data)
        task_data["updated_at"] = datetime.datetime.now().isoformat()
        self.repo.update(task_id, task_data)
        return TaskResponse(**task_data)

    def delete_task(self, task_id: str) -> None:
        task_data = self.repo.get(task_id)
        if task_data:
            self.repo.delete(task_id)

    def get_tasks(self) -> dict:
        tasks = self.repo.list()
        return {
            "tasks": [TaskResponse(**task) for task in tasks],
            "total": len(tasks)
        }