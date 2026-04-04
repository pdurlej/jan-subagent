# Benchmark Methodology

Repo używa teraz dwóch benchmarków o różnych rolach.

## Benchmark v1: workplace writing regression

To historyczny pilot, który pomógł znaleźć problem wrappera Jana i sprawdzić, czy produkt wraca do verbose UX.

Rola:

- regression guardrail
- kontrola `paste-ready` outputu
- porównanie literalnego wyniku produktu z dawnym baseline’em

Zakres:

- `PR description`
- `ticket/issue`
- `support reply`
- `release note/changelog`
- `status email/notatka`

Dokument wyników:

- [docs/benchmarks/workplace-writing-pilot.md](/Users/pd/Developer/jan/docs/benchmarks/workplace-writing-pilot.md)

## Benchmark v2: repo-native delivery workflows

To nowy north-star benchmark dla `v3.0.0`.

Rola:

- mierzyć przewagę workflowu i policy packa, nie tylko modelu
- sprawdzać, czy Jan wygrywa jako narzędzie codziennej pracy w software delivery
- oceniać wpływ source context i `jan.yml`

Zakres:

- `write_pr_description`
- `compose_release_notes`
- `rewrite_issue`
- `write_rollout_note`

Oś benchmarku:

- `artifact`
- `context richness`
- `audience`

Lane’y:

- `text_only`
- `structured_context`
- `policy_pack`

Dataset:

- [benchmarks/delivery_workflows_v2.jsonl](/Users/pd/Developer/jan/benchmarks/delivery_workflows_v2.jsonl)

Harness:

- [jan/delivery_benchmark.py](/Users/pd/Developer/jan/jan/delivery_benchmark.py)
- [scripts/test_delivery_benchmark.py](/Users/pd/Developer/jan/scripts/test_delivery_benchmark.py)
- [scripts/run_delivery_benchmark.py](/Users/pd/Developer/jan/scripts/run_delivery_benchmark.py)

## KPI dla benchmarku v2

- zero/one-edit acceptance rate
- fact preservation
- `no_new_facts`
- template compliance
- glossary adherence
- time-to-paste
- p95 latency
- escalation rate do manual/GPT

Targety startowe:

- PR zero/one-edit acceptance `>=70%`
- release notes zero/one-edit acceptance `>=60%`
- fact preservation `>=99%`
- `no_new_facts` `<2%`
- template/glossary compliance `>=95%`
- repo-aware jobs p95 `<5s`

## Fairness rules

- workflowy są oceniane literalnie jako produkt
- brakujące tokeny GitHub/Jira nie tworzą synthetic contextu
- benchmark v2 ma pokazać, czy Jan zyskuje disproporcjonalnie dużo na lane `structured_context` i `policy_pack`
- jeśli zysk nie rośnie wraz z kontekstem i policy packiem, moat produktu nie jest jeszcze zbudowany

## Commands

Regression guardrail:

```bash
.venv/bin/python scripts/test_benchmark_harness.py
```

Delivery benchmark v2, CI-safe:

```bash
.venv/bin/python scripts/test_delivery_benchmark.py
```

Delivery benchmark v2, live:

```bash
.venv/bin/python scripts/run_delivery_benchmark.py --systems Jan raw-bielik gpt-5.4
```
