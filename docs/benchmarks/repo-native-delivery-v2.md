# Repo-Native Delivery Benchmark v2

Ten dokument opisuje north-star benchmark dla Jana `v3.0.0`.

## Cel

Sprawdzić, czy Jan wygrywa jako repo-native narzędzie do polskojęzycznej komunikacji zmian, a nie jako ogólny assistant do pisania.

## Workflow coverage

- `write_pr_description`
- `compose_release_notes`
- `rewrite_issue`
- `write_rollout_note`

## Lane’y

- `text_only`
- `structured_context`
- `policy_pack`

## Czego oczekujemy od produktu

- wzrost jakości między `text_only` a `structured_context`
- dodatkowy wzrost jakości między `structured_context` a `policy_pack`
- brak cichego dopowiadania nowych faktów
- wysoka zgodność z template’em artefaktu
- wysoka zgodność z glossary i audience packiem

Jeśli Jan nie zyskuje wyraźnie na lane 2 i 3, to znaczy, że moat workflowowy jest jeszcze zbyt słaby.

## KPI

- zero/one-edit acceptance rate
- fact preservation
- `no_new_facts`
- template compliance
- glossary adherence
- time-to-paste
- p95 latency
- escalation rate do manual/GPT

## Artefakty

- dataset: [benchmarks/delivery_workflows_v2.jsonl](/Users/pd/Developer/jan/benchmarks/delivery_workflows_v2.jsonl)
- results: `_bmad-output/delivery-benchmarks/<timestamp>/`
- harness: [jan/delivery_benchmark.py](/Users/pd/Developer/jan/jan/delivery_benchmark.py)

## Status

- harness i CI-safe tests są zaimplementowane
- regression benchmark v1 nadal pozostaje guardrailem
- live results dla v2 powinny być dodawane jako osobne artefakty runów, nie jako ręcznie wpisane twierdzenia marketingowe
