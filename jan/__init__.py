"""
Jan - Subagent MCP Jana Kochanowskiego do korekty języka polskiego
"""

from typing import Any

__version__ = "2.1.0"
__author__ = "Jan Subagent Team"

# Importy podstawowe (zoptymalizowane)
from .kochanowski_quotes import KochanowskiPersona
from .system_prompts import get_system_prompt
from .config import config

__all__ = [
    "KochanowskiPersona",
    "get_system_prompt",
    "config",
    "mcp",
]

# Lazy import mcp, aby uniknąć side-effectów przy `python -m jan.jan_subagent_opencode`
def __getattr__(name: str) -> Any:
    if name == "mcp":
        try:
            from .jan_subagent_opencode import mcp as server
        except ImportError:
            server = None
        globals()["mcp"] = server
        return server
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
