"""Interface en ligne de commande (Partie 5).

    python src/main.py --dot automate.dot "(a|b)*abb" abb aabb 

Affiche une ligne par mot (`abb : OUI`, `ab : NON`). Code de retour non nul
si l'expression est invalide.
"""
import sys

from lexer import ErreurLexicale
from parser import Parser, ErreurSyntaxique

from export_dot import ecrire_dot
from simulation import reconnaitre
from afd import determiniser, minimiser, equivalents, ecrire_afd_dot
from recuperation import ParserRecuperation, ErreursMultiples


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    args = list(argv)

    # 1. Option --dot, en premier, car elle peut apparaitre n'importe ou
    dot_file = None
    if "--dot" in args:
        dot_index = args.index("--dot")
        if dot_index + 1 >= len(args):
            # Rien ne suit --dot
            print("Erreur : le fichier .dot n'est pas spécifié après --dot.", file=sys.stderr)
            return 2
        dot_file = args[dot_index + 1]
        del args[dot_index:dot_index + 2]


    # 1 bis. Options des extensions
    recup = "--recup" in args
    if recup:
        args.remove("--recup")
    fichiers_afd = {}
    for option in ("--afd", "--min"):
        if option in args:
            i = args.index(option)
            if i + 1 >= len(args):
                print(f"Erreur : fichier manquant après {option}.", file=sys.stderr)
                return 2
            fichiers_afd[option] = args[i + 1]
            del args[i:i + 2]

    if args and args[0] == "--equiv":
        if len(args) != 3:
            print('Usage : python src/main.py --equiv "r1" "r2"', file=sys.stderr)
            return 2
        try:
            f1 = Parser(args[1]).analyse()
            f2 = Parser(args[2]).analyse()
        except (ErreurLexicale, ErreurSyntaxique) as erreur:
            print(erreur, file=sys.stderr)
            return 1
        egales, mot = equivalents(f1, f2)
        if egales:
            print("Équivalentes")
        else:
            print(f"Non équivalentes (contre-exemple : {mot or '@'})")
        return 0

    # 2. L'expression, puis les mots (le mot vide "" est garde)
    if len(args) < 1:
        print("Usage : python src/main.py <expression> [mot1 mot2 ...] [--dot fichier.dot]",file=sys.stderr)
        return 2
    expression = args[0]
    mots = args[1:]

    # 3. Analyse lexicale et syntaxique
    try:
        classe = ParserRecuperation if recup else Parser
        frag = classe(expression).analyse()
    except (ErreurLexicale, ErreurSyntaxique, ErreursMultiples) as erreur:
        print(erreur, file=sys.stderr)
        return 1

    if not mots:
        print("Expression valide")   # Partie 2 : pas de mot a tester

    # 4. Export Graphviz
    if dot_file is not None:
        ecrire_dot(frag, dot_file)

    if "--afd" in fichiers_afd:
        ecrire_afd_dot(determiniser(frag), fichiers_afd["--afd"])
    if "--min" in fichiers_afd:
        ecrire_afd_dot(minimiser(determiniser(frag)), fichiers_afd["--min"])

    # 5. Simulation
    for mot in mots:
        print(f"{mot} : {'OUI' if reconnaitre(frag, mot) else 'NON'}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
