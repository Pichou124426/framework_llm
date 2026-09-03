"""Fonctions utilitaires réseau/état utilisées par l'interface Streamlit.

Séparées du reste du framework (dossier `common/`) pour ne pas mélanger la logique
métier du RAG avec les besoins spécifiques de l'interface graphique (health-check,
chat direct hors pipeline RAG...).

Note d'architecture : les embeddings (Retriever/Indexeur) passent toujours par Ollama
en local, tandis que la génération (Generation/Post_generation) passe désormais par
Azure OpenAI, configuré via les variables d'environnement du fichier `.env`.
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


def azure_chat_direct(messages: list, timeout: float = 120.0) -> str:
    """Appelle directement Azure OpenAI, sans passer par le pipeline RAG (page Chat libre).

    `messages` est une liste de dicts {"role": ..., "content": ...}.
    """
    if not check_azure_configured():
        manquantes = [k for k, present in azure_config_status().items() if not present]
        raise RuntimeError(
            "Configuration Azure OpenAI incomplète dans le fichier .env. Variable(s) manquante(s) : "
            + ", ".join(manquantes)
        )

    endpoint = (
        f"{AZURE_ENDPOINT.rstrip('/')}/openai/deployments/"
        f"{AZURE_DEPLOYMENT}/chat/completions"
        f"?api-version={AZURE_VERSION}"
    )
    headers = {"Content-Type": "application/json", "api-key": AZURE_KEY}
    payload_messages = [{"role": m["role"], "content": m["content"]} for m in messages]

    response = requests.post(endpoint, headers=headers, json={"messages": payload_messages}, timeout=timeout)
    data = response.json()

    if "error" in data:
        raise RuntimeError(f"Erreur Azure OpenAI : {data['error']}")
    if response.status_code != 200:
        raise RuntimeError(f"Azure OpenAI a répondu avec le code {response.status_code} : {response.text}")

    return data["choices"][0]["message"]["content"]
