"""
Test: est-ce que 'Plan' seul est trouvé ?
"""
import sys
import os
import re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

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

# Normaliser
text = text.replace("'", "'").replace("'", "'").replace("'", "'")

section_name = 'Plan'
patterns = [
    rf'^{re.escape(section_name)}(?:\s*[:\-]|\s*$)',
    rf'^{re.escape(section_name)}\s*&',
]

print(f"=== Recherche de '{section_name}' ===\n")

for i, pattern in enumerate(patterns, 1):
    print(f"Pattern {i}: {pattern}")
    matches = list(re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE))
    print(f"  Resultat: {len(matches)} match(es)")
    for match in matches:
        pos = match.start()
        line_num = text[:pos].count('\n') + 1
        print(f"    Ligne {line_num}, position {pos}")
        print(f"    Contexte: {repr(text[pos:pos+30])}")

print("\n=== Test parser complet ===")
from src.cr_parser import CRParser
parser = CRParser()
data = parser.parse(text)

print(f"Hypotheses: {len(data['hypotheses'])}")
print(f"Plan d'actions: {len(data['plan_actions'])}")
