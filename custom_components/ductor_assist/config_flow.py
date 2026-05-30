"""Config flow for Ductor Assist."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import DuctorAssistClient, DuctorAssistError
from .const import (
    CONF_API_KEY,
    CONF_CONTINUE_CONVERSATION,
    CONF_ENDPOINT_URL,
    CONF_MODEL,
    CONF_PROVIDER,
    CONF_SYSTEM_PROMPT,
    CONF_TIMEOUT,
    CONF_VERIFY_SSL,
    DEFAULT_CONTINUE_CONVERSATION,
    DEFAULT_MODEL,
    DEFAULT_PROVIDER,
    DEFAULT_SYSTEM_PROMPT,
    DEFAULT_TIMEOUT,
    DEFAULT_VERIFY_SSL,
    DOMAIN,
    PROVIDER_BRIDGE,
    PROVIDER_OPENAI_COMPATIBLE,
)


def _schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_PROVIDER,
                default=defaults.get(CONF_PROVIDER, DEFAULT_PROVIDER),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        {
                            "value": PROVIDER_OPENAI_COMPATIBLE,
                            "label": "OpenAI-compatible chat completions",
                        },
                        {"value": PROVIDER_BRIDGE, "label": "Generic Ductor bridge"},
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                ),
            ),
            vol.Required(
                CONF_ENDPOINT_URL,
                default=defaults.get(CONF_ENDPOINT_URL, ""),
            ): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.URL),
            ),
            vol.Optional(
                CONF_API_KEY,
                default=defaults.get(CONF_API_KEY, ""),
            ): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD),
            ),
            vol.Optional(
                CONF_MODEL,
                default=defaults.get(CONF_MODEL, DEFAULT_MODEL),
            ): str,
            vol.Optional(
                CONF_SYSTEM_PROMPT,
                default=defaults.get(CONF_SYSTEM_PROMPT, DEFAULT_SYSTEM_PROMPT),
            ): selector.TextSelector(
                selector.TextSelectorConfig(
                    multiline=True,
                    type=selector.TextSelectorType.TEXT,
                ),
            ),
            vol.Optional(
                CONF_TIMEOUT,
                default=defaults.get(CONF_TIMEOUT, DEFAULT_TIMEOUT),
            ): vol.All(vol.Coerce(int), vol.Range(min=5, max=300)),
            vol.Optional(
                CONF_VERIFY_SSL,
                default=defaults.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL),
            ): bool,
            vol.Optional(
                CONF_CONTINUE_CONVERSATION,
                default=defaults.get(
                    CONF_CONTINUE_CONVERSATION,
                    DEFAULT_CONTINUE_CONVERSATION,
                ),
            ): bool,
        },
    )


class DuctorAssistConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ductor Assist."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle initial setup."""
        errors: dict[str, str] = {}

        if user_input is not None:
            data = _clean_input(user_input)
            client = DuctorAssistClient(async_get_clientsession(self.hass), data)
            try:
                await client.async_test_connection()
            except DuctorAssistError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(data[CONF_ENDPOINT_URL])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="Ductor", data=data)

        return self.async_show_form(
            step_id="user",
            data_schema=_schema(user_input),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return DuctorAssistOptionsFlow(config_entry)


class DuctorAssistOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Ductor Assist."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Manage options."""
        errors: dict[str, str] = {}
        current = {**self._config_entry.data, **self._config_entry.options}

        if user_input is not None:
            data = _clean_input(user_input)
            client = DuctorAssistClient(async_get_clientsession(self.hass), data)
            try:
                await client.async_test_connection()
            except DuctorAssistError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(title="", data=data)

        return self.async_show_form(
            step_id="init",
            data_schema=_schema(user_input or current),
            errors=errors,
        )


def _clean_input(user_input: dict[str, Any]) -> dict[str, Any]:
    """Normalize config flow input."""
    data = dict(user_input)
    data[CONF_ENDPOINT_URL] = data[CONF_ENDPOINT_URL].strip()
    data[CONF_API_KEY] = data.get(CONF_API_KEY, "").strip()
    data[CONF_MODEL] = data.get(CONF_MODEL, DEFAULT_MODEL).strip()
    data[CONF_SYSTEM_PROMPT] = data.get(CONF_SYSTEM_PROMPT, DEFAULT_SYSTEM_PROMPT).strip()
    return data
