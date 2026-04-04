"""
Adaptery źródeł kontekstu dla repo-native workflowów Jana.
"""

from __future__ import annotations

import base64
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any
from urllib import error as urlerror
from urllib import parse as urlparse
from urllib import request as urlrequest

from .policy import JanPolicy, detect_repo_root
from .source_context import (
    IssueContext,
    PullRequestContext,
    ReleaseBundleContext,
    RepoContext,
    SourceItem,
)


def _truncate(text: str, limit: int = 4000) -> str:
    stripped = text.strip()
    if len(stripped) <= limit:
        return stripped
    return stripped[: limit - 3].rstrip() + "..."


def run_git_command(args: list[str], cwd: Path | None = None) -> str:
    try:
        output = subprocess.check_output(
            ["git", *args],
            cwd=str(cwd or detect_repo_root()),
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""
    return output.strip()


def detect_github_repository(cwd: Path | None = None, policy: JanPolicy | None = None) -> str | None:
    if policy and policy.github.repository:
        return policy.github.repository

    env_repo = os.getenv("GITHUB_REPOSITORY")
    if env_repo:
        return env_repo

    remote = run_git_command(["remote", "get-url", "origin"], cwd=cwd)
    if not remote:
        return None

    match = re.search(r"github\.com[:/](?P<repo>[^/]+/[^/.]+)(?:\.git)?$", remote)
    if match:
        return match.group("repo")
    return None


def collect_repo_context(
    git_range: str | None = None,
    cwd: Path | None = None,
    diff_char_limit: int = 5000,
) -> RepoContext | None:
    repo_root = detect_repo_root(cwd)
    branch = run_git_command(["rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_root)
    if not branch:
        return None

    effective_range = git_range
    changed_files_output = ""
    commit_output = ""
    diff_excerpt = ""

    if effective_range:
        changed_files_output = run_git_command(["diff", "--name-only", effective_range], cwd=repo_root)
        commit_output = run_git_command(
            ["log", "--oneline", "--decorate", effective_range],
            cwd=repo_root,
        )
        diff_excerpt = run_git_command(
            ["diff", "--unified=0", effective_range],
            cwd=repo_root,
        )
    else:
        changed_files_output = run_git_command(["diff", "--name-only", "HEAD"], cwd=repo_root)
        if not changed_files_output:
            changed_files_output = run_git_command(
                ["show", "--pretty=format:", "--name-only", "HEAD"],
                cwd=repo_root,
            )
        commit_output = run_git_command(["log", "--oneline", "--decorate", "-5"], cwd=repo_root)
        diff_excerpt = run_git_command(["diff", "--unified=0", "HEAD"], cwd=repo_root)
        if not diff_excerpt:
            diff_excerpt = run_git_command(["show", "--stat", "--oneline", "HEAD"], cwd=repo_root)

    changed_files = [line.strip() for line in changed_files_output.splitlines() if line.strip()]
    commits = [line.strip() for line in commit_output.splitlines() if line.strip()]
    diff_excerpt = _truncate(diff_excerpt, diff_char_limit)

    source_items = [
        SourceItem(
            source_id="git:branch",
            source_type="git_branch",
            title="Aktualna gałąź",
            content=branch,
        ),
    ]
    if changed_files:
        source_items.append(
            SourceItem(
                source_id=f"git:files:{effective_range or 'head'}",
                source_type="git_changed_files",
                title="Zmienione pliki",
                content="\n".join(changed_files),
                metadata={"files": changed_files},
            )
        )
    if commits:
        source_items.append(
            SourceItem(
                source_id=f"git:commits:{effective_range or 'head'}",
                source_type="git_commits",
                title="Ostatnie commity",
                content="\n".join(commits),
                metadata={"commits": commits},
            )
        )
    if diff_excerpt:
        source_items.append(
            SourceItem(
                source_id=f"git:diff:{effective_range or 'head'}",
                source_type="git_diff",
                title="Wyciąg diffa",
                content=diff_excerpt,
            )
        )

    return RepoContext(
        root_path=str(repo_root),
        branch=branch,
        git_range=effective_range,
        changed_files=changed_files,
        commits=commits,
        diff_excerpt=diff_excerpt,
        source_items=source_items,
    )


def _http_json(
    url: str,
    headers: dict[str, str],
) -> Any:
    request = urlrequest.Request(url, headers=headers)
    with urlrequest.urlopen(request, timeout=20) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def _github_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "jan-subagent/3.0.0",
    }


def collect_github_pr_context(
    number: int,
    policy: JanPolicy,
    cwd: Path | None = None,
) -> tuple[PullRequestContext | None, list[str]]:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return None, [f"Brak GITHUB_TOKEN; pomijam kontekst GitHub PR #{number}."]

    repository = detect_github_repository(cwd=cwd, policy=policy)
    if not repository:
        return None, [f"Nie udało się ustalić repozytorium GitHub dla PR #{number}."]

    base = policy.github.api_base.rstrip("/")
    headers = _github_headers(token)
    warnings: list[str] = []

    try:
        pr_data = _http_json(f"{base}/repos/{repository}/pulls/{number}", headers)
        files: list[str] = []
        page = 1
        while True:
            page_data = _http_json(
                f"{base}/repos/{repository}/pulls/{number}/files?per_page=100&page={page}",
                headers,
            )
            if not page_data:
                break
            files.extend(item["filename"] for item in page_data if item.get("filename"))
            if len(page_data) < 100:
                break
            page += 1
    except (urlerror.URLError, json.JSONDecodeError, KeyError) as exc:
        return None, [f"Nie udało się pobrać GitHub PR #{number}: {exc}"]

    labels = [label["name"] for label in pr_data.get("labels", []) if label.get("name")]
    title = pr_data.get("title", f"PR #{number}")
    body = pr_data.get("body") or ""
    url = pr_data.get("html_url")
    source_items = [
        SourceItem(
            source_id=f"github:pr:{number}:title",
            source_type="github_pr_title",
            title=f"GitHub PR #{number} - tytuł",
            content=title,
            metadata={"url": url},
        ),
    ]
    if body.strip():
        source_items.append(
            SourceItem(
                source_id=f"github:pr:{number}:body",
                source_type="github_pr_body",
                title=f"GitHub PR #{number} - opis",
                content=_truncate(body),
                metadata={"url": url},
            )
        )
    if files:
        source_items.append(
            SourceItem(
                source_id=f"github:pr:{number}:files",
                source_type="github_pr_files",
                title=f"GitHub PR #{number} - pliki",
                content="\n".join(files),
                metadata={"url": url, "files": files},
            )
        )
    if labels:
        source_items.append(
            SourceItem(
                source_id=f"github:pr:{number}:labels",
                source_type="github_pr_labels",
                title=f"GitHub PR #{number} - etykiety",
                content=", ".join(labels),
                metadata={"labels": labels},
            )
        )

    return (
        PullRequestContext(
            number=number,
            title=title,
            body=body,
            labels=labels,
            changed_files=files,
            url=url,
            source_items=source_items,
        ),
        warnings,
    )


def collect_github_issue_context(
    number: int,
    policy: JanPolicy,
    cwd: Path | None = None,
) -> tuple[IssueContext | None, list[str]]:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return None, [f"Brak GITHUB_TOKEN; pomijam kontekst GitHub issue #{number}."]

    repository = detect_github_repository(cwd=cwd, policy=policy)
    if not repository:
        return None, [f"Nie udało się ustalić repozytorium GitHub dla issue #{number}."]

    base = policy.github.api_base.rstrip("/")
    headers = _github_headers(token)
    try:
        issue_data = _http_json(f"{base}/repos/{repository}/issues/{number}", headers)
    except (urlerror.URLError, json.JSONDecodeError, KeyError) as exc:
        return None, [f"Nie udało się pobrać GitHub issue #{number}: {exc}"]

    title = issue_data.get("title", f"Issue #{number}")
    body = issue_data.get("body") or ""
    url = issue_data.get("html_url")
    labels = [label["name"] for label in issue_data.get("labels", []) if label.get("name")]
    source_items = [
        SourceItem(
            source_id=f"github:issue:{number}:title",
            source_type="github_issue_title",
            title=f"GitHub issue #{number} - tytuł",
            content=title,
            metadata={"url": url},
        )
    ]
    if body.strip():
        source_items.append(
            SourceItem(
                source_id=f"github:issue:{number}:body",
                source_type="github_issue_body",
                title=f"GitHub issue #{number} - opis",
                content=_truncate(body),
                metadata={"url": url},
            )
        )
    if labels:
        source_items.append(
            SourceItem(
                source_id=f"github:issue:{number}:labels",
                source_type="github_issue_labels",
                title=f"GitHub issue #{number} - etykiety",
                content=", ".join(labels),
                metadata={"labels": labels},
            )
        )

    return (
        IssueContext(
            provider="github",
            key=f"#{number}",
            title=title,
            description=body,
            acceptance_criteria=[],
            status=issue_data.get("state") or "",
            url=url,
            source_items=source_items,
        ),
        [],
    )


def _extract_jira_text(payload: Any) -> str:
    if isinstance(payload, str):
        return payload
    if isinstance(payload, list):
        return "\n".join(filter(None, (_extract_jira_text(item) for item in payload))).strip()
    if not isinstance(payload, dict):
        return ""

    if payload.get("type") == "text":
        return payload.get("text", "")

    content = payload.get("content")
    if isinstance(content, list):
        pieces = [_extract_jira_text(item) for item in content]
        joined = "\n".join(piece for piece in pieces if piece)
        return joined.strip()
    return ""


def _extract_acceptance_criteria(text: str) -> list[str]:
    criteria: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"^(?:[-*]|\d+\.)\s+", stripped):
            criteria.append(re.sub(r"^(?:[-*]|\d+\.)\s+", "", stripped))
    return criteria


def collect_jira_issue_context(
    key: str,
    policy: JanPolicy,
) -> tuple[IssueContext | None, list[str]]:
    base_url = os.getenv("JIRA_BASE_URL") or (policy.jira.base_url or "")
    email = os.getenv("JIRA_EMAIL")
    token = os.getenv("JIRA_API_TOKEN")

    if not (base_url and email and token):
        return None, [f"Brak kompletu danych JIRA dla zgłoszenia {key}; pomijam kontekst Jira."]

    encoded_credentials = base64.b64encode(f"{email}:{token}".encode("utf-8")).decode("ascii")
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Accept": "application/json",
        "User-Agent": "jan-subagent/3.0.0",
    }
    issue_url = f"{base_url.rstrip('/')}/rest/api/3/issue/{urlparse.quote(key)}"

    try:
        issue_data = _http_json(issue_url, headers)
    except (urlerror.URLError, json.JSONDecodeError, KeyError) as exc:
        return None, [f"Nie udało się pobrać Jira issue {key}: {exc}"]

    fields = issue_data.get("fields", {})
    description = _extract_jira_text(fields.get("description"))
    acceptance_criteria = _extract_acceptance_criteria(description)
    status = ((fields.get("status") or {}).get("name")) or ""
    title = fields.get("summary") or key
    url = f"{base_url.rstrip('/')}/browse/{key}"

    source_items = [
        SourceItem(
            source_id=f"jira:{key}:summary",
            source_type="jira_issue_summary",
            title=f"Jira {key} - summary",
            content=title,
            metadata={"url": url},
        )
    ]
    if description:
        source_items.append(
            SourceItem(
                source_id=f"jira:{key}:description",
                source_type="jira_issue_description",
                title=f"Jira {key} - description",
                content=_truncate(description),
                metadata={"url": url},
            )
        )
    if acceptance_criteria:
        source_items.append(
            SourceItem(
                source_id=f"jira:{key}:acceptance",
                source_type="jira_issue_acceptance_criteria",
                title=f"Jira {key} - acceptance criteria",
                content="\n".join(acceptance_criteria),
                metadata={"url": url, "acceptance_criteria": acceptance_criteria},
            )
        )

    return (
        IssueContext(
            provider="jira",
            key=key,
            title=title,
            description=description,
            acceptance_criteria=acceptance_criteria,
            status=status,
            url=url,
            source_items=source_items,
        ),
        [],
    )


def build_release_bundle_context(
    pull_requests: list[PullRequestContext],
    issues: list[IssueContext],
) -> ReleaseBundleContext | None:
    if not pull_requests and not issues:
        return None

    lines: list[str] = []
    for pr in pull_requests:
        lines.append(f"PR #{pr.number}: {pr.title}")
    for issue in issues:
        lines.append(f"{issue.provider.upper()} {issue.key}: {issue.title}")

    return ReleaseBundleContext(
        title="Bundle release context",
        source_items=[
            SourceItem(
                source_id="bundle:release",
                source_type="release_bundle",
                title="Zebrane źródła release bundle",
                content="\n".join(lines),
            )
        ],
    )
