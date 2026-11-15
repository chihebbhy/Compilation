"""Analyseur predictif a descente recursive (Parties 2, 3 et 4).

Grammaire LL(1) :

    R  -> T R'
    R' -> '|' T R' | epsilon
    T  -> F T'
    T' -> F T' | epsilon
    F  -> A F'
    F' -> '*' F' | '+' F' | '?' F' | epsilon
    A  -> '(' R ')' | SYMBOLE | '@'

Une procedure par non-terminal, sans retour arriere. Les actions
semantiques construisent un fragment d'automate (voir automate.py). Le
prochain numero d'etat libre circule en attribut (parametre / valeur de
retour) : aucun compteur global ou statique.
"""

from lexer import analyser 
