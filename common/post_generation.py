import requests
from difflib import SequenceMatcher

class Post_generation :
     def __init__(self, modele_ia):
        self.modele_ia = modele_ia
        self.counter = 1

     def fuite_verbatim(self, chunk_list, llm_response):
        print(f"Debut de l'analyse de fuite verbalism numéro {self.counter} !")
        endpoint_chat = 'http://localhost:11434/api/chat'
        tmp_response_llm = llm_response

        while self.counter <= 3:
            fuite_detectee = False

            for index, chunk in enumerate(chunk_list):
                ratio = SequenceMatcher(None, tmp_response_llm, chunk).ratio()
                print(f"Chunk {index} : Ratio = {ratio}")

                if ratio > 0.7:
                    print("Début de la reformulation de la réponse initiale !")
                    print(" Cause : Detection de fuite de données sources")
                    payload_reformulation = requests.post(endpoint_chat, json={
                        "model": self.modele_ia,
                        "messages": [
                            {"role": "system", "content": f"Tu es un expert en reformulation de texte. Nous avons une réponse contenant des données sensibles : {tmp_response_llm}. Je souhaite que tu reformules cette réponse en te basant uniquement sur celle-ci."}
                        ],
                        "stream": False
                    })
                    data = payload_reformulation.json()
                    tmp_response_llm = data["message"]["content"]
                    self.counter += 1
                    fuite_detectee = True
                    break  

            if not fuite_detectee:
                print("Réponse fiable. Fin de l'étape de détection de fuite verbatim.")
                return tmp_response_llm

        print("Nombre maximum de tentatives de reformulation atteint !")
        tmp_response_llm = "Je ne peux pas vous fournir une réponse fiable à cette demande pour le moment."
        return tmp_response_llm

    
        