# Instagram DM Bot — Phase 1 (n8n workflow)

Auto-replies to Instagram DMs via the Meta webhook, classifies intent with
Claude, answers routine questions from static templates or the model, and
hands off to a human (with a Telegram alert) when it's unsure — pausing the
bot for that conversation for 24h.

Import `workflow.json` into n8n (Workflows → Import from File), then
complete the setup below before going live.

## Architecture

```
Webhook (GET)  → verify hub.challenge (Meta handshake, one-time)
Webhook (POST) → respond 200 immediately → parse payload
                 → drop echoes/empty messages
                 → look up conversation state (Postgres)
                 → if bot_paused_until is in the future: log inbound only, stop
                 → fetch last 6 messages, build prompt
                 → call Claude (forced JSON via tool-use schema)
                 → route by intent:
                     price/installation/delivery/warranty/power → static template
                     faq (confidence ≥ 0.7)                     → Claude's own reply
                     wants_manager/handoff/low confidence        → handoff message
                                                                    + pause bot 24h
                                                                    + Telegram alert
                 → send Instagram reply → write audit log (in + out)
```

## Credentials

| Credential | Used by | Notes |
|---|---|---|
| Postgres | `Postgres - *` nodes | See schema below |
| Telegram API | `Telegram - Notify Handoff` | Bot token from @BotFather |

Attach these after import — the workflow references them by name
(`Postgres account`, `Telegram account`); relink to your own credential of
the matching type if the names don't line up.

## Environment variables

Set these on the n8n instance (not stored in the workflow file):

- `META_VERIFY_TOKEN` — a secret string you invent; must match the token you
  enter in the Meta App dashboard's webhook subscription
- `META_PAGE_ACCESS_TOKEN` — Page Access Token from Meta for Developers
- `ANTHROPIC_API_KEY` — Claude API key
- `TELEGRAM_CHAT_ID` — your chat/user ID for handoff alerts

## Database schema

```sql
CREATE TABLE conversations (
  sender_id TEXT PRIMARY KEY,
  bot_paused_until TIMESTAMPTZ,
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE messages (
  id BIGSERIAL PRIMARY KEY,
  sender_id TEXT NOT NULL,
  direction TEXT NOT NULL CHECK (direction IN ('in', 'out')),
  text TEXT,
  intent TEXT,
  confidence NUMERIC,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Optional, v1.1: move static template wording out of the workflow
-- CREATE TABLE templates (
--   intent TEXT PRIMARY KEY,
--   text_uz TEXT NOT NULL
-- );
```

## Meta webhook setup

1. Deploy this workflow and copy the production webhook URL for path
   `ig-webhook` (n8n shows separate GET/POST URLs pointing at the same path).
2. In the Meta App dashboard, add the webhook URL + your `META_VERIFY_TOKEN`,
   subscribe to the `messages` field on the Instagram/Page object.
3. Meta calls the GET URL once to verify (`hub.challenge` handshake), then
   sends POST events for each DM.

## Placeholders to fill in before go-live

- **`Code - Build LLM Prompt`**: replace the `SYSTEM_KB` template string with
  your real product facts (price, installation, delivery, warranty, specs)
  and any hard rules the bot must follow.
- **`Code - Static Template Lookup`**: replace the placeholder Uzbek wording
  per intent with your approved copy.
- **`Set - Handoff Message`**: replace the default handoff line if you want
  different wording.
- **`Switch - Route Intent`**: the `faq` confidence threshold starts at 0.7 —
  tune after watching real traffic and the audit log.
- **Model choice**: the Claude call defaults to `claude-haiku-4-5-20251001`
  for low-latency/cost at high volume; switch to `claude-sonnet-5` in the
  HTTP Request node's body if you want higher-quality classification instead.

## Known gaps from this scaffold

- No message-id dedup against `messages` yet (the blueprint calls this out
  as a nice-to-have); add an `IF` checking `message_id` against a lookup
  query if Meta's occasional redelivery becomes a problem.
- `Postgres - Get Recent History` and `Code - Build LLM Prompt` assume a
  single Postgres node's output ordering; double check history ends up
  oldest-first once real data is flowing.
- Credential IDs are left blank in `workflow.json`; n8n will prompt you to
  relink them to your own Postgres/Telegram credentials on first open.
