from django.core.management.base import BaseCommand
from apps.core.models import Task

class Command(BaseCommand):
    help = 'Populate the database with fake tasks'

    def handle(self, *args, **options):
        # Remove all existing tasks
        Task.objects.all().delete()
        self.stdout.write(self.style.WARNING("Deleted all existing tasks."))

        tasks_data = [
            # Brain Dump Tasks
            {
                "title": "Brainstorm new feature ideas",
                "description": "Generate innovative feature ideas for the next quarter.",
                "is_in_brain_dump": True,
                "is_completed": False,
                "tags": ["Planning", "Innovation"],
            },
            {
                "title": "Research competitor analysis",
                "description": "Analyze top 5 competitors and their feature sets.",
                "is_in_brain_dump": True,
                "is_completed": False,
                "tags": ["Research", "Strategy"],
            },
            {
                "title": "Draft content calendar",
                "description": "Plan content for social media and blog posts.",
                "is_in_brain_dump": True,
                "is_completed": False,
                "tags": ["Marketing", "Planning"],
            },

            # Regular Tasks
            {
                "title": "Code review: Authentication module",
                "description": "Review PR #123 for the new authentication system.",
                "is_in_brain_dump": False,
                "is_completed": False,
                "tags": ["Development", "Security"],
            },
            {
                "title": "Update API documentation",
                "description": "Add new endpoints and update existing documentation.",
                "is_in_brain_dump": False,
                "is_completed": True,
                "tags": ["Documentation", "API"],
            },
            {
                "title": "Weekly team meeting",
                "description": "Discuss sprint progress and upcoming milestones.",
                "is_in_brain_dump": False,
                "is_completed": False,
                "tags": ["Meeting", "Team"],
            },
            {
                "title": "Fix mobile responsiveness",
                "description": "Address UI issues on smaller screens.",
                "is_in_brain_dump": False,
                "is_completed": False,
                "tags": ["Bug", "UI"],
            },
            {
                "title": "Implement dark mode",
                "description": "Add dark mode theme support across all components.",
                "is_in_brain_dump": False,
                "is_completed": False,
                "tags": ["Feature", "UI"],
            },
            {
                "title": "Performance optimization",
                "description": "Optimize database queries and frontend loading.",
                "is_in_brain_dump": False,
                "is_completed": False,
                "tags": ["Performance", "Development"],
            },
            {
                "title": "User feedback analysis",
                "description": "Review and categorize recent user feedback.",
                "is_in_brain_dump": False,
                "is_completed": True,
                "tags": ["Analysis", "User Experience"],
            },
            {
                "title": "Security audit",
                "description": "Conduct monthly security review and updates.",
                "is_in_brain_dump": False,
                "is_completed": False,
                "tags": ["Security", "Maintenance"],
            },
            {
                "title": "Create onboarding tutorial",
                "description": "Design and implement user onboarding flow.",
                "is_in_brain_dump": False,
                "is_completed": False,
                "tags": ["UX", "Documentation"],
            },
            {
                "title": "Update dependencies",
                "description": "Update all project dependencies to latest versions.",
                "is_in_brain_dump": False,
                "is_completed": True,
                "tags": ["Maintenance", "Development"],
            },
            {
                "title": "Implement email notifications",
                "description": "Add email notification system for task updates.",
                "is_in_brain_dump": False,
                "is_completed": False,
                "tags": ["Feature", "Backend"],
            },
            {
                "title": "Create monthly analytics report",
                "description": "Generate and analyze monthly usage statistics.",
                "is_in_brain_dump": False,
                "is_completed": False,
                "tags": ["Analytics", "Reporting"],
            },
        ]

        # Insert sample tasks into the database
        for data in tasks_data:
            task = Task.objects.create(
                title=data["title"],
                description=data["description"],
                is_in_brain_dump=data["is_in_brain_dump"],
                is_completed=data["is_completed"],
            )
            # Add tags separately since TaggableManager needs to be handled after creation
            task.tags.add(*data["tags"])

            self.stdout.write(self.style.SUCCESS(
                f"Created task: {task.title} (Completed: {task.is_completed}, Brain Dump: {task.is_in_brain_dump})"
            ))

        self.stdout.write(self.style.SUCCESS(f"Successfully created {len(tasks_data)} tasks!"))
