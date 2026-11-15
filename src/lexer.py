"""Analyse lexicale (Partie 2) - Etudiant 1.

Decoupe le texte d'une expression reguliere en jetons. Chaque jeton porte
sa nature, sa valeur et sa position dans la chaine.

Interdit : le module `re` ou toute bibliotheque d'expressions regulieres.
"""
from enum import Enum
from string import ascii_letters, digits

TokenType = Enum('TokenType', [
    'SYMBOLE',
    'VIDE',
    'UNION',
    'ETOILE',
    'PLUS',
    'OPTION',
    'LEFTPAR',
    'RIGHTPAR',
    'EOF',
])

ALPHANUM = set(ascii_letters + digits)

# caractere special -> nature du jeton
SPECIAUX = {
    '@': TokenType.VIDE,
    '|': TokenType.UNION,
    '*': TokenType.ETOILE,
    '+': TokenType.PLUS,
    '?': TokenType.OPTION,
    '(': TokenType.LEFTPAR,
    ')': TokenType.RIGHTPAR,
}


class ErreurLexicale(Exception):
    def __init__(self, position, trouve):
        super().__init__(
            f"Erreur à la position {position} : "
            f"caractère '{trouve}' invalide"
        )
        self.position = position


class Token:
    def __init__(self, type=None, lexeme="", position=None):
        self.type = type
        self.lexeme = lexeme
        self.position = position

    def __repr__(self):
        return f"Token({self.type.name}, {self.lexeme!r}, {self.position})"


class Lexer:
    def __init__(self, string):
        self.string = string
        self.index = 0

    def nextToken(self):
        pos = self.index
        if pos >= len(self.string):
            return Token(TokenType.EOF, "", pos)

        c = self.string[pos]
        if c in ALPHANUM:
            self.index += 1
            return Token(TokenType.SYMBOLE, c, pos)
        if c in SPECIAUX:
            self.index += 1
            return Token(SPECIAUX[c], c, pos)
        raise ErreurLexicale(pos, c)