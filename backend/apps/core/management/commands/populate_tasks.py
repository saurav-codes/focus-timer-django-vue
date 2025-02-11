from django.core.management.base import BaseCommand
from apps.core.models import Task

class Command(BaseCommand):
    help = 'Populate the database with fake tasks'

    def handle(self, *args, **options):
        # Remove all existing tasks
        Task.objects.all().delete()
        self.stdout.write(self.style.WARNING("Deleted all existing tasks."))

        tasks_data = [
            {
                "title": "Write project proposal",
                "description": "Prepare an outline and draft for the new project proposal.",
                "status": "todo",
            },
            {
                "title": "Review team code",
                "description": "Go through the recent merge request and provide feedback.",
                "status": "in_progress",
            },
            {
                "title": "Attend stand-up meeting",
                "description": "Discuss daily progress and any blockers in the morning meeting.",
                "status": "todo",
            },
            {
                "title": "Design UI mockups",
                "description": "Create wireframes for the new dashboard feature.",
                "status": "in_progress",
            },
            {
                "title": "Fix login bug",
                "description": "Resolve the issue with user authentication on mobile devices.",
                "status": "done",
            },
            {
                "title": "Update documentation",
                "description": "Revise API endpoints and usage documentation.",
                "status": "done",
            },
            {
                "title": "Plan sprint backlog",
                "description": "Organize and prioritize tasks for the upcoming sprint.",
                "status": "todo",
            },
        ]

        # Insert sample tasks into the database
        for idx, data in enumerate(tasks_data):
            task = Task.objects.create(
                title=data["title"],
                description=data["description"],
                status=data["status"],
                order=idx
            )
            self.stdout.write(self.style.SUCCESS(
                f"Created task: {task.title} (Status: {task.status})"
            ))

        self.stdout.write(self.style.SUCCESS("Fake tasks have been populated successfully.")) 