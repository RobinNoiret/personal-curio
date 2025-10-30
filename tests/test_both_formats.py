"""
Test du parser avec les deux formats de CR
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.cr_parser import CRParser

# Format 1 : avec puces
format1 = """Bloc 1
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

# Format 2 : sans puces, lignes simples
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


def test_format(name, text):
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print('='*60)

    parser = CRParser()
    data = parser.parse(text)

    print(f"\nBloc: {data['bloc']}")
    print(f"Prosit: {data['prosit_number']} - {data['prosit_title']}")
    print(f"Date: {data['date']}")
    print(f"\nMots clés ({len(data['mots_cles'])}): {data['mots_cles'][:3]}...")
    print(f"Hypothèses ({len(data['hypotheses'])}): OK" if data['hypotheses'] else "Hypothèses: MANQUANT")
    print(f"Plan d'actions ({len(data['plan_actions'])}): OK" if data['plan_actions'] else "Plan d'actions: MANQUANT")

    if data['plan_actions']:
        print("\nPlan d'actions détaillé:")
        for i, action in enumerate(data['plan_actions'], 1):
            print(f"  {i}. {action}")

    return data


if __name__ == "__main__":
    print("TEST DU PARSER ROBUSTE")
    print("Tests avec deux formats différents de CR\n")

    data1 = test_format("Format 1 (avec puces •)", format1)
    data2 = test_format("Format 2 (lignes simples)", format2)

    print(f"\n{'='*60}")
    print("RÉSUMÉ")
    print('='*60)
    print(f"Format 1: {len(data1['plan_actions'])} actions extraites")
    print(f"Format 2: {len(data2['plan_actions'])} actions extraites")
    print("\n✓ Tests terminés avec succès !" if data1['plan_actions'] and data2['plan_actions'] else "\n✗ Échec de l'extraction")
