# Prosit Manager

Outil personnel pour gérer et générer automatiquement des documents de prosit à partir de comptes-rendus de réunion.

## Fonctionnalités

- **Extraction automatique** : Copier-coller un CR de réunion et l'outil extrait automatiquement toutes les sections (mots clés, contexte, problématique, etc.)
- **Génération de documents** : Remplissage automatique d'un template Word avec les données extraites
- **Configuration personnalisable** : Sauvegarde de vos informations personnelles et du chemin vers votre template
- **Interface moderne** : Interface graphique claire et intuitive avec thème sombre

## Installation

### Prérequis
- Python 3.8 ou supérieur

### Installation des dépendances

```bash
pip install -r requirements.txt
```

## Utilisation

### Lancer l'application

**Windows** (recommandé - nettoie automatiquement le cache) :
```cmd
start.bat
```

**Ou manuellement** :
```bash
python main.py
```

**⚠️ Note importante** : Si vous modifiez le code, supprimez le cache avant de relancer :
```bash
rm -rf src/__pycache__
python main.py
```

### Étapes d'utilisation

1. **Configuration initiale** :
   - Renseignez votre nom et formation
   - Sélectionnez votre template Word
   - Cliquez sur "Sauvegarder config"

2. **Analyser un CR** :
   - Copiez le contenu de votre compte-rendu de réunion
   - Collez-le dans la zone de texte de gauche
   - Cliquez sur "Analyser le CR"

3. **Vérifier les données extraites** :
   - Les données apparaissent dans la zone de droite
   - Vérifiez que tout a été correctement extrait

4. **Générer le document** :
   - Cliquez sur "Générer le document Word"
   - Choisissez l'emplacement de sauvegarde
   - Le document est créé avec toutes les informations remplies

## Structure du projet

```
prosit_manager/
├── src/
│   ├── __init__.py
│   ├── cr_parser.py       # Parser pour extraire les données du CR
│   ├── docx_generator.py  # Générateur de documents Word
│   └── gui.py             # Interface graphique
├── main.py                # Point d'entrée de l'application
├── requirements.txt       # Dépendances Python
├── specifications.md      # Spécifications du projet
└── README.md             # Ce fichier
```

## Format du CR attendu

L'outil s'attend à un format de CR structuré avec les sections suivantes :

```
Bloc X
Prosit aller Y – Titre du prosit
JJ/MM/AAAA

Mots clés & Mots inconnus
• Mot 1
• Mot 2

Contexte
Description du contexte...

Problématique
- Question principale

Contraintes
• Contrainte 1
• Contrainte 2

Livrables
• Livrable 1

Généralisation
Description...

Hypothèses
• Hypothèse 1
• Hypothèse 2

Plan d'actions
1. Action 1
2. Action 2
```

## Technologies utilisées

- **Python 3.8+**
- **CustomTkinter** : Interface graphique moderne
- **python-docx** : Manipulation de documents Word
- **Regex** : Extraction de données structurées

## Licence

Usage personnel - Robin NOIRET

## Support

Pour tout problème ou suggestion d'amélioration, créez une issue dans le dépôt du projet.
