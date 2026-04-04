# Jan MCP

![Version](https://img.shields.io/badge/version-3.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

<p align="center">
  <img src="docs/images/jan-kochanowski-coder-engraving.webp" alt="Jan Kochanowski jako skupiony coder w stylu starej ryciny" width="720" />
</p>

> Od suchych bulletów do publikowalnych release notes. Po polsku.

Jan to repo-native MCP agent dla polskich zespołów technicznych. Bierze typowe GitHubowe notki, diffy i surowe bullet points, a oddaje gotowe changelogi, release notesy i opisy PR, które da się wkleić bez dalszego wygładzania.

- Zamienia bezosobowe, angielskie notki z GitHuba w naturalny polski komunikat dla zespołu.
- Trzyma się faktów i szablonów artefaktu zamiast pisać "od zera" jak ogólny chat.
- Działa w MCP i można go prototypować za darmo na `NVIDIA_API_KEY`.

Szybkie przejścia: [Quickstart](#quickstart) · [Before / After](#before--after) · [Core workflows](#core-workflows) · [Benchmarki](#benchmark-snapshot)

## Co robi Jan

Jan jest ustawiony pod jeden konkretny workflow: komunikację zmian w software delivery po polsku.

Najlepiej sprawdza się przy:

- release notesach i changelogach z GitHubowych bulletów
- opisach PR dla reviewerów
- porządkowaniu ticketów i issue do formy gotowej dla zespołu
- notatkach rolloutowych opartych o realny kontekst z repo

Nie jest pozycjonowany jako "najmądrzejszy model ogólny". Ma być lepszym narzędziem do codziennego publikowania zmian po polsku.

## Before / After

Wejście z typowych, bezosobowych notek GitHuba:

```text
- Added retry handling for checkout webhook delivery.
- Improved cache invalidation for product detail pages.
- Fixed duplicate analytics events on checkout success.
```

| Typowy ogólny model | Jan MCP |
| --- | --- |
| Dodano obsługę ponownych prób dostarczenia webhooków checkoutu. Ulepszono unieważnianie pamięci podręcznej dla stron szczegółów produktu. Naprawiono zduplikowane zdarzenia analityczne po pomyślnym zakończeniu checkoutu. | Poprawiliśmy niezawodność checkoutu i uporządkowaliśmy kilka elementów wokół zakupu. System lepiej ponawia dostarczanie webhooków, strony produktów szybciej pokazują aktualne dane, a analityka po zakończonym checkoutcie nie dubluje już zdarzeń. |

Różnica nie polega na "magii modelu". Jan jest po prostu ustawiony produktowo pod polskie release notesy i changelogi dla współpracowników, a nie pod ogólną konwersację.

## Quickstart

```bash
git clone https://github.com/pdurlej/jan-subagent.git
cd jan-subagent
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -e .
export NVIDIA_API_KEY="twoj-klucz"
.venv/bin/python -m jan.jan_subagent_opencode
```

Gotowy sample config dla klienta MCP jest w [mcp_config.json](mcp_config.json).

Jeśli chcesz szybko sprawdzić runtime lokalnie:

```bash
python3 -m pytest -q
.venv/bin/python -m compileall -q jan
.venv/bin/python -m jan.jan_subagent_opencode
```

## Get a free NVIDIA API key

Jan działa na Bieliku przez hosted endpointy NVIDIA NIM. Do prototypowania wystarczy darmowy dostęp z NVIDIA Developer Program.

1. Wejdź na [build.nvidia.com](https://build.nvidia.com/).
2. Otwórz dowolny model lub endpoint i kliknij `Get API Key`.
3. Zaloguj się albo załóż konto w NVIDIA Developer Program.
4. Skopiuj klucz i ustaw lokalnie jako `NVIDIA_API_KEY`.

Oficjalne źródła:

- [API Catalog Quickstart Guide](https://docs.api.nvidia.com/nim/docs/api-quickstart)
- [Run NIM Anywhere](https://docs.api.nvidia.com/nim/docs/run-anywhere)

Przykładowy plik środowiskowy jest w [.env.example](.env.example).

## Core workflows

Jan ma dziś najwięcej sensu jako zestaw nazwanych workflowów, a nie zbiór ogólnych promptów.

### Release notes z surowych bulletów

```python
compose_release_notes(
    raw_notes="""
    - Added retry handling for checkout webhook delivery.
    - Improved cache invalidation for product detail pages.
    - Fixed duplicate analytics events on checkout success.
    """,
    audience="customer",
)
```

### Opis PR dla reviewera

```python
write_pr_description(
    raw_notes="""
    checkout webhook retries
    product page cache invalidation
    analytics dedupe on success
    """,
    audience="reviewer",
)
```

### Rewrite chaotycznego issue do formy zespołowej

```python
rewrite_issue(
    raw_notes="""
    klient zgłasza, że po checkoutcie czasem są zdublowane eventy,
    trudno to odtworzyć, wygląda na problem po stronie success callback
    """,
    audience="internal",
    response_mode="review",
)
```

### Notatka rolloutowa z review JSON

```python
write_rollout_note(
    raw_notes="Rollout checkout webhook retry logic behind a feature flag.",
    audience="internal",
    response_mode="review",
)
```

`response_mode="final"` zwraca gotowy tekst do wklejenia. `response_mode="review"` zwraca JSON z `final_text`, `source_trace` i `validator_report`.

## Dla kogo

Jan najlepiej pasuje do:

- polskich zespołów produktowo-inżynieryjnych
- leadów i senior engineerów piszących opisy PR
- release managerów składających changelog lub release notes
- zespołów, które chcą spójnej terminologii i szablonów bez ręcznego promptowania

Mniej sensu ma wtedy, gdy potrzebujesz ogólnego asystenta do wszystkiego albo miękkiej, relacyjnej komunikacji typu support reply czy statusowy mail.

## Kiedy Jan jest lepszym wyborem niż model ogólny

| Sytuacja | Lepszy wybór | Dlaczego |
| --- | --- | --- |
| Release notes z suchych bulletów i commitów | Jan | Ma workflow, audience packs, policy pack i output gotowy do wklejenia. |
| Opis PR zgodny z template'em zespołu | Jan | Lepiej trzyma sekcje, fakty i terminologię z repo. |
| Porządkowanie issue pod zespół techniczny | Jan | Pracuje na named workflow, nie na improwizowanym promptcie. |
| Otwarta burza mózgów albo swobodny writing assistant | Ogólny model | Tu specjalizacja Jana daje mniej przewagi niż szeroka inteligencja ogólna. |

## Benchmark snapshot

Obecny pilot po refactorze `paste-ready`:

- `GPT-5.4`: `96.5%`
- `Jan`: `94.0%`
- `raw Bielik`: `93.1%`

Najważniejszy sygnał: Jan nie wygrywa "większą inteligencją ogólną". Wygrywa tym, że daje lepszy workflow i bardziej publikowalny polski output niż surowy model.

Dalsze szczegóły:

- [Workplace writing pilot](docs/benchmarks/workplace-writing-pilot.md)
- [Repo-native delivery benchmark v2](docs/benchmarks/repo-native-delivery-v2.md)
- [Metodologia benchmarków](docs/benchmark-methodology.md)

## Advanced context

Jan potrafi pracować na więcej niż samym `raw_notes`.

- `jan.yml` trzyma glossary, `do_not_translate`, audience packs i validation policy.
- Workflow może korzystać z local git, GitHuba i Jiry, jeśli są dostępne kredensiale.
- `review` mode dodaje traceability i raport walidacyjny zamiast zgadywania.

Najważniejsze envy:

- `NVIDIA_API_KEY`
- `GITHUB_TOKEN`
- `GITHUB_REPOSITORY`
- `JIRA_BASE_URL`
- `JIRA_EMAIL`
- `JIRA_API_TOKEN`
- `JAN_POLICY_FILE`

Zobacz:

- [jan.yml](jan.yml)
- [.env.example](.env.example)

## Dalsza lektura

- [Release notes v3.0.0](docs/VERSION_3_0_0.md)
- [Migration guide 3.0.0](docs/MIGRATION_3_0_0.md)
- [Contributor thread bootstrap](docs/new-thread-start.md)

## Dla contributorów

Jeśli chcesz pracować nad repo, benchmarkami albo planowaniem kolejnych pivotów:

- [_bmad-output/project-context.md](_bmad-output/project-context.md)
- [_bmad-output/planning-artifacts/jan-v3-prd.md](_bmad-output/planning-artifacts/jan-v3-prd.md)
- [_bmad-output/planning-artifacts/jan-v3-architecture.md](_bmad-output/planning-artifacts/jan-v3-architecture.md)
- [scripts/test_delivery_benchmark.py](scripts/test_delivery_benchmark.py)
- [scripts/run_delivery_benchmark.py](scripts/run_delivery_benchmark.py)

## Kontakt

- [GitHub Issues](https://github.com/pdurlej/jan-subagent/issues)
- [Repozytorium](https://github.com/pdurlej/jan-subagent)
