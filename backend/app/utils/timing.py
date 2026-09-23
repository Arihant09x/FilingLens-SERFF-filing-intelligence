from time import perf_counter


class Timer:
	def __enter__(self):
		self.started = perf_counter()
		return self

	def __exit__(self, *_):
		self.duration_ms = round((perf_counter() - self.started) * 1000, 2)
