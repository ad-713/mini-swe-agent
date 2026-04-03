import os
from unittest.mock import patch, Mock
import pytest
from minisweagent.run.gitlab_utils import parse_issue_url, fetch_issue_details

def test_parse_issue_url():
    project_path, iid = parse_issue_url("https://gitlab.com/group/project/-/issues/123")
    assert project_path == "group%2Fproject"
    assert iid == "123"

@patch("minisweagent.run.gitlab_utils.requests.get")
def test_fetch_issue_details(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {"title": "Bug", "description": "Fix it"}
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    os.environ["GITLAB_TOKEN"] = "fake_token"
    res = fetch_issue_details("group%2Fproject", "123")
    
    assert res["title"] == "Bug"
    assert res["description"] == "Fix it"
