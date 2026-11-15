# Partie 1 – Grammaire LL(1) : tableaux à remplir

Grammaire (productions numérotées) :

| N°  | Production        |
|-----|-------------------|
| 1   | R → T R'          |
| 2   | R' → '\|' T R'    |
| 3   | R' → ε            |
| 4   | T → F T'          |
| 5   | T' → F T'         |
| 6   | T' → ε            |
| 7   | F → A F'          |
| 8   | F' → '*' F'       |
| 9   | F' → '+' F'       |
| 10  | F' → '?' F'       |
| 11  | F' → ε            |
| 12  | A → '(' R ')'     |
| 13  | A → SYMBOLE       |
| 14  | A → '@'           |

Terminaux : `|`  `*`  `+`  `?`  `(`  `)`  `SYMBOLE`  `@`  et `$` (fin de l'expression).

## 1. FIRST et FOLLOW des non-terminaux

| Non-terminal | FIRST               | FOLLOW                                |
|--------------|---------------------|---------------------------------------|
| R            | { (, @, SYMBOLE }   | { $, ) }                              |
| R'           | { \|, ε }           | { $, ) }                              |
| T            | { (, @, SYMBOLE }   | { $, ), \| }                          |
| T'           | { (, @, SYMBOLE, ε }| { $, ), \| }                         |
| F            | { (, @, SYMBOLE }   | { (, @, SYMBOLE, $, ), \| }           |
| F'           | { *, +, ?, ε }      | { (, @, SYMBOLE, $, ), \| }           |
| A            | { (, @, SYMBOLE }   | { *, +, ?, (, @, SYMBOLE, $, ), \| }  |

## 2. FIRST de chaque production

| N°  | Production        | FIRST (partie droite) |
|-----|-------------------|-----------------------|
| 1   | R → T R'          | { (, @, SYMBOLE }     |
| 2   | R' → '\|' T R'    | { \| }                |
| 3   | R' → ε            | { ε }                 |
| 4   | T → F T'          | { (, @, SYMBOLE }     |
| 5   | T' → F T'         | { (, @, SYMBOLE }     |
| 6   | T' → ε            | { ε }                 |
| 7   | F → A F'          | { (, @, SYMBOLE }     |
| 8   | F' → '*' F'       | { * }                 |
| 9   | F' → '+' F'       | { + }                 |
| 10  | F' → '?' F'       | { ? }                 |
| 11  | F' → ε            | { ε }                 |
| 12  | A → '(' R ')'     | { ( }                 |
| 13  | A → SYMBOLE       | { SYMBOLE }           |
| 14  | A → '@'           | { @ }                 |

## 3. Table d'analyse prédictive LL(1)

Chaque case contient le numéro de la production à appliquer ; une case vide
est une erreur.

|        | `\|` | `*` | `+` | `?` | `(` | `)` | SYMBOLE | `@` | `$` |
|--------|:----:|:---:|:---:|:---:|:---:|:---:|:-------:|:---:|:---:|
| **R**  |      |     |     |     |  1  |     |    1    |  1  |     |
| **R'** |  2   |     |     |     |     |  3  |         |     |  3  |
| **T**  |      |     |     |     |  4  |     |    4    |  4  |     |
| **T'** |  6   |     |     |     |  5  |  6  |    5    |  5  |  6  |
| **F**  |      |     |     |     |  7  |     |    7    |  7  |     |
| **F'** |  11  |  8  |  9  | 10  | 11  | 11  |   11    | 11  | 11  |
| **A**  |      |     |     |     | 12  |     |   13    | 14  |     |

Conclusion (conflits ? grammaire LL(1) ?) :

Cette grammaire est **LL(1)** puisqu'elle ne contient aucun conflit.

pour eliminer la récursivité a gauche immediate on utilise

A → Aα | β
⇒  A → βA' 
    A' → αA' | ε

on peut faire l'inverse pour avoir notre grammaire originale.


R → T | R '|' T  
T → F | T F  
F → A | F '*' | F '+' | F '?'   
A → '(' R ')' | SYMBOLE | '@'  
Est la grammaire avant de supprimer la récursivité a gauche.


Dans T’ → F T’ | ε, la concaténation est implicite : il n’y a aucun opérateur entre r et s dans rs. Après avoir lu un F, rien dans l’entrée ne dit explicitement « une concaténation commence ». L’analyseur doit donc le deviner à partir du jeton courant (le lookahead).

Pour choisir entre les deux alternatives de T’ :

T’ → F T’ doit être choisie quand le jeton courant peut commencer un F, c’est-à-dire quand il appartient à FIRST(F) = { (, @, SYMBOLE }.
T’ → ε doit être choisie quand le jeton courant peut suivre T, c’est-à-dire quand il appartient à FOLLOW(T’) = FOLLOW(T) = { |, ), $ }.

Les deux ensembles sont disjoints, donc le choix est toujours déterministe avec un seul jeton de lookahead. C’est exactement la condition LL(1) pour une production avec ε.

Si on ne testait pas FIRST(F), on ne saurait pas quand continuer la concaténation. Par exemple, dans `ab|c`, après avoir lu `a`, T’ voit `b` ∈ FIRST(F) : il applique T’ → F T’ et lit `b`. Il voit ensuite `|` ∈ FOLLOW(T’) : il applique T’ → ε et rend la main à R’, qui traite l’union.



## 4. Détection des erreurs

### Entrée `a)`

| Pile                   | Entrée  | Action                                   |
|------------------------|---------|------------------------------------------|
| `$ R`                  | `a ) $` | M[R, SYMBOLE] = 1 : R → T R'             |
| `$ R' T`               | `a ) $` | M[T, SYMBOLE] = 4 : T → F T'             |
| `$ R' T' F`            | `a ) $` | M[F, SYMBOLE] = 7 : F → A F'             |
| `$ R' T' F' A`         | `a ) $` | M[A, SYMBOLE] = 13 : A → SYMBOLE         |
| `$ R' T' F' SYMBOLE`   | `a ) $` | on reconnaît `a`                         |
| `$ R' T' F'`           | `) $`   | M[F', )] = 11 : F' → ε                   |
| `$ R' T'`              | `) $`   | M[T', )] = 6 : T' → ε                    |
| `$ R'`                 | `) $`   | M[R', )] = 3 : R' → ε                    |
| `$`                    | `) $`   | **erreur**                               |

Les trois ε-productions sont légitimes, car `)` ∈ FOLLOW(F') = FOLLOW(T') = FOLLOW(R').
Toute la pile des non-terminaux est vidée, mais l'entrée n'est pas finie : il reste `)`
alors que seul `$` est attendu. L'erreur est donc détectée au fond de la pile (symbole `$`
contre `)`), c'est-à-dire par la vérification de fin d'entrée, et non dans une case vide
de la table.


Cette erreur est détectée a la fin parce que `)` appartient à FOLLOW(R) : il serait
valide à l'intérieur d'une parenthèse, mais aucune parenthèse ouvrante n'est en attente ici.


### Entrée `a||b`


| Pile                   | Entrée        | Action                                   |
|------------------------|---------------|------------------------------------------|
| `$ R`                  | `a \| \| b $` | M[R, SYMBOLE] = 1 : R → T R'             |
| `$ R' T`               | `a \| \| b $` | M[T, SYMBOLE] = 4 : T → F T'             |
| `$ R' T' F`            | `a \| \| b $` | M[F, SYMBOLE] = 7 : F → A F'             |
| `$ R' T' F' A`         | `a \| \| b $` | M[A, SYMBOLE] = 13 : A → SYMBOLE         |
| `$ R' T' F' SYMBOLE`   | `a \| \| b $` | on reconnaît `a`                         |
| `$ R' T' F'`           | `\| \| b $`   | M[F', \|] = 11 : F' → ε                  |
| `$ R' T'`              | `\| \| b $`   | M[T', \|] = 6 : T' → ε                   |
| `$ R'`                 | `\| \| b $`   | M[R', \|] = 2 : R' → \| T R'             |
| `$ R' T \|`            | `\| \| b $`   | on reconnaît le premier `\|`             |
| `$ R' T`               | `\| b $`      | M[T, \|] = vide : **erreur**             |

Après `a`, les deux ε-productions F' → ε et T' → ε sont légitimes, car `|` ∈ FOLLOW(F') =
FOLLOW(T'). Puis R' voit `|` et applique R' → | T R' (règle 2) : un opérande T est
maintenant obligatoire après ce premier `|`. Le jeton courant est le second `|`. Or
`|` ∉ FIRST(T) = { (, @, SYMBOLE } et T n'est pas annulable, donc la case M[T, |] est vide.
L'erreur est détectée à cet endroit, sur le second `|` (position 2), avant même de lire `b`.
