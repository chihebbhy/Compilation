"""Analyse lexicale (Partie 2) - Etudiant 1.

Decoupe le texte d'une expression reguliere en jetons. Chaque jeton porte
sa nature, sa valeur et sa position dans la chaine.

Interdit : le module `re` ou toute bibliotheque d'expressions regulieres.

NOTE : la version poussee par l'Etudiant 1 ("en cours") ne fonctionnait pas
encore (Lexer sans parametre, `.length()`, parentheses inversees, pas de
ErreurLexicale, pas de jeton de fin). L'Etudiant 2 l'a corrigee en gardant
les memes noms (TokenType, Token, Lexer.nextToken) : a relire par l'Etudiant 1.
"""
from enum import Enum

TokenType = Enum('TokenType', [
    'SYMBOLE',
    'VIDE',
    'UNION',
    'ETOILE',
    'PLUS',
    'OPTION',
    'LEFTPAR',
    'RIGHTPAR',
    'FIN',
])


class ErreurLexicale(Exception):
    """Caractere non autorise, avec sa position (0-indexee)."""

    def __init__(self, position, caractere):
        super().__init__(
            f"Erreur à la position {position} : "
            f"caractère {caractere!r} non autorisé"
        )
        self.position = position


class Token:
    def __init__(self, type=None, lexeme="", position=None):
        self.type = type
        self.lexeme = lexeme
        self.position = position

    def __repr__(self):
        return f"Token({self.type.name}, {self.lexeme!r}, {self.position})"


_OPERATEURS = {
    '@': TokenType.VIDE,
    '|': TokenType.UNION,
    '*': TokenType.ETOILE,
    '+': TokenType.PLUS,
    '?': TokenType.OPTION,
    '(': TokenType.LEFTPAR,
    ')': TokenType.RIGHTPAR,
}


def _alphanumerique(c):
    return ("a" <= c <= "z") or ("A" <= c <= "Z") or ("0" <= c <= "9")


class Lexer:
    def __init__(self, texte=""):
        self.string = texte
        self.index = 0

    def nextToken(self):
        """Jeton suivant ; un jeton FIN (repete) a la fin de l'entree."""
        if self.index >= len(self.string):
            return Token(TokenType.FIN, "", len(self.string))
        c = self.string[self.index]
        pos = self.index
        if _alphanumerique(c):
            self.index += 1
            return Token(TokenType.SYMBOLE, c, pos)
        if c in _OPERATEURS:
            self.index += 1
            return Token(_OPERATEURS[c], c, pos)
        raise ErreurLexicale(pos, c)
