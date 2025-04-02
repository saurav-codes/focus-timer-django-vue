from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.core.models import Task
from datetime import timedelta

class Command(BaseCommand):
    help = 'Update task dates to spread across yesterday, today, and tomorrow'

    def handle(self, *args, **options):
        # Get today's date at midnight for consistent dating
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=7)
        after_next_week = today + timedelta(days=14)
        next_month = today + timedelta(days=30)

        # Get all tasks ordered by creation date
        tasks = Task.objects.all().order_by('created_at')
        total_tasks = tasks.count()

        if total_tasks == 0:
            self.stdout.write(self.style.WARNING("No tasks found. Please run populate_tasks first."))
            return

        date_assignments = [
            (yesterday, 2),    # 2 tasks for yesterday
            (today, 2),        # 2 tasks for today
            (tomorrow, 2),     # 2 tasks for tomorrow
            (next_week, 1),    # 1 task for next week
            (after_next_week, 1), # 1 task for after next week
        ]

        current_index = 0
        for date, num_tasks in date_assignments:
            for _ in range(num_tasks):
                if current_index >= total_tasks:
                    break

                task = tasks[current_index]
                task.created_at = date
                task.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Updated task '{task.title}' to date: {date.strftime('%Y-%m-%d')}"
                    )
                )
                current_index += 1

        # If there are any remaining tasks, set them to next_month
        for i in range(current_index, total_tasks):
            task = tasks[i]
            task.created_at = next_month
            task.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Updated task '{task.title}' to date: {next_month.strftime('%Y-%m-%d')}"
                )
            )

        self.stdout.write(self.style.SUCCESS("Successfully updated all task dates"))