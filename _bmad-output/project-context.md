# Project Context: Jan v3.0.0 Pivot

## Source of truth

Ten dokument jest trwałym technical memory dla pivotu Jana do repo-native agenta dla tech teamów.
BMAD pozostaje source-of-truth dla procesu, a BMADX jedynie dokłada scaffold bundle i verify discipline.

## Product category

Jan v3.0.0:

- nie jest już pozycjonowany jako ogólny korektor polszczyzny
- jest repo-native agentem MCP do polskojęzycznej komunikacji zmian w software delivery

## Core workflows

- `write_pr_description`
- `compose_release_notes`
- `rewrite_issue`
- `write_rollout_note`

## Supporting layers

- `jan.yml` jako memory-as-code
- source adapters: local git, GitHub, Jira
- trust layer
- benchmark v2 na lane’ach `text_only`, `structured_context`, `policy_pack`

## Compatibility

- legacy tools zostają callable w `v3.0.0`
- są deprecated
- nie są głównym onboardingiem

## Brand rule

- Jan Kochanowski zostaje jako brand skin, tone i easter egg
- persona nie wraca do domyślnego outputu workflowów produkcyjnych

## Verify rule

Done oznacza:

- workflow działa
- trust layer działa
- benchmark v1 nadal przechodzi jako guardrail
- benchmark v2 ma działający harness
- docs, migration note i rollout artifacts są zsynchronizowane
