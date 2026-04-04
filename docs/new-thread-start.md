# New Thread Start

Use this as the first context file for the next Codex thread.

## Working Folder

`/Users/pd/Developer/jan`

## Repo State

- Git repo root is `/Users/pd/Developer/jan`
- Current branch: `master`
- Remote: `https://github.com/pdurlej/jan-subagent.git`
- Current release target is `3.0.0`
- Canonical runtime is `jan.jan_subagent_opencode`
- `mcp_config.json` is the only maintained sample config
- `jan.yml` is now the repo-level policy pack
- `project-context.md` in `_bmad-output/` is the technical memory for the v3 pivot
- BMAD is installed in two layers:
  - maintenance scaffold in `scripts/`, `references/`, `agents/`, `state/`
  - project workflow assets in `_bmad/` and `_bmad-output/`
- The working tree may still be dirty; check `git status --short` before editing

## What Changed Recently

1. Product pivot
- Jan moved from general Polish correction tooling to a repo-native MCP agent for Polish-language change communication in software delivery.
- The main surface is now named workflows for tech teams instead of generic correction tools.

2. New runtime layers
- Added `jan.policy`, `jan.source_context`, `jan.source_adapters`, `jan.workflow_engine`, and `jan.delivery_benchmark`.
- Added new primary tools:
  - `write_pr_description`
  - `compose_release_notes`
  - `rewrite_issue`
  - `write_rollout_note`
- Legacy correction tools remain callable but are deprecated and no longer the main onboarding path.

3. Trust layer and repo memory
- Added `jan.yml` with glossary, do-not-translate, templates, audiences and validation policy.
- Added trust checks for fact preservation, `no_new_facts`, template compliance, glossary adherence and audience policy.
- Added `response_mode="review"` with JSON `final_text`, `source_trace` and `validator_report`.

4. BMAD / BMADX artifacts
- Added `_bmad-output/project-context.md`.
- Added PRD and architecture notes for the v3 pivot in `_bmad-output/planning-artifacts/`.
- Rendered an `X4/FUBAR` bundle in `_bmad-output/planning-artifacts/jan-v3-fubar`.

5. Benchmarking
- Kept workplace writing pilot as a regression suite.
- Added delivery benchmark v2 on lanes:
  - `text_only`
  - `structured_context`
  - `policy_pack`
- Added `scripts/test_delivery_benchmark.py` and `scripts/run_delivery_benchmark.py`.

## Validation Status

- `python3 -m pytest -q tests/test_jan_subagent.py tests/test_repo_native_workflows.py` passes
- `.venv/bin/python scripts/test_delivery_benchmark.py` passes
- `.venv/bin/python -m compileall -q jan` passes
- Remaining full-suite verification should be rerun before making final claims on the current tree

## Read Order

1. `/Users/pd/Developer/jan/AGENTS.md`
2. `/Users/pd/Developer/jan/README.md`
3. `/Users/pd/Developer/jan/docs/VERSION_3_0_0.md`
4. `/Users/pd/Developer/jan/_bmad-output/project-context.md`
5. `/Users/pd/Developer/jan/jan/jan_subagent_opencode.py`
6. `/Users/pd/Developer/jan/jan/workflow_engine.py`
7. `/Users/pd/Developer/jan/jan/policy.py`
8. `/Users/pd/Developer/jan/jan/source_adapters.py`
9. `/Users/pd/Developer/jan/tests/test_repo_native_workflows.py`

## Recommended Next Work

1. Keep repo description, README and `jan.yml` aligned whenever the product wedge changes.
2. Treat `workflow_engine`, `jan.yml` and benchmark v2 as one contract.
3. Use workplace pilot only as regression guardrail, not as roadmap compass.
4. Do not let persona leak back into default production workflow output.

## Important Constraints

- Do not move the working context back to `/Users/pd/Developer`.
- Do not add comments to `mcp_config.json`; it must remain valid JSON.
- Do not create fake GitHub or Jira context when credentials are missing.
- Prefer updating `docs/new-thread-start.md`, release notes and migration docs whenever the workflow surface changes.
