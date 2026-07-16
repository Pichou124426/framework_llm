from common.initialisation import Initialisation
from common.indexation import Indexeur
from common.retriever import Retriever
from common.generation import Generation

rag_db = Initialisation("CGI_collection")
rag_db.creation()
rag_db.afficher_informations()



""" rag_index = Indexeur("https://rmcsport.bfmtv.com/rss/football/coupe-du-monde/", rag_db.recover_id())
rag_index.insert_data()
rag_index.listening_data_db()   """


chat =  Generation("llama3",rag_db.recover_id())
chat.chat()