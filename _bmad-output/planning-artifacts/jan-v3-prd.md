# Jan v3.0.0 PRD

## Product decision

Jan przestaje być pozycjonowany jako ogólny korektor polszczyzny.
Jan v3.0.0 staje się repo-native agentem MCP do polskojęzycznej komunikacji zmian w software delivery.

## Primary audience

- tech leads
- senior engineers
- engineering managers
- release owners

Wszyscy pracują w MCP-enabled workflow i regularnie piszą artefakty typu PR description, release notes, changelog, rollout note i issue rewrite.

## Core jobs-to-be-done

1. Z diffa, PR-a, commitów i notatek zrobić reviewer-ready opis PR po polsku.
2. Z wielu zmian i ticketów zrobić release notes albo changelog dla audience internal/customer.
3. Z chaotycznej notatki i zgłoszeń zrobić ticket gotowy dla zespołu.
4. Z notatek rolloutowych, issue i zmian w repo zrobić krótką operacyjną notatkę rolloutową.

## Product wedge

- repo-native workflows zamiast ogólnych promptów
- policy pack `jan.yml`
- source context z local git, GitHub i Jira
- trust layer: fact preservation, no-new-facts, template compliance, glossary adherence
- review mode z traceability

## Non-goals for v3.0.0

- parity z GPT-5.4 w ogólnym workplace writing
- support replies jako core use case
- status emails jako core use case
- tryb nauki polskiego
- persona Jana w domyślnym outputcie produkcyjnym

## Public product shape

Primary workflows:

- `write_pr_description`
- `compose_release_notes`
- `rewrite_issue`
- `write_rollout_note`

Legacy compatibility:

- `correct_orthography`
- `correct_punctuation`
- `verify_grammar`
- `improve_style`
- `comprehensive_correction`

Te tools zostają callable, ale są deprecated i nie są głównym onboardingiem.

## Success metrics

- PR zero/one-edit acceptance `>=70%`
- release notes zero/one-edit acceptance `>=60%`
- fact preservation `>=99%`
- no-new-facts `<2%`
- template compliance `>=95%`
- repo-aware p95 `<5s`

## Risks

- zbyt szeroki surface MCP utrudni onboarding
- brak tokenów GitHub/Jira może dawać myląco ubogi kontekst
- heurystyczny trust layer może być zbyt surowy albo zbyt miękki
- persona może dalej przeciekać do produkcyjnego UX, jeśli prompt contracts się rozjadą
