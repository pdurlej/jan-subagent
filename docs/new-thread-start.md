# New Thread Start

Use this as the first context file for the next Codex thread.

## Working Folder

`/Users/pd/Developer/jan`

## Repo State

- Git repo root is `/Users/pd/Developer/jan`
- Current branch: `master`
- Remote: `https://github.com/pdurlej/jan-subagent.git`
- Current release target is `2.0.0`
- Canonical runtime is `jan.jan_subagent_opencode`
- Legacy `jan/jan_subagent.py` was removed
- `mcp_config.json` is the only maintained sample config
- BMAD is installed in two layers:
  - maintenance scaffold in `scripts/`, `references/`, `agents/`, `state/`
  - project workflow assets in `_bmad/` and `_bmad-output/`
- GitHub metadata should now match the public product description and topics for `jan-subagent`
- The working tree may still be dirty; check `git status --short` before starting new edits

## What Was Done In The Last Thread

1. Runtime and package cleanup
- Removed the legacy `jan.jan_subagent` module.
- Kept `jan/__init__.py` on lazy `mcp` import.
- Updated runtime behavior so `main()` no longer writes to `stdout`.
- Changed `check_configuration()` to emit `✅/❌`.
- Updated `greet_jan(name=...)` to use the passed addressee.
- Extended `BielikClient.reset()` to refresh `api_key`, `api_base`, and `model_id`.

2. Repo and documentation cleanup
- Moved README and release notes to `2.0.0` language.
- Added `docs/VERSION_2_0_0.md` and archived `docs/VERSION_1_1_0.md`.
- Replaced dual MCP samples with a single valid JSON file: `mcp_config.json`.
- Removed `mcp_config_opencode.json`.
- Updated examples and packaging metadata to point only at `jan.jan_subagent_opencode`.

3. BMAD and CI onboarding
- Copied the local `bmad-method-codex` maintenance scaffold into the repo.
- Installed full `_bmad/` project assets with the `bmm` module and no IDE integration.
- Added CI coverage for tests, compileall, runtime smoke, and BMAD maintenance checks.

## Validation Status

- `pytest -q` passes: `89 passed, 1 warning`
- `.venv/bin/python -m compileall -q jan` passes
- `.venv/bin/python -m jan.jan_subagent_opencode` exits cleanly without writing to `stdout`
- `python3 scripts/test_sync_bmad_method.py` passes
- `python3 scripts/sync_bmad_method.py check --json` returns `is_optimal: true`

Re-run them before making claims about the current tree, because this repo may still be dirty between threads.

## Read Order

1. `/Users/pd/Developer/jan/AGENTS.md`
2. `/Users/pd/Developer/jan/README.md`
3. `/Users/pd/Developer/jan/docs/VERSION_2_0_0.md`
4. `/Users/pd/Developer/jan/jan/jan_subagent_opencode.py`
5. `/Users/pd/Developer/jan/jan/api_client.py`
6. `/Users/pd/Developer/jan/jan/config.py`
7. `/Users/pd/Developer/jan/tests/test_jan_subagent.py`

## Recommended Next Work

1. Keep GitHub metadata aligned with README whenever the product description changes.
2. If BMAD upstream changes, run `python3 scripts/sync_bmad_method.py check --json` first and sync only when needed.
3. Treat `mcp_config.json`, README, tests, and `setup.py` as one contract; update them together.

## Important Constraints

- Do not move the working context back to `/Users/pd/Developer`.
- Do not reintroduce `jan/jan_subagent.py` unless there is an explicit migration decision.
- Do not add comments to `mcp_config.json`; it must remain valid JSON.
- Prefer updating `docs/new-thread-start.md` and release docs when changing runtime behavior, BMAD setup, or release hygiene.
