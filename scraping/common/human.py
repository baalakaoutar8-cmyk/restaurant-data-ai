"""
human.py

Fonctions utilitaires simulant un comportement humain.

Responsabilités
----------------
- Délais aléatoires
- Scroll progressif
"""

import random
import time

from playwright.sync_api import Page


def short_pause():
    """
    Pause courte.
    """
    time.sleep(random.uniform(1.5, 3.5))


def medium_pause():
    """
    Pause moyenne.
    """
    time.sleep(random.uniform(3, 6))


def long_pause():
    """
    Pause longue.
    """
    time.sleep(random.uniform(8, 15))


def custom_pause(min_seconds: float, max_seconds: float):
    """
    Pause personnalisée.
    """
    time.sleep(random.uniform(min_seconds, max_seconds))


def human_scroll(page: Page, steps: int = 5):
    """
    Effectue un scroll progressif.
    """

    for _ in range(steps):

        pixels = random.randint(300, 700)

        page.mouse.wheel(0, pixels)

        time.sleep(random.uniform(0.4, 1.0))