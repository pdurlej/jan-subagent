# New Thread Start

Use this as the first context file for the next Codex thread.

## Working Folder

`/Users/pd/Developer/jan`

## Repo State

- Git repo root is `/Users/pd/Developer/jan`
- Current branch: `master`
- Remote: `https://github.com/pdurlej/jan-subagent.git`
- Current release target is `2.1.0`
- Canonical runtime is `jan.jan_subagent_opencode`
- Legacy `jan/jan_subagent.py` was removed
- `mcp_config.json` is the only maintained sample config
- Benchmark harness lives in `jan/workplace_benchmark.py` with datasets, prompts and rubrics in `benchmarks/`
- Workplace correction tools are paste-ready by default; `include_explanation=True` is opt-in
- Benchmark reporting has both `Primary Literal Score` and `Normalized Diagnostic Score`
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
- Moved README and release notes to `2.x` language.
- Added `docs/VERSION_2_0_0.md`, `docs/VERSION_2_1_0.md` and archived `docs/VERSION_1_1_0.md`.
- Replaced dual MCP samples with a single valid JSON file: `mcp_config.json`.
- Removed `mcp_config_opencode.json`.
- Updated examples and packaging metadata to point only at `jan.jan_subagent_opencode`.

3. BMAD and CI onboarding
- Copied the local `bmad-method-codex` maintenance scaffold into the repo.
- Installed full `_bmad/` project assets with the `bmm` module and no IDE integration.
- Added CI coverage for tests, compileall, runtime smoke, and BMAD maintenance checks.

4. Workplace writing benchmark pilot
- Added a persistent benchmark harness in `jan/workplace_benchmark.py`.
- Added `benchmarks/workplace_writing_v1.jsonl`, `benchmarks/prompt_families.json`, and `benchmarks/judge_rubric.md`.
- Added `scripts/run_workplace_benchmark.py` for live pilot runs.
- Added `scripts/test_benchmark_harness.py` for CI-safe validation without live APIs.
- Added methodology and public-safe benchmark docs under `docs/benchmark-methodology.md` and `docs/benchmarks/`.
- Completed a full live run at `_bmad-output/benchmarks/20260404T012404Z-workplace-writing-pilot`.
- Pilot outcome: `GPT-5.4` leads (`96.8%`), `raw Bielik` is second (`92.4%`), and `Jan` trails (`49.9%`) mainly because default persona/reporting hurts concision and paste-readiness.

5. Paste-ready refactor for workplace tools
- Correction tools now default to paste-ready output with no greeting, reflection, farewell, headings, lists of changes or commentary.
- `include_greeting=True` remains supported, but only adds a short one-line Jan greeting before the final text.
- `include_explanation=True` returns the final text plus a short bullet summary of the most important changes.
- `verify_grammar()` now keeps a stable JSON-only contract.
- `check_text_quality()` now returns a short plain-text scorecard without persona wrapper.
- Benchmark reporting now keeps the literal product score as the primary KPI and adds a normalized diagnostic score that strips Jan wrappers technically for analysis.
- A live rerun completed at `_bmad-output/benchmarks/20260404T020037Z-workplace-writing-pilot`.
- Rerun outcome: `GPT-5.4` stays first (`96.5%`), `Jan` jumps to second (`94.0%`) ahead of `raw Bielik` (`93.1%`), and Jan latency drops from `26.28s` to `2.58s`.

## Validation Status

- `pytest -q` passed as of the last local verification: `98 passed, 1 warning`
- `.venv/bin/python -m compileall -q jan` passes
- `.venv/bin/python -m jan.jan_subagent_opencode` exits cleanly without writing to `stdout`
- `.venv/bin/python scripts/test_benchmark_harness.py` passes
- `python3 scripts/test_sync_bmad_method.py` passes
- `python3 scripts/sync_bmad_method.py check --json` returns `is_optimal: true`
- Full benchmark live run succeeds when a valid `OPENAI_API_KEY` is available and writes summary/report artifacts under `_bmad-output/benchmarks/20260404T020037Z-workplace-writing-pilot`

Re-run them before making claims about the current tree, because this repo may still be dirty between threads.

## Read Order

1. `/Users/pd/Developer/jan/AGENTS.md`
2. `/Users/pd/Developer/jan/README.md`
3. `/Users/pd/Developer/jan/docs/VERSION_2_1_0.md`
4. `/Users/pd/Developer/jan/jan/jan_subagent_opencode.py`
5. `/Users/pd/Developer/jan/jan/api_client.py`
6. `/Users/pd/Developer/jan/jan/config.py`
7. `/Users/pd/Developer/jan/tests/test_jan_subagent.py`

## Recommended Next Work

1. Keep GitHub metadata aligned with README whenever the product description changes.
2. If BMAD upstream changes, run `python3 scripts/sync_bmad_method.py check --json` first and sync only when needed.
3. Treat `mcp_config.json`, README, tests, and `setup.py` as one contract; update them together.
4. Treat `benchmarks/`, `jan/workplace_benchmark.py`, and `docs/benchmark-methodology.md` as one contract for benchmark changes.

## Important Constraints

- Do not move the working context back to `/Users/pd/Developer`.
- Do not reintroduce `jan/jan_subagent.py` unless there is an explicit migration decision.
- Do not add comments to `mcp_config.json`; it must remain valid JSON.
- Prefer updating `docs/new-thread-start.md` and release docs when changing runtime behavior, BMAD setup, or release hygiene.
