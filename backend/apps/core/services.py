"""All DB write operations for apps.core.model will be here"""

from .models import Task, Project
from .serializers import TaskSerializer
from logging import getLogger
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from .selectors import get_task_future_siblings, get_future_childrens_of_parent_task

logger = getLogger(__name__)


class TaskService:
    def __init__(self, user):
        self.user = user

    def create_task(self, data: dict, post_request: HttpRequest):
        serializer = TaskSerializer(data=data, context={"request": post_request})
        if serializer.is_valid():
            serializer.save()
            logger.info(
                f"Task created: task_id={serializer.instance.pk} by user_id={self.user.id}"
            )
            return serializer.data, True
        return serializer.errors, False

    def update_task(self, task_data: dict):
        logger.info(
            f"Updating task: task_id={task_data['id']} by user_id={self.user.id}"
        )
        series_scope = task_data.pop("series_scope", "single")  # 'single' | 'future'
        # Keep a snapshot of pre-update values for recurrence comparison
        original_task = get_object_or_404(Task, id=task_data["id"], user=self.user)
        serializer = TaskSerializer(original_task, data=task_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            updated_instance: Task = serializer.instance
            logger.info(
                f"Task updated: task_id={task_data['id']} by user_id={self.user.id}"
            )
            # ---- Recurring series propagation -----------------------------
            # if it's a sibling or parent task along with user selecting to update all future instances
            # so we will update/generate future instances
            if series_scope == "future" and (
                updated_instance.recurrence_parent
                or updated_instance.is_rec_task_parent
            ):
                # tags_changed = list(original_task.tags.all()) != list(updated_instance.tags.all())
                # parent will be either recurrence_parent or updated_instance itself
                # incase of it's original task i.e. parent itself.
                # parent_or_sibling = updated_instance.recurrence_parent or updated_instance
                # # Copy attributes
                # # Copy each important field from updated_instance to parent
                # for field_name in Task.SERIES_FIELDS_TO_MONITOR:
                #     # Remove _id suffix if present (for foreign keys)
                #     clean_field_name = field_name.replace("_id", "")
                #     # Get value from updated instance
                #     field_value = getattr(updated_instance, clean_field_name)
                #     # Set the same value on parent
                #     setattr(parent_or_sibling, clean_field_name, field_value)

                # # If this task is a child in a recurring series
                # if updated_instance.recurrence_parent:
                #     parent_or_sibling.save(update_fields=[f.replace("_id", "") for f in Task.SERIES_FIELDS_TO_MONITOR])
                # else:
                #     parent_or_sibling.save()  # already the instance
                # if tags_changed:
                # parent_or_sibling.tags.set(updated_instance.tags.all())

                # Enqueue async regeneration of future siblings
                try:
                    from .tasks import regenerate_recurring_series

                    regenerate_recurring_series(updated_instance.pk)
                except Exception as e:
                    logger.error(
                        f"Failed to enqueue regenerate_recurring_series for parent_id={updated_instance.pk}: {e}",
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
            f"Bulk update order by user_id={self.user.id} for task_ids={[t['id'] for t in tasks]}"
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
            f"Task assigned to project: task_id={task_id} project_id={project_id} by user_id={self.user.id}"
        )
        return TaskSerializer(task).data

    def turn_off_repeat(self, task_id):
        task = get_object_or_404(Task, id=task_id, user=self.user)
        # delete any future siblings/childrens
        future_task = None
        if task.is_rec_task_parent:
            future_task = get_future_childrens_of_parent_task(task)
        else:
            future_task = get_task_future_siblings(task)
        deleted_future_task_ids = list(future_task.values_list("id", flat=True))
        future_task.delete()
        logger.info(
            f"Deleted future siblings for task_id={task_id} by user_id={self.user.id}"
        )
        task.recurrence_rule = None
        task.save()
        logger.info(
            f"Turned off repeat for task_id={task_id} by user_id={self.user.id}"
        )
        return TaskSerializer(task).data, deleted_future_task_ids
