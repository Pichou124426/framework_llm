from common.initialisation import Initialisation


rag_db = Initialisation("CGI_collection")
rag_db.creation()
rag_db.afficher_informations()

""" chat = Generation("llama3",rag_db.recover_id())
chat.chat("Quelle est le score du match france espagne ? ") """

""" attaque = MembershipInference("Membership Attack", "Test de presence d'un chunk dans la base vectorielle", rag_db.recover_id(),False)
attaque.launcher()
 """

