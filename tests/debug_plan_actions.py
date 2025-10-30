"""
Debug: Pourquoi Plan d'actions n'est pas détecté ?
"""
import sys
import os
import re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

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

# Normaliser
text_norm = text.replace("'", "'").replace("'", "'").replace("'", "'")

print("=== Recherche de 'Plan d'actions' ===\n")

# Chercher "Plan d'actions" dans le texte brut
for i, line in enumerate(text.split('\n'), 1):
    if 'plan' in line.lower():
        print(f"Ligne {i}: {repr(line)}")
        print(f"  Après normalisation: {repr(line.replace(chr(8217), chr(39)))}")

print("\n=== Test des patterns ===\n")

section_name = "Plan d'actions"
patterns = [
    rf'^{re.escape(section_name)}(?:\s*[:\-]|\s*$)',
    rf'^{re.escape(section_name)}\s*&',
]

for i, pattern in enumerate(patterns, 1):
    print(f"Pattern {i}: {pattern}")
    matches = list(re.finditer(pattern, text_norm, re.MULTILINE | re.IGNORECASE))
    print(f"  Matches: {len(matches)}")
    for match in matches:
        pos = match.start()
        line_num = text_norm[:pos].count('\n') + 1
        print(f"    Position {pos}, ligne {line_num}")
        print(f"    Texte: {repr(text_norm[pos:pos+30])}")
    print()

# Chercher toutes les lignes qui commencent par "Plan"
print("=== Lignes commençant par 'Plan' (regex ^Plan) ===\n")
for match in re.finditer(r'^Plan.*$', text_norm, re.MULTILINE | re.IGNORECASE):
    pos = match.start()
    line_num = text_norm[:pos].count('\n') + 1
    print(f"Ligne {line_num}: {repr(match.group())}")
