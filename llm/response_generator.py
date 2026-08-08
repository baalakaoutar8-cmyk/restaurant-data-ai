import os
import time
import json
from google import genai
from google.genai import types
from google.genai.errors import APIError
from dotenv import load_dotenv
from llm.prompt import SYSTEM_PROMPT_RESPONSE

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_natural_response(user_question: str, db_data: list) -> str:
    model_name = "gemini-3.1-flash-lite"
    
    # Formater proprement db_data sous forme de JSON string ou texte lisible
    if isinstance(db_data, list) and len(db_data) > 0:
        # Si db_data est une liste de dicts ou tuples, on le formate proprement
        data_str = json.dumps(db_data, indent=2, ensure_ascii=False, default=str)
    else:
        data_str = "Aucun résultat trouvé dans la base de données."
    
    prompt = f"""
    Question de l'utilisateur : {user_question}
    
    Données extraites de la base PostgreSQL :
    {data_str}
    """
    
    for attempt in range(1, 4):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT_RESPONSE,
                    temperature=0.3
                )
            )
            return response.text
        except APIError as e:
            if e.code == 429:
                print(f"⚠️ Quota temporairement atteint ({model_name}). Attente de 15s (essai {attempt}/3)...")
                time.sleep(15)
            else:
                return f"❌ Erreur API Gemini : {e}"
        except Exception as e:
            return f"❌ Erreur lors de la génération de la réponse : {e}"
            
    return "Désolé, impossible d'obtenir une réponse du modèle en raison des limites de quota de l'API."