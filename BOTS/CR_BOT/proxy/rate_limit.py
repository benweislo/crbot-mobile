import time
from collections import defaultdict


class RateLimiter:
    """Simple in-memory rate limiter per key."""

    def __init__(self, max_per_minute: int = 10, max_per_day: int = 50):
        self.max_per_minute = max_per_minute
        self.max_per_day = max_per_day
        self._minute_windows: dict[str, list[float]] = defaultdict(list)
        self._day_windows: dict[str, list[float]] = defaultdict(list)

    def check(self, key: str) -> bool:
        """Check if key is within rate limits. Records the attempt if allowed."""
        now = time.time()
        minute_ago = now - 60
        day_ago = now - 86400

        self._minute_windows[key] = [t for t in self._minute_windows[key] if t > minute_ago]
        self._day_windows[key] = [t for t in self._day_windows[key] if t > day_ago]

        if len(self._minute_windows[key]) >= self.max_per_minute:
            return False
        if len(self._day_windows[key]) >= self.max_per_day:
            return False

        self._minute_windows[key].append(now)
        self._day_windows[key].append(now)
        return True
