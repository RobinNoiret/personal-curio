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
            os.path.dirname(__file__), '..', 'assets', 'curio_basic.png'
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
            width=280,  # Largeur augmentée pour la nouvelle layout
            fg_color=COLORS['navbar_bg'],
            border_width=0
        )
        self.sidebar.pack(side='left', fill='y', padx=0, pady=0)
        self.sidebar.pack_propagate(False)

        # Logo en haut
        self._create_logo()

        # Boutons de navigation
        self._create_nav_buttons()

        # Spacer pour pousser les boutons du bas
        spacer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        spacer.pack(fill='both', expand=True)

        # Boutons en bas de la sidebar
        self._create_bottom_buttons()

    def _create_logo(self):
        """Crée le logo en haut de la sidebar"""
        # Frame pour le logo avec fond jaune
        logo_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color=COLORS['yellow'],
            height=90,
            corner_radius=8
        )
        logo_frame.pack(fill='x', pady=20, padx=20)
        logo_frame.pack_propagate(False)

        # Conteneur pour l'icône et le texte
        content_frame = ctk.CTkFrame(logo_frame, fg_color="transparent")
        content_frame.pack(expand=True, fill='both', padx=15, pady=15)

        try:
            # Icône Curio
            logo_image = ctk.CTkImage(
                light_image=Image.open(self.logo_path),
                dark_image=Image.open(self.logo_path),
                size=(40, 40)
            )
            logo_label = ctk.CTkLabel(
                content_frame,
                text="",
                image=logo_image
            )
            logo_label.pack(side='left', padx=(0, 10))
        except Exception as e:
            print(f"Erreur lors du chargement du logo: {e}")

        # Texte "Curio"
        text_label = ctk.CTkLabel(
            content_frame,
            text="Curio",
            font=("Arial", 16, "bold"),
            text_color=COLORS['black'],
            anchor='w'
        )
        text_label.pack(side='left', fill='x', expand=True)

        # Rendre le logo cliquable
        logo_frame.bind("<Button-1>", lambda e: self.navigate_to('home'))
        content_frame.bind("<Button-1>", lambda e: self.navigate_to('home'))
        if 'logo_label' in locals():
            logo_label.bind("<Button-1>", lambda e: self.navigate_to('home'))
        text_label.bind("<Button-1>", lambda e: self.navigate_to('home'))

    def _create_nav_buttons(self):
        """Crée les boutons de navigation"""
        for key, icon, text in NAV_ITEMS:
            # Frame conteneur pour chaque segment
            segment = ctk.CTkFrame(
                self.sidebar,
                fg_color=COLORS['navbar_bg'],
                height=NAV_BUTTON_HEIGHT,
                corner_radius=0
            )
            segment.pack(fill='x', pady=0, padx=0)
            segment.pack_propagate(False)

            # Créer un conteneur interne pour l'icône et le texte
            inner_frame = ctk.CTkFrame(segment, fg_color="transparent")
            inner_frame.pack(expand=True, fill='both', padx=10, pady=10)

            # Icône à gauche
            icon_label = ctk.CTkLabel(
                inner_frame,
                text=icon,
                font=("Arial", 24),
                text_color=COLORS['text_gray']
            )
            icon_label.pack(side='left', padx=(5, 10))

            # Texte à droite
            text_label = ctk.CTkLabel(
                inner_frame,
                text=text,
                font=("Arial", 14),
                text_color=COLORS['text_gray'],
                anchor='w'
            )
            text_label.pack(side='left', fill='x', expand=True)

            # Rendre le segment cliquable
            command = self._get_command(key)
            if command:
                segment.bind("<Button-1>", lambda e, cmd=command: cmd())
                inner_frame.bind("<Button-1>", lambda e, cmd=command: cmd())
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

    def _create_bottom_buttons(self):
        """Crée les boutons en bas de la sidebar"""
        bottom_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom_frame.pack(pady=20, padx=20)

        # Conteneur pour les 3 boutons
        buttons_container = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        buttons_container.pack()

        # Créer les labels au lieu de boutons pour un meilleur contrôle du hover
        # Bouton Settings (⚙)
        settings_frame = ctk.CTkFrame(buttons_container, fg_color="transparent", width=50, height=50)
        settings_frame.pack(side='left', padx=5)
        settings_frame.pack_propagate(False)

        settings_label = ctk.CTkLabel(
            settings_frame,
            text="⚙",
            font=("Arial", 20),
            text_color=COLORS['text_gray'],
            cursor="hand2"
        )
        settings_label.place(relx=0.5, rely=0.5, anchor='center')
        settings_label.bind("<Button-1>", lambda e: self.navigate_to('settings'))
        settings_label.bind("<Enter>", lambda e: self._on_icon_hover(settings_label, settings_frame, True))
        settings_label.bind("<Leave>", lambda e: self._on_icon_hover(settings_label, settings_frame, False))

        # Bouton Logs (📋)
        logs_frame = ctk.CTkFrame(buttons_container, fg_color="transparent", width=50, height=50)
        logs_frame.pack(side='left', padx=5)
        logs_frame.pack_propagate(False)

        logs_label = ctk.CTkLabel(
            logs_frame,
            text="📋",
            font=("Arial", 20),
            text_color=COLORS['text_gray'],
            cursor="hand2"
        )
        logs_label.place(relx=0.5, rely=0.5, anchor='center')
        logs_label.bind("<Button-1>", lambda e: self.navigate_to('logs'))
        logs_label.bind("<Enter>", lambda e: self._on_icon_hover(logs_label, logs_frame, True))
        logs_label.bind("<Leave>", lambda e: self._on_icon_hover(logs_label, logs_frame, False))

        # Bouton Info (ℹ)
        info_frame = ctk.CTkFrame(buttons_container, fg_color="transparent", width=50, height=50)
        info_frame.pack(side='left', padx=5)
        info_frame.pack_propagate(False)

        info_label = ctk.CTkLabel(
            info_frame,
            text="ℹ",
            font=("Arial", 20, "bold"),
            text_color=COLORS['text_gray'],
            cursor="hand2"
        )
        info_label.place(relx=0.5, rely=0.5, anchor='center')
        info_label.bind("<Button-1>", lambda e: self.navigate_to('info'))
        info_label.bind("<Enter>", lambda e: self._on_icon_hover(info_label, info_frame, True))
        info_label.bind("<Leave>", lambda e: self._on_icon_hover(info_label, info_frame, False))

    def _on_icon_hover(self, label, frame, is_entering):
        """Gère l'effet de hover sur les icônes (remontée)"""
        if is_entering:
            # Remonte l'icône de 3 pixels
            label.place(relx=0.5, rely=0.4, anchor='center')
        else:
            # Remet l'icône à sa position normale
            label.place(relx=0.5, rely=0.5, anchor='center')

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
                # Inactif - fond navbar
                segment.configure(fg_color=COLORS['navbar_bg'])
                if key in self.nav_labels:
                    self.nav_labels[key]['icon'].configure(text_color=COLORS['text_gray'])
                    self.nav_labels[key]['text'].configure(text_color=COLORS['text_gray'])
