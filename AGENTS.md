# AGENTS.md

## Scope

This file is local to `/Users/pd/Developer/jan` and should be treated as the primary Codex context for new threads started in this repository.

## Working Folder

- Always work from `/Users/pd/Developer/jan`.
- Treat this directory as the repo root.

## Repo Summary

- Project: `jan-subagent`
- Purpose: MCP server for Polish language correction with a Jan Kochanowski persona and NVIDIA Bielik integration.
- Canonical runtime entrypoint: `jan.jan_subagent_opencode`
- Legacy module `jan/jan_subagent.py` was removed in `2.0.0`.

## Read Order For New Threads

1. `/Users/pd/Developer/jan/docs/new-thread-start.md`
2. `/Users/pd/Developer/jan/README.md`
3. `/Users/pd/Developer/jan/docs/VERSION_2_0_0.md`
4. `/Users/pd/Developer/jan/jan/jan_subagent_opencode.py`
5. `/Users/pd/Developer/jan/jan/api_client.py`
6. `/Users/pd/Developer/jan/jan/config.py`
7. `/Users/pd/Developer/jan/tests/test_jan_subagent.py`

## Current Engineering Decisions

- The `opencode` server is the default implementation for MCP usage and packaging.
- `setup.py` version is aligned to `2.0.0`.
- `jan/__init__.py` uses lazy import for `mcp`.
  - Do not reintroduce eager import of `jan_subagent_opencode` there.
- Config is loaded from environment or `~/.jan/config.json`.
- Default model ID is `speakleash/bielik-11b-v2.6-instruct`.
- README examples and API docs should stay aligned with `jan_subagent_opencode` and `jan.api_client.BielikClient`.
- `mcp_config.json` is the only maintained sample config and must stay valid JSON.
- BMAD is present in two layers:
  - maintenance scaffold: `scripts/`, `references/`, `agents/`, `state/`
  - project workflows: `_bmad/` and `_bmad-output/`

## Validation Commands

- `cd /Users/pd/Developer/jan && pytest -q`
- `cd /Users/pd/Developer/jan && .venv/bin/python -m compileall -q jan`
- `cd /Users/pd/Developer/jan && .venv/bin/python -m jan.jan_subagent_opencode`
- `cd /Users/pd/Developer/jan && python3 scripts/test_sync_bmad_method.py`
- `cd /Users/pd/Developer/jan && python3 scripts/sync_bmad_method.py check --json`

## Practical Constraints

- There are already uncommitted local changes in this repo. Do not discard them unless explicitly requested.
- Prefer updating docs when public behavior, signatures, or setup flow changes.
- If a task adds release readiness or automation, capture it in `docs/new-thread-start.md` or adjacent docs so the next thread inherits the state cleanly.
