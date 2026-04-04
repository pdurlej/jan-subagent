#!/usr/bin/env python3
"""
Uruchamia pilot benchmarkowy workplace writing dla Jana.
"""

from __future__ import annotations

import argparse
from contextlib import AsyncExitStack
from pathlib import Path
import sys

import anyio

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from jan.config import config
from jan.workplace_benchmark import (
    DEFAULT_DATASET_PATH,
    DEFAULT_JUDGE_MODEL,
    DEFAULT_OPENAI_MODEL,
    DEFAULT_OUTPUT_ROOT,
    JanMcpRunner,
    OpenAIJudge,
    OpenAIWorkplaceRunner,
    RawBielikRunner,
    create_output_dir,
    load_cases,
    load_judge_rubric,
    load_prompt_families,
    run_benchmark,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the workplace writing benchmark pilot for Jan."
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET_PATH,
        help="Path to the benchmark JSONL dataset.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Root directory for benchmark run outputs.",
    )
    parser.add_argument(
        "--run-label",
        default="workplace-writing-pilot",
        help="Optional label appended to the output directory name.",
    )
    parser.add_argument(
        "--jan-python",
        default=str(REPO_ROOT / ".venv" / "bin" / "python"),
        help="Python executable used to start Jan via MCP stdio.",
    )
    parser.add_argument(
        "--jan-cwd",
        type=Path,
        default=REPO_ROOT,
        help="Working directory used to start Jan.",
    )
    parser.add_argument(
        "--openai-model",
        default=DEFAULT_OPENAI_MODEL,
        help="OpenAI model used as the workplace writing baseline.",
    )
    parser.add_argument(
        "--judge-model",
        default=DEFAULT_JUDGE_MODEL,
        help="OpenAI model used as the benchmark judge.",
    )
    return parser.parse_args()


async def async_main(args: argparse.Namespace) -> int:
    cases = load_cases(args.dataset)
    prompt_families = load_prompt_families()
    rubric = load_judge_rubric()
    output_dir = create_output_dir(args.output_root, args.run_label)

    metadata = {
        "timestamp": output_dir.name.split("-")[0],
        "dataset": str(args.dataset),
        "output_dir": str(output_dir),
        "systems": ["Jan", "raw Bielik", "GPT-5.4"],
        "openai_model": args.openai_model,
        "judge_model": args.judge_model,
        "bielik_model": config.model_id,
        "jan_python": args.jan_python,
        "jan_cwd": str(args.jan_cwd),
    }

    async with AsyncExitStack() as stack:
        jan_runner = await stack.enter_async_context(
            JanMcpRunner(
                jan_python=args.jan_python,
                jan_cwd=args.jan_cwd,
                prompt_families=prompt_families,
            )
        )
        raw_bielik_runner = RawBielikRunner(prompt_families=prompt_families)
        gpt_runner = OpenAIWorkplaceRunner(
            model=args.openai_model,
            prompt_families=prompt_families,
        )
        judge = OpenAIJudge(model=args.judge_model, rubric=rubric)

        _, aggregate, _ = await run_benchmark(
            cases=cases,
            runners=[jan_runner, raw_bielik_runner, gpt_runner],
            judge=judge,
            output_dir=output_dir,
            metadata=metadata,
        )

    literal_overall = aggregate["literal"]["overall"]
    normalized_overall = aggregate["normalized"]["overall"]
    print(f"Saved benchmark artifacts to: {output_dir}")
    print("Primary Literal Score:")
    for system, row in literal_overall.items():
        print(
            f"- {system}: final={row['final_score'] * 100:.1f}%, "
            f"judge={row['judge_score'] * 100:.1f}%, "
            f"deterministic={row['deterministic_score'] * 100:.1f}%, "
            f"latency={row['latency_seconds']:.2f}s"
        )
    print("Normalized Diagnostic Score:")
    for system, row in normalized_overall.items():
        print(
            f"- {system}: final={row['final_score'] * 100:.1f}%, "
            f"judge={row['judge_score'] * 100:.1f}%, "
            f"deterministic={row['deterministic_score'] * 100:.1f}%, "
            f"latency={row['latency_seconds']:.2f}s"
        )
    return 0


def main() -> int:
    args = parse_args()
    return anyio.run(async_main, args)


if __name__ == "__main__":
    raise SystemExit(main())
