# 📜 Jan Subagent - MCP server do korekty polszczyzny

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

> *"Niechaj Bóg strzeże wasze pióra i myśli"* - Jan Kochanowski

`jan-subagent` to MCP server do korekty języka polskiego z personą Jana Kochanowskiego i integracją z NVIDIA Bielik. Wydanie `2.0.0` ustanawia jeden kanoniczny runtime: `jan.jan_subagent_opencode`.

## Co się zmieniło w 2.0.0

- `jan.jan_subagent_opencode` jest jedynym wspieranym runtime MCP.
- Usunięto legacy moduł `jan.jan_subagent`.
- `mcp_config.json` jest jedynym sample configiem i jest poprawnym JSON-em.
- `check_configuration()` zwraca statusy jako `✅/❌`.
- `greet_jan(name=...)` realnie używa przekazanego adresata.
- `main()` nie wypisuje nic na `stdout`, więc nie zakłóca transportu `stdio`.
- Repo zawiera maintenance scaffold BMAD oraz pełną warstwę projektową `_bmad/`.

Pełna nota wydania: [docs/VERSION_2_0_0.md](/Users/pd/Developer/jan/docs/VERSION_2_0_0.md)

## Cechy

- Persona Jana Kochanowskiego w odpowiedziach, refleksjach i poradach językowych.
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
correct_orthography(text: str, include_greeting: bool = True) -> str
correct_punctuation(text: str, include_greeting: bool = True) -> str
verify_grammar(text: str, include_greeting: bool = True) -> str
improve_style(text: str, style: str = "elegancki", include_greeting: bool = True) -> str
comprehensive_correction(text: str, mode: str = "standard") -> str
get_language_advice(topic: str) -> str
check_text_quality(text: str) -> str
greet_jan(name: str = "miłościw") -> str
farewell_jan() -> str
```

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
│   └── system_prompts.py
├── docs/
│   ├── VERSION_1_1_0.md
│   ├── VERSION_2_0_0.md
│   └── new-thread-start.md
├── tests/
├── examples/
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

## Testowanie

```bash
pytest -q
.venv/bin/python -m compileall -q jan
.venv/bin/python -m jan.jan_subagent_opencode
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
