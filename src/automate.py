"""Fragments d'automate et construction de Thompson (Parties 3 et 4) - Etudiant 2.

Un fragment est un triplet (init, fin, transitions) : un seul etat initial
sans transition entrante, un seul etat d'acceptation sans transition
sortante. Propriete a respecter : au plus 2n etats.

Representation (a respecter par l'export Graphviz et la simulation) :
  - un etat est un entier ;
  - une transition est un triplet (source, etiquette, cible) ;
  - l'etiquette est un caractere, ou EPS (= None) pour une epsilon-transition ;
  - `transitions` est une liste.

Chaque constructeur recoit le prochain numero d'etat libre `n` et rend le
fragment construit ET le prochain numero libre mis a jour : (fragment, n').
Le compteur circule donc comme attribut (herite en entree, synthetise en
sortie). Aucune variable globale ou statique.

Les fragments ne sont jamais modifies : les constructeurs fabriquent de
nouvelles listes de transitions, sans dupliquer d'etats.
"""

from collections import namedtuple

EPS = None  # etiquette d'une epsilon-transition

Fragment = namedtuple("Fragment", ["init", "fin", "transitions"])


def symbole(c, n):
    """N(a) : i -a-> f. Consomme 2 numeros."""
    i, f = n, n + 1
    return Fragment(i, f, [(i, c, f)]), n + 2


def mot_vide(n):
    """N(@) : i -eps-> f. Consomme 2 numeros."""
    i, f = n, n + 1
    return Fragment(i, f, [(i, EPS, f)]), n + 2


def union(r, s, n):
    """N(r|s) : nouveaux etats i et f. Consomme 2 numeros."""
    i, f = n, n + 1
    trans = (r.transitions + s.transitions + [
        (i, EPS, r.init), (i, EPS, s.init),
        (r.fin, EPS, f), (s.fin, EPS, f),
    ])
    return Fragment(i, f, trans), n + 2


def concat(r, s, n):
    """N(rs) : fin(r) -eps-> init(s). Aucun nouvel etat (n inchange)."""
    trans = r.transitions + s.transitions + [(r.fin, EPS, s.init)]
    return Fragment(r.init, s.fin, trans), n


def etoile(r, n):
    """N(r*) : nouveaux etats i et f. Consomme 2 numeros."""
    i, f = n, n + 1
    trans = r.transitions + [
        (i, EPS, r.init), (r.fin, EPS, f),
        (r.fin, EPS, r.init), (i, EPS, f),
    ]
    return Fragment(i, f, trans), n + 2


def plus(r, n):
    """N(r+) = N(r) puis boucle, sans dupliquer r : c'est r* privee de
    l'epsilon-transition i -> f (donc au moins une occurrence)."""
    i, f = n, n + 1
    trans = r.transitions + [
        (i, EPS, r.init), (r.fin, EPS, f),
        (r.fin, EPS, r.init),
    ]
    return Fragment(i, f, trans), n + 2


def optionnel(r, n):
    """N(r?) = N(r | eps), sans dupliquer r : r* privee de la boucle
    fin(r) -> init(r) (donc au plus une occurrence)."""
    i, f = n, n + 1
    trans = r.transitions + [
        (i, EPS, r.init), (r.fin, EPS, f),
        (i, EPS, f),
    ]
    return Fragment(i, f, trans), n + 2


def etats(frag):
    """Ensemble des etats d'un fragment."""
    ens = {frag.init, frag.fin}
    for src, _, dst in frag.transitions:
        ens.add(src)
        ens.add(dst)
    return ens
