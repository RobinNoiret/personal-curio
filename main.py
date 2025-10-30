"""
Point d'entrée principal de l'application Prosit Manager
"""
import sys
import os

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.gui import PrositManagerGUI


def main():
    """Lance l'application"""
    app = PrositManagerGUI()
    app.run()


if __name__ == "__main__":
    main()
