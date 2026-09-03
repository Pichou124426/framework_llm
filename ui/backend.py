"""Fonctions utilitaires réseau/état utilisées par l'interface Streamlit.

Séparées du reste du framework (dossier `common/`) pour ne pas mélanger la logique
métier du RAG avec les besoins spécifiques de l'interface graphique (health-check,
chat direct hors pipeline RAG, listing des modèles disponibles...).
"""

import requests

OLLAMA_URL = "http://localhost:11434"
CHROMA_URL = "http://localhost:8000"

FALLBACK_MODELS = ["llama3", "mistral", "nomic-embed-text"]


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


def list_ollama_models(timeout: float = 2.0) -> list:
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=timeout)
        if response.status_code != 200:
            return list(FALLBACK_MODELS)
        data = response.json()
        names = [model["name"] for model in data.get("models", [])]
        return names if names else list(FALLBACK_MODELS)
    except (requests.RequestException, KeyError, ValueError):
        return list(FALLBACK_MODELS)


def ollama_chat_direct(model: str, messages: list, timeout: float = 120.0) -> str:
    """Appelle directement l'API chat d'Ollama, sans passer par le pipeline RAG.

    `messages` est une liste de dicts {"role": ..., "content": ...} au format Ollama.
    """
    payload_messages = [{"role": m["role"], "content": m["content"]} for m in messages]
    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={"model": model, "messages": payload_messages, "stream": False},
        timeout=timeout,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Ollama a répondu avec le code {response.status_code} : {response.text}")
    data = response.json()
    return data["message"]["content"]
