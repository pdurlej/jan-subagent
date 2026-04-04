"""
Harness benchmarkowy dla pilota workplace writing.
"""

from __future__ import annotations

import json
import os
import re
import time
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Protocol
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator

from .config import config
from .output_utils import normalize_benchmark_output

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_PATH = REPO_ROOT / "benchmarks" / "workplace_writing_v1.jsonl"
DEFAULT_PROMPT_FAMILIES_PATH = REPO_ROOT / "benchmarks" / "prompt_families.json"
DEFAULT_JUDGE_RUBRIC_PATH = REPO_ROOT / "benchmarks" / "judge_rubric.md"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "_bmad-output" / "benchmarks"
DEFAULT_OPENAI_MODEL = "gpt-5.4"
DEFAULT_JUDGE_MODEL = "gpt-5.4-mini"

SUPPORTED_INTENTS = (
    "surface correction",
    "style rewrite",
    "full polish",
)

SUPPORTED_SCENARIOS = (
    "PR description",
    "ticket/issue",
    "support reply",
    "release note/changelog",
    "status email/notatka",
)

PROMPT_FAMILY_TO_JAN_TOOL = {
    "surface_orthography": "correct_orthography",
    "surface_punctuation": "correct_punctuation",
    "style_prosty": "improve_style",
    "style_elegancki": "improve_style",
    "full_polish_standard": "comprehensive_correction",
}

FINAL_SCORE_WEIGHTS = {
    "surface correction": {"deterministic": 0.7, "judge": 0.3},
    "style rewrite": {"deterministic": 0.4, "judge": 0.6},
    "full polish": {"deterministic": 0.4, "judge": 0.6},
}

DETERMINISTIC_COMPONENT_WEIGHTS = {
    "must_keep": 0.3,
    "should_fix": 0.25,
    "must_not_introduce": 0.15,
    "non_empty": 0.1,
    "error_free": 0.1,
    "latency": 0.1,
}

LATENCY_SWEET_SPOT_SECONDS = {
    "surface correction": 4.0,
    "style rewrite": 6.0,
    "full polish": 9.0,
}

LATENCY_MAX_SECONDS = {
    "surface correction": 20.0,
    "style rewrite": 25.0,
    "full polish": 30.0,
}


class BenchmarkCase(BaseModel):
    """Jeden przypadek benchmarkowy dla workplace writing."""

    id: str
    scenario: str
    intent: str
    input_text: str
    jan_tool: str
    baseline_prompt_family: str
    must_keep: list[str] = Field(default_factory=list)
    should_fix: list[str] = Field(default_factory=list)
    must_not_introduce: list[str] = Field(default_factory=list)
    notes: str = ""

    @field_validator("scenario")
    @classmethod
    def validate_scenario(cls, value: str) -> str:
        if value not in SUPPORTED_SCENARIOS:
            raise ValueError(f"Unsupported scenario: {value}")
        return value

    @field_validator("intent")
    @classmethod
    def validate_intent(cls, value: str) -> str:
        if value not in SUPPORTED_INTENTS:
            raise ValueError(f"Unsupported intent: {value}")
        return value

    @field_validator("jan_tool")
    @classmethod
    def validate_jan_tool(cls, value: str) -> str:
        if value not in PROMPT_FAMILY_TO_JAN_TOOL.values():
            raise ValueError(f"Unsupported Jan tool: {value}")
        return value

    @field_validator("must_keep", "should_fix", "must_not_introduce")
    @classmethod
    def validate_string_lists(cls, value: list[str]) -> list[str]:
        if not isinstance(value, list):
            raise ValueError("Expected a list of strings")
        cleaned = [item.strip() for item in value if item.strip()]
        if len(cleaned) != len(value):
            raise ValueError("String lists must not contain empty items")
        return cleaned

    @model_validator(mode="after")
    def validate_tool_matches_prompt_family(self) -> "BenchmarkCase":
        expected_tool = PROMPT_FAMILY_TO_JAN_TOOL.get(self.baseline_prompt_family)
        if not expected_tool:
            raise ValueError(
                f"Unsupported baseline prompt family: {self.baseline_prompt_family}"
            )
        if self.jan_tool != expected_tool:
            raise ValueError(
                "jan_tool must match baseline_prompt_family; "
                f"expected {expected_tool}, got {self.jan_tool}"
            )
        return self


class PromptFamily(BaseModel):
    """Konfiguracja promptu baseline."""

    intent: str
    jan_tool: str
    instructions: str
    temperature: float
    jan_style: str | None = None
    jan_mode: str | None = None

    @field_validator("intent")
    @classmethod
    def validate_intent(cls, value: str) -> str:
        if value not in SUPPORTED_INTENTS:
            raise ValueError(f"Unsupported intent in prompt family: {value}")
        return value


class JudgeVerdict(BaseModel):
    """Ustrukturyzowana odpowiedź modelu-judga."""

    factual_preservation: int = Field(ge=1, le=5)
    language_quality: int = Field(ge=1, le=5)
    clarity: int = Field(ge=1, le=5)
    workplace_usefulness: int = Field(ge=1, le=5)
    concision: int = Field(ge=1, le=5)
    rationale: str = Field(min_length=1)


@dataclass
class ModelExecution:
    """Surowy wynik pojedynczego systemu na jednym case."""

    system: str
    output_text: str
    latency_seconds: float
    normalized_output_text: str | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def get_normalized_output_text(self) -> str:
        """Zwraca output diagnostyczny po normalizacji wrappera."""

        return self.normalized_output_text if self.normalized_output_text is not None else self.output_text


@dataclass
class DeterministicScore:
    total: float
    components: dict[str, float]
    matched: dict[str, list[str]]
    missing: dict[str, list[str]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": round(self.total, 6),
            "components": {key: round(value, 6) for key, value in self.components.items()},
            "matched": self.matched,
            "missing": self.missing,
        }


@dataclass
class JudgeScore:
    total: float
    dimensions: dict[str, float]
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": round(self.total, 6),
            "dimensions": {
                key: round(value, 6) for key, value in self.dimensions.items()
            },
            "rationale": self.rationale,
        }


@dataclass
class Scorecard:
    deterministic: DeterministicScore
    judge: JudgeScore
    final_score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "deterministic": self.deterministic.to_dict(),
            "judge": self.judge.to_dict(),
            "final_score": round(self.final_score, 6),
        }


@dataclass
class ScoredResult:
    case: BenchmarkCase
    execution: ModelExecution
    literal: Scorecard
    normalized: Scorecard

    def to_dict(self) -> dict[str, Any]:
        return {
            "case": self.case.model_dump(),
            "system": self.execution.system,
            "output_text": self.execution.output_text,
            "normalized_output_text": self.execution.get_normalized_output_text(),
            "latency_seconds": round(self.execution.latency_seconds, 6),
            "error": self.execution.error,
            "metadata": self.execution.metadata,
            "literal": self.literal.to_dict(),
            "normalized": self.normalized.to_dict(),
        }


class AsyncSystemRunner(Protocol):
    name: str

    async def run_case(self, case: BenchmarkCase) -> ModelExecution:
        ...


class AsyncJudge(Protocol):
    async def score(self, case: BenchmarkCase, execution: ModelExecution) -> JudgeScore:
        ...


def load_cases(dataset_path: Path = DEFAULT_DATASET_PATH) -> list[BenchmarkCase]:
    """Ładuje przypadki benchmarkowe z JSONL."""

    cases: list[BenchmarkCase] = []
    with dataset_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                raw = json.loads(stripped)
                cases.append(BenchmarkCase.model_validate(raw))
            except (json.JSONDecodeError, ValidationError) as exc:
                raise ValueError(
                    f"Invalid dataset row at line {line_number} in {dataset_path}: {exc}"
                ) from exc
    if not cases:
        raise ValueError(f"Dataset {dataset_path} is empty")
    return cases


def load_prompt_families(
    prompt_path: Path = DEFAULT_PROMPT_FAMILIES_PATH,
) -> dict[str, PromptFamily]:
    """Ładuje definicje promptów baseline."""

    payload = json.loads(prompt_path.read_text(encoding="utf-8"))
    families = {
        family_name: PromptFamily.model_validate(config_data)
        for family_name, config_data in payload.items()
    }
    for family_name, family in families.items():
        expected_tool = PROMPT_FAMILY_TO_JAN_TOOL[family_name]
        if family.jan_tool != expected_tool:
            raise ValueError(
                f"Prompt family {family_name} points to {family.jan_tool}, "
                f"expected {expected_tool}"
            )
    return families


def load_judge_rubric(rubric_path: Path = DEFAULT_JUDGE_RUBRIC_PATH) -> str:
    """Ładuje rubric dla modelu-judga."""

    return rubric_path.read_text(encoding="utf-8").strip()


def build_jan_tool_call(
    case: BenchmarkCase, prompt_families: dict[str, PromptFamily]
) -> tuple[str, dict[str, Any]]:
    """Buduje nazwę narzędzia Jana i jego argumenty w domyślnym UX."""

    family = prompt_families[case.baseline_prompt_family]
    arguments: dict[str, Any] = {"text": case.input_text}

    if case.jan_tool == "improve_style":
        arguments["style"] = family.jan_style or "elegancki"
    elif case.jan_tool == "comprehensive_correction":
        arguments["mode"] = family.jan_mode or "standard"

    return case.jan_tool, arguments


def build_baseline_prompt(
    case: BenchmarkCase, prompt_families: dict[str, PromptFamily]
) -> dict[str, Any]:
    """Buduje minimalny prompt baseline bez persony Jana."""

    family = prompt_families[case.baseline_prompt_family]
    payload = (
        f"Scenariusz: {case.scenario}\n"
        f"Intencja: {case.intent}\n"
        "Wymaganie: zachowaj sens, fakty, liczby i nazwy własne. "
        "Nie dodawaj komentarza o zmianach. Zwróć wyłącznie finalny tekst.\n\n"
        f"Tekst wejściowy:\n{case.input_text}"
    )
    return {
        "instructions": family.instructions,
        "input_text": payload,
        "temperature": family.temperature,
        "family": case.baseline_prompt_family,
    }


def normalize_text_for_matching(text: str) -> str:
    """Normalizuje output do prostych porównań substringowych."""

    normalized = unicodedata.normalize("NFKC", text)
    normalized = normalized.replace("**", "")
    normalized = normalized.replace("__", "")
    normalized = normalized.replace("*", "")
    normalized = normalized.replace("`", "")
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip().casefold()


def measure_fraction_present(output_text: str, phrases: list[str]) -> tuple[float, list[str], list[str]]:
    """Mierzy, ile wymaganych fraz jest obecnych."""

    if not phrases:
        return 1.0, [], []

    normalized_output = normalize_text_for_matching(output_text)
    matched = [
        phrase for phrase in phrases if normalize_text_for_matching(phrase) in normalized_output
    ]
    missing = [phrase for phrase in phrases if phrase not in matched]
    return len(matched) / len(phrases), matched, missing


def measure_fraction_removed(output_text: str, phrases: list[str]) -> tuple[float, list[str], list[str]]:
    """Mierzy, ile niepożądanych fraz zniknęło z outputu."""

    if not phrases:
        return 1.0, [], []

    normalized_output = normalize_text_for_matching(output_text)
    removed = [
        phrase
        for phrase in phrases
        if normalize_text_for_matching(phrase) not in normalized_output
    ]
    still_present = [phrase for phrase in phrases if phrase not in removed]
    return len(removed) / len(phrases), removed, still_present


def latency_score(intent: str, latency_seconds: float) -> float:
    """Konwertuje latency do przedziału 0-1."""

    sweet_spot = LATENCY_SWEET_SPOT_SECONDS[intent]
    hard_cap = LATENCY_MAX_SECONDS[intent]
    if latency_seconds <= sweet_spot:
        return 1.0
    if latency_seconds >= hard_cap:
        return 0.0
    return max(0.0, 1.0 - ((latency_seconds - sweet_spot) / (hard_cap - sweet_spot)))


def compute_deterministic_score(
    case: BenchmarkCase,
    output_text: str,
    latency_seconds: float,
    error: str | None = None,
) -> DeterministicScore:
    """Liczy warstwę deterministyczną benchmarku."""

    keep_score, kept, keep_missing = measure_fraction_present(
        output_text, case.must_keep
    )
    fix_score, fixed, fix_missing = measure_fraction_removed(
        output_text, case.should_fix
    )
    guard_score, guarded, guard_missing = measure_fraction_removed(
        output_text, case.must_not_introduce
    )
    non_empty = 1.0 if output_text.strip() else 0.0
    error_free = 1.0 if not error else 0.0
    latency_component = latency_score(case.intent, latency_seconds)

    components = {
        "must_keep": keep_score,
        "should_fix": fix_score,
        "must_not_introduce": guard_score,
        "non_empty": non_empty,
        "error_free": error_free,
        "latency": latency_component,
    }
    total = sum(
        value * DETERMINISTIC_COMPONENT_WEIGHTS[key]
        for key, value in components.items()
    )
    return DeterministicScore(
        total=total,
        components=components,
        matched={
            "must_keep": kept,
            "should_fix": fixed,
            "must_not_introduce": guarded,
        },
        missing={
            "must_keep": keep_missing,
            "should_fix": fix_missing,
            "must_not_introduce": guard_missing,
        },
    )


def compute_final_score(
    case: BenchmarkCase,
    deterministic_score: DeterministicScore,
    judge_score: JudgeScore,
) -> float:
    """Łączy warstwę deterministyczną z oceną judge modelu."""

    weights = FINAL_SCORE_WEIGHTS[case.intent]
    return (
        deterministic_score.total * weights["deterministic"]
        + judge_score.total * weights["judge"]
    )


def select_scorecard(result: ScoredResult, score_kind: str) -> Scorecard:
    """Wybiera literalny lub znormalizowany scorecard."""

    if score_kind == "literal":
        return result.literal
    if score_kind == "normalized":
        return result.normalized
    raise ValueError(f"Unsupported score kind: {score_kind}")


def average_scores(scored_results: list[ScoredResult], score_kind: str) -> dict[str, float]:
    """Średnie dla listy wyników."""

    return {
        "final_score": mean(select_scorecard(result, score_kind).final_score for result in scored_results),
        "deterministic_score": mean(
            select_scorecard(result, score_kind).deterministic.total
            for result in scored_results
        ),
        "judge_score": mean(
            select_scorecard(result, score_kind).judge.total for result in scored_results
        ),
        "latency_seconds": mean(
            result.execution.latency_seconds for result in scored_results
        ),
        "error_rate": sum(1 for result in scored_results if result.execution.error)
        / len(scored_results),
    }


def aggregate_results(scored_results: list[ScoredResult], score_kind: str = "literal") -> dict[str, Any]:
    """Agreguje wyniki per system, scenario i intent."""

    if not scored_results:
        raise ValueError("Cannot aggregate an empty benchmark run")

    grouped_by_system: dict[str, list[ScoredResult]] = {}
    grouped_by_scenario: dict[str, dict[str, list[ScoredResult]]] = {}
    grouped_by_intent: dict[str, dict[str, list[ScoredResult]]] = {}

    for result in scored_results:
        grouped_by_system.setdefault(result.execution.system, []).append(result)
        grouped_by_scenario.setdefault(result.case.scenario, {}).setdefault(
            result.execution.system, []
        ).append(result)
        grouped_by_intent.setdefault(result.case.intent, {}).setdefault(
            result.execution.system, []
        ).append(result)

    overall = {
        system: average_scores(results, score_kind)
        for system, results in sorted(grouped_by_system.items())
    }
    by_scenario = {
        scenario: {
            system: average_scores(results, score_kind)
            for system, results in sorted(system_results.items())
        }
        for scenario, system_results in grouped_by_scenario.items()
    }
    by_intent = {
        intent: {
            system: average_scores(results, score_kind)
            for system, results in sorted(system_results.items())
        }
        for intent, system_results in grouped_by_intent.items()
    }

    jan_name = "Jan"
    jan_scenario_rows = []
    for scenario, systems in by_scenario.items():
        if jan_name not in systems:
            continue
        leader = max(
            systems.items(), key=lambda item: item[1]["final_score"]
        )
        jan_score = systems[jan_name]["final_score"]
        jan_scenario_rows.append(
            {
                "scenario": scenario,
                "jan_score": jan_score,
                "leader": leader[0],
                "leader_score": leader[1]["final_score"],
                "delta_to_leader": jan_score - leader[1]["final_score"],
            }
        )

    jan_scenario_rows.sort(key=lambda row: row["delta_to_leader"], reverse=True)
    top_use_cases = jan_scenario_rows[:2]
    weak_spots = sorted(jan_scenario_rows, key=lambda row: row["delta_to_leader"])[:2]

    return {
        "overall": overall,
        "by_scenario": by_scenario,
        "by_intent": by_intent,
        "top_use_cases_for_jan": top_use_cases,
        "weak_spots_for_jan": weak_spots,
    }


def score_to_pct(score: float) -> str:
    """Format procentowy dla raportu."""

    return f"{score * 100:.1f}%"


def extend_score_section(lines: list[str], title: str, aggregate: dict[str, Any]) -> None:
    """Dokleja sekcję score tables dla wybranego widoku benchmarku."""

    lines.extend(
        [
            f"## {title}",
            "",
            "| System | Final | Deterministic | Judge | Avg latency | Error rate |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )

    for system, row in aggregate["overall"].items():
        lines.append(
            "| "
            f"{system} | {score_to_pct(row['final_score'])} | "
            f"{score_to_pct(row['deterministic_score'])} | "
            f"{score_to_pct(row['judge_score'])} | "
            f"{row['latency_seconds']:.2f}s | {score_to_pct(row['error_rate'])} |"
        )

    lines.extend(
        [
            "",
            "| Scenario | Jan | raw Bielik | GPT-5.4 | Lider |",
            "| --- | ---: | ---: | ---: | --- |",
        ]
    )
    for scenario, systems in aggregate["by_scenario"].items():
        leader_name, leader_row = max(
            systems.items(), key=lambda item: item[1]["final_score"]
        )
        lines.append(
            "| "
            f"{scenario} | "
            f"{score_to_pct(systems['Jan']['final_score'])} | "
            f"{score_to_pct(systems['raw Bielik']['final_score'])} | "
            f"{score_to_pct(systems['GPT-5.4']['final_score'])} | "
            f"{leader_name} ({score_to_pct(leader_row['final_score'])}) |"
        )

    lines.append("")


def render_report_markdown(
    metadata: dict[str, Any],
    cases: list[BenchmarkCase],
    scored_results: list[ScoredResult],
    aggregate: dict[str, Any],
) -> str:
    """Renderuje public-safe raport Markdown z pilota."""

    lines = [
        "# Workplace Writing Pilot",
        "",
        "> Ten raport opisuje pilot benchmarkowy. Wyniki dotyczą wyłącznie tego zestawu 15 przypadków i nie są pełnym badaniem statystycznym.",
        "",
        "## Zakres",
        "",
        f"- Timestamp runu: `{metadata['timestamp']}`",
        f"- Liczba przypadków: `{len(cases)}`",
        f"- Systemy: `{', '.join(metadata['systems'])}`",
        f"- Model OpenAI baseline: `{metadata['openai_model']}`",
        f"- Model judge: `{metadata['judge_model']}`",
        f"- Model NVIDIA/Bielik: `{metadata['bielik_model']}`",
        "",
        "## Scoring Modes",
        "",
        "- `Primary Literal Score` jest głównym KPI produktu i ocenia dokładnie to, co użytkownik dostaje z narzędzia.",
        "- `Normalized Diagnostic Score` usuwa technicznie wrapper Jana i służy tylko do sprawdzenia, ile kosztuje opakowanie odpowiedzi.",
        "",
    ]
    extend_score_section(lines, "Primary Literal Score", aggregate["literal"])
    extend_score_section(lines, "Normalized Diagnostic Score", aggregate["normalized"])

    jan_positive_rows = [
        row
        for row in aggregate["literal"]["top_use_cases_for_jan"]
        if row["delta_to_leader"] >= 0
    ]
    lines.extend(["", "## Where Jan Helps", ""])

    if jan_positive_rows:
        for row in jan_positive_rows:
            lines.append(
                f"- `{row['scenario']}`: Jan prowadzi z wynikiem {score_to_pct(row['jan_score'])}."
            )
    else:
        lines.append(
            "- W tym pilocie Jan nie prowadzi w żadnym scenariuszu, więc poniżej pokazane są najmniejsze straty względem lidera."
        )
        for row in aggregate["literal"]["top_use_cases_for_jan"]:
            lines.append(
                f"- `{row['scenario']}`: Jan ma wynik {score_to_pct(row['jan_score'])} i traci {score_to_pct(abs(row['delta_to_leader']))} względem lidera `{row['leader']}`."
            )

    lines.extend(
        [
            "",
            "## Where Jan Hurts",
            "",
        ]
    )

    for row in aggregate["literal"]["weak_spots_for_jan"]:
        lines.append(
            f"- `{row['scenario']}`: Jan ma wynik {score_to_pct(row['jan_score'])}, a lider `{row['leader']}` osiąga {score_to_pct(row['leader_score'])}."
        )

    jan_surface_results = [
        result
        for result in scored_results
        if result.execution.system == "Jan" and result.case.intent == "surface correction"
    ]
    jan_surface_concision = mean(
        result.literal.judge.dimensions["concision"] for result in jan_surface_results
    )
    jan_surface_workplace = mean(
        result.literal.judge.dimensions["workplace_usefulness"] for result in jan_surface_results
    )
    jan_surface_normalized_concision = mean(
        result.normalized.judge.dimensions["concision"] for result in jan_surface_results
    )
    jan_surface_normalized_workplace = mean(
        result.normalized.judge.dimensions["workplace_usefulness"] for result in jan_surface_results
    )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"- W tym pilocie Jan ma średni score concision `{score_to_pct(jan_surface_concision)}` dla `surface correction`, co pozwala zobaczyć koszt persony i refleksji w krótkich zadaniach.",
            f"- Średni score workplace usefulness Jana dla `surface correction` wynosi `{score_to_pct(jan_surface_workplace)}`; to pokazuje, czy domyślny UX pomaga mimo dłuższego outputu.",
            f"- Po technicznym odfiltrowaniu wrappera Jana surface-correction concision rośnie do `{score_to_pct(jan_surface_normalized_concision)}`, a workplace usefulness do `{score_to_pct(jan_surface_normalized_workplace)}`.",
            "- Raport nie czyści ręcznie outputów Jana. Persona, refleksje i ewentualne ozdobniki liczą się do literalnej oceny systemu.",
            "",
            "## Artefakty",
            "",
            f"- Surowe wyniki i raport live są zapisane w `{metadata['output_dir']}`.",
            "- Metodologia benchmarku znajduje się w `docs/benchmark-methodology.md`.",
        ]
    )

    return "\n".join(lines) + "\n"


def write_json(path: Path, payload: Any) -> None:
    """Zapisuje JSON z czytelnym formatowaniem."""

    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def create_output_dir(
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    run_label: str | None = None,
) -> Path:
    """Tworzy katalog wyników live runu."""

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    suffix = f"-{run_label}" if run_label else ""
    output_dir = output_root / f"{timestamp}{suffix}"
    output_dir.mkdir(parents=True, exist_ok=False)
    return output_dir


def flatten_mcp_text(payload: Any) -> str:
    """Wyciąga literalny tekst z odpowiedzi MCP."""

    content = getattr(payload, "content", None)
    if content:
        parts = []
        for item in content:
            if getattr(item, "type", None) == "text":
                parts.append(getattr(item, "text", ""))
        if parts:
            return "\n".join(part for part in parts if part)
    structured = getattr(payload, "structuredContent", None)
    if isinstance(structured, dict) and "result" in structured:
        return str(structured["result"])
    return ""


class JanMcpRunner:
    """Runner dla Jana przez realne MCP stdio."""

    name = "Jan"

    def __init__(
        self,
        jan_python: str,
        jan_cwd: Path,
        prompt_families: dict[str, PromptFamily],
    ) -> None:
        self.jan_python = jan_python
        self.jan_cwd = jan_cwd
        self.prompt_families = prompt_families
        self._stack: AsyncExitStack | None = None
        self._session: ClientSession | None = None
        self.tool_names: list[str] = []

    async def __aenter__(self) -> "JanMcpRunner":
        self._stack = AsyncExitStack()
        server_params = StdioServerParameters(
            command=self.jan_python,
            args=["-m", "jan.jan_subagent_opencode"],
            cwd=str(self.jan_cwd),
            env={},
        )
        read_stream, write_stream = await self._stack.enter_async_context(
            stdio_client(server_params)
        )
        self._session = await self._stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )
        await self._session.initialize()
        tools_result = await self._session.list_tools()
        self.tool_names = [tool.name for tool in tools_result.tools]
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._stack is not None:
            await self._stack.aclose()
        self._stack = None
        self._session = None

    async def run_case(self, case: BenchmarkCase) -> ModelExecution:
        if self._session is None:
            raise RuntimeError("JanMcpRunner has not been started")

        tool_name, arguments = build_jan_tool_call(case, self.prompt_families)
        started = time.perf_counter()
        try:
            result = await self._session.call_tool(tool_name, arguments)
            latency = time.perf_counter() - started
            output_text = flatten_mcp_text(result)
            return ModelExecution(
                system=self.name,
                output_text=output_text,
                normalized_output_text=normalize_benchmark_output(self.name, output_text),
                latency_seconds=latency,
                error=None if not getattr(result, "isError", False) else "MCP tool error",
                metadata={"tool_name": tool_name, "tool_names": self.tool_names},
            )
        except Exception as exc:
            latency = time.perf_counter() - started
            return ModelExecution(
                system=self.name,
                output_text="",
                normalized_output_text="",
                latency_seconds=latency,
                error=str(exc),
                metadata={"tool_name": tool_name, "tool_names": self.tool_names},
            )


class RawBielikRunner:
    """Runner dla surowego Bielika bez persony Jana."""

    name = "raw Bielik"

    def __init__(self, prompt_families: dict[str, PromptFamily]) -> None:
        self.prompt_families = prompt_families
        self.client = OpenAI(base_url=config.api_base, api_key=config.api_key)

    async def run_case(self, case: BenchmarkCase) -> ModelExecution:
        prompt = build_baseline_prompt(case, self.prompt_families)
        started = time.perf_counter()
        try:
            response = self.client.chat.completions.create(
                model=config.model_id,
                messages=[
                    {"role": "system", "content": prompt["instructions"]},
                    {"role": "user", "content": prompt["input_text"]},
                ],
                temperature=prompt["temperature"],
                max_tokens=config.max_tokens,
                top_p=0.9,
            )
            latency = time.perf_counter() - started
            content = response.choices[0].message.content if response.choices else ""
            return ModelExecution(
                system=self.name,
                output_text=content or "",
                normalized_output_text=normalize_benchmark_output(self.name, content or ""),
                latency_seconds=latency,
                metadata={"prompt_family": prompt["family"], "model": config.model_id},
            )
        except Exception as exc:
            latency = time.perf_counter() - started
            return ModelExecution(
                system=self.name,
                output_text="",
                normalized_output_text="",
                latency_seconds=latency,
                error=str(exc),
                metadata={"prompt_family": prompt["family"], "model": config.model_id},
            )


class OpenAIWorkplaceRunner:
    """Runner baseline na modelu OpenAI."""

    name = "GPT-5.4"

    def __init__(
        self,
        model: str,
        prompt_families: dict[str, PromptFamily],
    ) -> None:
        self.model = model
        self.prompt_families = prompt_families
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required for the GPT-5.4 baseline")
        self.client = OpenAI(api_key=api_key)

    async def run_case(self, case: BenchmarkCase) -> ModelExecution:
        prompt = build_baseline_prompt(case, self.prompt_families)
        started = time.perf_counter()
        try:
            response = self.client.responses.create(
                model=self.model,
                instructions=prompt["instructions"],
                input=prompt["input_text"],
                temperature=prompt["temperature"],
                max_output_tokens=800,
            )
            latency = time.perf_counter() - started
            return ModelExecution(
                system=self.name,
                output_text=response.output_text,
                normalized_output_text=normalize_benchmark_output(
                    self.name, response.output_text
                ),
                latency_seconds=latency,
                metadata={"prompt_family": prompt["family"], "model": self.model},
            )
        except Exception as exc:
            latency = time.perf_counter() - started
            return ModelExecution(
                system=self.name,
                output_text="",
                normalized_output_text="",
                latency_seconds=latency,
                error=str(exc),
                metadata={"prompt_family": prompt["family"], "model": self.model},
            )


class OpenAIJudge:
    """Judge model oceniający literalny output bez czyszczenia persony."""

    def __init__(self, model: str, rubric: str) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required for the benchmark judge")
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.rubric = rubric

    async def score(
        self,
        case: BenchmarkCase,
        execution: ModelExecution,
        output_text: str | None = None,
    ) -> JudgeScore:
        text_to_score = (output_text if output_text is not None else execution.output_text).strip()
        if execution.error:
            return JudgeScore(
                total=0.0,
                dimensions={
                    "factual_preservation": 0.0,
                    "language_quality": 0.0,
                    "clarity": 0.0,
                    "workplace_usefulness": 0.0,
                    "concision": 0.0,
                },
                rationale=f"System failed before output generation: {execution.error}",
            )

        prompt = (
            f"{self.rubric}\n\n"
            f"Scenariusz: {case.scenario}\n"
            f"Intencja: {case.intent}\n"
            f"Tekst wejściowy:\n{case.input_text}\n\n"
            f"Output do oceny:\n{text_to_score}"
        )
        parsed = self.client.responses.parse(
            model=self.model,
            instructions=(
                "Oceń odpowiedź ślepo. Nie zakładaj, jaki system ją wygenerował. "
                "Zwróć tylko ustrukturyzowaną ocenę zgodną ze schematem."
            ),
            input=prompt,
            text_format=JudgeVerdict,
            temperature=0.0,
            max_output_tokens=400,
        )
        verdict: JudgeVerdict = parsed.output_parsed
        dimensions = {
            "factual_preservation": verdict.factual_preservation / 5.0,
            "language_quality": verdict.language_quality / 5.0,
            "clarity": verdict.clarity / 5.0,
            "workplace_usefulness": verdict.workplace_usefulness / 5.0,
            "concision": verdict.concision / 5.0,
        }
        total = mean(dimensions.values())
        return JudgeScore(total=total, dimensions=dimensions, rationale=verdict.rationale)


async def run_benchmark(
    cases: list[BenchmarkCase],
    runners: list[AsyncSystemRunner],
    judge: AsyncJudge,
    output_dir: Path,
    metadata: dict[str, Any],
) -> tuple[list[ScoredResult], dict[str, Any], str]:
    """Uruchamia benchmark i zapisuje artefakty po każdej iteracji."""

    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "metadata.json", metadata)
    write_json(output_dir / "cases.json", [case.model_dump() for case in cases])

    scored_results: list[ScoredResult] = []

    for case in cases:
        for runner in runners:
            execution = await runner.run_case(case)
            literal_deterministic = compute_deterministic_score(
                case,
                execution.output_text,
                latency_seconds=execution.latency_seconds,
                error=execution.error,
            )
            literal_judge = await judge.score(case, execution, output_text=execution.output_text)
            literal_final_score = compute_final_score(
                case, literal_deterministic, literal_judge
            )
            normalized_text = execution.get_normalized_output_text()
            normalized_deterministic = compute_deterministic_score(
                case,
                normalized_text,
                latency_seconds=execution.latency_seconds,
                error=execution.error,
            )
            normalized_judge = await judge.score(
                case, execution, output_text=normalized_text
            )
            normalized_final_score = compute_final_score(
                case, normalized_deterministic, normalized_judge
            )
            scored_result = ScoredResult(
                case=case,
                execution=execution,
                literal=Scorecard(
                    deterministic=literal_deterministic,
                    judge=literal_judge,
                    final_score=literal_final_score,
                ),
                normalized=Scorecard(
                    deterministic=normalized_deterministic,
                    judge=normalized_judge,
                    final_score=normalized_final_score,
                ),
            )
            scored_results.append(scored_result)
            write_json(
                output_dir / "results.json",
                [result.to_dict() for result in scored_results],
            )

    aggregate = {
        "literal": aggregate_results(scored_results, score_kind="literal"),
        "normalized": aggregate_results(scored_results, score_kind="normalized"),
    }
    report = render_report_markdown(metadata, cases, scored_results, aggregate)
    write_json(output_dir / "summary.json", aggregate)
    (output_dir / "report.md").write_text(report, encoding="utf-8")
    return scored_results, aggregate, report
