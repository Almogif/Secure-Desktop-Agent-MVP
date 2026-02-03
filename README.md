# Flow V0

Flow is a quiet writing environment with inline AI suggestions and word-level annotations.

## Setup

```bash
npm install
```

Create a `.env.local` file with:

```bash
GEMINI_API_KEY=your_key_here
```

Run the app:

```bash
npm run dev
```

## Notes

- Suggestions come from `/api/suggest` using the Gemini REST API.
- Draft text and annotations are stored in localStorage.
=======
# Secure Desktop Agent MVP

This repository contains a security-first MVP for a Telegram-controlled desktop agent. The agent only executes strict JSON commands validated by schema and allowlists, and defaults to SAFE mode.

## Repo Layout

- `agent/` - Python agent implementation.
- `schemas/` - JSON schema for commands.
- `workflows/` - Local workflow definitions.
- `docs/` - Setup, threat model, examples, troubleshooting.
- `tests/` - Unit tests for security controls.

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set environment variables:
   ```bash
   export TELEGRAM_BOT_TOKEN="..."
   export ALLOWED_TELEGRAM_USER_IDS="123456789"
   ```
3. Run the agent:
   ```bash
   python -m agent.main run
   ```

See `docs/setup.md` for detailed onboarding and security controls.

