from django.core.management.base import BaseCommand
from apps.core.models import Task
from taggit.models import Tag
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
import pytz
from django.utils.dateparse import parse_duration

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate the database with fake tasks'

    def handle(self, *args, **options):
        # Remove all existing tasks
        Task.objects.all().delete()
        # either create a new user or use the existing one
        user = User.objects.filter(email='raju@gmail.com').first()
        if not user:
            print("didn't find user, creating one")
            user = User.objects.create_user(
                first_name='raju test user',
                email='raju@gmail.com',
                password='raju123'
            )
        else:
            print(f"found user {user.email} so using it to assign tasks")
        self.stdout.write(self.style.WARNING("Deleted all existing tasks."))
        today = datetime.now(pytz.utc)

        tasks_data = [
            # Brain Dump Tasks
            {
                "title": "Brainstorm new feature ideas",
                "description": "Generate innovative feature ideas for the next quarter.",
                "is_completed": False,
                "status": Task.BRAINDUMP,
                "column_date": None,
                "tags": ["Planning", "Innovation"],
                "planned_duration": "00:20:00",
            },
            {
                "title": "Research competitor analysis",
                "description": "Analyze top 5 competitors and their feature sets.",
                "is_completed": False,
                "status": Task.BRAINDUMP,
                "tags": ["Research", "Strategy"],
                "column_date": None,
                "planned_duration": "00:30:00",
            },
            {
                "title": "Draft content calendar",
                "description": "Plan content for social media and blog posts.",
                "is_completed": False,
                "status": Task.BRAINDUMP,
                "tags": ["Marketing", "Planning"],
                "column_date": None,
                "planned_duration": "01:00:00",
            },

            # Regular Tasks
            {
                "title": "Code review: Authentication module",
                "description": "Review PR #123 for the new authentication system.",
                "is_completed": False,
                "status": Task.ON_BOARD,
                "tags": ["Development", "Security"],
                "column_date": today,
                "planned_duration": "00:30:00",
            },
            {
                "title": "Update API documentation",
                "description": "Add new endpoints and update existing documentation.",
                "is_completed": True,
                "status": Task.ON_BOARD,
                "tags": ["Documentation", "API"],
                "column_date": today,
                "planned_duration": "00:40:00",
            },
            {
                "title": "Weekly team meeting",
                "description": "Discuss sprint progress and upcoming milestones.",
                "is_completed": False,
                "tags": ["Meeting", "Team"],
                "status": Task.ON_BOARD,
                "column_date": today + timedelta(days=1),
                "planned_duration": "00:80:00",
            },
            {
                "title": "Fix mobile responsiveness",
                "description": "Address UI issues on smaller screens.",
                "is_completed": False,
                "tags": ["Bug", "UI"],
                "status": Task.ON_BOARD,
                "column_date": today + timedelta(days=1),
                "planned_duration": "00:30:00",
            },
            {
                "title": "Implement dark mode",
                "description": "Add dark mode theme support across all components.",
                "is_completed": False,
                "tags": ["Feature", "UI"],
                "status": Task.ON_BOARD,
                "column_date": today - timedelta(days=1),
                "planned_duration": "00:30:00",
            },
            {
                "title": "Performance optimization",
                "description": "Optimize database queries and frontend loading.",
                "is_completed": False,
                "tags": ["Performance", "Development"],
                "status": Task.ON_BOARD,
                "column_date": today - timedelta(days=1),
                "planned_duration": "00:30:00",
            },
            {
                "title": "User feedback analysis",
                "description": "Review and categorize recent user feedback.",
                "is_completed": True,
                "tags": ["Analysis", "User Experience"],
                "status": Task.ON_BOARD,
                "column_date": today + timedelta(days=2),
                "planned_duration": "00:30:00",
            },
            {
                "title": "Security audit",
                "description": "Conduct monthly security review and updates.",
                "is_completed": False,
                "tags": ["Security", "Maintenance"],
                "status": Task.ON_BOARD,
                "column_date": today + timedelta(days=2),
                "planned_duration": "00:30:00",
            },
            {
                "title": "Create onboarding tutorial",
                "description": "Design and implement user onboarding flow.",
                "is_completed": False,
                "tags": ["UX", "Documentation"],
                "status": Task.ON_BOARD,
                "column_date": today + timedelta(days=3),
                "planned_duration": "00:110:00",
            },
            {
                "title": "Update dependencies",
                "description": "Update all project dependencies to latest versions.",
                "is_completed": True,
                "tags": ["Maintenance", "Development"],
                "column_date": today + timedelta(days=3),
                "status": Task.ON_BOARD,
                "planned_duration": "00:50:00",
            },
            {
                "title": "Implement email notifications",
                "description": "Add email notification system for task updates.",
                "is_completed": False,
                "tags": ["Feature", "Backend"],
                "status": Task.ON_BOARD,
                "column_date": today + timedelta(days=4),
                "planned_duration": "00:30:00",
            },
            {
                "title": "Create monthly analytics report",
                "description": "Generate and analyze monthly usage statistics.",
                "is_completed": False,
                "tags": ["Analytics", "Reporting"],
                "column_date": today + timedelta(days=4),
                "status": Task.ON_BOARD,
                "planned_duration": "00:30:00",
            },
            # backlog tasks
            {
                "title": "filter out completed reports",
                "description": "filter monthly usage statistics.",
                "is_completed": False,
                "tags": ["Analytics", "Reporting"],
                "status": Task.BACKLOG,
                "column_date": None,
                "planned_duration": "00:30:00",
            },
            {
                "title": "go to market",
                "description": "we need food to survive.",
                "is_completed": False,
                "status": Task.BACKLOG,
                "tags": ["outdoor", "Reporting"],
                "column_date": None,
                "planned_duration": "00:30:00",
            },
        ]

        # Insert sample tasks into the database
        for data in tasks_data:
            task = Task.objects.create(
                title=data["title"],
                description=data["description"],
                is_completed=data["is_completed"],
                column_date=data["column_date"],
                planned_duration=parse_duration(data["planned_duration"]),
                user=user,
                status=data["status"],
            )
            # Add tags separately since TaggableManager needs to be handled after creation
            for t in data["tags"]:
                tag, _ = Tag.objects.get_or_create(name=t)
                task.tags.add(tag)

            self.stdout.write(self.style.SUCCESS(
                f"Created task: {task.title}"
            ))

        self.stdout.write(self.style.SUCCESS(f"Successfully created {len(tasks_data)} tasks!"))
