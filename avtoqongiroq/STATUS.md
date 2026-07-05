# Avtoqongiroq — Instagram DM Bot: Project Status

**Last updated:** 2026-07-05
**Workflow:** [Instagram DM Bot — Phase 1](https://ktimuz.app.n8n.cloud/workflow/YtIbUtyuGhs67SuC) on n8n Cloud (`ktimuz.app.n8n.cloud`)
**Status:** 🟡 Almost ready — one missing token and content blanks stand between now and go-live

## What this project is

An Instagram DM auto-reply bot ("avtoqongiroq") for a business page. When a customer
sends a DM, the bot classifies the message with an LLM, answers common questions
automatically in Uzbek, logs every conversation to Google Sheets, and pings the owner
on Telegram whenever it isn't confident about its answer.

## How it works (current architecture)

```
Instagram DM
   │  (Meta webhook → POST /webhook/ig-webhook)
   ▼
Parse payload ──► skip echoes / empty messages
   ▼
Google Sheets: read last messages of this customer (conversation history)
   ▼
Gemini 2.5 Flash: classify intent + draft Uzbek reply (structured JSON:
   intent / reply / confidence)
   ▼
Route by intent:
   ├─ price, installation, delivery, warranty, power → fixed Uzbek template reply
   ├─ faq with confidence ≥ 0.7                      → send the LLM's own reply
   └─ anything else (unsure / wants a manager)       → send the LLM's reply anyway
                                                       + ⚠️ Telegram alert to owner
   ▼
Send reply via Instagram Graph API
   ▼
Google Sheets: append 2 log rows (customer message + bot reply)
```

### Key design decisions made along the way

- **Storage = Google Sheets, not Postgres.** The original design used a Postgres
  database (2 tables). Replaced with a single Google Sheet — spreadsheet
  **"Avtoqongiroq"**, tab **`messages`**, columns:
  `sender_id | direction | text | intent | confidence | created_at`.
- **LLM = Google Gemini 2.5 Flash** (was Anthropic Claude). Called via HTTP with a
  JSON response schema so output is always machine-parseable.
- **No human-handoff pause.** Originally an unsure bot said "a manager will contact
  you" and silenced itself for 24 h. Now it always replies itself and only *notifies*
  the owner on Telegram (in Uzbek). No pause, no handoff message.
- **Secrets are inlined in nodes, not env vars** — n8n Cloud does not support `$env`.
- **Telegram uses a plain HTTP call** (`api.telegram.org/bot…/sendMessage`), so no
  Telegram credential object is needed in n8n.

## What is DONE and verified ✅

| Piece | State |
|---|---|
| Workflow structure (21 nodes, both webhook branches) | Built and rewired |
| Gemini API key | Inlined in the Gemini HTTP node |
| Google Sheets credential ("Google Sheets account", OAuth2) | Created by owner, attached to both Sheets nodes |
| Spreadsheet + tab selection | "Avtoqongiroq" / `messages` selected in both nodes |
| Sheets read + append | **Live-tested** — real rows written successfully |
| Telegram alerts (bot @avtoqungiroqbot → chat 217407561) | **Live-tested** — real messages delivered, wording in Uzbek |
| Meta webhook verify token | Hardcoded: `kt_ig_verify_2026` |
| End-to-end logic (routing, unsure branch, logging) | Verified with simulated test executions |

## What is STILL NEEDED before go-live ❌

1. **`META_PAGE_ACCESS_TOKEN`** — the Facebook Page access token. Without it the
   "Send Instagram Reply" node cannot send anything. *(Owner must provide; it gets
   inlined into the node.)*
2. **Knowledge-base facts** — the system prompt in "Code - Build LLM Prompt" still has
   `[FILL IN]` placeholders for price, installation, delivery, warranty, and specs.
   The bot cannot answer real questions until these are filled.
3. **Template wording review** — the canned Uzbek replies in
   "Code - Static Template Lookup" are placeholders ("we'll inform you shortly...").
4. **Meta developer console setup** — subscribe the Instagram webhook to
   `https://ktimuz.app.n8n.cloud/webhook/ig-webhook` with verify token
   `kt_ig_verify_2026`, messaging events enabled, Instagram Business account linked
   to the Facebook Page.
5. **Activate the workflow** — it is currently unpublished/inactive.

## Housekeeping / security ⚠️

- A sticky note inside the workflow still contains **plain-text secrets** (Gemini key,
  Telegram bot token, Google OAuth client secret). **Delete it** once setup is done,
  and consider rotating the Telegram token (BotFather → `/revoke`) after go-live.
- Test artifacts: a few test rows in the `messages` sheet (sender ids
  `test_sender_001`, `telegram_test_sender`) — safe to delete.
- The confidence threshold for trusting an LLM faq answer is **0.7** (in
  "Switch - Route Intent") — tune after observing real traffic.

## Nice-to-haves considered but not done

- Telegram alerts to a **group chat** instead of the owner's private chat (add
  @avtoqungiroqbot to a group and swap the chat ID).
- Rotating/managing secrets via n8n credentials instead of inline values.
