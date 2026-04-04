# Workplace Writing Pilot

> Ten raport opisuje pilot benchmarkowy. Wyniki dotyczą wyłącznie tego zestawu 15 przypadków i nie są pełnym badaniem statystycznym.

## Zakres

- Timestamp runu: `20260404T012404Z`
- Liczba przypadków: `15`
- Systemy: `Jan, raw Bielik, GPT-5.4`
- Model OpenAI baseline: `gpt-5.4`
- Model judge: `gpt-5.4-mini`
- Model NVIDIA/Bielik: `speakleash/bielik-11b-v2.6-instruct`

## Overall

| System | Final | Deterministic | Judge | Avg latency | Error rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| GPT-5.4 | 96.8% | 92.7% | 100.0% | 1.47s | 0.0% |
| Jan | 49.9% | 68.8% | 30.1% | 26.28s | 0.0% |
| raw Bielik | 92.4% | 88.8% | 95.2% | 3.21s | 0.0% |

## By Scenario

| Scenario | Jan | raw Bielik | GPT-5.4 | Lider |
| --- | ---: | ---: | ---: | --- |
| PR description | 50.8% | 86.9% | 97.6% | GPT-5.4 (97.6%) |
| ticket/issue | 53.3% | 96.0% | 98.7% | GPT-5.4 (98.7%) |
| support reply | 46.7% | 94.7% | 100.0% | GPT-5.4 (100.0%) |
| release note/changelog | 49.8% | 91.1% | 90.1% | raw Bielik (91.1%) |
| status email/notatka | 49.1% | 93.2% | 97.8% | GPT-5.4 (97.8%) |

## Where Jan Helps

- W tym pilocie Jan nie prowadzi w żadnym scenariuszu, więc poniżej pokazane są najmniejsze straty względem lidera.
- `release note/changelog`: Jan ma wynik 49.8% i traci 41.2% względem lidera `raw Bielik`.
- `ticket/issue`: Jan ma wynik 53.3% i traci 45.3% względem lidera `GPT-5.4`.

## Where Jan Hurts

- `support reply`: Jan ma wynik 46.7%, a lider `GPT-5.4` osiąga 100.0%.
- `status email/notatka`: Jan ma wynik 49.1%, a lider `GPT-5.4` osiąga 97.8%.

## Interpretation

- W tym pilocie Jan ma średni score concision `20.0%` dla `surface correction`, co pozwala zobaczyć koszt persony i refleksji w krótkich zadaniach.
- Średni score workplace usefulness Jana dla `surface correction` wynosi `20.0%`; to pokazuje, czy domyślny UX pomaga mimo dłuższego outputu.
- Raport nie czyści ręcznie outputów Jana. Persona, refleksje i ewentualne ozdobniki liczą się do literalnej oceny systemu.

## Artefakty

- Surowe wyniki i raport live są zapisane w `/Users/pd/Developer/jan/_bmad-output/benchmarks/20260404T012404Z-workplace-writing-pilot`.
- Metodologia benchmarku znajduje się w `docs/benchmark-methodology.md`.
