"""
Page d'accueil
"""
import customtkinter as ctk
import os
from PIL import Image
from .base_page import BasePage
from ..ui_components import Container
from ..utils.home_messages import get_fixed_message, get_random_quote, get_note_reminder
from ..utils.obsidian_scanner import ObsidianVaultScanner


class HomePage(BasePage):
    """Page d'accueil de l'application"""

    def __init__(self, parent, colors, config=None, on_navigate=None):
        """Initialise la page d'accueil avec la config pour récupérer le prénom"""
        super().__init__(parent, colors, on_navigate)
        self.config = config or {}
        self.current_note_name = None  # Pour stocker le nom de la note affichée
        self.current_notes_path = None  # Pour stocker le chemin du dossier
        self.note_content_frame = None  # Frame pour afficher le contenu

    def _get_message_lines(self) -> tuple:
        """
        Récupère les lignes du message selon le mode configuré

        Returns:
            Tuple (ligne1_suite, ligne2) - la suite de "Hey [Prénom]," et la deuxième ligne
        """
        mode = self.config.get('home_message_mode', 'Phrase fixe')

        if mode == "Citation aléatoire":
            self.current_note_name = None  # Pas de note pour les citations
            return get_random_quote()
        elif mode == "Rappel de note (depuis Obsidian)":
            # Essayer de récupérer une note aléatoire depuis le dossier configuré
            notes_path = self.config.get('obsidian_home_notes_path', '')

            # Si pas de dossier spécifique configuré, fallback sur le dossier d'export
            if not notes_path:
                notes_path = self.config.get('obsidian_export_path', '')

            if notes_path and os.path.exists(notes_path):
                # Scanner directement le dossier configuré
                scanner = ObsidianVaultScanner(notes_path)
                scanner.scan_notes(notes_path)
                random_note = scanner.get_random_note()
                if random_note:
                    # Stocker la note et le chemin pour pouvoir afficher le contenu
                    self.current_note_name = random_note
                    self.current_notes_path = notes_path
                    return get_note_reminder(random_note)

            # Si pas de note trouvée, fallback sur phrase fixe
            self.current_note_name = None
            return get_fixed_message()
        else:  # "Phrase fixe" par défaut
            self.current_note_name = None
            return get_fixed_message()

    def _find_vault_root(self, path: str) -> str:
        """Trouve le dossier racine du vault Obsidian en cherchant le dossier .obsidian"""
        if not path or not os.path.exists(path):
            return ''

        current = os.path.abspath(path)
        # Remonter jusqu'à trouver un dossier .obsidian ou atteindre la racine
        while current:
            obsidian_folder = os.path.join(current, '.obsidian')
            if os.path.exists(obsidian_folder) and os.path.isdir(obsidian_folder):
                return current
            parent = os.path.dirname(current)
            if parent == current:  # On a atteint la racine
                break
            current = parent

        # Si pas trouvé, retourner le chemin original
        return path

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

        # Récupérer le prénom et le message
        prenom = self.config.get('prenom', 'Toi')
        line1_suite, line2 = self._get_message_lines()

        title_frame = Container.transparent(center_frame)
        title_frame.pack(pady=0)

        # Première ligne: "Hey [Prénom], [message]"
        line1_frame = Container.transparent(title_frame)
        line1_frame.pack()

        ctk.CTkLabel(
            line1_frame,
            text="Hey ",
            font=("Degular Medium", 48),
            text_color=self.colors['black']
        ).pack(side='left')

        ctk.CTkLabel(
            line1_frame,
            text=prenom,
            font=("Degular Medium", 48, "underline"),
            text_color=self.colors['black']
        ).pack(side='left')

        ctk.CTkLabel(
            line1_frame,
            text=f", {line1_suite}",
            font=("Degular Semibold", 48),
            text_color=self.colors['black']
        ).pack(side='left')

        # Deuxième ligne
        ctk.CTkLabel(
            title_frame,
            text=line2,
            font=("Degular Semibold", 48),
            text_color=self.colors['black']
        ).pack(pady=(5, 0))

        # Si on a une note, ajouter un bouton pour voir la définition
        if self.current_note_name and self.on_navigate:
            button_frame = Container.transparent(center_frame)
            button_frame.pack(pady=(30, 0))

            reveal_button = ctk.CTkButton(
                button_frame,
                text="Voir la définition",
                command=self._view_note,
                font=("Arial", 14, "bold"),
                fg_color=self.colors['yellow'],
                hover_color="#FFD700",
                text_color=self.colors['black'],
                width=200,
                height=45,
                corner_radius=10
            )
            reveal_button.pack()

        return self.container

    def _view_note(self):
        """Navigue vers la page de visualisation de la note"""
        if not self.current_note_name or not self.current_notes_path:
            return

        if self.on_navigate:
            self.on_navigate(
                'note_viewer',
                note_data={
                    'note_name': self.current_note_name,
                    'notes_path': self.current_notes_path
                }
            )
