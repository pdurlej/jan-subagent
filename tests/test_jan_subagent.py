"""
Unit tests dla Jan Subagent
"""

import json
import os
import sys
from pathlib import Path

import pytest

# Dodaj katalog nadrzędny do Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from jan import __version__, mcp
from jan.api_client import BielikClient
from jan.kochanowski_quotes import (
    FAREWELLS,
    GREETINGS,
    KochanowskiPersona,
    QUOTES_BY_THEME,
)
from jan.jan_subagent_opencode import check_configuration, greet_jan, main
from jan.system_prompts import get_system_prompt, SYSTEM_PROMPTS


class TestKochanowskiPersona:
    """Testy dla klasy KochanowskiPersona"""

    def test_get_greeting(self):
        """Test powitania"""
        greeting = KochanowskiPersona.get_greeting()
        assert greeting is not None
        assert isinstance(greeting, str)
        assert len(greeting) > 0
        assert greeting in GREETINGS

    def test_get_farewell(self):
        """Test pożegnania"""
        farewell = KochanowskiPersona.get_farewell()
        assert farewell is not None
        assert isinstance(farewell, str)
        assert len(farewell) > 0
        assert farewell in FAREWELLS

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
        assert any(greeting in result for greeting in GREETINGS)

        # Tylko z pożegnaniem
        result = KochanowskiPersona.format_with_personality(
            message, include_greeting=False, include_farewell=True
        )
        assert message in result
        assert any(farewell in result for farewell in FAREWELLS)

        # Kompletna wiadomość
        result = KochanowskiPersona.format_with_personality(
            message, include_greeting=True, include_farewell=True
        )
        assert message in result
        assert any(greeting in result for greeting in GREETINGS)
        assert any(farewell in result for farewell in FAREWELLS)


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


class TestRuntimeBehavior:
    """Testy publicznego zachowania runtime."""

    def test_check_configuration_uses_status_icons(self):
        summary = check_configuration()
        assert "✅" in summary or "❌" in summary
        assert "True" not in summary
        assert "False" not in summary

    def test_greet_jan_uses_addressee(self):
        result = greet_jan("Pawle")
        assert "Pawle" in result

    def test_main_does_not_write_to_stdout(self, monkeypatch, capsys):
        monkeypatch.setattr("jan.jan_subagent_opencode.mcp.run", lambda: None)
        main()
        captured = capsys.readouterr()
        assert captured.out == ""


class TestPackagingAndConfig:
    """Testy pakietowania i sample configu."""

    def test_package_version_is_2_0_0(self):
        assert __version__ == "2.0.0"

    def test_mcp_config_is_valid_json_and_uses_opencode(self):
        config_path = Path(__file__).resolve().parents[1] / "mcp_config.json"
        content = config_path.read_text(encoding="utf-8")
        payload = json.loads(content)
        server = payload["mcpServers"]["jan-kochanowski"]
        assert server["args"] == ["-m", "jan.jan_subagent_opencode"]

    def test_bielik_client_reset_refreshes_runtime_config(self, monkeypatch):
        monkeypatch.setenv("NVIDIA_API_KEY", "nvapi-initial-test-key")
        monkeypatch.setenv("NVIDIA_API_BASE", "https://initial.example.test/v1")
        monkeypatch.setenv("BIELIK_MODEL_ID", "initial-model")

        client = BielikClient()

        monkeypatch.setenv("NVIDIA_API_KEY", "nvapi-updated-test-key")
        monkeypatch.setenv("NVIDIA_API_BASE", "https://updated.example.test/v1")
        monkeypatch.setenv("BIELIK_MODEL_ID", "updated-model")

        client.reset()

        assert client.api_key == "nvapi-updated-test-key"
        assert client.base_url == "https://updated.example.test/v1"
        assert client.model_id == "updated-model"


def test_imports():
    """Test czy można importować główne elementy"""
    assert KochanowskiPersona is not None
    assert get_system_prompt is not None
    assert mcp is not None


if __name__ == "__main__":
    # Uruchom testy
    pytest.main([__file__, "-v"])
