"""HTTP client for Ductor Assist providers."""

from __future__ import annotations

import asyncio
from typing import Any

from aiohttp import ClientError, ClientSession

from homeassistant.exceptions import HomeAssistantError

from .const import (
    BRIDGE_RESPONSE_KEYS,
    CONF_API_KEY,
    CONF_ENDPOINT_URL,
    CONF_MODEL,
    CONF_PROVIDER,
    CONF_SYSTEM_PROMPT,
    CONF_TIMEOUT,
    CONF_VERIFY_SSL,
    DEFAULT_SYSTEM_PROMPT,
    DEFAULT_TIMEOUT,
    DEFAULT_VERIFY_SSL,
    PROVIDER_BRIDGE,
    PROVIDER_OPENAI_COMPATIBLE,
)


class DuctorAssistError(HomeAssistantError):
    """Base error for Ductor Assist."""


class DuctorAssistClient:
    """Small async client for Ductor and OpenAI-compatible endpoints."""

    def __init__(self, session: ClientSession, settings: dict[str, Any]) -> None:
        """Initialize the client."""
        self._session = session
        self._settings = settings

    async def async_test_connection(self) -> None:
        """Validate that the configured endpoint responds."""
        await self.async_ask("Odpovez jen slovem OK.", "cs", None)

    async def async_ask(
        self,
        text: str,
        language: str,
        conversation_id: str | None,
    ) -> tuple[str, str | None]:
        """Send a message and return response text plus optional conversation id."""
        provider = self._settings[CONF_PROVIDER]
        if provider == PROVIDER_OPENAI_COMPATIBLE:
            return await self._async_openai_compatible(text, language, conversation_id)
        if provider == PROVIDER_BRIDGE:
            return await self._async_bridge(text, language, conversation_id)
        raise DuctorAssistError(f"Unsupported provider: {provider}")

    async def _async_openai_compatible(
        self,
        text: str,
        language: str,
        conversation_id: str | None,
    ) -> tuple[str, str | None]:
        """Call an OpenAI-compatible chat completions endpoint."""
        endpoint = self._settings[CONF_ENDPOINT_URL].rstrip("/")
        if not endpoint.endswith("/chat/completions"):
            endpoint = f"{endpoint}/chat/completions"

        payload = {
            "model": self._settings[CONF_MODEL],
            "messages": [
                {"role": "system", "content": self._system_prompt},
                {"role": "user", "content": text},
            ],
            "temperature": 0.2,
        }
        headers = self._headers

        data = await self._async_post(endpoint, payload, headers)
        try:
            response = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as err:
            raise DuctorAssistError("OpenAI-compatible response is missing content") from err

        return str(response).strip(), conversation_id

    async def _async_bridge(
        self,
        text: str,
        language: str,
        conversation_id: str | None,
    ) -> tuple[str, str | None]:
        """Call a generic Ductor bridge endpoint."""
        payload = {
            "text": text,
            "language": language,
            "conversation_id": conversation_id,
            "system_prompt": self._system_prompt,
            "source": "home_assistant_assist",
        }
        data = await self._async_post(
            self._settings[CONF_ENDPOINT_URL],
            payload,
            self._headers,
        )

        response: Any = None
        for key in BRIDGE_RESPONSE_KEYS:
            if key in data:
                response = data[key]
                break

        if response is None:
            raise DuctorAssistError("Bridge response is missing response text")

        new_conversation_id = data.get("conversation_id", conversation_id)
        return str(response).strip(), new_conversation_id

    async def _async_post(
        self,
        endpoint: str,
        payload: dict[str, Any],
        headers: dict[str, str],
    ) -> dict[str, Any]:
        """POST JSON and return parsed JSON."""
        timeout = self._settings.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)
        verify_ssl = self._settings.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL)

        try:
            async with asyncio.timeout(timeout):
                response = await self._session.post(
                    endpoint,
                    json=payload,
                    headers=headers,
                    ssl=verify_ssl,
                )
                response.raise_for_status()
                data = await response.json()
        except TimeoutError as err:
            raise DuctorAssistError("Ductor Assist endpoint timed out") from err
        except ClientError as err:
            raise DuctorAssistError(f"Ductor Assist endpoint failed: {err}") from err

        if not isinstance(data, dict):
            raise DuctorAssistError("Ductor Assist endpoint returned non-object JSON")
        return data

    @property
    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        api_key = self._settings.get(CONF_API_KEY)
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers

    @property
    def _system_prompt(self) -> str:
        return self._settings.get(CONF_SYSTEM_PROMPT) or DEFAULT_SYSTEM_PROMPT
