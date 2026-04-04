# AGENTS.md

## Scope

This file is local to `/Users/pd/Developer/jan` and should be treated as the primary Codex context for new threads started in this repository.

## Working Folder

- Always work from `/Users/pd/Developer/jan`.
- Treat this directory as the repo root.

## Repo Summary

- Project: `jan-subagent`
- Purpose: repo-native MCP agent for Polish-language change communication in software delivery, powered by NVIDIA Bielik.
- Canonical runtime entrypoint: `jan.jan_subagent_opencode`
- Legacy module `jan/jan_subagent.py` was removed in `2.0.0`.
- Current behavioral release target: `3.0.0`.

## Read Order For New Threads

1. `/Users/pd/Developer/jan/docs/new-thread-start.md`
2. `/Users/pd/Developer/jan/README.md`
3. `/Users/pd/Developer/jan/docs/VERSION_3_0_0.md`
4. `/Users/pd/Developer/jan/_bmad-output/project-context.md`
5. `/Users/pd/Developer/jan/jan/jan_subagent_opencode.py`
6. `/Users/pd/Developer/jan/jan/workflow_engine.py`
7. `/Users/pd/Developer/jan/jan/policy.py`
8. `/Users/pd/Developer/jan/jan/source_adapters.py`
9. `/Users/pd/Developer/jan/tests/test_repo_native_workflows.py`

## Current Engineering Decisions

- The `opencode` server is the default implementation for MCP usage and packaging.
- `setup.py` version is aligned to `3.0.0`.
- `jan/__init__.py` uses lazy import for `mcp`.
  - Do not reintroduce eager import of `jan_subagent_opencode` there.
- Config is loaded from environment or `~/.jan/config.json`.
- Default model ID is `speakleash/bielik-11b-v2.6-instruct`.
- README examples and API docs should stay aligned with named repo-native workflows and `jan.workflow_engine`.
- `mcp_config.json` is the only maintained sample config and must stay valid JSON.
- Primary workflows are:
  - `write_pr_description`
  - `compose_release_notes`
  - `rewrite_issue`
  - `write_rollout_note`
- Legacy tools remain callable for compatibility, but are deprecated and not the main product surface.
- `jan.yml` is the repo-level policy pack and should be treated as memory-as-code.
- `response_mode="review"` must stay stable and JSON-only.
- BMAD is present in two layers:
  - maintenance scaffold: `scripts/`, `references/`, `agents/`, `state/`
  - project workflows: `_bmad/` and `_bmad-output/`
- `project-context.md` in `_bmad-output/` is the source-of-truth for the `v3.0.0` pivot.
- Benchmarking now has two tiers:
  - workplace writing pilot as regression guardrail
  - delivery benchmark v2 as north-star workflow benchmark

## Validation Commands

- `cd /Users/pd/Developer/jan && python3 -m pytest -q`
- `cd /Users/pd/Developer/jan && .venv/bin/python -m compileall -q jan`
- `cd /Users/pd/Developer/jan && .venv/bin/python -m jan.jan_subagent_opencode`
- `cd /Users/pd/Developer/jan && .venv/bin/python scripts/test_benchmark_harness.py`
- `cd /Users/pd/Developer/jan && .venv/bin/python scripts/test_delivery_benchmark.py`
- `cd /Users/pd/Developer/jan && python3 scripts/test_sync_bmad_method.py`
- `cd /Users/pd/Developer/jan && python3 scripts/sync_bmad_method.py check --json`

## Practical Constraints

- There are already uncommitted local changes in this repo. Do not discard them unless explicitly requested.
- Prefer updating docs when public behavior, signatures, or setup flow changes.
- If a task adds release readiness or automation, capture it in `docs/new-thread-start.md` or adjacent docs so the next thread inherits the state cleanly.
- Do not let the Jana persona leak back into default production workflow output.
- Do not add fake source context when GitHub or Jira credentials are missing.
