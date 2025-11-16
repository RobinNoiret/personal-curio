# Guide Rapide - Build Curio en Exécutable

## 🚀 Quick Start

```bash
# 1. Installer les dépendances de build
pip install -r requirements-build.txt

# 2. Lancer le build
python build.py

# 3. L'exécutable est dans dist/Curio/
```

C'est tout ! 🎉

## 📋 Checklist avant distribution

- [ ] Tester l'exécutable sur une machine vierge (sans Python)
- [ ] Vérifier que les assets (fonts, images) sont présents
- [ ] Tester la création de config dans %APPDATA%
- [ ] Tester la génération de logs
- [ ] Vérifier que l'application fonctionne hors ligne

## 📦 Structure du build

```
dist/Curio/
├── Curio.exe              # ← L'exécutable à lancer
├── _internal/             # Dépendances (ne pas toucher)
│   ├── customtkinter/
│   ├── PIL/
│   └── ...
├── assets/                # Polices et images
│   ├── fonts/
│   │   ├── Degular-*.otf
│   │   └── Inter-*.ttf
│   └── curio_basic.png
├── config/                # Config par défaut (référence)
└── README.txt             # Instructions utilisateur
```

## 🗂️ Où sont stockées les données utilisateur ?

### Windows (par défaut sur votre machine)
```
C:\Users\Noiret\AppData\Roaming\Curio\
├── config.txt             # Configuration utilisateur
├── app_info.txt           # Info application
└── logs/
    └── curio_20250116.log # Logs quotidiens
```

### Pour accéder rapidement
- Taper `%APPDATA%\Curio` dans l'explorateur Windows
- Ou depuis l'application : Page "Logs"

## 🎯 Taille approximative

- **Exécutable complet** : ~120-150 MB
- **Compressé (ZIP)** : ~50-70 MB

## ⚡ Optimisations possibles

### Réduire la taille
Si 150 MB c'est trop :
1. Exclure des modules inutilisés dans `curio.spec`
2. Utiliser UPX compression (déjà activé)
3. Mode OneFile (voir BUILD.md) : ~80 MB mais plus lent au démarrage

### Icône personnalisée
Pour Windows, il faut un fichier `.ico` :

```bash
# Convertir PNG vers ICO (nécessite pillow)
python -c "from PIL import Image; img = Image.open('assets/curio_basic.png'); img.save('assets/curio.ico', sizes=[(256,256)])"
```

Puis dans `curio.spec` :
```python
icon='assets/curio.ico'
```

## 🐛 Problèmes courants

### "L'exécutable ne se lance pas"
→ Vérifiez que tous les assets sont présents dans dist/Curio/assets/

### "Module customtkinter introuvable"
→ Réinstallez : `pip install --force-reinstall customtkinter`

### "Antivirus bloque l'exe"
→ Normal pour un nouvel .exe. Ajouter une exception ou signer le code.

### "L'interface ne s'affiche pas"
→ Lancez avec `console=True` dans curio.spec pour voir les erreurs

## 📝 Notes importantes

1. **Ne pas inclure de données sensibles** dans le build (mots de passe, tokens, etc.)
2. **Tester sur machine propre** avant distribution
3. **Versionner** : Mettez à jour la version dans `app_info.txt`
4. **Changelog** : Documentez les changements pour les utilisateurs

## 🔄 Workflow de release

```bash
# 1. Mettre à jour la version
# Éditer app_info.txt : version=2.1.0

# 2. Commit des changements
git add .
git commit -m "Release v2.1.0"
git tag v2.1.0

# 3. Build
python build.py

# 4. Test
cd dist/Curio
./Curio.exe

# 5. Package
cd dist
Compress-Archive -Path Curio -DestinationPath Curio-v2.1.0.zip

# 6. Distribuer
# Upload sur GitHub Releases ou partager le ZIP
```

## 📚 Documentation complète

Pour plus de détails, voir [BUILD.md](BUILD.md)
