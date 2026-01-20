# animation.py
import time


def ease_out_cubic(t: float) -> float:
    """
    缓入（快 → 慢）
    t ∈ [0, 1]
    """
    return 1 - pow(1 - t, 3)


class Tween:
    def __init__(self, start, end, duration, easing=ease_out_cubic):
        self.start = start
        self.end = end
        self.duration = duration
        self.easing = easing

        self.start_time = time.perf_counter()
        self.finished = False
        self.value = start

    def update(self):
        if self.finished:
            return self.value

        elapsed = time.perf_counter() - self.start_time
        t = min(elapsed / self.duration, 1.0)

        k = self.easing(t)
        self.value = self.start + (self.end - self.start) * k

        if t >= 1.0:
            self.finished = True

        return self.value
