"""
Silnik repo-native workflowów Jana dla tech teamów.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from .api_client import BielikClient, bielik
from .output_utils import extract_json_payload
from .policy import JanPolicy, detect_repo_root, load_jan_policy
from .source_adapters import (
    build_release_bundle_context,
    collect_github_issue_context,
    collect_github_pr_context,
    collect_jira_issue_context,
    collect_repo_context,
)
from .source_context import WorkflowContextBundle
from .system_prompts import get_repo_native_system_prompt

SUPPORTED_AUDIENCES = ("reviewer", "internal", "customer", "exec")
SUPPORTED_RESPONSE_MODES = ("final", "review")

WORKFLOW_DEFINITIONS: dict[str, dict[str, str]] = {
    "write_pr_description": {
        "artifact_key": "pr_description",
        "summary": "Przygotuj opis PR dla reviewerów technicznych.",
    },
    "compose_release_notes": {
        "artifact_key": "release_notes",
        "summary": "Przygotuj release notes lub changelog dla wybranego audience.",
    },
    "rewrite_issue": {
        "artifact_key": "issue",
        "summary": "Przepisz notatki na czytelny ticket dla zespołu.",
    },
    "write_rollout_note": {
        "artifact_key": "rollout_note",
        "summary": "Przygotuj notatkę rolloutową dla zespołu dostarczającego zmianę.",
    },
}

IDENTIFIER_PATTERNS = (
    r"\b[A-Z][A-Z0-9]+-\d+\b",
    r"\b[A-Z]{2,}\d+(?:[A-Z0-9_-]*)\b",
    r"#\d+\b",
    r"\bv?\d+\.\d+(?:\.\d+)?\b",
    r"https?://\S+",
    r"`[^`]+`",
)


class WorkflowSourceTraceEntry(BaseModel):
    segment: str
    source_ids: list[str] = Field(default_factory=list)
    note: str = ""


class WorkflowReviewEnvelope(BaseModel):
    final_text: str
    source_trace: list[WorkflowSourceTraceEntry] = Field(default_factory=list)
    validator_report: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    workflow: str = ""
    audience: str = ""


def normalize_int_list(values: list[int] | None) -> list[int]:
    return [int(value) for value in values or []]


def normalize_string_list(values: list[str] | None) -> list[str]:
    return [value.strip() for value in values or [] if value and value.strip()]


def collect_context_bundle(
    *,
    raw_notes: str = "",
    git_range: str | None = None,
    github_pr: int | None = None,
    github_prs: list[int] | None = None,
    github_issue: int | None = None,
    jira_key: str | None = None,
    jira_keys: list[str] | None = None,
    repo_root: Path | None = None,
    policy: JanPolicy,
) -> WorkflowContextBundle:
    warnings: list[str] = []
    pull_requests = []
    issues = []
    root = detect_repo_root(repo_root)

    repo_context = collect_repo_context(git_range=git_range, cwd=root) if git_range else None

    github_pr_numbers = normalize_int_list(github_prs)
    if github_pr is not None:
        github_pr_numbers.insert(0, int(github_pr))

    seen_prs: set[int] = set()
    for number in github_pr_numbers:
        if number in seen_prs:
            continue
        seen_prs.add(number)
        pr_context, pr_warnings = collect_github_pr_context(number, policy=policy, cwd=root)
        warnings.extend(pr_warnings)
        if pr_context is not None:
            pull_requests.append(pr_context)

    github_issue_number = int(github_issue) if github_issue is not None else None
    if github_issue_number is not None:
        issue_context, issue_warnings = collect_github_issue_context(
            github_issue_number,
            policy=policy,
            cwd=root,
        )
        warnings.extend(issue_warnings)
        if issue_context is not None:
            issues.append(issue_context)

    jira_issue_keys = normalize_string_list(jira_keys)
    if jira_key:
        jira_issue_keys.insert(0, jira_key.strip())

    seen_jira: set[str] = set()
    for key in jira_issue_keys:
        if key in seen_jira:
            continue
        seen_jira.add(key)
        jira_context, jira_warnings = collect_jira_issue_context(key, policy=policy)
        warnings.extend(jira_warnings)
        if jira_context is not None:
            issues.append(jira_context)

    release_bundle = build_release_bundle_context(pull_requests, issues)

    return WorkflowContextBundle(
        repo=repo_context,
        pull_requests=pull_requests,
        issues=issues,
        release_bundle=release_bundle,
        raw_notes=raw_notes.strip(),
        warnings=warnings,
    )


def serialize_context_bundle(bundle: WorkflowContextBundle) -> str:
    parts: list[str] = []
    if bundle.raw_notes.strip():
        parts.append(f"## Raw notes\n{bundle.raw_notes.strip()}")

    if bundle.repo is not None:
        repo_lines = [
            f"Repo root: {bundle.repo.root_path}",
            f"Branch: {bundle.repo.branch}",
        ]
        if bundle.repo.git_range:
            repo_lines.append(f"Git range: {bundle.repo.git_range}")
        if bundle.repo.changed_files:
            repo_lines.append("Changed files:")
            repo_lines.extend(f"- {path}" for path in bundle.repo.changed_files)
        if bundle.repo.commits:
            repo_lines.append("Recent commits:")
            repo_lines.extend(f"- {line}" for line in bundle.repo.commits)
        if bundle.repo.diff_excerpt:
            repo_lines.append("Diff excerpt:")
            repo_lines.append(bundle.repo.diff_excerpt)
        parts.append("## Repo context\n" + "\n".join(repo_lines))

    for pr in bundle.pull_requests:
        pr_lines = [f"PR #{pr.number}: {pr.title}"]
        if pr.labels:
            pr_lines.append("Labels: " + ", ".join(pr.labels))
        if pr.body.strip():
            pr_lines.append("Body:")
            pr_lines.append(pr.body.strip())
        if pr.changed_files:
            pr_lines.append("Files:")
            pr_lines.extend(f"- {path}" for path in pr.changed_files)
        parts.append("## GitHub PR context\n" + "\n".join(pr_lines))

    for issue in bundle.issues:
        issue_lines = [f"{issue.provider.upper()} {issue.key}: {issue.title}"]
        if issue.status:
            issue_lines.append("Status: " + issue.status)
        if issue.description.strip():
            issue_lines.append("Description:")
            issue_lines.append(issue.description.strip())
        if issue.acceptance_criteria:
            issue_lines.append("Acceptance criteria:")
            issue_lines.extend(f"- {item}" for item in issue.acceptance_criteria)
        parts.append("## Issue context\n" + "\n".join(issue_lines))

    if bundle.warnings:
        parts.append("## Warnings\n" + "\n".join(f"- {warning}" for warning in bundle.warnings))

    return "\n\n".join(part for part in parts if part).strip()


def extract_identifiers(text: str, policy: JanPolicy | None = None) -> set[str]:
    identifiers: set[str] = set()
    for pattern in IDENTIFIER_PATTERNS:
        identifiers.update(match.strip("`") for match in re.findall(pattern, text))
    if policy is not None:
        lower_source = text.lower()
        for token in policy.do_not_translate:
            if re.search(rf"(?<!\w){re.escape(token.lower())}(?!\w)", lower_source):
                identifiers.add(token)
    return {item for item in identifiers if item}


def fallback_source_trace(bundle: WorkflowContextBundle, final_text: str) -> list[WorkflowSourceTraceEntry]:
    source_ids = [item.source_id for item in bundle.all_source_items()]
    if not source_ids:
        source_ids = ["raw:notes"] if bundle.raw_notes.strip() else []
    if not final_text.strip():
        return []
    return [
        WorkflowSourceTraceEntry(
            segment=final_text.strip(),
            source_ids=source_ids,
            note="Fallback trace: cały artefakt zmapowany do dostępnych źródeł.",
        )
    ]


def extract_workflow_final_text(raw_output: str) -> str:
    payload = extract_json_payload(raw_output) or {}
    if isinstance(payload, dict):
        candidate = payload.get("final_text")
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()

    stripped = raw_output.replace("\r\n", "\n").strip()
    labeled_fence_match = re.search(
        r"(?is)finalny tekst gotowy do wklejenia\s*:?\s*```(?:[\w+-]+)?\s*(.*?)\s*```",
        stripped,
    )
    if labeled_fence_match:
        return labeled_fence_match.group(1).strip()

    labeled_match = re.search(
        r"(?is)finalny tekst gotowy do wklejenia\s*:?\s*(.+)$",
        stripped,
    )
    if labeled_match:
        candidate = labeled_match.group(1).strip()
        if candidate:
            return candidate

    fence_match = re.fullmatch(r"```(?:[\w+-]+)?\s*(.*?)\s*```", stripped, flags=re.S)
    if fence_match:
        return fence_match.group(1).strip()

    quote_pairs = [('"', '"'), ("'", "'"), ("“", "”"), ("„", "”")]
    for left, right in quote_pairs:
        if stripped.startswith(left) and stripped.endswith(right):
            return stripped[len(left) : -len(right)].strip()

    return stripped


def normalize_structured_final_text(
    final_text: str,
    artifact_key: str,
    policy: JanPolicy,
) -> str:
    required_sections = policy.get_required_sections(artifact_key)
    if not required_sections:
        return final_text.strip()

    canonical_by_lower = {section.lower(): section for section in required_sections}
    section_content: dict[str, list[str]] = {}
    current_section: str | None = None

    for line in final_text.replace("\r\n", "\n").splitlines():
        matched_section = _match_canonical_section(line, canonical_by_lower)
        if matched_section is not None:
            current_section = matched_section
            section_content.setdefault(current_section, [])
            continue

        if re.match(r"^\s*#+\s+.+$", line) or re.match(r"^\s*\*\*.+\*\*\s*$", line):
            current_section = None
            continue

        if current_section is not None:
            section_content[current_section].append(line)

    if any(section not in section_content for section in required_sections):
        return final_text.strip()

    rebuilt_sections: list[str] = []
    for section in required_sections:
        content = "\n".join(section_content.get(section, [])).strip()
        if not content:
            return final_text.strip()
        rebuilt_sections.append(f"### {section}\n{content}")

    return "\n\n".join(rebuilt_sections).strip()


def parse_review_output(
    raw_output: str,
    bundle: WorkflowContextBundle,
) -> WorkflowReviewEnvelope:
    payload = extract_json_payload(raw_output) or {}
    final_text = ""
    if isinstance(payload, dict):
        candidate = payload.get("final_text")
        if isinstance(candidate, str):
            final_text = candidate.strip()

    if not final_text:
        final_text = extract_workflow_final_text(raw_output)

    trace_items: list[WorkflowSourceTraceEntry] = []
    source_trace = payload.get("source_trace") if isinstance(payload, dict) else None
    if isinstance(source_trace, list):
        for item in source_trace:
            if not isinstance(item, dict):
                continue
            segment = str(item.get("segment", "")).strip()
            source_ids = [str(value) for value in item.get("source_ids", []) if str(value).strip()]
            note = str(item.get("note", "")).strip()
            if segment:
                trace_items.append(
                    WorkflowSourceTraceEntry(segment=segment, source_ids=source_ids, note=note)
                )
    if not trace_items:
        trace_items = fallback_source_trace(bundle, final_text)

    return WorkflowReviewEnvelope(final_text=final_text, source_trace=trace_items)


def _match_canonical_section(line: str, canonical_by_lower: dict[str, str]) -> str | None:
    stripped = line.strip()
    candidates = []

    markdown_match = re.match(r"^\s*#+\s*(.+?)\s*:?\s*$", stripped)
    if markdown_match:
        candidates.append(markdown_match.group(1).strip())

    bold_match = re.match(r"^\s*\*\*(.+?)\*\*\s*$", stripped)
    if bold_match:
        candidates.append(bold_match.group(1).strip().rstrip(":").strip())

    candidates.append(stripped.rstrip(":").strip())

    for candidate in candidates:
        canonical = canonical_by_lower.get(candidate.lower())
        if canonical is not None:
            return canonical
    return None


def _contains_header(final_text: str, section: str) -> bool:
    canonical_by_lower = {section.lower(): section}
    return any(
        _match_canonical_section(line, canonical_by_lower) is not None
        for line in final_text.splitlines()
    )


def validate_fact_preservation(final_text: str, bundle: WorkflowContextBundle, policy: JanPolicy) -> dict[str, Any]:
    source_text = "\n".join(item.content for item in bundle.all_source_items())
    required = sorted(extract_identifiers(source_text, policy=policy))
    final_text_lower = final_text.lower()
    matched = [item for item in required if item.lower() in final_text_lower]
    missing = [item for item in required if item.lower() not in final_text_lower]
    return {
        "passed": not missing,
        "required_identifiers": required,
        "matched_identifiers": matched,
        "missing_identifiers": missing,
    }


def validate_no_new_facts(final_text: str, bundle: WorkflowContextBundle, policy: JanPolicy) -> dict[str, Any]:
    source_text = "\n".join(item.content for item in bundle.all_source_items())
    source_identifiers = extract_identifiers(source_text, policy=policy)
    output_identifiers = extract_identifiers(final_text, policy=policy)
    new_identifiers = sorted(item for item in output_identifiers if item not in source_identifiers)
    return {
        "passed": not new_identifiers,
        "new_identifiers": new_identifiers,
    }


def validate_template_compliance(
    final_text: str,
    artifact_key: str,
    policy: JanPolicy,
) -> dict[str, Any]:
    required_sections = policy.get_required_sections(artifact_key)
    missing_sections = [section for section in required_sections if not _contains_header(final_text, section)]
    return {
        "passed": not missing_sections,
        "required_sections": required_sections,
        "missing_sections": missing_sections,
    }


def validate_glossary_adherence(
    final_text: str,
    bundle: WorkflowContextBundle,
    policy: JanPolicy,
) -> dict[str, Any]:
    output_lower = final_text.lower()
    violations: list[dict[str, str]] = []
    missing_preserved_terms: list[str] = []
    source_text = "\n".join(item.content for item in bundle.all_source_items())
    source_lower = source_text.lower()

    for entry in policy.glossary:
        preferred_lower = entry.preferred.lower()
        aliases_in_output = [alias for alias in entry.aliases if alias.lower() in output_lower]
        if aliases_in_output and preferred_lower not in output_lower:
            violations.append(
                {
                    "preferred": entry.preferred,
                    "alias_used": aliases_in_output[0],
                }
            )

    for token in policy.do_not_translate:
        if re.search(rf"(?<!\w){re.escape(token.lower())}(?!\w)", source_lower) and not re.search(
            rf"(?<!\w){re.escape(token)}(?!\w)",
            final_text,
            flags=re.I,
        ):
            missing_preserved_terms.append(token)

    return {
        "passed": not violations and not missing_preserved_terms,
        "alias_violations": violations,
        "missing_do_not_translate": missing_preserved_terms,
    }


def validate_audience_policy(
    final_text: str,
    audience: str,
    policy: JanPolicy,
) -> dict[str, Any]:
    audience_pack = policy.get_audience(audience)
    output_lower = final_text.lower()
    found_banned = [
        term for term in audience_pack.banned_terms if term.lower() in output_lower
    ]
    global_banned = [
        term for term in policy.banned_phrases if term.lower() in output_lower
    ]
    return {
        "passed": not found_banned and not global_banned,
        "audience_banned_terms_found": found_banned,
        "global_banned_phrases_found": global_banned,
    }


def build_validator_report(
    final_text: str,
    workflow_name: str,
    audience: str,
    bundle: WorkflowContextBundle,
    policy: JanPolicy,
) -> dict[str, Any]:
    artifact_key = WORKFLOW_DEFINITIONS[workflow_name]["artifact_key"]
    report = {
        "fact_preservation": validate_fact_preservation(final_text, bundle, policy),
        "no_new_facts": validate_no_new_facts(final_text, bundle, policy),
        "template_compliance": validate_template_compliance(final_text, artifact_key, policy),
        "glossary_adherence": validate_glossary_adherence(final_text, bundle, policy),
        "audience_policy_compliance": validate_audience_policy(final_text, audience, policy),
        "warnings": bundle.warnings,
    }
    report["passed"] = all(
        item.get("passed", True)
        for key, item in report.items()
        if isinstance(item, dict) and key != "warnings"
    )
    return report


def execute_repo_native_workflow(
    workflow_name: str,
    *,
    raw_notes: str = "",
    git_range: str | None = None,
    github_pr: int | None = None,
    github_prs: list[int] | None = None,
    github_issue: int | None = None,
    jira_key: str | None = None,
    jira_keys: list[str] | None = None,
    audience: str = "internal",
    response_mode: str = "final",
    repo_root: Path | None = None,
    policy: JanPolicy | None = None,
    model_client: BielikClient | None = None,
    context_bundle_override: WorkflowContextBundle | None = None,
) -> str:
    if workflow_name not in WORKFLOW_DEFINITIONS:
        raise ValueError(f"Unsupported workflow: {workflow_name}")
    if audience not in SUPPORTED_AUDIENCES:
        raise ValueError(f"Unsupported audience: {audience}")
    if response_mode not in SUPPORTED_RESPONSE_MODES:
        raise ValueError(f"Unsupported response_mode: {response_mode}")

    root = detect_repo_root(repo_root)
    loaded_policy, _ = load_jan_policy(repo_root=root) if policy is None else (policy, root / "jan.yml")
    bundle = context_bundle_override or collect_context_bundle(
        raw_notes=raw_notes,
        git_range=git_range,
        github_pr=github_pr,
        github_prs=github_prs,
        github_issue=github_issue,
        jira_key=jira_key,
        jira_keys=jira_keys,
        repo_root=root,
        policy=loaded_policy,
    )

    if not bundle.has_any_context():
        return (
            "Brak kontekstu źródłowego. Podaj raw_notes albo wskaż git_range, PR, issue lub klucze Jira."
        )

    artifact_key = WORKFLOW_DEFINITIONS[workflow_name]["artifact_key"]
    system_prompt = get_repo_native_system_prompt(
        workflow_name=workflow_name,
        artifact_key=artifact_key,
        policy=loaded_policy,
        audience=audience,
        response_mode=response_mode,
    )
    user_message = (
        f"Workflow: {workflow_name}\n"
        f"Audience: {audience}\n"
        f"Task summary: {WORKFLOW_DEFINITIONS[workflow_name]['summary']}\n\n"
        f"{serialize_context_bundle(bundle)}"
    )

    client = model_client or bielik
    result = client.call(system_prompt, user_message, temperature=0.2)

    if response_mode == "review":
        review = parse_review_output(result, bundle)
        review.workflow = workflow_name
        review.audience = audience
        review.validator_report = build_validator_report(
            review.final_text,
            workflow_name,
            audience,
            bundle,
            loaded_policy,
        )
        review.warnings = bundle.warnings
        return json.dumps(review.model_dump(), indent=2, ensure_ascii=False)

    final_text = extract_workflow_final_text(result)
    if not final_text:
        review = parse_review_output(result, bundle)
        final_text = review.final_text
    final_text = normalize_structured_final_text(final_text, artifact_key, loaded_policy)
    return final_text
