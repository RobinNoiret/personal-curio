"""
Page de gestion des prosits
"""
import customtkinter as ctk
import os
from tkinter import messagebox, filedialog
from .base_page import BasePage
from ..ui_components import Button, Label, Container, Input
from ..constants import FONTS


class PrositPage(BasePage):
    """Page de gestion des prosits"""

    def __init__(self, parent, colors: dict, parser, generator, config):
        super().__init__(parent, colors)
        self.parser = parser
        self.generator = generator
        self.config = config
        self.parsed_data = None

        # Widgets
        self.cr_text = None
        self.result_text = None
        self.analyze_btn = None
        self.generate_btn = None
        self.status_label = None

    def render(self) -> ctk.CTkFrame:
        """Rend la page prosit"""
        # Container principal
        prosit_container = ctk.CTkFrame(self.parent, fg_color=self.colors['white'])
        prosit_container.pack(fill='both', expand=True, padx=80, pady=40)

        # En-tête
        header_frame = Container.transparent(prosit_container)
        header_frame.pack(fill='x', pady=(0, 30))

        Label.title(header_frame, "Prosit Manager", size='large').pack(side='left')

        # Bouton effacer
        action_frame = Container.transparent(header_frame)
        action_frame.pack(side='right')

        Button.outline(
            action_frame,
            "Effacer",
            self._clear_cr,
            font=FONTS['text_medium'],
            width=100,
            height=40,
            corner_radius=8
        ).pack(side='left', padx=5)

        # Zone principale avec 2 colonnes
        main_frame = Container.transparent(prosit_container)
        main_frame.pack(fill='both', expand=True)

        # Colonne gauche - Saisie du CR
        self._create_left_column(main_frame)

        # Colonne droite - Données extraites
        self._create_right_column(main_frame)

        # Barre de statut
        self.status_label = Label.text(
            prosit_container,
            "Prêt à analyser",
            font=FONTS['text_small']
        )
        self.status_label.pack(pady=(20, 0))

        self.container = prosit_container
        return prosit_container

    def _create_left_column(self, parent):
        """Crée la colonne gauche"""
        left_frame = Container.transparent(parent)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 15))

        Label.title(left_frame, "Compte-Rendu", size='small').pack(anchor='w', pady=(0, 15))

        self.cr_text = Input.textbox(left_frame)
        self.cr_text.pack(fill='both', expand=True)

        # Bouton analyser
        self.analyze_btn = Button.primary(
            left_frame,
            "Analyser le CR →",
            self._analyze_cr,
            font=("Arial", 16, "bold"),
            height=50
        )
        self.analyze_btn.pack(fill='x', pady=(15, 0))

    def _create_right_column(self, parent):
        """Crée la colonne droite"""
        right_frame = Container.transparent(parent)
        right_frame.pack(side='right', fill='both', expand=True, padx=(15, 0))

        Label.title(right_frame, "Données extraites", size='small').pack(anchor='w', pady=(0, 15))

        self.result_text = Input.textbox(right_frame, fg_color=self.colors['gray'])
        self.result_text.pack(fill='both', expand=True)

        # Bouton génération
        self.generate_btn = Button.secondary(
            right_frame,
            "Générer le document",
            self._generate_document,
            font=("Arial", 16, "bold"),
            height=50
        )
        self.generate_btn.configure(state='disabled')
        self.generate_btn.pack(fill='x', pady=(15, 0))

    def _analyze_cr(self):
        """Analyse le CR et extrait les données"""
        cr_text = self.cr_text.get("1.0", "end-1c").strip()

        if not cr_text:
            messagebox.showwarning("Attention", "Veuillez coller un compte-rendu avant d'analyser.")
            return

        try:
            self.status_label.configure(text="⏳ Analyse en cours...", text_color=self.colors['yellow'])

            # Parser le CR
            self.parsed_data = self.parser.parse(cr_text)

            # Afficher les résultats
            formatted_result = self.parser.format_for_display(self.parsed_data)
            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", formatted_result)

            # Activer le bouton de génération
            self.generate_btn.configure(state='normal')

            self.status_label.configure(text="✓ Analyse terminée avec succès", text_color="#10B981")

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'analyse:\n{str(e)}")
            self.status_label.configure(text="✗ Erreur lors de l'analyse", text_color="#EF4444")

    def _clear_cr(self):
        """Efface le contenu du CR"""
        self.cr_text.delete("1.0", "end")
        self.result_text.delete("1.0", "end")
        self.parsed_data = None
        self.generate_btn.configure(state='disabled')
        self.status_label.configure(text="Prêt à analyser", text_color=self.colors['text_gray'])

    def _generate_document(self):
        """Génère le document Word à partir des données extraites"""
        if not self.parsed_data:
            messagebox.showwarning("Attention", "Veuillez d'abord analyser un compte-rendu.")
            return

        # Récupérer le template path
        template_path = self.config.get('template_path', '')

        if not template_path or not os.path.exists(template_path):
            messagebox.showwarning(
                "Attention",
                "Veuillez sélectionner un template valide dans les Settings.\n\n"
                "Allez dans Paramètres > Prosit Management > Template de document"
            )
            return

        # Demander où sauvegarder
        default_name = f"Prosit_{self.parsed_data.get('prosit_number', 'X')}_{self.parsed_data.get('prosit_title', 'document')[:30]}.docx"
        default_name = default_name.replace('/', '_').replace('\\', '_').replace(':', '_')

        save_path = filedialog.asksaveasfilename(
            title="Enregistrer le document",
            defaultextension=".docx",
            initialfile=default_name,
            filetypes=[("Word Documents", "*.docx"), ("All Files", "*.*")]
        )

        if not save_path:
            return

        try:
            self.status_label.configure(text="⏳ Génération du document...", text_color=self.colors['yellow'])

            # Récupérer nom et formation
            nom = self.config.get('nom', '')
            prenom = self.config.get('prenom', '')
            formation = self.config.get('formation', '')

            # Construire le nom complet
            nom_complet = f"{prenom} {nom}".strip() if prenom else nom

            # Générer le document
            self.generator.generate(
                template_path=template_path,
                output_path=save_path,
                data=self.parsed_data,
                nom=nom_complet,
                formation=formation
            )

            self.status_label.configure(
                text=f"✓ Document généré: {os.path.basename(save_path)}",
                text_color="#10B981"
            )

            # Demander si on veut ouvrir le fichier
            if messagebox.askyesno("Succès", f"Document généré avec succès!\n\n{save_path}\n\nVoulez-vous ouvrir le document?"):
                try:
                    os.startfile(save_path)
                except Exception as e:
                    print(f"Erreur lors de l'ouverture du fichier: {e}")

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la génération:\n{str(e)}")
            self.status_label.configure(text="✗ Erreur lors de la génération", text_color="#EF4444")
