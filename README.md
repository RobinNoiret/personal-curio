<div align="center">

# 🎯 Curio

**Pleins d'outils pour se simplifier le quotidien**

[![Version](https://img.shields.io/badge/version-1.0.0-yellow.svg)](https://github.com/your-repo)

[Fonctionnalités](#-fonctionnalités) • [Installation](#-installation) • [Utilisation](#-utilisation) • [Build](#-build-exécutable)

</div>

---

## Table des matières

- [À propos](#-à-propos)
- [Fonctionnalités](#-fonctionnalités)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [Build exécutable](#-build-exécutable)
- [Structure du projet](#-structure-du-projet)
- [Technologies](#-technologies)
- [Auteur](#-auteur)

---

## À propos

**Curio** est une application desktop développée pour simplifier et automatiser les tâches répétitives liées à :
- La gestion et la génération de documents de prosit à partir de comptes-rendus
- L'extraction et l'organisation de définitions depuis des documents Word vers Obsidian
- La révision et la mémorisation de notes grâce à un système de rappel intelligent

L'application offre une **interface graphique moderne** développée avec CustomTkinter, offrant une expérience utilisateur fluide et intuitive.

---

## Fonctionnalités

### Page d'accueil personnalisée
- Message de bienvenue personnalisé avec votre prénom
- Trois modes d'affichage configurables :
  - **Phrase fixe** : Message de bienvenue simple
  - **Citation aléatoire** : Citations inspirantes aléatoires
  - **Rappel de note** : Révision aléatoire de vos notes Obsidian
- Accès rapide à la visualisation complète des notes

### Gestion de Prosits
- **Extraction automatique** de comptes-rendus de réunion
  - Détection automatique des sections (mots clés, contexte, problématique, contraintes, etc.)
  - Analyse par regex des structures de document
- **Génération de documents Word** professionnels
  - Remplissage automatique d'un template Word personnalisé
  - Export prêt à l'emploi avec mise en forme préservée
- **Interface de copier-coller** simple et rapide

### Extraction Word to Obsidian
- **Import de fichiers Word** (.docx)
- **Extraction automatique** de définitions avec support de deux modes :
  - Import de fichier Word
  - Copier-coller de texte brut (format "Terme : Définition")
- **Éditeur de notes complet** avec :
  - Modification en temps réel du titre et de la définition
  - Métadonnées YAML personnalisables (type, date, from, about, related, tags)
  - Autocomplétion intelligente pour les liens Obsidian (`[[note]]`)
  - Sélection multiple pour supprimer plusieurs notes à la fois
  - Sauvegarde automatique lors du changement de note
- **Export vers Obsidian** au format Markdown avec frontmatter YAML
- **Scanner de vault Obsidian** intégré pour l'autocomplétion

### Visualiseur de notes
- Affichage formaté des notes Obsidian
- Navigation fluide entre les notes
- Retour rapide vers la page d'accueil

### Paramètres
- Configuration de vos informations personnelles (prénom, formation)
- Sélection du template Word pour les prosits
- Configuration du dossier d'export Obsidian
- Choix du dossier de notes pour les rappels
- Sélection du mode d'affichage de la page d'accueil
- Sauvegarde automatique de la configuration

### Logs et informations
- Système de logs détaillé pour le débogage
- Page d'informations sur l'application (version, auteur, description)

---

## Installation

### Prérequis
- **Python 3.8+** ([Télécharger Python](https://www.python.org/downloads/))
- pip (installé avec Python)

### Installation des dépendances

1. **Cloner ou télécharger le projet**
   ```bash
   git clone https://github.com/your-repo/curio.git
   cd curio
   ```

2. **Installer les dépendances Python**
   ```bash
   pip install -r requirements.txt
   ```

### Dépendances principales
- `customtkinter` : Interface graphique moderne
- `python-docx` : Manipulation de documents Word
- `Pillow` : Gestion des images

---

## Utilisation

### Lancer l'application (mode développement)

**Méthode simple** :
```bash
python main.py
```

### Configuration initiale

Au premier lancement, configurez l'application via la page **Paramètres** :

1. **Informations personnelles** :
   - Renseignez votre prénom (utilisé dans l'accueil)
   - Indiquez votre formation (utilisé dans les documents de prosit)

2. **Chemins et templates** :
   - Sélectionnez votre template Word pour les prosits
   - Configurez le dossier d'export Obsidian (où seront créées les notes)
   - Configurez le dossier de notes pour les rappels (optionnel)

3. **Préférences** :
   - Choisissez le mode d'affichage de la page d'accueil

4. **Sauvegarder** :
   - Cliquez sur "Sauvegarder la configuration"

### Workflow : Génération de prosit

1. **Accédez à la page Prosit**
2. **Copiez votre compte-rendu de réunion**
3. **Collez-le dans la zone de texte**
4. **Cliquez sur "Analyser le CR"**
5. **Vérifiez les données extraites** dans la zone de droite
6. **Cliquez sur "Générer le document Word"**
7. **Choisissez l'emplacement de sauvegarde**

Le document est généré avec toutes les sections automatiquement remplies !

### Workflow : Extraction Word → Obsidian

1. **Accédez à la page Obsidian**
2. **Choisissez votre mode d'import** :
   - **Import fichier** : Sélectionnez un fichier .docx
   - **Copier-coller** : Collez vos définitions (format "Terme : Définition")
3. **Les notes sont automatiquement extraites**
4. **Éditez chaque note** :
   - Cliquez sur une note dans la liste de gauche
   - Modifiez le titre et la définition
   - Complétez les métadonnées YAML (optionnel)
   - Utilisez `[[` pour créer des liens vers d'autres notes (autocomplétion)
5. **Exportez vers Obsidian** :
   - Cliquez sur "Exporter vers Obsidian"
   - Les fichiers .md sont créés dans votre dossier configuré

### Format de CR attendu (pour Prosit)

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

---

## Build exécutable

Pour créer un exécutable Windows autonome (sans besoin de Python installé) :

### Prérequis pour le build
```bash
pip install -r requirements-build.txt
```

### Méthode automatique (recommandée)

**Sur Windows** :
```cmd
setup_build.bat
```

Ce script va :
1. Installer PyInstaller si nécessaire
2. Builder l'application
3. Créer un exécutable dans le dossier `dist/Curio/`

### Méthode manuelle

1. **Installer PyInstaller**
   ```bash
   pip install pyinstaller
   ```

2. **Lancer le build**
   ```bash
   python build.py
   ```

   Ou directement avec PyInstaller :
   ```bash
   pyinstaller curio.spec
   ```

3. **L'exécutable sera disponible dans** :
   ```
   dist/Curio/Curio.exe
   ```

### Distribution

Pour distribuer l'application :
- Compressez le dossier `dist/Curio/` en archive ZIP
- Partagez l'archive
- L'utilisateur final n'a qu'à extraire et lancer `Curio.exe`

---

## Structure du projet

```
prosit_manager/
├── assets/                      # Ressources (icônes, images)
│   ├── curio_basic.png          # Logo de l'application
│   └── curio_optimized.ico      # Icône Windows
├── config/                      # Fichiers de configuration
├── src/                         # Code source
│   ├── pages/                   # Pages de l'application
│   │   ├── home_page.py         # Page d'accueil
│   │   ├── prosit_page.py       # Page de gestion des prosits
│   │   ├── obsidian_page.py     # Page d'extraction Obsidian
│   │   ├── note_viewer_page.py  # Visualiseur de notes
│   │   ├── settings_page.py     # Page de paramètres
│   │   ├── logs_page.py         # Page des logs
│   │   └── info_page.py         # Page d'informations
│   ├── utils/                   # Utilitaires
│   │   ├── config_manager.py    # Gestion de la configuration
│   │   ├── cr_parser.py         # Parser de comptes-rendus
│   │   ├── docx_generator.py    # Générateur de documents Word
│   │   ├── obsidian_extractor.py # Extracteur Word → Obsidian
│   │   ├── obsidian_scanner.py  # Scanner de vault Obsidian
│   │   ├── home_messages.py     # Messages de la page d'accueil
│   │   └── logger.py            # Système de logs
│   ├── autocomplete_widget.py   # Widget d'autocomplétion
│   ├── constants.py             # Constantes (couleurs, fonts)
│   ├── gui.py                   # Interface principale
│   ├── navigation.py            # Barre de navigation
│   └── ui_components.py         # Composants UI réutilisables
├── main.py                      # Point d'entrée de l'application
├── build.py                     # Script de build
├── curio.spec                   # Configuration PyInstaller
├── requirements.txt             # Dépendances Python
├── requirements-build.txt       # Dépendances pour le build
├── app_info.txt                 # Métadonnées de l'application
└── README.md                    # Ce fichier
```

---

## Technologies

- **[Python 3.8+](https://www.python.org/)** - Langage de programmation
- **[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)** - Framework d'interface graphique moderne
- **[python-docx](https://python-docx.readthedocs.io/)** - Manipulation de documents Word
- **[Pillow](https://pillow.readthedocs.io/)** - Traitement d'images
- **[PyInstaller](https://pyinstaller.org/)** - Création d'exécutables
- **Regex** - Extraction de données structurées

---

## Auteur

**NOIRET Robin**

Application personnelle développée pour automatiser les tâches quotidiennes liées à la gestion de prosits et de notes.

---

## Licence

Usage personnel - © 2024 Robin NOIRET

---

<div align="center">

**Curio v1.0.0** - Simplifie ton quotidien 🚀

</div>
