import os
import requests
from dotenv import load_dotenv
from difflib import SequenceMatcher

load_dotenv()

AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_API_ENDPOINT")
AZURE_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")


class Post_generation:
    def __init__(self, modele_ia):
        self.modele_ia = modele_ia
        self.counter = 1

    def fuite_verbatim(self, chunk_list, llm_response):
        print(f"Debut de l'analyse de fuite verbatim numero {self.counter} !")
        endpoint_chat = (
            f"{AZURE_ENDPOINT.rstrip('/')}/openai/deployments/"
            f"{AZURE_DEPLOYMENT}/chat/completions"
            f"?api-version={AZURE_VERSION}"
        )
        headers = {
            "Content-Type": "application/json",
            "api-key": AZURE_KEY,
        }
        tmp_response_llm = llm_response

        while self.counter <= 3:
            fuite_detectee = False

            for index, chunk in enumerate(chunk_list):
                ratio = SequenceMatcher(None, tmp_response_llm, chunk).ratio()
                print(f"Chunk {index} : Ratio = {ratio}")

                if ratio > 0.7:
                    print("Debut de la reformulation de la reponse initiale !")
                    print(" Cause : Detection de fuite de donnees sources")
                    payload_reformulation = requests.post(endpoint_chat, headers=headers, json={
                        "messages": [
                            {"role": "system", "content": f"Tu es un expert en reformulation de texte. Nous avons une reponse contenant des donnees sensibles : {tmp_response_llm}. Je souhaite que tu reformules cette reponse en te basant uniquement sur celle-ci."}
                        ],
                    })
                    data = payload_reformulation.json()

                    if "error" in data:
                        raise RuntimeError(f"Erreur Azure OpenAI : {data['error']}")

                    tmp_response_llm = data["choices"][0]["message"]["content"]
                    self.counter += 1
                    fuite_detectee = True
                    break

            if not fuite_detectee:
                print("Reponse fiable. Fin de l'etape de detection de fuite verbatim.")
                return tmp_response_llm

        print("Nombre maximum de tentatives de reformulation atteint !")
        tmp_response_llm = "Je ne peux pas vous fournir une reponse fiable a cette demande pour le moment."
        return tmp_response_llm