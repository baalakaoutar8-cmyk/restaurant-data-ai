"""
Gestion du rate limiting.
"""

import random
import time

from scraping.common.config import (
    MIN_DELAY,
    MAX_DELAY,
    MAX_REQUESTS_PER_MINUTE,
)


class RateLimiter:
    """
    Limiteur de débit des requêtes.
    """

    def __init__(self):
        self.request_times = []

    def wait(self):
        """
        Attend un délai aléatoire.
        """
        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        time.sleep(delay)

    def respect_rate_limit(self):
        """
        Respecte le nombre maximal de requêtes par minute.
        """
        current = time.time()

        self.request_times = [
            t for t in self.request_times
            if current - t < 60
        ]

        if len(self.request_times) >= MAX_REQUESTS_PER_MINUTE:
            sleep_time = 60 - (current - self.request_times[0])
            if sleep_time > 0:
                time.sleep(sleep_time)

        self.request_times.append(time.time())

    def pause(self):
        """
        Applique le délai + le contrôle du débit.
        """
        self.respect_rate_limit()
        self.wait()


rate_limiter = RateLimiter()