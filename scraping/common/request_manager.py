"""
Gestion centralisée des requêtes HTTP.

Responsabilités :
- Gérer les sessions HTTP
- Appliquer les headers par défaut
- Logger les requêtes et les erreurs
- Gérer les timeouts et les retries
"""

import requests

from scraping.common.config import (
    HEADERS,
    REQUEST_TIMEOUT,
    VERIFY_SSL,
)
from scraping.common.logger import get_logger

logger = get_logger(__name__)


class RequestManager:
    """
    Gestionnaire centralisé des requêtes HTTP.
    """

    def __init__(self):
        """
        Initialise une session HTTP avec les headers par défaut.
        """
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def get(self, url, params=None, headers=None):
        """
        Effectue une requête GET.
        
        Parameters
        ----------
        url : str
            URL cible
        params : dict, optional
            Paramètres de query string
        headers : dict, optional
            Headers additionnels (override les headers par défaut)
            
        Returns
        -------
        requests.Response
            Réponse HTTP
        """
        try:
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
                verify=VERIFY_SSL
            )

            response.raise_for_status()
            return response

        except requests.RequestException as e:
            logger.error(f"GET {url} -> {type(e).__name__}: {e}")
            raise

    def post(self, url, json=None, data=None, headers=None):
        """
        Effectue une requête POST.
        
        Notes
        -----
        Contrairement à requests, cette méthode ne mélange pas les headers
        de la session avec les headers fournis - les headers fournis
        remplacent les headers de la session pour cette requête.
        
        Parameters
        ----------
        url : str
            URL cible
        json : dict, optional
            Corps JSON (ne pas utiliser avec data)
        data : str or dict, optional
            Corps de la requête (form-encoded ou raw text)
        headers : dict, optional
            Headers additionnels (override les headers par défaut)
            
        Returns
        -------
        requests.Response
            Réponse HTTP
        """
        try:
            # Important: quand on fournit des headers custom, 
            # requests les merge avec session.headers
            # Les headers custom ont la priorité
            response = self.session.post(
                url,
                json=json,
                data=data,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
                verify=VERIFY_SSL
            )

            response.raise_for_status()
            return response

        except requests.RequestException as e:
            logger.error(f"POST {url} -> {type(e).__name__}: {e}")
            raise

    def download_file(self, url, destination):
        """
        Télécharge un fichier.
        
        Parameters
        ----------
        url : str
            URL du fichier à télécharger
        destination : str
            Chemin de destination
        """
        try:
            response = self.get(url)

            with open(destination, "wb") as f:
                f.write(response.content)

            logger.info(f"Fichier téléchargé : {destination}")

        except Exception as e:
            logger.error(f"Erreur lors du téléchargement : {e}")
            raise

    def close(self):
        """
        Ferme la session HTTP.
        """
        self.session.close()