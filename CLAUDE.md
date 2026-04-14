# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run a single test file
pytest tests/agents/test_default.py

# Run tests excluding slow ones
pytest -k "not slow"

# Run tests in parallel
pytest -n auto

# Lint (check)
ruff check src/ tests/

# Lint (auto-fix)
ruff check --fix src/ tests/

# Format
ruff format src/ tests/

# Run the CLI
mini
mini -m anthropic/claude-sonnet-4-5-20250929 -t "Write a hello world script"
mini -c mini.yaml -c model.model_kwargs.temperature=0.5
mini gitlab <issue-url>
```

## Architecture

The agent is built around three orthogonal abstractions that are composed at runtime:

- **Agent** ([src/minisweagent/agents/default.py](src/minisweagent/agents/default.py)): `DefaultAgent` runs the main loop — renders Jinja2 templates for the system/instance messages, calls `model.query()`, calls `env.execute()` on each action, and loops until the last message has `role == "exit"`. The `InteractiveAgent` subclass adds human-in-the-loop confirmation prompts.

- **Model** ([src/minisweagent/models/litellm_model.py](src/minisweagent/models/litellm_model.py)): Wraps an LLM API. `LitellmModel` is the default; uses the tool-call interface with a single `bash` tool. "Textbased" variants parse bash fenced code blocks from free-form text instead of tool calls. All models expose `query(messages) -> dict`, `format_message(...)`, and `format_observation_messages(...)`.

- **Environment** ([src/minisweagent/environments/local.py](src/minisweagent/environments/local.py)): Executes bash commands via `subprocess.run` (local), `docker exec` (Docker), `singularity exec`, etc. Each `execute(action) -> dict` call is stateless — a new subshell every time. Task completion is detected when the output's first line is `COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT`, which raises `Submitted` (an `InterruptAgentFlow` subclass).

**Configuration** ([src/minisweagent/config/](src/minisweagent/config/)): YAML files with `agent`, `model`, `environment`, and `run` top-level keys. Multiple configs are recursively merged. Config specs on the CLI can be file paths, bare filenames (resolved from built-in dirs), or `key.subkey=value` pairs. Built-in configs live in `src/minisweagent/config/`.

**Entry point** ([src/minisweagent/run/mini.py](src/minisweagent/run/mini.py)): `typer` app with a default command (`mini`) and subcommands (e.g., `mini gitlab`). Uses `get_model()`, `get_environment()`, `get_agent()` factory functions that resolve short names (e.g., `"litellm"`, `"docker"`, `"interactive"`) to full class paths via internal mappings.

**Message format**: Every message is a plain `dict`. The `extra` key holds metadata (actions list, cost, exit status, etc.) and is stripped before passing to the API. The trajectory (all messages + metadata) is serialized to JSON.

## Code Style

- Python 3.10+, type annotations required, use `list`/`dict` not `List`/`Dict`
- Use `pathlib.Path` (not `os.path`), prefer `Path.read_text()` over `open()`
- Use `pydantic.BaseModel` for config, `dataclass` for plain data, `jinja2` for templates, `typer` for CLIs
- Minimal code — no unnecessary error handling, no speculative abstractions
- Do not catch exceptions unless explicitly needed; exceptions surface problems to users
- Tests: use `pytest`, no mocking unless explicitly asked, inline assertions (`assert func() == b` not `result = func(); assert result == b`)
- `pytest.mark.parametrize` first arg must be a tuple, second must be a list
- Line length: 120 chars
