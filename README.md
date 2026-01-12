# 📜 Jan Subagent - MCP Subagent Jana Kochanowskiego

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

> *"Niechaj Bóg strzeże wasze pióra i myśli"* - Jan Kochanowski

Subagent MCP z osobowością Jana Kochanowskiego, poety renesansowego, do kompleksowej korekty języka polskiego. Używa modelu **Bielik 11B v2.6 Instruct** od NVIDIA jako eksperta językowego.

## 🎯 Cechy

- ✨ **Persona Jana Kochanowskiego** - powitania, pożegnania i komentarze w stylu renesansowym
- 📝 **Korekta ortografii** - z wyróżnionymi zmianami i wyjaśnieniami
- 🔤 **Korekta interpunkcji** - szczegółowa analiza znaków przystankowych
- 📚 **Weryfikacja gramatyki** - zgodność z polskimi regułami gramatycznymi
- 🎨 **Ulepszanie stylu** - transformacje stylów (elegancki, prosty, poetycki, naukowy)
- 🔄 **Kompleksowa korekta** - pełna analiza tekstu w jednym zapytaniu
- 💡 **Porady językowe** - edukacyjne porady w stylu "Trenów"
- 📊 **Ocena jakości tekstu** - szybka ocena i rekomendacje

## 🚀 Instalacja

### Wymagania

- Python 3.10 lub nowszy
- NVIDIA API Key (uzyskaj na [build.nvidia.com](https://build.nvidia.com/api-key))
- MCP Client (Claude Desktop, Cursor, inne)

### Kroki instalacji

```bash
# 1. Zainstaluj zależności
pip install -r requirements.txt

# 2. Skopiuj i uzupełnij plik .env
cp .env.example .env
# Edytuj .env i wpisz swój NVIDIA_API_KEY

# 3. Zainstaluj pakiet w trybie development
pip install -e .
```

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

### `correct_orthography`
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
│   ├── __init__.py              # Inicjalizacja pakietu
│   ├── jan_subagent.py          # Główny plik subagenta z narzędziami MCP
│   ├── kochanowski_quotes.py    # Cytaty i persona Kochanowskiego
│   └── system_prompts.py        # System prompty dla Bielika
├── src/                         # Dodatkowe źródła
├── tests/                       # Testy jednostkowe
├── examples/                    # Przykłady użycia
├── docs/                        # Dokumentacja
├── requirements.txt             # Zależności Pythona
├── .env.example                # Przykładowe zmienne środowiskowe
├── mcp_config.json             # Konfiguracja MCP
└── README.md                   # Ten plik
```

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
