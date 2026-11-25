TP Techniques de compilation - Du texte d'une expression reguliere a l'automate
================================================================================

Langage : Python 3.12 ou plus recent (bibliotheque standard uniquement)
Tests executes avec Python 3.14.2. Aucune compilation n'est necessaire.
Outil externe : Graphviz (commande dot) pour la visualisation

Execution
---------
    python src/main.py "(a|b)*abb" abb aabb ab
    python src/main.py "(a|b)*abb" abb --dot automates/exemple.dot
    dot -Tpng automates/exemple.dot -o automates/exemple.png

Extensions
----------
    python src/main.py "(a|b)*abb" --afd automates/afd.dot
    python src/main.py "(a|b)*abb" --min automates/afd_min.dot
    python src/main.py --equiv "(a|b)*" "(a*b*)*"
    python src/main.py "a||b)(|c" --recup

Un mot vide est passe avec "". En cas d'expression invalide, le message
d'erreur est affiche et le code de retour est non nul.

Tests
-----
    python tests/run_tests.py
    python tests/test_bonus.py

Structure
---------
    EQUIPE.txt          membres de l'equipe
    rapport.pdf         rapport d'equipe (page de garde + 5 pages)
    UTILISATION_IA.txt  declaration d'utilisation des assistants IA
    docs/               reponses theoriques (parties 1, 3 et 4) et source du rapport
    src/lexer.py        analyse lexicale (Partie 2)
    src/parser.py       analyseur predictif + schema de traduction (Parties 2, 3, 4)
    src/automate.py     fragments d'automate, construction de Thompson (Parties 3, 4)
    src/export_dot.py   export Graphviz (Partie 5)
    src/simulation.py   epsilon-fermeture et reconnaissance (Partie 5)
    src/main.py         interface en ligne de commande (Partie 5)
    src/afd.py          determinisation, minimisation, equivalence (extensions)
    src/recuperation.py recuperation d'erreur en mode panique (extension)
    tests/test_bonus.py tests des extensions
    tests/tests.txt     jeu de tests (Partie 6)
    tests/run_tests.py  lanceur de tests (Partie 6)
    automates/          fichiers .dot generes
