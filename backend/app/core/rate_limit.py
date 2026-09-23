from collections import defaultdict, deque
from time import monotonic


class SimpleRateLimiter:
	def __init__(self) -> None:
		self._requests: dict[str, deque[float]] = defaultdict(deque)

	def check(self, key: str, limit: int, window_seconds: int = 60) -> None:
		now = monotonic()
		requests = self._requests[key]
		while requests and now - requests[0] >= window_seconds:
			requests.popleft()
		if len(requests) >= limit:
			raise RuntimeError("rate limit exceeded")
		requests.append(now)


limiter = SimpleRateLimiter()
