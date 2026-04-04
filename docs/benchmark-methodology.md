# Benchmark Methodology

## Scope

Ten benchmark dotyczy `jan-subagent` jako produktu do workplace writing, nie wyłącznie modelu bazowego.
To pilot public-safe, więc wyniki należy interpretować jako obserwacje z małego zestawu przypadków, a nie jako pełny benchmark statystyczny.

## Systems

Benchmark porównuje trzy systemy:

- `Jan` przez realny transport MCP `stdio` i aktualne domyślne UX narzędzi Jana
- `raw Bielik` przez bezpośrednie wywołania NVIDIA API bez persony Jana
- `GPT-5.4` przez OpenAI API jako mocny baseline workplace writing

Judge jest osobny od benchmarkowanych modeli i domyślnie działa na `gpt-5.4-mini`.

## Dataset

Pilot korzysta z `benchmarks/workplace_writing_v1.jsonl`.

Zestaw zawiera `15` przypadków:

- `5` scenariuszy:
  - `PR description`
  - `ticket/issue`
  - `support reply`
  - `release note/changelog`
  - `status email/notatka`
- `3` intencje na scenariusz:
  - `surface correction`
  - `style rewrite`
  - `full polish`

Każdy case ma jawny schemat:

- `id`
- `scenario`
- `intent`
- `input_text`
- `jan_tool`
- `baseline_prompt_family`
- `must_keep`
- `should_fix`
- `must_not_introduce`
- `notes`

## Prompting Rules

Jan jest mierzony przez realne narzędzia MCP:

- `surface correction` trafia do `correct_orthography` albo `correct_punctuation`
- `style rewrite` trafia do `improve_style`
- `full polish` trafia do `comprehensive_correction(mode="standard")`

Nie wyłączamy domyślnych elementów UX Jana. Jeśli narzędzie dorzuca powitanie, refleksję lub pożegnanie, to te elementy zostają ocenione literalnie.

Baseline prompts są jawnie zdefiniowane w `benchmarks/prompt_families.json` i spełniają trzy zasady:

- brak persony Jana
- brak promptowych hacków pod benchmark
- zwrot wyłącznie finalnego tekstu

## Scoring

Benchmark ma scoring hybrydowy i dwa widoki raportowe.

### Two Views

- `Primary Literal Score`: główny wynik produktu. Ocenia dokładnie literalny output, który użytkownik dostaje z narzędzia.
- `Normalized Diagnostic Score`: widok diagnostyczny. Dla Jana usuwa technicznie wrappery takie jak greeting, nagłówki, listy zmian i sekcje raportowe, aby oszacować koszt opakowania odpowiedzi.

### Deterministic Layer

Warstwa deterministyczna ocenia:

- `must_keep`: czy ważne fakty i słowa nadal są obecne
- `should_fix`: czy błędne lub niepożądane fragmenty zniknęły
- `must_not_introduce`: czy system nie dodał zakazanych elementów
- `non_empty`: czy output nie jest pusty
- `error_free`: czy system nie zakończył się błędem
- `latency`: prosty score 0-1 zależny od czasu odpowiedzi

Wagi komponentów deterministycznych:

- `must_keep`: `0.30`
- `should_fix`: `0.25`
- `must_not_introduce`: `0.15`
- `non_empty`: `0.10`
- `error_free`: `0.10`
- `latency`: `0.10`

### Judge Layer

Judge ocenia ślepo i literalnie pięć wymiarów:

- `factual_preservation`
- `language_quality`
- `clarity`
- `workplace_usefulness`
- `concision`

Każdy wymiar jest oceniany w skali `1-5`, a finalny judge score jest średnią przeskalowaną do `0-1`.

Rubric live runu znajduje się w `benchmarks/judge_rubric.md`.

### Final Weights

Final score zależy od intencji:

- `surface correction`: `70% deterministic` + `30% judge`
- `style rewrite`: `40% deterministic` + `60% judge`
- `full polish`: `40% deterministic` + `60% judge`

## Fairness Rules

- Oceniane są literalne outputy systemów.
- Nie czyścimy ręcznie persony, refleksji, powitań ani komentarzy Jana.
- W widoku diagnostycznym normalizacja jest jawna i techniczna:
  - dla `Jan` wycinane są znane wrappery i sekcje raportowe
  - dla `raw Bielik` i `GPT-5.4` normalizacja jest prawie no-op poza lekkim cleanupem markdownu
- Raport ma odpowiedzieć nie tylko na pytanie kto wygrał, ale przede wszystkim gdzie Jan pomaga i gdzie szkodzi.

## Artifacts

Live run zapisuje artefakty do `_bmad-output/benchmarks/<timestamp>/`:

- `metadata.json`
- `cases.json`
- `results.json`
- `summary.json`
- `report.md`

`summary.json` i `report.md` zawierają oba widoki: literalny i diagnostyczny.

## Commands

CI-safe walidacja harnessu:

```bash
.venv/bin/python scripts/test_benchmark_harness.py
```

Live pilot:

```bash
.venv/bin/python scripts/run_workplace_benchmark.py
```

Wymagania do live runu:

- działający klucz NVIDIA dla Bielika
- `OPENAI_API_KEY`

## Interpretation Limits

- To pilot na `15` przypadkach.
- Wyniki są użyteczne do wykrywania trendów produktowych i do decyzji o dalszym tuningu.
- Wyniki nie powinny być używane jako ogólne twierdzenie o przewadze jednego systemu na całej klasie zadań.
