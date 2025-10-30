"""
Test avec le scénario exact de l'utilisateur
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.cr_parser import CRParser

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

parser = CRParser()
data = parser.parse(text)

print("=== Données extraites ===\n")
print(f"Hypothèses ({len(data['hypotheses'])}):")
for i, h in enumerate(data['hypotheses'], 1):
    print(f"  {i}. {h}")

print(f"\nPlan d'actions ({len(data['plan_actions'])}):")
for i, p in enumerate(data['plan_actions'], 1):
    print(f"  {i}. {p}")

print("\n=== Affichage complet ===\n")
formatted = parser.format_for_display(data)
print(formatted)
