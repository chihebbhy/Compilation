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
from lexer import Lexer, TokenType


class ErreurSyntaxique(Exception):
    """Erreur de syntaxe : position, jetons attendus, jeton trouve."""

    def __init__(self, position, attendus, trouve):
        super().__init__(
            f"Erreur à la position {position} : "
            f"{' ou '.join(attendus)} attendu, {trouve} trouvé"
        )
        self.position = position


class Parser:
    def __init__(self, texte):
        self.lexer = Lexer(texte)
        self.courant = self.lexer.nextToken()   # jeton de pre-vision (lookahead)

    def analyser(self):
        """Analyse R, puis verifie que la fin de l'entree est atteinte.
        A completer (Etudiant 2) : une methode par non-terminal
        R, R', T, T', F, F', A."""
        pass
    def printTokens(self):
        """Affiche tous les jetons de l'analyse lexicale."""
        self.lexer.index = 0
        c = self.lexer.nextToken()
        while c.type != TokenType.EOF:
            print(c)
            c = self.lexer.nextToken()