import os
import urllib.parse
from sqlalchemy import create_engine
from dotenv import load_dotenv
from llm.rag import run_rag_pipeline

load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "1234")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "restaurants_db")

password_encoded = urllib.parse.quote_plus(DB_PASSWORD)
DATABASE_URL = f"postgresql://{DB_USER}:{password_encoded}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def start_chatbot():
    engine = create_engine(DATABASE_URL)
    print("ASSISTANT GASTRONOMIQUE IA OPERATIONNEL ")
    print("Tapez 'exit' pour quitter.\n")

    while True:
        question = input("Vous : ")
        if question.lower() in ["exit", "quit"]:
            break
        
        response = run_rag_pipeline(question, engine)
        print(f"\nAssistant :\n{response}\n" + "-"*50)

if __name__ == "__main__":
    start_chatbot()