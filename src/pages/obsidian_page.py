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

        # Widgets qui doivent persister entre les vues
        self.progress_frame = None
        self.progress_bar = None
        self.progress_label = None
        self.error_label = None
        self.center_frame = None

        # Garder les références aux items de la liste pour l'optimisation
        self.note_items: List[ctk.CTkFrame] = []

        # Scanner Obsidian
        vault_path = config.get('obsidian_vault_path', '')
        self.vault_scanner = ObsidianVaultScanner(vault_path)
        # Scanner le vault au démarrage si le chemin existe
        if vault_path and os.path.exists(vault_path):
            self.vault_scanner.scan_notes(vault_path)

        # Garder les références aux champs de l'éditeur pour la sauvegarde automatique
        self.current_metadata_fields = None
        self.current_editing_index = None
        self.current_title_entry = None
        self.current_def_textbox = None

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
            height=500
        )
        self.center_frame.pack(pady=30, padx=50, expand=True)
        self.center_frame.pack_propagate(False)

        # Zone de drag & drop
        drop_zone = ctk.CTkFrame(
            self.center_frame,
            fg_color=self.colors['gray'],
            corner_radius=15,
            border_width=2,
            border_color=self.colors['border']
        )
        drop_zone.pack(fill='both', expand=True, padx=40, pady=40)

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

    def _browse_file(self):
        """Ouvre un dialogue de sélection de fichier"""
        self.logger.info("Ouverture du dialogue de sélection de fichier", "ObsidianPage")

        filename = filedialog.askopenfilename(
            title="Sélectionner un fichier Word",
            filetypes=[("Documents Word", "*.docx"), ("Tous les fichiers", "*.*")]
        )

        if filename:
            self._process_file(filename)

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
        list_header = ctk.CTkFrame(left_panel, fg_color="transparent", height=50)
        list_header.pack(fill='x', padx=15, pady=10)
        list_header.pack_propagate(False)

        Label.text(list_header, "Notes détectées", font=FONTS['subtitle_bold']).pack(
            side='left', anchor='w', pady=10
        )

        Button.outline(
            list_header,
            "+ Ajouter",
            self._add_new_note,
            width=90,
            height=30
        ).pack(side='right', pady=10)

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

        # Réinitialiser la liste des items
        self.note_items = []

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
            item.configure(border_color=self.colors['blue'], border_width=2)

        # Contenu
        content_frame = Container.transparent(item)
        content_frame.pack(fill='both', expand=True, padx=15, pady=10)

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
            wraplength=200
        )
        def_label.pack(fill='x', pady=(5, 0))

        # Bind click
        item.bind("<Button-1>", lambda e: self._select_note(index))
        title_label.bind("<Button-1>", lambda e: self._select_note(index))
        def_label.bind("<Button-1>", lambda e: self._select_note(index))

        return item

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
                border_color=self.colors['blue'],
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
        vault_path = self.config.get('obsidian_vault_path', '')

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

        # From (avec autocomplete)
        from_frame = ctk.CTkFrame(metadata_content, fg_color="transparent")
        from_frame.pack(fill='x', padx=15, pady=5)
        ctk.CTkLabel(from_frame, text="From:", font=FONTS['body'], width=80, anchor='w').pack(side='left')
        from_entry = AutocompleteEntry(
            from_frame,
            search_function=self._search_notes,
            height=30,
            font=FONTS['body_small'],
            placeholder_text="Tapez [[nom]] pour lier une note"
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

        # Related (avec autocomplete)
        related_frame = ctk.CTkFrame(metadata_content, fg_color="transparent")
        related_frame.pack(fill='x', padx=15, pady=5)
        ctk.CTkLabel(related_frame, text="Related:", font=FONTS['body'], width=80, anchor='w').pack(side='left')
        related_entry = AutocompleteEntry(
            related_frame,
            search_function=self._search_notes,
            height=30,
            font=FONTS['body_small'],
            placeholder_text="Ex: [[Note 1]], [[Note 2]]"
        )
        related_entry.pack(side='left', fill='x', expand=True, padx=(10, 0))
        related_entry.insert(0, note.metadata.get('related', ''))
        metadata_fields['related'] = related_entry

        # Tags (checkboxes)
        tags_frame = ctk.CTkFrame(metadata_content, fg_color="transparent")
        tags_frame.pack(fill='x', padx=15, pady=(5, 15))
        ctk.CTkLabel(tags_frame, text="Tags:", font=FONTS['body'], width=80, anchor='w').pack(side='left')

        tags_container = ctk.CTkFrame(tags_frame, fg_color="transparent")
        tags_container.pack(side='left', fill='x', expand=True, padx=(10, 0))

        tags_list = note.metadata.get('tags', [])
        tag_vars = {}

        # Checkbox pour draft
        draft_var = ctk.BooleanVar(value='draft' in tags_list)
        draft_check = ctk.CTkCheckBox(
            tags_container,
            text="draft",
            variable=draft_var,
            font=FONTS['body_small']
        )
        draft_check.pack(side='left', padx=5)
        tag_vars['draft'] = draft_var

        # Checkbox pour to_complete
        to_complete_var = ctk.BooleanVar(value='to_complete' in tags_list)
        to_complete_check = ctk.CTkCheckBox(
            tags_container,
            text="to_complete",
            variable=to_complete_var,
            font=FONTS['body_small']
        )
        to_complete_check.pack(side='left', padx=5)
        tag_vars['to_complete'] = to_complete_var

        # Checkbox pour permanent
        permanent_var = ctk.BooleanVar(value='permanent' in tags_list)
        permanent_check = ctk.CTkCheckBox(
            tags_container,
            text="permanent",
            variable=permanent_var,
            font=FONTS['body_small']
        )
        permanent_check.pack(side='left', padx=5)
        tag_vars['permanent'] = permanent_var

        metadata_fields['tags'] = tag_vars

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

                # Récupérer les tags cochés
                tag_vars = self.current_metadata_fields['tags']
                new_metadata['tags'] = []
                for tag_name, tag_var in tag_vars.items():
                    if tag_var.get():
                        new_metadata['tags'].append(tag_name)

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

        # Demander le répertoire de destination
        default_path = self.extractor.get_vault_path()
        output_dir = filedialog.askdirectory(
            title="Sélectionner le dossier de destination",
            initialdir=default_path if os.path.exists(default_path) else None
        )

        if not output_dir:
            return

        try:
            # Log de debug avant export
            self.logger.info(f"Export de {len(self.extractor.notes)} notes", "ObsidianPage")
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
