# Parties 3 et 4 – Schéma de traduction et numérotation des états

Notations : `h` = attribut **hérité** (fragment déjà construit, à gauche),
`s` = attribut **synthétisé** (fragment résultat), `n` = prochain numéro
d'état libre (**hérité** en entrée), `n'` = prochain numéro libre
(**synthétisé** en sortie). Un fragment est un triplet `(init, fin, transitions)`.

## 1. Schéma de traduction complet

| Production | Actions sémantiques |
|---|---|
| R → T R' | `T.n = R.n` ; `R'.h = T.s` ; `R'.n = T.n'` ; `R.s = R'.s` ; `R.n' = R'.n'` |
| R' → '\|' T R'₁ | `T.n = R'.n` ; `(u, n₁) = union(R'.h, T.s, T.n')` ; `R'₁.h = u` ; `R'₁.n = n₁` ; `R'.s = R'₁.s` ; `R'.n' = R'₁.n'` |
| R' → ε | `R'.s = R'.h` ; `R'.n' = R'.n` |
| T → F T' | `F.n = T.n` ; `T'.h = F.s` ; `T'.n = F.n'` ; `T.s = T'.s` ; `T.n' = T'.n'` |
| T' → F T'₁ | `F.n = T'.n` ; `T'₁.h = concat(T'.h, F.s)` (aucun état créé) ; `T'₁.n = F.n'` ; `T'.s = T'₁.s` ; `T'.n' = T'₁.n'` |
| T' → ε | `T'.s = T'.h` ; `T'.n' = T'.n` |
| F → A F' | `A.n = F.n` ; `F'.h = A.s` ; `F'.n = A.n'` ; `F.s = F'.s` ; `F.n' = F'.n'` |
| F' → '*' F'₁ | `(e, n₁) = etoile(F'.h, F'.n)` ; `F'₁.h = e` ; `F'₁.n = n₁` ; `F'.s = F'₁.s` ; `F'.n' = F'₁.n'` |
| F' → '+' F'₁ | idem avec `plus` |
| F' → '?' F'₁ | idem avec `optionnel` |
| F' → ε | `F'.s = F'.h` ; `F'.n' = F'.n` |
| A → '(' R ')' | `R.n = A.n` ; `A.s = R.s` ; `A.n' = R.n'` |
| A → SYMBOLE | `(A.s, A.n') = symbole(SYMBOLE.valeur, A.n)` |
| A → '@' | `(A.s, A.n') = mot_vide(A.n)` |

Appel initial : `(frag, n) = R(0)`, puis vérification que l'entrée est épuisée.

Constructeurs (dans `src/automate.py`) — `i = n`, `f = n+1`, résultat `n+2` sauf concaténation :

| Opérateur | Transitions ajoutées |
|---|---|
| `a` | `i –a→ f` |
| `@` | `i –ε→ f` |
| `r\|s` | `i→init(r)`, `i→init(s)`, `fin(r)→f`, `fin(s)→f` (toutes ε) |
| `rs` | `fin(r) –ε→ init(s)` ; init = `init(r)`, fin = `fin(s)` ; **0 état créé** |
| `r*` | `i→init(r)`, `fin(r)→f`, `fin(r)→init(r)`, `i→f` |
| `r+` | `i→init(r)`, `fin(r)→f`, `fin(r)→init(r)` (= `r*` **sans** `i→f`) |
| `r?` | `i→init(r)`, `fin(r)→f`, `i→f` (= `r*` **sans** `fin(r)→init(r)`) |

**Construction de `+` et `?` (demandée par l'énoncé).** `r+ = r r*` mais on ne
recopie pas `r` : on utilise une seule copie de `N(r)` et la boucle
`fin(r)→init(r)` permet de la reparcourir ; il n'y a pas de court-circuit
`i→f`, donc au moins un passage dans `r`. De même `r? = r | ε` : on garde
une seule copie de `N(r)` et le court-circuit `i→f` joue le rôle de la branche ε,
sans boucle de retour, donc au plus un passage. Ces deux opérateurs
n'utilisent donc que les transitions déjà décrites pour `*`, avec 2 nouveaux
états chacun.

**Propriété 2n.** Symbole, `@`, `|`, `*`, `+`, `?` créent exactement 2 états ;
la concaténation et les parenthèses n'en créent aucun, et aucun état n'est
jamais partagé ni recopié. Avec `n` symboles et opérateurs comptés, l'automate
a donc exactement `2n` états (donc au plus `2n`). Vérifié sur 3000
expressions aléatoires (nombre d'états distincts = compteur final ≤ 2n).

## 2. Graphe de dépendances de `ab|c` ; L-attribué mais pas S-attribué

Arbre syntaxique de `ab|c` (dérivation) :

```
R
├─ T
│   ├─ F
│   │   ├─ A ── a
│   │   └─ F' ── ε
│   └─ T'
│       ├─ F
│       │   ├─ A ── b
│       │   └─ F' ── ε
│       └─ T' ── ε
└─ R'
    ├─ '|'
    ├─ T
    │   ├─ F
    │   │   ├─ A ── c
    │   │   └─ F' ── ε
    │   └─ T' ── ε
    └─ R' ── ε
```

Dépendances (flèche = « sert à calculer »), pour l'attribut fragment et le compteur `n` :

```
a.valeur ─► A_a.s ─► F'_a.h ─► F'_a.s ─► F_a.s ─► T'_1.h  (hérité : frère gauche)
                                                     │
 b.valeur ─► A_b.s ─► F'_b.h ─► F'_b.s ─► F_b.s ─────┤  concat(T'_1.h, F_b.s)
                                                     ▼
                                           T'_2.h ─► T'_2.s ─► T'_1.s ─► T_1.s ─► R'_1.h
                                                                                   │ (hérité : frère gauche)
 c.valeur ─► A_c.s ─► ... ─► T_2.s ─────────────────────────────────────────────────┤ union(R'_1.h, T_2.s)
                                                                                   ▼
                                                              R'_2.h ─► R'_2.s ─► R'_1.s ─► R.s
```

Le compteur `n` suit le même chemin, de gauche à droite : `R.n=0 → A_a (0..1) →
A_b (2..3) → A_c (4..5) → union (6..7)`, et `R.n'` est le dernier `n'`.

* **L-attribué** : chaque attribut hérité d'un symbole de la partie droite ne
  dépend que (i) des attributs hérités du père et (ii) d'attributs de frères
  **situés à sa gauche**. Ex. `R'₁.h = union(R'.h, T.s)` : `R'.h` est hérité du
  père, `T` est à gauche de `R'₁`. De même `F'.h = A.s`, `T'₁.h = concat(T'.h, F.s)`,
  `T'.n = F.n'`. Aucune dépendance ne va de droite à gauche : une seule
  traversée gauche-droite en profondeur (donc l'analyse descendante) suffit.
* **Pas S-attribué** : un schéma S-attribué n'a que des attributs synthétisés.
  Ici `h` (et `n`) sont hérités : `F'.h = A.s` copie l'attribut d'un **frère**
  dans un nœud fils, ce qui est impossible avec des attributs purement
  synthétisés (calculés de bas en haut uniquement).

## 3. Arbre syntaxique annoté de `a|bc*`

Chaque fragment est noté `(init,fin)` ; `n` = prochain état libre en entrée,
`n'` en sortie. Valeurs obtenues en exécutant l'analyseur.

```
R              n=0                      s=(8,9)   n'=10
├─ T           n=0                      s=(0,1)   n'=2
│   ├─ F       n=0                      s=(0,1)   n'=2
│   │   ├─ A   n=0  a                   s=(0,1)   n'=2
│   │   └─ F'  n=2  h=(0,1)             s=(0,1)   n'=2   (ε)
│   └─ T'      n=2  h=(0,1)             s=(0,1)   n'=2   (ε)
└─ R'          n=2  h=(0,1)             s=(8,9)   n'=10
    ├─ '|'
    ├─ T       n=2                      s=(2,7)   n'=8
    │   ├─ F   n=2                      s=(2,3)   n'=4
    │   │   ├─ A   n=2  b               s=(2,3)   n'=4
    │   │   └─ F'  n=4  h=(2,3)         s=(2,3)   n'=4   (ε)
    │   └─ T'  n=4  h=(2,3)             s=(2,7)   n'=8
    │       ├─ F   n=4                  s=(6,7)   n'=8
    │       │   ├─ A   n=4  c           s=(4,5)   n'=6
    │       │   └─ F'  n=6  h=(4,5)     s=(6,7)   n'=8
    │       │       ├─ '*'              (etoile : i=6, f=7)
    │       │       └─ F'  n=8  h=(6,7) s=(6,7)   n'=8   (ε)
    │       └─ T'  n=8  h=(2,7)  [= concat((2,3),(6,7))]  s=(2,7)  n'=8  (ε)
    └─ R'  n=8  h=(8,9)  [= union((0,1),(2,7)), i=8, f=9]  s=(8,9)  n'=10  (ε)
```

Résultat : automate d'init 8, fin 9, **10 états** (`n = 5` : a, b, c, `*`, `|` → `2n = 10`).
Transitions : `0–a→1`, `2–b→3`, `4–c→5`, `6→4`, `5→7`, `5→4`, `6→7`, `3→6`,
`8→0`, `8→2`, `1→9`, `7→9` (les 8 dernières sauf `0–a→1`, `2–b→3`, `4–c→5` sont des ε).

## 4. Associativité à gauche malgré la grammaire sans récursivité à gauche

La récursivité à gauche `R → R '|' T` donnerait naturellement `((a|b)|c)`.
Après transformation, la grammaire est récursive à **droite** (`R' → '|' T R'`),
ce qui donnerait un arbre penché à droite. Mais l'attribut hérité `h`
accumule le résultat **déjà construit à gauche** : à chaque `'|'` lu, on
calcule `union(h, T.s)` *avant* de descendre dans `R'₁`, et ce résultat devient
le `h` suivant. L'ordre des actions suit donc l'ordre de lecture, pas la
forme de l'arbre de dérivation.

Exemple `a|b|c` (états : `a`=(0,1), `b`=(2,3), `c`=(6,7)) :

1. `R'(h=a)` lit `|`, lit `b`, calcule `u₁ = union(a, b)` = `(4,5)`, appelle `R'(h=u₁)`.
2. `R'(h=u₁)` lit `|`, lit `c`, calcule `u₂ = union(u₁, c)` = `(8,9)`, appelle `R'(h=u₂)`.
3. `R'(h=u₂)` voit `$` : `R'.s = u₂`.

Le fragment final est `union(union(a,b),c)` = `((a|b)|c)`, associatif à gauche.
Même mécanisme pour la concaténation (`T'.h`) : `abc` → `concat(concat(a,b),c)`.

## 5. Opérateur demandant le plus de précautions

Le **`+`** (et, dans une moindre mesure, `?` et `*`). Écrire naïvement
`r+ = r r*` impose d'utiliser `r` **deux fois** : si l'on réemploie le même
fragment, les mêmes numéros d'état apparaissent à deux endroits différents
(l'automate fusionne deux copies de `r`, ce qui crée des chemins parasites et
casse la propriété « un seul état initial sans transition entrante »).
Il faudrait sinon recopier `r` avec de nouveaux numéros,
donc faire circuler le compteur dans une duplication. Notre construction
évite ce risque en n'utilisant **qu'une copie** de `N(r)` et en ajoutant la
boucle `fin(r) → init(r)` plus deux états frais `i` et `f`. Les nouveaux `i`
et `f` sont indispensables aussi pour `*` : boucler directement sur `init(r)`
et `fin(r)` ferait entrer une transition dans `init(r)` et sortir une
transition de `fin(r)`, ce qui, imbriqué (`(a*)*`, `((a*)*)*`), produirait
des ε-cycles ou des confusions entre états. La simulation doit de toute façon
gérer ces cycles (ε-fermeture avec ensemble de visités).

## 6. Partie 4 – Numérotation sans variable globale

Le prochain numéro libre est un **attribut** : hérité (`n`, paramètre de chaque
procédure) en entrée, synthétisé (`n'`, valeur retournée) en sortie, comme dans
la table du §1. Chaque procédure `R, R', T, T', F, F', A` reçoit `n` et rend
`(fragment, n')` ; les constructeurs (`symbole`, `union`, `etoile`, …) font de
même. Le numéro circule dans l'ordre de lecture de l'expression : aucune
variable globale ni statique ; deux appels indépendants à `traduire(texte)`
repartent chacun de 0 (ou du `n0` passé en paramètre) et donnent le même
résultat. Cela rend l'analyseur ré-entrant et testable.
