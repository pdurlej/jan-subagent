"""
Jan Subagent - MCP subagent Jana Kochanowskiego do korekty języka polskiego
Zoptymalizowana wersja pod OpenCode
"""

import json
import random
from typing import Dict, List, Optional
from mcp.server.fastmcp import FastMCP
from .kochanowski_quotes import KochanowskiPersona
from .system_prompts import get_system_prompt
from .config import config
from .api_client import bielik


# Inicjalizacja MCP server (zoptymalizowana)
mcp = FastMCP(
    name="jan-kochanowski",
    description="Jan Kochanowski - ekspert do korekty języka polskiego",
)


# ==================== HELPER FUNCTIONS ====================


def format_response(
    content: str,
    correction_type: str,
    include_greeting: bool = False,
    include_farewell: bool = False,
    include_reflection: bool = True,
) -> str:
    """Formatuje odpowiedź z osobowością Kochanowskiego"""
    parts = []

    if include_greeting:
        parts.append(f"{KochanowskiPersona.get_greeting()}\n\n")

    parts.append(content)

    if include_reflection:
        parts.append(f"\n\n*{KochanowskiPersona.get_reflection(correction_type)}*")

    if include_farewell:
        parts.append(f"\n\n{KochanowskiPersona.get_farewell()}")

    return "".join(parts)


def format_json_response(json_str: str, prefix: str = "") -> str:
    """Formatuje JSON z odpowiedzi Bielika"""
    try:
        import re

        json_match = re.search(r"\{[\s\S]*\}", json_str)
        if json_match:
            json_data = json.loads(json_match.group())
            formatted = json.dumps(json_data, indent=2, ensure_ascii=False)
            return f"{prefix}```json\n{formatted}\n```\n\n{json_str.replace(json_match.group(), '')}"
    except:
        pass
    return json_str


# ==================== MCP TOOLS - KONFIGURACJA ====================


@mcp.tool()
def check_configuration() -> str:
    """Sprawdź konfigurację Jana"""
    summary = config.get_config_summary()

    msg = "### Konfiguracja Jana Kochanowskiego\n\n"
    msg += f"**API Key skonfigurowany:** {summary['is_configured']}\n"
    msg += f"**Environment Variable:** {summary['has_env_key']}\n"
    msg += f"**Config File:** {summary['has_config_key']}\n\n"

    msg += f"**Model:** {summary['model_id']}\n"
    msg += f"**API Base:** {summary['api_base']}\n"
    msg += f"**Default Temperature:** {summary['default_temperature']}\n"
    msg += f"**Max Tokens:** {summary['max_tokens']}\n\n"

    if not summary["is_configured"]:
        msg += "> ⚠️ **API Key nie jest ustawiony!**\n"
        msg += "> Użyj `setup_api_key` aby skonfigurować Jana.\n"

    return msg


@mcp.tool()
def setup_api_key(api_key: str) -> str:
    """
    Ustaw NVIDIA API Key dla Bielika

    Args:
        api_key: Twój NVIDIA API Key (uzyskaj na build.nvidia.com)

    Returns:
        Potwierdzenie ustawienia lub błąd
    """
    if not config.is_configured:
        greeting = KochanowskiPersona.get_greeting()
    else:
        greeting = ""

    try:
        config.set_api_key(api_key)
        bielik.reset()  # Reset klienta API

        msg = f"{greeting}\n\n" if greeting else ""
        msg += "✅ **API Key został pomyślnie ustawiony!**\n\n"
        msg += f"Lokalizacja: `{config.config_file}`\n"
        msg += f"Model: `{config.model_id}`\n\n"
        msg += "Teraz mogę pomóc w korekcie języka polskiego!"

        return format_response(
            msg,
            "setup",
            include_greeting=False,
            include_farewell=True,
            include_reflection=True,
        )
    except Exception as e:
        return f"❌ **Błąd:** {str(e)}\n\nSprawdź czy API key jest poprawny."


@mcp.tool()
def reset_api_key() -> str:
    """Resetuj API Key"""
    config.reset_api_key()
    bielik.reset()

    return "✅ **API Key został zresetowany.**\n\nUżyj `setup_api_key` aby ustawić nowy klucz."


# ==================== MCP TOOLS - KOREKTA ====================


@mcp.tool()
def correct_orthography(text: str, include_greeting: bool = True) -> str:
    """Poprawa ortografii tekstu polskiego"""
    if not bielik.is_ready():
        return bielik.call("", "")  # Zwraca komunikat o braku API key

    system_prompt = get_system_prompt("orthography")
    user_message = f'Popraw ortografię w tekście: "{text}"'

    result = bielik.call(system_prompt, user_message, temperature=0.2)

    return format_response(result, "orthography", include_greeting=include_greeting)


@mcp.tool()
def correct_punctuation(text: str, include_greeting: bool = True) -> str:
    """Korekta interpunkcji tekstu polskiego"""
    if not bielik.is_ready():
        return bielik.call("", "")

    system_prompt = get_system_prompt("punctuation")
    user_message = f'Popraw interpunkcję w tekście: "{text}"'

    result = bielik.call(system_prompt, user_message, temperature=0.2)

    return format_response(result, "punctuation", include_greeting=include_greeting)


@mcp.tool()
def verify_grammar(text: str, include_greeting: bool = True) -> str:
    """Weryfikacja gramatyki tekstu polskiego"""
    if not bielik.is_ready():
        return bielik.call("", "")

    system_prompt = get_system_prompt("grammar")
    user_message = f'Sprawdź gramatykę tekstu: "{text}"'

    result = bielik.call(system_prompt, user_message, temperature=0.1)
    result = format_json_response(result, "### Raport Gramatyczny\n\n")

    return format_response(result, "grammar", include_greeting=include_greeting)


@mcp.tool()
def improve_style(
    text: str, style: str = "elegancki", include_greeting: bool = True
) -> str:
    """Ulepszenie stylu tekstu polskiego"""
    if not bielik.is_ready():
        return bielik.call("", "")

    available_styles = ["elegancki", "prosty", "poetycki", "naukowy", "ulotny"]
    style = style.lower() if style.lower() in available_styles else "elegancki"

    system_prompt = get_system_prompt("style")
    user_message = f'Ulepsz styl tekstu "{text}" na styl: {style}'

    result = bielik.call(system_prompt, user_message, temperature=0.4)

    return format_response(result, "style", include_greeting=include_greeting)


@mcp.tool()
def comprehensive_correction(text: str, mode: str = "standard") -> str:
    """Kompleksowa korekta tekstu polskiego"""
    if not bielik.is_ready():
        return bielik.call("", "")

    system_prompt = get_system_prompt("comprehensive")
    user_message = f'Kompleksowa korekta tekstu: "{text}" w trybie: {mode}'

    result = bielik.call(system_prompt, user_message, temperature=0.3)
    result = format_json_response(result)

    return format_response(
        result, "comprehensive", include_greeting=True, include_farewell=True
    )


@mcp.tool()
def get_language_advice(topic: str) -> str:
    """Porada językowa w stylu Jana Kochanowskiego"""
    if not bielik.is_ready():
        return bielik.call("", "")

    system_prompt = get_system_prompt("advice")
    user_message = f"Oferuj poradę językową na temat: {topic}"

    result = bielik.call(system_prompt, user_message, temperature=0.5)

    return format_response(
        result, "advice", include_greeting=False, include_reflection=False
    )


@mcp.tool()
def check_text_quality(text: str) -> str:
    """Szybka ocena jakości tekstu"""
    if not bielik.is_ready():
        return bielik.call("", "")

    system_prompt = get_system_prompt("main")
    user_message = f'Sprawdź jakość tekstu: "{text}" (maks. 300 słów)'

    result = bielik.call(system_prompt, user_message, temperature=0.3)

    return format_response(result, "general", include_greeting=False)


# ==================== MCP TOOLS - PERSONA ====================


@mcp.tool()
def greet_jan(name: str = "miłościw") -> str:
    """Powitanie od Jana Kochanowskiego"""
    return f"{KochanowskiPersona.get_greeting()}\n\n*Cóż to za piękny język polski! Czym mogę Cię dzisiaj służyć?*"


@mcp.tool()
def farewell_jan() -> str:
    """Pożegnanie od Jana Kochanowskiego"""
    return f"{KochanowskiPersona.get_farewell()}\n\n*Pamiętaj: język polski to skarb narodu. Chroń go i pielęgnuj.*"


# ==================== MAIN ====================


def main():
    """Uruchamia MCP server"""
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 25 + "JAN SUBAGENT" + " " * 41 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    print(f"API Key: {'✅ Ustawiony' if config.is_configured else '❌ Brak'}")
    print(f"Model: {config.model_id}")
    print(f"Konfiguracja: {config.config_file}")
    print()
    print("Uruchamiam MCP server...")
    mcp.run()


if __name__ == "__main__":
    main()
