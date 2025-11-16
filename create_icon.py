"""
Script pour créer un fichier .ico optimisé à partir d'un PNG
Tailles standard pour Windows : 16x16, 32x32, 48x48, 256x256
"""
from PIL import Image
import os

def create_optimized_ico(png_path, ico_path):
    """
    Crée un fichier .ico optimisé avec les tailles standards Windows

    Args:
        png_path: Chemin vers le fichier PNG source
        ico_path: Chemin vers le fichier .ico de sortie
    """
    print(f"📸 Ouverture de {png_path}...")

    # Ouvrir l'image PNG
    img = Image.open(png_path)

    # Convertir en RGBA si nécessaire (pour la transparence)
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    print(f"   ✓ Image chargée : {img.size[0]}x{img.size[1]} pixels")

    # Tailles standard Windows (du plus petit au plus grand)
    sizes = [
        (16, 16),   # Petites icônes (barre des tâches)
        (32, 32),   # Icônes moyennes
        (48, 48),   # Icônes normales
        (256, 256), # Grandes icônes (Windows 7+)
    ]

    print(f"\n🔧 Création des tailles d'icône...")
    for size in sizes:
        print(f"   • {size[0]}x{size[1]}")

    # Sauvegarder au format ICO avec toutes les tailles
    print(f"\n💾 Sauvegarde de {ico_path}...")
    img.save(ico_path, format='ICO', sizes=sizes)

    # Vérifier la taille du fichier créé
    file_size = os.path.getsize(ico_path)
    file_size_kb = file_size / 1024

    print(f"\n✅ Fichier créé avec succès !")
    print(f"   Taille : {file_size_kb:.1f} KB")

    if file_size_kb > 50:
        print(f"   ⚠️  Attention : Le fichier est un peu gros ({file_size_kb:.1f} KB)")
        print(f"       Idéalement < 50 KB pour PyInstaller")
    else:
        print(f"   ✓ Taille optimale pour PyInstaller")

    return ico_path


def main():
    """Point d'entrée principal"""
    print("=" * 60)
    print("🎨 Création d'icône optimisée pour Curio")
    print("=" * 60)
    print()

    # Chemins
    assets_dir = os.path.join(os.path.dirname(__file__), 'assets')

    # Chercher le PNG blanc/logo principal
    # Vous pouvez modifier ce chemin selon votre fichier source
    possible_sources = [
        'curio_white.png',      # Logo simple
    ]

    png_source = None
    for source in possible_sources:
        path = os.path.join(assets_dir, source)
        if os.path.exists(path):
            png_source = path
            break

    if not png_source:
        print("❌ Aucun fichier PNG source trouvé dans assets/")
        print(f"   Fichiers recherchés : {', '.join(possible_sources)}")
        return 1

    print(f"📁 Fichier source : {os.path.basename(png_source)}")

    # Créer le fichier ICO optimisé
    ico_output = os.path.join(assets_dir, 'Curio_optimized.ico')

    try:
        create_optimized_ico(png_source, ico_output)

        print("\n" + "=" * 60)
        print("✨ Terminé !")
        print("=" * 60)
        print(f"\n📝 Prochaines étapes :")
        print(f"   1. Vérifier que {os.path.basename(ico_output)} a la bonne apparence")
        print(f"   2. Renommer l'ancien Curio.ico en Curio_old.ico")
        print(f"   3. Renommer Curio_optimized.ico en Curio.ico")
        print(f"   4. Relancer le build : python build.py")

        return 0

    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
