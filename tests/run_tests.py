#!/usr/bin/env python3
"""
Lanceur de tests automatisé (Partie 6) - Étudiant 4.

Ce script :
 1. Lit et exécute les tests valides définis dans `tests/tests.txt`.
 2. Contrôle automatiquement la propriété « au plus 2n états ».
 3. Vérifie la reconnaissance des mots (acceptés / rejetés).
 4. Exécute les tests d'erreurs syntaxiques et lexicales avec vérification de la position.
 5. Affiche un bilan clair et structuré dans le terminal.
"""

from pathlib import Path
import sys

# Ajout du dossier src au PYTHONPATH
RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "src"))

try:
  from lexer import ErreurLexicale
  from parser import Parser, ErreurSyntaxique
  from automate import etats
  from simulation import reconnaitre
except ImportError as err:
  print(f"\033[31mErreur d'importation des modules src/ : {err}\033[0m")
  sys.exit(1)


# Style ANSI pour un affichage propre dans le terminal
class Style:
  VERT = "\033[92m"
  ROUGE = "\033[91m"
  JAUNE = "\033[93m"
  BLEU = "\033[94m"
  CYAN = "\033[96m"
  GRAS = "\033[1m"
  RESET = "\033[0m"


def compter_n(expression: str) -> int:
  """
    Calcule 'n' selon l'énoncé du TP :
    Chaque symbole alphanumérique, '@', '|', '*', '+', '?' compte pour 1.
    Les parenthèses '(' et ')' et la concaténation ne comptent pas.
    """
  operateurs_et_symboles = set(
      "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@|*+?"
  )
  return sum(1 for char in expression if char in operateurs_et_symboles)


def obtenir_fragment(parser_obj, expression: str):
  """Extrait le fragment d'automate retourné par l'analyseur."""
  return parser_obj.analyse()


def charger_fichier_tests(chemin: Path):
  """Lit tests.txt et sépare les tests valides et les tests d'erreurs."""
  valides = []
  erreurs = []

  if not chemin.exists():
    print(f"{Style.ROUGE}Fichier introuvable : {chemin}{Style.RESET}")
    sys.exit(1)

  with open(chemin, "r", encoding="utf-8") as f:
    for num_ligne, ligne in enumerate(f, start=1):
      ligne = ligne.strip()
      if not ligne or ligne.startswith("#"):
        continue

      if ligne.startswith("ERR:"):
        parties = [p.strip() for p in ligne[4:].split(";")]
        if len(parties) == 3:
          expr, pos_str, desc = parties
          erreurs.append((expr, int(pos_str), desc, num_ligne))
      else:
        parties = [p.strip() for p in ligne.split(";")]
        if len(parties) == 3:
          expr, acc_str, rej_str = parties
          acc = (
              []
              if not acc_str
              else ["" if m == "@" else m for m in acc_str.split()]
          )
          rej = (
              []
              if not rej_str
              else ["" if m == "@" else m for m in rej_str.split()]
          )
          valides.append((expr, acc, rej, num_ligne))

  return valides, erreurs


def exécuter_tests():
  fichier_tests = Path(__file__).resolve().parent / "tests.txt"
  tests_valides, tests_erreurs = charger_fichier_tests(fichier_tests)

  total_pass = 0
  total_fail = 0

  print(
      f"\n{Style.GRAS}{Style.CYAN}================================================================================{Style.RESET}"
  )
  print(
      f"{Style.GRAS}{Style.CYAN}               VALIDATION AUTOMATISÉE DU PROJET"
      f" COMPILATION                 {Style.RESET}"
  )
  print(
      f"{Style.GRAS}{Style.CYAN}================================================================================{Style.RESET}\n"
  )

  # --------------------------------------------------------------------------
  # 1. Expressions ACCEPTÉES par le compilateur (validité, <= 2n états, mots)
  # --------------------------------------------------------------------------
  print(
      f"{Style.GRAS}{Style.BLEU}[1/2] EXPRESSIONS ACCEPTÉES (VALIDES) &"
      f" PROPRIÉTÉ <= 2n ÉTATS{Style.RESET}"
  )
  print("-" * 80)
  print(
      f"{'Expression':<18} | {'Décision':<12} | {'Etats':<6} | {'Max (2n)':<8} |"
      f" {'2n OK?':<7} | {'Mots (Statut)':<15}"
  )
  print("-" * 80)

  for expr, acceptes, rejetes, Ligne in tests_valides:
    try:
      p = Parser(expr)
      frag = obtenir_fragment(p, expr)

      n = compter_n(expr)
      nb_etats = len(etats(frag))
      limite_2n = 2 * n
      ok_2n = nb_etats <= limite_2n

      # Test des mots
      echecs_mots = []
      for m in acceptes:
        nom_m = "@" if m == "" else m
        if not reconnaitre(frag, m):
          echecs_mots.append(f"+{nom_m}")
      for m in rejetes:
        nom_m = "@" if m == "" else m
        if reconnaitre(frag, m):
          echecs_mots.append(f"-{nom_m}")

      ok_reco = len(echecs_mots) == 0

      str_decision = f"{Style.VERT}ACCEPTÉE{Style.RESET}"
      str_2n = (
          f"{Style.VERT}OUI{Style.RESET}"
          if ok_2n
          else f"{Style.ROUGE}NON{Style.RESET}"
      )
      str_reco = (
          f"{Style.VERT}PASS{Style.RESET}"
          if ok_reco
          else f"{Style.ROUGE}FAIL ({','.join(echecs_mots)}){Style.RESET}"
      )

      if ok_2n and ok_reco:
        total_pass += 1
      else:
        total_fail += 1

      print(
          f"{expr:<18} | {str_decision:<21} | {nb_etats:<6} | {limite_2n:<8} |"
          f" {str_2n:<16} | {str_reco}"
      )

    except Exception as e:
      total_fail += 1
      str_decision = f"{Style.ROUGE}REJETÉE{Style.RESET}"
      print(
          f"{expr:<18} | {str_decision:<21} | {Style.ROUGE}ERREUR : {e}{Style.RESET}"
      )

  # --------------------------------------------------------------------------
  # 2. Expressions REJETÉES par le compilateur (erreurs lexicales & syntaxiques)
  # --------------------------------------------------------------------------
  print(
      f"\n{Style.GRAS}{Style.BLEU}[2/2] EXPRESSIONS REJETÉES (INVALIDES) &"
      f" DÉTECTION D'ERREURS{Style.RESET}"
  )
  print("-" * 80)
  print(
      f"{'Expression':<14} | {'Décision':<12} | {'Pos attendue':<13} |"
      f" {'Pos obtenue':<12} | {'Statut test':<12}"
  )
  print("-" * 80)

  for expr, pos_attendue, desc, ligne in tests_erreurs:
    try:
      p = Parser(expr)
      obtenir_fragment(p, expr)
      # Si aucune erreur n'a été levée, le compilateur l'a acceptée à tort
      total_fail += 1
      str_decision = f"{Style.VERT}ACCEPTÉE{Style.RESET}"
      print(
          f"{expr:<14} | {str_decision:<21} | {pos_attendue:<13} |"
          f" {'Aucune':<12} | {Style.ROUGE}FAIL (non rejetée){Style.RESET}"
      )
    except (ErreurSyntaxique, ErreurLexicale) as err:
      pos_obtenue = getattr(err, "position", None)
      str_decision = f"{Style.ROUGE}REJETÉE{Style.RESET}"
      if pos_obtenue == pos_attendue:
        total_pass += 1
        str_status = f"{Style.VERT}PASS{Style.RESET}"
      else:
        total_fail += 1
        str_status = f"{Style.ROUGE}FAIL (pos){Style.RESET}"
      print(
          f"{expr:<14} | {str_decision:<21} | {pos_attendue:<13} |"
          f" {str(pos_obtenue):<12} | {str_status}"
      )
    except Exception as e:
      total_fail += 1
      str_decision = f"{Style.ROUGE}REJETÉE{Style.RESET}"
      print(
          f"{expr:<14} | {str_decision:<21} | {pos_attendue:<13} |"
          f" {'Exception':<12} | {Style.ROUGE}FAIL ({e}){Style.RESET}"
      )

  # --------------------------------------------------------------------------
  # Bilan Final
  # --------------------------------------------------------------------------
  total_tests = total_pass + total_fail
  print(
      f"\n{Style.GRAS}{Style.CYAN}================================================================================{Style.RESET}"
  )
  print(
      f"{Style.GRAS}BILAN DES TESTS : {total_pass}/{total_tests} réussis"
      f" ({len(tests_valides)} acceptées, {len(tests_erreurs)} rejetées){Style.RESET}"
  )
  if total_fail == 0:
    print(
        f"{Style.GRAS}{Style.VERT}TOUS LES TESTS ONT RÉUSSI AVEC SUCCÈS !"
        f" 🎉{Style.RESET}"
    )
  else:
    print(
        f"{Style.GRAS}{Style.ROUGE}CERTAINS TESTS ONT ÉCHOUÉ ({total_fail}"
        f" ÉCHEC(S)).{Style.RESET}"
    )
  print(
      f"{Style.GRAS}{Style.CYAN}================================================================================{Style.RESET}\n"
  )

  sys.exit(0 if total_fail == 0 else 1)


if __name__ == "__main__":
  exécuter_tests()