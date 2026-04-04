"""
Moduł konfiguracyjny dla Jan Subagent
Zarządzanie API key, konfiguracją i cache'owaniem
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class JanConfig:
    """Menadżer konfiguracji dla Jana"""

    def __init__(self):
        """Inicjalizuje menadżer konfiguracji"""
        # Ścieżka do katalogu configu
        self.config_dir = Path.home() / ".jan"
        self.config_file = self.config_dir / "config.json"

        # Utwórz katalog configu jeśli nie istnieje
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Załaduj konfigurację
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Załaduj konfigurację z pliku"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(
                    "Nie udało się załadować konfiguracji z %s: %s",
                    self.config_file,
                    e,
                )
        return {}

    def _save_config(self):
        """Zapisz konfigurację do pliku"""
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    @property
    def api_key(self) -> Optional[str]:
        """Pobierz API key"""
        # Najpierw sprawdź environment variable
        env_key = os.getenv("NVIDIA_API_KEY")
        if env_key:
            return env_key

        # Potem sprawdź config file
        return self.config.get("api_key")

    def set_api_key(self, api_key: str) -> None:
        """Ustaw API key i zapisz w configu"""
        # Walidacja
        if not api_key or len(api_key.strip()) < 10:
            raise ValueError("API key musi mieć co najmniej 10 znaków")

        api_key = api_key.strip()

        # Zapisz w configu
        self.config["api_key"] = api_key
        self._save_config()

        # Zapisz jako environment variable dla tej sesji
        os.environ["NVIDIA_API_KEY"] = api_key

    @property
    def is_configured(self) -> bool:
        """Sprawdź czy API key jest skonfigurowany"""
        return bool(self.api_key)

    @property
    def model_id(self) -> str:
        """Pobierz ID modelu"""
        return os.getenv("BIELIK_MODEL_ID", "speakleash/bielik-11b-v2.6-instruct")

    @property
    def api_base(self) -> str:
        """Pobierz base URL API"""
        return os.getenv("NVIDIA_API_BASE", "https://integrate.api.nvidia.com/v1")

    @property
    def default_temperature(self) -> float:
        """Pobierz domyślną temperaturę"""
        return float(os.getenv("DEFAULT_CORRECTION_TEMPERATURE", "0.3"))

    @property
    def max_tokens(self) -> int:
        """Pobierz maksymalną liczbę tokenów"""
        return int(os.getenv("DEFAULT_MAX_TOKENS", "4096"))

    @property
    def log_level(self) -> str:
        """Pobierz poziom logowania"""
        return os.getenv("LOG_LEVEL", "info")

    @property
    def github_token_configured(self) -> bool:
        return bool(os.getenv("GITHUB_TOKEN"))

    @property
    def github_repository(self) -> str | None:
        return os.getenv("GITHUB_REPOSITORY")

    @property
    def jira_base_url(self) -> str | None:
        return os.getenv("JIRA_BASE_URL")

    @property
    def jira_email(self) -> str | None:
        return os.getenv("JIRA_EMAIL")

    @property
    def jira_token_configured(self) -> bool:
        return bool(os.getenv("JIRA_API_TOKEN"))

    @property
    def policy_file(self) -> str:
        return os.getenv("JAN_POLICY_FILE", str(Path.cwd() / "jan.yml"))

    def get_config_summary(self) -> Dict[str, Any]:
        """Pobierz podsumowanie konfiguracji"""
        return {
            "is_configured": self.is_configured,
            "has_env_key": bool(os.getenv("NVIDIA_API_KEY")),
            "has_config_key": bool(self.config.get("api_key")),
            "model_id": self.model_id,
            "api_base": self.api_base,
            "default_temperature": self.default_temperature,
            "max_tokens": self.max_tokens,
            "config_file": str(self.config_file),
            "github_token_configured": self.github_token_configured,
            "github_repository": self.github_repository,
            "jira_base_url": self.jira_base_url,
            "jira_token_configured": self.jira_token_configured,
            "policy_file": self.policy_file,
        }

    def reset_api_key(self) -> None:
        """Resetuj API key"""
        if "api_key" in self.config:
            del self.config["api_key"]
        self._save_config()

        if "NVIDIA_API_KEY" in os.environ:
            del os.environ["NVIDIA_API_KEY"]


# Globalna instancja
config = JanConfig()
