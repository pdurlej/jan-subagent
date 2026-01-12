"""
Jan - Subagent MCP Jana Kochanowskiego do korekty języka polskiego
"""

__version__ = "1.1.0"
__author__ = "Jan Subagent Team"

# Importy podstawowe (zoptymalizowane)
from .kochanowski_quotes import KochanowskiPersona
from .system_prompts import get_system_prompt
from .config import config

__all__ = [
    "KochanowskiPersona",
    "get_system_prompt",
    "config",
]

# MCP server jest dostępny tylko jeśli zainstalowane są zależności
try:
    from .jan_subagent_opencode import mcp

    __all__.append("mcp")
except ImportError:
    mcp = None
