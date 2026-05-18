from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from minisweagent.run.gitlab_listener import app

runner = CliRunner()

@patch("minisweagent.run.gitlab_listener.fetch_project_issues")
@patch("minisweagent.run.gitlab_listener.fetch_issue_comments")
@patch("minisweagent.run.gitlab_listener.has_reaction")
@patch("minisweagent.run.gitlab_listener.add_comment_reaction")
@patch("minisweagent.run.gitlab_listener.subprocess.run")
def test_listen_triggered(mock_run, mock_add_reaction, mock_has_reaction, mock_fetch_comments, mock_fetch_issues):
    # Mock issues
    mock_fetch_issues.return_value = [
        {"iid": 1, "web_url": "https://gitlab.com/test/project/-/issues/1"}
    ]
    # Mock comments
    mock_fetch_comments.return_value = [
        {"id": 101, "body": "Hey @mini-swe-agent fix this"}
    ]
    # Mock reaction check (not yet reacted)
    mock_has_reaction.return_value = False
    
    result = runner.invoke(app, ["--project-id", "123"])
    
    assert result.exit_code == 0
    assert "Found mention in comment 101. Triggering agent..." in result.stdout
    
    # Check if reactions were added
    mock_add_reaction.assert_any_call("https://gitlab.com", "123", "1", 101, "eyes")
    mock_add_reaction.assert_any_call("https://gitlab.com", "123", "1", 101, "white_check_mark")
    
    # Check if subprocess was called
    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    assert args[0] == ["mini", "gitlab", "https://gitlab.com/test/project/-/issues/1", "-y"]

@patch("minisweagent.run.gitlab_listener.fetch_project_issues")
@patch("minisweagent.run.gitlab_listener.fetch_issue_comments")
@patch("minisweagent.run.gitlab_listener.has_reaction")
def test_listen_already_processed(mock_has_reaction, mock_fetch_comments, mock_fetch_issues):
    # Mock issues
    mock_fetch_issues.return_value = [
        {"iid": 1, "web_url": "https://gitlab.com/test/project/-/issues/1"}
    ]
    # Mock comments
    mock_fetch_comments.return_value = [
        {"id": 101, "body": "Hey @mini-swe-agent fix this"}
    ]
    # Mock reaction check (already reacted)
    mock_has_reaction.return_value = True
    
    result = runner.invoke(app, ["--project-id", "123"])
    
    assert result.exit_code == 0
    assert "Found mention in comment 101. Triggering agent..." not in result.stdout
