"""Conversation platform for Ductor Assist."""

from __future__ import annotations

from typing import Literal

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import MATCH_ALL
from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import DuctorAssistClient, DuctorAssistError
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ductor Assist conversation entity."""
    async_add_entities([DuctorConversationEntity(config_entry)])


class DuctorConversationEntity(conversation.ConversationEntity):
    """Ductor conversation agent for Home Assistant Assist."""

    _attr_name = "Ductor"
    _attr_has_entity_name = False

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize the entity."""
        self._config_entry = config_entry
        self._attr_unique_id = config_entry.entry_id

    async def async_added_to_hass(self) -> None:
        """Register this entity as a selectable Assist conversation agent."""
        await super().async_added_to_hass()
        conversation.async_set_agent(self.hass, self._config_entry, self)

    async def async_will_remove_from_hass(self) -> None:
        """Unregister this conversation agent."""
        conversation.async_unset_agent(self.hass, self._config_entry)
        await super().async_will_remove_from_hass()

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        """Return supported languages."""
        return MATCH_ALL

    async def async_process(
        self,
        user_input: conversation.ConversationInput,
    ) -> conversation.ConversationResult:
        """Process a sentence through the configured Ductor endpoint."""
        settings = {**self._config_entry.data, **self._config_entry.options}
        client = DuctorAssistClient(async_get_clientsession(self.hass), settings)

        response = intent.IntentResponse(language=user_input.language)
        try:
            text, conversation_id = await client.async_ask(
                user_input.text,
                user_input.language,
                user_input.conversation_id,
            )
        except DuctorAssistError as err:
            response.async_set_error(
                "cannot_connect",
                f"Ductor Assist neni dostupny: {err}",
            )
            return conversation.ConversationResult(
                response=response,
                conversation_id=user_input.conversation_id,
            )

        response.async_set_speech(text)
        return conversation.ConversationResult(
            response=response,
            conversation_id=conversation_id,
            continue_conversation=False,
        )

    async def async_prepare(self, language: str | None = None) -> None:
        """Prepare the agent."""
