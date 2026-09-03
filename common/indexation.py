
import requests
import feedparser
import re

class Indexeur :
    def __init__(self, flux_rss, collection_id) :
        self.flux_rss = flux_rss
        self.collection_id = collection_id
    
    def feed_rss (self) :
        feed_url = self.flux_rss
        feed = feedparser.parse(feed_url)
        list_article = []
        for post in feed.entries : 
            article_title = post.title
            article_content = post.description
            sensibilty_label = self.classify(article_content)
            list_article.append({"title": article_title, "content": article_content, "sensibility": sensibilty_label})
        return list_article

    def classify (self, text : str) :
            lower_text = text.lower()
            clean_text = re.sub(r'\s+', ' ', lower_text).strip()
            forbidden_word = ["paraguay", "argentine", "argentin", "lionel","messi"]
            sensibility = "easy"
            for word in forbidden_word :
                if word in  clean_text :
                    sensibility = "critical"
                    break
            return sensibility

        
    def insert_data (self) :
        endpoint_embedding = "http://localhost:11434/api/embeddings"
        endpoint_storage =  f"http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database/collections/{self.collection_id}/add"
        data = self.feed_rss()
        print("--- Lancement de l'injection des données dans la collection ---")
        rapport = {"total": len(data), "success": 0, "errors": []}
        for index, post in enumerate (data) :
            response = requests.post(endpoint_embedding,
                json={
                    "model" : "nomic-embed-text",
                    "prompt": post["content"]
                })
            if response.status_code != 200:
                print (f"Erreur embedding n°{index}   \n Code erreur : {response.status_code} ")
                rapport["errors"].append({"index": index, "titre": post["title"], "etape": "embedding", "code": response.status_code})
                continue
            embedding = response.json()["embedding"]
            response_storage = requests.post(endpoint_storage,
                json= {
                    "documents" :[
                        post["content"]

                    ],
                    "embeddings" : [
                        embedding
                    ],
                    "ids" : [
                        post["title"]

                    ],
                    "metadatas": [
                        {"sensibility": post["sensibility"]}
                    ]
                } )
            if response_storage.status_code not in [200,201] :
                print(f"Erreur stockage \n Code d'erreur : {response_storage.status_code}")
                print(f"Détail : {response_storage.text}")
                rapport["errors"].append({"index": index, "titre": post["title"], "etape": "stockage", "code": response_storage.status_code})
                continue
            print (f"Reussit ! indexe correctement. \n ({index + 1}/{len(data)}) ")
            rapport["success"] += 1
        return rapport

    def listening_data_db (self):
        endpoint_storage =  f"http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database/collections/{self.collection_id}/get"
        response = requests.post(endpoint_storage,
            json={"include": ["documents", "metadatas"]})
        print (response.json())
        return response.json()




    
    
        
        
        
        
        



