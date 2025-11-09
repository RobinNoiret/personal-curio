# Feature: Extracteur Word vers Obsidian

## Vue d'ensemble

Module permettant l'extraction automatique de documents Word (.docx) vers des notes Obsidian avec interface de révision avant création.

## Fonctionnalités

### Interface 1 : Import de fichier
- Zone de sélection de fichier .docx (max 50 MB)
- Bouton "Parcourir" pour sélectionner un fichier
- Indicateur de progression pendant le parsing
- Messages d'erreur si format invalide

### Interface 2 : Édition des notes extraites
- **Layout**:
  - Liste scrollable des notes détectées (panneau gauche)
  - Panel d'édition pour la note sélectionnée (panneau droit)
  - Boutons "Supprimer note" et "Ajouter note"
  - Bouton "Exporter vers Obsidian"

## Configuration

Le fichier de configuration se trouve dans `config/obsidian_extractor.yaml`:

```yaml
# config/obsidian_extractor.yaml
vault_path: "~/Obsidian/MyVault"
default_folder: "/Imports"
date_format: "YYYY-MM-DD"
frontmatter_template: "standard"
auto_link_detection: true
max_file_size_mb: 50

# Template Obsidian pour les notes de mots-clés
note_template:
  type: "réunion"
  default_tags:
    - "réunion"
    - "vicat"
    - "project"
    - "raw"
  data_quality: "raw"

# Section à extraire du document Word
extraction:
  section_title: "Définition des mots clés"
  definition_pattern: "^(.+?)\\s*[:\\u2009\\u00a0]\\s*(.+)$"
```

## Template Obsidian

Les notes générées suivent ce template:

```markdown
---
type: réunion
guest:
date: YYYY-MM-DD
topic: [Titre du mot-clé]
related:
tags:
  - réunion
  - vicat
  - project
  - raw
data_quality: raw
---
___
#### Ressources
___
### Définition

[Définition extraite du document Word]
```

## Utilisation

### Via l'interface graphique

1. Lancer l'application : `python main.py`
2. Cliquer sur "Obsidian Extractor" dans la navigation
3. Cliquer sur "Parcourir" et sélectionner un fichier .docx
4. Réviser les notes extraites (éditer, ajouter, supprimer)
5. Cliquer sur "Exporter vers Obsidian"
6. Sélectionner le dossier de destination

### Via le code

```python
from src.utils.obsidian_extractor import WordToObsidianExtractor

# Initialiser l'extracteur
extractor = WordToObsidianExtractor()

# Extraire les notes
notes = extractor.extract_from_docx("document.docx")

# Afficher les notes
for note in notes:
    print(f"{note.title}: {note.definition}")

# Exporter vers Obsidian
output_dir = "~/Obsidian/MyVault/Imports"
created_files = extractor.export_notes(output_dir)
print(f"{len(created_files)} notes exportées")
```

## Format du document Word attendu

Le document Word doit contenir une section intitulée **"Définition des mots clés"** avec des définitions au format:

```
Terme : Définition du terme
Autre terme : Définition de l'autre terme
```

Exemple:
```
Définition des mots clés
Complexité O(...) : En informatique, c'est une notation mathématique...
Table de hachage : Une structure de données qui implémente...
```

## Structure des fichiers

```
prosit_manager/
├── config/
│   └── obsidian_extractor.yaml    # Configuration
├── src/
│   ├── pages/
│   │   └── obsidian_page.py       # Interface graphique
│   └── utils/
│       └── obsidian_extractor.py  # Logique d'extraction
└── test_extraction.py             # Script de test
```

## Dépendances

- `python-docx>=1.1.0` : Lecture des fichiers Word
- `PyYAML>=6.0` : Lecture de la configuration
- `customtkinter>=5.2.0` : Interface graphique

## Test

Pour tester l'extraction sans l'interface graphique:

```bash
python test_extraction.py
```

Ce script affichera:
- Le nombre de notes extraites
- La liste des notes avec leur titre et définition
- Un aperçu du format Markdown généré
