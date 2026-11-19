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
from lexer import Lexer, TokenType

Types = TokenType
_FIRST_F = (Types.LEFTPAR, Types.SYMBOLE, Types.VIDE)
_NOMS = {Types.UNION: "'|'", Types.ETOILE: "'*'", Types.PLUS: "'+'",
         Types.OPTION: "'?'", Types.LEFTPAR: "'('", Types.RIGHTPAR: "')'",
         Types.SYMBOLE: "symbole", Types.VIDE: "'@'",
         Types.EOF: "fin de l'expression"}

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

class Parser():
    def __init__(self,text):
        self.lexer = Lexer(text)
        self.current = self.lexer.nextToken()

    def consume(self,expected):
        if self.peek() != expected:
            raise ErreurSyntaxique(self.current.position, [expected], self.current)
        token = self.current
        self.current = self.lexer.nextToken()
        return token

    def peek(self):
        return self.current.type

    def analyse(self):
        self.R()
        self.consume(Types.EOF)

    def R(self):
        self.T()
        self.Rp()

    def Rp(self):
        if self.peek() == Types.UNION:
            self.consume(Types.UNION)
            self.T()
            self.Rp()
        # else epsilon

    def T(self):
        self.F()
        self.Tp()

    def Tp(self):
        if self.peek() in _FIRST_F :
            self.F()
            self.Tp()
        # else epsilon
    def F(self):
        self.A()
        self.Fp()

    def Fp(self):
        if self.peek() == Types.ETOILE:
            self.consume(Types.ETOILE)
            self.Fp()
        elif self.peek() == Types.PLUS:
            self.consume(Types.PLUS)
            self.Fp()
        elif self.peek() == Types.OPTION:
            self.consume(Types.OPTION)
            self.Fp()
        # else epsilon

    def A(self):
        if self.peek() == Types.LEFTPAR:
            self.consume(Types.LEFTPAR)
            self.R()
            self.consume(Types.RIGHTPAR)
        elif self.peek() == Types.SYMBOLE:
            self.consume(Types.SYMBOLE)
        elif self.peek() == Types.VIDE:
            self.consume(Types.VIDE)
        else:
            raise ErreurSyntaxique(self.current.position, _FIRST_F, self.current)



if __name__ == "__main__":
    texte = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        Parser(texte).analyse()
        print("Expression valide")
    except Exception as e:
        print(e)
        sys.exit(1)