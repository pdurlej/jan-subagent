# Wersja v2.1.0 - Paste-Ready Refactor

## Najważniejsze zmiany

- Domyślny kontrakt narzędzi correction tools jest teraz `paste-ready`.
- Explainery są dostępne tylko jako `opt-in` przez `include_explanation=True`.
- Benchmark workplace writing ma teraz dwa widoki:
  - `Primary Literal Score`
  - `Normalized Diagnostic Score`
- To wydanie nie dodaje osobnego trybu edukacyjnego ani learning mode.

## Zmiany zachowania

- `correct_orthography`, `correct_punctuation`, `improve_style` i `comprehensive_correction` zwracają domyślnie tylko finalny tekst.
- `verify_grammar` zwraca stabilny, parseowalny JSON bez wrappera persony.
- `check_text_quality` zwraca krótki plain-text scorecard bez persony.
- Persona-rich odpowiedzi pozostają w `get_language_advice`, `greet_jan` i `farewell_jan`.
- `include_explanation=True` zwraca corrected text i zwięzłą listę 2-5 najważniejszych zmian zamiast ciężkiego raportu.

## Migracja

Jeśli polegałeś na verbose outputach correction tools:

```python
# stary, implicit verbose behavior
correct_orthography(text)

# nowy default
correct_orthography(text)

# jeśli potrzebujesz skróconego explainera
correct_orthography(text, include_explanation=True)
```

Jeśli używałeś `include_greeting=True`, nadal możesz to zrobić, ale greeting jest teraz lekki i jednozdaniowy.

## Benchmark

- Literal score pozostaje głównym KPI produktu.
- Normalized diagnostic score służy tylko do odpowiedzi na pytanie, ile jakości kosztuje wrapper Jana.
- Public-safe raport pilota znajduje się w `docs/benchmarks/workplace-writing-pilot.md`.
- W rerunie pilota po refactorze Jan urósł z `49.9%` do `94.0%` literal final score, a średnia latency spadła z `26.28s` do `2.58s`.

## Future Direction Out Of Scope

- W tym wydaniu nie pozycjonujemy Jana jako produktu do nauki polskiego.
- Jeśli taki kierunek wróci, powinien dostać osobny workflow i osobny benchmark zamiast obciążać domyślne correction tools dla workplace writing.

## Walidacja wydania

```bash
pytest -q
.venv/bin/python -m compileall -q jan
.venv/bin/python -m jan.jan_subagent_opencode
.venv/bin/python scripts/test_benchmark_harness.py
python3 scripts/test_sync_bmad_method.py
python3 scripts/sync_bmad_method.py check --json
```
