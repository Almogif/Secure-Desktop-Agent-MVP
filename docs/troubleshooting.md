# Troubleshooting

## Agent stuck in SAFE mode
- Check `Ctrl+Alt+S` hotkey.
- Use `python -m agent.main arm`.

## Screenshot blocked
- Ensure active window title is allowlisted in config.
- Update `allowed_windows` in config override file.

## Schema validation errors
- Validate JSON formatting.
- Ensure command-specific params match schema.

## Rate limit errors
- Increase `rate_limit_per_minute` in override config.
- Avoid rapid repeated commands.
