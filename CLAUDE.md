# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bashhub is a Python CLI client that saves, searches, and manages terminal command history in the cloud across multiple systems and sessions. It supports Bash, Zsh, and Fish shells.

## Development Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
```

## Common Commands

```bash
# Run all tests
pytest

# Run a single test file
pytest tests/test_command.py

# Run a specific test
pytest tests/test_command.py::TestCommand::test_json_serialize
```

There is no separate lint or build step. The package is installed via `pip install -e .` for development.

## Entry Points

- `bh` → `bashhub.bh:main` — search command history
- `bashhub` → `bashhub.bashhub:main` — main CLI (setup, save, status, filter, update)

## Architecture

**CLI layer** (`bashhub.py`, `bh.py`): Uses Click. `bashhub` is a command group with subcommands (setup, save, status, filter, update). `bh` is a standalone search command.

**Command save flow**: Shell hook scripts call `bashhub save <command> <path> <pid> <start_time> <exit_status>`. The save handler validates the command (checks save toggle, `#ignore` suffix, `BH_FILTER` regex, auth token), creates a `CommandForm`, and POSTs to the API via `rest_client`.

**Search flow**: `bh` accepts a query with filters (directory, system, session, timestamps). Results come back as `MinCommand` objects. With `-i` flag, results display in a curses-based interactive search UI (`interactive_search.py`).

**Configuration** (`bashhub_globals.py`): Reads from environment variables or `~/.bashhub/config`. Key settings: `url`, `access_token`, `system_name`, `save_commands`, `filter`, `debug`. Auth functions are lazy to support token changes during setup.

**API client** (`rest_client.py`): All requests use Bearer token auth. Base URL defaults to `https://bashhub.com`, configurable via `BH_URL` env var or config.

**Models** (`model/`): All inherit from `Serializable` which provides `to_JSON()`/`from_JSON()` via jsonpickle. Key models: `Command`, `CommandForm`, `MinCommand`, `RegisterUser`, `LoginResponse`, `System`, `StatusView`.

**Shell integration** (`shell/`): Hook scripts for bash (`bashhub.sh`), zsh (`bashhub.zsh`), and fish (`bashhub.fish`) capture command context (PID, start time, exit status) and invoke the Python client.

## Testing Patterns

- Tests use pytest with Click's `CliRunner` for CLI testing
- Mock `rest_client.save_command` and global state (`BH_SAVE_COMMANDS`, `BH_FILTER`, `BH_AUTH`) in tests
- JSON string fixtures for model serialization tests

## Key Conventions

- Python 3 only (3.9, 3.11, 3.13, 3.14). No Python 2 compatibility code.
- Errors are caught and printed as user-friendly messages; functions degrade gracefully rather than raising exceptions
- 401/403 API errors prompt users to run `bashhub setup`
