# Workplace Writing Pilot

> Ten raport opisuje pilot benchmarkowy. Wyniki dotyczą wyłącznie tego zestawu 15 przypadków i nie są pełnym badaniem statystycznym.

## Zakres

- Timestamp runu: `20260404T020037Z`
- Liczba przypadków: `15`
- Systemy: `Jan, raw Bielik, GPT-5.4`
- Model OpenAI baseline: `gpt-5.4`
- Model judge: `gpt-5.4-mini`
- Model NVIDIA/Bielik: `speakleash/bielik-11b-v2.6-instruct`

## Scoring Modes

- `Primary Literal Score` jest głównym KPI produktu i ocenia dokładnie to, co użytkownik dostaje z narzędzia.
- `Normalized Diagnostic Score` usuwa technicznie wrapper Jana i służy tylko do sprawdzenia, ile kosztuje opakowanie odpowiedzi.

## Primary Literal Score

| System | Final | Deterministic | Judge | Avg latency | Error rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| GPT-5.4 | 96.5% | 92.0% | 100.0% | 1.48s | 0.0% |
| Jan | 94.0% | 88.9% | 97.9% | 2.58s | 0.0% |
| raw Bielik | 93.1% | 88.3% | 96.8% | 3.24s | 0.0% |

| Scenario | Jan | raw Bielik | GPT-5.4 | Lider |
| --- | ---: | ---: | ---: | --- |
| PR description | 96.8% | 91.7% | 97.6% | GPT-5.4 (97.6%) |
| ticket/issue | 95.2% | 96.0% | 97.3% | GPT-5.4 (97.3%) |
| support reply | 96.0% | 94.7% | 100.0% | GPT-5.4 (100.0%) |
| release note/changelog | 91.1% | 91.1% | 90.1% | Jan (91.1%) |
| status email/notatka | 91.1% | 92.2% | 97.8% | GPT-5.4 (97.8%) |

## Normalized Diagnostic Score

| System | Final | Deterministic | Judge | Avg latency | Error rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| GPT-5.4 | 96.5% | 92.0% | 100.0% | 1.48s | 0.0% |
| Jan | 93.9% | 88.9% | 97.6% | 2.58s | 0.0% |
| raw Bielik | 92.3% | 88.3% | 95.5% | 3.24s | 0.0% |

| Scenario | Jan | raw Bielik | GPT-5.4 | Lider |
| --- | ---: | ---: | ---: | --- |
| PR description | 96.8% | 87.7% | 97.6% | GPT-5.4 (97.6%) |
| ticket/issue | 94.4% | 96.0% | 97.3% | GPT-5.4 (97.3%) |
| support reply | 96.0% | 94.7% | 100.0% | GPT-5.4 (100.0%) |
| release note/changelog | 91.1% | 91.1% | 90.1% | Jan (91.1%) |
| status email/notatka | 91.1% | 92.2% | 97.8% | GPT-5.4 (97.8%) |


## Where Jan Helps

- `release note/changelog`: Jan prowadzi z wynikiem 91.1%.

## Where Jan Hurts

- `status email/notatka`: Jan ma wynik 91.1%, a lider `GPT-5.4` osiąga 97.8%.
- `support reply`: Jan ma wynik 96.0%, a lider `GPT-5.4` osiąga 100.0%.

## Interpretation

- W tym pilocie Jan ma średni score concision `100.0%` dla `surface correction`, co pozwala zobaczyć koszt persony i refleksji w krótkich zadaniach.
- Średni score workplace usefulness Jana dla `surface correction` wynosi `100.0%`; to pokazuje, czy domyślny UX pomaga mimo dłuższego outputu.
- Po technicznym odfiltrowaniu wrappera Jana surface-correction concision rośnie do `100.0%`, a workplace usefulness do `100.0%`.
- Raport nie czyści ręcznie outputów Jana. Persona, refleksje i ewentualne ozdobniki liczą się do literalnej oceny systemu.

## Artefakty

- Surowe wyniki i raport live są zapisane w `/Users/pd/Developer/jan/_bmad-output/benchmarks/20260404T020037Z-workplace-writing-pilot`.
- Metodologia benchmarku znajduje się w `docs/benchmark-methodology.md`.
