"""
Script de build pour créer l'exécutable Curio avec PyInstaller
"""
import subprocess
import sys
import shutil
import os
from pathlib import Path


def clean_build_folders():
    """Nettoie les dossiers de build précédents"""
    print("🧹 Nettoyage des dossiers de build...")
    folders_to_clean = ['build', 'dist']

    for folder in folders_to_clean:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"  ✓ {folder}/ supprimé")


def check_pyinstaller():
    """Vérifie que PyInstaller est installé"""
    try:
        import PyInstaller
        print(f"✓ PyInstaller {PyInstaller.__version__} détecté")
        return True
    except ImportError:
        print("❌ PyInstaller n'est pas installé")
        print("   Installez-le avec: pip install pyinstaller")
        return False


def build_executable():
    """Construit l'exécutable avec PyInstaller"""
    print("\n🔨 Construction de l'exécutable...")

    # Commande PyInstaller
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "curio.spec",
        "--clean",
        "--noconfirm"
    ]

    # Lancer PyInstaller
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Build réussi!")
        print(f"\n📦 Exécutable disponible dans: {os.path.abspath('dist/Curio')}")
        return True
    else:
        print("❌ Erreur lors du build:")
        print(result.stdout)
        print(result.stderr)
        return False


def create_readme():
    """Crée un README dans le dossier dist"""
    readme_content = """# Curio - Gestionnaire de Prosits

## Installation

1. Copiez le dossier "Curio" où vous voulez sur votre ordinateur
2. Lancez l'exécutable "Curio.exe"

## Configuration et Logs

Les fichiers de configuration et logs sont stockés dans :
- **Windows**: `%APPDATA%\\Curio\\`
  - Configuration: `%APPDATA%\\Curio\\config.txt`
  - Logs: `%APPDATA%\\Curio\\logs\\`

- **macOS**:
  - Configuration: `~/Library/Application Support/Curio/`
  - Logs: `~/Library/Logs/Curio/`

- **Linux**:
  - Configuration: `~/.config/Curio/`
  - Logs: `~/.local/share/Curio/logs/`

## Désinstallation

1. Supprimez le dossier "Curio"
2. Si vous voulez supprimer les données utilisateur, supprimez le dossier mentionné ci-dessus

## Support

Pour toute question ou bug, contactez Robin NOIRET
"""

    dist_folder = Path("dist/Curio")
    if dist_folder.exists():
        readme_path = dist_folder / "README.txt"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"✓ README créé: {readme_path}")


def main():
    """Point d'entrée principal"""
    print("=" * 60)
    print("🚀 Build de Curio")
    print("=" * 60)

    # Vérifier PyInstaller
    if not check_pyinstaller():
        return 1

    # Nettoyer
    clean_build_folders()

    # Build
    if not build_executable():
        return 1

    # Créer README
    create_readme()

    print("\n" + "=" * 60)
    print("✨ Build terminé avec succès!")
    print("=" * 60)
    print("\n💡 Vous pouvez maintenant distribuer le dossier dist/Curio/")

    return 0


if __name__ == "__main__":
    sys.exit(main())
