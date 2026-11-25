"""Simulation de l'AFN (Partie 5) - Etudiant 3.

Reconnaissance d'un mot w par un fragment (init, fin, transitions) construit
par automate.py :

  1. S = epsilon-fermeture({init}) ;
  2. pour chaque caractere c de w :
         S = epsilon-fermeture(etats atteints depuis S par une transition c) ;
  3. w est accepte si l'etat d'acceptation `fin` appartient a S.

L'epsilon-fermeture est un parcours du graphe qui memorise les etats deja
visites : chaque etat est traite une seule fois, donc pas de boucle infinie
sur les cycles d'epsilon-transitions (par exemple (a*)*).

etats: l ensemble des etats 
c: caract entrain de lire 
table : dict des transitions 
"""
from automate import EPS


def table_transitions(frag): # ranger les transitions dans un dict table
    table = {}
    # Avant : [(0,'a',1), (0,'a',2), (1,EPS,3)]
    #Après : {(0,'a'): {1,2}, (1,EPS): {3}} depuis l etat  on peut aller en  ou 
    for src, symbole_lu, dst in frag.transitions:
        if (src, symbole_lu) not in table:
             table[(src, symbole_lu)] = set() # set cree ensemble vide
        table[(src, symbole_lu)].add(dst)  # hors du if : toutes les cibles
    return table


def epsilon_fermeture(etats, table): # ajouter etat sans lire la lettre 
    etat_lu=set(etats)
    a_traiter = list(etats)  # pile des etats restant a explorer par ordre
    while a_traiter:
        e = a_traiter.pop()
        for cible in table.get((e, EPS), ()):
            if cible not in etat_lu:
                etat_lu.add(cible)
                a_traiter.append(cible)
    return etat_lu


def transition(etats, c, table): # avance pas en laisant une lettre calcule tous les etats qu'on peut atteindre en lisant c
    atteints = set()
    for e in etats:
        if (e, c) in table:
            for cible in table[(e, c)]:
                atteints.add(cible)
    return atteints


def reconnaitre(frag, mot): # true or false 
    #Vrai si l'automate `frag` accepte `mot` (chaine, "" = mot vide)
    table = table_transitions(frag)
    courant = epsilon_fermeture({frag.init}, table)
    for c in mot:
        courant = epsilon_fermeture(transition(courant, c, table), table)
        if not courant:              # plus aucun etat actif : rejet certain
            return False
    return frag.fin in courant
