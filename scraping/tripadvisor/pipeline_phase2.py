# scraping/tripadvisor/pipeline_phase2.py

import logging
from typing import List, Dict, Any
from storage import Storage  # Assurez-vous d'importer votre module storage
from checkpoint import CheckpointManager

logger = logging.getLogger("scraping.tripadvisor.phase2")

def get_pending_restaurants(storage: Storage) -> List[Dict[str, Any]]:
    """
    Récupère tous les restaurants enregistrés en Phase 1
    qui n'ont pas encore été enrichis par la Phase 2.
    """
    all_restaurants = storage.get_all_restaurants()
    
    # On filtre ceux qui n'ont pas encore les détails (ex: pas de téléphone ou pas d'adresse complète)
    pending = [
        r for r in all_restaurants 
        if not r.get("phone") and r.get("tripadvisor_url")
    ]
    
    logger.info(f"Total restaurants trouvés : {len(all_restaurants)}")
    logger.info(f"Restaurants restant à enrichir en Phase 2 : {len(pending)}")
    return pending