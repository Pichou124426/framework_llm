class Pre_generation:
    def __init__(self, user_is_admin : bool = False):
        self.user_is_admin = user_is_admin
        
    def innocuite_document (self, chunks_list, metadatas_list,) :
            print(" Début de la verification de l'innocuité de chaque documents")
            new_chunks_list = []
            pairs_chunk_metatdata= list(zip(chunks_list,metadatas_list))
            for chunk, permission in pairs_chunk_metatdata :
                print(f"Chunk: {chunk} avec la permission : {permission}")
                if  self.user_is_admin != True :
                    if permission["sensibility"] == "easy" :
                        new_chunks_list.append(chunk)
                    else : 
                        print ("Le chunk n'est pas accessible ! ")
                else : 
                    new_chunks_list = chunks_list
            print (" Fin de l'analyse ! ")
            return new_chunks_list