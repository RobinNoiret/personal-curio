"""
Test depuis un fichier
"""
from src.cr_parser import CRParser

with open('test_cr.txt', 'r', encoding='utf-8') as f:
    cr_text = f.read()

print("=== Contenu du fichier ===")
print(f"Longueur: {len(cr_text)} caracteres")
print(f"Nombre de lignes: {len(cr_text.splitlines())}")
print()

parser = CRParser()
data = parser.parse(cr_text)

print("=== Resultat du parsing ===")
print(f"Bloc: {data['bloc']}")
print(f"Prosit: {data['prosit_number']}")
print(f"Mots cles: {len(data['mots_cles'])}")
print(f"Hypotheses: {len(data['hypotheses'])}")
print(f"Plan d'actions: {len(data['plan_actions'])}")
print()

if data['plan_actions']:
    print("Plan d'actions trouve:")
    for i, action in enumerate(data['plan_actions'], 1):
        print(f"  {i}. {action}")
else:
    print("ERREUR: Plan d'actions VIDE!")

print("\n=== Affichage complet ===")
formatted = parser.format_for_display(data)
print(formatted)
