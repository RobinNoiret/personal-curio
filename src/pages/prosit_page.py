"""
Page de gestion des prosits
"""
import customtkinter as ctk
import os
import re
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

    def _update_parsed_data_from_display(self):
        """
        Met à jour self.parsed_data à partir du texte affiché dans result_text
        Permet de prendre en compte les modifications faites par l'utilisateur
        """
        if not self.parsed_data:
            return

        display_text = self.result_text.get("1.0", "end-1c").strip()

        # Parser le texte affiché pour extraire les données modifiées
        lines = display_text.split('\n')
        current_section = None
        section_items = []

        for line in lines:
            line_stripped = line.strip()

            if not line_stripped:
                continue

            # Détecter les en-têtes de section
            if line_stripped.startswith("Bloc:"):
                self.parsed_data['bloc'] = line_stripped.replace("Bloc:", "").strip()
            elif line_stripped.startswith("Prosit"):
                # Format: "Prosit X: Titre"
                match = re.match(r'Prosit\s+(\d+):\s*(.+)', line_stripped)
                if match:
                    self.parsed_data['prosit_number'] = match.group(1)
                    self.parsed_data['prosit_title'] = match.group(2).strip()
            elif line_stripped.startswith("Date:"):
                self.parsed_data['date'] = line_stripped.replace("Date:", "").strip()
            elif line_stripped == "Mots clés:":
                if current_section and section_items:
                    self._save_section_items(current_section, section_items)
                current_section = 'mots_cles'
                section_items = []
            elif line_stripped == "Contexte:":
                if current_section and section_items:
                    self._save_section_items(current_section, section_items)
                current_section = 'contexte'
                section_items = []
            elif line_stripped == "Problématique:":
                if current_section and section_items:
                    self._save_section_items(current_section, section_items)
                current_section = 'problematique'
                section_items = []
            elif line_stripped == "Contraintes:":
                if current_section and section_items:
                    self._save_section_items(current_section, section_items)
                current_section = 'contraintes'
                section_items = []
            elif line_stripped == "Livrables:":
                if current_section and section_items:
                    self._save_section_items(current_section, section_items)
                current_section = 'livrables'
                section_items = []
            elif line_stripped == "Généralisation:":
                if current_section and section_items:
                    self._save_section_items(current_section, section_items)
                current_section = 'generalisation'
                section_items = []
            elif line_stripped == "Hypothèses:":
                if current_section and section_items:
                    self._save_section_items(current_section, section_items)
                current_section = 'hypotheses'
                section_items = []
            elif line_stripped == "Plan d'actions:":
                if current_section and section_items:
                    self._save_section_items(current_section, section_items)
                current_section = 'plan_actions'
                section_items = []
            else:
                # C'est un item de la section courante
                if current_section:
                    # Nettoyer les puces et numéros
                    cleaned = re.sub(r'^[•\-\*]\s*', '', line_stripped)
                    cleaned = re.sub(r'^\d+\.\s*', '', cleaned)
                    if cleaned:
                        section_items.append(cleaned)

        # Sauvegarder la dernière section
        if current_section and section_items:
            self._save_section_items(current_section, section_items)

    def _save_section_items(self, section_name: str, items: list):
        """
        Sauvegarde les items d'une section dans self.parsed_data

        Args:
            section_name: Nom de la section
            items: Liste des items de la section
        """
        if section_name in ['contexte', 'problematique']:
            # Pour les sections textuelles, joindre les items en un texte
            self.parsed_data[section_name] = ' '.join(items)
        else:
            # Pour les listes, sauvegarder tel quel
            self.parsed_data[section_name] = items

    def _generate_document(self):
        """Génère le document Word à partir des données extraites"""
        if not self.parsed_data:
            messagebox.showwarning("Attention", "Veuillez d'abord analyser un compte-rendu.")
            return

        # Mettre à jour parsed_data avec les modifications éventuelles de l'utilisateur
        self._update_parsed_data_from_display()

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
