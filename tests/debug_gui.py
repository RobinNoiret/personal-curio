"""
Debug: simuler ce que fait l'interface GUI
"""
from src.cr_parser import CRParser

# Votre CR exact
cr_text = """Bloc 1
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

print("=== Simulation GUI ===")
parser = CRParser()

print("\n1. Parsing du CR...")
parsed_data = parser.parse(cr_text)

print(f"\n2. plan_actions extrait: {parsed_data['plan_actions']}")
print(f"   Nombre: {len(parsed_data['plan_actions'])}")

print("\n3. Formatage pour affichage...")
formatted_result = parser.format_for_display(parsed_data)

print("\n4. Resultat qui serait affiche dans la GUI:")
print("=" * 60)
print(formatted_result)
print("=" * 60)

print("\n5. Le texte contient 'Plan d'actions':", "Plan d'actions" in formatted_result)
print(f"   Nombre de lignes: {len(formatted_result.split(chr(10)))}")

# Afficher les dernières lignes
lines = formatted_result.split('\n')
print(f"\n6. Les 10 dernieres lignes:")
for line in lines[-10:]:
    print(f"   > {line}")
