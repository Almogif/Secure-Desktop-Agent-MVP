from agent.security import RateLimiter


def test_rate_limiter():
    limiter = RateLimiter(limit_per_minute=2)
    assert limiter.allow(1, now=1000).allowed
    assert limiter.allow(1, now=1001).allowed
    result = limiter.allow(1, now=1002)
    assert result.allowed is False
    assert result.retry_after_s is not None
