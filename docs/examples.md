# Example Commands

All commands must be JSON. Include a `request_id`.

## Screenshot
```json
{"request_id":"11111111","command":"screenshot","params":{"mode":"full"}}
```

## Open Notepad
```json
{"request_id":"22222222","command":"open_app","params":{"app_id":"notepad"}}
```

## Type Text
```json
{"request_id":"33333333","command":"type_text","params":{"text":"hello from phone"}}
```

## Click UI Element
```json
{"request_id":"44444444","command":"click","params":{"window_title":"Notepad","target":{"by":"automation_id","value":"15"}}}
```

## Run Workflow
```json
{"request_id":"55555555","command":"run_workflow","params":{"workflow_id":"daily_email_triage"}}
```
