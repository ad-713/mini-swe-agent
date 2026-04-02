# Gemini CLI Context: mini-swe-agent

This project is `mini-swe-agent`, a minimal and highly performant AI software engineering agent designed to solve GitHub issues. It prioritizes simplicity, using a linear message history and independent shell command execution via `subprocess.run`.

## Project Overview

*   **Purpose:** A lightweight alternative to complex agent scaffolds, achieving high scores on SWE-bench with minimal code.
*   **Core Philosophy:** "Bash-only" toolset, linear history, and stateless action execution.
*   **Tech Stack:** Python (>=3.10), LiteLLM (for multi-model support), Pydantic (for configuration), Jinja2 (for templating), and Typer/Rich (for the CLI).
*   **Architecture:** Follows a strict separation of concerns via three main Protocols defined in `src/minisweagent/__init__.py`:
    *   **Agent:** Manages the high-level loop (Query -> Act -> Observe).
    *   **Model:** Handles LLM communication, message formatting, and action parsing.
    *   **Environment:** Executes shell commands (locally, in Docker, etc.) and handles completion signals.

## Building and Running

### Development Setup
```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Key Commands
*   **Run CLI:** `mini` or `mini-swe-agent` (Entry point: `minisweagent.run.mini:app`)
*   **Run Tests:** `pytest`
*   **Linting/Formatting:** `ruff check .` and `ruff format .`
*   **Type Checking:** The project uses Protocols for static type checking; ensure changes adhere to `Agent`, `Model`, and `Environment` definitions.

## Project Structure

*   `src/minisweagent/`: Core source code.
    *   `agents/`: Implementation of agent logic (e.g., `DefaultAgent`).
    *   `environments/`: Execution environments (Local, Docker, Singularity, etc.).
    *   `models/`: Model wrappers (primarily `LitellmModel`).
    *   `config/`: YAML templates for system prompts and default settings.
    *   `run/`: CLI entry points and main execution scripts.
*   `tests/`: Comprehensive test suite mirroring the `src` structure.
*   `docs/`: MkDocs-based documentation.

## Development Conventions

*   **Configuration:** All components use Pydantic `BaseModel` for configuration. Default settings are stored in YAML files within `src/minisweagent/config/`.
*   **Completion Signal:** The agent signals task completion by echoing the specific string `COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT`.
*   **Stateless Actions:** Actions are independent. Do not rely on persistent shell state (like `export` or `cd`) across different `step()` calls unless explicitly prefixed in the same command.
*   **Error Handling:** The `DefaultAgent` catches uncaught exceptions and appends them to the trajectory as an `exit` role message.

## Usage for Gemini

When assisting with this project:
1.  **Respect the Minimalist Design:** Avoid adding complex "fancy" dependencies or heavy abstractions.
2.  **Verify via LocalEnvironment:** Use `src/minisweagent/environments/local.py` logic to understand how commands will be executed by the agent.
3.  **Template Precision:** System prompts and observation formatting are governed by Jinja2 templates in `src/minisweagent/config/default.yaml`.
