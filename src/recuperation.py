"""Extension : recuperation d'erreur en mode panique.

On herite de Parser : l'analyseur normal ne change pas. Au lieu de s'arreter
a la premiere erreur, on la memorise puis on se resynchronise.
"""
import automate
from lexer import ErreurLexicale
from parser import Parser, ErreurSyntaxique, Types

_POSTFIXES = (Types.ETOILE, Types.PLUS, Types.OPTION)
_FIRST_A = (Types.LEFTPAR, Types.SYMBOLE, Types.VIDE)
# jetons de synchronisation : on abandonne l'operande manquant sans les manger
_SYNCHRO = (Types.UNION, Types.RIGHTPAR, Types.EOF)


class ErreursMultiples(Exception):
    def __init__(self, erreurs):
        super().__init__("\n".join(str(e) for e in erreurs))
        self.erreurs = erreurs


class ParserRecuperation(Parser):
    def __init__(self, text):
        self.erreurs = []
        super().__init__("")               # initialise les attributs
        self.lexer.string = text
        self.lexer.index = 0
        self.current = self._suivant()

    def _suivant(self):
        """Jeton suivant ; un caractere interdit est signale puis saute."""
        while True:
            try:
                return self.lexer.nextToken()
            except ErreurLexicale as e:
                self.erreurs.append(e)
                self.lexer.index += 1

    def _signaler(self):
        position = self.current.position
        if all(e.position != position for e in self.erreurs):  # pas de doublon
            self.erreurs.append(
                ErreurSyntaxique(position, self.attendus, self.current))

    def _avancer(self):
        token = self.current
        self.current = self._suivant()
        self.attendus = set()
        return token

    def consume(self, expected):
        if not self.tester(expected):
            self._signaler()       # ex. ')' manquante : on fait comme si
            return None
        return self._avancer()

    def A(self, n):
        while True:
            if self.peek() in _FIRST_A:
                return super().A(n)
            self.tester(*_FIRST_A)
            self._signaler()
            if self.peek() in _SYNCHRO:
                return automate.mot_vide(n)   # operande manquant : bouche-trou
            self._avancer()                   # '*', '+', '?' isole : on saute

    def analyse(self, n0=0):
        while True:
            frag, n = self.R(n0)
            if self.peek() == Types.EOF:
                break
            self.tester(Types.EOF)            # il reste une ')' en trop
            self._signaler()
            self._avancer()
            while self.peek() in _POSTFIXES + (Types.UNION,):
                self._avancer()               # evite les erreurs en cascade
            if self.peek() == Types.EOF:
                break
        if self.erreurs:
            self.erreurs.sort(key=lambda e: e.position)
            raise ErreursMultiples(self.erreurs)
        self.prochain = n
        return frag
