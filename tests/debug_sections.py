"""
Debug: chercher "Plan d'actions" dans le texte
"""
import sys

# Lire depuis stdin ou fichier
if len(sys.argv) > 1:
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        text = f.read()
else:
    text = """Bloc 1
Prosit aller 4 – Etude de fonction Green IT
17/10/2025

Mots clés & Mots inconnus
•	Cryptographie
•	ASCII
•	Algorithme d'Euclide
•	Décryptage
•	Démonstration Scientifique
•	Message codé
Contexte
Alexander découvre un parchemin chiffré dans son château et demande aux étudiants de l'aider à le déchiffrer.
Problématique
-	Comment déchiffrer un message codé en Python ?
Contraintes
•	Python
•	Méthode de cryptage inconnu
Livrables
•	Code Python
•	CER
•	Méthode Scientifique

Généralisation
-	Cryptographie
-	Hachage
-	Communication réseau
-	Algorithme de chiffrement
Hypothèses
•	Un des messages est chiffré en code CESAR
•	L'algorithme d'Euclide ne servira à rien
•	L'algorithme de décryptage est le même que celui de cryptage
•	Il nous manque une information pour décrypter le message
Plan d'actions
1.	Définir les mots clés
2.	Études des ressources
3.	Se renseigner sur le cryptage
4.	Trouver le cryptage réalisé
5.	Décrypter le message
6.	Script python pour crypter et décrypter"""

print("=== Recherche de 'Plan d'actions' ===")
print(f"Longueur du texte: {len(text)} caracteres")
print(f"Nombre de lignes: {len(text.splitlines())}")
print()

# Rechercher "Plan"
lines_with_plan = []
for i, line in enumerate(text.splitlines(), 1):
    if 'plan' in line.lower():
        print(f"Ligne {i}: {repr(line)}")
        lines_with_plan.append((i, line))

print()
if lines_with_plan:
    print(f"Trouvé {len(lines_with_plan)} ligne(s) contenant 'plan'")
    for i, line in lines_with_plan:
        print(f"\n  Ligne {i}:")
        print(f"    Texte: {line}")
        print(f"    Stripped: {line.strip()}")
        print(f"    Repr: {repr(line.strip())}")

        # Analyser chaque caractère
        for j, char in enumerate(line.strip()):
            if char in ["'", "'", "'", "'"]:
                print(f"    Apostrophe trouvée à position {j}: U+{ord(char):04X}")
else:
    print("AUCUNE ligne contenant 'plan' trouvée!")
    print("\nVoici toutes les lignes du texte:")
    for i, line in enumerate(text.splitlines(), 1):
        print(f"  {i:2d}: {repr(line)}")
