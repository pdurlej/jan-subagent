#!/usr/bin/env python3
"""
CI-safe walidacja harnessu benchmarkowego bez live API.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
import sys

import anyio

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from jan.workplace_benchmark import (
    DEFAULT_OUTPUT_ROOT,
    BenchmarkCase,
    JudgeScore,
    ModelExecution,
    aggregate_results,
    build_baseline_prompt,
    build_jan_tool_call,
    compute_deterministic_score,
    compute_final_score,
    load_cases,
    load_prompt_families,
    render_report_markdown,
    run_benchmark,
)
from jan.output_utils import normalize_benchmark_output


class FakeRunner:
    def __init__(self, name: str, outputs: dict[str, str], latency: float = 1.0) -> None:
        self.name = name
        self.outputs = outputs
        self.latency = latency

    async def run_case(self, case: BenchmarkCase) -> ModelExecution:
        return ModelExecution(
            system=self.name,
            output_text=self.outputs[case.id],
            latency_seconds=self.latency,
            metadata={"fake": True},
        )


class FakeJudge:
    def __init__(self, totals: dict[str, float]) -> None:
        self.totals = totals

    async def score(
        self,
        case: BenchmarkCase,
        execution: ModelExecution,
        output_text: str | None = None,
    ) -> JudgeScore:
        key = f"{execution.system}:{case.id}"
        if output_text is not None and output_text != execution.output_text:
            key = f"{key}:normalized"
        total = self.totals[key]
        dimensions = {
            "factual_preservation": total,
            "language_quality": total,
            "clarity": total,
            "workplace_usefulness": total,
            "concision": total,
        }
        return JudgeScore(
            total=total,
            dimensions=dimensions,
            rationale=f"Mock judge score for {execution.system} on {case.id}",
        )


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def check_dataset_schema() -> None:
    cases = load_cases()
    assert_true(len(cases) == 15, "Expected 15 pilot cases")
    assert_true(len({case.id for case in cases}) == 15, "Case ids must be unique")
    assert_true(
        {case.scenario for case in cases}
        == {
            "PR description",
            "ticket/issue",
            "support reply",
            "release note/changelog",
            "status email/notatka",
        },
        "Unexpected scenario set",
    )
    assert_true(
        {case.intent for case in cases}
        == {"surface correction", "style rewrite", "full polish"},
        "Unexpected intent set",
    )


def check_prompt_and_tool_routing() -> None:
    prompt_families = load_prompt_families()
    cases = {case.id: case for case in load_cases()}

    surface_prompt = build_baseline_prompt(cases["pr-surface-01"], prompt_families)
    assert_true(
        "wyłącznie ortografię" in surface_prompt["instructions"],
        "Surface orthography prompt should preserve minimal instructions",
    )

    style_tool, style_args = build_jan_tool_call(cases["status-style-01"], prompt_families)
    assert_true(style_tool == "improve_style", "Style case should route to improve_style")
    assert_true(style_args["style"] == "elegancki", "Style family should pass elegancki")

    full_tool, full_args = build_jan_tool_call(cases["release-full-01"], prompt_families)
    assert_true(
        full_tool == "comprehensive_correction",
        "Full polish case should route to comprehensive_correction",
    )
    assert_true(full_args["mode"] == "standard", "Full polish case should use standard mode")


def check_scoring_math() -> None:
    case = BenchmarkCase.model_validate(
        {
            "id": "score-case",
            "scenario": "PR description",
            "intent": "surface correction",
            "input_text": "blad test",
            "jan_tool": "correct_orthography",
            "baseline_prompt_family": "surface_orthography",
            "must_keep": ["test"],
            "should_fix": ["blad"],
            "must_not_introduce": ["rollback"],
            "notes": "",
        }
    )
    execution = ModelExecution(
        system="Jan",
        output_text="błąd test",
        latency_seconds=2.0,
    )
    deterministic = compute_deterministic_score(
        case,
        execution.output_text,
        latency_seconds=execution.latency_seconds,
        error=execution.error,
    )
    judge = JudgeScore(
        total=0.8,
        dimensions={
            "factual_preservation": 0.8,
            "language_quality": 0.8,
            "clarity": 0.8,
            "workplace_usefulness": 0.8,
            "concision": 0.8,
        },
        rationale="mock",
    )
    final_score = compute_final_score(case, deterministic, judge)
    assert_true(deterministic.total > 0.8, "Deterministic score should be high")
    assert_true(final_score > 0.8, "Final weighted score should be high")


async def check_mock_benchmark_run() -> None:
    prompt_families = load_prompt_families()
    cases = [
        BenchmarkCase.model_validate(
            {
                "id": "mock-surface",
                "scenario": "PR description",
                "intent": "surface correction",
                "input_text": "blad cache",
                "jan_tool": "correct_orthography",
                "baseline_prompt_family": "surface_orthography",
                "must_keep": ["cache"],
                "should_fix": ["blad"],
                "must_not_introduce": ["rollback"],
                "notes": "",
            }
        ),
        BenchmarkCase.model_validate(
            {
                "id": "mock-style",
                "scenario": "support reply",
                "intent": "style rewrite",
                "input_text": "ogarnięte, śmiga",
                "jan_tool": "improve_style",
                "baseline_prompt_family": "style_elegancki",
                "must_keep": ["proszę"],
                "should_fix": ["ogarnięte", "śmiga"],
                "must_not_introduce": ["premium"],
                "notes": "",
            }
        ),
        BenchmarkCase.model_validate(
            {
                "id": "mock-full",
                "scenario": "status email/notatka",
                "intent": "full polish",
                "input_text": "rollout analytics łapie",
                "jan_tool": "comprehensive_correction",
                "baseline_prompt_family": "full_polish_standard",
                "must_keep": ["analytics"],
                "should_fix": ["rollout", "łapie"],
                "must_not_introduce": ["CRM"],
                "notes": "",
            }
        ),
    ]
    style_tool, style_args = build_jan_tool_call(cases[1], prompt_families)
    assert_true(style_tool == "improve_style", "Mock style case should resolve Jan tool")
    assert_true(style_args["style"] == "elegancki", "Mock style should carry style argument")

    jan_outputs = {
        "mock-surface": "błąd cache",
        "mock-style": "Proszę o kontakt, jeśli problem się powtórzy.",
        "mock-full": "Po synchronizacji mamy zielone światło na wdrożenie do grupy beta, ale przed publikacją trzeba dopracować copy i potwierdzić event analytics.",
    }
    bielik_outputs = {
        "mock-surface": "błąd cache",
        "mock-style": "Problem został rozwiązany. Proszę o wiadomość, jeśli sytuacja wróci.",
        "mock-full": "Mamy zgodę na wdrożenie do grupy beta. Przed publikacją trzeba jeszcze dopiąć copy i sprawdzić analytics.",
    }
    gpt_outputs = {
        "mock-surface": "błąd cache",
        "mock-style": "Temat został rozwiązany. Jeśli problem wróci, proszę o wiadomość, a sprawdzimy go z zespołem.",
        "mock-full": "Po wczorajszym spotkaniu mamy zgodę na rollout do grupy beta. Przed publikacją musimy dopracować treść maila i upewnić się, że analytics rejestruje event invite_sent.",
    }

    judge_scores = {}
    for system in ["Jan", "raw Bielik", "GPT-5.4"]:
        for case in cases:
            score = 0.72
            if system == "raw Bielik":
                score = 0.78
            if system == "GPT-5.4":
                score = 0.85
            judge_scores[f"{system}:{case.id}"] = score
            judge_scores[f"{system}:{case.id}:normalized"] = min(score + 0.05, 1.0)

    with tempfile.TemporaryDirectory() as tmp_dir:
        output_dir = Path(tmp_dir) / "_bmad-output" / "benchmarks" / "mock-run"
        metadata = {
            "timestamp": "mock-run",
            "dataset": "fixtures",
            "output_dir": str(output_dir),
            "systems": ["Jan", "raw Bielik", "GPT-5.4"],
            "openai_model": "gpt-5.4",
            "judge_model": "gpt-5.4-mini",
            "bielik_model": "mock-bielik",
        }
        results, aggregate, report = await run_benchmark(
            cases=cases,
            runners=[
                FakeRunner("Jan", jan_outputs),
                FakeRunner("raw Bielik", bielik_outputs),
                FakeRunner("GPT-5.4", gpt_outputs),
            ],
            judge=FakeJudge(judge_scores),
            output_dir=output_dir,
            metadata=metadata,
        )
        assert_true(len(results) == 9, "Expected 3 cases x 3 systems")
        assert_true((output_dir / "results.json").exists(), "results.json must exist")
        assert_true((output_dir / "summary.json").exists(), "summary.json must exist")
        assert_true((output_dir / "report.md").exists(), "report.md must exist")
        assert_true(
            str(DEFAULT_OUTPUT_ROOT).endswith("_bmad-output/benchmarks"),
            "Default output root must live under _bmad-output/benchmarks",
        )
        assert_true(
            "Primary Literal Score" in report and "Normalized Diagnostic Score" in report,
            "Report should contain both literal and normalized sections",
        )
        rendered_report = render_report_markdown(metadata, cases, results, aggregate)
        assert_true(
            "PR description" in rendered_report and "GPT-5.4" in rendered_report,
            "Rendered report should contain scenario and system rows",
        )
        overall = aggregate_results(results, "literal")["overall"]
        assert_true("Jan" in overall, "Aggregate should contain Jan")
        normalized_overall = aggregate_results(results, "normalized")["overall"]
        assert_true("Jan" in normalized_overall, "Normalized aggregate should contain Jan")


def check_normalizer() -> None:
    legacy_output = (
        "Niech wam się wiedzie w mowie polskiej.\n\n"
        "### Poprawiony tekst:\n"
        "\"Po wdrożeniu wersji 2.3 panel admina czasem się nie ładuje.\"\n\n"
        "### Lista zmian z uzasadnieniami:\n"
        "1. **Dodanie kropki**\n"
        "- **Uzasadnienie:** Koniec zdania.\n"
    )
    normalized = normalize_benchmark_output("Jan", legacy_output)
    assert_true(
        normalized == "Po wdrożeniu wersji 2.3 panel admina czasem się nie ładuje.",
        "Normalizer should extract primary corrected text from legacy Jan output",
    )
    non_jan = normalize_benchmark_output("GPT-5.4", "**Krótki tekst**")
    assert_true(non_jan == "Krótki tekst", "Non-Jan normalization should be minimal")


def main() -> int:
    check_dataset_schema()
    check_prompt_and_tool_routing()
    check_scoring_math()
    check_normalizer()
    anyio.run(check_mock_benchmark_run)
    print("Benchmark harness checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
