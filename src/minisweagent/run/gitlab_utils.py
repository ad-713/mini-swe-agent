import os
import re
from urllib.parse import quote_plus

import requests


def parse_issue_url(url: str) -> tuple[str, str, str]:
    """Parse a GitLab issue/work_item URL to extract base URL, URL-encoded project path, and IID."""
    # Pattern to match both /issues/ and /work_items/ and extract parts
    # Group 1: Protocol and Host (Base URL)
    # Group 2: Project Path
    # Group 3: Issue/Work Item IID
    match = re.search(r"^(https?://[^/]+)/(.*?)/-/(?:issues|work_items)/(\d+)", url)
    if not match:
        raise ValueError(f"Invalid GitLab issue URL: {url}")

    base_url = match.group(1).rstrip("/")
    project_path = match.group(2).strip("/")
    return base_url, quote_plus(project_path), match.group(3)


def fetch_issue_details(base_url: str, project_id: str, issue_iid: str) -> dict:
    """Fetch issue details from GitLab API."""
    token = os.getenv("GITLAB_TOKEN")
    if not token:
        raise ValueError("GITLAB_TOKEN environment variable is not set")

    url = f"{base_url}/api/v4/projects/{project_id}/issues/{issue_iid}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def create_merge_request(
    base_url: str, project_id: str, source_branch: str, issue_iid: str, title: str, description: str
) -> str:
    """Create a Merge Request and return its web URL."""
    token = os.getenv("GITLAB_TOKEN")
    if not token:
        raise ValueError("GITLAB_TOKEN environment variable is not set")

    url = f"{base_url}/api/v4/projects/{project_id}/merge_requests"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "source_branch": source_branch,
        "target_branch": "main",
        "title": f"Draft: Resolve issue #{issue_iid}: {title}",
        "description": f"Resolves #{issue_iid}\n\n{description}",
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["web_url"]


def fetch_project_issues(base_url: str, project_id: str, state: str = "opened") -> list[dict]:
    """Fetch issues for a project."""
    token = os.getenv("GITLAB_TOKEN")
    if not token:
        raise ValueError("GITLAB_TOKEN environment variable is not set")

    url = f"{base_url}/api/v4/projects/{project_id}/issues"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"state": state, "order_by": "updated_at", "sort": "desc"}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def fetch_issue_comments(base_url: str, project_id: str, issue_iid: str) -> list[dict]:
    """Fetch comments (notes) for an issue."""
    token = os.getenv("GITLAB_TOKEN")
    if not token:
        raise ValueError("GITLAB_TOKEN environment variable is not set")

    url = f"{base_url}/api/v4/projects/{project_id}/issues/{issue_iid}/notes"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"sort": "asc", "order_by": "created_at"}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def add_comment_reaction(base_url: str, project_id: str, issue_iid: str, note_id: int, emoji_name: str) -> None:
    """Add an emoji reaction to a comment."""
    token = os.getenv("GITLAB_TOKEN")
    if not token:
        raise ValueError("GITLAB_TOKEN environment variable is not set")

    url = f"{base_url}/api/v4/projects/{project_id}/issues/{issue_iid}/notes/{note_id}/award_emoji"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"name": emoji_name}
    response = requests.post(url, headers=headers, json=payload)
    # Ignore if reaction already exists
    if response.status_code != 409:
        response.raise_for_status()


def has_reaction(base_url: str, project_id: str, issue_iid: str, note_id: int, emoji_name: str) -> bool:
    """Check if a comment has a specific emoji reaction."""
    token = os.getenv("GITLAB_TOKEN")
    if not token:
        raise ValueError("GITLAB_TOKEN environment variable is not set")

    url = f"{base_url}/api/v4/projects/{project_id}/issues/{issue_iid}/notes/{note_id}/award_emoji"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    reactions = response.json()
    return any(r["name"] == emoji_name for r in reactions)
