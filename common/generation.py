import requests
from dataclasses import asdict
from common.retriever import Retriever
from common.rag_config import RetrieverConfig
from common.post_generation import Post_generation
from common.pre_generation import Pre_generation

class Generation:
    def __init__(self, ai_model, collection_id, retriever_config : RetrieverConfig , balise_system: bool = False, pre_generation: bool = False, post_generation: bool = False):
        self.ai_model = ai_model
        self.collection_id = collection_id
        self.balise_system = balise_system
        self.retriever_instance = Retriever (**retriever_config)
        self.pre_generation = pre_generation
        self.post_generation = post_generation
        self.historique = []

    def chat(self, query):
        endpoint_chat = 'http://localhost:11434/api/chat'
        user_input = query
        chunks_list, metadatas_list, _ = self.retriever_instance.retriever(user_input, 5)

        if self.pre_generation:
            pre_generation_instance = Pre_generation(self.retriever_instance.user_is_admin)
            chunks_list = pre_generation_instance.check_permissions(chunks_list, metadatas_list)

        if self.balise_system:
            contenue_balise = ""
            for chunk in chunks_list:
                contenue_balise += f"<contenu_externe_non_fiable>\n{chunk}\n</contenu_externe_non_fiable>\n"
        else:
            contenue_balise = chunks_list

        system_message = {
            "role": "system",
            "content": f"Tu es un expert en football, tu dois te baser uniquement sur les données qu'on te transmet là : {contenue_balise}"
        }

        messages = [system_message] + self.historique + [{"role": "user", "content": user_input}]

        payload_llm = requests.post(endpoint_chat, json={
            "model": self.ai_model,
            "messages": messages,
            "stream": False
        })
        data = payload_llm.json()
        response_llm = data["message"]["content"]

        self.historique.append({"role": "user", "content": user_input})
        self.historique.append({"role": "assistant", "content": response_llm})

        if self.post_generation:
            post_generation_instance = Post_generation(self.ai_model)
            response_llm = post_generation_instance.fuite_verbatim(chunks_list, response_llm)

        return response_llm
        
    def chatbox(self) :
        print("Chatbot prêt ! Tape 'exit' pour quitter.\n")
        while True:
            question = input("Toi : ")
            if question.lower() == "exit":
                print("Fin de la conversation.")
                break

            reponse = self.chat(question)
            print(f"Assistant : {reponse}\n")





    
                     
        
        

