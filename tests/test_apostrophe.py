"""
Test pour identifier le type d'apostrophe
"""

# L'apostrophe que vous avez copiée
text_from_user = "Plan d'actions"

print("=== Analyse de l'apostrophe ===")
for i, char in enumerate(text_from_user):
    print(f"Char {i}: '{char}' -> Unicode: U+{ord(char):04X} ({ord(char)})")

print()
print(f"Texte complet: {text_from_user}")
print(f"Représentation: {repr(text_from_user)}")
