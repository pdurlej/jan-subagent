# 📜 Jan - MCP do polskich changelogów i release notesów z notek GitHuba

![Version](https://img.shields.io/badge/version-3.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

> *"Niechaj mowa o waszych zmianach będzie jasna, wierna i gotowa do publikacji."*  
> Jan Kochanowski, gdyby pisał release notes

`jan-subagent` w `v3.0.0` nie jest już ogólnym korektorem polszczyzny. To repo-native agent MCP do tłumaczenia i pisania polskich changelogów, release notesów i opisów zmian na bazie typowych githubowych, bezosobowych angielskich notek, diffów i surowych bulletów technicznych.

Jan zachowuje charakter i brand Jana Kochanowskiego, ale domyślny workplace UX jest już w pełni `paste-ready`.

## Dlaczego Jan jest praktyczny

Najprostsza obietnica produktu jest taka:

- bierzesz typowe, surowe angielskie notki z GitHuba
- wrzucasz je do `compose_release_notes(...)`
- dostajesz gotowe, polskie release notesy albo changelog dla współpracowników

I możesz to odpalić za darmo w trybie prototypowania, korzystając z klucza NVIDIA Developer Program do hosted endpointów NIM. NVIDIA podaje, że członkowie programu mają darmowy dostęp do endpointów NIM do prototypowania:

- [Run NIM Anywhere](https://docs.api.nvidia.com/nim/docs/run-anywhere)
- [API Catalog Quickstart Guide](https://docs.api.nvidia.com/nim/docs/api-quickstart)

## Co zmieniło się w 3.0.0

- główny wedge produktu to `repo-native workflows`, nie ogólna korekta tekstu
- primary MCP surface to named workflows dla tech teamów
- `jan.yml` w repo działa jako memory-as-code dla templates, glossary, audience packs i validation policy
- source context może pochodzić z local git, GitHub i Jira
- workflowy mają trust layer: fact preservation, `no_new_facts`, template compliance, glossary adherence i audience-policy compliance
- `response_mode="review"` zwraca JSON z `final_text`, `source_trace` i `validator_report`
- stare tools korektorskie zostają tylko jako `legacy`

Pełna nota wydania: [docs/VERSION_3_0_0.md](/Users/pd/Developer/jan/docs/VERSION_3_0_0.md)  
Mapa migracji: [docs/MIGRATION_3_0_0.md](/Users/pd/Developer/jan/docs/MIGRATION_3_0_0.md)

## Pozycja produktu

Jan nie próbuje być „najlepszym LLM-em ogólnym”. Ma być najlepszym narzędziem MCP do codziennego zamieniania surowych angielskich notek z GitHuba na publikowalne polskie changelogi i release notesy.

Najwięcej sensu ma dziś w:

- tłumaczeniu i wygładzaniu release notes z angielskich bulletów
- opisach PR
- release notes i changelogach
- przepisywaniu ticketów i issue
- notatkach rolloutowych
- repo-native workflowach, gdzie liczy się `time-to-paste`, `fact preservation` i zgodność z template’em zespołu

Najmocniejszy sygnał z dotychczasowego pilota:

- po refactorze `paste-ready` Jan urósł z `49.9%` do `94.0%` `Primary Literal Score`
- średnia latency spadła z `26.28s` do `2.58s`
- Jan wyprzedził `raw Bielik` jako produkt, choć nadal minimalnie przegrywa ogólny wynik z `GPT-5.4`

Szczegóły: [docs/benchmarks/workplace-writing-pilot.md](/Users/pd/Developer/jan/docs/benchmarks/workplace-writing-pilot.md)

## Side by side: Jan vs typowy ogólny model

To nie jest formalny benchmark. To jest ilustracja różnicy stylu dla tego samego wejścia.

Wejście z typowych, bezosobowych notek GitHuba:

```text
- Added retry handling for checkout webhook delivery.
- Improved cache invalidation for product detail pages.
- Fixed duplicate analytics events on checkout success.
```

| Typowy baseline ogólnego modelu pokroju GPT-5.4 | Jan MCP |
| --- | --- |
| „Dodano obsługę ponownych prób dostarczenia webhooków checkoutu. Ulepszono unieważnianie pamięci podręcznej dla stron szczegółów produktu. Naprawiono zduplikowane zdarzenia analityczne po pomyślnym zakończeniu checkoutu.” | „Poprawiliśmy niezawodność checkoutu i uporządkowaliśmy kilka elementów wokół zakupu. System lepiej ponawia dostarczanie webhooków, strony produktów szybciej pokazują aktualne dane, a analityka po zakończonym checkoutcie nie dubluje już zdarzeń.” |

W praktyce chcemy, żeby różnica była taka:

- Jan ma brzmieć bardziej naturalnie dla polskiego odbiorcy technicznego albo produktowego
- Jan ma lepiej składać suche, angielskie bullet points w notkę, którą da się wkleić współpracownikom bez dalszego wygładzania
- baseline ogólnego modelu bywa bardziej neutralny, dosłowny i checklistowy

Nie chodzi o to, że GPT-5.4 „nie umie” pisać po polsku. Chodzi o to, że Jan jest ustawiony produktowo pod ten konkretny workflow: polskie release notesy i changelogi dla zespołu na bazie surowych notek z GitHuba.

## Primary MCP workflows

```python
write_pr_description(
    raw_notes: str = "",
    git_range: str | None = None,
    github_pr: int | None = None,
    jira_keys: list[str] | None = None,
    audience: str = "reviewer",
    response_mode: str = "final",
) -> str

compose_release_notes(
    raw_notes: str = "",
    git_range: str | None = None,
    github_prs: list[int] | None = None,
    jira_keys: list[str] | None = None,
    audience: str = "internal",
    response_mode: str = "final",
) -> str

rewrite_issue(
    raw_notes: str = "",
    github_issue: int | None = None,
    jira_key: str | None = None,
    audience: str = "internal",
    response_mode: str = "final",
) -> str

write_rollout_note(
    raw_notes: str = "",
    git_range: str | None = None,
    github_prs: list[int] | None = None,
    jira_keys: list[str] | None = None,
    audience: str = "internal",
    response_mode: str = "final",
) -> str
```

### Response modes

- `final`  
  Zwraca wyłącznie paste-ready tekst z wymaganymi sekcjami artefaktu.

- `review`  
  Zwraca JSON:

```json
{
  "final_text": "string",
  "source_trace": [
    {
      "segment": "string",
      "source_ids": ["string"],
      "note": "string"
    }
  ],
  "validator_report": {}
}
```

## Legacy tools

Te tools zostają callable dla kompatybilności, ale nie są już głównym surface’em produktu:

- `correct_orthography`
- `correct_punctuation`
- `verify_grammar`
- `improve_style`
- `comprehensive_correction`
- `check_text_quality`

`greet_jan`, `farewell_jan` i `get_language_advice` zostają jako brand skin i opt-in delight pack. To jest świadomy easter egg, nie główny workflow produktu.

## jan.yml

Repo-level `jan.yml` działa jako policy pack dla workflowów. Trzyma:

- `glossary`
- `do_not_translate`
- `banned_phrases`
- `artifact_templates`
- `required_sections`
- `audiences`
- `validation`
- `github`
- `jira`

To jest memory-as-code dla zespołu. Reguły nie są powtarzane w promptach ręcznie przy każdym użyciu.

W tym repo przykładowy policy pack jest w [jan.yml](/Users/pd/Developer/jan/jan.yml).

## Source context

Jan może pracować z trzema warstwami kontekstu:

1. `raw_notes`
2. local git: branch, changed files, commits, diff excerpt
3. GitHub i Jira, jeśli są dostępne tokeny

Brak tokenów nie tworzy sztucznego kontekstu. Workflow degraduje się do tego, co jest naprawdę dostępne, i raportuje warningi w `review`.

## Instalacja

### Wymagania

- Python 3.10+
- MCP client, np. Claude Desktop albo Cursor
- NVIDIA API key dla Bielika

### Jak dostać darmowy NVIDIA API key krok po kroku

Poniższy flow opiera się na oficjalnym quickstarcie NVIDIA API Catalog i dokumentacji NIM:

1. Wejdź na [build.nvidia.com](https://build.nvidia.com/).
2. Wyszukaj model albo endpoint, którego chcesz używać. Dla Jana najważniejsze jest to, żeby mieć działający klucz do hosted endpointów NVIDIA.
3. Otwórz stronę modelu i kliknij `Get API Key` w prawym panelu.
4. Podaj adres e-mail i dokończ logowanie albo rejestrację. Według dokumentacji NVIDIA zapisze Cię to do NVIDIA Developer Program.
5. Po powrocie na stronę modelu skopiuj wygenerowany klucz API i zapisz go lokalnie w bezpiecznym miejscu.
6. Ustaw go lokalnie jako `NVIDIA_API_KEY`, np. w `.env` albo w `~/.jan/config.json`.
7. Uruchom Jana i sprawdź smoke test:

```bash
NVIDIA_API_KEY="twoj-klucz" .venv/bin/python -m jan.jan_subagent_opencode
```

Oficjalne źródła:

- [API Catalog Quickstart Guide](https://docs.api.nvidia.com/nim/docs/api-quickstart)
- [Run NIM Anywhere](https://docs.api.nvidia.com/nim/docs/run-anywhere)

W dokumentacji NVIDIA jest wprost napisane, że członkowie programu deweloperskiego mają darmowy dostęp do endpointów NIM do prototypowania. Traktuj to jako darmowy start dla zespołu i sprawdzenie workflowu przed ewentualnym wdrożeniem produkcyjnym.

### Instalacja lokalna

```bash
cd /Users/pd/Developer/jan
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -e .
```

### Konfiguracja MCP

Repo zawiera gotowy sample config: [mcp_config.json](/Users/pd/Developer/jan/mcp_config.json)

```json
{
  "mcpServers": {
    "jan-kochanowski": {
      "command": "/absolute/path/to/jan/.venv/bin/python",
      "args": [
        "-m",
        "jan.jan_subagent_opencode"
      ],
      "cwd": "/absolute/path/to/jan",
      "env": {}
    }
  }
}
```

### Konfiguracja kluczy i source context

Najważniejsze envy:

- `NVIDIA_API_KEY`
- `GITHUB_TOKEN`
- `GITHUB_REPOSITORY`
- `JIRA_BASE_URL`
- `JIRA_EMAIL`
- `JIRA_API_TOKEN`
- `JAN_POLICY_FILE`

Pełny przykład: [.env.example](/Users/pd/Developer/jan/.env.example)

## Benchmarking

### Benchmark v1: workplace writing pilot

Ten benchmark zostaje jako regression suite. Mierzy literalny wynik produktu i pilnuje, żeby Jan nie wrócił do verbose wrappera.

- metodologia: [docs/benchmark-methodology.md](/Users/pd/Developer/jan/docs/benchmark-methodology.md)
- public-safe raport: [docs/benchmarks/workplace-writing-pilot.md](/Users/pd/Developer/jan/docs/benchmarks/workplace-writing-pilot.md)

### Benchmark v2: repo-native delivery workflows

Nowy harness benchmarkowy działa na osi:

- `artifact`
- `context richness`
- `audience`

Lane’y:

- `text_only`
- `structured_context`
- `policy_pack`

North-star KPI:

- zero/one-edit acceptance rate
- fact preservation
- `no_new_facts`
- template compliance
- glossary adherence
- time-to-paste
- p95 latency

Artefakty i harness:

- dataset: [benchmarks/delivery_workflows_v2.jsonl](/Users/pd/Developer/jan/benchmarks/delivery_workflows_v2.jsonl)
- module: [jan/delivery_benchmark.py](/Users/pd/Developer/jan/jan/delivery_benchmark.py)
- CI-safe test: [scripts/test_delivery_benchmark.py](/Users/pd/Developer/jan/scripts/test_delivery_benchmark.py)
- live runner: [scripts/run_delivery_benchmark.py](/Users/pd/Developer/jan/scripts/run_delivery_benchmark.py)

## BMAD / BMADX

Repo pracuje teraz na fundamencie `X4` dla pivotu `v3.0.0`.

Trwałe artefakty:

- PRD: [_bmad-output/planning-artifacts/jan-v3-prd.md](/Users/pd/Developer/jan/_bmad-output/planning-artifacts/jan-v3-prd.md)
- architektura: [_bmad-output/planning-artifacts/jan-v3-architecture.md](/Users/pd/Developer/jan/_bmad-output/planning-artifacts/jan-v3-architecture.md)
- project context: [_bmad-output/project-context.md](/Users/pd/Developer/jan/_bmad-output/project-context.md)
- FUBAR bundle: [_bmad-output/planning-artifacts/jan-v3-fubar](/Users/pd/Developer/jan/_bmad-output/planning-artifacts/jan-v3-fubar)

Zasada pozostaje prosta:

- `BMAD > BMADX`
- `project-context.md` jest source-of-truth dla tego pivotu

## Architektura repo

```text
jan/
├── jan/
│   ├── api_client.py
│   ├── config.py
│   ├── delivery_benchmark.py
│   ├── jan_subagent_opencode.py
│   ├── output_utils.py
│   ├── policy.py
│   ├── source_adapters.py
│   ├── source_context.py
│   ├── system_prompts.py
│   ├── workflow_engine.py
│   └── workplace_benchmark.py
├── benchmarks/
├── docs/
├── scripts/
├── _bmad/
├── _bmad-output/
├── jan.yml
└── mcp_config.json
```

## Validation commands

```bash
python3 -m pytest -q
.venv/bin/python -m compileall -q jan
.venv/bin/python -m jan.jan_subagent_opencode
.venv/bin/python scripts/test_benchmark_harness.py
.venv/bin/python scripts/test_delivery_benchmark.py
python3 scripts/test_sync_bmad_method.py
python3 scripts/sync_bmad_method.py check --json
```

Live benchmark v2:

```bash
.venv/bin/python scripts/run_delivery_benchmark.py --systems Jan raw-bielik gpt-5.4
```

## Kontakt

- Issues: [GitHub Issues](https://github.com/pdurlej/jan-subagent/issues)
- Repo: [pdurlej/jan-subagent](https://github.com/pdurlej/jan-subagent)

---

*Jan wciąż umie się ukłonić, ale teraz przede wszystkim dowozi release notes.*
