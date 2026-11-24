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
import sys
from lexer import Lexer, TokenType
from automate import (
    symbole,
    mot_vide,
    union,
    concat,
    etoile,
    plus,
    optionnel,
)

Types = TokenType
_FIRST_F = (Types.LEFTPAR, Types.SYMBOLE, Types.VIDE)
_NOMS = {
    Types.UNION: "'|'",
    Types.ETOILE: "'*'",
    Types.PLUS: "'+'",
    Types.OPTION: "'?'",
    Types.LEFTPAR: "'('",
    Types.RIGHTPAR: "')'",
    Types.SYMBOLE: "symbole",
    Types.VIDE: "'@'",
    Types.EOF: "fin de l'expression",
}


class ErreurSyntaxique(Exception):
    def __init__(self, position, attendus, trouve):
        noms = [_NOMS[t] for t in attendus]
        if len(noms) > 1:
            liste = ", ".join(noms[:-1]) + " ou " + noms[-1]
        else:
            liste = noms[0]
        found = "fin de l'expression" if trouve.type == Types.EOF else f"'{trouve.lexeme}'"
        super().__init__(
            f"Erreur à la position {position} : {liste} attendu, {found} trouvé"
        )
        self.position = position


class Parser:
    def __init__(self, text):
        self.lexer = Lexer(text)
        self.current = self.lexer.nextToken()

    def consume(self, expected):
        if self.peek() != expected:
            raise ErreurSyntaxique(self.current.position, [expected], self.current)
        token = self.current
        self.current = self.lexer.nextToken()
        return token

    def peek(self):
        return self.current.type

    def traduire(self, n0=0):
        frag, n_suivant = self.R(n0)
        self.consume(Types.EOF)
        return frag, n_suivant

    def analyse(self, n0=0):
        frag, _ = self.traduire(n0)
        return frag

    def R(self, n):
        frag, n = self.T(n)
        return self.Rp(frag, n)

    def Rp(self, acc, n):
        if self.peek() == Types.UNION:
            self.consume(Types.UNION)
            droite, n = self.T(n)
            frag, n = union(acc, droite, n)
            return self.Rp(frag, n)
        return acc, n

    def T(self, n):
        frag, n = self.F(n)
        return self.Tp(frag, n)

    def Tp(self, acc, n):
        if self.peek() in _FIRST_F:
            droite, n = self.F(n)
            frag, n = concat(acc, droite, n)
            return self.Tp(frag, n)
        return acc, n

    def F(self, n):
        frag, n = self.A(n)
        return self.Fp(frag, n)

    def Fp(self, acc, n):
        if self.peek() == Types.ETOILE:
            self.consume(Types.ETOILE)
            frag, n = etoile(acc, n)
            return self.Fp(frag, n)
        if self.peek() == Types.PLUS:
            self.consume(Types.PLUS)
            frag, n = plus(acc, n)
            return self.Fp(frag, n)
        if self.peek() == Types.OPTION:
            self.consume(Types.OPTION)
            frag, n = optionnel(acc, n)
            return self.Fp(frag, n)
        return acc, n

    def A(self, n):
        if self.peek() == Types.LEFTPAR:
            self.consume(Types.LEFTPAR)
            frag, n = self.R(n)
            self.consume(Types.RIGHTPAR)
            return frag, n
        if self.peek() == Types.SYMBOLE:
            tok = self.consume(Types.SYMBOLE)
            return symbole(tok.lexeme, n)
        if self.peek() == Types.VIDE:
            self.consume(Types.VIDE)
            return mot_vide(n)
        raise ErreurSyntaxique(self.current.position, _FIRST_F, self.current)


if __name__ == "__main__":
    texte = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        Parser(texte).analyse()
        print("Expression valide")
    except Exception as e:
        print(e)
        sys.exit(1)