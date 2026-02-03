import time
from pathlib import Path

from agent.storage import JsonStore, ReplayCache


def test_replay_cache():
    store = JsonStore(Path(".agent_data/test_replay.json"))
    cache = ReplayCache(store, ttl_seconds=1)
    assert cache.seen("abc", now=1000) is False
    assert cache.seen("abc", now=1000) is True
    assert cache.seen("abc", now=1002) is False
