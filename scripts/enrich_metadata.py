import os
import time
import json
import psycopg2 #type:ignore
from psycopg2.extras import RealDictCursor #type:ignore
from google import genai
from google.genai import errors #type:ignore

# --- CONFIGURATION BASE DE DONNÉES ---
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "restaurants_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "1234")

# --- CONFIGURATION GEMINI ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ La variable d'environnement GEMINI_API_KEY n'est pas définie dans PowerShell.")

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-3.1-flash-lite"


def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )


def call_gemini_with_retry(prompt: str, max_retries: int = 5, initial_delay: int = 4):
    delay = initial_delay
    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config={
                    "response_mime_type": "application/json"
                }
            )
            return response.text
        except errors.APIError as e:
            if e.code == 429:
                print(f"⚠️ Quota atteint (429). Pause de {delay}s (tentative {attempt}/{max_retries})...")
                time.sleep(delay)
                delay *= 2
            else:
                print(f"❌ Erreur API Google : {e}")
                break
        except Exception as e:
            print(f"❌ Erreur inattendue : {e}")
            break
    return None


def enrich_restaurants():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # REQUÊTE CIBLÉE SUR LE MAROC
    # On cherche les restaurants où la cuisine est NULL/vide ET situés au Maroc
    query = """
        SELECT id, name, city, country, address, price_range, rating, website
        FROM restaurants
        WHERE (cuisine IS NULL OR cuisine = '')
          AND (
               LOWER(country) LIKE '%maroc%' 
            OR LOWER(country) LIKE '%morocco%'
            OR LOWER(city) IN ('casablanca', 'rabat', 'marrakech', 'tanger', 'agadir', 'fès', 'fes', 'meknès', 'meknes', 'oujda')
          )
        LIMIT 500;
    """
    
    try:
        cursor.execute(query)
        restaurants = cursor.fetchall()
    except Exception as e:
        print(f"❌ Erreur SQL : {e}")
        conn.close()
        return

    if not restaurants:
        print("✅ Aucun restaurant marocain non enrichi trouvé !")
        conn.close()
        return

    print(f"📌 {len(restaurants)} restaurant(s) situé(s) au Maroc trouvé(s) à enrichir.\n")

    for index, resto in enumerate(restaurants, start=1):
        resto_id = resto['id']
        name = resto.get('name', 'Inconnu')
        city = resto.get('city', '')
        country = resto.get('country', '')
        address = resto.get('address', '')
        price_range = resto.get('price_range', '')
        rating = resto.get('rating', '')
        website = resto.get('website', '')

        print(f"[{index}/{len(restaurants)}] Traitement de #{resto_id} : {name} ({city})")

        prompt = f"""
        Tu es un expert de la restauration et de la gastronomie au Maroc.
        Analyse les informations suivantes d'un restaurant marocain et génère les 5 attributs manquants :

        - Nom : {name}
        - Ville : {city}
        - Pays : {country}
        - Adresse : {address}
        - Fourchette de prix : {price_range}
        - Note : {rating}
        - Site Web : {website}

        Fournis une réponse JSON stricte contenant exactement ces 5 clés :
        1. "cuisine" (string) : Le type principal de cuisine (ex: "Marocaine", "Italienne", "Japonaise", "Fast Food", "Française", "Poissons & Fruits de mer", etc.).
        2. "has_delivery" (boolean) : true si le restaurant propose la livraison, false sinon.
        3. "is_family_friendly" (boolean) : true si le cadre convient aux familles/enfants, false sinon.
        4. "opening_hours" (string) : Horaires d'ouverture estimés (ex: "12:00 - 23:00").
        5. "avg_price" (number/float) : Prix moyen estimé par personne en Dirhams marocains (MAD/DH) (ex: 80.0, 150.0).

        Format JSON attendu :
        {{
            "cuisine": "Marocaine",
            "has_delivery": true,
            "is_family_friendly": true,
            "opening_hours": "12:00 - 23:00",
            "avg_price": 120.0
        }}
        """

        result_json = call_gemini_with_retry(prompt)

        if result_json:
            try:
                data = json.loads(result_json)

                cuisine = data.get("cuisine", "Autre")
                has_delivery = bool(data.get("has_delivery", False))
                is_family_friendly = bool(data.get("is_family_friendly", True))
                opening_hours = str(data.get("opening_hours", "12:00 - 23:00"))
                avg_price = float(data.get("avg_price", 0.0))

                update_query = """
                    UPDATE restaurants
                    SET cuisine = %s,
                        has_delivery = %s,
                        is_family_friendly = %s,
                        opening_hours = %s,
                        avg_price = %s
                    WHERE id = %s;
                """
                cursor.execute(
                    update_query, 
                    (cuisine, has_delivery, is_family_friendly, opening_hours, avg_price, resto_id)
                )
                conn.commit()
                print(f"   ✅ Mis à jour -> Cuisine='{cuisine}', Delivery={has_delivery}, Family={is_family_friendly}, Price={avg_price} DH")

            except json.JSONDecodeError:
                print(f"   ❌ Erreur de parsing JSON pour #{resto_id}.")
            except Exception as e:
                conn.rollback()
                print(f"   ❌ Erreur UPDATE pour #{resto_id} : {e}")
        else:
            print(f"   ⏩ Échec de la réponse pour #{resto_id}.")

        time.sleep(1.5)

    cursor.close()
    conn.close()
    print("\n🎉 Enrichissement des restaurants au Maroc terminé !")


if __name__ == "__main__":
    enrich_restaurants()