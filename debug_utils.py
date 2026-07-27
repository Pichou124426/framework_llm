def inspect_object(obj, depth=2, indent=0, seen=None):
    """
    Affiche récursivement tous les attributs (self.xxx) d'un objet Python,
    y compris les objets imbriqués (comme self.retriever_instance à l'intérieur
    d'un objet Generation), jusqu'à une profondeur donnée.

    Usage :
        from debug_utils import inspect_object
        inspect_object(mon_objet_generation)
    """
    if seen is None:
        seen = set()

    prefix = "  " * indent

    # Évite de boucler à l'infini si deux objets se référencent l'un l'autre
    obj_id = id(obj)
    if obj_id in seen:
        print(f"{prefix}(déjà affiché, référence circulaire évitée)")
        return
    seen.add(obj_id)

    print(f"{prefix}{type(obj).__name__} :")

    # __dict__ contient tous les attributs self.xxx d'un objet
    if not hasattr(obj, "__dict__"):
        print(f"{prefix}  (pas d'attributs, type simple : {obj!r})")
        return

    for nom_attribut, valeur in vars(obj).items():
        # Cas 1 : c'est un objet "maison" (Retriever, Generation, etc.)
        # -> on redescend dedans si on n'a pas atteint la profondeur max
        if hasattr(valeur, "__dict__") and depth > 0:
            print(f"{prefix}  self.{nom_attribut} =")
            inspect_object(valeur, depth=depth - 1, indent=indent + 2, seen=seen)

        # Cas 2 : liste ou dict, on affiche la taille pour ne pas noyer l'écran
        elif isinstance(valeur, (list, tuple)):
            print(f"{prefix}  self.{nom_attribut} = [liste de {len(valeur)} élément(s)]")

        elif isinstance(valeur, dict):
            print(f"{prefix}  self.{nom_attribut} = {{dictionnaire, {len(valeur)} clé(s) : {list(valeur.keys())}}}")

        # Cas 3 : valeur simple (str, bool, int, None...) -> affichage direct
        else:
            print(f"{prefix}  self.{nom_attribut} = {valeur!r}")


def inspect_rag(rag_dict, depth=2):
    """
    Version spécifique pour un self.rag construit par build_rag() / Attack.
    Affiche chaque module ("retriever", "generation", ...) et son contenu.

    Usage :
        inspect_rag(mon_attaque.rag)
    """
    print("===== Contenu de self.rag =====")
    for nom_module, instance in rag_dict.items():
        print(f"\n--- Module '{nom_module}' ---")
        inspect_object(instance, depth=depth)