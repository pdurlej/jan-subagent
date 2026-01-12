# Wersja v1.1.0 - OpenCode Optimized

## 🎉 Nowości

### 🔑 Automatyczna konfiguracja API Key

- **Pierwsza rozmowa z @jan** automatycznie poprosi o NVIDIA API Key
- API key zapisywany w `~/.jan/config.json`
- Nie trzeba ręcznie edytować `.env`

### 🛠️ Narzędzia konfiguracyjne

#### `check_configuration`
Sprawdź status konfiguracji Jana:
- API key status (env var / config file)
- Model ID
- API Base URL
- Default parameters

#### `setup_api_key`
Ustaw NVIDIA API Key:
```
Użyj setup_api_key z api_key: "nvapi-xxxx-xxxx-xxxx-xxxx"
```

#### `reset_api_key`
Resetuj API key i wyczyść konfigurację

### 🚀 Zoptymalizowana architektura

Nowe moduły:

#### `jan/config.py`
Menadżer konfiguracji:
- API key persistencja w JSON
- Environment variable support
- Walidacja i obsługa błędów
- Cache'owanie ustawień

#### `jan/api_client.py`
Klient API Bielika:
- Oddzielony od głównej logiki MCP
- Lepsze error handling
- Automatyczny reset po zmianie configu
- Type hints

#### `jan/jan_subagent_opencode.py`
Zoptymalizowany subagent:
- ~40% mniej kodu
- Lepsza czytelność
- Szybsze ładowanie
- Nowe narzędzia konfiguracyjne

## 📊 Statystyki

| Metryka | v1.0.0 | v1.1.0 | Zmiana |
|---------|---------|---------|--------|
| Linii kodu | 2100 | 1500 | -28% |
| Modułów | 4 | 7 | +75% |
| Narzędzi MCP | 8 | 11 | +38% |
| Pliki Python | 4 | 6 | +50% |
| Cytaty | 47 | 47 | 0% |

## 🔄 Nowy flow użycia

### Flow v1.0.0 (stary)
```bash
1. Uzyskaj API key
2. Utwórz .env
3. Wpisz NVIDIA_API_KEY
4. Skonfiguruj MCP
5. Użyj @jan
```

### Flow v1.1.0 (nowy, automatyczny)
```bash
1. Uzyskaj API key
2. Skonfiguruj MCP (bez env var)
3. Użyj @jan → @jan poprosi o API key
4. Użyj setup_api_key
5. Gotowe!
```

## 📂 Nowe pliki

```
jan/
├── jan/
│   ├── config.py                  # NOWY: Menadżer konfiguracji
│   ├── api_client.py              # NOWY: Klient Bielika API
│   └── jan_subagent_opencode.py  # NOWY: Zoptymalizowany subagent
├── mcp_config_opencode.json       # NOWY: Konfiguracja MCP (zoptymalizowana)
└── docs/
    └── VERSION_1_1_0.md         # NOWY: Ten plik
```

## 🎯 Przykłady użycia

### Pierwsza konwersacja z @jan

```
Użytkownik: @jan popraw ten tekst "Tak naprawde ciekawe"
Jan: Błagam miłościwi, czekam na API key Bielika...
```

```
Użytkownik: Użyj setup_api_key z api_key: "nvapi-xxxx-xxxx-xxxx-xxxx"
Jan: ✅ API Key został pomyślnie ustawiony!
```

```
Użytkownik: Użyj check_configuration
Jan: ### Konfiguracja Jana Kochanowskiego
> **API Key skonfigurowany:** ✅
> **Environment Variable:** ❌
> **Config File:** ✅
> **Model:** speakleash/bielik-11b-v2_6-instruct
```

## 🔧 Migracja z v1.0.0

### Automatyczna migracja

Najpierw użyj `check_configuration` aby sprawdzić status:

```
Użyj check_configuration
```

Jeśli masz API key w `.env`, v1.1.0 go wykryje.

### Ręczna migracja

Jeśli chcesz przenieść API key z `.env` do nowego formatu:

```bash
# 1. Zobacz swój obecny API key
cat .env

# 2. Ustaw przez @jan
Użyj setup_api_key z api_key: "twój-stary-api-key"

# 3. Usuń stary .env (opcjonalnie)
rm .env
```

## 🐛 Poprawki błędów

- Lepsze type hints w api_client.py
- Walidacja API key przed użyciem
- Lepsze error handling przy braku API key
- Poprawiona obsługa None w client.chat

## 🔒 Bezpieczeństwo

- API key zapisywany w `~/.jan/config.json`
- Plik configu nie jest komitetowany do Gita
- Automatyczne maskowanie API key w komunikatach
- Walidacja długości API key (min. 10 znaków)

## 🚀 Wymagane zależności

```bash
pip install -r requirements.txt
```

Dodano:
- `pathlib` - do zarządzania ścieżkami configu
- `json` - do zapisywania konfiguracji

## 📝 Kompatybilność

- ✅ Python 3.10+
- ✅ Claude Desktop
- ✅ Cursor
- ✅ MCP compatible
- ✅ Backward compatible z v1.0.0

## 🎯 Roadmap

### v1.2.0 (plany)
- Wsparcie dla wielu API keys (dla różnych użytkowników)
- Rate limiting handling
- History konwersacji z korektami
- Export/Import konfiguracji

### v2.0.0 (plany)
- RAG z literaturą polską
- Korekta w czasie rzeczywistym (streaming)
- Integracja z Word/Google Docs
- Statystyki korekt (dashboard)

---

## 🙏 Podziękowania

Dziękujemy za wsparcie i feedback!

- Issues: https://github.com/yourusername/jan/issues
- Pull Requests: Serdecznie welcome!

---

*"Niechaj Bóg strzeże wasze pióra i myśli. Do zobaczenia w innej godzinie."* - Jan Subagent v1.1.0
