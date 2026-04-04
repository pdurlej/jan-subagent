"""
Repo-level policy pack dla repo-native workflowów Jana.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class GlossaryEntry(BaseModel):
    preferred: str
    aliases: list[str] = Field(default_factory=list)
    description: str = ""


class ArtifactTemplate(BaseModel):
    title: str
    sections: list[str] = Field(default_factory=list)
    instructions: str = ""


class AudiencePack(BaseModel):
    description: str
    banned_terms: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class ValidationPolicy(BaseModel):
    preserve_identifiers: bool = True
    require_sections: bool = True
    enforce_no_new_facts: bool = True
    enforce_glossary: bool = True
    require_traceability: bool = True


class GitHubPolicy(BaseModel):
    repository: str | None = None
    api_base: str = "https://api.github.com"


class JiraPolicy(BaseModel):
    base_url: str | None = None
    project_keys: list[str] = Field(default_factory=list)


class JanPolicy(BaseModel):
    version: int = 1
    glossary: list[GlossaryEntry] = Field(default_factory=list)
    do_not_translate: list[str] = Field(default_factory=list)
    banned_phrases: list[str] = Field(default_factory=list)
    artifact_templates: dict[str, ArtifactTemplate] = Field(default_factory=dict)
    required_sections: dict[str, list[str]] = Field(default_factory=dict)
    audiences: dict[str, AudiencePack] = Field(default_factory=dict)
    validation: ValidationPolicy = Field(default_factory=ValidationPolicy)
    github: GitHubPolicy = Field(default_factory=GitHubPolicy)
    jira: JiraPolicy = Field(default_factory=JiraPolicy)

    def get_artifact_template(self, artifact_key: str) -> ArtifactTemplate:
        return self.artifact_templates[artifact_key]

    def get_required_sections(self, artifact_key: str) -> list[str]:
        sections = self.required_sections.get(artifact_key)
        if sections:
            return sections
        return self.artifact_templates[artifact_key].sections

    def get_audience(self, audience: str) -> AudiencePack:
        if audience not in self.audiences:
            raise ValueError(f"Unsupported audience: {audience}")
        return self.audiences[audience]


def default_policy_payload() -> dict[str, Any]:
    return {
        "version": 1,
        "glossary": [
            {
                "preferred": "wdrożenie",
                "aliases": ["deploy", "deployment"],
                "description": "Używaj polskiej formy w opisach zmian.",
            },
            {
                "preferred": "opis PR",
                "aliases": ["PR description"],
                "description": "W komunikacji zespołu używaj polskiej nazwy artefaktu.",
            },
            {
                "preferred": "release notes",
                "aliases": ["release note", "changelog dla klienta"],
                "description": "Nazwa artefaktu klient-facing pozostaje angielska.",
            },
        ],
        "do_not_translate": [
            "GitHub",
            "Jira",
            "Sentry",
            "CI",
            "CD",
            "API",
            "PR",
            "feature flag",
        ],
        "banned_phrases": [
            "to tylko drobna zmiana",
            "wydaje się, że",
            "prawdopodobnie działa",
        ],
        "artifact_templates": {
            "pr_description": {
                "title": "Opis PR",
                "sections": ["Cel zmiany", "Zakres", "Testy", "Ryzyka"],
                "instructions": (
                    "Pisz zwięźle dla reviewerów technicznych. Nie dopisuj nowych faktów "
                    "i jasno oddzielaj zakres od ryzyk."
                ),
            },
            "release_notes": {
                "title": "Release notes",
                "sections": [
                    "Najważniejsze zmiany",
                    "Wpływ dla użytkownika",
                    "Ryzyka",
                ],
                "instructions": (
                    "Twórz komunikat gotowy do publikacji wewnętrznej albo klient-facing, "
                    "bez żargonu niepotrzebnego dla wybranego audience."
                ),
            },
            "issue": {
                "title": "Opis zgłoszenia",
                "sections": [
                    "Kontekst",
                    "Problem",
                    "Kroki odtworzenia",
                    "Oczekiwany rezultat",
                    "Następny krok",
                ],
                "instructions": (
                    "Porządkuj chaotyczne notatki do formy ticketu gotowego dla zespołu."
                ),
            },
            "rollout_note": {
                "title": "Notatka rolloutowa",
                "sections": [
                    "Zakres rolloutu",
                    "Monitoring",
                    "Ryzyka",
                    "Plan wycofania",
                ],
                "instructions": (
                    "Pisz konkretnie operacyjnie. Uwzględniaj monitoring i rollback tylko "
                    "gdy wynikają ze źródeł."
                ),
            },
        },
        "required_sections": {
            "pr_description": ["Cel zmiany", "Zakres", "Testy", "Ryzyka"],
            "release_notes": ["Najważniejsze zmiany", "Wpływ dla użytkownika", "Ryzyka"],
            "issue": [
                "Kontekst",
                "Problem",
                "Kroki odtworzenia",
                "Oczekiwany rezultat",
                "Następny krok",
            ],
            "rollout_note": ["Zakres rolloutu", "Monitoring", "Ryzyka", "Plan wycofania"],
        },
        "audiences": {
            "reviewer": {
                "description": (
                    "Odbiorca techniczny sprawdzający zmianę w PR. Ceni precyzję, testy, "
                    "ryzyka i brak marketingowego tonu."
                ),
                "banned_terms": ["wow", "rewolucyjny"],
                "notes": ["Uwzględnij techniczne ryzyka i testy."],
            },
            "internal": {
                "description": (
                    "Odbiorca wewnętrzny w zespole produktowo-inżynieryjnym. Potrzebuje "
                    "klarownej notatki do współpracy i koordynacji."
                ),
                "banned_terms": ["rewolucyjny"],
                "notes": ["Możesz użyć skrótów zespołowych tylko jeśli są w źródłach."],
            },
            "customer": {
                "description": (
                    "Odbiorca klient-facing. Uprość techniczny żargon i mów o wpływie dla "
                    "użytkownika, ale nie ukrywaj realnych ograniczeń."
                ),
                "banned_terms": ["commit", "branch", "PR", "hotfix"],
                "notes": ["Nie eksponuj wewnętrznych nazw procesów."],
            },
            "exec": {
                "description": (
                    "Odbiorca decyzyjny. Potrzebuje krótkiej, wysokopoziomowej informacji o "
                    "statusie, ryzyku i wpływie biznesowym."
                ),
                "banned_terms": ["nit", "refactor-only", "branch"],
                "notes": ["Skup się na wpływie, nie na szczegółach implementacji."],
            },
        },
        "validation": {
            "preserve_identifiers": True,
            "require_sections": True,
            "enforce_no_new_facts": True,
            "enforce_glossary": True,
            "require_traceability": True,
        },
        "github": {
            "repository": "pdurlej/jan-subagent",
            "api_base": "https://api.github.com",
        },
        "jira": {
            "base_url": "",
            "project_keys": ["JAN"],
        },
    }


def detect_repo_root(start_path: Path | None = None) -> Path:
    """Próbuje znaleźć root repo git bez zgadywania."""

    cwd = Path(start_path or Path.cwd()).resolve()
    try:
        output = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=str(cwd),
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        if output:
            return Path(output)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return cwd


def resolve_policy_path(repo_root: Path | None = None, explicit_path: str | None = None) -> Path:
    """Zwraca ścieżkę do jan.yml."""

    if explicit_path:
        return Path(explicit_path).expanduser().resolve()
    root = detect_repo_root(repo_root)
    return root / "jan.yml"


def load_jan_policy(
    repo_root: Path | None = None,
    explicit_path: str | None = None,
) -> tuple[JanPolicy, Path]:
    """Ładuje policy pack z pliku lub fallbackuje do domyślnego payloadu."""

    policy_path = resolve_policy_path(repo_root=repo_root, explicit_path=explicit_path)
    if policy_path.exists():
        payload = yaml.safe_load(policy_path.read_text(encoding="utf-8")) or {}
        return JanPolicy.model_validate(payload), policy_path
    return JanPolicy.model_validate(default_policy_payload()), policy_path
