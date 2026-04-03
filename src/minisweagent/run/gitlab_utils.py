import os
import re
from urllib.parse import quote_plus
import requests

def parse_issue_url(url: str) -> tuple[str, str]:
    """Parse a GitLab issue URL to extract URL-encoded project path and issue IID."""
    match = re.search(r"gitlab\.com/(.*?)/-/issues/(\d+)", url)
    if not match:
        raise ValueError(f"Invalid GitLab issue URL: {url}")
    project_path = match.group(1)
    return quote_plus(project_path), match.group(2)

def fetch_issue_details(project_id: str, issue_iid: str) -> dict:
    """Fetch issue details from GitLab API."""
    token = os.getenv("GITLAB_TOKEN")
    if not token:
        raise ValueError("GITLAB_TOKEN environment variable is not set")
    
    url = f"https://gitlab.com/api/v4/projects/{project_id}/issues/{issue_iid}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def create_merge_request(project_id: str, source_branch: str, issue_iid: str, title: str, description: str) -> str:
    """Create a Merge Request and return its web URL."""
    token = os.getenv("GITLAB_TOKEN")
    if not token:
        raise ValueError("GITLAB_TOKEN environment variable is not set")

    url = f"https://gitlab.com/api/v4/projects/{project_id}/merge_requests"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "source_branch": source_branch,
        "target_branch": "main",
        "title": f"Draft: Resolve issue #{issue_iid}: {title}",
        "description": f"Resolves #{issue_iid}\n\n{description}"
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["web_url"]
