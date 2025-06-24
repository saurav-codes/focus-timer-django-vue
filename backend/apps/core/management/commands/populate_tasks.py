from django.core.management.base import BaseCommand
from apps.core.models import Task, Project, RecurrenceSeries
from taggit.models import Tag
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
import pytz
from django.utils.dateparse import parse_duration
import random
from django.conf import settings

project_names = [
    "Social Media Marketing",
    "UI/UX Design",
    "Backend Development",
    "Frontend Development",
    "Content Creation",
    "SEO Optimization",
    "LifeStyle",
    "Health & Fitness",
]

User = get_user_model()


class Command(BaseCommand):
    help = "Populate the database with fake tasks"

    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stdout.write(
                self.style.ERROR(
                    "This command is not meant to be run in production as it deletes all existing tasks and projects."
                )
            )
            return False
        # Remove all existing tasks
        Task.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Deleted all existing tasks."))
        # either create a new user or use the existing one
        user = User.objects.filter(email="raju@gmail.com").first()
        if not user:
            self.stdout.write(
                self.style.WARNING("No existing user found, creating one")
            )
            user = User.objects.create_user(  # type:ignore
                first_name="raju test user",
                email="raju@gmail.com",
                password="raju123",
                is_superuser=True,
                is_staff=True,
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Found existing user= {user}, using it to assign tasks"
                )
            )
        Project.objects.all().delete()
        RecurrenceSeries.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Deleted all existing projects."))
        # Create sample projects
        for project_name in project_names:
            project = Project.objects.create(
                title=project_name,
                description=f"Description for {project_name}",
                user=user,
            )
            self.stdout.write(self.style.SUCCESS(f"Created project: {project.title}"))
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
                "duration": "00:20:00",
            },
            {
                "title": "Research competitor analysis",
                "description": "Analyze top 5 competitors and their feature sets.",
                "is_completed": False,
                "status": Task.BRAINDUMP,
                "tags": ["Research", "Strategy"],
                "column_date": None,
                "duration": "00:30:00",
            },
            {
                "title": "Draft content calendar",
                "description": "Plan content for social media and blog posts.",
                "is_completed": False,
                "status": Task.BRAINDUMP,
                "tags": ["Marketing", "Planning"],
                "column_date": None,
                "duration": "01:00:00",
            },
            # Regular Tasks
            {
                "title": "Code review: Authentication module",
                "description": "Review PR #123 for the new authentication system.",
                "is_completed": False,
                "status": Task.ON_BOARD,
                "tags": ["Development", "Security"],
                "column_date": today,
                "duration": "00:30:00",
            },
            {
                "title": "Update API documentation",
                "description": "Add new endpoints and update existing documentation.",
                "is_completed": True,
                "status": Task.ON_BOARD,
                "tags": ["Documentation", "API"],
                "column_date": today,
                "duration": "00:40:00",
            },
            {
                "title": "Weekly team meeting",
                "description": "Discuss sprint progress and upcoming milestones.",
                "is_completed": False,
                "tags": ["Meeting", "Team"],
                "status": Task.ON_BOARD,
                "column_date": today + timedelta(days=1),
                "duration": "00:80:00",
            },
            {
                "title": "Fix mobile responsiveness",
                "description": "Address UI issues on smaller screens.",
                "is_completed": False,
                "tags": ["Bug", "UI"],
                "status": Task.ON_BOARD,
                "column_date": today + timedelta(days=1),
                "duration": "00:30:00",
            },
            {
                "title": "Implement dark mode",
                "description": "Add dark mode theme support across all components.",
                "is_completed": False,
                "tags": ["Feature", "UI"],
                "status": Task.ON_BOARD,
                "column_date": today - timedelta(days=1),
                "duration": "00:30:00",
            },
            {
                "title": "Performance optimization",
                "description": "Optimize database queries and frontend loading.",
                "is_completed": False,
                "tags": ["Performance", "Development"],
                "status": Task.ON_BOARD,
                "column_date": today - timedelta(days=1),
                "duration": "00:30:00",
            },
            {
                "title": "User feedback analysis",
                "description": "Review and categorize recent user feedback.",
                "is_completed": True,
                "tags": ["Analysis", "User Experience"],
                "status": Task.ON_BOARD,
                "column_date": today + timedelta(days=2),
                "duration": "00:30:00",
            },
            {
                "title": "Security audit",
                "description": "Conduct monthly security review and updates.",
                "is_completed": False,
                "tags": ["Security", "Maintenance"],
                "status": Task.ON_BOARD,
                "column_date": today + timedelta(days=2),
                "duration": "00:30:00",
            },
            {
                "title": "Create onboarding tutorial",
                "description": "Design and implement user onboarding flow.",
                "is_completed": False,
                "tags": ["UX", "Documentation"],
                "status": Task.ON_BOARD,
                "column_date": today + timedelta(days=3),
                "duration": "00:110:00",
            },
            {
                "title": "Update dependencies",
                "description": "Update all project dependencies to latest versions.",
                "is_completed": True,
                "tags": ["Maintenance", "Development"],
                "column_date": today + timedelta(days=3),
                "status": Task.ON_BOARD,
                "duration": "00:50:00",
            },
            {
                "title": "Implement email notifications",
                "description": "Add email notification system for task updates.",
                "is_completed": False,
                "tags": ["Feature", "Backend"],
                "status": Task.ON_BOARD,
                "column_date": today + timedelta(days=4),
                "duration": "00:30:00",
            },
            {
                "title": "Create monthly analytics report",
                "description": "Generate and analyze monthly usage statistics.",
                "is_completed": False,
                "tags": ["Analytics", "Reporting"],
                "column_date": today + timedelta(days=4),
                "status": Task.ON_BOARD,
                "duration": "00:30:00",
            },
            # backlog tasks
            {
                "title": "filter out completed reports",
                "description": "filter monthly usage statistics.",
                "is_completed": False,
                "tags": ["Analytics", "Reporting"],
                "status": Task.BACKLOG,
                "column_date": None,
                "duration": "00:30:00",
            },
            {
                "title": "go to market",
                "description": "we need food to survive.",
                "is_completed": False,
                "status": Task.BACKLOG,
                "tags": ["outdoor", "Reporting"],
                "column_date": None,
                "duration": "00:30:00",
            },
            # Archived Tasks
            {
                "title": "Archive old tasks",
                "description": "Move completed tasks to the archive.",
                "is_completed": True,
                "status": Task.ARCHIVED,
                "tags": ["Maintenance", "Cleanup"],
                "column_date": None,
                "duration": "00:30:00",
            },
            {
                "title": "Update project wiki",
                "description": "Archive old tasks and update wiki with new info.",
                "is_completed": False,
                "status": Task.ARCHIVED,
                "tags": ["Documentation", "Wiki"],
                "column_date": None,
                "duration": "00:30:00",
            },
            {
                "title": "Remove deprecated APIs",
                "description": "Delete old API endpoints that are no longer in use.",
                "is_completed": True,
                "status": Task.ARCHIVED,
                "tags": ["Maintenance", "API"],
                "column_date": None,
                "duration": "00:30:00",
            },
            {
                "title": "Clean up old branches",
                "description": "Delete branches that have been merged or are no longer needed.",
                "is_completed": False,
                "status": Task.ARCHIVED,
                "tags": ["Maintenance", "Git"],
                "column_date": None,
                "duration": "00:30:00",
            },
            {
                "title": "Update README",
                "description": "Add new features and update existing documentation.",
                "is_completed": True,
                "status": Task.ARCHIVED,
                "tags": ["Documentation", "Git"],
                "column_date": None,
                "duration": "00:30:00",
            },
            {
                "title": "Create release notes",
                "description": "Document changes for the next release.",
                "is_completed": True,
                "status": Task.ARCHIVED,
                "tags": ["Documentation", "Release"],
                "column_date": None,
                "duration": "00:30:00",
            },
            {
                "title": "Migrate to new server",
                "description": "Move all services to the new server infrastructure.",
                "is_completed": False,
                "status": Task.ARCHIVED,
                "tags": ["Infrastructure", "Maintenance"],
                "column_date": None,
                "duration": "00:30:00",
            },
            {
                "title": "Backup database",
                "description": "Create a backup of the production database.",
                "is_completed": True,
                "status": Task.ARCHIVED,
                "tags": ["Backup", "Maintenance"],
                "column_date": None,
                "duration": "00:30:00",
            },
            {
                "title": "Test disaster recovery plan",
                "description": "Ensure the disaster recovery plan works as expected.",
                "is_completed": False,
                "status": Task.ARCHIVED,
                "tags": ["Testing", "Maintenance"],
                "column_date": None,
                "duration": "00:30:00",
            },
            {
                "title": "Conduct user interviews",
                "description": "Gather feedback from users about the new feature.",
                "is_completed": False,
                "status": Task.ARCHIVED,
                "tags": ["Research", "User Experience"],
                "column_date": None,
                "duration": "00:30:00",
            },
        ]

        # Insert sample tasks into the database
        project_ids = Project.objects.values_list("id", flat=True)
        for data in tasks_data:
            task = Task.objects.create(
                title=data["title"],
                description=data["description"],
                is_completed=data["is_completed"],
                column_date=data["column_date"],
                duration=parse_duration(data["duration"]),
                user=user,
                project_id=random.choice(project_ids),
                status=data["status"],
            )
            # Add tags separately since TaggableManager needs to be handled after creation
            for t in data["tags"]:
                tag, _ = Tag.objects.get_or_create(name=t)
                task.tags.add(tag)

            self.stdout.write(self.style.SUCCESS(f"Created task: {task.title}"))

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {len(tasks_data)} tasks!")
        )
