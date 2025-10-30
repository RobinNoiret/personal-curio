"""
Script de test pour vérifier le parser
"""
from src.cr_parser import CRParser

# Exemple de CR fourni
example_cr = """Bloc 1
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

def main():
    parser = CRParser()
    print("=== Test du Parser ===\n")

    # Parser le CR
    data = parser.parse(example_cr)

    # Afficher les résultats
    print(f"Bloc: {data['bloc']}")
    print(f"Numéro de Prosit: {data['prosit_number']}")
    print(f"Titre: {data['prosit_title']}")
    print(f"Date: {data['date']}")
    print()

    print(f"Mots clés ({len(data['mots_cles'])}): {data['mots_cles']}")
    print()

    print(f"Contexte: {data['contexte']}")
    print()

    print(f"Problématique: {data['problematique']}")
    print()

    print(f"Contraintes ({len(data['contraintes'])}): {data['contraintes']}")
    print()

    print(f"Livrables ({len(data['livrables'])}): {data['livrables']}")
    print()

    print(f"Généralisation: {data['generalisation']}")
    print()

    print(f"Hypothèses ({len(data['hypotheses'])}): {data['hypotheses']}")
    print()

    print(f"Plan d'actions ({len(data['plan_actions'])}): {data['plan_actions']}")
    print()

    print("\n=== Formatage pour affichage ===\n")
    formatted = parser.format_for_display(data)
    print(formatted)

if __name__ == "__main__":
    main()
