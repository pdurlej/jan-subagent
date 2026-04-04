#!/usr/bin/env python3
"""
CI-safe walidacja benchmarku delivery v2 bez live API.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from jan.delivery_benchmark import (
    DeliveryBenchmarkCase,
    DeliveryExecution,
    SUPPORTED_LANES,
    aggregate_delivery_results,
    build_bundle_for_lane,
    load_delivery_cases,
    render_delivery_report,
    run_delivery_benchmark,
    score_delivery_execution,
    write_delivery_results,
)


class FakeRunner:
    def __init__(self, name: str, outputs: dict[tuple[str, str], str], latency: float = 1.0) -> None:
        self.name = name
        self.outputs = outputs
        self.latency = latency

    def run_case(self, case: DeliveryBenchmarkCase, lane: str) -> DeliveryExecution:
        return DeliveryExecution(
            system=self.name,
            lane=lane,
            output_text=self.outputs[(case.id, lane)],
            latency_seconds=self.latency,
        )


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def check_dataset_schema() -> None:
    cases = load_delivery_cases()
    assert_true(len(cases) == 4, "Expected 4 delivery benchmark cases")
    assert_true(
        {case.workflow for case in cases}
        == {
            "write_pr_description",
            "compose_release_notes",
            "rewrite_issue",
            "write_rollout_note",
        },
        "Unexpected workflow set",
    )


def check_lane_building() -> None:
    case = load_delivery_cases()[0]
    text_only = build_bundle_for_lane(case, "text_only")
    assert_true(text_only.raw_notes == case.raw_notes, "Text-only lane should only carry raw notes")
    assert_true(text_only.repo is None, "Text-only lane should not inject repo context")

    structured = build_bundle_for_lane(case, "structured_context")
    assert_true(structured.repo is not None, "Structured lane should include repo context")
    assert_true(structured.pull_requests, "Structured lane should include PR context")


def check_scoring() -> None:
    case = DeliveryBenchmarkCase.model_validate(
        {
            "id": "score-delivery",
            "workflow": "write_pr_description",
            "audience": "reviewer",
            "raw_notes": "JAN-101 dodać Sentry.",
            "required_sections": ["Cel zmiany", "Zakres"],
            "must_keep": ["JAN-101", "Sentry"],
            "must_not_introduce": ["GA4"],
        }
    )
    execution = DeliveryExecution(
        system="Jan",
        lane="policy_pack",
        output_text=(
            "Cel zmiany\nOpisuje JAN-101.\n\n"
            "Zakres\nDodajemy alert w Sentry."
        ),
        latency_seconds=1.2,
    )
    score = score_delivery_execution(case, execution)
    assert_true(score.template_compliance == 1.0, "Template compliance should be perfect")
    assert_true(score.fact_preservation == 1.0, "Must-keep facts should be preserved")
    assert_true(score.no_new_facts == 1.0, "No forbidden facts should be introduced")


def check_mock_run_and_report() -> None:
    cases = load_delivery_cases()
    outputs = {}
    for case in cases:
        outputs[(case.id, "text_only")] = "\n\n".join(
            [section + "\nWersja robocza." for section in case.required_sections]
        )
        outputs[(case.id, "structured_context")] = "\n\n".join(
            [section + "\nWersja ze structured context." for section in case.required_sections]
        )
        outputs[(case.id, "policy_pack")] = "\n\n".join(
            [section + "\nWersja z policy pack." for section in case.required_sections]
        )

    results, summary = run_delivery_benchmark(
        cases=cases,
        runners=[
            FakeRunner("Jan", outputs, latency=1.1),
            FakeRunner("raw Bielik", outputs, latency=1.4),
        ],
    )
    assert_true(results, "Benchmark run should return results")
    assert_true("Jan" in summary, "Summary should include Jan")
    report = render_delivery_report(summary)
    assert_true("Lane: text_only" in report, "Report should render text_only lane")
    assert_true("Lane: policy_pack" in report, "Report should render policy_pack lane")

    with tempfile.TemporaryDirectory() as tmp_dir:
        output_dir = Path(tmp_dir) / "delivery-benchmark"
        write_delivery_results(output_dir, results, summary)
        assert_true((output_dir / "results.json").exists(), "Results file should be written")
        assert_true((output_dir / "summary.json").exists(), "Summary file should be written")
        assert_true((output_dir / "report.md").exists(), "Report file should be written")


def main() -> int:
    check_dataset_schema()
    check_lane_building()
    check_scoring()
    check_mock_run_and_report()
    print("Delivery benchmark checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
