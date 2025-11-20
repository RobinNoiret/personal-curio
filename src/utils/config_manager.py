"""
Gestionnaire de configuration pour l'application
"""
import os
import sys
from typing import Dict
from pathlib import Path


class ConfigManager:
    """Gère le chargement et la sauvegarde de la configuration"""

    def __init__(self, config_file: str = 'config.txt', app_info_file: str = 'app_info.txt'):
        # Déterminer le dossier de configuration approprié selon l'OS
        self.app_name = 'Curio'
        self.config_dir = self._get_config_dir()

        # Créer le dossier de configuration s'il n'existe pas
        os.makedirs(self.config_dir, exist_ok=True)

        self.config_path = os.path.join(self.config_dir, config_file)
        self.app_info_path = os.path.join(self.config_dir, app_info_file)

        # Pour rétrocompatibilité : essayer de migrer l'ancienne config si elle existe
        self._migrate_old_config(config_file, app_info_file)

    def _get_config_dir(self) -> str:
        """
        Retourne le dossier de configuration approprié selon l'OS
        - Windows: %APPDATA%/Curio
        - macOS: ~/Library/Application Support/Curio
        - Linux: ~/.config/Curio
        """
        if sys.platform == 'win32':
            # Windows: utiliser APPDATA
            base = os.environ.get('APPDATA', os.path.expanduser('~'))
            return os.path.join(base, self.app_name)
        elif sys.platform == 'darwin':
            # macOS: utiliser ~/Library/Application Support
            return os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', self.app_name)
        else:
            # Linux et autres: utiliser ~/.config
            return os.path.join(os.path.expanduser('~'), '.config', self.app_name)

    def _migrate_old_config(self, config_file: str, app_info_file: str):
        """Migre l'ancienne configuration si elle existe dans le dossier de développement"""
        # Essayer de trouver l'ancien dossier (2 niveaux au-dessus)
        try:
            old_base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            old_config_path = os.path.join(old_base_dir, config_file)
            old_app_info_path = os.path.join(old_base_dir, app_info_file)

            # Migrer config.txt si l'ancien existe et le nouveau n'existe pas
            if os.path.exists(old_config_path) and not os.path.exists(self.config_path):
                import shutil
                shutil.copy2(old_config_path, self.config_path)
                print(f"Configuration migrée vers {self.config_path}")

            # Migrer app_info.txt
            if os.path.exists(old_app_info_path) and not os.path.exists(self.app_info_path):
                import shutil
                shutil.copy2(old_app_info_path, self.app_info_path)
                print(f"App info migré vers {self.app_info_path}")
        except Exception as e:
            # Ignorer les erreurs de migration (normal en production)
            pass

        # Configuration par défaut
        self.default_config = {
            'prenom': 'Robin',  # Prénom par défaut
            'nom': '',
            'email': '',
            'formation': '',
            'template_path': '',
            'obsidian_export_path': '',
            'home_message_mode': 'Phrase fixe',  # Mode du message d'accueil
            'obsidian_home_notes_path': '',  # Dossier pour les notes de la page d'accueil
            'obsidian_vault_path': ''  # Chemin vers le vault Obsidian (pour le dashboard)
        }

        # Info de l'application par défaut
        self.default_app_info = {
            'name': 'Curio',
            'version': '2.0.0',
            'author': 'NOIRET Robin',
            'description': 'Gestionnaire de prosits avec analyse et génération automatique'
        }

    def load_config(self) -> Dict[str, str]:
        """Charge la configuration depuis le fichier"""
        config = self.default_config.copy()
        loaded_data = {}

        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            loaded_data[key] = value
                            if key in config:
                                config[key] = value

                # Migration: Si on a les anciennes clés mais pas la nouvelle
                if 'obsidian_vault_path' in loaded_data and 'obsidian_export_path' not in loaded_data:
                    vault_path = loaded_data.get('obsidian_vault_path', '')
                    default_folder = loaded_data.get('obsidian_default_folder', '')
                    if vault_path:
                        # Combiner vault_path et default_folder
                        config['obsidian_export_path'] = os.path.join(vault_path, default_folder).replace('\\', '/')
                        print(f"Migration de la config: obsidian_export_path = {config['obsidian_export_path']}")
                        # Sauvegarder automatiquement la migration
                        self.save_config(config)

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
