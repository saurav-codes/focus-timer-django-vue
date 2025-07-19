import requests
import logging
from apps.core.models import Task
from apps.core.serializers import TaskSerializer
from django.utils import timezone
from django.http import HttpRequest

from .models import GitHubCredentials, GitHubSettings

logger = logging.getLogger(__name__)


def get_repositories(user):
    """Get list of repositories accessible to the user."""
    try:
        credentials = GitHubCredentials.objects.filter(user=user).first()
        if not credentials:
            return {"error": "GitHub not connected"}

        headers = credentials.get_auth_headers()

        # Get user's repositories (including organizations)
        repos = []
        page = 1
        per_page = 100

        while True:
            response = requests.get(
                "https://api.github.com/user/repos",
                headers=headers,
                params={"page": page, "per_page": per_page, "sort": "updated"},
                timeout=30,
            )

            if response.status_code != 200:
                logger.error(
                    f"GitHub API error: {response.status_code} - {response.text}"
                )
                return {"error": "Failed to fetch repositories"}

            batch = response.json()
            if not batch:
                break

            repos.extend(batch)
            page += 1

            # Limit to prevent infinite loop
            if len(repos) >= 1000:
                break

        # Format repositories for frontend
        formatted_repos = []
        for repo in repos:
            formatted_repos.append(
                {
                    "id": repo["id"],
                    "full_name": repo["full_name"],
                    "name": repo["name"],
                    "description": repo.get("description", ""),
                    "private": repo["private"],
                    "html_url": repo["html_url"],
                    "updated_at": repo["updated_at"],
                }
            )

        return {"repositories": formatted_repos}

    except requests.RequestException as e:
        logger.error(f"GitHub API request failed: {str(e)}")
        return {"error": "Failed to connect to GitHub"}
    except Exception as e:
        logger.error(f"Error fetching repositories: {str(e)}")
        return {"error": str(e)}


def get_issues(
    user, repositories=None, page=1, per_page=30, assignee="assigned", state="open"
):
    """Get issues from selected repositories."""
    try:
        credentials = GitHubCredentials.objects.filter(user=user).first()
        if not credentials:
            return {"error": "GitHub not connected"}

        settings_obj = GitHubSettings.get_or_create_for_user(user)
        if not settings_obj.sync_enabled:
            return {"error": "GitHub sync is disabled"}

        headers = credentials.get_auth_headers()

        # Use repositories from settings if not provided
        if not repositories:
            repositories = settings_obj.sync_repositories

        all_issues = []

        if not repositories:
            # If no repositories selected, search across all user's issues
            params = {
                "filter": "assigned" if assignee == "assigned" else "all",
                "state": state,
                "page": page,
                "per_page": per_page,
                "sort": "updated",
                "direction": "desc",
            }

            response = requests.get(
                "https://api.github.com/issues",
                headers=headers,
                params=params,
                timeout=30,
            )

            if response.status_code == 200:
                issues = response.json()
                # Check if there are more pages
                has_more = len(issues) == per_page and "next" in response.links
                all_issues.extend(issues)
            else:
                logger.error(
                    f"GitHub API error: {response.status_code} - {response.text}"
                )
                return {"error": "Failed to fetch issues"}
        else:
            # Fetch from specific repositories
            for repo_id in repositories:
                if not repo_id:
                    continue

                # Convert repository ID to owner/repo format
                try:
                    repo_response = requests.get(
                        f"https://api.github.com/repositories/{repo_id}",
                        headers=headers,
                        timeout=30,
                    )
                    if repo_response.status_code != 200:
                        logger.warning(f"Could not find repository {repo_id}")
                        continue

                    repo_info = repo_response.json()
                    repo_full_name = repo_info["full_name"]

                except Exception as e:
                    logger.error(
                        f"Error fetching repository info for {repo_id}: {str(e)}"
                    )
                    continue

                params = {
                    "state": state,
                    "assignee": credentials.github_username
                    if assignee == "assigned"
                    else assignee,
                    "page": page,
                    "per_page": per_page,
                    "sort": "updated",
                    "direction": "desc",
                }

                response = requests.get(
                    f"https://api.github.com/repos/{repo_full_name}/issues",
                    headers=headers,
                    params=params,
                    timeout=30,
                )

                if response.status_code == 200:
                    repo_issues = response.json()
                    # Add repository info to each issue
                    for issue in repo_issues:
                        issue["repository"] = repo_full_name
                    all_issues.extend(repo_issues)
                else:
                    logger.error(
                        f"Error fetching issues for {repo_full_name}: {response.text}"
                    )

        # Format issues for frontend
        formatted_issues = []
        for issue in all_issues:
            # Skip pull requests (they appear as issues in GitHub API)
            if "pull_request" in issue:
                continue

            formatted_issue = {
                "id": issue["id"],
                "number": issue["number"],
                "title": issue["title"],
                "body": issue.get("body", ""),
                "state": issue["state"],
                "html_url": issue["html_url"],
                "created_at": issue["created_at"],
                "updated_at": issue["updated_at"],
                "closed_at": issue.get("closed_at"),
                "user": {
                    "login": issue["user"]["login"],
                    "avatar_url": issue["user"]["avatar_url"],
                    "html_url": issue["user"]["html_url"],
                },
                "assignees": [
                    {
                        "login": assignee["login"],
                        "avatar_url": assignee["avatar_url"],
                        "html_url": assignee["html_url"],
                    }
                    for assignee in issue.get("assignees", [])
                ],
                "labels": [
                    {
                        "name": label["name"],
                        "color": label["color"],
                        "description": label.get("description", ""),
                    }
                    for label in issue.get("labels", [])
                ],
                "repository": issue.get(
                    "repository", issue["repository_url"].split("/")[-2:]
                )
                if "repository" not in issue
                else issue["repository"],
            }
            formatted_issues.append(formatted_issue)

        has_more = len(all_issues) == per_page
        total_count = len(formatted_issues)

        return {
            "issues": formatted_issues,
            "has_more": has_more,
            "total_count": total_count,
            "page": page,
        }

    except requests.RequestException as e:
        logger.error(f"GitHub API request failed: {str(e)}")
        return {"error": "Failed to connect to GitHub"}
    except Exception as e:
        logger.error(f"Error fetching issues: {str(e)}")
        return {"error": str(e)}


def get_issue_details(user, issue_id):
    """Get detailed information about a specific issue including timeline."""
    try:
        credentials = GitHubCredentials.objects.filter(user=user).first()
        if not credentials:
            return {"error": "GitHub not connected"}

        # headers = credentials.get_auth_headers()

        # First get the issue details
        # response = requests.get(
        #     f"https://api.github.com/repositories/{issue_id}",  # This won't work, need proper repo/issue
        #     headers=headers,
        #     timeout=30,
        # )

        # For now, return a placeholder
        # In a real implementation, you'd need to store repo info with issues or parse from URL
        return {"timeline": [], "pull_requests": []}

    except Exception as e:
        logger.error(f"Error fetching issue details: {str(e)}")
        return {"error": str(e)}


def convert_to_task(user, issue_id, task_data):
    """Convert a GitHub issue to a task in the system."""
    try:
        # Create task in the system
        request = HttpRequest()
        request.user = user  # type: ignore
        task_serializer = TaskSerializer(
            data={
                "user": user,
                "title": task_data.get("title", "No title - task from github"),
                "description": task_data.get("description"),
                "status": Task.ON_BOARD,
                "start_at": timezone.now(),
            },
            context={"request": request},
        )
        if task_serializer.is_valid():
            task = task_serializer.save()
        else:
            return {"error": task_serializer.errors}

        return {"task": TaskSerializer(task).data}

    except Exception as e:
        logger.error(f"Error converting issue to task: {str(e)}")
        return {"error": str(e)}
