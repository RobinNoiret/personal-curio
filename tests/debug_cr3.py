"""
Debug CR3
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.cr_parser import CRParser
import re

text = """Bloc 3
Prosit 3 – Boucles statistiques SI
15.10.2025

Mots clés & Mots inconnus
•	Statistiques SI
•	CPU
•	Optimiser
•	Métrique
•	Distribution
•	Système d'exploitation
•	Pattern
•	Seuil de vigilance
•	Charges de travail
•	Coûts opérationnels
•	Gestion de la mémoire
Contexte
Emma, stagiaire Optimal doit faire des analyses de composants d'un SI et mettre en place une stratégie d'optimisation de travail de composants du système d'exploitation.
Problématique
Comment optimiser les coûts d'une infrastructure par l'analyse de ses données ?
Comment optimiser les performances ?
Contraintes
•	Données : fichiers CSV
•	Python
Livrables
•	CER
•	Script Python
•	Analyse des patterns
•	Recommandations

Généralisation
-	Statistiques descriptives
-	SI
Hypothèses
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
text_norm = text.replace("'", "'").replace("'", "'").replace("'", "'")

print("=== Recherche des sections ===\n")

section_titles = [
    'Mots clés',
    'Contexte',
    'Problématique',
    'Contraintes',
    'Livrables',
    'Généralisation',
    'Hypothèses',
    'Plan d\'actions'
]

section_positions = []

for section_name in section_titles:
    patterns = [
        rf'^{re.escape(section_name)}(?:\s*[:\-]|\s*$)',
        rf'^{re.escape(section_name)}\s*&',
    ]

    all_matches = []
    for pattern in patterns:
        matches = list(re.finditer(pattern, text_norm, re.MULTILINE | re.IGNORECASE))
        all_matches.extend(matches)

    if all_matches:
        all_matches.sort(key=lambda m: m.start())
        match = all_matches[0]
        line_num = text_norm[:match.start()].count('\n') + 1
        section_positions.append({
            'name': section_name,
            'start': match.start(),
            'line': line_num
        })
        print(f"[OK] {section_name:20} -> ligne {line_num:3}, position {match.start()}")
    else:
        print(f"[--] {section_name:20} -> NON TROUVE")

print("\n=== Sections triées par position ===\n")
section_positions.sort(key=lambda x: x['start'])
for i, sec in enumerate(section_positions):
    print(f"{i+1}. {sec['name']:20} ligne {sec['line']}")

print("\n=== Parsing complet ===\n")
parser = CRParser()
data = parser.parse(text)

print(f"Hypothèses: {len(data['hypotheses'])}")
for i, h in enumerate(data['hypotheses'], 1):
    print(f"  {i}. {h}")

print(f"\nPlan d'actions: {len(data['plan_actions'])}")
for i, p in enumerate(data['plan_actions'], 1):
    print(f"  {i}. {p}")
