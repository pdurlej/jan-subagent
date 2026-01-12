"""
Przykłady użycia subagenta Jan - testy lokalne bez MCP
Demonstracja różnych narzędzi Jana Kochanowskiego
"""

import os
import sys

# Dodaj katalog nadrzędny do Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from jan.kochanowski_quotes import KochanowskiPersona
from jan.system_prompts import get_system_prompt


def example_1_greeting():
    """Przykład 1: Powitanie Jana Kochanowskiego"""
    print("=" * 80)
    print("PRZYKŁAD 1: Powitanie Jana Kochanowskiego")
    print("=" * 80)
    print()

    greeting = KochanowskiPersona.get_greeting()
    print(f"Powitanie: {greeting}")
    print()


def example_2_farewell():
    """Przykład 2: Pożegnanie Jana Kochanowskiego"""
    print("=" * 80)
    print("PRZYKŁAD 2: Pożegnanie Jana Kochanowskiego")
    print("=" * 80)
    print()

    farewell = KochanowskiPersona.get_farewell()
    print(f"Pożegnanie: {farewell}")
    print()


def example_3_reflection():
    """Przykład 3: Refleksje językowe"""
    print("=" * 80)
    print("PRZYKŁAD 3: Refleksje językowe")
    print("=" * 80)
    print()

    print("Refleksja o ortografii:")
    print(f"  {KochanowskiPersona.get_reflection('orthography')}")
    print()

    print("Refleksja o gramatyce:")
    print(f"  {KochanowskiPersona.get_reflection('grammar')}")
    print()

    print("Refleksja o stylu:")
    print(f"  {KochanowskiPersona.get_reflection('style')}")
    print()


def example_4_full_message():
    """Przykład 4: Kompletna wiadomość z osobowością"""
    print("=" * 80)
    print("PRZYKŁAD 4: Kompletna wiadomość z osobowością")
    print("=" * 80)
    print()

    message = "Poprawiłem twoje słowa zgodnie z zasadami polskiego piśmiennictwa."

    full_message = KochanowskiPersona.format_with_personality(
        message=message, include_greeting=True, include_farewell=True
    )

    print(full_message)
    print()


def example_5_language_quotes():
    """Przykład 5: Cytaty o języku polskim"""
    print("=" * 80)
    print("PRZYKŁAD 5: Cytaty o języku polskim")
    print("=" * 80)
    print()

    print("Losowe cytaty:")
    for i in range(3):
        quote = KochanowskiPersona.get_language_quote()
        print(f"  {i + 1}. {quote}")
    print()


def example_6_system_prompts():
    """Przykład 6: System prompty dla Bielika"""
    print("=" * 80)
    print("PRZYKŁAD 6: System prompty dla Bielika")
    print("=" * 80)
    print()

    print("Dostępne prompty:")
    prompt_types = [
        "main",
        "orthography",
        "punctuation",
        "grammar",
        "style",
        "comprehensive",
    ]
    for prompt_type in prompt_types:
        prompt = get_system_prompt(prompt_type)
        print(f"\n--- {prompt_type.upper()} ---")
        print(prompt[:200] + "...")
    print()


def example_7_all_quotes():
    """Przykład 7: Kategorie cytatów"""
    print("=" * 80)
    print("PRZYKŁAD 7: Kategorie cytatów")
    print("=" * 80)
    print()

    from jan.kochanowski_quotes import QUOTES_BY_THEME

    for theme, quotes in QUOTES_BY_THEME.items():
        print(f"\n--- {theme.upper()} ({len(quotes)} cytatów) ---")
        for i, quote in enumerate(quotes[:2], 1):  # Pokaż pierwsze 2
            print(f"  {i}. {quote}")
    print()


def main():
    """Uruchamia wszystkie przykłady"""
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "PRZYKŁADY SUBAGENTA JAN" + " " * 36 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    # Uruchom przykłady
    example_1_greeting()
    example_2_farewell()
    example_3_reflection()
    example_4_full_message()
    example_5_language_quotes()
    example_7_all_quotes()

    print()
    print("=" * 80)
    print("KONIEC PRZYKŁADÓW")
    print("=" * 80)
    print()
    print("Aby przetestować z API, ustaw NVIDIA_API_KEY w pliku .env")
    print("i uruchom: python jan/jan_subagent.py")


if __name__ == "__main__":
    main()
