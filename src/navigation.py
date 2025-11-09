"""
Composant de navigation
"""
import customtkinter as ctk
import os
from typing import Dict, Callable
from PIL import Image
from .constants import COLORS, SIDEBAR_WIDTH, LOGO_SIZE, NAV_BUTTON_HEIGHT, NAV_ITEMS, FONTS


class NavigationSidebar:
    """Barre de navigation latérale"""

    def __init__(self, parent, on_navigate: Callable, logo_path: str = None):
        """
        Args:
            parent: Widget parent
            on_navigate: Callback appelé lors de la navigation (page_name)
            logo_path: Chemin vers le logo
        """
        self.parent = parent
        self.on_navigate = on_navigate
        self.logo_path = logo_path or os.path.join(
            os.path.dirname(__file__), '..', 'assets', 'logo_black_version.png'
        )

        # État
        self.nav_buttons = {}
        self.nav_labels = {}
        self.current_page = 'home'

        # Créer la sidebar
        self.sidebar = None
        self._create_sidebar()

    def _create_sidebar(self):
        """Crée la barre de navigation"""
        self.sidebar = ctk.CTkFrame(
            self.parent,
            width=SIDEBAR_WIDTH,
            fg_color=COLORS['gray'],
            border_width=0
        )
        self.sidebar.pack(side='left', fill='y', padx=0, pady=0)
        self.sidebar.pack_propagate(False)

        # Logo en haut
        self._create_logo()

        # Boutons de navigation
        self._create_nav_buttons()

    def _create_logo(self):
        """Crée le logo en haut de la sidebar"""
        try:
            logo_image = ctk.CTkImage(
                light_image=Image.open(self.logo_path),
                dark_image=Image.open(self.logo_path),
                size=(60, 60)
            )
            logo_btn = ctk.CTkButton(
                self.sidebar,
                text="",
                image=logo_image,
                fg_color=COLORS['yellow'],
                hover_color="#FFD700",
                width=SIDEBAR_WIDTH,
                height=LOGO_SIZE,
                corner_radius=0,
                command=lambda: self.navigate_to('home')
            )
        except Exception as e:
            print(f"Erreur lors du chargement du logo: {e}")
            # Fallback
            logo_btn = ctk.CTkButton(
                self.sidebar,
                text="/",
                font=("Arial", 40, "bold"),
                fg_color=COLORS['yellow'],
                text_color=COLORS['black'],
                hover_color="#FFD700",
                width=SIDEBAR_WIDTH,
                height=LOGO_SIZE,
                corner_radius=0,
                command=lambda: self.navigate_to('home')
            )

        logo_btn.pack(fill='x', pady=(0, 0), padx=0)

    def _create_nav_buttons(self):
        """Crée les boutons de navigation"""
        for key, icon, text in NAV_ITEMS:
            # Frame conteneur pour chaque segment
            segment = ctk.CTkFrame(
                self.sidebar,
                fg_color=COLORS['gray'],
                height=NAV_BUTTON_HEIGHT,
                corner_radius=0
            )
            segment.pack(fill='x', pady=0, padx=0)
            segment.pack_propagate(False)

            # Icône grande
            icon_label = ctk.CTkLabel(
                segment,
                text=icon,
                font=FONTS['icon_large'],
                text_color=COLORS['text_gray']
            )
            icon_label.pack(pady=(15, 2))

            # Texte petit
            text_label = ctk.CTkLabel(
                segment,
                text=text,
                font=("Arial", 7),
                text_color=COLORS['text_gray']
            )
            text_label.pack(pady=(0, 5))

            # Rendre le segment cliquable
            command = self._get_command(key)
            if command:
                segment.bind("<Button-1>", lambda e, cmd=command: cmd())
                icon_label.bind("<Button-1>", lambda e, cmd=command: cmd())
                text_label.bind("<Button-1>", lambda e, cmd=command: cmd())

            self.nav_buttons[key] = segment
            self.nav_labels[key] = {'icon': icon_label, 'text': text_label}

    def _get_command(self, key: str) -> Callable:
        """Retourne la commande pour un bouton"""
        if key == 'prosit':
            return lambda: self.navigate_to('prosit')
        elif key == 'obsidian':
            return lambda: self.navigate_to('obsidian')
        # Pour l'instant, les autres sont désactivés
        return None

    def navigate_to(self, page_name: str):
        """Navigate vers une page"""
        self.current_page = page_name
        self._highlight_button(page_name)
        if self.on_navigate:
            self.on_navigate(page_name)

    def _highlight_button(self, page_name: str):
        """Met en surbrillance le bouton actif"""
        for key in self.nav_buttons.keys():
            segment = self.nav_buttons[key]

            if key == page_name:
                # Actif - jaune
                segment.configure(fg_color=COLORS['yellow'])
                if key in self.nav_labels:
                    self.nav_labels[key]['icon'].configure(text_color=COLORS['black'])
                    self.nav_labels[key]['text'].configure(text_color=COLORS['black'])
            else:
                # Inactif - gris
                segment.configure(fg_color=COLORS['gray'])
                if key in self.nav_labels:
                    self.nav_labels[key]['icon'].configure(text_color=COLORS['text_gray'])
                    self.nav_labels[key]['text'].configure(text_color=COLORS['text_gray'])
