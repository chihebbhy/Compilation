"""Export Graphviz (Partie 5) - Etudiant 3.

Etat initial signale par une fleche entrante, etat d'acceptation en double
cercle, ε-transitions etiquetees ε, transitions paralleles regroupees en
une seule arete (etiquette "a,b").

Visualisation :  dot -Tpng automate.py -o automate.png

transitions: source , etiquette ( symbole lu) , dest (0 , 'a', 1 ) de l etat 0 par a il va en 1
"""
from automate import EPS
EPSILON = "ε"

def regrouper(transitions):
    """Regroupe les transitions paralleles : (source, cible) -> liste des
    etiquettes, sans doublon, dans l'ordre de premiere apparition."""
    grp_transition = {} # dictionnaire il admet (src , dst), liste des etiquettes
    for src, symbole_lu, dst in transitions:
        texte = EPSILON if symbole_lu is EPS else symbole_lu
        etiquettes = grp_transition.setdefault((src, dst), []) #si existe ne l ajoute pas sinon il l ajoute
        if texte not in etiquettes:
            etiquettes.append(texte)
    return grp_transition #{(0,1): ['a','b'], (1,2): ['ε']}


def vers_dot(frag, nom="AFN"): # prendre automate et le transforme en texet pour dessiner en graphviz
    lignes = [
        f"digraph {nom} {{", # f pour que le nom est remplace par son valeur 
        "  rankdir=LR;",
        "  node [shape=circle];",
        "  __start [shape=point];",        # point invisible 
        f"  __start -> {frag.init};",      # fleche entrante de l'etat initial
        f"  {frag.fin} [shape=doublecircle];",
    ]
    grp_transition = regrouper(frag.transitions)
    for src, dst in sorted(grp_transition):        # ordre stable : fichier reproductible
        symbole_lu = ",".join(grp_transition[(src, dst)]) # ['a', 'b'] devient "a,b"
        lignes.append(f'  {src} -> {dst} [label="{symbole_lu}"];')
    lignes.append("}")
    return "\n".join(lignes) + "\n"


def ecrire_dot(frag, chemin, nom="AFN"):
    """Ecrit l'automate dans le fichier `chemin` (UTF-8, a cause de ε)."""
    with open(chemin, "w", encoding="utf-8", newline="\n") as f:
        f.write(vers_dot(frag, nom))
