"""
Simule exactement ce que fait la GUI
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.cr_parser import CRParser

# Simuler l'action de copier-coller dans la GUI
print("Collez votre CR ici (Ctrl+Z puis Entrée pour terminer):\n")

lines = []
try:
    while True:
        line = input()
        lines.append(line)
except EOFError:
    pass

cr_text = '\n'.join(lines)

print("\n" + "="*60)
print("ANALYSE DU CR")
print("="*60)

parser = CRParser()
data = parser.parse(cr_text)

formatted = parser.format_for_display(data)

print("\n" + "="*60)
print("RESULTAT")
print("="*60)
print(formatted)

print("\n" + "="*60)
print("VERIFICATION")
print("="*60)
print(f"Nombre d'hypotheses: {len(data['hypotheses'])}")
print(f"Nombre d'actions dans le plan: {len(data['plan_actions'])}")
