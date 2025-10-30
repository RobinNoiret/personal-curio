"""
Debug du Format 2
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.cr_parser import CRParser

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

parser = CRParser()
data = parser.parse(format2)

print("=== Résultats extraction ===")
print(f"Mots clés: {data['mots_cles']}")
print(f"\nPlan d'actions: {data['plan_actions']}")
print(f"\nNombre d'actions: {len(data['plan_actions'])}")
