"""
Unit tests dla Jan Subagent
"""

import pytest
import sys
import os

# Dodaj katalog nadrzędny do Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from jan.kochanowski_quotes import KochanowskiPersona, QUOTES_BY_THEME
from jan.system_prompts import get_system_prompt, SYSTEM_PROMPTS


class TestKochanowskiPersona:
    """Testy dla klasy KochanowskiPersona"""

    def test_get_greeting(self):
        """Test powitania"""
        greeting = KochanowskiPersona.get_greeting()
        assert greeting is not None
        assert isinstance(greeting, str)
        assert len(greeting) > 0
        assert "Bóg" in greeting or "Zdrowi" in greeting or "Niech" in greeting

    def test_get_farewell(self):
        """Test pożegnania"""
        farewell = KochanowskiPersona.get_farewell()
        assert farewell is not None
        assert isinstance(farewell, str)
        assert len(farewell) > 0
        assert "Bóg" in farewell or "pióra" in farewell or "mowa" in farewell

    def test_get_reflection(self):
        """Test refleksji dla różnych typów korekty"""
        correction_types = [
            "orthography",
            "punctuation",
            "grammar",
            "style",
            "general",
            "error",
        ]

        for correction_type in correction_types:
            reflection = KochanowskiPersona.get_reflection(correction_type)
            assert reflection is not None
            assert isinstance(reflection, str)
            assert len(reflection) > 0

    def test_get_language_quote(self):
        """Test cytatów o języku polskim"""
        quote = KochanowskiPersona.get_language_quote()
        assert quote is not None
        assert isinstance(quote, str)
        assert len(quote) > 0

    def test_format_with_personality(self):
        """Test formatowania z osobowością"""
        message = "Testowa wiadomość"

        # Tylko z powitaniem
        result = KochanowskiPersona.format_with_personality(
            message, include_greeting=True, include_farewell=False
        )
        assert message in result

        # Tylko z pożegnaniem
        result = KochanowskiPersona.format_with_personality(
            message, include_greeting=False, include_farewell=True
        )
        assert message in result

        # Kompletna wiadomość
        result = KochanowskiPersona.format_with_personality(
            message, include_greeting=True, include_farewell=True
        )
        assert message in result
        assert "Bóg" in result or "Zdrowi" in result  # powitanie
        assert "pióra" in result or "mowa" in result  # pożegnanie


class TestSystemPrompts:
    """Testy dla system prompts"""

    def test_get_system_prompt_default(self):
        """Test pobierania domyślnego system prompt"""
        prompt = get_system_prompt()
        assert prompt is not None
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "Jan Kochanowski" in prompt

    def test_get_system_prompt_types(self):
        """Test pobierania różnych typów system prompts"""
        prompt_types = [
            "main",
            "orthography",
            "punctuation",
            "grammar",
            "style",
            "comprehensive",
            "advice",
        ]

        for prompt_type in prompt_types:
            prompt = get_system_prompt(prompt_type)
            assert prompt is not None
            assert isinstance(prompt, str)
            assert len(prompt) > 0
            assert "Kochanowski" in prompt or "ekspert" in prompt.lower()

    def test_system_prompts_dict(self):
        """Test słownika system prompts"""
        assert "main" in SYSTEM_PROMPTS
        assert "orthography" in SYSTEM_PROMPTS
        assert "punctuation" in SYSTEM_PROMPTS
        assert "grammar" in SYSTEM_PROMPTS
        assert "style" in SYSTEM_PROMPTS
        assert "comprehensive" in SYSTEM_PROMPTS
        assert "advice" in SYSTEM_PROMPTS


class TestQuotesStructure:
    """Testy struktury cytatów"""

    def test_quotes_by_theme_exists(self):
        """Test czy QUOTES_BY_THEME istnieje i jest słownikiem"""
        assert isinstance(QUOTES_BY_THEME, dict)
        assert len(QUOTES_BY_THEME) > 0

    def test_quotes_themes(self):
        """Test czy wszystkie tematy mają listy cytatów"""
        expected_themes = [
            "powitania",
            "pożegnania",
            "język",
            "korekta",
            "błędy",
            "gramatyka",
            "ortografia",
            "interpunkcja",
            "styl",
        ]

        for theme in expected_themes:
            assert theme in QUOTES_BY_THEME
            quotes = QUOTES_BY_THEME[theme]
            assert isinstance(quotes, list)
            assert len(quotes) > 0

    def test_quotes_content(self):
        """Test czy cytaty są poprawnymi stringami"""
        for theme, quotes in QUOTES_BY_THEME.items():
            for quote in quotes:
                assert isinstance(quote, str)
                assert len(quote) > 0


def test_imports():
    """Test czy można importować główne elementy"""
    from jan import mcp, KochanowskiPersona, get_system_prompt

    assert KochanowskiPersona is not None
    assert get_system_prompt is not None
    # mcp może być None jeśli nie zainstalowano zależności
    # assert mcp is not None


if __name__ == "__main__":
    # Uruchom testy
    pytest.main([__file__, "-v"])
