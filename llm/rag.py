import pandas as pd
from sqlalchemy import text
from llm.sql_generator import generate_sql
from llm.response_generator import generate_natural_response

def run_rag_pipeline(user_question: str, db_engine) -> str:
    # 1. Génération de la requête SQL par Gemini
    sql_query = generate_sql(user_question)
    print(f"\n Requête SQL Générée : {sql_query}\n")

    if not sql_query:
        return "Désolé, je n'ai pas pu interpréter votre demande."

    # 2. Exécution SQL sécurisée avec connexion explicite et text()
    records = []
    try:
        with db_engine.connect() as connection:
            # Envelopper la requête dans text() pour éviter l'erreur de mapping/séquence
            df = pd.read_sql_query(text(sql_query), connection)
            records = df.to_dict(orient="records")
    except Exception as e:
        print(f"Erreur d'exécution SQL : {e}")
        records = []

    # 3. Synthèse des résultats par le LLM
    return generate_natural_response(user_question, records)