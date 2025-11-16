"""
Page des paramètres
"""
import customtkinter as ctk
from tkinter import messagebox
from .base_page import BasePage
from ..ui_components import Button, Container
from ..settings_components import SettingsSection, FormField


class SettingsPage(BasePage):
    """Page des paramètres"""

    def __init__(self, parent, colors: dict, config_manager, app_info, on_config_saved=None):
        super().__init__(parent, colors)
        self.config_manager = config_manager
        self.app_info = app_info
        self.config = config_manager.load_config()
        self.on_config_saved = on_config_saved  # Callback pour recharger l'app

        # Widgets
        self.prenom_entry = None
        self.nom_entry = None
        self.email_entry = None
        self.formation_entry = None
        self.template_entry = None

        # Widgets Obsidian
        self.obsidian_export_path_entry = None

        # Widget Interface
        self.home_message_mode_combo = None
        self.obsidian_home_notes_path_entry = None

    def render(self) -> ctk.CTkFrame:
        """Rend la page des paramètres"""
        # Container principal avec scrollbar
        settings_container = Container.scrollable(self.parent)
        settings_container.pack(fill='both', expand=True, padx=60, pady=30)

        # En-tête
        from ..ui_components import Label
        Label.title(settings_container, "Paramètres", size='medium').pack(anchor='w', pady=(0, 30))

        # Section Général
        self._create_general_section(settings_container)

        # Section Interface
        self._create_interface_section(settings_container)

        # Section Prosit Management
        self._create_prosit_section(settings_container)

        # Section Obsidian Extractor
        self._create_obsidian_section(settings_container)

        # Bouton sauvegarder
        Button.primary(
            settings_container,
            "💾 Sauvegarder la configuration",
            self._save_config,
            font=("Arial", 14, "bold"),
            height=50
        ).pack(fill='x', pady=(20, 30))

        self.container = settings_container
        return settings_container

    def _create_general_section(self, parent):
        """Crée la section général"""
        general_section = SettingsSection.create(parent, "Général", self.colors)

        self.prenom_entry = FormField.create_text_field(
            general_section, "Prénom", "Votre prénom",
            self.config.get('prenom', ''), self.colors
        )

        self.nom_entry = FormField.create_text_field(
            general_section, "Nom", "Votre nom",
            self.config.get('nom', ''), self.colors
        )

        self.email_entry = FormField.create_text_field(
            general_section, "Email", "votre.email@example.com",
            self.config.get('email', ''), self.colors
        )

        self.formation_entry = FormField.create_text_field(
            general_section, "Formation", "Ex: A3 FISA INFO",
            self.config.get('formation', ''), self.colors
        )

        from ..ui_components import Spacer
        Spacer.vertical(general_section, 10)

    def _create_interface_section(self, parent):
        """Crée la section Interface"""
        interface_section = SettingsSection.create(parent, "Interface", self.colors)

        # ComboBox pour le mode de message
        mode_options = [
            "Phrase fixe",
            "Citation aléatoire",
            "Rappel de note (depuis Obsidian)"
        ]

        self.home_message_mode_combo = FormField.create_combo_field(
            interface_section,
            "Message de la page d'accueil",
            "Choisis ce qui s'affiche après 'Hey [Prénom]'",
            mode_options,
            self.config.get('home_message_mode', 'Phrase fixe'),
            self.colors
        )

        # Champ pour le dossier des notes Obsidian
        from tkinter import filedialog

        def browse_notes_folder(entry):
            folder = filedialog.askdirectory(
                title="Sélectionner le dossier des notes Obsidian pour la page d'accueil"
            )
            if folder:
                entry.delete(0, 'end')
                entry.insert(0, folder)

        self.obsidian_home_notes_path_entry = FormField.create_file_field(
            interface_section, "Dossier des notes pour la page d'accueil",
            self.config.get('obsidian_home_notes_path', ''),
            browse_notes_folder, self.colors
        )

        from ..ui_components import Spacer
        Spacer.vertical(interface_section, 10)

    def _create_prosit_section(self, parent):
        """Crée la section Prosit Management"""
        prosit_section = SettingsSection.create(parent, "Prosit Management", self.colors)

        from tkinter import filedialog

        def browse_template(entry):
            filename = filedialog.askopenfilename(
                title="Sélectionner le template Word",
                filetypes=[("Word Documents", "*.docx"), ("All Files", "*.*")]
            )
            if filename:
                entry.delete(0, 'end')
                entry.insert(0, filename)

        self.template_entry = FormField.create_file_field(
            prosit_section, "Template de document (.docx)",
            self.config.get('template_path', ''),
            browse_template, self.colors
        )

        from ..ui_components import Spacer
        Spacer.vertical(prosit_section, 10)

    def _create_obsidian_section(self, parent):
        """Crée la section Obsidian Extractor"""
        obsidian_section = SettingsSection.create(parent, "Obsidian Extractor", self.colors)

        from tkinter import filedialog

        def browse_export_folder(entry):
            folder = filedialog.askdirectory(
                title="Sélectionner le dossier d'export des notes Obsidian"
            )
            if folder:
                entry.delete(0, 'end')
                entry.insert(0, folder)

        self.obsidian_export_path_entry = FormField.create_file_field(
            obsidian_section, "Dossier d'export des notes Obsidian",
            self.config.get('obsidian_export_path', ''),
            browse_export_folder, self.colors
        )

        from ..ui_components import Spacer
        Spacer.vertical(obsidian_section, 10)

    def _save_config(self):
        """Sauvegarde la configuration"""
        # Mettre à jour la config depuis les widgets
        if self.prenom_entry and self.prenom_entry.winfo_exists():
            self.config['prenom'] = self.prenom_entry.get()
        if self.nom_entry and self.nom_entry.winfo_exists():
            self.config['nom'] = self.nom_entry.get()
        if self.email_entry and self.email_entry.winfo_exists():
            self.config['email'] = self.email_entry.get()
        if self.formation_entry and self.formation_entry.winfo_exists():
            self.config['formation'] = self.formation_entry.get()
        if self.template_entry and self.template_entry.winfo_exists():
            self.config['template_path'] = self.template_entry.get()
        if self.obsidian_export_path_entry and self.obsidian_export_path_entry.winfo_exists():
            self.config['obsidian_export_path'] = self.obsidian_export_path_entry.get()
        if self.home_message_mode_combo and self.home_message_mode_combo.winfo_exists():
            self.config['home_message_mode'] = self.home_message_mode_combo.get()
        if self.obsidian_home_notes_path_entry and self.obsidian_home_notes_path_entry.winfo_exists():
            self.config['obsidian_home_notes_path'] = self.obsidian_home_notes_path_entry.get()

        # Sauvegarder
        if self.config_manager.save_config(self.config):
            messagebox.showinfo("Succès", "Configuration sauvegardée avec succès!\n\nRetour à la page d'accueil...")
            # Appeler le callback pour recharger la config et rafraîchir la HomePage
            if self.on_config_saved:
                self.on_config_saved()
        else:
            messagebox.showerror("Erreur", "Erreur lors de la sauvegarde de la configuration")
