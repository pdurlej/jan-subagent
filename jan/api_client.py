"""
Klient API dla Bielika 11B
Oddzielony moduł do komunikacji z NVIDIA NIM API
"""

import os
from typing import Optional, Any, cast
from openai import OpenAI, Client
from .config import config


class BielikClient:
    """Klient do komunikacji z NVIDIA Bielik API"""

    def __init__(self):
        """Inicjalizuje klienta Bielika"""
        self.api_key = config.api_key
        self.base_url = config.api_base
        self.model_id = config.model_id
        self.client: Optional[Client] = None

        if self.api_key:
            self._init_client()

    def _init_client(self):
        """Inicjalizuje OpenAI client"""
        try:
            if self.api_key:
                self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)
            else:
                self.client = None
        except Exception as e:
            print(f"Błąd inicjalizacji klienta Bielika: {e}")
            self.client = None

    def is_ready(self) -> bool:
        """Sprawdź czy klient jest gotowy"""
        return bool(self.client and self.api_key)

    def call(
        self,
        system_prompt: str,
        user_message: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None,
    ) -> str:
        """
        Wywołaj Bielika 11B jako eksperta językowego

        Args:
            system_prompt: System prompt instrukujący model
            user_message: Wiadomość użytkownika
            temperature: Temperatura generacji (default z configu)
            max_tokens: Maksymalna liczba tokenów (default z configu)
            model: ID modelu (default z configu)

        Returns:
            Odpowiedź od modelu Bielik lub komunikat błędu
        """
        if not self.is_ready() or not self.client:
            return self._get_unavailable_message()

        try:
            # Użyj parametrów z configu jeśli nie podane
            temp = (
                temperature if temperature is not None else config.default_temperature
            )
            tokens = max_tokens if max_tokens is not None else config.max_tokens
            model_id = model if model is not None else self.model_id

            response = self.client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=temp,
                max_tokens=tokens,
                top_p=0.9,
            )
            choices = response.choices
            if choices and len(choices) > 0 and choices[0].message:
                return choices[0].message.content or ""
            return "Nie otrzymano odpowiedzi od modelu."
        except Exception as e:
            return f"Nie udało się połączyć z Bielikiem: {str(e)}"

    def _get_unavailable_message(self) -> str:
        """Zwraca komunikat gdy API key nie jest skonfigurowany"""
        return (
            "Błagam miłościwi, czekam na API key Bielika, by móc pomóc w korekcie. "
            "Użyj narzędzia `setup_api_key` aby ustawić klucz."
        )

    def reset(self):
        """Resetuje klienta (np. po zmianie API key)"""
        self.api_key = config.api_key
        self._init_client()


# Globalna instancja klienta
bielik = BielikClient()
