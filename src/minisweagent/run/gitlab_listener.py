import os
import subprocess
import typer
from minisweagent.run.gitlab_utils import (
    fetch_project_issues,
    fetch_issue_comments,
    add_comment_reaction,
    has_reaction
)

app = typer.Typer()

@app.command()
def listen(
    project_id: str = typer.Option(os.getenv("CI_PROJECT_ID"), help="GitLab Project ID"),
    base_url: str = typer.Option(os.getenv("CI_SERVER_URL", "https://gitlab.com"), help="GitLab Base URL"),
    bot_mention: str = typer.Option("@mini-swe-agent", help="Bot mention string"),
):
    if not project_id:
        print("Error: project_id must be provided or CI_PROJECT_ID must be set")
        raise typer.Exit(1)

    print(f"Checking for mentions of {bot_mention} in project {project_id}...")
    issues = fetch_project_issues(base_url, project_id)
    
    for issue in issues:
        issue_iid = str(issue["iid"])
        issue_url = issue["web_url"]
        print(f"Checking issue #{issue_iid}...")
        
        comments = fetch_issue_comments(base_url, project_id, issue_iid)
        for comment in comments:
            if bot_mention in comment["body"]:
                note_id = comment["id"]
                
                # Check if already processed
                if has_reaction(base_url, project_id, issue_iid, note_id, "eyes"):
                    continue
                
                print(f"Found mention in comment {note_id}. Triggering agent...")
                
                # Mark as processing
                add_comment_reaction(base_url, project_id, issue_iid, note_id, "eyes")
                
                # Run the agent
                try:
                    # Assuming 'mini' is installed or we run via python -m
                    cmd = ["mini", "gitlab", issue_url, "-y"]
                    subprocess.run(cmd, check=True)
                    add_comment_reaction(base_url, project_id, issue_iid, note_id, "white_check_mark")
                except subprocess.CalledProcessError:
                    print(f"Agent failed for issue {issue_url}")
                    add_comment_reaction(base_url, project_id, issue_iid, note_id, "x")

if __name__ == "__main__":
    app()
