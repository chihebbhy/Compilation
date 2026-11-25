"""Tests des extensions."""
import sys
from itertools import product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from parser import Parser
from simulation import reconnaitre
from afd import determiniser, minimiser, equivalents, accepte_afd, etats_afd
from recuperation import ParserRecuperation, ErreursMultiples


def afn(expr):
    return Parser(expr).analyse()


# AFD et AFD minimal : memes reponses que l'AFN sur tous les mots courts
for expr in ["a", "a|b", "ab*", "(a|b)*abb", "(ab)+", "a?b", "(a*)*",
             "a(b|c)*d", "@", "a|bc*"]:
    frag = afn(expr)
    d = determiniser(frag)
    m = minimiser(d)
    for longueur in range(6):
        for lettres in product("abcd", repeat=longueur):
            mot = "".join(lettres)
            attendu = reconnaitre(frag, mot)
            assert accepte_afd(d, mot) == attendu, (expr, mot, "AFD")
            assert accepte_afd(m, mot) == attendu, (expr, mot, "min")
    assert len(etats_afd(m)) <= len(etats_afd(d))
assert len(etats_afd(minimiser(determiniser(afn("(a|b)*abb"))))) == 4
print("AFD et minimisation : OK")

# Equivalence
assert equivalents(afn("(a|b)*"), afn("(a*b*)*")) == (True, None)
assert equivalents(afn("aa*"), afn("a+")) == (True, None)
assert equivalents(afn("a+"), afn("a*")) == (False, "")
assert equivalents(afn("ab"), afn("a|b")) == (False, "a")
print("Equivalence : OK")


# Mode panique : positions de toutes les erreurs
def positions(expr):
    try:
        ParserRecuperation(expr).analyse()
    except ErreursMultiples as e:
        return [x.position for x in e.erreurs]
    return []


for expr, attendu in [("a||b)(|c", [2, 4, 6, 8]), ("*a|b|", [0, 5]),
                      ("a#b$", [1, 3]), ("()()", [1, 3]), ("(", [1]),
                      ("a)", [1]), ("(a|b)*abb", [])]:
    assert positions(expr) == attendu, (expr, positions(expr))
print("Mode panique : OK")
