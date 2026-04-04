#!/usr/bin/env python3
"""
Uruchamia benchmark v2 dla repo-native workflowów Jana.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from jan.delivery_benchmark import (
    DEFAULT_DATASET_PATH,
    DEFAULT_OPENAI_MODEL,
    DEFAULT_OUTPUT_ROOT,
    JanDeliveryRunner,
    OpenAIDeliveryRunner,
    RawBielikDeliveryRunner,
    create_output_dir,
    load_delivery_cases,
    render_delivery_report,
    run_delivery_benchmark,
    write_delivery_results,
)
from jan.policy import load_jan_policy


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Jan delivery benchmark v2.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET_PATH)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--openai-model", default=DEFAULT_OPENAI_MODEL)
    parser.add_argument(
        "--systems",
        nargs="+",
        default=["Jan"],
        help="Subset of systems to run: Jan, raw-bielik, gpt-5.4",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cases = load_delivery_cases(args.dataset)
    policy, _ = load_jan_policy(REPO_ROOT)
    runners = []
    for name in args.systems:
        normalized = name.lower()
        if normalized == "jan":
            runners.append(JanDeliveryRunner(policy=policy))
        elif normalized in {"raw-bielik", "raw_bielik", "bielik"}:
            runners.append(RawBielikDeliveryRunner(policy=policy))
        elif normalized in {"gpt-5.4", "gpt", "openai"}:
            runners.append(OpenAIDeliveryRunner(model=args.openai_model, policy=policy))
        else:
            raise ValueError(f"Unsupported system: {name}")

    output_dir = create_output_dir(args.output_root, label="repo-native-delivery-v2")
    results, summary = run_delivery_benchmark(cases, runners)
    write_delivery_results(output_dir, results, summary)
    print(f"Saved delivery benchmark artifacts to: {output_dir}")
    print(render_delivery_report(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
