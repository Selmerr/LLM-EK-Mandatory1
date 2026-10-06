import pytest
from pydantic import ValidationError

from app.models.task import TaskCreate, TaskUpdate, TaskResponse


VALID_TASK = {
    "title": "Test task",
    "description": "Test description",
    "status": "pending",
    "priority": 1,
    "due_date": "2026-12-31",
}


def test_task_create_accepts_valid_task():
    task = TaskCreate(**VALID_TASK)

    assert task.title == "Test task"
    assert task.description == "Test description"
    assert task.status == "pending"
    assert task.priority == 1
    assert task.due_date == "2026-12-31"


def test_task_create_requires_all_fields():
    with pytest.raises(ValidationError):
        TaskCreate(title="Incomplete task")


def test_task_update_accepts_valid_task():
    task = TaskUpdate(**VALID_TASK)

    assert task.title == "Test task"
    assert task.priority == 1


def test_task_update_requires_all_fields():
    with pytest.raises(ValidationError):
        TaskUpdate(title="Incomplete update")


def test_task_response_accepts_valid_response():
    task = TaskResponse(
        id="test-id",
        **VALID_TASK,
        created_at="2026-10-06T18:00:00",
        updated_at="2026-10-06T18:00:00",
    )

    assert task.id == "test-id"
    assert task.title == "Test task"
    assert task.priority == 1
