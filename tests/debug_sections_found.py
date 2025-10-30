"""
Debug : quelles sections sont trouvées ?
"""
import sys
import os
import re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

format2 = """Bloc SF Ingénieur

Prosit aller 2 – Statistiques descriptives

14.10.2025

ligne horizontale

Mots clés & Mots inconnus

Statistiques descriptives

Analyse de données

Exhaustif

Restriction

Pertinent

dataset



Contexte

Le projet bikesurfing vise à établir un service de libre-service de vélo. Face aux restrictions ils doivent choisir leur jour d'ouverture.



Problématique

Comment trouver le/les meilleurs jours d'ouverture en utilisant les données ?

Comment présenter les résultats de l'analyse ?



Contraintes

Dataset kaggle

Résultats exhaustifs

Restriction sur le nombre de jour d'ouverture



Livrables

Classement des meilleurs jours (graphiques)

Code python d'analyse

CER



Généralisation

Statistiques descriptives, python,



Hypothèses

Nous devrons présenter les résultats sont forme de graphique

Les jours de la semaine attirent moins les clients que le weekend

Le jour le plus optimale tombera pendant les vacances

Il y aura des trous dans les données



Plan d'actions

Mots clés

Analyse des ressources

Comprendre la structure des données

Développement du programme python (analyse + graphique)

Analyse des résultats

Conclusion

Validation des hypothèses"""

# Normaliser
text = format2.replace("'", "'").replace("'", "'").replace("'", "'")

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

print("=== Recherche des sections ===\n")

for section_name in section_titles:
    patterns = [
        rf'^{re.escape(section_name)}(?:\s*[:\-]|\s*$)',
        rf'^{re.escape(section_name)}\s*&',
    ]

    print(f"Section '{section_name}':")
    for i, pattern in enumerate(patterns, 1):
        matches = list(re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE))
        if matches:
            print(f"  Pattern {i}: {len(matches)} trouvée(s)")
            for j, match in enumerate(matches, 1):
                pos = match.start()
                line_num = text[:pos].count('\n') + 1
                print(f"    Match {j}: position {pos}, ligne {line_num}")
                print(f"      Texte: {repr(text[pos:pos+50])}")
        else:
            print(f"  Pattern {i}: aucune")
    print()
