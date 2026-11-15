"""Interface en ligne de commande (Partie 5).

    python src/main.py "(a|b)*abb" abb aabb ab [--dot fichier.dot]

Affiche une ligne par mot (`abb : OUI`, `ab : NON`). Code de retour non nul
si l'expression est invalide.
"""
import sys

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = list(argv)
    dot_file = None
    if "--dot" in args:
        dot_index = args.index("--dot")
        if dot_index + 1 < len(args):
            dot_file = args[dot_index + 1]
            del args[dot_index:dot_index + 2]
        else:
            print("Erreur : le fichier .dot n'est pas spécifié après --dot.", file=sys.stderr)
            sys.exit(2)
    
