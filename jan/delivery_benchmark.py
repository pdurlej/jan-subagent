"""
Benchmark v2 dla repo-native workflowów Jana.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any, Protocol

from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError, field_validator

from .api_client import BielikClient, bielik
from .policy import JanPolicy, default_policy_payload, load_jan_policy
from .source_context import WorkflowContextBundle
from .workflow_engine import SUPPORTED_AUDIENCES, execute_repo_native_workflow, serialize_context_bundle

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_PATH = REPO_ROOT / "benchmarks" / "delivery_workflows_v2.jsonl"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "_bmad-output" / "delivery-benchmarks"
DEFAULT_OPENAI_MODEL = "gpt-5.4"

SUPPORTED_LANES = ("text_only", "structured_context", "policy_pack")
SUPPORTED_WORKFLOWS = (
    "write_pr_description",
    "compose_release_notes",
    "rewrite_issue",
    "write_rollout_note",
)


class DeliveryBenchmarkCase(BaseModel):
    id: str
    workflow: str
    audience: str
    raw_notes: str
    structured_context: dict[str, Any] = Field(default_factory=dict)
    required_sections: list[str] = Field(default_factory=list)
    must_keep: list[str] = Field(default_factory=list)
    must_not_introduce: list[str] = Field(default_factory=list)
    notes: str = ""

    @field_validator("workflow")
    @classmethod
    def validate_workflow(cls, value: str) -> str:
        if value not in SUPPORTED_WORKFLOWS:
            raise ValueError(f"Unsupported workflow: {value}")
        return value

    @field_validator("audience")
    @classmethod
    def validate_audience(cls, value: str) -> str:
        if value not in SUPPORTED_AUDIENCES:
            raise ValueError(f"Unsupported audience: {value}")
        return value


@dataclass
class DeliveryExecution:
    system: str
    lane: str
    output_text: str
    latency_seconds: float
    error: str | None = None


@dataclass
class DeliveryScore:
    final_score: float
    zero_one_edit_acceptance: float
    fact_preservation: float
    no_new_facts: float
    template_compliance: float
    latency_seconds: float
    error_rate: float

    def to_dict(self) -> dict[str, float]:
        return {
            "final_score": round(self.final_score, 6),
            "zero_one_edit_acceptance": round(self.zero_one_edit_acceptance, 6),
            "fact_preservation": round(self.fact_preservation, 6),
            "no_new_facts": round(self.no_new_facts, 6),
            "template_compliance": round(self.template_compliance, 6),
            "latency_seconds": round(self.latency_seconds, 6),
            "error_rate": round(self.error_rate, 6),
        }


class DeliveryRunner(Protocol):
    name: str

    def run_case(self, case: DeliveryBenchmarkCase, lane: str) -> DeliveryExecution:
        ...


def load_delivery_cases(path: Path = DEFAULT_DATASET_PATH) -> list[DeliveryBenchmarkCase]:
    cases: list[DeliveryBenchmarkCase] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                cases.append(DeliveryBenchmarkCase.model_validate(json.loads(stripped)))
            except (ValidationError, json.JSONDecodeError) as exc:
                raise ValueError(f"Invalid delivery benchmark row {line_number}: {exc}") from exc
    if not cases:
        raise ValueError(f"Dataset {path} is empty")
    return cases


def create_output_dir(output_root: Path = DEFAULT_OUTPUT_ROOT, label: str = "delivery-v2") -> Path:
    timestamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    output_dir = output_root / f"{timestamp}-{label}"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def build_bundle_for_lane(case: DeliveryBenchmarkCase, lane: str) -> WorkflowContextBundle:
    if lane not in SUPPORTED_LANES:
        raise ValueError(f"Unsupported lane: {lane}")
    if lane == "text_only":
        return WorkflowContextBundle(raw_notes=case.raw_notes, warnings=[])

    payload = dict(case.structured_context)
    payload["raw_notes"] = case.raw_notes
    payload.setdefault("warnings", [])
    return WorkflowContextBundle.model_validate(payload)


def build_policy_for_lane(policy: JanPolicy, lane: str) -> JanPolicy:
    if lane == "policy_pack":
        return policy
    return JanPolicy.model_validate(default_policy_payload())


def _section_score(output_text: str, required_sections: list[str]) -> float:
    if not required_sections:
        return 1.0
    matched = 0
    for section in required_sections:
        if any(line.strip().lower().startswith(section.lower()) for line in output_text.splitlines()):
            matched += 1
    return matched / len(required_sections)


def _match_score(output_text: str, phrases: list[str]) -> float:
    if not phrases:
        return 1.0
    output_lower = output_text.lower()
    matched = sum(1 for phrase in phrases if phrase.lower() in output_lower)
    return matched / len(phrases)


def _absence_score(output_text: str, phrases: list[str]) -> float:
    if not phrases:
        return 1.0
    output_lower = output_text.lower()
    absent = sum(1 for phrase in phrases if phrase.lower() not in output_lower)
    return absent / len(phrases)


def score_delivery_execution(case: DeliveryBenchmarkCase, execution: DeliveryExecution) -> DeliveryScore:
    template_score = _section_score(execution.output_text, case.required_sections)
    fact_score = _match_score(execution.output_text, case.must_keep)
    no_new_facts = _absence_score(execution.output_text, case.must_not_introduce)
    non_empty = 1.0 if execution.output_text.strip() else 0.0
    error_free = 0.0 if execution.error else 1.0
    latency_score = 1.0 if execution.latency_seconds <= 5 else max(0.0, 1 - ((execution.latency_seconds - 5) / 10))
    acceptance = 1.0 if min(template_score, fact_score, no_new_facts, non_empty, error_free) == 1.0 else 0.0
    final_score = (
        template_score * 0.25
        + fact_score * 0.25
        + no_new_facts * 0.2
        + acceptance * 0.15
        + latency_score * 0.1
        + error_free * 0.05
    )
    return DeliveryScore(
        final_score=final_score,
        zero_one_edit_acceptance=acceptance,
        fact_preservation=fact_score,
        no_new_facts=no_new_facts,
        template_compliance=template_score,
        latency_seconds=execution.latency_seconds,
        error_rate=0.0 if execution.error is None else 1.0,
    )


class JanDeliveryRunner:
    name = "Jan"

    def __init__(self, policy: JanPolicy | None = None) -> None:
        self.policy = policy

    def run_case(self, case: DeliveryBenchmarkCase, lane: str) -> DeliveryExecution:
        bundle = build_bundle_for_lane(case, lane)
        repo_policy = build_policy_for_lane(self.policy or load_jan_policy(REPO_ROOT)[0], lane)
        start = time.perf_counter()
        try:
            output = execute_repo_native_workflow(
                case.workflow,
                raw_notes=case.raw_notes,
                audience=case.audience,
                response_mode="final",
                policy=repo_policy,
                model_client=bielik,
                context_bundle_override=bundle,
                repo_root=REPO_ROOT,
            )
            return DeliveryExecution(
                system=self.name,
                lane=lane,
                output_text=output,
                latency_seconds=time.perf_counter() - start,
            )
        except Exception as exc:  # pragma: no cover - guardrail for live runs
            return DeliveryExecution(
                system=self.name,
                lane=lane,
                output_text="",
                latency_seconds=time.perf_counter() - start,
                error=str(exc),
            )


class RawBielikDeliveryRunner:
    name = "raw Bielik"

    def __init__(self, policy: JanPolicy | None = None, client: BielikClient | None = None) -> None:
        self.policy = policy
        self.client = client or bielik

    def run_case(self, case: DeliveryBenchmarkCase, lane: str) -> DeliveryExecution:
        bundle = build_bundle_for_lane(case, lane)
        policy = build_policy_for_lane(self.policy or load_jan_policy(REPO_ROOT)[0], lane)
        prompt = build_baseline_prompt(case, bundle, policy)
        start = time.perf_counter()
        try:
            output = self.client.call(prompt["system"], prompt["user"], temperature=0.2)
            return DeliveryExecution(
                system=self.name,
                lane=lane,
                output_text=output.strip(),
                latency_seconds=time.perf_counter() - start,
            )
        except Exception as exc:  # pragma: no cover - guardrail for live runs
            return DeliveryExecution(
                system=self.name,
                lane=lane,
                output_text="",
                latency_seconds=time.perf_counter() - start,
                error=str(exc),
            )


class OpenAIDeliveryRunner:
    name = "GPT-5.4"

    def __init__(self, model: str = DEFAULT_OPENAI_MODEL, policy: JanPolicy | None = None) -> None:
        self.model = model
        self.policy = policy
        self.client = OpenAI()

    def run_case(self, case: DeliveryBenchmarkCase, lane: str) -> DeliveryExecution:
        bundle = build_bundle_for_lane(case, lane)
        policy = build_policy_for_lane(self.policy or load_jan_policy(REPO_ROOT)[0], lane)
        prompt = build_baseline_prompt(case, bundle, policy)
        start = time.perf_counter()
        try:
            response = self.client.responses.create(
                model=self.model,
                input=[
                    {"role": "system", "content": prompt["system"]},
                    {"role": "user", "content": prompt["user"]},
                ],
            )
            output = (response.output_text or "").strip()
            return DeliveryExecution(
                system=self.name,
                lane=lane,
                output_text=output,
                latency_seconds=time.perf_counter() - start,
            )
        except Exception as exc:  # pragma: no cover - guardrail for live runs
            return DeliveryExecution(
                system=self.name,
                lane=lane,
                output_text="",
                latency_seconds=time.perf_counter() - start,
                error=str(exc),
            )


def build_baseline_prompt(
    case: DeliveryBenchmarkCase,
    bundle: WorkflowContextBundle,
    policy: JanPolicy,
) -> dict[str, str]:
    template = policy.get_artifact_template(
        {
            "write_pr_description": "pr_description",
            "compose_release_notes": "release_notes",
            "rewrite_issue": "issue",
            "write_rollout_note": "rollout_note",
        }[case.workflow]
    )
    audience = policy.get_audience(case.audience)
    sections = "\n".join(f"- {section}" for section in template.sections)
    user_message = (
        f"Przygotuj artefakt `{template.title}` po polsku.\n"
        f"Audience: {case.audience}\n"
        f"Wymagane sekcje:\n{sections}\n\n"
        f"Kontekst źródłowy:\n{serialize_context_bundle(bundle)}"
    )
    system_prompt = (
        "Jesteś asystentem do polskojęzycznej komunikacji zmian w software delivery.\n"
        f"Odbiorca: {audience.description}\n"
        f"Instrukcje artefaktu: {template.instructions}\n"
        "Nie dodawaj nowych faktów i zwróć wyłącznie finalny tekst."
    )
    return {"system": system_prompt, "user": user_message}


def run_delivery_benchmark(
    cases: list[DeliveryBenchmarkCase],
    runners: list[DeliveryRunner],
    lanes: tuple[str, ...] = SUPPORTED_LANES,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for runner in runners:
        for lane in lanes:
            for case in cases:
                execution = runner.run_case(case, lane)
                score = score_delivery_execution(case, execution)
                results.append(
                    {
                        "case": case.model_dump(),
                        "system": runner.name,
                        "lane": lane,
                        "output_text": execution.output_text,
                        "error": execution.error,
                        "score": score.to_dict(),
                    }
                )
    summary = aggregate_delivery_results(results)
    return results, summary


def aggregate_delivery_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    aggregate: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for row in results:
        aggregate.setdefault(row["system"], {}).setdefault(row["lane"], []).append(row["score"])

    summary: dict[str, Any] = {}
    for system, lane_map in aggregate.items():
        summary[system] = {}
        for lane, scores in lane_map.items():
            summary[system][lane] = {
                "final_score": mean(item["final_score"] for item in scores),
                "zero_one_edit_acceptance": mean(item["zero_one_edit_acceptance"] for item in scores),
                "fact_preservation": mean(item["fact_preservation"] for item in scores),
                "no_new_facts": mean(item["no_new_facts"] for item in scores),
                "template_compliance": mean(item["template_compliance"] for item in scores),
                "latency_seconds": mean(item["latency_seconds"] for item in scores),
                "error_rate": mean(item["error_rate"] for item in scores),
            }
    return summary


def render_delivery_report(summary: dict[str, Any]) -> str:
    lines = [
        "# Delivery Benchmark v2",
        "",
        "Benchmark na osi `artifact x context richness x audience` dla repo-native workflowów Jana.",
        "",
    ]
    for lane in SUPPORTED_LANES:
        lines.append(f"## Lane: {lane}")
        lines.append("")
        lines.append("| System | Final | Acceptance | Fact preservation | No new facts | Template | Avg latency |")
        lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
        for system in sorted(summary.keys()):
            row = summary[system].get(lane)
            if not row:
                continue
            lines.append(
                "| "
                + f"{system} | "
                + f"{row['final_score'] * 100:.1f}% | "
                + f"{row['zero_one_edit_acceptance'] * 100:.1f}% | "
                + f"{row['fact_preservation'] * 100:.1f}% | "
                + f"{row['no_new_facts'] * 100:.1f}% | "
                + f"{row['template_compliance'] * 100:.1f}% | "
                + f"{row['latency_seconds']:.2f}s |"
            )
        lines.append("")
    lines.extend(
        [
            "## KPI Targets",
            "",
            "- PR zero/one-edit acceptance: `>=70%`",
            "- Release notes zero/one-edit acceptance: `>=60%`",
            "- Fact preservation: `>=99%`",
            "- No-new-facts violation rate: `<2%`",
            "- Template/glossary compliance: `>=95%`",
            "- Repo-aware jobs p95: `<5s`",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def write_delivery_results(output_dir: Path, results: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "report.md").write_text(render_delivery_report(summary), encoding="utf-8")
