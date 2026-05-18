import os
from unittest.mock import Mock, patch

from minisweagent.run.gitlab_utils import (
    fetch_issue_details,
    parse_issue_url,
    fetch_project_issues,
    fetch_issue_comments,
    add_comment_reaction,
    has_reaction
)


def test_parse_issue_url():
    base_url, project_path, iid = parse_issue_url("https://gitlab.com/group/project/-/issues/123")
    assert base_url == "https://gitlab.com"
    assert project_path == "group%2Fproject"
    assert iid == "123"


@patch("minisweagent.run.gitlab_utils.requests.get")
def test_fetch_issue_details(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {"title": "Bug", "description": "Fix it"}
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    os.environ["GITLAB_TOKEN"] = "fake_token"
    res = fetch_issue_details("https://gitlab.com", "group%2Fproject", "123")

    assert res["title"] == "Bug"
    assert res["description"] == "Fix it"


@patch("minisweagent.run.gitlab_utils.requests.get")
def test_fetch_project_issues(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = [{"id": 1, "title": "Issue 1"}]
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    os.environ["GITLAB_TOKEN"] = "fake_token"
    res = fetch_project_issues("https://gitlab.com", "123")

    assert len(res) == 1
    assert res[0]["title"] == "Issue 1"
    mock_get.assert_called_once()


@patch("minisweagent.run.gitlab_utils.requests.get")
def test_fetch_issue_comments(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = [{"id": 1, "body": "Comment 1"}]
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    os.environ["GITLAB_TOKEN"] = "fake_token"
    res = fetch_issue_comments("https://gitlab.com", "123", "456")

    assert len(res) == 1
    assert res[0]["body"] == "Comment 1"


@patch("minisweagent.run.gitlab_utils.requests.post")
def test_add_comment_reaction(mock_post):
    mock_response = Mock()
    mock_response.status_code = 201
    mock_response.raise_for_status = Mock()
    mock_post.return_value = mock_response

    os.environ["GITLAB_TOKEN"] = "fake_token"
    add_comment_reaction("https://gitlab.com", "123", "456", 789, "thumbsup")

    mock_post.assert_called_once()


@patch("minisweagent.run.gitlab_utils.requests.get")
def test_has_reaction(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = [{"name": "thumbsup"}]
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    os.environ["GITLAB_TOKEN"] = "fake_token"
    res = has_reaction("https://gitlab.com", "123", "456", 789, "thumbsup")

    assert res is True

    res = has_reaction("https://gitlab.com", "123", "456", 789, "heart")
    assert res is False
