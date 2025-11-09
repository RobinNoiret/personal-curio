"""
Page d'accueil
"""
import customtkinter as ctk
import os
from PIL import Image
from .base_page import BasePage
from ..ui_components import Button, Label, Container, Spacer
from ..constants import FONTS


class HomePage(BasePage):
    """Page d'accueil de l'application"""

    def __init__(self, parent, colors, config=None, on_navigate=None):
        """Initialise la page d'accueil avec la config pour récupérer le prénom"""
        super().__init__(parent, colors, on_navigate)
        self.config = config or {}

    def render(self) -> ctk.CTkFrame:
        """Rend la page d'accueil"""
        # Container principal
        self.container = ctk.CTkFrame(self.parent, fg_color=self.colors['white'])
        self.container.pack(fill='both', expand=True)

        # Centrer le contenu verticalement et horizontalement
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
                size=(150, 150)
            )
            curio_label = ctk.CTkLabel(
                center_frame,
                text="",
                image=curio_image
            )
            curio_label.pack(pady=(0, 40))
        except Exception as e:
            print(f"Erreur lors du chargement de Curio: {e}")

        # Titre avec formatage selon la maquette
        # "Hey [Prénom]," en noir normal, reste en gras
        # Récupérer le prénom depuis la config
        prenom = self.config.get('prenom', 'Toi')

        title_frame = Container.transparent(center_frame)
        title_frame.pack(pady=0)

        # Première ligne: "Hey [Prénom], lorem ipsum"
        line1_frame = Container.transparent(title_frame)
        line1_frame.pack()

        ctk.CTkLabel(
            line1_frame,
            text="Hey ",
            font=("Arial", 48),
            text_color=self.colors['black']
        ).pack(side='left')

        ctk.CTkLabel(
            line1_frame,
            text=prenom,
            font=("Arial", 48, "underline"),
            text_color=self.colors['black']
        ).pack(side='left')

        ctk.CTkLabel(
            line1_frame,
            text=", lorem ipsum",
            font=("Arial", 48, "bold"),
            text_color=self.colors['black']
        ).pack(side='left')

        # Deuxième ligne: "ipsum de ipsum."
        ctk.CTkLabel(
            title_frame,
            text="ipsum de ipsum.",
            font=("Arial", 48, "bold"),
            text_color=self.colors['black']
        ).pack(pady=(5, 0))

        return self.container
