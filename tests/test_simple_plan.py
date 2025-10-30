"""
Test simple : chercher "Plan" sans apostrophe
"""
import re

text = """Hypothèses
•	L'optimisation de la mémoire va influencer positivement sur le travail du CPU
•	Les patterns prédisent-ils vraiment les tendances de la consommation ?
•	L'optimisation des ressources va-t-elle réduire la température ?
Plan d'actions
•	Se cultiver sur le système informatique
•	Analyser les données
•	Analyser les patterns
•	Développer le programme
•	Proposer des recommandations
•	Réaliser le CER"""

print("=== Test 1: Chercher 'Plan' ===")
for match in re.finditer(r'^Plan', text, re.MULTILINE | re.IGNORECASE):
    line_num = text[:match.start()].count('\n') + 1
    print(f"Trouvé à la ligne {line_num}: {repr(text[match.start():match.end()+20])}")

print("\n=== Test 2: Chercher 'Plan' + tout jusqu'à la fin de ligne ===")
for match in re.finditer(r'^Plan.*$', text, re.MULTILINE | re.IGNORECASE):
    line_num = text[:match.start()].count('\n') + 1
    print(f"Trouvé à la ligne {line_num}: {repr(match.group())}")

print("\n=== Test 3: Avec différentes apostrophes ===")
variants = ["Plan d'actions", "Plan d'actions", "Plan d'actions", "Plan d actions"]
for variant in variants:
    if variant in text:
        print(f"✓ Trouvé: {repr(variant)}")
    else:
        print(f"✗ Pas trouvé: {repr(variant)}")

print("\n=== Test 4: Analyser caractère par caractère ===")
for match in re.finditer(r'^Plan.*$', text, re.MULTILINE):
    line = match.group()
    print(f"Ligne trouvée: {repr(line)}")
    print("Caractères:")
    for i, char in enumerate(line):
        print(f"  [{i}] '{char}' = U+{ord(char):04X} ({ord(char)})")
