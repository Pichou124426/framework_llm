import requests

class Initialisation :
    def __init__(self,nom_collection):
        self.nom_collection = nom_collection
        self.id_collection = None
    
    def creation(self) :
            endpoint = 'http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database/collections'
            payload = {
                "name": self.nom_collection,
                "metadata": {
                    "description": "Règlement handball",
                    "version": "1.0"
                },
                "schema": None,
                "get_or_create": True}
            requete = requests.post(endpoint,json=payload)
            data = requete.json()
            if requete.status_code in [200,201] :
                print (f"Création prête ! Nom: {self.nom_collection}")
                self.id_collection = data["id"]
            elif requete.status_code == 409:
                print("Collection déjà existante !")
            else :
                print (f"Code erreur : {requete.status_code} : {data}")
    
    def recuperer_id (self) :
        return self.id_collection
    

    def afficher_informations(self) :
        if self.nom_collection and self.id_collection :
            print(f"Nom: {self.nom_collection}\n Id: {self.id_collection}")
        else : 
            print("Impossible d'afficher les informations, merci de créer la collection à l'aide de : .creation() !")
    
    def supprimer(self):
        if self.id_collection == None :
            print("Aucune collection initialisé ! ")
            return
        endpoint = f"http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database/collections/{self.nom_collection}"
        requete = requests.delete(endpoint, json= {})
        if requete.status_code in [200,204]: 
            print ("La collection a  bien été supprimée.")
            self.nom_collection = None
            self.id_collection = None
        else : print (f"Code erreur : {requete.status_code} :")
            
        
                    
        
   










