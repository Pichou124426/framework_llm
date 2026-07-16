from sentence_transformers import CrossEncoder
import requests
class Retriever : 
    def __init__(self, id_collection, embedding_model ="nomic-embed-text"):
        self.id_collection = id_collection
        self.embedding_model = embedding_model
    
    def embed(self, text: str ) -> list[float] :
        endpoint_embedding = "http://localhost:11434/api/embeddings"
        response = requests.post (endpoint_embedding, json = {
            "model" : self.embedding_model,
            "prompt": text
        })
        data = response.json()
        return data["embedding"]
    
    def retriever ( self, query: str, top_k_init: int = 5, use_reranker : bool = False,) :
        embedding_user = self.embed(query)
        endpoint_query =  f"http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database/collections/{self.id_collection}/query"
       
        if use_reranker: 
            top_k = top_k_init*3
        else :
            top_k= top_k_init

        results = requests.post(endpoint_query, json={
            "include" : [
                "documents",
                "metadatas"
            ],
            "n_results" :top_k,
            "query_embeddings": [embedding_user]
        })
        data = results.json()

        chunks_list = data["documents"][0]
        metadatas_list = data["metadatas"][0]
         
        if use_reranker:
            chunks_list, metadatas_list = self.rerank(query,chunks_list, metadatas_list, top_k_init)

        return chunks_list, metadatas_list
    

    def rerank (self,query: str  ,chunks: list, metadatas: list, top_k) :
        model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        pairs = []
        for text in chunks : 
            tmp = [query, text]
            pairs.append(tmp)
        scores = model.predict(pairs)
        pairs_score_chunk = list(zip(chunks,metadatas,scores))
        paires_triees = sorted(pairs_score_chunk, key=lambda x: x[2], reverse=True)
        chunk_triees, metadatas_triees, _ = zip(*paires_triees)
        return chunk_triees[:top_k],metadatas_triees[:top_k]
    
    def report (self, result) :
        print ("Debut du rapport")
        print (result)

    

        
        