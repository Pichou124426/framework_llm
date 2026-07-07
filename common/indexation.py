
import requests
import os 

class Indexeur :
    def __init__(self, data_folder, collection_id):
        self.data_folder = data_folder
        self.collection_id = collection_id
        
    
    def listing_file (self) :
        try :            
            list_file = os.listdir(self.data_folder)
            print (f"Le contenue de {self.data_folder} :")
            for file in (list_file) :
                print(file)
        except FileNotFoundError : 
            print (f"Le chemin renseigné n'a pas été trouvé : {self.data_folder}")

    def insert_data (self) :
        endpoint_embedding = "http://localhost:11434/api/embeddings"
        endpoint_storage =  f"http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database/collections/{self.collection_id}/add"
        list_file = os.listdir(self.data_folder)
        print("--- Lancement de l'injection des données dans la collection ---")
        for index, file in enumerate (list_file) :
            with open (os.path.join(self.data_folder, file),"r",encoding="utf-8") as f :
                content = f.read()
            response = requests.post(endpoint_embedding,
                json={
                    "model" : "nomic-embed-text",
                    "prompt": content
                })
            if response.status_code != 200:
                print (f"Erreur embedding sur {file}.  \n Code erreur : {response.status_code} ")
                continue
            embedding = response.json()["embedding"]
            response_storage = requests.post(endpoint_storage,
                json= {
                    "documents" :[
                        content
                    ],
                    "embeddings" : [
                        embedding
                    ],
                    "ids" : [
                        file   
                    ]
                } )
            if response_storage.status_code not in [200,201] :
                print(f"Erreur stockage sur {file} \n Code d'erreur : {response_storage.status_code}")
                continue
            print (f"Reussit ! {file} indexe correctement. \n ({index + 1}/{len(list_file)}) ")
        
    def listening_data_db (self):
        endpoint_storage =  f"http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database/collections/{self.collection_id}/get"
        response = requests.post(endpoint_storage, 
            json={"ids": [],"include": ["documents", "embeddings"]})
        print (response.json())
    
        
        
        
        
        
test = Indexeur("","")
test.listening_data_db()


