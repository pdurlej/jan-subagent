# Wersja v1.1.0 - archiwalna nota wydania

Ta nota opisuje historyczne wydanie `1.1.0`, które wprowadziło runtime `jan.jan_subagent_opencode` oraz konfigurację przez `~/.jan/config.json`.

Aktualne wydanie kanoniczne to `2.0.0`:

- bieżąca nota: [docs/VERSION_2_0_0.md](/Users/pd/Developer/jan/docs/VERSION_2_0_0.md)
- bieżący runtime: `jan.jan_subagent_opencode`
- legacy `jan.jan_subagent` zostało usunięte

## Co wniosło 1.1.0

- automatyczną konfigurację API key przez `setup_api_key`
- moduły `config.py`, `api_client.py` i `jan_subagent_opencode.py`
- lazy import `jan.mcp`
- uporządkowanie integracji z modelem `speakleash/bielik-11b-v2.6-instruct`

## Co zmieniło się później w 2.0.0

- usunięto legacy entrypoint `jan.jan_subagent`
- uproszczono surface repo do jednego sample configu `mcp_config.json`
- runtime przestał emitować banner na `stdout`
- dodano onboarding BMAD, CI i release hygiene pod aktualny stan repo
