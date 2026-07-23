"""
Gestion du navigateur Playwright.
"""

from playwright.sync_api import sync_playwright

from scraping.common.logger import get_logger

logger = get_logger(__name__)


class BrowserManager:

    def __init__(self, headless=True):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def start(self):

        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=self.headless
        )

        self.context = self.browser.new_context()

        self.page = self.context.new_page()

        logger.info("Navigateur lancé.")

        return self.page

    def close(self):

        if self.context:
            self.context.close()

        if self.browser:
            self.browser.close()

        if self.playwright:
            self.playwright.stop()

        logger.info("Navigateur fermé.")


browser_manager = BrowserManager()
"""
browser.py

Gestion centralisée du navigateur Selenium.

Responsabilités :
- Ouvrir Chrome
- Configurer ChromeOptions
- Définir le User-Agent
- Ouvrir une URL
- Attendre le chargement
- Fermer le navigateur
"""

import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class Browser:
    """
    Gestionnaire du navigateur Selenium.
    """

    def __init__(
        self,
        headless: bool = False,
        window_size: str = "1920,1080",
    ):
        """
        Parameters
        ----------
        headless : bool
            Lance Chrome sans interface graphique.

        window_size : str
            Taille de la fenêtre.
        """

        options = Options()

        if headless:
            options.add_argument("--headless=new")

        options.add_argument(f"--window-size={window_size}")

        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        options.add_argument("--disable-blink-features=AutomationControlled")

        options.add_argument(
            "--user-agent=Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/137.0.0.0 "
            "Safari/537.36"
        )

        options.add_experimental_option(
            "excludeSwitches",
            ["enable-automation"]
        )

        options.add_experimental_option(
            "useAutomationExtension",
            False
        )

        self.driver = webdriver.Chrome(
            service=Service(
                ChromeDriverManager().install()
            ),
            options=options,
        )

        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

    # ======================================================

    def get(self, url: str):
        """
        Ouvre une URL.

        Parameters
        ----------
        url : str
        """

        self.driver.get(url)

    # ======================================================

    def wait(self, seconds: int = 3):
        """
        Attend quelques secondes.

        Parameters
        ----------
        seconds : int
        """

        time.sleep(seconds)

    # ======================================================

    def maximize(self):
        """
        Agrandit la fenêtre.
        """

        self.driver.maximize_window()

    # ======================================================

    def page_source(self):
        """
        Retourne le HTML courant.
        """

        return self.driver.page_source

    # ======================================================

    def current_url(self):
        """
        Retourne l'URL courante.
        """

        return self.driver.current_url

    # ======================================================

    def quit(self):
        """
        Ferme complètement le navigateur.
        """

        self.driver.quit()