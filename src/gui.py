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
from .config_manager import ConfigManager
from .settings_components import SettingsSection, FormField, AboutSection


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

        # Gestionnaire de configuration
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        self.app_info = self.config_manager.load_app_info()

        # Page actuelle
        self.current_page = None

        # Références aux widgets de configuration (créés dans Settings)
        self.prenom_entry = None
        self.nom_entry = None
        self.email_entry = None
        self.formation_entry = None
        self.template_entry = None

        # Créer l'interface
        self._create_main_layout()

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
            segment = ctk.CTkFrame(self.sidebar, fg_color=self.COLORS['gray'], height=100, corner_radius=0)
            segment.pack(fill='x', pady=0, padx=0)
            segment.pack_propagate(False)

            # Icône grande
            icon_label = ctk.CTkLabel(
                segment,
                text=icon,
                font=("Arial", 48),
                text_color=self.COLORS['text_gray']
            )
            icon_label.pack(pady=(15, 2))

            # Texte petit
            text_label = ctk.CTkLabel(
                segment,
                text=text,
                font=("Arial", 7),
                text_color=self.COLORS['text_gray']
            )
            text_label.pack(pady=(0, 5))

            # Rendre le segment cliquable
            if command:
                segment.bind("<Button-1>", lambda e, cmd=command: cmd())
                icon_label.bind("<Button-1>", lambda e, cmd=command: cmd())
                text_label.bind("<Button-1>", lambda e, cmd=command: cmd())

            self.nav_buttons[key] = segment
            self.nav_labels[key] = {'icon': icon_label, 'text': text_label}

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
        for name in self.nav_buttons.keys():
            if name == 'settings':  # Skip settings button (in header)
                continue

            # Le segment est maintenant directement stocké dans nav_buttons
            segment = self.nav_buttons[name]

            if name == button_name:
                # Onglet actuel - segment entier en jaune
                segment.configure(fg_color=self.COLORS['yellow'])
                if name in self.nav_labels:
                    self.nav_labels[name]['icon'].configure(text_color=self.COLORS['black'])
                    self.nav_labels[name]['text'].configure(text_color=self.COLORS['black'])
            else:
                # Autres onglets - segment en gris clair
                segment.configure(fg_color=self.COLORS['gray'])
                if name in self.nav_labels:
                    self.nav_labels[name]['icon'].configure(text_color=self.COLORS['text_gray'])
                    self.nav_labels[name]['text'].configure(text_color=self.COLORS['text_gray'])

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

        # Container principal avec scrollbar
        settings_container = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color=self.COLORS['white']
        )
        settings_container.pack(fill='both', expand=True, padx=60, pady=30)

        # En-tête
        ctk.CTkLabel(
            settings_container,
            text="Paramètres",
            font=("Arial", 36, "bold"),
            text_color=self.COLORS['black']
        ).pack(anchor='w', pady=(0, 30))

        # ===== SECTION GÉNÉRAL =====
        general_section = SettingsSection.create(settings_container, "Général", self.COLORS)

        # Prénom
        self.prenom_entry = FormField.create_text_field(
            general_section,
            "Prénom",
            "Votre prénom",
            self.config.get('prenom', ''),
            self.COLORS
        )

        # Nom
        self.nom_entry = FormField.create_text_field(
            general_section,
            "Nom",
            "Votre nom",
            self.config.get('nom', ''),
            self.COLORS
        )

        # Email
        self.email_entry = FormField.create_text_field(
            general_section,
            "Email",
            "votre.email@example.com",
            self.config.get('email', ''),
            self.COLORS
        )

        # Formation
        self.formation_entry = FormField.create_text_field(
            general_section,
            "Formation",
            "Ex: A3 FISA INFO",
            self.config.get('formation', ''),
            self.COLORS
        )

        # Spacer
        ctk.CTkFrame(general_section, fg_color="transparent", height=10).pack()

        # ===== SECTION PROSIT MANAGEMENT =====
        prosit_section = SettingsSection.create(settings_container, "Prosit Management", self.COLORS)

        # Template
        self.template_entry = FormField.create_file_field(
            prosit_section,
            "Template de document (.docx)",
            self.config.get('template_path', ''),
            self._browse_template,
            self.COLORS
        )

        # Spacer
        ctk.CTkFrame(prosit_section, fg_color="transparent", height=10).pack()

        # Bouton sauvegarder
        save_btn = ctk.CTkButton(
            settings_container,
            text="💾 Sauvegarder la configuration",
            command=self._save_config,
            font=("Arial", 14, "bold"),
            height=50,
            fg_color=self.COLORS['yellow'],
            text_color=self.COLORS['black'],
            hover_color="#FFD700",
            corner_radius=10
        )
        save_btn.pack(fill='x', pady=(20, 30))

        # ===== SECTION À PROPOS =====
        AboutSection.create(settings_container, self.app_info, self.COLORS)

    def _browse_template(self, entry_widget):
        """Ouvre un dialogue pour sélectionner le template"""
        filename = filedialog.askopenfilename(
            title="Sélectionner le template Word",
            filetypes=[("Word Documents", "*.docx"), ("All Files", "*.*")]
        )
        if filename:
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, filename)

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

        # Utiliser le ConfigManager pour sauvegarder
        if self.config_manager.save_config(self.config):
            messagebox.showinfo("Succès", "Configuration sauvegardée avec succès!")
        else:
            messagebox.showerror("Erreur", "Erreur lors de la sauvegarde de la configuration")

    def run(self):
        """Lance l'application"""
        self.root.mainloop()
