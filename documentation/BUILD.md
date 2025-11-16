# Guide de Build - Curio

Ce guide explique comment créer un exécutable autonome de Curio.

## Prérequis

1. Python 3.8 ou supérieur installé
2. Toutes les dépendances du projet installées

## Installation des dépendances

```bash
# Installer les dépendances de l'application
pip install -r requirements.txt

# Installer les dépendances de build
pip install -r requirements-build.txt
```

## Construction de l'exécutable

### Méthode rapide (recommandée)

Utilisez le script de build automatisé :

```bash
python build.py
```

Ce script va :
1. Nettoyer les anciens builds
2. Vérifier que PyInstaller est installé
3. Construire l'exécutable
4. Créer un README pour l'utilisateur final

### Méthode manuelle

Si vous préférez lancer PyInstaller manuellement :

```bash
# Nettoyer les anciens builds
rmdir /s /q build dist  # Windows
# ou
rm -rf build dist  # Linux/macOS

# Lancer PyInstaller
pyinstaller curio.spec --clean --noconfirm
```

## Résultat

L'exécutable sera créé dans le dossier `dist/Curio/` :

```
dist/
└── Curio/
    ├── Curio.exe          # L'exécutable principal
    ├── _internal/         # Fichiers internes nécessaires
    ├── assets/            # Assets (fonts, images)
    ├── config/            # Configuration par défaut
    └── README.txt         # Instructions pour l'utilisateur
```

## Distribution

Pour distribuer l'application :

1. Compressez le dossier `dist/Curio/` en ZIP
2. Partagez le fichier ZIP
3. L'utilisateur doit :
   - Extraire le ZIP
   - Lancer `Curio.exe`

## Emplacements des fichiers utilisateur

Les fichiers de configuration et logs sont stockés dans des emplacements système appropriés :

### Windows
- Configuration : `%APPDATA%\Curio\`
  - `config.txt` : Configuration utilisateur
  - `app_info.txt` : Informations de l'application
- Logs : `%APPDATA%\Curio\logs\`

### macOS
- Configuration : `~/Library/Application Support/Curio/`
- Logs : `~/Library/Logs/Curio/`

### Linux
- Configuration : `~/.config/Curio/`
- Logs : `~/.local/share/Curio/logs/`

## Personnalisation du build

Pour modifier le build, éditez le fichier `curio.spec` :

### Changer l'icône
```python
icon='assets/votre_icone.ico'  # Windows nécessite un .ico
```

### Ajouter des fichiers
```python
datas=[
    ('assets', 'assets'),
    ('nouveau_dossier', 'nouveau_dossier'),
],
```

### Mode debug
Pour afficher la console (utile pour le debug) :
```python
console=True,  # Au lieu de False
```

## Dépannage

### Erreur "Module not found"

Si PyInstaller ne trouve pas certains modules, ajoutez-les dans `hiddenimports` :

```python
hiddenimports = [
    'customtkinter',
    'PIL._tkinter_finder',
    'votre_module',  # Ajouter ici
]
```

### L'exécutable est trop gros

Pour réduire la taille :
- Utilisez UPX compression (déjà activé dans le .spec)
- Excluez les modules inutiles dans `excludes`

### Antivirus bloque l'exécutable

C'est normal pour un nouvel exécutable. Options :
- Ajouter une exception dans l'antivirus
- Signer l'exécutable avec un certificat de code (production)

## Notes importantes

- **Ne commitez jamais** les dossiers `build/` et `dist/` dans Git
- La première exécution peut être lente (création des dossiers de config)
- Les logs sont accessibles via l'interface (page Logs)

## Version OneFile (optionnel)

Pour créer un exécutable unique au lieu d'un dossier, modifiez `curio.spec` :

```python
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,      # Ajouter
    a.zipfiles,      # Ajouter
    a.datas,         # Ajouter
    [],
    name='Curio',
    # ... reste identique
)

# Supprimer ou commenter la section COLLECT
```

⚠️ **Attention** : Le mode OneFile est plus lent au démarrage car il doit extraire les fichiers temporairement.
