"""
Fonctions utilitaires communes au module de scraping.
"""

import json
import re
from datetime import datetime
from pathlib import Path

import pandas as pd

from scraping.common.config import (
    RAW_DATA_DIR,
    INTERIM_DATA_DIR,
    PROCESSED_DATA_DIR,
    CSV_ENCODING,
)


# ==========================================================
# Dates
# ==========================================================

def now():
    """Retourne la date et l'heure actuelle."""
    return datetime.now()


def timestamp():
    """Retourne un timestamp sous forme de chaîne."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


# ==========================================================
# Création de dossiers
# ==========================================================

def ensure_directory(path):
    """
    Crée un dossier (et ses parents) s'il n'existe pas.
    """
    Path(path).mkdir(parents=True, exist_ok=True)


# ==========================================================
# Préparation d'un chemin de sortie
# ==========================================================

def prepare_output_path(folder, filename):
    """
    Construit le chemin complet du fichier et crée
    automatiquement tous les dossiers nécessaires.

    Exemple :

        folder = data/raw
        filename = intermediate/restaurants.csv

    -> crée automatiquement :

        data/raw/intermediate/
    """

    filepath = Path(folder) / filename

    ensure_directory(filepath.parent)

    return filepath


# ==========================================================
# Sauvegarde CSV
# ==========================================================

def save_csv(
    df: pd.DataFrame,
    filename,
    folder=RAW_DATA_DIR,
):
    """
    Sauvegarde un DataFrame au format CSV.

    Les sous-dossiers éventuels contenus dans filename
    sont créés automatiquement.
    """

    filepath = prepare_output_path(
        folder,
        filename,
    )

    df.to_csv(
        filepath,
        index=False,
        encoding=CSV_ENCODING,
    )

    return filepath


# ==========================================================
# Lecture CSV
# ==========================================================

def load_csv(
    filename,
    folder=RAW_DATA_DIR,
):
    """
    Charge un fichier CSV.
    """

    filepath = Path(folder) / filename

    return pd.read_csv(filepath)


# ==========================================================
# Sauvegarde JSON
# ==========================================================

def save_json(
    data,
    filename,
    folder=INTERIM_DATA_DIR,
):
    """
    Sauvegarde un dictionnaire ou une liste au format JSON.
    """

    filepath = prepare_output_path(
        folder,
        filename,
    )

    with open(
        filepath,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False,
        )

    return filepath


# ==========================================================
# Lecture JSON
# ==========================================================

def load_json(
    filename,
    folder=INTERIM_DATA_DIR,
):
    """
    Charge un fichier JSON.
    """

    filepath = Path(folder) / filename

    with open(
        filepath,
        encoding="utf-8",
    ) as f:

        return json.load(f)


# ==========================================================
# Génération d'un nom de fichier
# ==========================================================

def generate_filename(
    prefix,
    extension="csv",
):
    """
    Exemple :

        restaurants_20260714_153050.csv
    """

    return f"{prefix}_{timestamp()}.{extension}"


# ==========================================================
# Nettoyage de texte
# ==========================================================

def clean_text(text):
    """
    Nettoie une chaîne de caractères.
    """

    if text is None:
        return ""

    text = str(text)

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# ==========================================================
# Suppression des doublons
# ==========================================================

def remove_duplicates(df):
    """
    Supprime les doublons d'un DataFrame.
    """

    return df.drop_duplicates()


# ==========================================================
# Vérification de fichier
# ==========================================================

def file_exists(filepath):
    """
    Vérifie si un fichier existe.
    """

    return Path(filepath).exists()


# ==========================================================
# Fusion de DataFrames
# ==========================================================

def merge_dataframes(dataframes):
    """
    Concatène plusieurs DataFrames.
    """

    if not dataframes:
        return pd.DataFrame()

    return pd.concat(
        dataframes,
        ignore_index=True,
    )


# ==========================================================
# Export Excel
# ==========================================================

def save_excel(
    df,
    filename,
    folder=PROCESSED_DATA_DIR,
):
    """
    Sauvegarde un DataFrame au format Excel.
    """

    filepath = prepare_output_path(
        folder,
        filename,
    )

    df.to_excel(
        filepath,
        index=False,
    )

    return filepath


# ==========================================================
# Affichage console
# ==========================================================

def print_separator():
    print("=" * 80)


def print_title(title):
    print_separator()
    print(title)
    print_separator()