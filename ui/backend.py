"""Fonctions utilitaires réseau/état utilisées par l'interface Streamlit.

Séparées du reste du framework (dossier `common/`) pour ne pas mélanger la logique
métier du RAG avec les besoins spécifiques de l'interface graphique (health-check...).

Note d'architecture : les embeddings (Retriever/Indexeur) passent toujours par Ollama
en local, tandis que la génération (Generation/Post_generation) passe par Azure OpenAI,
configuré via les variables d'environnement du fichier `.env`. La page "Chat libre" de
l'UI fait du live prompting sur la cible RAG construite (donc via `common.generation.Generation`
directement) plutôt que d'appeler Azure OpenAI de façon indépendante — il n'y a donc pas
de fonction de chat direct ici.
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = "http://localhost:11434"
CHROMA_URL = "http://localhost:8000"

AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_API_ENDPOINT")
AZURE_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")


def check_ollama(timeout: float = 1.5) -> bool:
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=timeout)
        return response.status_code == 200
    except requests.RequestException:
        return False


def check_chroma(timeout: float = 1.5) -> bool:
    try:
        response = requests.get(f"{CHROMA_URL}/api/v2/heartbeat", timeout=timeout)
        return response.status_code == 200
    except requests.RequestException:
        return False


def azure_config_status() -> dict:
    """Indique quelles variables d'environnement Azure sont renseignées, sans exposer leur valeur."""
    return {
        "AZURE_OPENAI_API_ENDPOINT": bool(AZURE_ENDPOINT),
        "AZURE_OPENAI_API_KEY": bool(AZURE_KEY),
        "AZURE_OPENAI_API_VERSION": bool(AZURE_VERSION),
        "AZURE_OPENAI_DEPLOYMENT_NAME": bool(AZURE_DEPLOYMENT),
    }


def check_azure_configured() -> bool:
    return all(azure_config_status().values())
