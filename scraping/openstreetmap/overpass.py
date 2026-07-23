"""
Client Overpass API.

Responsabilités :
- Exécuter des requêtes Overpass QL
- Gérer les erreurs et les retry
- Logger les requêtes et les réponses
"""

import requests

from scraping.common.request_manager import RequestManager
from scraping.common.rate_limiter import rate_limiter
from scraping.common.retry import retry
from scraping.common.logger import get_logger
from scraping.common.config import OVERPASS_ENDPOINT

logger = get_logger(__name__)


class OverpassClient:
    """
    Client pour l'API Overpass.
    """

    def __init__(self):
        self.request = RequestManager()

    @retry()
    def execute(self, query: str):
        """
        Exécute une requête Overpass QL.
        
        Parameters
        ----------
        query : str
            Requête Overpass QL valide
            
        Returns
        -------
        dict
            Réponse JSON de Overpass
        """

        # Validation
        if not isinstance(query, str):
            raise TypeError(
                f"query doit être str, pas {type(query).__name__}"
            )
        
        if not query or len(query.strip()) == 0:
            raise ValueError("query ne peut pas être vide")

        rate_limiter.pause()

        # Debug logging avant l'envoi
        logger.info("="*70)
        logger.info("Envoi d'une requête Overpass API")
        logger.debug(f"Type de query : {type(query).__name__}")
        logger.debug(f"Taille de query : {len(query)} caractères")
        logger.debug(f"Premiers 500 caractères de query :")
        logger.debug(query[:500])
        logger.debug(f"URL cible : {OVERPASS_ENDPOINT}")
        logger.info("="*70)

        # Envoi avec headers minimaux pour Overpass
        # Important: Overpass rejette les Accept headers spécifiques
        # On doit utiliser une requête directe sans les headers de session
        try:
            # Headers minimaux
            headers_for_request = {}
            logger.debug(f"Headers envoyés (empty) : {headers_for_request}")
            logger.info(f"Données à envoyer : type={type(query).__name__}, len={len(query)}, id={id(query)}")
            logger.info(f"Premiers 100 chars des données : {repr(query[:100])}")
            logger.info(f"Derniers 100 chars des données : {repr(query[-100:])}")
            
            # Requête POST directe avec headers vides
            # pour que requests utilise ses defaults
            response = requests.post(
                url=OVERPASS_ENDPOINT,
                data=query,
                timeout=30,
                verify=True
            )
            
            logger.info(f"Réponse HTTP reçue : code={response.status_code}")
            logger.info(f"Headers de réponse : {dict(response.headers)}")
            
            response.raise_for_status()

            data = response.json()
            
            elements_count = len(data.get('elements', []))
            logger.info(
                f"Succès! {elements_count} éléments récupérés."
            )

            return data
            
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution Overpass :")
            logger.error(f"  Type d'erreur : {type(e).__name__}")
            logger.error(f"  Message : {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"  Code HTTP : {e.response.status_code}")
                logger.error(f"  Headers de réponse : {dict(e.response.headers)}")
                try:
                    logger.error(f"  Corps de réponse : {e.response.text[:500]}")
                except:
                    pass
            raise

    def get_elements(self, query: str):
        """
        Exécute une requête et retourne uniquement les éléments OSM.
        
        Parameters
        ----------
        query : str
            Requête Overpass QL valide
            
        Returns
        -------
        list
            Liste des éléments OSM
        """

        data = self.execute(query)
        return data.get("elements", [])

    def close(self):
        """
        Ferme la session HTTP.
        """
        self.request.close()