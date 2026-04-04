# Migracja do v3.0.0

## Co się zmieniło

Jan zmienia główny surface MCP.

W `2.x` główne były ogólne tools korektorskie.
W `3.0.0` główne są workflowy repo-native dla tech teamów.

## Nowy primary surface

- `write_pr_description`
- `compose_release_notes`
- `rewrite_issue`
- `write_rollout_note`

## Legacy map

| Stare narzędzie | Nowy workflow | Kiedy używać |
| --- | --- | --- |
| `correct_orthography` | `write_pr_description` lub `rewrite_issue` | Gdy tekst jest częścią artefaktu repo-native, nie samodzielnym ćwiczeniem korektorskim |
| `correct_punctuation` | `write_pr_description` lub `compose_release_notes` | Gdy potrzebujesz gotowego artefaktu, nie tylko poprawy znaków |
| `improve_style` | `compose_release_notes` lub `write_rollout_note` | Gdy styl ma wynikać z audience packa i template’u |
| `comprehensive_correction` | dowolny named workflow | Gdy zależy Ci na source context, nie na ogólnej korekcie |
| `verify_grammar` | `response_mode="review"` + trust layer | Gdy chcesz ocenić gotowy artefakt pod kątem jakości i zgodności |
| `check_text_quality` | `response_mode="review"` + validator report | Gdy potrzebujesz quality gate, nie tylko oceny ad hoc |

## Response mode

Nowe workflowy wspierają:

- `final` -> tylko gotowy tekst
- `review` -> JSON z:
  - `final_text`
  - `source_trace`
  - `validator_report`

## jan.yml

Jeśli chcesz używać Jana repo-native, dodaj lub utrzymuj `jan.yml` w repo.
To tam trzymasz:

- templates
- glossary
- do-not-translate
- audience packs
- validation policy

## Co zostaje

- legacy tools nadal działają
- `greet_jan`, `farewell_jan` i `get_language_advice` nadal istnieją
- Bielik i runtime MCP pozostają tą samą warstwą wykonawczą

## Co przestaje być promowane

- ogólne „stylizowanie tekstu” jako główny value prop
- persona jako domyślny UX
- szeroki benchmark workplace writing jako north star produktu
