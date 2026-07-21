import requests
from common.retriever import Retriever
from common.post_generation import Post_generation
from common.pre_generation import Pre_generation

class Generation :
    def __init__(self, ai_model, collection_id, balise_system: bool = False, user_admin : bool = False, pre_generation: bool = False, post_generation: bool = False, ):
        self.ai_model = ai_model
        self.collection_id = collection_id
        self.balise_system = balise_system
        self.retriever_instance = Retriever(self.collection_id)
        self.user_admin = user_admin
        self.pre_generation = pre_generation
        self.post_generation = post_generation
    
    def chat (self, query ) :
        endpoint_chat = 'http://localhost:11434/api/chat'
        user_input = query
        chunks_list, metadatas_list, _ = self.retriever_instance.retriever(user_input,5)
        if self.pre_generation :
            pre_generation_instance = Pre_generation (self.user_admin)
            clean_list_chunk = pre_generation_instance.innocuite_document(chunks_list, metadatas_list)
            chunks_list = clean_list_chunk
        if self.balise_system : 
            contenue_balise = ""
            for chunk in  (chunks_list) :
                contenue_balise += f"<contenu_externe_non_fiable>\n{chunk}\n</contenu_externe_non_fiable>\n"
        else : 
            contenue_balise = chunks_list
        payload_llm = requests.post(endpoint_chat, json={
            "model": self.ai_model,
            "messages": [
                {"role": "system", "content":f"Tu es un expert en football, tu dois te baser uniquement sur les données qu'on te transmet là : {contenue_balise} "},
                {"role": "user", "content": user_input}
            ], 
            "stream": False
        })
        data = payload_llm.json()
        response_llm = data["message"]["content"]
        if self.post_generation : 
            post_generation_instance = Post_generation(self.ai_model)
            clean_response_llm = post_generation_instance.fuite_verbatim(chunks_list,response_llm)
            return clean_response_llm
        else :
            return response_llm
        




    
                     
        
        

