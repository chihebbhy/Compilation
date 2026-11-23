"""Interface en ligne de commande (Partie 5).

    python src/main.py "(a|b)*abb" abb aabb ab [--dot fichier.dot]

Affiche une ligne par mot (`abb : OUI`, `ab : NON`). Code de retour non nul
si l'expression est invalide.
"""
import sys

from lexer import ErreurLexicale
from parser import Parser, ErreurSyntaxique

from export_dot import ecrire_dot
from simulation import reconnaitre


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    args = list(argv)

    # 1. Option --dot, en premier, car elle peut apparaitre n'importe ou
    dot_file = None
    if "--dot" in args:
        dot_index = args.index("--dot")
        if dot_index + 1 >= len(args):
            print("Erreur : le fichier .dot n'est pas spécifié après --dot.", file=sys.stderr)
            return 2
        dot_file = args[dot_index + 1]
        del args[dot_index:dot_index + 2]


    # 2. L'expression, puis les mots (le mot vide "" est garde)
    if len(args) < 1:
        print("Usage : python src/main.py <expression> [mot1 mot2 ...] [--dot fichier.dot]",file=sys.stderr)
        return 2
    expression = args[0]
    mots = args[1:]

    # 3. Analyse lexicale et syntaxique
    try:
        frag = Parser(expression).analyse()
    except (ErreurLexicale, ErreurSyntaxique) as erreur:
        print(erreur, file=sys.stderr)
        return 1

    if not mots:
        print("Expression valide")   # Partie 2 : pas de mot a tester

    # 4. Export Graphviz
    if dot_file is not None:
        ecrire_dot(frag, dot_file)

    # 5. Simulation
    for mot in mots:
        print(f"{mot} : {'OUI' if reconnaitre(frag, mot) else 'NON'}")

    return 0


if __name__ == "__main__":
    sys.exit(main())