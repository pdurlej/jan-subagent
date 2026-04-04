"""
Jan Subagent - MCP subagent Jana Kochanowskiego do korekty języka polskiego
Zoptymalizowana wersja pod OpenCode
"""

import json
import logging
from mcp.server.fastmcp import FastMCP
from .kochanowski_quotes import KochanowskiPersona
from .system_prompts import get_system_prompt
from .config import config
from .api_client import bielik
from .workflow_engine import execute_repo_native_workflow
from .output_utils import (
    choose_light_greeting,
    extract_json_payload,
    extract_primary_text,
    format_compact_explainer,
)

logger = logging.getLogger(__name__)


# Inicjalizacja MCP server (zoptymalizowana)
mcp = FastMCP(
    name="jan-kochanowski",
)


# ==================== HELPER FUNCTIONS ====================


def format_status_icon(value: bool) -> str:
    """Zwraca ikonę statusu zgodną z publiczną dokumentacją."""
    return "✅" if value else "❌"


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


def format_plain_text_response(content: str, include_greeting: bool = False) -> str:
    """Zwraca paste-ready tekst bez wrapperów Jana."""

    primary = extract_primary_text(content)
    if not primary:
        return ""
    if include_greeting:
        return f"{choose_light_greeting()}\n{primary}"
    return primary


def format_explainer_response(content: str, include_greeting: bool = False) -> str:
    """Zwraca zwięzły explain mode dla korekty workplace."""

    formatted = format_compact_explainer(content, include_greeting=include_greeting)
    return formatted or format_plain_text_response(content, include_greeting=include_greeting)


def format_json_report_response(content: str) -> str:
    """Zwraca wyłącznie poprawny JSON, jeśli uda się go wydobyć."""

    payload = extract_json_payload(content)
    if payload is not None:
        return json.dumps(payload, indent=2, ensure_ascii=False)
    return content.strip()


def format_quality_scorecard(content: str) -> str:
    """Zwraca krótki scorecard jakości tekstu bez wrappera persony."""

    return content.strip()


def build_workplace_response(
    content: str,
    include_greeting: bool = False,
    include_explanation: bool = False,
) -> str:
    """Formatowanie odpowiedzi dla tooli workplace."""

    if include_explanation:
        return format_explainer_response(content, include_greeting=include_greeting)
    return format_plain_text_response(content, include_greeting=include_greeting)


def build_response_mode(include_explanation: bool = False) -> str:
    """Zwraca response mode dla prompt buildera."""

    return "compact_explainer" if include_explanation else "plain_text"


# ==================== MCP TOOLS - KONFIGURACJA ====================


@mcp.tool()
def check_configuration() -> str:
    """Sprawdź konfigurację Jana"""
    summary = config.get_config_summary()

    msg = "### Konfiguracja Jana Repo-Native\n\n"
    msg += f"**API Key skonfigurowany:** {format_status_icon(summary['is_configured'])}\n"
    msg += f"**Environment Variable:** {format_status_icon(summary['has_env_key'])}\n"
    msg += f"**Config File:** {format_status_icon(summary['has_config_key'])}\n\n"

    msg += f"**Model:** {summary['model_id']}\n"
    msg += f"**API Base:** {summary['api_base']}\n"
    msg += f"**Default Temperature:** {summary['default_temperature']}\n"
    msg += f"**Max Tokens:** {summary['max_tokens']}\n\n"
    msg += f"**GitHub token:** {format_status_icon(summary['github_token_configured'])}\n"
    msg += f"**GitHub repo:** {summary['github_repository'] or 'auto-detect'}\n"
    msg += f"**Jira base URL:** {summary['jira_base_url'] or 'nie ustawiono'}\n"
    msg += f"**Jira token:** {format_status_icon(summary['jira_token_configured'])}\n"
    msg += f"**Policy file:** {summary['policy_file']}\n\n"

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


def _ensure_model_ready() -> str | None:
    if not bielik.is_ready():
        return bielik.call("", "")
    return None


@mcp.tool()
def write_pr_description(
    raw_notes: str = "",
    git_range: str | None = None,
    github_pr: int | None = None,
    jira_keys: list[str] | None = None,
    audience: str = "reviewer",
    response_mode: str = "final",
) -> str:
    """Repo-native workflow dla opisu PR po polsku."""
    unavailable = _ensure_model_ready()
    if unavailable:
        return unavailable
    return execute_repo_native_workflow(
        "write_pr_description",
        raw_notes=raw_notes,
        git_range=git_range,
        github_pr=github_pr,
        jira_keys=jira_keys,
        audience=audience,
        response_mode=response_mode,
    )


@mcp.tool()
def compose_release_notes(
    raw_notes: str = "",
    git_range: str | None = None,
    github_prs: list[int] | None = None,
    jira_keys: list[str] | None = None,
    audience: str = "internal",
    response_mode: str = "final",
) -> str:
    """Repo-native workflow dla changelogu i release notes."""
    unavailable = _ensure_model_ready()
    if unavailable:
        return unavailable
    return execute_repo_native_workflow(
        "compose_release_notes",
        raw_notes=raw_notes,
        git_range=git_range,
        github_prs=github_prs,
        jira_keys=jira_keys,
        audience=audience,
        response_mode=response_mode,
    )


@mcp.tool()
def rewrite_issue(
    raw_notes: str = "",
    github_issue: int | None = None,
    jira_key: str | None = None,
    audience: str = "internal",
    response_mode: str = "final",
) -> str:
    """Repo-native workflow do przepisywania zgłoszeń i ticketów."""
    unavailable = _ensure_model_ready()
    if unavailable:
        return unavailable
    return execute_repo_native_workflow(
        "rewrite_issue",
        raw_notes=raw_notes,
        github_issue=github_issue,
        jira_key=jira_key,
        audience=audience,
        response_mode=response_mode,
    )


@mcp.tool()
def write_rollout_note(
    raw_notes: str = "",
    git_range: str | None = None,
    github_prs: list[int] | None = None,
    jira_keys: list[str] | None = None,
    audience: str = "internal",
    response_mode: str = "final",
) -> str:
    """Repo-native workflow dla notatki rolloutowej."""
    unavailable = _ensure_model_ready()
    if unavailable:
        return unavailable
    return execute_repo_native_workflow(
        "write_rollout_note",
        raw_notes=raw_notes,
        git_range=git_range,
        github_prs=github_prs,
        jira_keys=jira_keys,
        audience=audience,
        response_mode=response_mode,
    )


@mcp.tool()
def correct_orthography(
    text: str,
    include_greeting: bool = False,
    include_explanation: bool = False,
) -> str:
    """[LEGACY] Poprawa ortografii tekstu polskiego."""
    if not bielik.is_ready():
        return bielik.call("", "")  # Zwraca komunikat o braku API key

    system_prompt = get_system_prompt(
        "orthography", response_mode=build_response_mode(include_explanation)
    )
    user_message = f'Popraw ortografię w tekście: "{text}"'

    result = bielik.call(system_prompt, user_message, temperature=0.2)
    return build_workplace_response(
        result,
        include_greeting=include_greeting,
        include_explanation=include_explanation,
    )


@mcp.tool()
def correct_punctuation(
    text: str,
    include_greeting: bool = False,
    include_explanation: bool = False,
) -> str:
    """[LEGACY] Korekta interpunkcji tekstu polskiego."""
    if not bielik.is_ready():
        return bielik.call("", "")

    system_prompt = get_system_prompt(
        "punctuation", response_mode=build_response_mode(include_explanation)
    )
    user_message = f'Popraw interpunkcję w tekście: "{text}"'

    result = bielik.call(system_prompt, user_message, temperature=0.2)
    return build_workplace_response(
        result,
        include_greeting=include_greeting,
        include_explanation=include_explanation,
    )


@mcp.tool()
def verify_grammar(text: str, include_greeting: bool = False) -> str:
    """[LEGACY] Weryfikacja gramatyki tekstu polskiego."""
    if not bielik.is_ready():
        return bielik.call("", "")

    system_prompt = get_system_prompt("grammar", response_mode="json_report")
    user_message = f'Sprawdź gramatykę tekstu: "{text}"'

    result = bielik.call(system_prompt, user_message, temperature=0.1)
    if include_greeting:
        logger.debug("verify_grammar ignores include_greeting to preserve parseable JSON")
    return format_json_report_response(result)


@mcp.tool()
def improve_style(
    text: str,
    style: str = "elegancki",
    include_greeting: bool = False,
    include_explanation: bool = False,
) -> str:
    """[LEGACY] Ulepszenie stylu tekstu polskiego."""
    if not bielik.is_ready():
        return bielik.call("", "")

    available_styles = ["elegancki", "prosty", "poetycki", "naukowy", "ulotny"]
    style = style.lower() if style.lower() in available_styles else "elegancki"

    system_prompt = get_system_prompt(
        "style", response_mode=build_response_mode(include_explanation)
    )
    user_message = f'Ulepsz styl tekstu "{text}" na styl: {style}'

    result = bielik.call(system_prompt, user_message, temperature=0.4)
    return build_workplace_response(
        result,
        include_greeting=include_greeting,
        include_explanation=include_explanation,
    )


@mcp.tool()
def comprehensive_correction(
    text: str,
    mode: str = "standard",
    include_greeting: bool = False,
    include_explanation: bool = False,
) -> str:
    """[LEGACY] Kompleksowa korekta tekstu polskiego."""
    if not bielik.is_ready():
        return bielik.call("", "")

    system_prompt = get_system_prompt(
        "comprehensive", response_mode=build_response_mode(include_explanation)
    )
    user_message = f'Kompleksowa korekta tekstu: "{text}" w trybie: {mode}'

    result = bielik.call(system_prompt, user_message, temperature=0.3)
    return build_workplace_response(
        result,
        include_greeting=include_greeting,
        include_explanation=include_explanation,
    )


@mcp.tool()
def get_language_advice(topic: str) -> str:
    """Nie-core: porada językowa w stylu Jana Kochanowskiego."""
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
    """Legacy utility i wewnętrzny QA helper dla workflowów."""
    if not bielik.is_ready():
        return bielik.call("", "")

    system_prompt = get_system_prompt("quality")
    user_message = f'Sprawdź jakość tekstu: "{text}" (maks. 300 słów)'

    result = bielik.call(system_prompt, user_message, temperature=0.3)
    return format_quality_scorecard(result)


# ==================== MCP TOOLS - PERSONA ====================


@mcp.tool()
def greet_jan(name: str = "miłościw") -> str:
    """Powitanie od Jana Kochanowskiego"""
    addressee = name.strip()
    suffix = f", {addressee}" if addressee else ""
    return (
        f"{KochanowskiPersona.get_greeting()}\n\n"
        f"*Cóż to za piękny język polski{suffix}! Czym mogę Ci dzisiaj służyć?*"
    )


@mcp.tool()
def farewell_jan() -> str:
    """Pożegnanie od Jana Kochanowskiego"""
    return f"{KochanowskiPersona.get_farewell()}\n\n*Pamiętaj: język polski to skarb narodu. Chroń go i pielęgnuj.*"


# ==================== MAIN ====================


def main():
    """Uruchamia MCP server"""
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper(), logging.INFO)
    )
    mcp.run()


if __name__ == "__main__":
    main()
