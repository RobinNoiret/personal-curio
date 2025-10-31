"""
Page d'accueil
"""
import customtkinter as ctk
from .base_page import BasePage
from ..ui_components import Button, Label, Container, Spacer
from ..constants import FONTS


class HomePage(BasePage):
    """Page d'accueil de l'application"""

    def render(self) -> ctk.CTkFrame:
        """Rend la page d'accueil"""
        # Container principal
        self.container = ctk.CTkFrame(self.parent, fg_color=self.colors['white'])
        self.container.pack(fill='both', expand=True)

        # Spacer pour centrer verticalement
        Spacer.vertical(self.container, 100)

        # Titre principal
        title_frame = Container.transparent(self.container)
        title_frame.pack(pady=20)

        Label.title(title_frame, "Gérez vos", size='large').pack()

        # Mot clé avec fond jaune
        title2_bg = ctk.CTkFrame(title_frame, fg_color=self.colors['yellow'], corner_radius=8)
        title2_bg.pack(pady=10)

        ctk.CTkLabel(
            title2_bg,
            text="Prosits",
            font=FONTS['title_large'],
            text_color=self.colors['black']
        ).pack(padx=30, pady=5)

        # Sous-titre
        Label.text(
            self.container,
            "Analysez, générez et organisez vos documents facilement",
            font=FONTS['subtitle']
        ).pack(pady=20)

        # Boutons d'action
        action_frame = Container.transparent(self.container)
        action_frame.pack(pady=40)

        # Bouton principal
        Button.secondary(
            action_frame,
            "Commencer →",
            lambda: self.on_navigate('prosit') if self.on_navigate else None,
            font=("Arial", 18, "bold"),
            width=200,
            height=55
        ).pack(side='left', padx=10)

        # Bouton secondaire
        Button.outline(
            action_frame,
            "Configurer",
            lambda: self.on_navigate('settings') if self.on_navigate else None,
            font=("Arial", 18),
            width=180,
            height=55
        ).pack(side='left', padx=10)

        return self.container
