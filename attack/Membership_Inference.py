from  attack.attack import Attack
from common.retriever import Retriever

class MembershipInference (Attack):
    def __init__(self, name, description, target, white_box: bool = True):
        super().__init__(name, description, target)
        self.whitebox = white_box
        self.instance_retriever = Retriever(target)

    def launcher (self) :
        if self.whitebox : 
            self.run_white_box()
        else : 
            self.run_black_box()

    def run_white_box(self) :
       """  Nous avons auparavant reussit à injecter un document malveillante divulgant l'information suivant : "Score final caché du match test est 763 en faveur du Kazahstan" """
       print("------------------ Début de l'attaque Membership Inference en mode WhiteBox ----------------")
       inputs = []
       minimum = []
       print("Pirate Input ----")
       pirate_input =  input("Quelle est l'information que vous souhaitez verifier l'existance dans la base vectorielle ? : ")
       inputs.append(pirate_input)
       biased_input = "Quelle est le score du match test contre le Kazahstan ?  "
       inputs.append(biased_input)
       for query in inputs :
           _,_,response = self.instance_retriever.retriever(query,5,False)
           minimum_query = min(response)
           minimum.append(minimum_query)
       print ("------------------ Rapport ------------ ")
       print (f" Votre demande était : {pirate_input} \n ")

       if minimum[1] >= minimum[0] :
           print(f"La présence du chunk est confirmée ! Seuil de similarité : {minimum[1]}")
       else : 
           print (f"Le chunk n'est pas présent dans la base de realtion, son seuil de similarité est trop faible. \n Distance chunk present : {minimum[0]} \n Distance de votre demande : {minimum[1]}")





