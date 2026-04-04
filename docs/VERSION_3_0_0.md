# Wersja v3.0.0 - Repo-Native Pivot

## Najważniejsze zmiany

- Jan zmienia kategorię produktu: z ogólnego korektora polszczyzny na repo-native agenta MCP dla tech teamów.
- Główny surface MCP to teraz named workflows:
  - `write_pr_description`
  - `compose_release_notes`
  - `rewrite_issue`
  - `write_rollout_note`
- `jan.yml` wchodzi jako memory-as-code dla glossary, templates, audience packs i validation policy.
- Local git, GitHub i Jira stają się first-class źródłami kontekstu.
- `response_mode="review"` dodaje JSON z `final_text`, `source_trace` i `validator_report`.
- Stare tools korektorskie zostają jako `legacy`, ale znikają z głównego onboardingu.

## Zmiana kategorii produktu

Jan v3.0.0 nie jest pozycjonowany jako „MCP server do korekty polszczyzny”.
Nowa pozycja produktu to:

repo-native agent do polskojęzycznej komunikacji zmian w software delivery.

Core use-case'y:

- PR descriptions
- release notes / changelog
- issue rewrite
- rollout notes

## Nowe warstwy techniczne

- `jan.policy`
- `jan.source_context`
- `jan.source_adapters`
- `jan.workflow_engine`
- `jan.delivery_benchmark`

## Trust layer

Każdy nowy workflow może przejść przez:

- fact preservation
- `no_new_facts`
- template compliance
- glossary adherence
- audience-policy compliance

W `review` to jest zwracane wprost. W `final` workflow zwraca tylko paste-ready tekst.

## Benchmarki

- benchmark v1 workplace writing zostaje jako regression guardrail
- benchmark v2 delivery workflows wchodzi jako north-star harness dla nowej niszy

## BMAD / BMADX

Pivot v3 ma formalne artefakty:

- `project-context.md`
- PRD
- architekturę
- bundle `X4/FUBAR`

## Uwaga o personie

Jan Kochanowski zostaje jako warstwa marki i easter egg.
Nie wraca do domyślnego outputu workflowów produkcyjnych.
