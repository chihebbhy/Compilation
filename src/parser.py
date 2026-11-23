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

Schema de traduction (h = attribut herite : fragment deja construit,
s = attribut synthetise, n = prochain etat libre, herite ; n' synthetise) :

    R      -> T R'      { R'.h = T.s ; R'.n = T.n' ; R.s = R'.s }
    R'     -> '|' T R'1 { R'1.h = union(R'.h, T.s) ; R'.s = R'1.s }
    R'     -> eps       { R'.s = R'.h }
    T      -> F T'      { T'.h = F.s ; T.s = T'.s }
    T'     -> F T'1     { T'1.h = concat(T'.h, F.s) ; T'.s = T'1.s }
    T'     -> eps       { T'.s = T'.h }
    F      -> A F'      { F'.h = A.s ; F.s = F'.s }
    F'     -> '*' F'1   { F'1.h = etoile(F'.h) ; F'.s = F'1.s }   (idem + et ?)
    F'     -> eps       { F'.s = F'.h }
    A      -> '(' R ')' { A.s = R.s }
    A      -> SYMBOLE   { A.s = symbole(SYMBOLE.lexeme) }
    A      -> '@'       { A.s = mot_vide() }
"""
import sys

import automate
from lexer import Lexer, TokenType

Types = TokenType
_FIRST_F = (Types.LEFTPAR, Types.SYMBOLE, Types.VIDE)
# ordre d'affichage des jetons attendus
_ORDRE = [Types.UNION, Types.ETOILE, Types.PLUS, Types.OPTION, Types.LEFTPAR,
          Types.RIGHTPAR, Types.SYMBOLE, Types.VIDE, Types.EOF]
_NOMS = {Types.UNION: "'|'", Types.ETOILE: "'*'", Types.PLUS: "'+'",
         Types.OPTION: "'?'", Types.LEFTPAR: "'('", Types.RIGHTPAR: "')'",
         Types.SYMBOLE: "symbole", Types.VIDE: "'@'",
         Types.EOF: "fin de l'expression"}


class ErreurSyntaxique(Exception):
    def __init__(self, position, attendus, trouve):
        noms = [_NOMS[t] for t in _ORDRE if t in set(attendus)]
        if len(noms) > 1:
            liste = ", ".join(noms[:-1]) + " ou " + noms[-1]
        else:
            liste = noms[0]
        found = ("fin de l'expression" if trouve.type == Types.EOF
                 else f"'{trouve.lexeme}'")
        super().__init__(
            f"Erreur à la position {position} : {liste} attendu, {found} trouvé"
        )
        self.position = position


class Parser:
    def __init__(self, text):
        self.lexer = Lexer(text)
        self.current = self.lexer.nextToken()
        self.attendus = set()   # types testes depuis le dernier jeton consomme
        self.prochain = 0       # prochain etat libre apres analyse()

    # -- outils -----------------------------------------------------------
    def peek(self):
        return self.current.type

    def tester(self, *types):
        """Teste le lookahead et memorise ce qui etait attendu."""
        self.attendus.update(types)
        return self.current.type in types

    def consume(self, expected):
        if not self.tester(expected):
            self.erreur()
        token = self.current
        self.current = self.lexer.nextToken()
        self.attendus = set()
        return token

    def erreur(self):
        raise ErreurSyntaxique(self.current.position, self.attendus,
                               self.current)

    # -- point d'entree ---------------------------------------------------
    def analyse(self, n0=0):
        """Analyse R puis verifie la fin de l'entree. Rend le fragment
        (init, fin, transitions) ; self.prochain = prochain etat libre.
        Leve ErreurLexicale / ErreurSyntaxique si l'expression est invalide.
        Le numero de depart n0 est un parametre : aucun etat global."""
        # une procedure recursive par symbole/operateur : on releve la limite
        sys.setrecursionlimit(max(sys.getrecursionlimit(), 20000))
        frag, n = self.R(n0)
        self.consume(Types.EOF)
        self.prochain = n
        return frag

    # -- une procedure par non-terminal ----------------------------------
    # Chacune rend (fragment synthetise s, prochain etat libre n').

    def R(self, n):
        t, n = self.T(n)
        return self.Rp(t, n)

    def Rp(self, h, n):
        if self.tester(Types.UNION):
            self.consume(Types.UNION)
            t, n = self.T(n)
            h, n = automate.union(h, t, n)
            return self.Rp(h, n)
        return h, n  # R' -> epsilon

    def T(self, n):
        f, n = self.F(n)
        return self.Tp(f, n)

    def Tp(self, h, n):
        # la concatenation est implicite : on continue si FIRST(F)
        if self.tester(*_FIRST_F):
            f, n = self.F(n)
            h, n = automate.concat(h, f, n)
            return self.Tp(h, n)
        return h, n  # T' -> epsilon

    def F(self, n):
        a, n = self.A(n)
        return self.Fp(a, n)

    def Fp(self, h, n):
        if self.tester(Types.ETOILE):
            self.consume(Types.ETOILE)
            h, n = automate.etoile(h, n)
            return self.Fp(h, n)
        if self.tester(Types.PLUS):
            self.consume(Types.PLUS)
            h, n = automate.plus(h, n)
            return self.Fp(h, n)
        if self.tester(Types.OPTION):
            self.consume(Types.OPTION)
            h, n = automate.optionnel(h, n)
            return self.Fp(h, n)
        return h, n  # F' -> epsilon

    def A(self, n):
        if self.tester(Types.LEFTPAR):
            self.consume(Types.LEFTPAR)
            r, n = self.R(n)
            self.consume(Types.RIGHTPAR)
            return r, n
        if self.tester(Types.SYMBOLE):
            jeton = self.consume(Types.SYMBOLE)
            return automate.symbole(jeton.lexeme, n)
        if self.tester(Types.VIDE):
            self.consume(Types.VIDE)
            return automate.mot_vide(n)
        self.erreur()


def compter_n(texte):
    """n = nombre de symboles et d'operateurs (@ | * + ?), hors
    concatenation et parentheses : sert a verifier 'au plus 2n etats'."""
    lexer = Lexer(texte)
    compte = 0
    while True:
        j = lexer.nextToken()
        if j.type == Types.EOF:
            return compte
        if j.type not in (Types.LEFTPAR, Types.RIGHTPAR):
            compte += 1


if __name__ == "__main__":
    texte = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        Parser(texte).analyse()
        print("Expression valide")
    except Exception as e:
        print(e)
        sys.exit(1)
