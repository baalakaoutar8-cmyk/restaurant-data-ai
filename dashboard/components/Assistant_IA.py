import streamlit as st
import sys
import os

# Ajouter le dossier racine au PATH pour importer le module llm
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from llm.rag import run_rag_pipeline

st.set_page_config(page_title="Assistant IA Gastronomique", page_icon="💬", layout="wide")

st.title("💬 Assistant Gastronomique IA")
st.write("Interrogez la base de données PostgreSQL en langage naturel grâce à l'architecture RAG / Text-to-SQL.")

if "engine" in st.session_state and st.session_state.engine is not None:
    engine = st.session_state.engine

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_prompt := st.chat_input("Ex: Quel est le meilleur restaurant italien à Casablanca ?"):
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyse et recherche SQL en cours..."):
                response = run_rag_pipeline(user_prompt, engine)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.error("La connexion à la base de données n'est pas initialisée.")