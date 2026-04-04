"""
Testy workflowów repo-native Jana v3.
"""

from __future__ import annotations

import json
from pathlib import Path

from jan.jan_subagent_opencode import write_pr_description
from jan.policy import load_jan_policy
from jan.source_context import SourceItem, WorkflowContextBundle
from jan.workflow_engine import (
    build_validator_report,
    collect_context_bundle,
    execute_repo_native_workflow,
    normalize_structured_final_text,
)


class FakeClient:
    def __init__(self, response: str) -> None:
        self.response = response

    def call(self, system_prompt: str, user_message: str, temperature: float = 0.2) -> str:
        assert system_prompt
        assert user_message
        return self.response


def make_bundle() -> WorkflowContextBundle:
    return WorkflowContextBundle(
        raw_notes=(
            "JAN-101: dodaliśmy feature flag checkout_summary i testy smoke dla panelu."
        ),
        warnings=[],
    )


def test_load_jan_policy_reads_repo_file():
    repo_root = Path(__file__).resolve().parents[1]
    policy, path = load_jan_policy(repo_root=repo_root)
    assert path.name == "jan.yml"
    assert policy.get_required_sections("pr_description") == [
        "Cel zmiany",
        "Zakres",
        "Testy",
        "Ryzyka",
    ]
    assert "reviewer" in policy.audiences


def test_collect_context_bundle_warns_without_github_token(monkeypatch):
    repo_root = Path(__file__).resolve().parents[1]
    policy, _ = load_jan_policy(repo_root=repo_root)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    bundle = collect_context_bundle(
        raw_notes="Mamy gotowy opis PR.",
        github_pr=123,
        repo_root=repo_root,
        policy=policy,
    )

    assert bundle.pull_requests == []
    assert any("GITHUB_TOKEN" in warning for warning in bundle.warnings)


def test_collect_context_bundle_without_git_range_skips_repo_context():
    repo_root = Path(__file__).resolve().parents[1]
    policy, _ = load_jan_policy(repo_root=repo_root)

    bundle = collect_context_bundle(
        raw_notes="Mamy gotowy opis PR.",
        repo_root=repo_root,
        policy=policy,
    )

    assert bundle.repo is None


def test_build_validator_report_flags_new_identifier():
    repo_root = Path(__file__).resolve().parents[1]
    policy, _ = load_jan_policy(repo_root=repo_root)
    bundle = WorkflowContextBundle(
        raw_notes="JAN-101: dodaliśmy feature flag checkout_summary i testy smoke.",
        warnings=[],
    )

    final_text = (
        "Cel zmiany\n"
        "Dodanie JAN-101 oraz GA4 tracking.\n\n"
        "Zakres\n"
        "Wdrożenie obejmuje checkout_summary.\n\n"
        "Testy\n"
        "Smoke testy wykonane.\n\n"
        "Ryzyka\n"
        "Brak."
    )
    report = build_validator_report(
        final_text,
        workflow_name="write_pr_description",
        audience="reviewer",
        bundle=bundle,
        policy=policy,
    )
    assert report["no_new_facts"]["passed"] is False
    assert "GA4" in report["no_new_facts"]["new_identifiers"]


def test_execute_repo_native_workflow_final_returns_sectioned_text(monkeypatch):
    repo_root = Path(__file__).resolve().parents[1]
    policy, _ = load_jan_policy(repo_root=repo_root)
    monkeypatch.setattr(
        "jan.workflow_engine.collect_context_bundle",
        lambda **kwargs: make_bundle(),
    )

    client = FakeClient(
        "Cel zmiany\nDodanie feature flag checkout_summary.\n\n"
        "Zakres\nPanel checkout pokazuje podsumowanie koszyka.\n\n"
        "Testy\nWykonano smoke testy checkout.\n\n"
        "Ryzyka\nRyzyko ogranicza się do flagi feature."
    )

    result = execute_repo_native_workflow(
        "write_pr_description",
        raw_notes="dummy",
        audience="reviewer",
        response_mode="final",
        repo_root=repo_root,
        policy=policy,
        model_client=client,
    )

    assert "Cel zmiany" in result
    assert "Zakres" in result
    assert "Ryzyka" in result


def test_normalize_structured_final_text_drops_extra_sections():
    repo_root = Path(__file__).resolve().parents[1]
    policy, _ = load_jan_policy(repo_root=repo_root)
    raw_output = (
        "### Cel zmiany\nDodanie feature flag checkout_summary.\n\n"
        "### Zakres\nPanel checkout pokazuje podsumowanie koszyka.\n\n"
        "### Testy\nWykonano smoke testy checkout.\n\n"
        "### Ryzyka\nRyzyko ogranicza się do flagi feature.\n\n"
        "### Notatki dla reviewera\nSprawdź konfigurację alertu."
    )

    normalized = normalize_structured_final_text(raw_output, "pr_description", policy)

    assert "Notatki dla reviewera" not in normalized
    assert normalized.count("### ") == 4


def test_execute_repo_native_workflow_review_returns_json(monkeypatch):
    repo_root = Path(__file__).resolve().parents[1]
    policy, _ = load_jan_policy(repo_root=repo_root)
    monkeypatch.setattr(
        "jan.workflow_engine.collect_context_bundle",
        lambda **kwargs: WorkflowContextBundle(
            raw_notes="JAN-101: rollout note dla feature flag checkout_summary.",
            warnings=["Brak GitHub PR; używam tylko raw notes."],
        ),
    )

    client = FakeClient(
        json.dumps(
            {
                "final_text": (
                    "Zakres rolloutu\nCheckout summary idzie za feature flagą.\n\n"
                    "Monitoring\nObserwujemy Sentry i dashboard checkout.\n\n"
                    "Ryzyka\nRyzyko dotyczy tylko ścieżki z aktywną flagą.\n\n"
                    "Plan wycofania\nWyłączamy feature flagę."
                ),
                "source_trace": [
                    {
                        "segment": "Checkout summary idzie za feature flagą.",
                        "source_ids": ["raw:notes"],
                        "note": "Pochodzi z notatki wejściowej.",
                    }
                ],
            }
        )
    )

    result = execute_repo_native_workflow(
        "write_rollout_note",
        raw_notes="dummy",
        audience="internal",
        response_mode="review",
        repo_root=repo_root,
        policy=policy,
        model_client=client,
    )
    payload = json.loads(result)

    assert payload["final_text"].startswith("Zakres rolloutu")
    assert payload["source_trace"][0]["source_ids"] == ["raw:notes"]
    assert "validator_report" in payload
    assert payload["warnings"] == ["Brak GitHub PR; używam tylko raw notes."]


def test_public_workflow_wrapper_uses_repo_native_engine(monkeypatch):
    monkeypatch.setattr("jan.jan_subagent_opencode.bielik.is_ready", lambda: True)
    monkeypatch.setattr(
        "jan.jan_subagent_opencode.execute_repo_native_workflow",
        lambda *args, **kwargs: "Cel zmiany\nOpis gotowy.",
    )

    result = write_pr_description(raw_notes="Dodaliśmy testy.", audience="reviewer")
    assert result == "Cel zmiany\nOpis gotowy."
