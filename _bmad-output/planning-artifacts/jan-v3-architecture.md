# Jan v3.0.0 Architecture

## Core modules

- `jan.policy`
  - ładuje `jan.yml`
  - daje templates, audience packs, glossary i validation defaults
- `jan.source_context`
  - wspólne modele kontekstu
- `jan.source_adapters`
  - local git
  - GitHub REST
  - Jira REST
- `jan.workflow_engine`
  - buduje context bundle
  - składa prompt workflowu
  - odpala model
  - waliduje wynik
  - składa review envelope
- `jan.jan_subagent_opencode`
  - wystawia MCP surface
  - utrzymuje legacy tools i nowe repo-native workflows
- `jan.delivery_benchmark`
  - benchmark v2 dla repo-native workflows
- `jan.workplace_benchmark`
  - regression suite dla poprzedniego workplace pilotu

## Request flow

1. MCP tool przyjmuje workflow args.
2. `workflow_engine` ładuje `jan.yml`.
3. `source_adapters` budują bundle z:
   - raw notes
   - local git
   - GitHub
   - Jira
4. `system_prompts` budują workflow-specific contract.
5. Bielik generuje final text albo review JSON.
6. trust layer waliduje output.
7. Tool zwraca:
   - `final` -> paste-ready tekst
   - `review` -> `final_text` + `source_trace` + `validator_report`

## Trust layer

Walidacja jest programowa, nie tylko promptowa:

- fact preservation
- no-new-facts
- template compliance
- glossary adherence
- audience-policy compliance

To nie jest pełny formal verifier. To heurystyczna warstwa zaufania do codziennego workflowu.

## Context precedence

1. explicit args użytkownika
2. source adapters
3. `jan.yml`
4. model generation

Brak tokenów GitHub/Jira nie tworzy synthetic contextu. System degraduje się do dostępnych źródeł i zapisuje warning.

## Benchmark architecture

- benchmark v1 zostaje jako regression guardrail
- benchmark v2 mierzy workflowy na lane’ach:
  - `text_only`
  - `structured_context`
  - `policy_pack`
- benchmark v2 skupia się na KPI produktu, nie na judge-first writing quality

## Rollout contract

- `v3.0.0` jest hard pivotem kategorii produktu
- README i docs promują named workflows
- legacy tools pozostają tylko dla kompatybilności
- persona Jana zostaje jako brand skin i opt-in delight pack
