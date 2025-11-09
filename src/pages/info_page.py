"""
Page d'informations sur l'application
"""
import customtkinter as ctk
import os
from PIL import Image
from .base_page import BasePage
from ..ui_components import Label, Container, Spacer
from ..constants import FONTS


class InfoPage(BasePage):
    """Page d'informations de l'application"""

    def __init__(self, parent, colors, app_info=None):
        """Initialise la page d'informations avec les infos de l'app"""
        super().__init__(parent, colors)
        self.app_info = app_info or {}

    def render(self) -> ctk.CTkFrame:
        """Rend la page d'informations"""
        # Container principal
        self.container = ctk.CTkFrame(self.parent, fg_color=self.colors['white'])
        self.container.pack(fill='both', expand=True, padx=60, pady=60)

        # Centrer le contenu
        center_frame = Container.transparent(self.container)
        center_frame.place(relx=0.5, rely=0.5, anchor='center')

        # Logo Curio en haut
        try:
            curio_path = os.path.join(
                os.path.dirname(__file__), '..', '..', 'assets', 'curio_basic.png'
            )
            curio_image = ctk.CTkImage(
                light_image=Image.open(curio_path),
                dark_image=Image.open(curio_path),
                size=(120, 120)
            )
            curio_label = ctk.CTkLabel(
                center_frame,
                text="",
                image=curio_image
            )
            curio_label.pack(pady=(0, 30))
        except Exception as e:
            print(f"Erreur lors du chargement de Curio: {e}")

        # Nom de l'application
        app_name = self.app_info.get('name', 'Curio')
        ctk.CTkLabel(
            center_frame,
            text=app_name,
            font=("Arial", 48, "bold"),
            text_color=self.colors['black']
        ).pack(pady=(0, 10))

        # Version
        version = self.app_info.get('version', '2.0.0')
        ctk.CTkLabel(
            center_frame,
            text=f"Version {version}",
            font=("Arial", 20),
            text_color=self.colors['text_gray']
        ).pack(pady=(0, 30))

        # Séparateur
        separator = ctk.CTkFrame(
            center_frame,
            height=1,
            width=400,
            fg_color=self.colors['border']
        )
        separator.pack(pady=20)

        # Description
        description = self.app_info.get('description', 'Gestionnaire de prosits avec analyse et génération automatique')
        ctk.CTkLabel(
            center_frame,
            text=description,
            font=("Arial", 16),
            text_color=self.colors['text_gray'],
            wraplength=500
        ).pack(pady=(0, 20))

        # Auteur
        author = self.app_info.get('author', 'NOIRET Robin')
        ctk.CTkLabel(
            center_frame,
            text=f"Développé par {author}",
            font=("Arial", 14, "bold"),
            text_color=self.colors['black']
        ).pack(pady=(20, 5))

        # Copyright
        ctk.CTkLabel(
            center_frame,
            text="© 2025 - Tous droits réservés",
            font=("Arial", 12),
            text_color=self.colors['text_gray']
        ).pack(pady=(0, 0))

        return self.container
