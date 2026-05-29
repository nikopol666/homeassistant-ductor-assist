"""Constants for Ductor Assist."""

from __future__ import annotations

DOMAIN = "ductor_assist"

CONF_PROVIDER = "provider"
CONF_ENDPOINT_URL = "endpoint_url"
CONF_API_KEY = "api_key"
CONF_MODEL = "model"
CONF_SYSTEM_PROMPT = "system_prompt"
CONF_TIMEOUT = "timeout"
CONF_VERIFY_SSL = "verify_ssl"

PROVIDER_OPENAI_COMPATIBLE = "openai_compatible"
PROVIDER_BRIDGE = "bridge"

DEFAULT_PROVIDER = PROVIDER_OPENAI_COMPATIBLE
DEFAULT_MODEL = "gpt-4.1-mini"
DEFAULT_TIMEOUT = 60
DEFAULT_VERIFY_SSL = True
DEFAULT_SYSTEM_PROMPT = (
    "Jsi Ductor, hlasovy asistent uzivatele v Home Assistant. "
    "Odpovidej cesky, strucne a prakticky. Pokud nemas jistotu, rekni co chybi."
)

BRIDGE_RESPONSE_KEYS = ("response", "text", "message", "answer")
