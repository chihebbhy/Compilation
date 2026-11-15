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
from lexer import Lexer, TokenType, ErreurLexicale

T = TokenType
_FIRST_F = (T.LEFTPAR, T.SYMBOLE, T.VIDE)
_ORDRE = [T.UNION, T.ETOILE, T.PLUS, T.OPTION, T.LEFTPAR, T.RIGHTPAR,
          T.SYMBOLE, T.VIDE, T.EOF]
_NOMS = {T.UNION: "'|'", T.ETOILE: "'*'", T.PLUS: "'+'", T.OPTION: "'?'",
         T.LEFTPAR: "'('", T.RIGHTPAR: "')'", T.SYMBOLE: "symbole",
         T.VIDE: "'@'", T.EOF: "fin de l'expression"}


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
        self.attendus = set()  # types testes depuis le dernier jeton consomme

    # -- outils -----------------------------------------------------------
    def tester(self, *types):
        """Teste le lookahead et memorise ce qui etait attendu."""
        self.attendus.update(types)
        return self.courant.type in types

    def consommer(self, type_):
        if not self.tester(type_):
            self.erreur()
        jeton = self.courant
        self.courant = self.lexer.nextToken()
        self.attendus = set()
        return jeton

    def erreur(self):
        liste = [_NOMS[t] for t in _ORDRE if t in self.attendus]
        if len(liste) > 1:
            attendus = [", ".join(liste[:-1]) + " ou " + liste[-1]]
        else:
            attendus = liste
        c = self.courant
        trouve = _NOMS[T.EOF] if c.type == T.EOF else repr(c.lexeme).replace('"', "'")
        raise ErreurSyntaxique(c.position, attendus, trouve)

    # -- point d'entree ---------------------------------------------------
    def analyser(self, n0=0):
        """Analyse R, puis verifie que la fin de l'entree est atteinte.
        Rend (fragment, prochain etat libre). Leve ErreurLexicale /
        ErreurSyntaxique si l'expression est invalide. Le numero de depart
        est un parametre : aucun etat global."""
        # une procedure recursive par operateur/symbole : on releve la limite
        sys.setrecursionlimit(max(sys.getrecursionlimit(), 20000))
        frag, n = self.R(n0)
        self.consommer(T.EOF)
        return frag, n

    # -- une procedure par non-terminal ----------------------------------
    # Chacune rend (fragment synthetise s, prochain etat libre n').

    def R(self, n):
        t, n = self.T(n)
        return self.Rp(t, n)

    def Rp(self, h, n):
        if self.tester(T.UNION):
            self.consommer(T.UNION)
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
        if self.tester(T.ETOILE):
            self.consommer(T.ETOILE)
            h, n = automate.etoile(h, n)
            return self.Fp(h, n)
        if self.tester(T.PLUS):
            self.consommer(T.PLUS)
            h, n = automate.plus(h, n)
            return self.Fp(h, n)
        if self.tester(T.OPTION):
            self.consommer(T.OPTION)
            h, n = automate.optionnel(h, n)
            return self.Fp(h, n)
        return h, n  # F' -> epsilon

    def A(self, n):
        if self.tester(T.LEFTPAR):
            self.consommer(T.LEFTPAR)
            r, n = self.R(n)
            self.consommer(T.RIGHTPAR)
            return r, n
        if self.tester(T.SYMBOLE):
            jeton = self.consommer(T.SYMBOLE)
            return automate.symbole(jeton.lexeme, n)
        if self.tester(T.VIDE):
            self.consommer(T.VIDE)
            return automate.mot_vide(n)
        self.erreur()


def traduire(texte, n0=0):
    """Rend (fragment, prochain etat libre) ; leve une erreur si invalide."""
    return Parser(texte).analyser(n0)


def compter_n(texte):
    """n = nombre de symboles et d'operateurs (@ | * + ?), hors
    concatenation et parentheses : sert a verifier 'au plus 2n etats'."""
    lexer = Lexer(texte)
    compte = 0
    while True:
        j = lexer.nextToken()
        if j.type == T.EOF:
            return compte
        if j.type not in (T.LEFTPAR, T.RIGHTPAR):
            compte += 1
