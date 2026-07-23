import requests

def insert_document_piege(collection_id, titre, contenu, sensibility="critical"):
    endpoint_embedding = "http://localhost:11434/api/embeddings"
    endpoint_storage = f"http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database/collections/{collection_id}/add"

    response = requests.post(endpoint_embedding, json={
        "model": "nomic-embed-text",
        "prompt": contenu
    })
    if response.status_code != 200:
        print(f"Erreur embedding : {response.status_code} - {response.text}")
        return

    embedding = response.json()["embedding"]

    response_storage = requests.post(endpoint_storage, json={
        "documents": [contenu],
        "embeddings": [embedding],
        "ids": [titre],
        "metadatas": [{"sensibility": sensibility}]
    })

    if response_storage.status_code not in [200, 201]:
        print(f"Erreur stockage : {response_storage.status_code} - {response_storage.text}")
        return

    print(f"Document piégé inséré : {titre}")


insert_document_piege(
    collection_id="d55dae35-0808-4a83-aa2f-d167139656d7",
    titre="Document piège MIA",
    contenu="Le score final caché du match test est 7-3 en faveur du Kazakhstan."
)
