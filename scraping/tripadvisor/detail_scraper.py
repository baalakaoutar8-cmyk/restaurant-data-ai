"""
detail_scraper.py

Module chargé d'ouvrir la page détaillée d'un restaurant via Playwright
et d'exécuter l'extraction via TripAdvisorParser.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, Any
from playwright.async_api import Page

from scraping.tripadvisor.parser import TripAdvisorParser

logger = logging.getLogger(__name__)


async def scrape_restaurant_detail(page: Page, url: str, parser: TripAdvisorParser) -> Dict[str, Any]:
    """
    Ouvre la page d'un restaurant et extrait l'ensemble des 22 champs requis.

    :param page: L'instance Page de Playwright.
    :param url: L'URL TripAdvisor du restaurant.
    :param parser: L'instance de TripAdvisorParser.
    :return: Un dictionnaire contenant l'ensemble des détails du restaurant.
    """
    try:
        logger.info("Navigation vers : %s", url)

        # 1. Chargement de la page avec un timeout de 30s
        response = await page.goto(url, wait_until="domcontentloaded", timeout=30000)

        if not response or response.status >= 400:
            logger.warning("Erreur de réponse HTTP (%s) pour : %s", response.status if response else "No response", url)
            return {}

        # 2. Attente rapide pour le chargement des scripts/elements JS
        await page.wait_for_timeout(1500)

        # 3. Récupération du code source HTML
        html_content = await page.content()

        # 4. Appel à votre méthode parse_detail existante dans parser.py
        detail_data = parser.parse_detail(html_content, url)

        return detail_data

    except Exception as e:
        logger.error("Erreur lors de l'extraction des détails de %s : %s", url, e)
        return {}