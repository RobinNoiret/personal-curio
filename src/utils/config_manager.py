"""
Gestionnaire de configuration pour l'application
"""
import os
from typing import Dict


class ConfigManager:
    """Gère le chargement et la sauvegarde de la configuration"""

    def __init__(self, config_file: str = 'config.txt', app_info_file: str = 'app_info.txt'):
        # Base dir est maintenant 2 niveaux au-dessus (utils -> src -> root)
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.config_path = os.path.join(self.base_dir, config_file)
        self.app_info_path = os.path.join(self.base_dir, app_info_file)

        # Configuration par défaut
        self.default_config = {
            'prenom': '',
            'nom': '',
            'email': '',
            'formation': '',
            'template_path': '',
            'obsidian_vault_path': '',
            'obsidian_default_folder': 'Imports'
        }

        # Info de l'application par défaut
        self.default_app_info = {
            'name': 'Prosit Manager',
            'version': '1.0.0',
            'author': 'NOIRET Robin',
            'description': 'Gestionnaire de prosits avec analyse et génération automatique'
        }

    def load_config(self) -> Dict[str, str]:
        """Charge la configuration depuis le fichier"""
        config = self.default_config.copy()

        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            if key in config:
                                config[key] = value
        except Exception as e:
            print(f"Erreur lors du chargement de la config: {e}")

        return config

    def save_config(self, config: Dict[str, str]) -> bool:
        """Sauvegarde la configuration dans le fichier"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                for key, value in config.items():
                    if key in self.default_config:  # Ne sauvegarder que les clés valides
                        f.write(f"{key}={value}\n")
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la config: {e}")
            return False

    def load_app_info(self) -> Dict[str, str]:
        """Charge les informations de l'application"""
        app_info = self.default_app_info.copy()

        try:
            if os.path.exists(self.app_info_path):
                with open(self.app_info_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            if key in app_info:
                                app_info[key] = value
        except Exception as e:
            print(f"Erreur lors du chargement des infos de l'app: {e}")

        return app_info
