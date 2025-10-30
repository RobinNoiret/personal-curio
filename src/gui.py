"""
Interface graphique pour le gestionnaire de prosits
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from typing import Dict, Optional
from PIL import Image
from .cr_parser import CRParser
from .docx_generator import DocxGenerator


class PrositManagerGUI:
    """Interface graphique principale de l'application"""

    # Palette de couleurs
    COLORS = {
        'yellow': '#FFC92C',
        'white': '#FFFFFF',
        'black': '#1A1A18',
        'gray': '#F8F9FA',
        'text_gray': '#6B7280',
        'border': '#E5E7EB'
    }

    def __init__(self):
        # Configuration du thème
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Fenêtre principale
        self.root = ctk.CTk()
        self.root.title("Prosit Manager")
        self.root.geometry("1600x1000")
        self.root.configure(fg_color=self.COLORS['white'])

        # Instances
        self.parser = CRParser()
        self.generator = DocxGenerator()
        self.parsed_data: Optional[Dict] = None

        # Configuration par défaut
        self.config = {
            'nom': 'NOIRET Robin',
            'formation': 'A3 FISA INFO',
            'template_path': ''
        }

        # Page actuelle
        self.current_page = None

        # Références aux widgets de configuration (créés dans Settings)
        self.nom_entry = None
        self.formation_entry = None
        self.template_entry = None

        # Créer l'interface
        self._create_main_layout()
        self._load_config()

        # Afficher la page d'accueil par défaut
        self._show_home_page()

    def _create_main_layout(self):
        """Crée la structure principale avec sidebar verticale à gauche et zone de contenu"""

        # === Container principal pour la disposition horizontale ===
        main_container = ctk.CTkFrame(self.root, fg_color=self.COLORS['white'])
        main_container.pack(fill='both', expand=True)

        # === Sidebar verticale à gauche ===
        self.sidebar = ctk.CTkFrame(main_container, width=120, fg_color=self.COLORS['gray'], border_width=0)
        self.sidebar.pack(side='left', fill='y', padx=0, pady=0)
        self.sidebar.pack_propagate(False)

        # Logo en haut de la sidebar (sert de bouton home)
        # Charger l'image du logo
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'logo_black_version.png')
        try:
            logo_image = ctk.CTkImage(
                light_image=Image.open(logo_path),
                dark_image=Image.open(logo_path),
                size=(60, 60)
            )
            logo_btn = ctk.CTkButton(
                self.sidebar,
                text="",
                image=logo_image,
                fg_color=self.COLORS['yellow'],
                hover_color="#FFD700",
                width=120,
                height=100,
                corner_radius=0,
                command=self._show_home_page
            )
        except Exception as e:
            # Fallback au texte "/" si l'image ne peut pas être chargée
            print(f"Erreur lors du chargement du logo: {e}")
            logo_btn = ctk.CTkButton(
                self.sidebar,
                text="/",
                font=("Arial", 40, "bold"),
                fg_color=self.COLORS['yellow'],
                text_color=self.COLORS['black'],
                hover_color="#FFD700",
                width=120,
                height=100,
                corner_radius=0,
                command=self._show_home_page
            )
        logo_btn.pack(fill='x', pady=(0, 0), padx=0)

        # Navigation buttons
        self.nav_buttons = {}
        self.nav_labels = {}

        # Structure pour chaque bouton: (clé, icône, texte, commande)
        nav_items = [
            ('prosit', '📦', 'Prosit\nManagement', self._show_prosit_page),
            ('articles', '📚', 'Knowledge\nManagement', None),
            ('placeholder1', '🔗', 'Placeholder', None),
            ('placeholder2', '📊', 'Placeholder', None),
            ('placeholder3', '▶', 'Placeholder', None),
            ('placeholder4', '💼', 'Placeholder', None),
        ]

        for key, icon, text, command in nav_items:
            # Frame conteneur pour chaque segment (icône + texte)
            segment = ctk.CTkFrame(self.sidebar, fg_color=self.COLORS['gray'])
            segment.pack(fill='x', pady=0, padx=0)

            # Bouton qui prend toute la largeur
            btn = ctk.CTkButton(
                segment,
                text=f"{icon}\n{text}",
                font=("Arial", 14),
                fg_color=self.COLORS['gray'],
                text_color=self.COLORS['text_gray'],
                hover_color=self.COLORS['border'],
                width=120,
                height=100,
                corner_radius=0,
                border_width=0,
                command=command if command else lambda: None,
                state='normal' if command else 'disabled',
                anchor='center'
            )
            btn.pack(fill='both', expand=True)
            self.nav_buttons[key] = btn

        # === Zone de droite (header + contenu) ===
        right_container = ctk.CTkFrame(main_container, fg_color=self.COLORS['white'])
        right_container.pack(side='right', fill='both', expand=True)

        # === Header en haut à droite ===
        header = ctk.CTkFrame(right_container, height=80, fg_color=self.COLORS['white'])
        header.pack(fill='x', padx=0, pady=0)
        header.pack_propagate(False)

        # Container pour les boutons à droite du header
        header_buttons = ctk.CTkFrame(header, fg_color="transparent")
        header_buttons.pack(side='right', padx=30, pady=20)

        # Bouton Legal
        legal_btn = ctk.CTkButton(
            header_buttons,
            text="legal (claude)",
            font=("Arial", 13),
            fg_color=self.COLORS['white'],
            text_color=self.COLORS['text_gray'],
            hover_color=self.COLORS['gray'],
            border_width=1,
            border_color=self.COLORS['border'],
            width=120,
            height=40,
            corner_radius=8
        )
        legal_btn.pack(side='left', padx=5)

        # Bouton Settings (roue crantée)
        self.nav_buttons['settings'] = ctk.CTkButton(
            header_buttons,
            text="⚙",
            font=("Arial", 20),
            fg_color=self.COLORS['white'],
            text_color=self.COLORS['text_gray'],
            hover_color=self.COLORS['gray'],
            border_width=1,
            border_color=self.COLORS['border'],
            command=self._show_settings_page,
            width=50,
            height=40,
            corner_radius=8
        )
        self.nav_buttons['settings'].pack(side='left', padx=5)

        # Ligne de séparation sous le header
        separator = ctk.CTkFrame(right_container, height=1, fg_color=self.COLORS['border'])
        separator.pack(fill='x')

        # === Zone de contenu principale ===
        self.content_frame = ctk.CTkFrame(right_container, fg_color=self.COLORS['white'])
        self.content_frame.pack(fill='both', expand=True, padx=0, pady=0)

    def _highlight_nav_button(self, button_name: str):
        """Met en surbrillance le bouton de navigation actif dans la sidebar"""
        for name, btn in self.nav_buttons.items():
            if name == 'settings':  # Skip settings button (in header)
                continue

            if name == button_name:
                # Onglet actuel - fond jaune
                btn.configure(
                    fg_color=self.COLORS['yellow'],
                    text_color=self.COLORS['black'],
                    hover_color="#FFD700"
                )
            else:
                # Autres onglets - fond gris clair
                btn.configure(
                    fg_color=self.COLORS['gray'],
                    text_color=self.COLORS['text_gray'],
                    hover_color=self.COLORS['border']
                )

    def _clear_content(self):
        """Efface le contenu actuel"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _show_home_page(self):
        """Affiche la page d'accueil"""
        self._clear_content()
        self._highlight_nav_button('home')

        # Container principal centré
        home_container = ctk.CTkFrame(self.content_frame, fg_color=self.COLORS['white'])
        home_container.pack(fill='both', expand=True)

        # Spacer pour centrer verticalement
        top_spacer = ctk.CTkFrame(home_container, fg_color="transparent", height=100)
        top_spacer.pack()

        # Titre principal - style moderne
        title_frame = ctk.CTkFrame(home_container, fg_color="transparent")
        title_frame.pack(pady=20)

        title1 = ctk.CTkLabel(
            title_frame,
            text="Gérez vos",
            font=("Arial", 72, "bold"),
            text_color=self.COLORS['black']
        )
        title1.pack()

        # Mot clé avec fond jaune
        title2_bg = ctk.CTkFrame(title_frame, fg_color=self.COLORS['yellow'], corner_radius=8)
        title2_bg.pack(pady=10)

        title2 = ctk.CTkLabel(
            title2_bg,
            text="Prosits",
            font=("Arial", 72, "bold"),
            text_color=self.COLORS['black']
        )
        title2.pack(padx=30, pady=5)

        # Sous-titre
        subtitle = ctk.CTkLabel(
            home_container,
            text="Analysez, générez et organisez vos documents facilement",
            font=("Arial", 20),
            text_color=self.COLORS['text_gray']
        )
        subtitle.pack(pady=20)

        # Boutons d'action
        action_frame = ctk.CTkFrame(home_container, fg_color="transparent")
        action_frame.pack(pady=40)

        # Bouton principal
        start_btn = ctk.CTkButton(
            action_frame,
            text="Commencer →",
            font=("Arial", 18, "bold"),
            fg_color=self.COLORS['black'],
            text_color=self.COLORS['white'],
            hover_color="#333333",
            command=self._show_prosit_page,
            width=200,
            height=55,
            corner_radius=10
        )
        start_btn.pack(side='left', padx=10)

        # Bouton secondaire
        settings_btn = ctk.CTkButton(
            action_frame,
            text="Configurer",
            font=("Arial", 18),
            fg_color=self.COLORS['white'],
            text_color=self.COLORS['black'],
            hover_color=self.COLORS['gray'],
            border_width=2,
            border_color=self.COLORS['border'],
            command=self._show_settings_page,
            width=180,
            height=55,
            corner_radius=10
        )
        settings_btn.pack(side='left', padx=10)

        # Features
        features_frame = ctk.CTkFrame(home_container, fg_color="transparent")
        features_frame.pack(pady=60)

        features = [
            ("📝", "Analyse automatique", "Extraction intelligente des données"),
            ("⚡", "Génération rapide", "Documents en quelques secondes"),
            ("🎯", "Interface intuitive", "Simple et efficace")
        ]

        for emoji, title, desc in features:
            feature = ctk.CTkFrame(features_frame, fg_color=self.COLORS['gray'], corner_radius=15, width=280)
            feature.pack(side='left', padx=20)

            ctk.CTkLabel(
                feature,
                text=emoji,
                font=("Arial", 48)
            ).pack(pady=(30, 15))

            ctk.CTkLabel(
                feature,
                text=title,
                font=("Arial", 18, "bold"),
                text_color=self.COLORS['black']
            ).pack()

            ctk.CTkLabel(
                feature,
                text=desc,
                font=("Arial", 14),
                text_color=self.COLORS['text_gray']
            ).pack(pady=(5, 30), padx=20)

    def _show_prosit_page(self):
        """Affiche la page Prosit"""
        self._clear_content()
        self._highlight_nav_button('prosit')

        # Container principal avec max-width
        prosit_container = ctk.CTkFrame(self.content_frame, fg_color=self.COLORS['white'])
        prosit_container.pack(fill='both', expand=True, padx=80, pady=40)

        # En-tête
        header_frame = ctk.CTkFrame(prosit_container, fg_color="transparent")
        header_frame.pack(fill='x', pady=(0, 30))

        ctk.CTkLabel(
            header_frame,
            text="Prosit Manager",
            font=("Arial", 42, "bold"),
            text_color=self.COLORS['black']
        ).pack(side='left')

        # Boutons d'action dans le header
        action_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        action_frame.pack(side='right')

        self.clear_btn = ctk.CTkButton(
            action_frame,
            text="Effacer",
            command=self._clear_cr,
            fg_color=self.COLORS['white'],
            text_color=self.COLORS['text_gray'],
            hover_color=self.COLORS['gray'],
            border_width=2,
            border_color=self.COLORS['border'],
            width=100,
            height=40,
            corner_radius=8,
            font=("Arial", 14)
        )
        self.clear_btn.pack(side='left', padx=5)

        # Zone principale avec 2 colonnes
        main_frame = ctk.CTkFrame(prosit_container, fg_color="transparent")
        main_frame.pack(fill='both', expand=True)

        # Colonne gauche - Saisie du CR
        left_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 15))

        header_left = ctk.CTkFrame(left_frame, fg_color="transparent")
        header_left.pack(fill='x', pady=(0, 15))

        ctk.CTkLabel(
            header_left,
            text="Compte-Rendu",
            font=("Arial", 20, "bold"),
            text_color=self.COLORS['black']
        ).pack(side='left')

        self.cr_text = ctk.CTkTextbox(
            left_frame,
            wrap='word',
            font=("Consolas", 12),
            fg_color=self.COLORS['white'],
            text_color=self.COLORS['black'],
            border_width=2,
            border_color=self.COLORS['border'],
            corner_radius=10
        )
        self.cr_text.pack(fill='both', expand=True)

        # Bouton analyser sous le CR
        self.analyze_btn = ctk.CTkButton(
            left_frame,
            text="Analyser le CR →",
            command=self._analyze_cr,
            font=("Arial", 16, "bold"),
            height=50,
            fg_color=self.COLORS['yellow'],
            text_color=self.COLORS['black'],
            hover_color="#FFD700",
            corner_radius=10
        )
        self.analyze_btn.pack(fill='x', pady=(15, 0))

        # Colonne droite - Données extraites
        right_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        right_frame.pack(side='right', fill='both', expand=True, padx=(15, 0))

        header_right = ctk.CTkFrame(right_frame, fg_color="transparent")
        header_right.pack(fill='x', pady=(0, 15))

        ctk.CTkLabel(
            header_right,
            text="Données extraites",
            font=("Arial", 20, "bold"),
            text_color=self.COLORS['black']
        ).pack(side='left')

        self.result_text = ctk.CTkTextbox(
            right_frame,
            wrap='word',
            font=("Consolas", 12),
            fg_color=self.COLORS['gray'],
            text_color=self.COLORS['black'],
            border_width=0,
            corner_radius=10
        )
        self.result_text.pack(fill='both', expand=True)

        # Bouton génération
        self.generate_btn = ctk.CTkButton(
            right_frame,
            text="Générer le document",
            command=self._generate_document,
            font=("Arial", 16, "bold"),
            height=50,
            state='disabled',
            fg_color=self.COLORS['black'],
            text_color=self.COLORS['white'],
            hover_color="#333333",
            corner_radius=10
        )
        self.generate_btn.pack(fill='x', pady=(15, 0))

        # Barre de statut
        self.status_label = ctk.CTkLabel(
            prosit_container,
            text="Prêt à analyser",
            font=("Arial", 13),
            text_color=self.COLORS['text_gray']
        )
        self.status_label.pack(pady=(20, 0))

    def _show_settings_page(self):
        """Affiche la page des paramètres"""
        self._clear_content()
        self._highlight_nav_button('settings')

        # Container principal avec max-width
        settings_container = ctk.CTkFrame(self.content_frame, fg_color=self.COLORS['white'])
        settings_container.pack(fill='both', expand=True, padx=80, pady=40)

        # En-tête
        ctk.CTkLabel(
            settings_container,
            text="Paramètres",
            font=("Arial", 42, "bold"),
            text_color=self.COLORS['black']
        ).pack(anchor='w', pady=(0, 40))

        # Formulaire
        form_frame = ctk.CTkFrame(settings_container, fg_color=self.COLORS['white'])
        form_frame.pack(fill='both', expand=True)

        # Section Informations personnelles
        section1 = ctk.CTkLabel(
            form_frame,
            text="Informations personnelles",
            font=("Arial", 24, "bold"),
            text_color=self.COLORS['black']
        )
        section1.pack(anchor='w', pady=(0, 25))

        # Nom
        nom_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        nom_container.pack(fill='x', pady=15)

        ctk.CTkLabel(
            nom_container,
            text="Nom complet",
            font=("Arial", 15),
            text_color=self.COLORS['text_gray']
        ).pack(anchor='w', pady=(0, 8))

        self.nom_entry = ctk.CTkEntry(
            nom_container,
            height=50,
            font=("Arial", 14),
            fg_color=self.COLORS['white'],
            border_color=self.COLORS['border'],
            border_width=2,
            corner_radius=10
        )
        self.nom_entry.insert(0, self.config['nom'])
        self.nom_entry.pack(fill='x')

        # Formation
        formation_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        formation_container.pack(fill='x', pady=15)

        ctk.CTkLabel(
            formation_container,
            text="Formation",
            font=("Arial", 15),
            text_color=self.COLORS['text_gray']
        ).pack(anchor='w', pady=(0, 8))

        self.formation_entry = ctk.CTkEntry(
            formation_container,
            height=50,
            font=("Arial", 14),
            fg_color=self.COLORS['white'],
            border_color=self.COLORS['border'],
            border_width=2,
            corner_radius=10
        )
        self.formation_entry.insert(0, self.config['formation'])
        self.formation_entry.pack(fill='x')

        # Spacer
        ctk.CTkFrame(form_frame, fg_color="transparent", height=40).pack()

        # Section Template
        section2 = ctk.CTkLabel(
            form_frame,
            text="Template de document",
            font=("Arial", 24, "bold"),
            text_color=self.COLORS['black']
        )
        section2.pack(anchor='w', pady=(0, 25))

        # Template
        template_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        template_container.pack(fill='x', pady=15)

        ctk.CTkLabel(
            template_container,
            text="Chemin du template (.docx)",
            font=("Arial", 15),
            text_color=self.COLORS['text_gray']
        ).pack(anchor='w', pady=(0, 8))

        template_input_frame = ctk.CTkFrame(template_container, fg_color="transparent")
        template_input_frame.pack(fill='x')

        self.template_entry = ctk.CTkEntry(
            template_input_frame,
            height=50,
            font=("Arial", 14),
            fg_color=self.COLORS['white'],
            border_color=self.COLORS['border'],
            border_width=2,
            corner_radius=10
        )
        self.template_entry.insert(0, self.config['template_path'])
        self.template_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))

        self.browse_btn = ctk.CTkButton(
            template_input_frame,
            text="Parcourir",
            command=self._browse_template,
            width=140,
            height=50,
            fg_color=self.COLORS['white'],
            text_color=self.COLORS['black'],
            hover_color=self.COLORS['gray'],
            border_width=2,
            border_color=self.COLORS['border'],
            corner_radius=10,
            font=("Arial", 14)
        )
        self.browse_btn.pack(side='left')

        # Spacer
        ctk.CTkFrame(form_frame, fg_color="transparent", height=40).pack()

        # Bouton sauvegarder
        save_btn = ctk.CTkButton(
            form_frame,
            text="Sauvegarder la configuration",
            command=self._save_config,
            font=("Arial", 16, "bold"),
            height=55,
            fg_color=self.COLORS['yellow'],
            text_color=self.COLORS['black'],
            hover_color="#FFD700",
            corner_radius=10
        )
        save_btn.pack(anchor='w', pady=20)

    def _browse_template(self):
        """Ouvre un dialogue pour sélectionner le template"""
        filename = filedialog.askopenfilename(
            title="Sélectionner le template Word",
            filetypes=[("Word Documents", "*.docx"), ("All Files", "*.*")]
        )
        if filename:
            self.template_entry.delete(0, 'end')
            self.template_entry.insert(0, filename)
            self.config['template_path'] = filename

    def _analyze_cr(self):
        """Analyse le CR et extrait les données"""
        cr_text = self.cr_text.get("1.0", "end-1c").strip()

        if not cr_text:
            messagebox.showwarning("Attention", "Veuillez coller un compte-rendu avant d'analyser.")
            return

        try:
            self.status_label.configure(text="⏳ Analyse en cours...", text_color=self.COLORS['yellow'])
            self.root.update()

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
        self.status_label.configure(text="Prêt à analyser", text_color=self.COLORS['text_gray'])

    def _generate_document(self):
        """Génère le document Word à partir des données extraites"""
        if not self.parsed_data:
            messagebox.showwarning("Attention", "Veuillez d'abord analyser un compte-rendu.")
            return

        # Récupérer le template depuis la config ou le widget si disponible
        template_path = self.config['template_path']
        if self.template_entry and self.template_entry.winfo_exists():
            template_path = self.template_entry.get().strip()

        if not template_path or not os.path.exists(template_path):
            messagebox.showwarning("Attention", "Veuillez sélectionner un template valide dans les Settings.")
            return

        # Demander où sauvegarder
        default_name = f"Prosit_{self.parsed_data['prosit_number']}_{self.parsed_data['prosit_title'][:30]}.docx"
        default_name = default_name.replace('/', '_').replace('\\', '_')

        save_path = filedialog.asksaveasfilename(
            title="Enregistrer le document",
            defaultextension=".docx",
            initialfile=default_name,
            filetypes=[("Word Documents", "*.docx"), ("All Files", "*.*")]
        )

        if not save_path:
            return

        try:
            self.status_label.configure(text="⏳ Génération du document...", text_color=self.COLORS['yellow'])
            self.root.update()

            # Récupérer nom et formation depuis la config ou les widgets si disponibles
            nom = self.config['nom']
            formation = self.config['formation']

            if self.nom_entry and self.nom_entry.winfo_exists():
                nom = self.nom_entry.get()
            if self.formation_entry and self.formation_entry.winfo_exists():
                formation = self.formation_entry.get()

            # Générer le document
            self.generator.generate(
                template_path=template_path,
                output_path=save_path,
                data=self.parsed_data,
                nom=nom,
                formation=formation
            )

            self.status_label.configure(
                text=f"✓ Document généré: {os.path.basename(save_path)}",
                text_color="#10B981"
            )
            messagebox.showinfo("Succès", f"Document généré avec succès!\n\n{save_path}")

            # Demander si on veut ouvrir le fichier
            if messagebox.askyesno("Ouvrir le fichier", "Voulez-vous ouvrir le document généré?"):
                os.startfile(save_path)

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la génération:\n{str(e)}")
            self.status_label.configure(text="✗ Erreur lors de la génération", text_color="#EF4444")

    def _save_config(self):
        """Sauvegarde la configuration"""
        # Mettre à jour la config depuis les widgets si disponibles
        if self.nom_entry and self.nom_entry.winfo_exists():
            self.config['nom'] = self.nom_entry.get()
        if self.formation_entry and self.formation_entry.winfo_exists():
            self.config['formation'] = self.formation_entry.get()
        if self.template_entry and self.template_entry.winfo_exists():
            self.config['template_path'] = self.template_entry.get()

        try:
            # Sauvegarder dans un fichier config
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config.txt')
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(f"nom={self.config['nom']}\n")
                f.write(f"formation={self.config['formation']}\n")
                f.write(f"template_path={self.config['template_path']}\n")

            messagebox.showinfo("Succès", "Configuration sauvegardée avec succès!")

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde:\n{str(e)}")

    def _load_config(self):
        """Charge la configuration sauvegardée"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config.txt')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            if key in self.config:
                                self.config[key] = value

        except Exception as e:
            print(f"Erreur lors du chargement de la config: {e}")

    def run(self):
        """Lance l'application"""
        self.root.mainloop()
