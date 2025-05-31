import pytest
import json
from django.urls import reverse
from apps.core.models import Task
from datetime import timedelta, datetime, timezone


@pytest.mark.django_db(transaction=True)
def test_complete_task_workflow(authenticated_client, authenticated_user):
    """
    Test a complete workflow for creating, updating, and completing a task.
    This simulates a real user journey through the application.
    """
    # 1. Create a project first
    project_url = reverse("create-project")
    project_data = {
        "user": authenticated_user.id,
        "title": "Project Workflow",
        "description": "A project for testing workflow",
    }

    project_response = authenticated_client.post(
        project_url, data=json.dumps(project_data), content_type="application/json"
    )
    assert project_response.status_code == 201
    project_id = project_response.json()["id"]

    # 2. Create a task in the "brain dump" (without a column_date)
    tasks_url = reverse("tasks")
    task_data = {
        "user": authenticated_user.id,
        "title": "Workflow Task",
        "description": "A task for testing workflow",
        "order": 1,
        "duration": "00:45:00",  # 45 minutes
        "project": project_id,
        "tags": ["workflow", "test"],
    }

    task_response = authenticated_client.post(
        tasks_url, data=json.dumps(task_data), content_type="application/json"
    )
    assert task_response.status_code == 201
    task_id = task_response.json()["id"]

    # 3. Move the task to a kanban column (today's column)
    task_detail_url = reverse("task-detail", args=[task_id])
    today = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    update_task_data = {
        "user": authenticated_user.id,
        "title": "Workflow Task",
        "description": "A task for testing workflow",
        "order": 1,
        "duration": "00:45:00",
        "project": project_id,
        "tags": ["workflow", "test"],
        "column_date": today,
    }

    update_response = authenticated_client.put(
        task_detail_url,
        data=json.dumps(update_task_data),
        content_type="application/json",
    )
    assert update_response.status_code == 200
    assert update_response.json()["column_date"] is not None

    # 4. Schedule the task on the calendar
    now = datetime.now(timezone.utc)
    start = now.replace(hour=10, minute=0, second=0, microsecond=0)
    end = start + timedelta(minutes=45)

    calendar_update_data = {
        "user": authenticated_user.id,
        "title": "Workflow Task",
        "description": "A task for testing workflow",
        "order": 1,
        "duration": "00:45:00",
        "project": project_id,
        "tags": ["workflow", "test"],
        "column_date": today,
        "start_at": start.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "end_at": end.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    }

    calendar_response = authenticated_client.put(
        task_detail_url,
        data=json.dumps(calendar_update_data),
        content_type="application/json",
    )
    assert calendar_response.status_code == 200
    assert calendar_response.json()["start_at"] is not None
    assert calendar_response.json()["end_at"] is not None

    # 5. Mark the task as completed
    toggle_url = reverse("toggle-task-completion", args=[task_id])
    completion_response = authenticated_client.post(toggle_url)
    assert completion_response.status_code == 200

    # Verify the task is now marked as completed
    task_response = authenticated_client.get(task_detail_url)
    assert task_response.status_code == 200
    assert task_response.json()["is_completed"] is True

    # 6. Delete the task
    delete_response = authenticated_client.delete(task_detail_url)
    assert delete_response.status_code == 204

    # Verify the task has been deleted
    assert not Task.objects.filter(id=task_id).exists()


@pytest.mark.django_db(transaction=True)
def test_kanban_board_workflow(authenticated_client, authenticated_user):
    """
    Test the kanban board workflow, including creating tasks
    and moving them between columns.
    """
    tasks_url = reverse("tasks")

    # Create three tasks for different days (columns)
    today = datetime.now(timezone.utc)
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)

    # 1. Create a "yesterday" task
    yesterday_task_data = {
        "user": authenticated_user.id,
        "title": "Yesterday Task",
        "description": "A task for yesterday",
        "order": 1,
        "column_date": yesterday.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "tags": ["yesterday"],
    }

    yesterday_response = authenticated_client.post(
        tasks_url, data=json.dumps(yesterday_task_data), content_type="application/json"
    )
    assert yesterday_response.status_code == 201
    yesterday_task_id = yesterday_response.json()["id"]

    # 2. Create a "today" task
    today_task_data = {
        "user": authenticated_user.id,
        "title": "Today Task",
        "description": "A task for today",
        "order": 1,
        "column_date": today.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "tags": ["today"],
    }

    today_response = authenticated_client.post(
        tasks_url, data=json.dumps(today_task_data), content_type="application/json"
    )
    assert today_response.status_code == 201
    today_task_id = today_response.json()["id"]

    # 3. Create a "brain dump" task (no column_date)
    brain_dump_task_data = {
        "user": authenticated_user.id,
        "title": "Brain Dump Task",
        "description": "A task in the brain dump",
        "order": 1,
        "tags": ["braindump"],
    }

    brain_dump_response = authenticated_client.post(
        tasks_url,
        data=json.dumps(brain_dump_task_data),
        content_type="application/json",
    )
    assert brain_dump_response.status_code == 201
    brain_dump_task_id = brain_dump_response.json()["id"]

    # 4. Move the "yesterday" task to "tomorrow"
    yesterday_task_url = reverse("task-detail", args=[yesterday_task_id])

    move_data = {
        "user": authenticated_user.id,
        "title": "Yesterday Task",
        "description": "A task for yesterday",
        "order": 1,
        "column_date": tomorrow.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),  # Move to tomorrow
        "tags": ["yesterday", "moved"],
    }

    move_response = authenticated_client.put(
        yesterday_task_url, data=json.dumps(move_data), content_type="application/json"
    )
    assert move_response.status_code == 200

    # 5. Move the "brain dump" task to "today"
    brain_dump_task_url = reverse("task-detail", args=[brain_dump_task_id])

    move_brain_dump_data = {
        "user": authenticated_user.id,
        "title": "Brain Dump Task",
        "description": "A task from the brain dump, now in today column",
        "order": 2,  # Should appear after the existing "today" task
        "column_date": today.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),  # Move to today
        "tags": ["braindump", "moved"],
    }

    move_brain_dump_response = authenticated_client.put(
        brain_dump_task_url,
        data=json.dumps(move_brain_dump_data),
        content_type="application/json",
    )
    assert move_brain_dump_response.status_code == 200

    # 6. Reorder the tasks in the "today" column
    reorder_data = {
        "action": "update_order",
        "tasks": [
            {"id": brain_dump_task_id},  # Brain dump task now first
            {"id": today_task_id},  # Today task now second
        ],
    }

    reorder_response = authenticated_client.put(
        tasks_url, data=json.dumps(reorder_data), content_type="application/json"
    )
    assert reorder_response.status_code == 200

    # 7. Verify final task status
    today_column_filter = f"{tasks_url}?column_date__date={today.strftime('%Y-%m-%d')}"
    today_column_response = authenticated_client.get(today_column_filter)
    assert today_column_response.status_code == 200

    tasks_in_today = today_column_response.json()
    assert len(tasks_in_today) == 2

    # Check ordering
    assert tasks_in_today[0]["id"] == brain_dump_task_id  # Brain dump task first
    assert tasks_in_today[0]["order"] == 1
    assert tasks_in_today[1]["id"] == today_task_id  # Today task second
    assert tasks_in_today[1]["order"] == 2
