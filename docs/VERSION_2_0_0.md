# Wersja v2.0.0 - Canonical OpenCode Release

## Najważniejsze zmiany

- `jan.jan_subagent_opencode` jest jedynym wspieranym runtime MCP.
- Usunięto legacy moduł `jan.jan_subagent`.
- `mcp_config.json` jest teraz jedynym sample configiem i jest poprawnym JSON-em.
- Release hygiene obejmuje teraz BMAD onboarding, CI i aktualne metadata repo.

## Breaking Changes

### Usunięty legacy entrypoint

- `python -m jan.jan_subagent` nie jest już wspierane.
- `jan-server` wskazuje wyłącznie na `jan.jan_subagent_opencode:main`.
- Dokumentacja i przykłady nie promują już starej ścieżki.

### Migracja

Jeśli używałeś starego entrypointu:

```bash
# stary sposób
python -m jan.jan_subagent

# nowy sposób
python -m jan.jan_subagent_opencode
```

Jeśli używałeś starego configu MCP, zaktualizuj `args` do:

```json
["-m", "jan.jan_subagent_opencode"]
```

## Runtime i konfiguracja

- `check_configuration()` zwraca statusy jako `✅/❌`, zgodnie z README.
- `greet_jan(name=...)` wykorzystuje przekazanego adresata.
- `main()` nie wypisuje banneru na `stdout`, więc nie zakłóca transportu `stdio`.
- `BielikClient.reset()` odświeża `api_key`, `api_base` i `model_id`.

## BMAD

- Dodano maintenance scaffold BMAD oparty o lokalny skill `bmad-method-codex`.
- Dodano pełną instalację projektową `_bmad/` i `_bmad-output/`.
- Repo-specific punkt wejścia do workflowów to `bmad-help`.
- Release hygiene BMAD utrzymujemy przez:

```bash
python3 scripts/test_sync_bmad_method.py
python3 scripts/sync_bmad_method.py check --json
```

## Walidacja wydania

```bash
pytest -q
.venv/bin/python -m compileall -q jan
.venv/bin/python -m jan.jan_subagent_opencode
python3 scripts/test_sync_bmad_method.py
python3 scripts/sync_bmad_method.py check --json
```
