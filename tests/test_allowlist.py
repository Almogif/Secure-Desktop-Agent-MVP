from agent.security import AllowList


def test_allowlist_checks():
    allowlist = AllowList({"notepad": {"command": ["notepad.exe"]}}, {"daily_email_triage"})
    assert allowlist.validate_app("notepad")
    assert not allowlist.validate_app("calc")
    assert allowlist.validate_workflow("daily_email_triage")
    assert not allowlist.validate_workflow("unknown")
