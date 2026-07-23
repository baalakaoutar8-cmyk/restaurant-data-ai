"""
browser.py

Gestion du navigateur Playwright.

Responsabilités
----------------
- Lancer Chromium
- Réutiliser une session existante
- Créer une page
- Sauvegarder la session
- Fermer proprement le navigateur
"""

from pathlib import Path

from playwright.sync_api import BrowserContext, Page, sync_playwright # type:ignore

from scraping.common.logger import get_logger

logger = get_logger(__name__)


from pathlib import Path

from playwright.sync_api import sync_playwright # type:ignore

from scraping.common.logger import get_logger

logger = get_logger(__name__)


class Browser:

    def __init__(
        self,
        headless=False,
        timeout=60000
    ):

        self.headless = headless
        self.timeout = timeout

        self.playwright = None
        self.context = None
        self.page = None


    def start(self):

        logger.info("Lancement navigateur...")

        self.playwright = sync_playwright().start()


        user_data = Path(
            "data/chrome_profile"
        )

        user_data.mkdir(
            parents=True,
            exist_ok=True
        )


        self.context = self.playwright.chromium.launch_persistent_context(

            user_data_dir=str(user_data),

            headless=self.headless,

            viewport={
                "width": 1366,
                "height": 768
            },

            locale="en-US",

            timezone_id="Asia/Qatar",

            args=[
                "--disable-blink-features=AutomationControlled",
            ],

        )


        self.page = self.context.pages[0]


        if not self.page:
            self.page = self.context.new_page()


        self.page.set_default_timeout(
            self.timeout
        )


        logger.info(
            "Navigateur prêt"
        )


        return self.page



    def stop(self):

        logger.info(
            "Fermeture navigateur..."
        )


        if self.context:
            self.context.close()


        if self.playwright:
            self.playwright.stop()