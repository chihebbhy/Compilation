"""Analyse lexicale (Partie 2) - Etudiant 1.

Decoupe le texte d'une expression reguliere en jetons. Chaque jeton porte
sa nature, sa valeur et sa position dans la chaine.

Interdit : le module `re` ou toute bibliotheque d'expressions regulieres.
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
])


class Token:
    def __init__(self,type=None,lexeme="",position=None):
        self.type = type
        self.lexeme = lexeme
        self.position = position

class Lexer:
    def __init__(self):
        self.string = None
        self.index = 0
    def nextToken(self):
        if self.index >= self.string.length():
            return None
        c = self.string[self.index]
        if c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789":
            self.index += 1
            return Token(type=TokenType('SYMBOLE'),
                        lexeme=c,
                        position=self.index -1
                        )
        elif c == '@':
            self.index += 1
            return Token(type=TokenType('VIDE'),
                        position=self.index -1
                        )
        elif c == '|':
            self.index += 1
            return Token(type=TokenType('UNION'),
                        position=self.index -1
                        )
        elif c == '*':
            self.index += 1
            return Token(type=TokenType('ETOILE'),
                        position=self.index -1
                        )
        elif c == '+':
            self.index += 1
            return Token(type=TokenType('PLUS'),
                        position=self.index -1
                        )
        elif c == '?':
            self.index += 1
            return Token(type=TokenType('OPTION'),
                        position=self.index -1
                        )
        elif c == '(':
            self.index += 1
            return Token(type=TokenType('RIGHTPAR'),
                        position=self.index -1
                        )
        elif c == ')':
            self.index += 1
            return Token(type=TokenType('LEFTPAR'),
                        position=self.index -1
                        )
        else:
            return 