class Pre_generation:
    def __init__(self, user_is_admin : bool = False):
        self.user_is_admin = user_is_admin
        
    def check_permissions (self, chunks_list, metadatas_list,) :
            print(" Début de la verification des permissions de chaque documents")
            new_chunks_list = []
            pairs_chunk_metatdata= list(zip(chunks_list,metadatas_list))
            for chunk, permission in pairs_chunk_metatdata :
                print(f"Chunk avec la permission : {permission}")
                if  self.user_is_admin != True :
                    if permission["sensibility"] == "easy" :
                        new_chunks_list.append(chunk)
                    else : 
                        print ("Le chunk n'est pas accessible ! ")
                else : 
                    new_chunks_list = chunks_list
            print (" Fin de l'analyse ! ")
            print (f"Nombre de chunks retenues : {len(new_chunks_list)} chunks.")
            return new_chunks_list

""" 
Possibilité d'ajouter une focntion innocuité des documents qui verifier garce à un modele un score dxe ocnfiance en connaissances des ignorer 
Posibilité d'ajouter une fonction qui detecter et gere l'input du user ( le prompt )"""