# Threat Model Summary

## Assumptions
- Telegram channel can be attacked or messages replayed.
- Desktop environment is sensitive.
- Network exposure should be outbound only.

## Key Threats & Mitigations
- **Command injection**: only strict JSON schema accepted; allowlists enforced.
- **Replay attacks**: `request_id` cache with TTL and persistent `last_update_id` tracking.
- **Privilege abuse**: SAFE mode default; allowlisted apps only.
- **Data leakage**: screenshots blocked when active window not allowlisted; redaction in logs.
- **DoS & spam**: rate limiting per user ID.
- **Workflow abuse**: workflow IDs allowlisted; step count + timeout enforced.

## Residual Risks
- UI automation can be brittle; agent defaults to refusal if UI targets are not found.
- Screenshot redaction is allowlist-based and should be tuned for production.
