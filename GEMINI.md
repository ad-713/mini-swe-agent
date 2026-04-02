# Gemini CLI Context: mini-swe-agent (GitLab Edition)

This project is `mini-swe-agent`, a minimal and highly performant AI software engineering agent. While the core is generic, this specific workspace is configured as a **Minimal GitLab SWE Agent CLI**, purpose-built to autonomously resolve GitLab issues using Docker sandboxing.

## Project Overview

*   **Purpose:** Autonomously resolve GitLab issues by cloning repositories into ephemeral Docker sandboxes, generating fixes, and submitting Merge Requests.
*   **Core Philosophy:** "Bash-only" toolset, linear history, and stateless action execution via independent shell commands.
*   **Key Technologies:** Python (>=3.10), LiteLLM, Docker (for sandboxing), GitLab API, and Pydantic.
*   **Architecture:**
    *   **Agent (`DefaultAgent`):** Manages the Query -> Act -> Observe loop.
    *   **Model (`LitellmModel`):** Interfaces with LLMs (e.g., Gemini, Claude) via LiteLLM.
    *   **Environment (`LocalEnvironment` / `DockerEnvironment`):** Executes shell commands and handles the `COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT` signal.

## Building and Running

### Development Setup
```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Configure environment (see .env.example)
cp .env.example .env
# Edit .env with your LLM_API_KEY and GITLAB_TOKEN
```

### Key Commands
*   **Run CLI:** `mini` or `mini-swe-agent` (Entry point: `minisweagent.run.mini:app`)
*   **Run Utility CLI:** `mini-extra` or `mini-e`
*   **Run Tests:** `pytest`
*   **Linting/Formatting:** `ruff check .` and `ruff format .`

## Project Structure

*   `src/minisweagent/`:
    *   `agents/`: Agent implementations (e.g., `DefaultAgent`).
    *   `environments/`: Execution environments (Local, Docker, etc.).
    *   `models/`: Model wrappers and tool-call parsing logic.
    *   `config/`: YAML templates for system prompts and default settings.
    *   `run/`: CLI entry points.
*   `tests/`: Extensive test suite for agents, environments, and models.
*   `PRD.md`: Specific requirements for the GitLab integration.

## Development Conventions

*   **Completion Signal:** The agent signals task completion by echoing `COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT`.
*   **Independent Actions:** Every action is executed in a new subshell. Do not assume persistent state (like `cd` or exports) between steps.
*   **Configuration:** Components use Pydantic `BaseModel`. Default prompts are in `src/minisweagent/config/default.yaml`.
*   **GitLab Workflow:** The agent is expected to fetch issue context, create a branch (`swe-agent/issue-[ID]`), commit changes, and open a Merge Request.

## Usage for Gemini

1.  **Respect the Minimalist Design:** Keep the core agent logic simple and "bash-only."
2.  **Sandbox Safety:** Always assume actions should be safe for a Docker-based environment as defined in the PRD.
3.  **Template Consistency:** Ensure any new prompts or observation formats align with the Jinja2 templates in `src/minisweagent/config/`.
