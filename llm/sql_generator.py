import os
import time
from google import genai
from google.genai import types
from google.genai.errors import APIError
from dotenv import load_dotenv
from llm.prompt import SYSTEM_PROMPT_SQL

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_sql(user_question: str) -> str:
    # Testez gemini-2.5-flash ou gemini-3.1-flash-lite
    model_name = "gemini-3.1-flash-lite"
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=f"Question : {user_question}",
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT_SQL,
                    temperature=0.0
                )
            )
            return response.text.strip().replace("```sql", "").replace("```", "").strip()
        except APIError as e:
            if e.code == 429:
                print(f" Quota temporairement atteint ({model_name}). Attente de 15s (essai {attempt+1}/3)...")
                time.sleep(15)
            else:
                print(f"Erreur API Gemini : {e}")
                break
        except Exception as e:
            print(f"Erreur inattendue : {e}")
            break
            
    return ""