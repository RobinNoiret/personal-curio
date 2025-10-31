# Architecture du Projet

## 📁 Structure des Dossiers

```
prosit_manager/
├── assets/                      # Ressources (images, logos)
│   └── logo_black_version.png
├── src/                         # Code source
│   ├── utils/                   # Utilitaires
│   │   ├── __init__.py
│   │   ├── config_manager.py   # Gestion configuration
│   │   ├── cr_parser.py        # Parser de compte-rendu
│   │   └── docx_generator.py   # Générateur de documents
│   ├── pages/                   # Pages de l'application
│   │   ├── __init__.py
│   │   ├── base_page.py        # Classe abstraite
│   │   ├── home_page.py        # Page d'accueil
│   │   ├── prosit_page.py      # Page prosit
│   │   └── settings_page.py    # Page paramètres
│   ├── constants.py             # Constantes (couleurs, polices, etc.)
│   ├── ui_components.py         # Composants UI réutilisables
│   ├── settings_components.py   # Composants des paramètres
│   ├── navigation.py            # Sidebar de navigation
│   └── gui.py                   # Contrôleur principal
├── config.txt                   # Configuration utilisateur
├── app_info.txt                 # Métadonnées de l'application
├── main.py                      # Point d'entrée
└── requirements.txt             # Dépendances
```

## 🏗️ Architecture Modulaire

### **1. Séparation des Responsabilités**

#### **Utils (`src/utils/`)**
Utilitaires réutilisables sans dépendance UI :
- `ConfigManager` : Gestion de la configuration
- `CRParser` : Analyse des comptes-rendus
- `DocxGenerator` : Génération de documents Word

#### **Pages (`src/pages/`)**
Chaque page est un module indépendant :
- Hérite de `BasePage`
- Gère son propre rendu
- Encapsule sa logique métier

#### **Composants UI (`src/ui_components.py`)**
Composants génériques réutilisables :
- `Button` : primary, secondary, outline
- `Label` : title, text
- `Input` : text_entry, textbox
- `Container` : section, scrollable, transparent
- `Spacer` : vertical, horizontal

#### **Navigation (`src/navigation.py`)**
Barre de navigation latérale autonome

#### **Constantes (`src/constants.py`)**
Configuration centralisée :
- Couleurs
- Polices
- Dimensions
- Navigation items

### **2. Patterns Utilisés**

#### **Factory Pattern**
```python
# Au lieu de répéter la configuration
Button.primary(parent, "Sauvegarder", command)
Button.secondary(parent, "Annuler", command)
Button.outline(parent, "Parcourir", command)
```

#### **Page Object Pattern**
```python
class HomePage(BasePage):
    def render(self):
        # Logique de rendu isolée
        pass
```

#### **Dependency Injection**
```python
page = PrositPage(parent, colors, parser, generator, config)
```

## 🎯 Principes de Conception

### **SOLID**
- **S**ingle Responsibility : Chaque module a une responsabilité unique
- **O**pen/Closed : Extensible via héritage (BasePage)
- **L**iskov Substitution : Toutes les pages sont interchangeables
- **I**nterface Segregation : Interfaces minimales (BasePage)
- **D**ependency Inversion : Injection de dépendances

### **DRY (Don't Repeat Yourself)**
- Composants réutilisables
- Constantes centralisées
- Factory methods

### **Separation of Concerns**
- UI séparée de la logique métier
- Configuration séparée du code
- Pages isolées les unes des autres

## 🔄 Flux de Navigation

```
main.py
  └─> PrositManagerGUI.__init__()
       ├─> ConfigManager (charge config)
       ├─> NavigationSidebar (crée menu)
       └─> navigate_to('home')
            └─> HomePage.render()
                 └─> Affichage de la page
```

## 📝 Comment Ajouter une Nouvelle Page

1. **Créer le fichier** : `src/pages/ma_page.py`
2. **Hériter de BasePage** :
```python
from .base_page import BasePage

class MaPage(BasePage):
    def render(self):
        container = Container.scrollable(self.parent)
        # Votre contenu ici
        return container
```
3. **Ajouter dans `pages/__init__.py`**
4. **Importer dans `gui.py`**
5. **Ajouter la route dans `navigate_to()`**
6. **Mettre à jour `NAV_ITEMS` dans `constants.py`**

## 🛠️ Comment Ajouter un Nouveau Composant

1. **Dans `ui_components.py`** :
```python
class MonComposant:
    @staticmethod
    def create(parent, **kwargs):
        # Logique de création
        return widget
```

2. **Utiliser** :
```python
from ..ui_components import MonComposant
widget = MonComposant.create(parent, options...)
```

## 📊 Statistiques

- **Lignes de code gui.py** : ~150 (vs 700+ avant)
- **Modules** : 14 fichiers organisés
- **Réutilisabilité** : Composants factories
- **Maintenabilité** : ⭐⭐⭐⭐⭐

## 🚀 Évolutivité

Cette architecture permet facilement :
- ✅ Ajouter de nouvelles pages
- ✅ Créer de nouveaux composants
- ✅ Changer le thème (modifier `constants.py`)
- ✅ Ajouter de nouvelles features
- ✅ Tester unitairement chaque module
- ✅ Réutiliser des composants dans d'autres projets
