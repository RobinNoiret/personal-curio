"""
Interface graphique refactorisée pour le gestionnaire de prosits
"""
import customtkinter as ctk
from typing import Dict
from .constants import COLORS, WINDOW_SIZE
from .utils import ConfigManager, CRParser, DocxGenerator, get_logger
from .navigation import NavigationSidebar
from .pages import HomePage, PrositPage, SettingsPage, LogsPage, ObsidianPage, InfoPage, NoteViewerPage


class PrositManagerGUI:
    """Interface graphique principale de l'application - Version refactorisée"""

    def __init__(self):
        # Initialiser le logger
        self.logger = get_logger()
        self.logger.info("Démarrage de l'application Curio", "GUI")

        # Configuration du thème
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Fenêtre principale
        self.root = ctk.CTk()
        self.root.title("Curio")
        self.root.geometry(WINDOW_SIZE)
        self.root.configure(fg_color=COLORS['white'])

        # Définir une taille minimale pour éviter que l'interface ne soit trop compressée
        self.root.minsize(1000, 700)  # Largeur min 1000px, hauteur min 700px

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
        self.note_viewer_data = None  # Pour stocker les données de la note à afficher

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

        # Zone de contenu principale (sans header, les boutons sont dans la sidebar)
        self.content_frame = ctk.CTkFrame(right_container, fg_color=COLORS['white'])
        self.content_frame.pack(fill='both', expand=True, padx=0, pady=0)

    def navigate_to(self, page_name: str, **kwargs):
        """Navigate vers une page avec paramètres optionnels"""
        # Éviter la récursion si c'est déjà la page actuelle
        if self.current_page == page_name and page_name != 'note_viewer':
            return

        self.logger.debug(f"Navigation vers la page: {page_name}", "GUI")

        # Stocker les données pour note_viewer si nécessaire
        if page_name == 'note_viewer' and 'note_data' in kwargs:
            self.note_viewer_data = kwargs['note_data']

        # Nettoyer la page actuelle
        self._clear_content()

        # Mettre à jour la navigation visuelle (sans callback)
        # Ne pas highlight les pages non-navigation (settings, logs, info)
        if page_name not in ['settings', 'logs', 'info']:
            self.navigation._highlight_button(page_name)

        # Créer et afficher la nouvelle page
        if page_name == 'home':
            page = HomePage(self.content_frame, COLORS, config=self.config, on_navigate=self.navigate_to)
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
                self.config_manager, self.app_info,
                on_config_saved=self._on_config_saved
            )
        elif page_name == 'logs':
            page = LogsPage(self.content_frame, COLORS)
        elif page_name == 'info':
            page = InfoPage(
                self.content_frame, COLORS,
                self.app_info
            )
        elif page_name == 'note_viewer':
            if self.note_viewer_data:
                page = NoteViewerPage(
                    self.content_frame, COLORS,
                    note_name=self.note_viewer_data['note_name'],
                    notes_path=self.note_viewer_data['notes_path'],
                    on_navigate=self.navigate_to
                )
            else:
                # Pas de données, retour à home
                self.navigate_to('home')
                return
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

    def _on_config_saved(self):
        """Callback appelé après la sauvegarde de la configuration"""
        self.logger.info("Configuration sauvegardée, rechargement...", "GUI")
        # Recharger la config
        self.config = self.config_manager.load_config()

        # Retourner automatiquement à la page d'accueil pour voir les changements
        self.navigate_to('home')

    def run(self):
        """Lance l'application"""
        self.root.mainloop()
