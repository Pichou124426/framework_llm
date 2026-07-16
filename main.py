from common.initialisation import Initialisation
from common.indexation import Indexeur
from common.retriever import Retriever

rag_db = Initialisation("CGI_collection")
rag_db.creation()
rag_db.afficher_informations()



rag_index = Indexeur("https://rmcsport.bfmtv.com/rss/football/coupe-du-monde/", rag_db.recover_id())
rag_index.insert_data()
rag_index.listening_data_db()  


""" retriver_cgi = Retriever(rag_db.recover_id(),"nomic-embed-text")
retriver_cgi.report(retriver_cgi.retriever("Quelle est le score du match France-Espagne ?",5, use_reranker= True))  """