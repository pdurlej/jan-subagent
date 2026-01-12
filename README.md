# 📜 Jan Subagent - MCP Subagent Jana Kochanowskiego

![Version](https://img.shields.io/badge/version-1.1.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

> *"Niechaj Bóg strzeże wasze pióra i myśli"* - Jan Kochanowski

Subagent MCP z osobowością Jana Kochanowskiego, poety renesansowego, do kompleksowej korekty języka polskiego. Używa modelu **Bielik 11B v2.6 Instruct** od NVIDIA jako eksperta językowego.

## ✨ Nowości w v1.1.0 (OpenCode Optimized)

- 🔑 **Automatyczna konfiguracja API key** - pierwszy raz @jan poprosi o NVIDIA API key
- 💾 **Zapisywanie konfiguracji** - API key zapisywany w `~/.jan/config.json`
- 🚀 **Zoptymalizowana architektura** - mniejsze pliki, szybsze ładowanie
- 🛠️ **Narzędzia konfiguracyjne** - `check_configuration`, `setup_api_key`, `reset_api_key`
- 📦 **Modularny kod** - oddzielone moduły dla łatwiejszego rozwijania

## 🎯 Cechy

- ✨ **Persona Jana Kochanowskiego** - powitania, pożegnania i komentarze w stylu renesansowym
- 🔑 **Integracja z NVIDIA Bielik** - model 11B v2.6 Instruct
- 📝 **Korekta ortografii** - z wyróżnionymi zmianami i wyjaśnieniami
- 🔤 **Korekta interpunkcji** - szczegółowa analiza znaków przystankowych
- 📚 **Weryfikacja gramatyki** - zgodność z polskimi regułami gramatycznymi
- 🎨 **Ulepszanie stylu** - transformacje stylów (elegancki, prosty, poetycki, naukowy)
- 🔄 **Kompleksowa korekta** - pełna analiza tekstu w jednym zapytaniu
- 💡 **Porady językowe** - edukacyjne porady w stylu "Trenów"
- 📊 **Ocena jakości tekstu** - szybka ocena i rekomendacje
- 🔧 **Narzędzia konfiguracyjne** - łatwe zarządzanie API key

## 🚀 Instalacja

### Wymagania

- Python 3.10 lub nowszy
- MCP Client (Claude Desktop, Cursor, inne)
- NVIDIA API Key (uzyskaj na [build.nvidia.com/api-key](https://build.nvidia.com/api-key))

### 🎉 Nowy flow v1.1.0 - Automatyczna konfiguracja!

#### Krok 1: Uzyskaj NVIDIA API Key

1. Otwórz [build.nvidia.com/api-key](https://build.nvidia.com/api-key)
2. Utwórz nowy API key
3. Skopiuj key

#### Krok 2: Zainstaluj zależności

```bash
cd /Users/pd/Developer/jan
pip install -r requirements.txt
```

#### Krok 3: Skonfiguruj MCP

**Claude Desktop (macOS):**
```json
{
  "mcpServers": {
    "jan-kochanowski": {
      "command": "python3",
      "args": ["-m", "jan.jan_subagent_opencode"],
      "cwd": "/Users/pd/Developer/jan",
      "env": {}
    }
  }
}
```

**Cursor:**
Edytuj `~/.cursor/mcp_config.json` z tym samym configiem.

#### Krok 4: Rozpocznij konwersację

Otwórz Claude/Cursor i zacznij konwersację z **@jan**. Przy pierwszym użyciu, **@jan** poprosi Cię o API key:

```
> @jan popraw ten tekst
```

**Jan odpowie:**
> Błagam miłościwi, czekam na API key Bielika, by móc pomóc w korekcie. Użyj narzędzia `setup_api_key` aby ustawić klucz.

Następnie ustaw klucz:

```
> Użyj setup_api_key z api_key: "nvapi-xxxx-xxxx-xxxx-xxxx-xxxx-xxxx"
```

**Jan potwierdzi:**
> ✅ **API Key został pomyślnie ustawiony!**

Gotowe! Od teraz **@jan** będzie działał normalnie bez dodatkowej konfiguracji.

### 📋 Stary flow (ręczna konfiguracja)

Jeśli wolisz ręczną konfigurację:

```bash
# 1. Utwórz plik .env
cp .env.example .env

# 2. Edytuj .env i wpisz NVIDIA_API_KEY
# NVIDIA_API_KEY=twój-nvidia-api-key

# 3. Zainstaluj pakiet
pip install -e .
```

### 🔍 Sprawdzanie konfiguracji

Zawsze możesz sprawdzić status konfiguracji:

```
> Użyj check_configuration
```

**Odpowiedź:**
> ### Konfiguracja Jana Kochanowskiego
>
> **API Key skonfigurowany:** ✅
> **Environment Variable:** ✅
> **Config File:** ❌
>
> **Model:** speakleash/bielik-11b-v2_6-instruct
> **API Base:** https://integrate.api.nvidia.com/v1
> **Default Temperature:** 0.3
> **Max Tokens:** 4096

## ⚙️ Konfiguracja MCP

### Claude Desktop (macOS)

Edytuj plik `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "jan-kochanowski": {
      "command": "python3",
      "args": [
        "-m",
        "jan.jan_subagent"
      ],
      "cwd": "/ścieżka/do/jan",
      "env": {
        "NVIDIA_API_KEY": "twój-nvidia-api-key"
      }
    }
  }
}
```

### Cursor

Edytuj `~/.cursor/mcp_config.json` z tym samym configiem co wyżej.

## 📖 Narzędzia MCP

### 📋 Konfiguracja

#### `check_configuration`
Sprawdź konfigurację Jana i status API key.

```python
check_configuration() -> str
```

**Odpowiedź:**
- Status API key (env var / config file)
- Model ID
- API Base URL
- Default parameters

#### `setup_api_key`
Ustaw NVIDIA API Key - użyj przy pierwszej konfiguracji.

```python
setup_api_key(api_key: str) -> str
```

**Przykład użycia przy pierwszej rozmowie:**
```
Użyj setup_api_key z api_key: "nvapi-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

**Odpowiedź Jana:**
> Niech Bóg wam błogosławi. Czym mogę służyć w sprawie języka ojczystego?
>
> ✅ **API Key został pomyślnie ustawiony!**
>
> Lokalizacja: `~/.jan/config.json`
> Model: `speakleash/bielik-11b-v2_6-instruct`
>
> *Słowa poprawione są jak polerowany diament - piękniej lśnią.*
>
> Niechaj Bóg strzeże wasze pióra i myśli. Do zobaczenia w innej godzinie.

#### `reset_api_key`
Resetuj API Key.

```python
reset_api_key() -> str
```

### 📝 Korekta języka

#### `correct_orthography`
Poprawa ortografii tekstu polskiego z komentarzami.

```python
correct_orthography(
    text: str,
    include_greeting: bool = True
) -> str
```

**Przykład:**
```
Użyj correct_orthography z tekstem:
"Tak naprawde ciekawe jest to co pisze."
```

### `correct_punctuation`
Korekta interpunkcji tekstu polskiego.

```python
correct_punctuation(
    text: str,
    include_greeting: bool = True
) -> str
```

### `verify_grammar`
Weryfikacja gramatyki tekstu polskiego.

```python
verify_grammar(
    text: str,
    include_greeting: bool = True
) -> str
```

**Zwraca:**
- `correct`: Czy tekst jest gramatycznie poprawny
- `errors`: Lista błędów z wyjaśnieniami
- `suggestions`: Sugestie poprawek
- `overall_assessment`: Ogólna ocena

### `improve_style`
Ulepszenie stylu tekstu.

```python
improve_style(
    text: str,
    style: str = "elegancki",  # elegancki, prosty, poetycki, naukowy, ulotny
    include_greeting: bool = True
) -> str
```

**Dostępne style:**
- `elegancki` - bogate słownictwo, złożona składnia
- `prosty` - jasny, zrozumiały, bez ozdobników
- `poetycki` - metafory, obrazowanie, rymy
- `naukowy` - precyzyjny, terminologiczny
- `ulotny` - lekki, humorystyczny

### `comprehensive_correction`
Kompleksowa korekta tekstu (wszystko w jednym).

```python
comprehensive_correction(
    text: str,
    mode: str = "standard",  # standard, conservative, aggressive
    include_greeting: bool = True,
    include_farewell: bool = True
) -> str
```

**Mode korekty:**
- `conservative` - tylko ewidentne błędy
- `standard` - błędy + wyraźne ulepszenia
- `aggressive` - pełna korekta + stylizacja

**Zwraca:**
- Raport JSON z ocenami dla: ortografii, interpunkcji, gramatyki, stylu
- Poprawiony tekst
- Ogólną ocenę jakości (0-10)

### `get_language_advice`
Edukacyjna porada językowa.

```python
get_language_advice(
    topic: str,
    include_greeting: bool = True
) -> str
```

**Przykłady tematów:**
- "ó vs u"
- "interpunkcja"
- "gramatyka"
- "styl"
- "frazeologia"

### `check_text_quality`
Szybka ocena jakości tekstu.

```python
check_text_quality(
    text: str,
    include_greeting: bool = False
) -> str
```

### `greet_jan`
Powitanie od Jana Kochanowskiego.

```python
greet_jan(name: str = "miłościw") -> str
```

### `farewell_jan`
Pożegnanie od Jana Kochanowskiego.

```python
farewell_jan() -> str
```

## 💬 Przykłady użycia

### Przykład 1: Prosta korekta ortograficzna

```
Użyj correct_orthography z tekstem:
"Cześć! Napisalem tekst z błedami. Czy jest OK?"
```

**Odpowiedź Jana:**
> Niech Bóg wam błogosławi. Czym mogę służyć w sprawie języka ojczystego?
>
> Poprawiłem twoje słowa zgodnie z zasadami polskiego piśmiennictwa.
>
> *Słowa poprawione są jak polerowany diament - piękniej lśnią.*
>
> Niechaj Bóg strzeże wasze pióra i myśli. Do zobaczenia w innej godzinie.

### Przykład 2: Kompleksowa korekta

```
Użyj comprehensive_correction z tekstem:
"Tak naprawde ciekawe jest to co pisze. Ale czy to jest dobre? Nie wiem."
mode: standard
```

**Odpowiedź Jana:**
> Zdrowi bądźcie, miłościwi. Przybywam by pomóc w kunszcie piśmiennictwa polskiego.
>
> [Raport JSON z wynikami korekty]
>
> *I tak się pisze w narodzie polskim, co jest piękniejsze niż w obcych językach.*
>
> Niech wasza mowa zawsze będzie czysta jak źródło polskiej wieśniaczki. Póki co.

### Przykład 3: Ulepszanie stylu

```
Użyj improve_style z tekstem:
"To jest dobre. Lubię to."
style: elegancki
```

### Przykład 4: Porada językowa

```
Użyj get_language_advice z tematem:
"ó vs u"
```

## 🏗️ Architektura projektu

```
jan/
├── jan/
│   ├── __init__.py              # Inicjalizacja pakietu (zoptymalizowana)
│   ├── jan_subagent.py          # Główny plik subagenta (oryginalny)
│   ├── jan_subagent_opencode.py # Zoptymalizowana wersja pod OpenCode
│   ├── kochanowski_quotes.py    # Cytaty i persona Kochanowskiego
│   ├── system_prompts.py        # System prompty dla Bielika
│   ├── config.py               # Menadżer konfiguracji (NOWY v1.1.0)
│   └── api_client.py           # Klient Bielika API (NOWY v1.1.0)
├── src/                         # Dodatkowe źródła
├── tests/                       # Testy jednostkowe
├── examples/                    # Przykłady użycia
├── docs/                        # Dokumentacja
├── requirements.txt             # Zależności Pythona
├── .env.example                # Przykładowe zmienne środowiskowe
├── mcp_config.json             # Konfiguracja MCP (oryginalna)
├── mcp_config_opencode.json    # Konfiguracja MCP (zoptymalizowana)
├── setup.py                    # Setup script
├── LICENSE                     # Licencja MIT
└── README.md                   # Ten plik
```

### Nowe moduły v1.1.0

#### `jan/config.py`
Menadżer konfiguracji Jana - zarządzanie API key, cache'owanie, persistencja.

- API key zapisywany w `~/.jan/config.json`
- Automatyczne sprawdzanie environment variables
- Metody do ustawiania/resetowania API key
- Podsumowanie konfiguracji

#### `jan/api_client.py`
Klient do komunikacji z NVIDIA Bielik API.

- Oddzielony od głównej logiki MCP
- Walidacja API key przed zapytaniami
- Obsługa błędów połączenia
- Automatyczny reset po zmianie configu

#### `jan/jan_subagent_opencode.py`
Zoptymalizowana wersja subagenta pod OpenCode.

- Krótszy kod (~40% mniej linii)
- Lepsza czytelność i modularność
- Nowe narzędzia konfiguracyjne
- Szybsze ładowanie

## 🎨 Persona Jana Kochanowskiego

Subagent 'jan' zachowuje się jak polski poeta renesansowy Jan Kochanowski (1530-1584), autor "Pieśni", "Trenów" i "Fraszek".

### Cechy persony:

- **Powitania i pożegnania** w stylu renesansowym
- **Słownictwo** bogate, metaforyczne, klasyczne
- **Cytaty** z literatury polskiej i samego Kochanowskiego
- **Refleksje** edukacyjne, inspirowane "Trenami"
- **Formy grzecznościowe** (miłościwi, panie, pani)
- **Stylizacja** humanistyczna, humanistyczna troska o język

### Przykłady cytatów:

> *"Mowa polska nie jest licha, lecz piękna, miła i do nauk zdolna."*
>
> *"Słowa są lustrą duszy ludzkiej."*
>
> *"Człowiek jest stworzony do mówienia, jak ptak do latania."*

## 🔧 Konfiguracja

### Zmienne środowiskowe

Utwórz plik `.env` w głównym katalogu projektu:

```bash
# NVIDIA API Key (wymagane)
NVIDIA_API_KEY=twój-nvidia-api-key

# Opcjonalne
BIELIK_MODEL_ID=speakleash/bielik-11b-v2_6-instruct
NVIDIA_API_BASE=https://integrate.api.nvidia.com/v1
LOG_LEVEL=info
DEFAULT_CORRECTION_TEMPERATURE=0.3
DEFAULT_MAX_TOKENS=4096
```

### Uzyskanie NVIDIA API Key

1. Otwórz [build.nvidia.com](https://build.nvidia.com/)
2. Zarejestruj się lub zaloguj
3. Przejdź do [API Keys](https://build.nvidia.com/api-key)
4. Utwórz nowy API key
5. Skopiuj i wklej do pliku `.env`

## 🧪 Testowanie

### Uruchomienie testów

```bash
# Testy jednostkowe
python -m pytest tests/

# Testy integracyjne (wymaga NVIDIA_API_KEY)
python -m pytest tests/integration/

# Testowanie persony Kochanowskiego
python jan/kochanowski_quotes.py
```

### Testowanie narzędzia

```python
from jan.jan_subagent import greet_jan

# Powitanie
print(greet_jan())

# Korekta ortograficzna
from jan.jan_subagent import correct_orthography
result = correct_orthography(
    "Cześć! Napisalem tekst.",
    include_greeting=False
)
print(result)
```

## 📚 Dokumentacja API

### BielikClient

Główna klasa do komunikacji z NVIDIA Bielik API.

```python
from jan.jan_subagent import BielikClient

client = BielikClient()
response = client.call_bielik(
    system_prompt="Jesteś ekspertem...",
    user_message="Popraw tekst...",
    temperature=0.3,
    max_tokens=4096
)
```

### KochanowskiPersona

Klasa persony Jana Kochanowskiego z cytatami i stylizacją.

```python
from jan.kochanowski_quotes import KochanowskiPersona

# Losowe powitanie
greeting = KochanowskiPersona.get_greeting()

# Losowa refleksja
reflection = KochanowskiPersona.get_reflection("orthography")

# Formatowanie z osobowością
message = KochanowskiPersona.format_with_personality(
    "Poprawiłem twój tekst.",
    include_greeting=True,
    include_farewell=True
)
```

## 🤝 Współpraca

Contributions are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 Licencja

MIT License - patrz plik [LICENSE](LICENSE) dla szczegółów.

## 🙏 Podziękowania

- **NVIDIA** za model Bielik 11B i API
- **Speakleash** za model Bielik wyspecjalizowany w języku polskim
- **Jan Kochanowski** za mistrzostwo w polskim piśmiennictwie

## 📞 Kontakt

- Issues: [GitHub Issues](https://github.com/yourusername/jan/issues)
- Email: your@email.com

---

*"Niechaj Bóg strzeże wasze pióra i myśli. Do zobaczenia w innej godzinie."* - Jan Subagent
