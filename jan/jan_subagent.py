"""
Jan Subagent - MCP subagent Jana Kochanowskiego do korekty języka polskiego
Główny plik z definicją narzędzi MCP i integracją z NVIDIA Bielik API
"""

import os
import json
import random
from typing import Dict, List, Optional, Any
from openai import OpenAI
from mcp.server.fastmcp import FastMCP
from .kochanowski_quotes import KochanowskiPersona
from .system_prompts import get_system_prompt


# Inicjalizacja MCP server
mcp = FastMCP(
    name="jan-kochanowski-editor",
    description="Subagent MCP Jana Kochanowskiego - ekspert do korekty języka polskiego",
)


# Konfiguracja klienta NVIDIA Bielik API
class BielikClient:
    """Klient do komunikacji z NVIDIA Bielik API"""

    def __init__(self):
        """Inicjalizuje klienta Bielika"""
        self.api_key = os.getenv("NVIDIA_API_KEY")
        if not self.api_key:
            raise ValueError(
                "NVIDIA_API_KEY nie jest ustawiony w zmiennych środowiskowych. "
                "Proszę ustawić NVIDIA_API_KEY w pliku .env lub environment variables."
            )

        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1", api_key=self.api_key
        )

    def call_bielik(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.3,
        max_tokens: int = 4096,
        model: str = "speakleash/bielik-11b-v2_6-instruct",
    ) -> str:
        """
        Wywołaj Bielika 11B jako eksperta językowego

        Args:
            system_prompt: System prompt instrukujący model
            user_message: Wiadomość użytkownika
            temperature: Temperatura generacji (0.0-1.0)
            max_tokens: Maksymalna liczba tokenów
            model: ID modelu do użycia

        Returns:
            Odpowiedź od modelu Bielik
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.9,
            )
            return response.choices[0].message.content
        except Exception as e:
            error_msg = f"Nie udało się połączyć z Bielikiem: {str(e)}"
            return error_msg


# Globalna instancja klienta
try:
    bielik_client = BielikClient()
except ValueError:
    bielik_client = None


def format_response(
    content: str,
    correction_type: str,
    include_greeting: bool = False,
    include_farewell: bool = False,
    include_reflection: bool = True,
) -> str:
    """
    Formatuje odpowiedź z osobowością Kochanowskiego

    Args:
        content: Główna treść odpowiedzi
        correction_type: Typ korekty (orthography, punctuation, grammar, style)
        include_greeting: Czy dodać powitanie
        include_farewell: Czy dodać pożegnanie
        include_reflection: Czy dodać refleksję po korekcie

    Returns:
        Sformatowana odpowiedź
    """
    parts = []

    if include_greeting:
        parts.append(f"{KochanowskiPersona.get_greeting()}\n\n")

    parts.append(content)

    if include_reflection:
        parts.append(f"\n\n*{KochanowskiPersona.get_reflection(correction_type)}*")

    if include_farewell:
        parts.append(f"\n\n{KochanowskiPersona.get_farewell()}")

    return "".join(parts)


# ==================== MCP NARZĘDZIA ====================


@mcp.tool()
def correct_orthography(text: str, include_greeting: bool = True) -> str:
    """
    Poprawa ortografii tekstu polskiego z komentarzami Jana Kochanowskiego

    Args:
        text: Tekst do skorektowania
        include_greeting: Czy dodać powitanie w stylu Kochanowskiego

    Returns:
        Poprawiony tekst z wyróżnionymi zmianami i wyjaśnieniami
    """
    if not bielik_client:
        return "Błagam, czekam na API key Bielika, by móc pomóc w korekcie."

    system_prompt = get_system_prompt("orthography")

    user_message = f"""
Popraw ortografię w poniższym tekście.

Tekst do korekty:
"{text}"

Format odpowiedzi:
1. Poprawiony tekst (z wyróżnionymi zmianami **bold**)
2. Lista błędów ortograficznych z wyjaśnieniami
3. Krótki komentarz na końcu
"""

    result = bielik_client.call_bielik(
        system_prompt=system_prompt, user_message=user_message, temperature=0.2
    )

    return format_response(
        content=result,
        correction_type="orthography",
        include_greeting=include_greeting,
        include_reflection=True,
    )


@mcp.tool()
def correct_punctuation(text: str, include_greeting: bool = True) -> str:
    """
    Korekta interpunkcji tekstu polskiego z komentarzami Jana Kochanowskiego

    Args:
        text: Tekst do skorygowania
        include_greeting: Czy dodać powitanie w stylu Kochanowskiego

    Returns:
        Tekst z poprawioną interpunkcją i wyjaśnieniami
    """
    if not bielik_client:
        return "Błagam, czekam na API key Bielika, by móc pomóc w korekcie."

    system_prompt = get_system_prompt("punctuation")

    user_message = f"""
Popraw interpunkcję w poniższym tekście.

Tekst do korekty:
"{text}"

Format odpowiedzi:
1. Poprawiony tekst (z wyróżnionymi zmianami)
2. Lista zmian interpunkcyjnych z uzasadnieniami
3. Cytat z polskiej literatury ilustrujący zasadę
"""

    result = bielik_client.call_bielik(
        system_prompt=system_prompt, user_message=user_message, temperature=0.2
    )

    return format_response(
        content=result,
        correction_type="punctuation",
        include_greeting=include_greeting,
        include_reflection=True,
    )


@mcp.tool()
def verify_grammar(text: str, include_greeting: bool = True) -> str:
    """
    Weryfikacja gramatyki tekstu polskiego z komentarzami Jana Kochanowskiego

    Args:
        text: Tekst do sprawdzenia
        include_greeting: Czy dodać powitanie w stylu Kochanowskiego

    Returns:
        Raport gramatyczny z wynikami weryfikacji
    """
    if not bielik_client:
        return "Błagam, czekam na API key Bielika, by móc pomóc w korekcie."

    system_prompt = get_system_prompt("grammar")

    user_message = f"""
Sprawdź gramatykę poniższego tekstu.

Tekst do sprawdzenia:
"{text}"

Format odpowiedzi:
Zwróć JSON:
{{
    "correct": boolean,
    "errors": [
        {{
            "type": "rodzaj błędu",
            "original": "oryginalna forma",
            "corrected": "poprawna forma",
            "explanation": "wyjaśnienie",
            "position": "pozycja w tekście"
        }}
    ],
    "suggestions": [
        {{
            "original": "oryginał",
            "suggestion": "sugestia",
            "reason": "powód"
        }}
    ],
    "overall_assessment": "ogólna ocena tekstu"
}}

Po JSON dodaj krótki komentarz.
"""

    try:
        result = bielik_client.call_bielik(
            system_prompt=system_prompt, user_message=user_message, temperature=0.1
        )

        # Próba parsowania JSON
        try:
            # Znajdź JSON w odpowiedzi
            import re

            json_match = re.search(r"\{[\s\S]*\}", result)
            if json_match:
                json_data = json.loads(json_match.group())
                # Formatuj JSON ładniej
                formatted_json = json.dumps(json_data, indent=2, ensure_ascii=False)
                result = f"### Raport Gramatyczny\n\n```json\n{formatted_json}\n```\n\n{result.replace(json_match.group(), '')}"
        except:
            pass

        return format_response(
            content=result,
            correction_type="grammar",
            include_greeting=include_greeting,
            include_reflection=True,
        )
    except Exception as e:
        return format_response(
            content=f"Przepraszam, ale napotkałem trudności: {str(e)}",
            correction_type="error",
            include_greeting=include_greeting,
        )


@mcp.tool()
def improve_style(
    text: str, style: str = "elegancki", include_greeting: bool = True
) -> str:
    """
    Ulepszenie stylu tekstu polskiego z komentarzami Jana Kochanowskiego

    Args:
        text: Tekst do ulepszenia
        style: Styl docelowy (elegancki, prosty, poetycki, naukowy)
        include_greeting: Czy dodać powitanie w stylu Kochanowskiego

    Returns:
        Ulepszony tekst z wyjaśnieniami zmian
    """
    if not bielik_client:
        return "Błagam, czekam na API key Bielika, by móc pomóc w korekcie."

    available_styles = ["elegancki", "prosty", "poetycki", "naukowy", "ulotny"]
    if style.lower() not in available_styles:
        style = "elegancki"

    system_prompt = get_system_prompt("style").replace("{style}", style)

    user_message = f"""
Ulepsz styl poniższego tekstu na styl: {style}.

Tekst do ulepszenia:
"{text}"

Format odpowiedzi:
1. Ulepszony tekst
2. Lista zmian stylowych z uzasadnieniami
3. Cytat z literatury ilustrujący styl
"""

    result = bielik_client.call_bielik(
        system_prompt=system_prompt, user_message=user_message, temperature=0.4
    )

    return format_response(
        content=result,
        correction_type="style",
        include_greeting=include_greeting,
        include_reflection=True,
    )


@mcp.tool()
def comprehensive_correction(
    text: str,
    mode: str = "standard",
    include_greeting: bool = True,
    include_farewell: bool = True,
) -> str:
    """
    Kompleksowa korekta tekstu polskiego: ortografia, interpunkcja, gramatyka i styl

    Args:
        text: Tekst do skorygowania
        mode: Tryb korekty (standard, conservative, aggressive)
        include_greeting: Czy dodać powitanie
        include_farewell: Czy dodać pożegnanie

    Returns:
        Kompletny raport korekty
    """
    if not bielik_client:
        return "Błagam, czekam na API key Bielika, by móc pomóc w korekcie."

    available_modes = ["standard", "conservative", "aggressive"]
    if mode.lower() not in available_modes:
        mode = "standard"

    system_prompt = get_system_prompt("comprehensive").replace("{mode}", mode)

    user_message = f"""
Przeprowadź kompleksową korektę poniższego tekstu w trybie: {mode}.

Tekst do korekty:
"{text}"

Format odpowiedzi:
Zwróć JSON:
{{
    "original_text": "oryginalny tekst",
    "corrected_text": "poprawiony tekst",
    "orthography": {{
        "errors": int,
        "corrections": ["korekta1", "korekta2"],
        "score": float
    }},
    "punctuation": {{
        "errors": int,
        "corrections": ["korekta1", "korekta2"],
        "score": float
    }},
    "grammar": {{
        "errors": int,
        "corrections": ["korekta1", "korekta2"],
        "score": float
    }},
    "style": {{
        "issues": [],
        "improvements": [],
        "score": float
    }},
    "overall_score": float,
    "summary": "podsumowanie"
}}

Po JSON dodaj osobistą refleksję o pięknie języka polskiego.
"""

    try:
        result = bielik_client.call_bielik(
            system_prompt=system_prompt, user_message=user_message, temperature=0.3
        )

        # Próba parsowania JSON
        try:
            import re

            json_match = re.search(r"\{[\s\S]*\}", result)
            if json_match:
                json_data = json.loads(json_match.group())
                # Formatuj JSON ładniej
                formatted_json = json.dumps(json_data, indent=2, ensure_ascii=False)

                # Oblicz ogólną ocenę
                overall_score = json_data.get("overall_score", 0)
                score_text = f"### Ocena ogólna: {overall_score}/10\n\n"

                result = f"{score_text}```json\n{formatted_json}\n```\n\n{result.replace(json_match.group(), '')}"
        except:
            pass

        return format_response(
            content=result,
            correction_type="comprehensive",
            include_greeting=include_greeting,
            include_farewell=include_farewell,
            include_reflection=False,  # Refleksja już w system prompt
        )
    except Exception as e:
        return format_response(
            content=f"Przepraszam, ale napotkałem trudności: {str(e)}",
            correction_type="error",
            include_greeting=include_greeting,
        )


@mcp.tool()
def get_language_advice(topic: str, include_greeting: bool = True) -> str:
    """
    Porada językowa w stylu Jana Kochanowskiego

    Args:
        topic: Temat porady (np. "ó vs u", "interpunkcja", "gramatyka", "styl")
        include_greeting: Czy dodać powitanie

    Returns:
        Edukacyjna porada językowa
    """
    if not bielik_client:
        return "Błagam, czekam na API key Bielika, by móc pomóc w korekcie."

    system_prompt = get_system_prompt("advice")

    user_message = f"""
Oferuj poradę językową na temat: {topic}.

Format odpowiedzi:
1. Tytuł porady
2. Wyjaśnienie zasady
3. Przykłady z literatury
4. Poradnia praktyczna
5. Refleksja o języku
"""

    result = bielik_client.call_bielik(
        system_prompt=system_prompt, user_message=user_message, temperature=0.5
    )

    return format_response(
        content=result,
        correction_type="advice",
        include_greeting=include_greeting,
        include_reflection=False,  # Refleksja w samej poradzie
    )


@mcp.tool()
def check_text_quality(text: str, include_greeting: bool = False) -> str:
    """
    Sprawdzenie jakości tekstu bez szczegółowej korekty

    Args:
        text: Tekst do sprawdzenia
        include_greeting: Czy dodać powitanie

    Returns:
        Krótka ocena jakości tekstu
    """
    if not bielik_client:
        return "Błagam, czekam na API key Bielika, by móc pomóc w korekcie."

    system_prompt = get_system_prompt("main")

    user_message = f"""
Sprawdź krótko jakość poniższego tekstu.

Tekst:
"{text}"

Zwróć:
1. Ogólną ocenę jakości (1-10)
2. Główne problemy (jeśli są)
3. Główne zalety (jeśli są)
3. Krótką rekomendację

Maksymalnie 300 słów.
"""

    result = bielik_client.call_bielik(
        system_prompt=system_prompt, user_message=user_message, temperature=0.3
    )

    return format_response(
        content=result,
        correction_type="general",
        include_greeting=include_greeting,
        include_reflection=True,
    )


@mcp.tool()
def greet_jan(name: str = "miłościw") -> str:
    """
    Powitanie od Jana Kochanowskiego

    Args:
        name: Imię lub tytuł do powitania

    Returns:
        Odpowiedź powitalna w stylu renesansowym
    """
    greeting = KochanowskiPersona.get_greeting()
    return (
        f"{greeting}\n\n*Cóż to za piękny język polski! Czym mogę Cię dzisiaj służyć?*"
    )


@mcp.tool()
def farewell_jan() -> str:
    """
    Pożegnanie od Jana Kochanowskiego

    Returns:
        Odpowiedź pożegnalna w stylu renesansowym
    """
    farewell = KochanowskiPersona.get_farewell()
    return (
        f"{farewell}\n\n*Pamiętaj: język polski to skarb narodu. Chroń go i pielęgnuj.*"
    )


# ==================== GŁÓWNA FUNKCJA ====================


def main():
    """Uruchamia MCP server"""
    print("=== Jan Subagent - Jana Kochanowskiego ===")
    print("Subagent MCP do korekty języka polskiego")
    print(f"Model: Bielik 11B v2.6 Instruct")
    print(f"Persona: Jan Kochanowski (poeta renesansowy)")
    print(f"Narzędzia: {len([tool for tool in dir(mcp) if not tool.startswith('_')])}")
    print()
    print("Uruchamiam MCP server...")
    mcp.run()


if __name__ == "__main__":
    main()
