import requests
from common.retriever import Retriever

class Generation :
    def __init__(self, ai_model, collection_id):
        self.ai_model = ai_model
        self.collection_id = collection_id
        self.retriever_instance = Retriever(self.collection_id)
    
    def chat (self) :
        endpoint_chat = 'http://localhost:11434/api/chat'
        user_input = input("Posez votre question : ")
        chunks_list, metadatas_list = self.retriever_instance.retriever(user_input,5)
        payload_llm = requests.post(endpoint_chat, json={
            "model": self.ai_model,
            "messages": [
                {"role": "system", "content":f"Tu es un expert en football, tu dois te baser uniquement sur les données qu'on te transmet là : {chunks_list}"},
                {"role": "user", "content": user_input}
            ], 
            "stream": False
        })
        data = payload_llm.json()
        return print(data["message"]["content"])


        