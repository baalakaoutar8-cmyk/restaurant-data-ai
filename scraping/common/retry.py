"""
Gestion des tentatives automatiques.
"""

import time
from functools import wraps

from scraping.common.config import (
    MAX_RETRIES,
    RETRY_DELAY,
)

from scraping.common.logger import get_logger

logger = get_logger(__name__)


def retry(
    retries=MAX_RETRIES,
    delay=RETRY_DELAY,
    exceptions=(Exception,),
):
    """
    Décorateur permettant de réessayer une fonction.
    """

    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):

            last_exception = None

            for attempt in range(1, retries + 1):

                try:
                    return function(*args, **kwargs)

                except exceptions as e:

                    last_exception = e

                    logger.warning(
                        f"Tentative {attempt}/{retries} échouée : {e}"
                    )

                    if attempt < retries:
                        time.sleep(delay)

            logger.error("Nombre maximal de tentatives atteint.")

            raise last_exception

        return wrapper

    return decorator