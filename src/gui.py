"""
Interface graphique refactorisée pour le gestionnaire de prosits
"""
import customtkinter as ctk
from typing import Dict
from .constants import COLORS, WINDOW_SIZE
from .utils import ConfigManager, CRParser, DocxGenerator, get_logger
from .navigation import NavigationSidebar
from .pages import HomePage, PrositPage, SettingsPage, LogsPage, ObsidianPage


class PrositManagerGUI:
    """Interface graphique principale de l'application - Version refactorisée"""

    def __init__(self):
        # Initialiser le logger
        self.logger = get_logger()
        self.logger.info("Démarrage de l'application Prosit Manager", "GUI")

        # Configuration du thème
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Fenêtre principale
        self.root = ctk.CTk()
        self.root.title("Prosit Manager")
        self.root.geometry(WINDOW_SIZE)
        self.root.configure(fg_color=COLORS['white'])

        # Gestionnaires
        self.logger.debug("Initialisation des gestionnaires", "GUI")
        self.config_manager = ConfigManager()
        self.parser = CRParser()
        self.generator = DocxGenerator()

        # Chargement des configs
        self.logger.debug("Chargement de la configuration", "GUI")
        self.config = self.config_manager.load_config()
        self.app_info = self.config_manager.load_app_info()

        # État
        self.current_page = None
        self.current_page_obj = None

        # Créer la structure principale
        self.logger.debug("Création de l'interface", "GUI")
        self._create_main_layout()

        # Afficher la page d'accueil
        self.logger.info("Interface principale créée avec succès", "GUI")
        self.navigate_to('home')

    def _create_main_layout(self):
        """Crée la structure principale"""
        # Container principal
        main_container = ctk.CTkFrame(self.root, fg_color=COLORS['white'])
        main_container.pack(fill='both', expand=True)

        # Sidebar de navigation
        self.navigation = NavigationSidebar(
            main_container,
            on_navigate=self.navigate_to
        )

        # Zone de contenu à droite
        right_container = ctk.CTkFrame(main_container, fg_color=COLORS['white'])
        right_container.pack(side='right', fill='both', expand=True)

        # Header en haut à droite
        self._create_header(right_container)

        # Zone de contenu principale
        self.content_frame = ctk.CTkFrame(right_container, fg_color=COLORS['white'])
        self.content_frame.pack(fill='both', expand=True, padx=0, pady=0)

    def _create_header(self, parent):
        """Crée le header avec les boutons settings et legal"""
        header = ctk.CTkFrame(parent, height=80, fg_color=COLORS['white'])
        header.pack(fill='x', padx=0, pady=0)
        header.pack_propagate(False)

        # Container pour les boutons à droite
        header_buttons = ctk.CTkFrame(header, fg_color="transparent")
        header_buttons.pack(side='right', padx=30, pady=20)

        # Bouton Logs
        logs_btn = ctk.CTkButton(
            header_buttons,
            text="logs",
            font=("Arial", 13),
            fg_color=COLORS['white'],
            text_color=COLORS['text_gray'],
            hover_color=COLORS['gray'],
            border_width=1,
            border_color=COLORS['border'],
            command=lambda: self.navigate_to('logs'),
            width=120,
            height=40,
            corner_radius=8
        )
        logs_btn.pack(side='left', padx=5)

        # Bouton Settings
        settings_btn = ctk.CTkButton(
            header_buttons,
            text="⚙",
            font=("Arial", 20),
            fg_color=COLORS['white'],
            text_color=COLORS['text_gray'],
            hover_color=COLORS['gray'],
            border_width=1,
            border_color=COLORS['border'],
            command=lambda: self.navigate_to('settings'),
            width=50,
            height=40,
            corner_radius=8
        )
        settings_btn.pack(side='left', padx=5)

        # Ligne de séparation
        separator = ctk.CTkFrame(parent, height=1, fg_color=COLORS['border'])
        separator.pack(fill='x')

    def navigate_to(self, page_name: str):
        """Navigate vers une page"""
        # Éviter la récursion si c'est déjà la page actuelle
        if self.current_page == page_name:
            return

        self.logger.debug(f"Navigation vers la page: {page_name}", "GUI")

        # Nettoyer la page actuelle
        self._clear_content()

        # Mettre à jour la navigation visuelle (sans callback)
        if page_name not in ['settings', 'logs']:  # Settings et logs sont gérés par le header
            self.navigation._highlight_button(page_name)

        # Créer et afficher la nouvelle page
        if page_name == 'home':
            page = HomePage(self.content_frame, COLORS, on_navigate=self.navigate_to)
        elif page_name == 'prosit':
            page = PrositPage(
                self.content_frame, COLORS,
                self.parser, self.generator, self.config
            )
        elif page_name == 'obsidian':
            page = ObsidianPage(
                self.content_frame, COLORS,
                self.config
            )
        elif page_name == 'settings':
            page = SettingsPage(
                self.content_frame, COLORS,
                self.config_manager, self.app_info
            )
        elif page_name == 'logs':
            page = LogsPage(self.content_frame, COLORS)
        else:
            # Page non trouvée, revenir à home
            self.navigate_to('home')
            return

        # Rendre la page
        page.render()

        # Sauvegarder la référence
        self.current_page = page_name
        self.current_page_obj = page

    def _clear_content(self):
        """Efface le contenu actuel"""
        if self.current_page_obj:
            self.current_page_obj.clear()
            self.current_page_obj = None

        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def run(self):
        """Lance l'application"""
        self.root.mainloop()
