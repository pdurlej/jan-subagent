# 📜 Jan Subagent - MCP server do korekty polszczyzny

![Version](https://img.shields.io/badge/version-2.1.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

> *"Niechaj Bóg strzeże wasze pióra i myśli"* - Jan Kochanowski

`jan-subagent` to MCP server do korekty języka polskiego z personą Jana Kochanowskiego i integracją z NVIDIA Bielik. Wydanie `2.1.0` przesuwa Jana w stronę paste-ready workplace writing przy zachowaniu persony w narzędziach poradniczych.

## Co się zmieniło w 2.1.0

- Correction tools są domyślnie `paste-ready` i zwracają tylko finalny tekst.
- Explainery są dostępne tylko jako `opt-in` przez `include_explanation=True`.
- `verify_grammar()` zwraca parseowalny JSON bez wrappera persony.
- `check_text_quality()` zwraca krótki plain-text scorecard.
- Benchmark workplace writing ma teraz `Primary Literal Score` i `Normalized Diagnostic Score`.
- To wydanie nie dodaje osobnego trybu edukacyjnego; domyślny fokus pozostaje na workplace writing.

Pełna nota wydania: [docs/VERSION_2_1_0.md](/Users/pd/Developer/jan/docs/VERSION_2_1_0.md)

## Cechy

- Paste-ready correction tools dla workplace writing.
- Persona Jana Kochanowskiego w poradach językowych i lekkich interakcjach.
- Integracja z NVIDIA Bielik przez OpenAI-compatible API.
- Narzędzia MCP do ortografii, interpunkcji, gramatyki, stylu i szybkiej oceny tekstu.
- Automatyczna konfiguracja API key przez `setup_api_key`.
- Konfiguracja ładowana z `NVIDIA_API_KEY` lub `~/.jan/config.json`.
- Lazy import `jan.mcp`, bez side-effectów przy `python -m`.

## Instalacja

### Wymagania

- Python 3.10+
- MCP client, np. Claude Desktop albo Cursor
- NVIDIA API key dla Bielika

### Instalacja lokalna

```bash
cd /Users/pd/Developer/jan
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -e .
```

### Konfiguracja MCP

Repo zawiera gotowy sample config: [mcp_config.json](/Users/pd/Developer/jan/mcp_config.json)

Uzupełnij w nim własne ścieżki:

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

Najbezpieczniej wskazać interpreter z wirtualnego środowiska, bo globalne `python3` może nie mieć zainstalowanego pakietu `mcp`.

### Pierwsza konfiguracja API key

1. Uzyskaj NVIDIA API key na [build.nvidia.com](https://build.nvidia.com/) albo [NGC API Keys](https://org.ngc.nvidia.com/setup/api-keys).
2. Uruchom klienta MCP z Janem.
3. Przy pierwszym użyciu `@jan` poprosi o klucz:

```text
@jan popraw ten tekst
```

4. Ustaw klucz przez narzędzie MCP:

```text
Użyj setup_api_key z api_key: "nvapi-xxxx-xxxx-xxxx-xxxx"
```

Klucz zostanie zapisany w `~/.jan/config.json`.

### Ręczna konfiguracja przez `.env`

Fallback nadal działa, ale nie jest preferowany. Przykład zmiennych znajdziesz w [.env.example](/Users/pd/Developer/jan/.env.example).

## Narzędzia MCP

### Konfiguracja

```python
check_configuration() -> str
setup_api_key(api_key: str) -> str
reset_api_key() -> str
```

`check_configuration()` zwraca status konfiguracji, model, base URL i domyślne parametry. Statusy są prezentowane jako `✅/❌`.

### Korekta językowa

```python
correct_orthography(text: str, include_greeting: bool = False, include_explanation: bool = False) -> str
correct_punctuation(text: str, include_greeting: bool = False, include_explanation: bool = False) -> str
verify_grammar(text: str, include_greeting: bool = False) -> str
improve_style(text: str, style: str = "elegancki", include_greeting: bool = False, include_explanation: bool = False) -> str
comprehensive_correction(text: str, mode: str = "standard", include_greeting: bool = False, include_explanation: bool = False) -> str
get_language_advice(topic: str) -> str
check_text_quality(text: str) -> str
greet_jan(name: str = "miłościw") -> str
farewell_jan() -> str
```

Domyślnie correction tools zwracają wyłącznie finalny tekst. Jeśli chcesz krótki explain mode, ustaw `include_explanation=True`.
`include_greeting=True` nadal działa, ale dodaje tylko jedną krótką linię przed wynikiem zamiast dawnego, rozbudowanego wrappera Jana.

Obsługiwane style dla `improve_style`:

- `elegancki`
- `prosty`
- `poetycki`
- `naukowy`
- `ulotny`

Obsługiwane tryby dla `comprehensive_correction`:

- `conservative`
- `standard`
- `aggressive`

## Przykłady użycia

### Prosta korekta ortografii

```text
Użyj correct_orthography z tekstem:
"Cześć! Napisalem tekst z błedami."
```

### Krótki explain mode

```text
Użyj improve_style z tekstem:
"Hej, temat mamy już ogarnięty i wszystko śmiga."

ustawiając include_explanation na true.
```

### Porada językowa

```text
Użyj get_language_advice z tematem:
"ó vs u"
```

### Powitanie z adresatem

```python
from jan.jan_subagent_opencode import greet_jan

print(greet_jan("Pawle"))
```

## Architektura repo

```text
jan/
├── jan/
│   ├── __init__.py
│   ├── api_client.py
│   ├── config.py
│   ├── jan_subagent_opencode.py
│   ├── kochanowski_quotes.py
│   ├── output_utils.py
│   ├── system_prompts.py
│   └── workplace_benchmark.py
├── docs/
│   ├── VERSION_1_1_0.md
│   ├── VERSION_2_0_0.md
│   ├── VERSION_2_1_0.md
│   ├── benchmark-methodology.md
│   ├── benchmarks/
│   └── new-thread-start.md
├── tests/
├── examples/
├── benchmarks/
├── scripts/
├── references/
├── agents/
├── state/
├── _bmad/
├── _bmad-output/
├── .github/
├── mcp_config.json
└── setup.py
```

## BMAD

Repo jest przygotowane do pracy zarówno z maintenance scaffoldem BMAD, jak i pełną warstwą projektową.

- Punkt wejścia do workflowów projektowych: `bmad-help`
- Maintenance sync:

```bash
python3 scripts/test_sync_bmad_method.py
python3 scripts/sync_bmad_method.py check --json
```

Pełna instalacja projektowa znajduje się w `_bmad/`, a wygenerowane artefakty trafiają do `_bmad-output/`.

## Benchmarking

Repo zawiera pilot benchmarkowy workplace writing porównujący:

- `Jan` przez realny MCP `stdio`
- `raw Bielik`
- `GPT-5.4`

Dataset, prompty i rubric są w `benchmarks/`, metodologia w [docs/benchmark-methodology.md](/Users/pd/Developer/jan/docs/benchmark-methodology.md), a public-safe notatka pilota w [docs/benchmarks/workplace-writing-pilot.md](/Users/pd/Developer/jan/docs/benchmarks/workplace-writing-pilot.md).

Benchmark ma teraz dwa widoki:

- `Primary Literal Score` jako główny KPI produktu
- `Normalized Diagnostic Score` jako diagnostykę kosztu wrappera Jana

`Normalized Diagnostic Score` nie zastępuje literalnego wyniku produktu. Służy tylko do odpowiedzi na pytanie, ile jakości kosztuje opakowanie odpowiedzi Jana.

CI-safe walidacja harnessu:

```bash
.venv/bin/python scripts/test_benchmark_harness.py
```

Live pilot:

```bash
.venv/bin/python scripts/run_workplace_benchmark.py
```

Artefakty live runu trafiają do `_bmad-output/benchmarks/<timestamp>/`.

## Testowanie

```bash
pytest -q
.venv/bin/python -m compileall -q jan
.venv/bin/python -m jan.jan_subagent_opencode
.venv/bin/python scripts/test_benchmark_harness.py
python3 scripts/test_sync_bmad_method.py
python3 scripts/sync_bmad_method.py check --json
```

## Dokumentacja API

### `BielikClient`

```python
from jan.api_client import BielikClient

client = BielikClient()
response = client.call(
    system_prompt="Jesteś ekspertem...",
    user_message="Popraw tekst...",
    temperature=0.3,
    max_tokens=4096,
)
```

### `KochanowskiPersona`

```python
from jan.kochanowski_quotes import KochanowskiPersona

greeting = KochanowskiPersona.get_greeting()
reflection = KochanowskiPersona.get_reflection("orthography")
```

## Współpraca

1. Utwórz branch roboczy.
2. Utrzymuj README, sample config i testy w zgodzie z runtime `jan.jan_subagent_opencode`.
3. Przy zmianach release/BMAD aktualizuj [docs/new-thread-start.md](/Users/pd/Developer/jan/docs/new-thread-start.md).

## Licencja

MIT License - patrz [LICENSE](/Users/pd/Developer/jan/LICENSE).

## Kontakt

- Issues: [GitHub Issues](https://github.com/pdurlej/jan-subagent/issues)
- Repo: [pdurlej/jan-subagent](https://github.com/pdurlej/jan-subagent)

---

*"Mowa polska to skarb narodu. Niech go chronicie i rozwijacie."* - Jan Subagent
