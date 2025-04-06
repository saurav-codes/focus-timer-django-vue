from django.core.management.base import BaseCommand
from apps.core.models import Task
from datetime import datetime, timedelta
import pytz


class Command(BaseCommand):
    help = 'Populate the database with fake tasks'

    def handle(self, *args, **options):
        # Remove all existing tasks
        Task.objects.all().delete()
        self.stdout.write(self.style.WARNING("Deleted all existing tasks."))
        today = datetime.now(pytz.utc)

        tasks_data = [
            # Brain Dump Tasks
            {
                "title": "Brainstorm new feature ideas",
                "description": "Generate innovative feature ideas for the next quarter.",
                "is_completed": False,
                "column_date": None,
                "tags": ["Planning", "Innovation"],
            },
            {
                "title": "Research competitor analysis",
                "description": "Analyze top 5 competitors and their feature sets.",
                "is_completed": False,
                "tags": ["Research", "Strategy"],
                "column_date": None,
            },
            {
                "title": "Draft content calendar",
                "description": "Plan content for social media and blog posts.",
                "is_completed": False,
                "tags": ["Marketing", "Planning"],
                "column_date": None,
            },

            # Regular Tasks
            {
                "title": "Code review: Authentication module",
                "description": "Review PR #123 for the new authentication system.",
                "is_completed": False,
                "tags": ["Development", "Security"],
                "column_date": today,
            },
            {
                "title": "Update API documentation",
                "description": "Add new endpoints and update existing documentation.",
                "is_completed": True,
                "tags": ["Documentation", "API"],
                "column_date": today,
            },
            {
                "title": "Weekly team meeting",
                "description": "Discuss sprint progress and upcoming milestones.",
                "is_completed": False,
                "tags": ["Meeting", "Team"],
                "column_date": today + timedelta(days=1),
            },
            {
                "title": "Fix mobile responsiveness",
                "description": "Address UI issues on smaller screens.",
                "is_completed": False,
                "tags": ["Bug", "UI"],
                "column_date": today + timedelta(days=1),
            },
            {
                "title": "Implement dark mode",
                "description": "Add dark mode theme support across all components.",
                "is_completed": False,
                "tags": ["Feature", "UI"],
                "column_date": today - timedelta(days=1),
            },
            {
                "title": "Performance optimization",
                "description": "Optimize database queries and frontend loading.",
                "is_completed": False,
                "tags": ["Performance", "Development"],
                "column_date": today - timedelta(days=1),
            },
            {
                "title": "User feedback analysis",
                "description": "Review and categorize recent user feedback.",
                "is_completed": True,
                "tags": ["Analysis", "User Experience"],
                "column_date": today + timedelta(days=2),
            },
            {
                "title": "Security audit",
                "description": "Conduct monthly security review and updates.",
                "is_completed": False,
                "tags": ["Security", "Maintenance"],
                "column_date": today + timedelta(days=2),
            },
            {
                "title": "Create onboarding tutorial",
                "description": "Design and implement user onboarding flow.",
                "is_completed": False,
                "tags": ["UX", "Documentation"],
                "column_date": today + timedelta(days=3),
            },
            {
                "title": "Update dependencies",
                "description": "Update all project dependencies to latest versions.",
                "is_completed": True,
                "tags": ["Maintenance", "Development"],
                "column_date": today + timedelta(days=3),
            },
            {
                "title": "Implement email notifications",
                "description": "Add email notification system for task updates.",
                "is_completed": False,
                "tags": ["Feature", "Backend"],
                "column_date": today + timedelta(days=4),
            },
            {
                "title": "Create monthly analytics report",
                "description": "Generate and analyze monthly usage statistics.",
                "is_completed": False,
                "tags": ["Analytics", "Reporting"],
                "column_date": today + timedelta(days=4),
            },
        ]

        # Insert sample tasks into the database
        for data in tasks_data:
            task = Task.objects.create(
                title=data["title"],
                description=data["description"],
                is_completed=data["is_completed"],
                column_date=data["column_date"],
            )
            # Add tags separately since TaggableManager needs to be handled after creation
            task.tags.add(",".join(data["tags"]))

            self.stdout.write(self.style.SUCCESS(
                f"Created task: {task.title}"
            ))

        self.stdout.write(self.style.SUCCESS(f"Successfully created {len(tasks_data)} tasks!"))
