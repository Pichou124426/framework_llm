from common.initialisation import Initialisation
from common.indexation import Indexeur

rag_db = Initialisation("CGI_db")
rag_db.creation()
rag_db.afficher_informations()

rag_index = Indexeur("https://rmcsport.bfmtv.com/rss/football/coupe-du-monde/", rag_db.recover_id())
rag_index.insert_data()
rag_index.listening_data_db()