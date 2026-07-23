"""
Fonctions utilitaires de nettoyage et de transformation des données.
"""

import re
import unicodedata
from urllib.parse import urlparse


def clean_text(text):
    """
    Nettoie une chaîne de caractères.
    """
    if not text:
        return ""

    text = str(text).strip()
    text = re.sub(r"\s+", " ", text)

    return text


def normalize_text(text):
    """
    Supprime les accents et convertit en minuscules.
    """
    if not text:
        return ""

    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ASCII", "ignore").decode("utf-8")

    return text.lower().strip()


def slugify(text):
    """
    Convertit une chaîne en slug.
    Exemple :
    Café de Paris -> cafe-de-paris
    """
    text = normalize_text(text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text)

    return text.strip("-")


def clean_phone(phone):
    """
    Nettoie un numéro de téléphone.
    """
    if not phone:
        return ""

    phone = re.sub(r"[^\d+]", "", phone)

    return phone


def clean_email(email):
    """
    Valide une adresse email.
    """
    if not email:
        return ""

    email = email.strip().lower()

    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    if re.match(pattern, email):
        return email

    return ""


def clean_url(url):
    """
    Vérifie qu'une URL est valide.
    """
    if not url:
        return ""

    parsed = urlparse(url)

    if parsed.scheme and parsed.netloc:
        return url

    return ""


def clean_price(price):
    """
    Nettoie le prix.
    """
    if not price:
        return ""

    return str(price).strip()


def clean_rating(rating):
    """
    Convertit une note en float.
    """
    try:
        return float(rating)
    except Exception:
        return None


def clean_review_count(value):
    """
    Convertit le nombre d'avis en entier.
    """
    try:
        return int(value)
    except Exception:
        return 0


def unique_list(values):
    """
    Supprime les doublons d'une liste.
    """
    if not values:
        return []

    return list(dict.fromkeys(values))


def remove_empty(data):
    """
    Supprime les valeurs vides d'un dictionnaire.
    """
    return {
        key: value
        for key, value in data.items()
        if value not in ("", None, [], {})
    }