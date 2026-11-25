# Corrections à apporter au rapport (rapport.pdf)

Le PDF n'a pas de source dans le dépôt. Ce fichier donne le texte exact à
mettre à la place des passages inexacts ou manquants, puis à régénérer le PDF.

## 1. Section 6.3 – Outils d'assistance IA (remplacer entièrement)

> **Outil :** Claude Code (assistant IA d'Anthropic), utilisé par l'Étudiant 1
> (mise en place du dépôt) et par l'Étudiant 2 (partie 3 et relecture,
> tests). Le détail figure dans la section 9 du rapport.
>
> **Écrit par l'assistant :** `src/automate.py` (construction de Thompson),
> les actions sémantiques de `src/parser.py` (dont la circulation du compteur
> d'états, partie 4) et `docs/partie3_4_schema.md`, dont le contenu a été
> repris dans les sections 2 et 3 de ce rapport.
>
> **Expliqué par l'assistant :** attributs hérités et synthétisés, schéma
> L-attribué, associativité malgré l'élimination de la récursivité à gauche.
>
> **Vérifié / corrigé grâce à l'assistant :** relecture du dépôt par rapport
> à l'énoncé et tests jetables. Trois défauts trouvés et corrigés (simulation
> ne gardant qu'une cible par transition, parser sans actions sémantiques,
> bloc dupliqué dans `main.py`).
>
> **Non réalisé par l'assistant :** lexer final, partie 1, export Graphviz,
> simulation, jeu de tests du dépôt. Les Étudiants 3 et 4 complètent leur
> propre usage dans la section 9 du rapport.
>
> **Phrase à supprimer :** « Tout le code Python d'analyse et de construction
> d'automate a été entièrement réécrit à la main. »

## 2. Section 3 – Partie 4 (corriger l'attribution)

La partie 4 (numérotation des états et test de la propriété 2n) est attribuée
à Sahar Abidi (Étudiant 4). Ghassen Khirouni (Étudiant 2) est en charge de la
construction de Thompson et du schéma de traduction (partie 3).

> Sahar a pris en charge la numérotation des états et le test automatique de
> la propriété « au plus 2n états » dans `tests/run_tests.py`.

Et, dans la fiche de répartition, indiquer les parties 4 et 6 pour l'Étudiant 4,
et la partie 3 pour l'Étudiant 2.

## 3. Section 2.4 – ajouter la construction de `r?`

> `r? = r | ε` sans dupliquer `r` : une seule copie de `N(r)`, deux états
> frais `i` et `f`, les transitions `i ─ε→ init(r)`, `fin(r) ─ε→ f` et le
> court-circuit `i ─ε→ f` (qui joue le rôle de la branche ε). Il n'y a pas
> de boucle `fin(r) ─ε→ init(r)` : au plus une occurrence. C'est `r*` privée
> de sa boucle de retour ; `r+` est `r*` privée de son court-circuit.

## 4. Section « Difficultés rencontrées et choix de conception » (manquante)

À insérer (à compléter par chacun avec ce qu'il a vraiment vécu) :

> - **Fusion du parser.** Une réécriture du lexer a aussi remplacé le parser
>   par une version qui ne faisait que valider : les actions sémantiques
>   avaient disparu et `main.py` plantait. Leçon : exécuter `main.py` et
>   `tests/run_tests.py` sur `main` avant chaque fusion.
> - **Simulation non déterministe.** Dans `table_transitions`, l'ajout de la
>   cible était à l'intérieur du `if` : une seule cible était gardée par
>   (état, étiquette), donc `a|b` rejetait `b`. Trouvé avec les neuf
>   expressions obligatoires.
> - **Messages d'erreur.** Pour afficher tous les jetons attendus, le parser
>   mémorise les types testés depuis le dernier jeton consommé ; les
>   ε-productions n'avaient pas besoin de FOLLOW explicite.
> - **Profondeur de récursion.** Une procédure par non-terminal consomme un
>   cadre par symbole ; la limite de récursion de Python est relevée dans
>   `Parser.analyse`.
> - **Choix : `+` et `?`.** Une seule copie de `N(r)` (voir 2.4) pour ne
>   jamais réutiliser un état à deux endroits.
> - **Choix : concaténation.** Elle ne crée aucun état ; elle ajoute une
>   ε-transition `fin(r) → init(s)`, ce qui garde exactement 2n états.

## 5. Petites corrections

- Titre de la section 5 : « JUEGO DE TESTS » → « JEU DE TESTS ».
- Section 5.2 (test de mutation) : joindre le script ou les 13 mutants au
  dépôt, ou retirer la section ; en l'état elle n'est pas vérifiable.
- Les sections 4 et 5 mentionnent des figures (automates 1 à 3) : les
  fichiers `automates/*.dot` correspondants sont fournis ; vérifier que les
  images insérées viennent de `dot -Tpng` sur ces fichiers.
