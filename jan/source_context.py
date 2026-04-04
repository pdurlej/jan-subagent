"""
Modele kontekstu źródłowego dla repo-native workflowów Jana.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SourceItem(BaseModel):
    source_id: str
    source_type: str
    title: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class RepoContext(BaseModel):
    root_path: str
    branch: str = ""
    git_range: str | None = None
    changed_files: list[str] = Field(default_factory=list)
    commits: list[str] = Field(default_factory=list)
    diff_excerpt: str = ""
    source_items: list[SourceItem] = Field(default_factory=list)


class PullRequestContext(BaseModel):
    number: int
    title: str
    body: str = ""
    labels: list[str] = Field(default_factory=list)
    changed_files: list[str] = Field(default_factory=list)
    url: str | None = None
    source_items: list[SourceItem] = Field(default_factory=list)


class IssueContext(BaseModel):
    provider: str
    key: str
    title: str
    description: str = ""
    acceptance_criteria: list[str] = Field(default_factory=list)
    status: str = ""
    url: str | None = None
    source_items: list[SourceItem] = Field(default_factory=list)


class ReleaseBundleContext(BaseModel):
    title: str = ""
    source_items: list[SourceItem] = Field(default_factory=list)


class WorkflowContextBundle(BaseModel):
    repo: RepoContext | None = None
    pull_requests: list[PullRequestContext] = Field(default_factory=list)
    issues: list[IssueContext] = Field(default_factory=list)
    release_bundle: ReleaseBundleContext | None = None
    raw_notes: str = ""
    warnings: list[str] = Field(default_factory=list)

    def all_source_items(self) -> list[SourceItem]:
        items: list[SourceItem] = []
        if self.raw_notes.strip():
            items.append(
                SourceItem(
                    source_id="raw:notes",
                    source_type="raw_notes",
                    title="Raw notes",
                    content=self.raw_notes.strip(),
                )
            )
        if self.repo is not None:
            items.extend(self.repo.source_items)
        for pr in self.pull_requests:
            items.extend(pr.source_items)
        for issue in self.issues:
            items.extend(issue.source_items)
        if self.release_bundle is not None:
            items.extend(self.release_bundle.source_items)
        return items

    def has_any_context(self) -> bool:
        return bool(self.raw_notes.strip() or self.all_source_items())
