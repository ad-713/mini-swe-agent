# Minimal GitLab SWE Agent CLI Design Document

## 1. Executive Summary
The Minimal GitLab SWE Agent is a subcommand of the existing `mini-swe-agent` CLI, designed to autonomously resolve assigned GitLab issues. It securely clones the repository into an ephemeral Docker sandbox, runs the agent to generate and test code patches, and seamlessly pushes the resulting fixes back to GitLab as a Draft Merge Request.

## 2. Core Components

### 2.1 CLI Integration
- Implemented as a Typer subcommand: `mini gitlab <issue_url_or_id>` within `src/minisweagent/run/mini.py`.
- Relies on the `GITLAB_TOKEN` environment variable for authentication.
- Fails fast with descriptive errors if the token is missing or if the API requests fail.

### 2.2 Issue Ingestion via GitLab API
- Uses the `requests` library to interface with the GitLab REST API.
- Parses the provided input to extract the Project ID and Issue IID.
- Fetches the issue title and description to serve as the prompt for the AI agent.
- Fetches the repository details to construct the clone URL.

### 2.3 Secure Ephemeral Sandbox Setup
- Initializes a `DockerEnvironment` (using the default `python:3.11` or configured image).
- Mounts no host volumes, ensuring complete isolation.
- Executes bash commands within the sandbox to securely `git clone` the repository using the `GITLAB_TOKEN` embedded in the origin URL.

### 2.4 Autonomous Execution Loop
- The standard `DefaultAgent` instance is executed against the Docker environment.
- The agent prompt is constructed primarily from the GitLab issue description.
- All actions (file edits, syntax checks, testing) run securely inside the Docker container.

### 2.5 Git Committing & MR Generation
- Upon a successful agent run, a series of bash commands are executed within the Docker sandbox:
  1. `git checkout -b swe-agent/issue-<IID>`
  2. `git add -A`
  3. `git commit -m "Fix issue <IID>"`
  4. `git push origin swe-agent/issue-<IID>`
- Following the push, a POST request is made to the GitLab REST API to create a new Draft Merge Request.
- The MR description includes an AI-generated summary of the problem and the applied fix (or a simple template referencing the issue).

## 3. Data Flow

1. User runs `mini gitlab https://gitlab.com/group/project/-/issues/123`
2. `mini gitlab` parses URL -> Project: `group/project`, Issue IID: `123`.
3. GET `/api/v4/projects/<id>/issues/<iid>` -> Issue Details.
4. `DockerEnvironment` is instantiated.
5. Sandbox clone: `git clone https://oauth2:<token>@gitlab.com/group/project.git .` in container.
6. `DefaultAgent.run(issue_details)` is invoked inside the container.
7. Sandbox commit & push to new branch.
8. POST `/api/v4/projects/<id>/merge_requests` -> Returns MR URL.
9. CLI prints the new MR URL and exits.
10. Container is torn down (automatically by `--rm` in DockerEnvironment).

## 4. Dependencies
- Relies purely on the existing `mini-swe-agent` dependencies (`requests`, `docker`, `typer`).
- Requires `GITLAB_TOKEN` configured in the environment.

## 5. Security Considerations
- The `GITLAB_TOKEN` is strictly kept out of logs and only passed to the git remote URL within the ephemeral container.
- The container is completely stateless and purged immediately after execution (via `--rm`).
