# Workplace Writing Pilot

Ten dokument jest public-safe notatką dla pilota benchmarkowego Jana w workplace writing.
W `v3.0.0` ten benchmark nie jest już north-star kompasem roadmapy. Zostaje jako regression suite pilnujący, żeby Jan nie wrócił do verbose wrappera i nie stracił `paste-ready` UX.

## Status

- Harness benchmarkowy jest zaimplementowany w repo.
- Baseline przed refactorem: `20260404T012404Z`
- Rerun po refactorze paste-ready: `20260404T020037Z`
- Artefakty baseline: `/Users/pd/Developer/jan/_bmad-output/benchmarks/20260404T012404Z-workplace-writing-pilot`
- Artefakty rerunu: `/Users/pd/Developer/jan/_bmad-output/benchmarks/20260404T020037Z-workplace-writing-pilot`

## Current Leaderboard

### Primary Literal Score

| System | Final | Deterministic | Judge | Avg latency | Error rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| `GPT-5.4` | `96.5%` | `92.0%` | `100.0%` | `1.48s` | `0.0%` |
| `Jan` | `94.0%` | `88.9%` | `97.9%` | `2.58s` | `0.0%` |
| `raw Bielik` | `93.1%` | `88.3%` | `96.8%` | `3.24s` | `0.0%` |

### Normalized Diagnostic Score

| System | Final | Deterministic | Judge | Avg latency | Error rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| `GPT-5.4` | `96.5%` | `92.0%` | `100.0%` | `1.48s` | `0.0%` |
| `Jan` | `93.9%` | `88.9%` | `97.6%` | `2.58s` | `0.0%` |
| `raw Bielik` | `92.3%` | `88.3%` | `95.5%` | `3.24s` | `0.0%` |

Literal score pozostaje głównym KPI produktu. Normalized score jest tylko diagnostyką pokazującą koszt wrappera odpowiedzi.

## Jan Before vs After

### Overall

| Metric | Before | After | Delta |
| --- | ---: | ---: | ---: |
| Final score | `49.9%` | `94.0%` | `+44.1 pp` |
| Deterministic | `68.8%` | `88.9%` | `+20.1 pp` |
| Judge | `30.1%` | `97.9%` | `+67.8 pp` |
| Avg latency | `26.28s` | `2.58s` | `-23.70s` |
| Error rate | `0.0%` | `0.0%` | `0.0 pp` |

### By Intent

| Intent | Before | After | Delta |
| --- | ---: | ---: | ---: |
| `surface correction` | `63.2%` | `98.2%` | `+35.0 pp` |
| `style rewrite` | `45.3%` | `92.0%` | `+46.8 pp` |
| `full polish` | `41.4%` | `91.8%` | `+50.4 pp` |

### Surface Correction Quality

| Metric | Before | After literal | After normalized |
| --- | ---: | ---: | ---: |
| Concision | `20.0%` | `100.0%` | `100.0%` |
| Workplace usefulness | `20.0%` | `100.0%` | `100.0%` |

To jest najważniejszy sygnał po refactorze: literalny wynik Jana i wynik po technicznym odfiltrowaniu wrappera są praktycznie takie same, więc koszt persony został zepchnięty poza domyślny workplace UX.

## Product Interpretation

- W tym pilocie Jan przeszedł z narzędzia przegrywającego przez opakowanie odpowiedzi do bardzo mocnego, paste-ready produktu workplace writing.
- Jan nie wygrywa całego pilota z `GPT-5.4`, ale jest blisko lidera i wyprzedza `raw Bielik` w wyniku literalnym.
- Najmocniejszy sygnał produktowy to `release note/changelog`, gdzie Jan jest liderem scenariusza.
- Jan jest też blisko lidera w `PR description`.
- Najsłabsze obszary po refactorze to nadal `status email/notatka` i `support reply`, ale to już nie są słabe wyniki bezwzględne, tylko miejsca z największą deltą do `GPT-5.4`.
- Spadek latency z `26.28s` do `2.58s` pokazuje, że usunięcie verbose wrappera poprawiło nie tylko judge score, ale też realny koszt użycia narzędzia.

## What Changed

- Correction tools zwracają domyślnie tylko finalny tekst.
- `include_explanation=True` daje krótki explain mode zamiast ciężkiego raportu.
- `include_greeting=True` dokłada najwyżej jedną krótką linię.
- `verify_grammar()` pozostaje JSON-only.
- Benchmark raportuje teraz zarówno literal product score, jak i normalized diagnostic score.

## What We Measure

- `Jan` przez realny MCP `stdio`
- `raw Bielik`
- `GPT-5.4`

Scenariusze:

- `PR description`
- `ticket/issue`
- `support reply`
- `release note/changelog`
- `status email/notatka`

Intencje:

- `surface correction`
- `style rewrite`
- `full polish`

## How To Run

```bash
.venv/bin/python scripts/run_workplace_benchmark.py
```

## Interpretation Limits

- To nadal jest pilot na `15` przypadkach.
- Wyniki należy czytać jako sygnał produktowy, nie jako statystyczny werdykt o całej klasie zadań.
- Gdy produkt się rozszerzy poza workplace writing, powinien dostać osobny benchmark zamiast przeciążać ten pilot.
