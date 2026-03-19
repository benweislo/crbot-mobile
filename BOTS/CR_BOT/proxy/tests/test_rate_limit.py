import pytest
from proxy.rate_limit import RateLimiter


class TestRateLimiter:
    def test_allows_under_limit(self):
        limiter = RateLimiter(max_per_minute=5, max_per_day=100)
        for _ in range(5):
            assert limiter.check("key1") is True

    def test_blocks_over_minute_limit(self):
        limiter = RateLimiter(max_per_minute=2, max_per_day=100)
        assert limiter.check("key1") is True
        assert limiter.check("key1") is True
        assert limiter.check("key1") is False

    def test_different_keys_independent(self):
        limiter = RateLimiter(max_per_minute=1, max_per_day=100)
        assert limiter.check("key1") is True
        assert limiter.check("key2") is True
        assert limiter.check("key1") is False

    def test_blocks_over_day_limit(self):
        limiter = RateLimiter(max_per_minute=100, max_per_day=2)
        assert limiter.check("key1") is True
        assert limiter.check("key1") is True
        assert limiter.check("key1") is False
