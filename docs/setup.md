# Setup & Onboarding Checklist

## Prerequisites
- Windows 10/11 desktop.
- Python 3.10+.
- Telegram bot token.

## Install Dependencies
```bash
pip install -r requirements.txt
```

## Configure Environment
```bash
set TELEGRAM_BOT_TOKEN=your-token-here
set ALLOWED_TELEGRAM_USER_IDS=123456789,987654321
```

Optional override config:
- `AGENT_CONFIG_PATH` can point to a JSON file with allowlist and safety overrides.

## First Run Checklist
1. Confirm allowlisted Telegram user IDs.
2. Confirm allowlisted apps in `agent/config.py` or override JSON.
3. Start in SAFE mode: `python -m agent.main safe`.
4. Test a screenshot: `python -m agent.main test_screenshot`.
5. Arm the agent: `python -m agent.main arm`.
6. Run the agent: `python -m agent.main run`.

## Kill Switch
- Global hotkey: `Ctrl+Alt+S` toggles SAFE/ARMED.

## Data Storage
- `./.agent_data/` stores audit logs, replay cache, and screenshots.
