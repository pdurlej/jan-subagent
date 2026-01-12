"""
Jan - Subagent MCP Jana Kochanowskiego do korekty języka polskiego
Pakiet narzędzi do poprawy ortografii, interpunkcji, gramatyki i stylu
"""

__version__ = "1.0.0"
__author__ = "Jan Kochanowski (AI persona)"
__description__ = (
    "Subagent MCP do korekty języka polskiego z wykorzystaniem modelu Bielik"
)

# Importy podstawowe
from .kochanowski_quotes import KochanowskiPersona
from .system_prompts import get_system_prompt

__all__ = [
    "KochanowskiPersona",
    "get_system_prompt",
]

# MCP server jest dostępny tylko jeśli zainstalowane są odpowiednie zależności
try:
    from .jan_subagent import mcp

    __all__.append("mcp")
except ImportError:
    mcp = None
