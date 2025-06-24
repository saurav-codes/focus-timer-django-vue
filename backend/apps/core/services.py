"""All DB write operations for apps.core.model will be here"""

import datetime
from .models import Task, Project
from .serializers import TaskSerializer
from logging import getLogger
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from .selectors import get_future_siblings, get_past_siblings
from django.db import transaction
from .tasks import notify_frontend

logger = getLogger(__name__)


def update_task_with_new_values(task: Task, updated_task: Task):
    task.title = updated_task.title
    task.description = updated_task.description
    task.start_at = updated_task.start_at
    task.end_at = updated_task.end_at
    task.tags.set(updated_task.tags.all())
    task.project = updated_task.project
    task.save()
    return task


class TaskService:
    def __init__(self, user):
        self.user = user

    def create_task(self, data: dict, post_request: HttpRequest):
        serializer = TaskSerializer(data=data, context={"request": post_request})
        if serializer.is_valid():
            serializer.save()
            logger.info(
                f"Task created: task_id={serializer.instance.pk} by user_id={self.user.id}"  # type:ignore
            )
            return serializer.data, True
        return serializer.errors, False

    def update_task(self, task_data: dict):
        logger.info(
            f"Updating task: task_id={task_data['id']} by user_id={self.user.id}"
        )
        series_scope = task_data.pop(
            "series_scope", "single"
        )  # 'single' | 'future' | 'all'
        # Keep a snapshot of pre-update values for recurrence comparison
        original_task = get_object_or_404(Task, id=task_data["id"], user=self.user)
        serializer = TaskSerializer(original_task, data=task_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            updated_instance: Task = serializer.instance  # type: ignore
            logger.info(
                f"Task updated: task_id={task_data['id']} by user_id={self.user.id}"
            )
            if updated_instance.recurrence_series:
                if series_scope == "all":
                    # update all prev tasks in series
                    # since future tasks will be deleted and regenerated
                    # so we need to update all prev tasks in series
                    prev_tasks = get_past_siblings(updated_instance)
                    updated_tasks = []
                    for task in prev_tasks:
                        updated_tasks.append(
                            update_task_with_new_values(task, updated_instance)
                        )
                    logger.info(
                        f"Updated {len(updated_tasks)} prev tasks in series:\
                        task_id={updated_instance.pk} by user_id={self.user.id}"
                    )
                    notify_frontend.delay(  # type: ignore
                        f"tasks_user_{updated_instance.user.pk}",
                        {
                            "type": "refresh_for_rec_task",
                            "deleted": [t.pk for t in updated_tasks],
                            "created": TaskSerializer(updated_tasks, many=True).data,
                        },
                    )

                # ---- Recurring series propagation -----------------------------
                if series_scope in ["future", "all"]:
                    # Enqueue async regeneration of future siblings
                    try:
                        from .tasks import regenerate_recurring_series

                        regenerate_recurring_series.delay(updated_instance.pk)  # type: ignore
                    except ValueError as e:
                        logger.error(
                            f"Failed to enqueue regenerate_recurring_series\
                            for parent_id={updated_instance.pk}: {e}",
                            exc_info=True,
                        )

            return serializer.data, True
        return serializer.errors, False

    def delete_task(self, task_id):
        task = get_object_or_404(Task, id=task_id, user=self.user)
        task_data = TaskSerializer(task).data
        task.delete()
        logger.info(f"Task deleted: task_id={task_id} by user_id={self.user.id}")
        return task_data

    def update_task_order(self, tasks: list[dict]):
        logger.info(
            f"Bulk update order by user_id={self.user.id}\
            for task_ids={[t['id'] for t in tasks]}"
        )
        for idx, task in enumerate(tasks, start=1):
            task_obj = get_object_or_404(Task, id=task["id"], user=self.user)
            task_obj.order = idx
            task_obj.save()

    def assign_project_to_task(self, task_id, project_id):
        task = get_object_or_404(Task, id=task_id, user=self.user)
        task.project = get_object_or_404(Project, id=project_id, user=self.user)
        task.save()
        logger.info(
            f"Task assigned to project: task_id={task_id}\
            project_id={project_id} by user_id={self.user.id}"
        )
        return TaskSerializer(task).data

    def turn_off_repeat(self, task_id):
        task = get_object_or_404(Task, id=task_id, user=self.user)
        if not task.recurrence_series:
            return TaskSerializer(task).data, []
        # delete any future siblings/childrens
        future_task = get_future_siblings(task=task)
        deleted_future_task_ids = list(future_task.values_list("id", flat=True))
        deleted_tasks, _ = future_task.delete()
        logger.info(
            f"Deleted {deleted_tasks} future siblings with \
            task_ids = {deleted_future_task_ids} for task_id={task_id}\
            by user_id={self.user.id}"
        )
        task.recurrence_series = None
        task.save()
        task.refresh_from_db()
        logger.info(
            f"Turned off repeat for task_id={task_id} by user_id={self.user.id}"
        )
        return TaskSerializer(task).data, deleted_future_task_ids

    def toggle_task_completion(self, task_id):
        task = get_object_or_404(Task, id=task_id, user=self.user)
        logger.info(
            f"Toggling completion: task_id={task_id} old_status={task.is_completed} by user_id={self.user.id}"
        )
        task.is_completed = not task.is_completed
        task.save()
        task.refresh_from_db()
        logger.info(
            f"New completion status: task_id={task_id} new_status={task.is_completed}"
        )
        return TaskSerializer(task).data


def generate_rec_tasks_for_parent(
    parent_task: Task, occurences_dates: list[datetime.datetime]
):
    results = []
    for occurence_date in occurences_dates:
        with transaction.atomic():
            # make sure we don't create two task for same column_date & recurrence_parent
            child, created = Task.objects.get_or_create(
                user=parent_task.user,
                title=parent_task.title,
                description=parent_task.description,
                order=parent_task.order,
                is_completed=False,
                duration=parent_task.duration,
                column_date=occurence_date,
                start_at=parent_task.start_at,
                end_at=parent_task.end_at,
                recurrence_series=parent_task.recurrence_series,
                project=parent_task.project,
                status=Task.ON_BOARD,  # TODO: what if task is on calendar?
            )
            if created:
                # copy over tags
                child.tags.set(parent_task.tags.all())

            action = "created" if created else "updated"
            msg = f"Recurring task {action}: parent_task_id={parent_task.pk}\
                child_task_id={child.pk} date={occurence_date}, user_id:{parent_task.user.pk}"
            logger.info(msg)
            results.append(msg)
    return results
