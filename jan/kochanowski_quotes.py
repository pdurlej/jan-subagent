"""
Cytaty Jana Kochanowskiego do użytku w subagencie MCP 'jan'
Zbiór cytatów, powitań, pożegnań i refleksji w stylu Kochanowskiego.
"""

from typing import List, Dict
import random


# Powitania w stylu Jana Kochanowskiego
GREETINGS: List[str] = [
    "Niech Bóg wam błogosławi. Czym mogę służyć w sprawie języka ojczystego?",
    "Zdrowi bądźcie, miłościwi. Przybywam by pomóc w kunszcie piśmiennictwa polskiego.",
    "Niech wam się wiedzie w mowie polskiej. Jakie kłopoty macie ze słowami?",
    "Niechaj Bóg strzeże wasze pióra. O co proszę mistrza korekty?",
    "Cóż to za piękny język polski! W czym mogę go dopomóc do doskonałości?",
]

# Pożegnania w stylu Jana Kochanowskiego
FAREWELLS: List[str] = [
    "Niechaj Bóg strzeże wasze pióra i myśli. Do zobaczenia w innej godzinie.",
    "Niech wasza mowa zawsze będzie czysta jak źródło polskiej wieśniaczki. Póki co.",
    "Odejdę, lecz wasz język w dobrych rękach zostaje. Niech Bóg was prowadzi.",
    "Słowa są jak diamenty - szanujcie je. Do usłyszenia, miłośnicy mowy.",
    "Mowa polska to skarb narodu. Niech go chronicie i rozwijacie. Do następnej rozmowy.",
]

# Cytaty o języku polskim i piśmiennictwie
LANGUAGE_QUOTES: List[str] = [
    "Mowa polska nie jest licha, lecz piękna, miła i do nauk zdolna.",
    "Kto języka swego nie szanuje, ten samego siebie gardzi.",
    "Słowa są lustrą duszy ludzkiej.",
    "Człowiek jest stworzony do mówienia, jak ptak do latania.",
    "Mowa jest ozdobą człowieka.",
    "Pisze się po polsku tak, jak się myśli po polsku.",
    "Język ojczysty to skarb, który trzeba czcić i pielęgnować.",
]

# Cytaty do refleksji po korekcie
CORRECTION_REFLECTIONS: List[str] = [
    "I tak się pisze w narodzie polskim, co jest piękniejsze niż w obcych językach.",
    "Słowa poprawione są jak polerowany diament - piękniej lśnią.",
    "Mowa polska ma swoje prawa, które trzeba szanować.",
    "Tak uczyli mistrzowie polskiego piśmiennictwa.",
    "W języku polskim piękno tkwi w prostocie i klarowności.",
    "Każde słowo ma swój ciężar i znaczenie - niech będą one odpowiednie.",
]

# Cytaty o błędach językowych
ERROR_QUOTES: List[str] = [
    "Czasem człowiek błądzi, lecz mądry człowiek z błędu się uczy.",
    "Nikt nie jest nieomylny, nawet w mowie ojczystej.",
    "Błędy w mowie są jak kamienie na drodze - trzeba je usunąć.",
    "Nie wstydź się błędu, lecz go napraw - to znak mądrości.",
    "Język polski jest skomplikowany, lecz piękny - warto się go uczyć.",
]

# Cytaty o gramatyce
GRAMMAR_QUOTES: List[str] = [
    "Gramatyka to fundament, na którym budujemy piękne zdania.",
    "Kto gramatykę zna, ten mawia jak pan.",
    "Bez gramatyki mowa jest jak dom bez fundamentu.",
    "Zasady języka nie są pętlą, lecz drogowskazem do piękna.",
    "Gramatyka to muzyka języka - trzeba ją zrozumieć, by pięknie grać.",
]

# Cytaty o ortografii
ORTHOGRAPHY_QUOTES: List[str] = [
    "Ortografia to straż czystości języka.",
    "Jedno 'ó' w wrong miejscu, a sens zdania inny bywa.",
    "Każda litera ma swoją wartość - niech one będą na swoim miejscu.",
    "Pisz tak, jak mówisz, ale pamiętaj o pisowni polskiej.",
    "Wielkie litery to szacunek dla imion własnych i nazw.",
]

# Cytaty o interpunkcji
PUNCTUATION_QUOTES: List[str] = [
    "Znaki przystankowe to tchnienie mowy - muszą być w odpowiednich miejscach.",
    "Przecinek to nieozdobnik, lecz znak zrozumienia.",
    "Kropka kończy myśl, średnik łączy je, dwukropek zapowiada nowe.",
    "Interpunkcja to muzyka tekstu - niech gra harmonijnie.",
    "Bez znaków przystankowych zdania byłyby jak rzeka bez brzegów.",
]

# Cytaty o stylu
STYLE_QUOTES: List[str] = [
    "Styl to człowiek - każdy ma swój własny, piękny styl.",
    "Prostota jest najwyższą formą elegancji w mowie.",
    "Piękny styl nie wymyśla, lecz wybiera najlepsze słowa.",
    "Słowa powinny być odpowiednie do myśli, a myśli do słów.",
    "Mowa powinna być klarowna jak źródło górskie.",
]


class KochanowskiPersona:
    """Persona Jana Kochanowskiego z cytatami i stylizacją"""

    @staticmethod
    def get_greeting() -> str:
        """Losowe powitanie w stylu Kochanowskiego"""
        return random.choice(GREETINGS)

    @staticmethod
    def get_farewell() -> str:
        """Losowe pożegnanie w stylu Kochanowskiego"""
        return random.choice(FAREWELLS)

    @staticmethod
    def get_reflection(correction_type: str) -> str:
        """
        Losowa refleksja po korekcie

        Args:
            correction_type: Typ korekty (orthography, punctuation, grammar, style)

        Returns:
            Odpowiedni cytat/refleksja
        """
        reflection_map = {
            "orthography": ORTHOGRAPHY_QUOTES,
            "punctuation": PUNCTUATION_QUOTES,
            "grammar": GRAMMAR_QUOTES,
            "style": STYLE_QUOTES,
            "general": CORRECTION_REFLECTIONS,
            "error": ERROR_QUOTES,
        }
        quotes = reflection_map.get(correction_type, LANGUAGE_QUOTES)
        return random.choice(quotes)

    @staticmethod
    def get_language_quote() -> str:
        """Losowy cytat o języku polskim"""
        return random.choice(LANGUAGE_QUOTES)

    @staticmethod
    def format_with_personality(
        message: str, include_greeting: bool = False, include_farewell: bool = False
    ) -> str:
        """
        Formatuje wiadomość z osobowością Kochanowskiego

        Args:
            message: Główna wiadomość
            include_greeting: Czy dodać powitanie
            include_farewell: Czy dodać pożegnanie

        Returns:
            Sformatowana wiadomość
        """
        parts = []
        if include_greeting:
            parts.append(f"{KochanowskiPersona.get_greeting()}\n\n")
        parts.append(message)
        if include_farewell:
            parts.append(f"\n\n{KochanowskiPersona.get_farewell()}")
        return "".join(parts)


# Mapa tematyczna cytatów
QUOTES_BY_THEME: Dict[str, List[str]] = {
    "powitania": GREETINGS,
    "pożegnania": FAREWELLS,
    "język": LANGUAGE_QUOTES,
    "korekta": CORRECTION_REFLECTIONS,
    "błędy": ERROR_QUOTES,
    "gramatyka": GRAMMAR_QUOTES,
    "ortografia": ORTHOGRAPHY_QUOTES,
    "interpunkcja": PUNCTUATION_QUOTES,
    "styl": STYLE_QUOTES,
}


if __name__ == "__main__":
    # Testowanie modułu
    print("=== Powitanie ===")
    print(KochanowskiPersona.get_greeting())
    print()

    print("=== Pożegnanie ===")
    print(KochanowskiPersona.get_farewell())
    print()

    print("=== Refleksja o ortografii ===")
    print(KochanowskiPersona.get_reflection("orthography"))
    print()

    print("=== Kompletna wiadomość ===")
    full_message = KochanowskiPersona.format_with_personality(
        "Poprawiłem twoje słowa zgodnie z zasadami polskiego piśmiennictwa.",
        include_greeting=True,
        include_farewell=True,
    )
    print(full_message)
