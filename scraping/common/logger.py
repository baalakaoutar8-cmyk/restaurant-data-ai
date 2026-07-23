"""
Gestion centralisée des logs du module de scraping.
"""

import logging
from pathlib import Path

from scraping.common.config import LOGS_DIR

# Création du dossier des logs si nécessaire
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def get_logger(name: str, log_file: str = "scraping.log") -> logging.Logger:
    """
    Crée ou retourne un logger configuré.

    Parameters
    ----------
    name : str
        Nom du logger (généralement __name__).
    log_file : str
        Nom du fichier de log.

    Returns
    -------
    logging.Logger
    """

    logger = logging.getLogger(name)

    # Évite d'ajouter plusieurs handlers si le logger existe déjà
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)

    # Format des messages
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Écriture dans un fichier
    file_handler = logging.FileHandler(
        LOGS_DIR / log_file,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Affichage dans le terminal
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def log_info(logger: logging.Logger, message: str):
    """Écrit un message d'information."""
    logger.info(message)


def log_warning(logger: logging.Logger, message: str):
    """Écrit un avertissement."""
    logger.warning(message)


def log_error(logger: logging.Logger, message: str):
    """Écrit un message d'erreur."""
    logger.error(message)


def log_exception(logger: logging.Logger, message: str):
    """
    Écrit une exception avec sa traceback.
    À utiliser dans un bloc try/except.
    """
    logger.exception(message)