"""
Page d'extraction Word vers Obsidian
"""
import customtkinter as ctk
import os
from tkinter import filedialog, messagebox
from typing import Dict, List, Optional
from .base_page import BasePage
from ..ui_components import Button, Label, Container, Spacer
from ..constants import FONTS
from ..utils.obsidian_extractor import WordToObsidianExtractor, ObsidianNote
from ..utils.obsidian_scanner import ObsidianVaultScanner
from ..utils.logger import get_logger
from ..autocomplete_widget import AutocompleteEntry


class ObsidianPage(BasePage):
    """Page d'extraction et édition de notes Obsidian"""

    def __init__(self, parent, colors: Dict, config: Dict = None):
        super().__init__(parent, colors)
        self.config = config or {}
        self.logger = get_logger()
        self.extractor = WordToObsidianExtractor()
        self.current_file = None
        self.selected_note_index: Optional[int] = None

        # État de l'interface
        self.current_view = 'import'  # 'import' ou 'edit'
        self.input_mode = 'file'  # 'file' ou 'text'

        # Widgets qui doivent persister entre les vues
        self.progress_frame = None
        self.progress_bar = None
        self.progress_label = None
        self.error_label = None
        self.center_frame = None

        # Garder les références aux items de la liste pour l'optimisation
        self.note_items: List[ctk.CTkFrame] = []

        # Pour la sélection multiple
        self.note_checkboxes: Dict[int, ctk.CTkCheckBox] = {}
        self.selected_notes: Dict[int, bool] = {}

        # Scanner Obsidian
        # On utilise le chemin d'export ou on essaie de trouver un vault parent
        export_path = config.get('obsidian_export_path', '')
        # Pour le scanner, on cherche le vault racine (dossier parent qui contient .obsidian)
        vault_path = self._find_vault_root(export_path) if export_path else ''
        self.vault_scanner = ObsidianVaultScanner(vault_path)
        # Scanner le vault au démarrage si le chemin existe
        if vault_path and os.path.exists(vault_path):
            self.vault_scanner.scan_notes(vault_path)

        # Garder les références aux champs de l'éditeur pour la sauvegarde automatique
        self.current_metadata_fields = None
        self.current_editing_index = None
        self.current_title_entry = None
        self.current_def_textbox = None

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

        # Si pas trouvé, retourner le chemin original (peut-être que c'est déjà le vault)
        return path

    def render(self) -> ctk.CTkFrame:
        """Rend la page"""
        self.container = ctk.CTkFrame(self.parent, fg_color=self.colors['white'])
        self.container.pack(fill='both', expand=True)

        # Afficher la vue d'import par défaut
        self._show_import_view()

        return self.container

    def _show_import_view(self):
        """Affiche l'interface d'import de fichier"""
        self._clear_container()
        self.current_view = 'import'

        # Titre
        title_container = Container.transparent(self.container)
        title_container.pack(pady=(40, 20))

        Label.title(title_container, "Extraction Word → Obsidian", size='medium').pack()

        # Zone centrale
        self.center_frame = ctk.CTkFrame(
            self.container,
            fg_color=self.colors['white'],
            width=700,
            height=600
        )
        self.center_frame.pack(pady=30, padx=50, expand=True)
        self.center_frame.pack_propagate(False)

        # Boutons toggle pour changer de mode
        switch_frame = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        switch_frame.pack(pady=(20, 10))

        Label.text(
            switch_frame,
            "",
            font=FONTS['body_bold']
        ).pack(side='left', padx=(0, 15))

        # Container pour les boutons
        buttons_container = ctk.CTkFrame(switch_frame, fg_color="transparent")
        buttons_container.pack(side='left')

        # Bouton Fichier
        self.file_button = ctk.CTkButton(
            buttons_container,
            text="Import fichier",
            command=lambda: self._switch_to_mode('file'),
            font=FONTS['body'],
            width=130,
            height=35,
            corner_radius=8,
            fg_color=self.colors['yellow'],
            hover_color=self.colors['yellow'],
            text_color=self.colors['black']
        )
        self.file_button.pack(side='left', padx=(0, 5))

        # Bouton Copier-coller
        self.text_button = ctk.CTkButton(
            buttons_container,
            text="Copier-coller",
            command=lambda: self._switch_to_mode('text'),
            font=FONTS['body'],
            width=130,
            height=35,
            corner_radius=8,
            fg_color=self.colors['gray'],
            hover_color=self.colors['border'],
            text_color=self.colors['text_gray']
        )
        self.text_button.pack(side='left')

        # Zone de contenu qui change selon le mode
        self.input_content_frame = ctk.CTkFrame(
            self.center_frame,
            fg_color=self.colors['white']
        )
        self.input_content_frame.pack(fill='both', expand=True, padx=40, pady=(10, 40))

        # Afficher le mode par défaut (fichier)
        self._show_file_input()

        # Barre de progression (cachée par défaut)
        self.progress_frame = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            width=400,
            height=20,
            corner_radius=10
        )
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="",
            font=FONTS['body_small'],
            text_color=self.colors['text_gray'],
            fg_color="transparent"
        )

        # Message d'erreur (caché par défaut)
        self.error_label = ctk.CTkLabel(
            self.center_frame,
            text="",
            font=FONTS['body'],
            text_color="red",
            fg_color="transparent"
        )

    def _switch_to_mode(self, mode: str):
        """Bascule vers le mode spécifié et met à jour l'apparence des boutons"""
        if mode == self.input_mode:
            return  # Déjà dans ce mode

        self.input_mode = mode

        # Mettre à jour l'apparence des boutons
        if mode == 'file':
            # Activer le bouton fichier
            self.file_button.configure(
                fg_color=self.colors['yellow'],
                hover_color=self.colors['yellow'],
                text_color=self.colors['black']
            )
            # Désactiver le bouton texte
            self.text_button.configure(
                fg_color=self.colors['gray'],
                hover_color=self.colors['border'],
                text_color=self.colors['text_gray']
            )
            self._show_file_input()
        else:
            # Activer le bouton texte
            self.text_button.configure(
                fg_color=self.colors['yellow'],
                hover_color=self.colors['yellow'],
                text_color=self.colors['black']
            )
            # Désactiver le bouton fichier
            self.file_button.configure(
                fg_color=self.colors['gray'],
                hover_color=self.colors['border'],
                text_color=self.colors['text_gray']
            )
            self._show_text_input()

    def _show_file_input(self):
        """Affiche l'interface d'upload de fichier"""
        # Nettoyer le contenu
        for widget in self.input_content_frame.winfo_children():
            widget.destroy()

        # Zone de drag & drop
        drop_zone = ctk.CTkFrame(
            self.input_content_frame,
            fg_color=self.colors['gray'],
            corner_radius=15,
            border_width=2,
            border_color=self.colors['border']
        )
        drop_zone.pack(fill='both', expand=True)

        # Contenu de la drop zone
        drop_content = Container.transparent(drop_zone)
        drop_content.place(relx=0.5, rely=0.5, anchor='center')

        # Icône
        icon_label = Label.title(drop_content, "📄", size='large')
        icon_label.pack(pady=10)

        # Texte principal
        Label.text(
            drop_content,
            "Importer un fichier .docx",
            font=FONTS['subtitle']
        ).pack(pady=5)

        # Bouton parcourir
        Button.secondary(
            drop_content,
            "Parcourir",
            self._browse_file,
            width=150,
            height=40
        ).pack(pady=10)

        # Info sur le format
        ctk.CTkLabel(
            drop_content,
            text="Format accepté: .docx (max 50 MB)",
            font=("Arial", 11),
            text_color=self.colors['text_gray'],
            fg_color="transparent"
        ).pack(pady=(20, 0))

    def _show_text_input(self):
        """Affiche l'interface de copier-coller de texte"""
        # Nettoyer le contenu
        for widget in self.input_content_frame.winfo_children():
            widget.destroy()

        # Zone de texte
        text_container = ctk.CTkFrame(
            self.input_content_frame,
            fg_color=self.colors['gray'],
            corner_radius=15,
            border_width=2,
            border_color=self.colors['border']
        )
        text_container.pack(fill='both', expand=True, padx=10, pady=10)

        # Instructions
        instruction_frame = Container.transparent(text_container)
        instruction_frame.pack(pady=(15, 10), padx=20, fill='x')

        Label.text(
            instruction_frame,
            "Collez vos définitions ci-dessous",
            font=FONTS['subtitle']
        ).pack(anchor='w')

        ctk.CTkLabel(
            instruction_frame,
            text="Format : Terme : Définition (une par ligne)",
            font=("Arial", 11),
            text_color=self.colors['text_gray'],
            fg_color="transparent"
        ).pack(anchor='w', pady=(5, 0))

        # Zone de texte
        self.text_input = ctk.CTkTextbox(
            text_container,
            font=FONTS['body'],
            border_width=1,
            border_color=self.colors['border'],
            wrap='word',
            fg_color=self.colors['white']
        )
        self.text_input.pack(fill='both', expand=True, padx=20, pady=(0, 15))

        # Bouton pour extraire
        button_frame = Container.transparent(text_container)
        button_frame.pack(pady=(0, 15))

        Button.secondary(
            button_frame,
            "Extraire les notes",
            self._process_text,
            width=180,
            height=40
        ).pack()

    def _browse_file(self):
        """Ouvre un dialogue de sélection de fichier"""
        self.logger.info("Ouverture du dialogue de sélection de fichier", "ObsidianPage")

        filename = filedialog.askopenfilename(
            title="Sélectionner un fichier Word",
            filetypes=[("Documents Word", "*.docx"), ("Tous les fichiers", "*.*")]
        )

        if filename:
            self._process_file(filename)

    def _process_text(self):
        """Traite le texte copié-collé"""
        if not hasattr(self, 'text_input'):
            return

        text = self.text_input.get('1.0', 'end-1c').strip()

        if not text:
            self._show_error("Veuillez coller du texte avant de continuer")
            return

        self.logger.info("Traitement du texte copié-collé", "ObsidianPage")

        # Afficher la barre de progression
        self._show_progress("Analyse du texte...")

        try:
            # Extraire les notes
            notes = self.extractor.extract_from_text(text)

            self.logger.info(f"{len(notes)} notes extraites", "ObsidianPage")

            # Cacher la progression
            self._hide_progress()

            if not notes:
                self._show_error("Aucune définition trouvée dans le texte")
                return

            # Passer à la vue d'édition
            self._show_edit_view()

        except Exception as e:
            self.logger.error(f"Erreur lors du traitement: {e}", "ObsidianPage")
            self._hide_progress()
            messagebox.showerror("Erreur", f"Erreur lors du traitement:\n{str(e)}")

    def _process_file(self, filepath: str):
        """Traite le fichier Word sélectionné"""
        self.logger.info(f"Traitement du fichier: {filepath}", "ObsidianPage")

        # Afficher la barre de progression
        self._show_progress("Analyse du document...")

        try:
            # Extraire les notes
            self.current_file = filepath
            notes = self.extractor.extract_from_docx(filepath)

            self.logger.info(f"{len(notes)} notes extraites", "ObsidianPage")

            # Cacher la progression
            self._hide_progress()

            if not notes:
                self._show_error("Aucune définition trouvée dans le document")
                return

            # Passer à la vue d'édition
            self._show_edit_view()

        except Exception as e:
            self.logger.error(f"Erreur lors du traitement: {e}", "ObsidianPage")
            self._hide_progress()
            # Utiliser messagebox au lieu de error_label car on pourrait avoir changé de vue
            messagebox.showerror("Erreur", f"Erreur lors du traitement:\n{str(e)}")

    def _show_progress(self, message: str):
        """Affiche la barre de progression"""
        if self.progress_frame and self.progress_bar and self.progress_label:
            self.progress_frame.pack(pady=20)
            self.progress_bar.pack(pady=5)
            self.progress_label.configure(text=message)
            self.progress_label.pack()
            self.progress_bar.set(0.5)  # Mode indéterminé
            self.container.update()

    def _hide_progress(self):
        """Cache la barre de progression"""
        if self.progress_frame:
            self.progress_frame.pack_forget()

    def _show_error(self, message: str):
        """Affiche un message d'erreur"""
        if self.error_label:
            self.error_label.configure(text=message)
            self.error_label.pack(pady=10)
            self.container.after(5000, lambda: self.error_label.pack_forget())

    def _show_edit_view(self):
        """Affiche l'interface d'édition des notes"""
        self._clear_container()
        self.current_view = 'edit'

        # En-tête
        header = ctk.CTkFrame(self.container, fg_color=self.colors['white'], height=80)
        header.pack(fill='x', padx=30, pady=(20, 0))
        header.pack_propagate(False)

        # Titre et bouton retour
        header_left = Container.transparent(header)
        header_left.pack(side='left', fill='y')

        Button.outline(
            header_left,
            "← Retour",
            lambda: self._show_import_view(),
            width=100,
            height=35
        ).pack(side='left', pady=20)

        title_frame = Container.transparent(header)
        title_frame.pack(side='left', expand=True, fill='y', padx=20)
        Label.title(title_frame, f"Notes extraites ({len(self.extractor.notes)})", size='small').pack(
            anchor='w', pady=25
        )

        # Bouton exporter
        header_right = Container.transparent(header)
        header_right.pack(side='right', fill='y')

        Button.secondary(
            header_right,
            "Exporter vers Obsidian",
            self._export_notes,
            width=200,
            height=40
        ).pack(side='right', pady=20)

        # Ligne de séparation
        separator = ctk.CTkFrame(self.container, height=1, fg_color=self.colors['border'])
        separator.pack(fill='x', padx=30)

        # Zone principale avec split view
        main_frame = ctk.CTkFrame(self.container, fg_color=self.colors['white'])
        main_frame.pack(fill='both', expand=True, padx=30, pady=20)

        # Liste des notes (gauche) - 40%
        left_panel = ctk.CTkFrame(main_frame, fg_color=self.colors['gray'], corner_radius=10)
        left_panel.pack(side='left', fill='both', expand=False, padx=(0, 10), ipadx=200)

        # En-tête de la liste
        list_header = ctk.CTkFrame(left_panel, fg_color="transparent", height=80)
        list_header.pack(fill='x', padx=15, pady=10)
        list_header.pack_propagate(False)

        # Première ligne : titre et bouton ajouter
        header_top = ctk.CTkFrame(list_header, fg_color="transparent")
        header_top.pack(fill='x', pady=(0, 5))

        Label.text(header_top, "Notes détectées", font=FONTS['subtitle_bold']).pack(
            side='left', anchor='w'
        )

        Button.outline(
            header_top,
            "+ Ajouter",
            self._add_new_note,
            width=90,
            height=30
        ).pack(side='right')

        # Deuxième ligne : boutons de sélection multiple
        header_bottom = ctk.CTkFrame(list_header, fg_color="transparent")
        header_bottom.pack(fill='x')

        self.select_all_button = ctk.CTkButton(
            header_bottom,
            text="Tout sélectionner",
            command=self._toggle_select_all,
            width=120,
            height=28,
            font=("Arial", 11),
            fg_color=self.colors['gray'],
            hover_color=self.colors['border'],
            text_color=self.colors['text_gray'],
            corner_radius=6
        )
        self.select_all_button.pack(side='left', padx=(0, 5))

        self.delete_selection_button = ctk.CTkButton(
            header_bottom,
            text="🗑 Supprimer sélection",
            command=self._delete_selected_notes,
            width=150,
            height=28,
            font=("Arial", 11),
            fg_color="#ff4444",
            hover_color="#cc0000",
            text_color="white",
            corner_radius=6
        )
        self.delete_selection_button.pack(side='left')

        # Liste scrollable
        list_scroll_frame = ctk.CTkScrollableFrame(
            left_panel,
            fg_color="transparent"
        )
        list_scroll_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        self.notes_list_frame = list_scroll_frame
        self._populate_notes_list()

        # Panel d'édition (droite) - 60%
        right_panel = ctk.CTkFrame(main_frame, fg_color=self.colors['white'])
        right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))

        # Placeholder ou contenu d'édition
        self.edit_panel = right_panel
        self._show_edit_placeholder()

    def _populate_notes_list(self):
        """Remplit la liste des notes"""
        # Nettoyer
        for widget in self.notes_list_frame.winfo_children():
            widget.destroy()

        # Réinitialiser la liste des items et les checkboxes
        self.note_items = []
        self.note_checkboxes = {}
        self.selected_notes = {}

        # Ajouter chaque note
        for i, note in enumerate(self.extractor.notes):
            note_item = self._create_note_list_item(i, note)
            note_item.pack(fill='x', pady=5)
            self.note_items.append(note_item)

    def _create_note_list_item(self, index: int, note: ObsidianNote) -> ctk.CTkFrame:
        """Crée un item de la liste des notes"""
        item = ctk.CTkFrame(
            self.notes_list_frame,
            fg_color=self.colors['white'],
            corner_radius=8,
            border_width=1,
            border_color=self.colors['border']
        )

        # Sélection
        is_selected = (self.selected_note_index == index)
        if is_selected:
            item.configure(border_color=self.colors['yellow'], border_width=2)

        # Contenu principal avec checkbox à gauche
        main_container = Container.transparent(item)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)

        # Checkbox à gauche
        checkbox_var = ctk.BooleanVar(value=False)
        checkbox = ctk.CTkCheckBox(
            main_container,
            text="",
            variable=checkbox_var,
            width=20,
            checkbox_width=20,
            checkbox_height=20,
            fg_color=self.colors['yellow'],
            hover_color="#FFD700",
            border_color=self.colors['border'],
            command=lambda: self._on_checkbox_changed(index, checkbox_var.get())
        )
        checkbox.pack(side='left', padx=(0, 10))
        self.note_checkboxes[index] = checkbox
        self.selected_notes[index] = False

        # Contenu (titre + définition)
        content_frame = Container.transparent(main_container)
        content_frame.pack(side='left', fill='both', expand=True)

        # Titre
        title_label = ctk.CTkLabel(
            content_frame,
            text=note.title,
            font=FONTS['body_bold'],
            text_color=self.colors['black'],
            anchor='w'
        )
        title_label.pack(fill='x')

        # Définition (tronquée)
        def_preview = note.definition[:80] + "..." if len(note.definition) > 80 else note.definition
        def_label = ctk.CTkLabel(
            content_frame,
            text=def_preview,
            font=("Arial", 11),
            text_color=self.colors['text_gray'],
            anchor='w',
            wraplength=180
        )
        def_label.pack(fill='x', pady=(5, 0))

        # Bind click sur le contenu (pas sur la checkbox)
        content_frame.bind("<Button-1>", lambda _: self._select_note(index))
        title_label.bind("<Button-1>", lambda _: self._select_note(index))
        def_label.bind("<Button-1>", lambda _: self._select_note(index))

        return item

    def _on_checkbox_changed(self, index: int, is_checked: bool):
        """Appelé quand une checkbox change d'état"""
        self.selected_notes[index] = is_checked
        self.logger.debug(f"Checkbox {index} changée: {is_checked}", "ObsidianPage")

    def _toggle_select_all(self):
        """Bascule entre sélectionner tout et désélectionner tout"""
        # Vérifier si toutes les notes sont sélectionnées
        all_selected = all(self.selected_notes.values()) if self.selected_notes else False

        # Inverser l'état
        new_state = not all_selected

        # Mettre à jour toutes les checkboxes
        for index, checkbox in self.note_checkboxes.items():
            checkbox.select() if new_state else checkbox.deselect()
            self.selected_notes[index] = new_state

        # Mettre à jour le texte du bouton
        if new_state:
            self.select_all_button.configure(text="Tout désélectionner")
        else:
            self.select_all_button.configure(text="Tout sélectionner")

        self.logger.info(f"Toutes les notes {'sélectionnées' if new_state else 'désélectionnées'}", "ObsidianPage")

    def _delete_selected_notes(self):
        """Supprime toutes les notes sélectionnées"""
        # Récupérer les indices des notes sélectionnées
        selected_indices = [index for index, is_selected in self.selected_notes.items() if is_selected]

        if not selected_indices:
            messagebox.showinfo("Information", "Aucune note sélectionnée")
            return

        # Confirmation
        count = len(selected_indices)
        message = f"Êtes-vous sûr de vouloir supprimer {count} note(s) ?"
        if not messagebox.askyesno("Confirmation", message):
            return

        # Supprimer les notes en commençant par la fin pour éviter les problèmes d'index
        selected_indices.sort(reverse=True)
        for index in selected_indices:
            self.extractor.remove_note(index)

        self.logger.info(f"{count} note(s) supprimée(s)", "ObsidianPage")

        # Si la note en cours d'édition a été supprimée, réinitialiser
        if self.selected_note_index in selected_indices:
            self.selected_note_index = None

        # Rafraîchir l'interface
        self._populate_notes_list()
        if self.selected_note_index is None:
            self._show_edit_placeholder()

        # Afficher un message de succès
        messagebox.showinfo("Succès", f"{count} note(s) supprimée(s) avec succès")

    def _update_selection_borders(self, old_index: Optional[int], new_index: int):
        """Met à jour les bordures de sélection sans recharger toute la liste"""
        # Désélectionner l'ancien item
        if old_index is not None and 0 <= old_index < len(self.note_items):
            self.note_items[old_index].configure(
                border_color=self.colors['border'],
                border_width=1
            )

        # Sélectionner le nouvel item
        if 0 <= new_index < len(self.note_items):
            self.note_items[new_index].configure(
                border_color=self.colors['yellow'],
                border_width=2
            )

    def _select_note(self, index: int):
        """Sélectionne une note pour l'édition"""
        self.logger.debug(f"Sélection de la note {index}", "ObsidianPage")

        # Auto-sauvegarder la note précédente si on change de note
        if self.selected_note_index is not None and self.selected_note_index != index:
            self._auto_save_current_note()

        old_index = self.selected_note_index
        self.selected_note_index = index

        # Mettre à jour seulement les bordures des items concernés
        self._update_selection_borders(old_index, index)

        # Afficher l'éditeur
        self._show_note_editor(index)

    def _search_notes(self, query: str) -> List[str]:
        """Fonction de recherche pour l'autocomplete des notes Obsidian"""
        # Vérifier si le vault_path a changé ou si le cache est vide
        export_path = self.config.get('obsidian_export_path', '')
        vault_path = self._find_vault_root(export_path) if export_path else ''

        if vault_path and vault_path != self.vault_scanner.vault_path:
            # Le chemin a changé, mettre à jour le scanner
            self.vault_scanner.vault_path = vault_path
            self.logger.info(f"Vault path mis à jour: {vault_path}", "ObsidianPage")

        # Si le cache est vide et qu'on a un vault_path, scanner
        if vault_path and not self.vault_scanner._notes_cache:
            self.logger.info(f"Scan du vault: {vault_path}", "ObsidianPage")
            self.vault_scanner.scan_notes(vault_path)

        # Utiliser directement la méthode search_notes du scanner
        return self.vault_scanner.search_notes(query, limit=10)

    def _show_edit_placeholder(self):
        """Affiche le placeholder quand aucune note n'est sélectionnée"""
        # Nettoyer
        for widget in self.edit_panel.winfo_children():
            widget.destroy()

        # Message
        placeholder = Container.transparent(self.edit_panel)
        placeholder.place(relx=0.5, rely=0.5, anchor='center')

        ctk.CTkLabel(
            placeholder,
            text="Sélectionnez une note pour l'éditer",
            font=FONTS['subtitle'],
            text_color=self.colors['text_gray'],
            fg_color="transparent"
        ).pack()

    def _show_note_editor(self, index: int):
        """Affiche l'éditeur pour une note"""
        # Nettoyer
        for widget in self.edit_panel.winfo_children():
            widget.destroy()

        note = self.extractor.notes[index]

        # Container principal
        editor = ctk.CTkFrame(self.edit_panel, fg_color="transparent")
        editor.pack(fill='both', expand=True, padx=20, pady=20)

        # En-tête avec bouton supprimer
        editor_header = Container.transparent(editor)
        editor_header.pack(fill='x', pady=(0, 20))

        Label.text(editor_header, "Éditer la note", font=FONTS['subtitle_bold']).pack(
            side='left', anchor='w'
        )

        ctk.CTkButton(
            editor_header,
            text="🗑 Supprimer",
            command=lambda: self._delete_note(index),
            width=120,
            height=35,
            fg_color="#ff4444",
            hover_color="#cc0000",
            text_color="white",
            font=FONTS['body'],
            corner_radius=8
        ).pack(side='right')

        # Champ titre
        Label.text(editor, "Titre de la note", font=FONTS['body_bold']).pack(
            anchor='w', pady=(10, 5)
        )

        title_entry = ctk.CTkEntry(
            editor,
            height=40,
            font=FONTS['body'],
            border_width=1,
            border_color=self.colors['border']
        )
        title_entry.pack(fill='x', pady=(0, 20))
        title_entry.insert(0, note.title)

        # Section métadonnées YAML (pliable)
        metadata_frame = ctk.CTkFrame(editor, fg_color=self.colors['gray'], corner_radius=8)
        metadata_frame.pack(fill='x', pady=(0, 20))

        # En-tête pliable
        metadata_header = ctk.CTkFrame(metadata_frame, fg_color="transparent")
        metadata_header.pack(fill='x', padx=15, pady=10)

        # Variable pour l'état plié/déplié
        metadata_expanded = [False]  # Liste pour la closure

        metadata_toggle_label = ctk.CTkLabel(
            metadata_header,
            text="▶ Métadonnées YAML",
            font=FONTS['body_bold'],
            text_color=self.colors['black'],
            cursor="hand2"
        )
        metadata_toggle_label.pack(side='left', anchor='w')

        # Container pour les champs de métadonnées (caché par défaut)
        metadata_content = ctk.CTkFrame(metadata_frame, fg_color="transparent")

        # Créer les champs de métadonnées
        metadata_fields = {}

        # Type
        type_frame = ctk.CTkFrame(metadata_content, fg_color="transparent")
        type_frame.pack(fill='x', padx=15, pady=5)
        ctk.CTkLabel(type_frame, text="Type:", font=FONTS['body'], width=80, anchor='w').pack(side='left')
        type_entry = ctk.CTkEntry(type_frame, height=30, font=FONTS['body_small'])
        type_entry.pack(side='left', fill='x', expand=True, padx=(10, 0))
        type_entry.insert(0, note.metadata.get('type', ''))
        metadata_fields['type'] = type_entry

        # Date
        date_frame = ctk.CTkFrame(metadata_content, fg_color="transparent")
        date_frame.pack(fill='x', padx=15, pady=5)
        ctk.CTkLabel(date_frame, text="Date:", font=FONTS['body'], width=80, anchor='w').pack(side='left')
        date_entry = ctk.CTkEntry(date_frame, height=30, font=FONTS['body_small'])
        date_entry.pack(side='left', fill='x', expand=True, padx=(10, 0))
        date_entry.insert(0, note.metadata.get('date', ''))
        metadata_fields['date'] = date_entry

        # From (avec autocomplete, un seul lien)
        from_frame = ctk.CTkFrame(metadata_content, fg_color="transparent")
        from_frame.pack(fill='x', padx=15, pady=5)
        ctk.CTkLabel(from_frame, text="From:", font=FONTS['body'], width=80, anchor='w').pack(side='left')
        from_entry = AutocompleteEntry(
            from_frame,
            search_function=self._search_notes,
            allow_multiple=False,  # Un seul lien
            height=30,
            font=FONTS['body_small'],
            placeholder_text="Tapez [[ pour chercher une note"
        )
        from_entry.pack(side='left', fill='x', expand=True, padx=(10, 0))
        from_entry.insert(0, note.metadata.get('from', ''))
        metadata_fields['from'] = from_entry

        # About (TODO: ajouter autocomplete)
        about_frame = ctk.CTkFrame(metadata_content, fg_color="transparent")
        about_frame.pack(fill='x', padx=15, pady=5)
        ctk.CTkLabel(about_frame, text="About:", font=FONTS['body'], width=80, anchor='w').pack(side='left')
        about_entry = ctk.CTkEntry(about_frame, height=30, font=FONTS['body_small'], placeholder_text="Ex: article, vidéo, ...")
        about_entry.pack(side='left', fill='x', expand=True, padx=(10, 0))
        about_entry.insert(0, note.metadata.get('about', ''))
        metadata_fields['about'] = about_entry

        # Related (avec autocomplete, plusieurs liens possibles)
        related_frame = ctk.CTkFrame(metadata_content, fg_color="transparent")
        related_frame.pack(fill='x', padx=15, pady=5)
        ctk.CTkLabel(related_frame, text="Related:", font=FONTS['body'], width=80, anchor='w').pack(side='left')
        related_entry = AutocompleteEntry(
            related_frame,
            search_function=self._search_notes,
            allow_multiple=True,  # Plusieurs liens possibles
            height=30,
            font=FONTS['body_small'],
            placeholder_text="Tapez [[ pour ajouter des notes"
        )
        related_entry.pack(side='left', fill='x', expand=True, padx=(10, 0))
        related_entry.insert(0, note.metadata.get('related', ''))
        metadata_fields['related'] = related_entry

        # Tags (liste déroulante simple - sélection unique)
        tags_frame = ctk.CTkFrame(metadata_content, fg_color="transparent")
        tags_frame.pack(fill='x', padx=15, pady=(5, 15))
        ctk.CTkLabel(tags_frame, text="Tags:", font=FONTS['body'], width=80, anchor='w').pack(side='left')

        # Options de tags disponibles
        available_tags = ['draft', 'to_complete', 'permanent']
        tags_list = note.metadata.get('tags', [])

        # ComboBox pour sélectionner un tag
        tags_combobox = ctk.CTkComboBox(
            tags_frame,
            values=available_tags,
            height=30,
            font=FONTS['body_small'],
            button_color=self.colors['yellow'],
            button_hover_color="#FFD700",
            border_color=self.colors['border'],
            fg_color=self.colors['white'],
            dropdown_fg_color=self.colors['white'],
            dropdown_hover_color=self.colors['gray']
        )
        tags_combobox.pack(side='left', fill='x', expand=True, padx=(10, 0))

        # Définir la valeur initiale (premier tag s'il existe, sinon 'draft' par défaut)
        if tags_list:
            tags_combobox.set(tags_list[0])
        else:
            tags_combobox.set('draft')

        metadata_fields['tags'] = tags_combobox

        # Fonction pour basculer l'affichage
        def toggle_metadata():
            if metadata_expanded[0]:
                metadata_content.pack_forget()
                metadata_toggle_label.configure(text="▶ Métadonnées YAML")
                metadata_expanded[0] = False
            else:
                metadata_content.pack(fill='x', pady=(0, 10))
                metadata_toggle_label.configure(text="▼ Métadonnées YAML")
                metadata_expanded[0] = True

        metadata_toggle_label.bind("<Button-1>", lambda e: toggle_metadata())

        # Champ définition
        Label.text(editor, "Définition", font=FONTS['body_bold']).pack(
            anchor='w', pady=(10, 5)
        )

        def_textbox = ctk.CTkTextbox(
            editor,
            height=200,
            font=FONTS['body'],
            border_width=1,
            border_color=self.colors['border'],
            wrap='word'
        )
        def_textbox.pack(fill='both', expand=True, pady=(0, 20))
        def_textbox.insert('1.0', note.definition)

        # Sauvegarder les références pour l'auto-save
        self.current_editing_index = index
        self.current_title_entry = title_entry
        self.current_def_textbox = def_textbox
        self.current_metadata_fields = metadata_fields

    def _auto_save_current_note(self):
        """Sauvegarde automatique de la note en cours d'édition (sans message)"""
        if (self.current_editing_index is not None and
            self.current_title_entry and
            self.current_def_textbox and
            self.current_metadata_fields):

            try:
                new_title = self.current_title_entry.get().strip()
                new_def = self.current_def_textbox.get('1.0', 'end-1c').strip()

                # Ne pas sauvegarder si les champs sont vides
                if not new_title or not new_def:
                    return

                # Récupérer les métadonnées
                new_metadata = {}
                new_metadata['type'] = self.current_metadata_fields['type'].get().strip()
                new_metadata['date'] = self.current_metadata_fields['date'].get().strip()
                new_metadata['from'] = self.current_metadata_fields['from'].get().strip()
                new_metadata['about'] = self.current_metadata_fields['about'].get().strip()
                new_metadata['related'] = self.current_metadata_fields['related'].get().strip()

                # Récupérer le tag sélectionné dans la ComboBox (un seul tag)
                selected_tag = self.current_metadata_fields['tags'].get()
                new_metadata['tags'] = [selected_tag] if selected_tag else []

                # Mettre à jour la note
                self.extractor.update_note(self.current_editing_index, new_title, new_def, new_metadata)
                self.logger.info(f"Auto-save: Note {self.current_editing_index} '{new_title}' sauvegardée", "ObsidianPage")

                # Mettre à jour l'affichage du titre dans la liste (sans tout recharger)
                if 0 <= self.current_editing_index < len(self.note_items):
                    item = self.note_items[self.current_editing_index]
                    for widget in item.winfo_children():
                        if isinstance(widget, ctk.CTkFrame):
                            for child in widget.winfo_children():
                                if isinstance(child, ctk.CTkLabel) and child.cget("font") == FONTS['body_bold']:
                                    child.configure(text=new_title)
                                    break
            except Exception as e:
                self.logger.error(f"Erreur lors de l'auto-save: {e}", "ObsidianPage")

    def _delete_note(self, index: int):
        """Supprime une note"""
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer cette note ?"):
            self.extractor.remove_note(index)
            self.logger.info(f"Note {index} supprimée", "ObsidianPage")

            # Rafraîchir
            self.selected_note_index = None
            self._populate_notes_list()
            self._show_edit_placeholder()

    def _add_new_note(self):
        """Ajoute une nouvelle note vide"""
        self.extractor.add_note("Nouveau terme", "Définition à compléter")
        self.logger.info("Nouvelle note ajoutée", "ObsidianPage")

        # Rafraîchir et sélectionner la nouvelle note
        new_index = len(self.extractor.notes) - 1
        self._populate_notes_list()
        self._select_note(new_index)

    def _export_notes(self):
        """Exporte toutes les notes vers Obsidian"""
        if not self.extractor.notes:
            messagebox.showwarning("Attention", "Aucune note à exporter")
            return

        # Auto-sauvegarder la note en cours d'édition avant l'export
        self._auto_save_current_note()

        # Récupérer le chemin d'export depuis la config
        output_dir = self.config.get('obsidian_export_path', '')

        # Vérifier que le chemin d'export est configuré
        if not output_dir:
            messagebox.showwarning(
                "Configuration manquante",
                "Veuillez configurer le dossier d'export Obsidian dans les paramètres."
            )
            return

        # Créer le dossier d'export s'il n'existe pas
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            self.logger.error(f"Erreur lors de la création du dossier: {e}", "ObsidianPage")
            messagebox.showerror("Erreur", f"Impossible de créer le dossier:\n{str(e)}")
            return

        try:
            # Log de debug avant export
            self.logger.info(f"Export de {len(self.extractor.notes)} notes vers {output_dir}", "ObsidianPage")
            for i, note in enumerate(self.extractor.notes):
                self.logger.info(f"Note {i} '{note.title}' - Tags: {note.metadata.get('tags')}, From: {note.metadata.get('from')}, About: {note.metadata.get('about')}", "ObsidianPage")

            created_files = self.extractor.export_notes(output_dir)
            self.logger.info(f"{len(created_files)} notes exportées vers {output_dir}", "ObsidianPage")

            messagebox.showinfo(
                "Succès",
                f"{len(created_files)} notes exportées avec succès !\n\nDossier: {output_dir}"
            )

        except Exception as e:
            self.logger.error(f"Erreur lors de l'export: {e}", "ObsidianPage")
            messagebox.showerror("Erreur", f"Erreur lors de l'export:\n{str(e)}")

    def _clear_container(self):
        """Nettoie le container"""
        for widget in self.container.winfo_children():
            widget.destroy()
