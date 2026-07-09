
import requests
import os 
import feedparser

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
            list_article.append({"title": article_title, "content": article_content})
        return list_article

        
    def insert_data (self) :
        endpoint_embedding = "http://localhost:11434/api/embeddings"
        endpoint_storage =  f"http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database/collections/{self.collection_id}/add"
        data = self.feed_rss()
        print("--- Lancement de l'injection des données dans la collection ---")
        for index, post in enumerate (data) :
            response = requests.post(endpoint_embedding,
                json={
                    "model" : "nomic-embed-text",
                    "prompt": post["content"]
                })
            if response.status_code != 200:
                print (f"Erreur embedding   \n Code erreur : {response.status_code} ")
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
                           
                    ]
                } )
            if response_storage.status_code not in [200,201] :
                print(f"Erreur stockage \n Code d'erreur : {response_storage.status_code}")
                continue
            print (f"Reussit ! indexe correctement. \n ({index + 1}/{len(data)}) ")
        
    def listening_data_db (self):
        endpoint_storage =  f"http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database/collections/{self.collection_id}/get"
        response = requests.post(endpoint_storage, 
            json={"ids": [],"include": ["documents", "embeddings"]})
        print (response.json())
    
    
    
        
        
        
        
        


