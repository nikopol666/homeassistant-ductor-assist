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

## Select in Assist

After setup, go to:

Settings -> Voice assistants -> your pipeline -> Conversation agent -> Ductor

## Notes

This first version returns spoken responses through Assist. Direct Home
Assistant entity control should be handled either by the endpoint you configure,
or added later through a dedicated bridge that can call the Home Assistant API.
