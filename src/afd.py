"""Extensions : determinisation, minimisation (Moore), equivalence."""
from collections import namedtuple

from automate import EPS
from export_dot import regrouper
from simulation import table_transitions, epsilon_fermeture, transition

# Un AFD : etat initial, ensemble des etats acceptants,
# dictionnaire (etat, lettre) -> etat, alphabet trie.
AFD = namedtuple("AFD", ["init", "finaux", "delta", "alphabet"])


def alphabet_de(frag):
    return sorted({c for _, c, _ in frag.transitions if c is not EPS})


# ---------- Determinisation (construction des sous-ensembles) ----------

def determiniser(frag, alphabet=None):
    if alphabet is None:
        alphabet = alphabet_de(frag)
    table = table_transitions(frag)
    depart = frozenset(epsilon_fermeture({frag.init}, table))
    numero = {depart: 0}          # ensemble d'etats AFN -> numero AFD
    a_traiter = [depart]
    delta = {}
    finaux = set()
    for ensemble in a_traiter:    # la liste grandit pendant le parcours
        q = numero[ensemble]
        if frag.fin in ensemble:
            finaux.add(q)
        for c in alphabet:
            suivant = frozenset(
                epsilon_fermeture(transition(ensemble, c, table), table))
            if not suivant:
                continue          # pas de transition (puits implicite)
            if suivant not in numero:
                numero[suivant] = len(numero)
                a_traiter.append(suivant)
            delta[(q, c)] = numero[suivant]
    return AFD(0, finaux, delta, list(alphabet))


def accepte_afd(afd, mot):
    q = afd.init
    for c in mot:
        if (q, c) not in afd.delta:
            return False
        q = afd.delta[(q, c)]
    return q in afd.finaux


def etats_afd(afd):
    ens = {afd.init} | afd.finaux
    for (src, _), dst in afd.delta.items():
        ens.add(src)
        ens.add(dst)
    return ens


# ---------- Minimisation (Moore) ----------

def completer(afd, alphabet):
    """Ajoute un etat puits pour que chaque (etat, lettre) soit defini."""
    etats = etats_afd(afd)
    puits = max(etats) + 1
    delta = dict(afd.delta)
    utilise = False
    for q in etats:
        for c in alphabet:
            if (q, c) not in delta:
                delta[(q, c)] = puits
                utilise = True
    if utilise:
        for c in alphabet:
            delta[(puits, c)] = puits
    return AFD(afd.init, set(afd.finaux), delta, list(alphabet))


def minimiser(afd):
    complet = completer(afd, afd.alphabet)
    etats = sorted(etats_afd(complet))
    # partition de depart : acceptants / non acceptants
    groupe = {q: int(q in complet.finaux) for q in etats}
    while True:
        # signature = mon groupe + les groupes atteints par chaque lettre
        signatures = {}
        nouveau = {}
        for q in etats:
            sig = (groupe[q], tuple(groupe[complet.delta[(q, c)]]
                                    for c in complet.alphabet))
            nouveau[q] = signatures.setdefault(sig, len(signatures))
        stable = len(signatures) == len(set(groupe.values()))
        groupe = nouveau
        if stable:
            break
    delta = {(groupe[q], c): groupe[d] for (q, c), d in complet.delta.items()}
    finaux = {groupe[q] for q in complet.finaux}
    init = groupe[complet.init]

    # retirer l'etat puits (non acceptant, boucle sur lui-meme)
    puits = {g for g in set(groupe.values())
             if g not in finaux and g != init
             and all(delta[(g, c)] == g for c in complet.alphabet)}
    delta = {k: d for k, d in delta.items()
             if k[0] not in puits and d not in puits}

    # renumeroter 0, 1, 2... dans l'ordre d'un parcours en largeur
    numero = {init: 0}
    file = [init]
    for g in file:
        for c in complet.alphabet:
            if (g, c) in delta and delta[(g, c)] not in numero:
                numero[delta[(g, c)]] = len(numero)
                file.append(delta[(g, c)])
    return AFD(0,
               {numero[g] for g in finaux},
               {(numero[g], c): numero[d] for (g, c), d in delta.items()},
               complet.alphabet)


# ---------- Equivalence de deux expressions ----------

def equivalents(frag1, frag2):
    """Rend (True, None) ou (False, mot_contre_exemple)."""
    alphabet = sorted(set(alphabet_de(frag1)) | set(alphabet_de(frag2)))
    a = completer(determiniser(frag1, alphabet), alphabet)
    b = completer(determiniser(frag2, alphabet), alphabet)
    depart = (a.init, b.init)
    vus = {depart}
    file = [(depart, "")]
    for (p, q), mot in file:          # parcours en largeur des paires
        if (p in a.finaux) != (q in b.finaux):
            return False, mot         # un seul des deux accepte ce mot
        for c in alphabet:
            paire = (a.delta[(p, c)], b.delta[(q, c)])
            if paire not in vus:
                vus.add(paire)
                file.append((paire, mot + c))
    return True, None


# ---------- Export Graphviz d'un AFD (plusieurs etats acceptants) ----------

def afd_vers_dot(afd, nom="AFD"):
    lignes = [f"digraph {nom} {{", "  rankdir=LR;", "  node [shape=circle];",
              "  __start [shape=point];", f"  __start -> {afd.init};"]
    for q in sorted(afd.finaux):
        lignes.append(f"  {q} [shape=doublecircle];")
    triplets = [(s, c, d) for (s, c), d in sorted(afd.delta.items())]
    for (src, dst), etiquettes in regrouper(triplets).items():
        lignes.append(f'  {src} -> {dst} [label="{",".join(etiquettes)}"];')
    lignes.append("}")
    return "\n".join(lignes) + "\n"


def ecrire_afd_dot(afd, chemin):
    with open(chemin, "w", encoding="utf-8", newline="\n") as f:
        f.write(afd_vers_dot(afd))
