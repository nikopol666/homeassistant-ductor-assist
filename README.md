# Ductor Assist for Home Assistant

Ductor Assist is a Home Assistant custom integration that exposes a conversation
agent for Assist. It can call either:

- an OpenAI-compatible `/v1/chat/completions` endpoint, such as a local proxy;
- a generic Ductor bridge endpoint that accepts JSON and returns a text response.

This is intended as a small bridge layer: Home Assistant keeps the voice pipeline
for wake word, STT and TTS, while Ductor provides the conversation response.

## Install with HACS

1. HACS -> Integrations -> Custom repositories.
2. Add `https://github.com/nikopol666/homeassistant-ductor-assist`.
3. Category: Integration.
4. Install **Ductor Assist**.
5. Restart Home Assistant.
6. Settings -> Devices & services -> Add integration -> Ductor Assist.

## OpenAI-Compatible Mode

Use this when you already have an OpenAI-compatible API, for example:

```text
Provider: OpenAI-compatible chat completions
Endpoint URL: http://192.168.88.42:8317/v1
Bearer token / API key: your proxy key, if required
Model: gpt-4.1-mini
```

The integration appends `/chat/completions` if the URL does not already end
with it.

## Generic Bridge Mode

Use this when you run your own Ductor HTTP bridge.

Request:

```json
{
  "text": "Turn on the kitchen light",
  "language": "en",
  "conversation_id": "abc",
  "system_prompt": "You are Ductor...",
  "source": "home_assistant_assist"
}
```

Response can use any of these response text keys:

```json
{
  "response": "Done.",
  "conversation_id": "abc"
}
```

Accepted response keys are `response`, `text`, `message` and `answer`.

## Home Assistant Native Control

Ductor Assist first lets Home Assistant handle native control intents and
sentence triggers. This keeps common voice commands local to Home Assistant:

- lights, switches, scenes and scripts;
- climate, covers and other domains supported by Home Assistant Assist;
- Home Assistant voice timers.

If Home Assistant cannot handle the sentence, Ductor Assist falls back to the
configured OpenAI-compatible endpoint or Ductor bridge. This is where broader
Ductor features such as Mealie, homelab tools or memory should be connected.

## Select in Assist

After setup, go to:

Settings -> Voice assistants -> your pipeline -> Conversation agent -> Ductor

## Continued Conversation

In Ductor Assist options, enable **Continue listening after responses** when
your voice satellite/card supports Home Assistant's continued conversation
flow. When enabled, Ductor Assist returns `continue_conversation=True` for
native Home Assistant intents and Ductor bridge responses.

## Notes

The OpenAI-compatible mode is only a language endpoint. Broader tool access
requires a Ductor bridge endpoint with an explicit permission policy.
