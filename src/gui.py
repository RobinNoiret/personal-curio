"""
Interface graphique pour le gestionnaire de prosits
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from typing import Dict, Optional
from .cr_parser import CRParser
from .docx_generator import DocxGenerator


class PrositManagerGUI:
    """Interface graphique principale de l'application"""

    # Palette de couleurs
    COLORS = {
        'yellow': '#FFC92C',
        'white': '#FFFFFF',
        'black': '#1A1A18',
        'gray': '#F5F5F5',
        'dark_gray': '#333333'
    }

    def __init__(self):
        # Configuration du thème
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Fenêtre principale
        self.root = ctk.CTk()
        self.root.title("Prosit Manager")
        self.root.geometry("1400x900")
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
        """Crée la structure principale avec navbar et zone de contenu"""

        # Container principal
        main_container = ctk.CTkFrame(self.root, fg_color=self.COLORS['white'])
        main_container.pack(fill='both', expand=True)

        # === Navbar verticale à gauche ===
        self.navbar = ctk.CTkFrame(main_container, width=200, fg_color=self.COLORS['black'])
        self.navbar.pack(side='left', fill='y', padx=0, pady=0)
        self.navbar.pack_propagate(False)

        # Logo/Titre dans la navbar
        title_label = ctk.CTkLabel(
            self.navbar,
            text="PROSIT\nMANAGER",
            font=("Arial", 20, "bold"),
            text_color=self.COLORS['yellow']
        )
        title_label.pack(pady=30)

        # Séparateur
        separator = ctk.CTkFrame(self.navbar, height=2, fg_color=self.COLORS['yellow'])
        separator.pack(fill='x', padx=20, pady=10)

        # Boutons de navigation
        self.nav_buttons = {}

        # Bouton Accueil
        self.nav_buttons['home'] = ctk.CTkButton(
            self.navbar,
            text="🏠 Accueil",
            font=("Arial", 14),
            fg_color="transparent",
            text_color=self.COLORS['white'],
            hover_color=self.COLORS['dark_gray'],
            anchor='w',
            command=self._show_home_page,
            height=50
        )
        self.nav_buttons['home'].pack(fill='x', padx=10, pady=5)

        # Bouton Prosit
        self.nav_buttons['prosit'] = ctk.CTkButton(
            self.navbar,
            text="📝 Prosit",
            font=("Arial", 14),
            fg_color="transparent",
            text_color=self.COLORS['white'],
            hover_color=self.COLORS['dark_gray'],
            anchor='w',
            command=self._show_prosit_page,
            height=50
        )
        self.nav_buttons['prosit'].pack(fill='x', padx=10, pady=5)

        # Spacer pour pousser Settings en bas
        spacer = ctk.CTkFrame(self.navbar, fg_color="transparent")
        spacer.pack(fill='both', expand=True)

        # Bouton Settings (en bas)
        self.nav_buttons['settings'] = ctk.CTkButton(
            self.navbar,
            text="⚙️ Settings",
            font=("Arial", 14),
            fg_color="transparent",
            text_color=self.COLORS['white'],
            hover_color=self.COLORS['dark_gray'],
            anchor='w',
            command=self._show_settings_page,
            height=50
        )
        self.nav_buttons['settings'].pack(fill='x', padx=10, pady=10, side='bottom')

        # === Zone de contenu principale ===
        self.content_frame = ctk.CTkFrame(main_container, fg_color=self.COLORS['white'])
        self.content_frame.pack(side='right', fill='both', expand=True, padx=0, pady=0)

    def _highlight_nav_button(self, button_name: str):
        """Met en surbrillance le bouton de navigation actif"""
        for name, btn in self.nav_buttons.items():
            if name == button_name:
                btn.configure(fg_color=self.COLORS['yellow'], text_color=self.COLORS['black'])
            else:
                btn.configure(fg_color="transparent", text_color=self.COLORS['white'])

    def _clear_content(self):
        """Efface le contenu actuel"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _show_home_page(self):
        """Affiche la page d'accueil"""
        self._clear_content()
        self._highlight_nav_button('home')

        # Container de la page d'accueil
        home_container = ctk.CTkFrame(self.content_frame, fg_color=self.COLORS['white'])
        home_container.pack(fill='both', expand=True, padx=40, pady=40)

        # Titre principal
        title = ctk.CTkLabel(
            home_container,
            text="Bienvenue sur Prosit Manager",
            font=("Arial", 36, "bold"),
            text_color=self.COLORS['black']
        )
        title.pack(pady=(50, 20))

        # Sous-titre avec accent jaune
        subtitle_frame = ctk.CTkFrame(home_container, fg_color=self.COLORS['yellow'])
        subtitle_frame.pack(pady=10)

        subtitle = ctk.CTkLabel(
            subtitle_frame,
            text="Votre outil de gestion de prosits",
            font=("Arial", 20),
            text_color=self.COLORS['black']
        )
        subtitle.pack(padx=30, pady=10)

        # Description
        description = ctk.CTkLabel(
            home_container,
            text="Gérez vos prosits efficacement avec des outils dédiés",
            font=("Arial", 14),
            text_color=self.COLORS['dark_gray']
        )
        description.pack(pady=30)

        # Cartes d'actions rapides
        cards_frame = ctk.CTkFrame(home_container, fg_color="transparent")
        cards_frame.pack(pady=30)

        # Card Prosit
        prosit_card = ctk.CTkFrame(cards_frame, fg_color=self.COLORS['gray'], corner_radius=15)
        prosit_card.pack(side='left', padx=15)

        ctk.CTkLabel(
            prosit_card,
            text="📝",
            font=("Arial", 48)
        ).pack(pady=(20, 10))

        ctk.CTkLabel(
            prosit_card,
            text="Prosit",
            font=("Arial", 18, "bold"),
            text_color=self.COLORS['black']
        ).pack()

        ctk.CTkLabel(
            prosit_card,
            text="Analyser et générer\nvos documents prosit",
            font=("Arial", 12),
            text_color=self.COLORS['dark_gray']
        ).pack(pady=10)

        ctk.CTkButton(
            prosit_card,
            text="Accéder",
            font=("Arial", 14, "bold"),
            fg_color=self.COLORS['yellow'],
            text_color=self.COLORS['black'],
            hover_color="#FFD700",
            command=self._show_prosit_page,
            width=150,
            height=40
        ).pack(pady=20, padx=20)

    def _show_prosit_page(self):
        """Affiche la page Prosit"""
        self._clear_content()
        self._highlight_nav_button('prosit')

        # Container principal
        prosit_container = ctk.CTkFrame(self.content_frame, fg_color=self.COLORS['white'])
        prosit_container.pack(fill='both', expand=True, padx=20, pady=20)

        # En-tête
        header = ctk.CTkLabel(
            prosit_container,
            text="📝 Prosit Manager",
            font=("Arial", 28, "bold"),
            text_color=self.COLORS['black']
        )
        header.pack(pady=(10, 20))

        # Zone principale avec 2 colonnes
        main_frame = ctk.CTkFrame(prosit_container, fg_color="transparent")
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Colonne gauche - Saisie du CR
        left_frame = ctk.CTkFrame(main_frame, fg_color=self.COLORS['gray'], corner_radius=10)
        left_frame.pack(side='left', fill='both', expand=True, padx=5)

        ctk.CTkLabel(
            left_frame,
            text="Compte-Rendu de réunion",
            font=("Arial", 16, "bold"),
            text_color=self.COLORS['black']
        ).pack(pady=15)

        self.cr_text = ctk.CTkTextbox(
            left_frame,
            wrap='word',
            font=("Consolas", 11),
            fg_color=self.COLORS['white'],
            text_color=self.COLORS['black'],
            border_width=2,
            border_color=self.COLORS['yellow']
        )
        self.cr_text.pack(fill='both', expand=True, padx=15, pady=10)

        # Boutons d'action
        btn_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_frame.pack(fill='x', padx=15, pady=15)

        self.analyze_btn = ctk.CTkButton(
            btn_frame,
            text="Analyser le CR",
            command=self._analyze_cr,
            font=("Arial", 14, "bold"),
            height=45,
            fg_color=self.COLORS['yellow'],
            text_color=self.COLORS['black'],
            hover_color="#FFD700"
        )
        self.analyze_btn.pack(side='left', expand=True, padx=5)

        self.clear_btn = ctk.CTkButton(
            btn_frame,
            text="Effacer",
            command=self._clear_cr,
            fg_color=self.COLORS['dark_gray'],
            hover_color="#555555",
            width=100,
            height=45,
            text_color=self.COLORS['white']
        )
        self.clear_btn.pack(side='left', padx=5)

        # Colonne droite - Données extraites
        right_frame = ctk.CTkFrame(main_frame, fg_color=self.COLORS['gray'], corner_radius=10)
        right_frame.pack(side='right', fill='both', expand=True, padx=5)

        ctk.CTkLabel(
            right_frame,
            text="Données extraites",
            font=("Arial", 16, "bold"),
            text_color=self.COLORS['black']
        ).pack(pady=15)

        self.result_text = ctk.CTkTextbox(
            right_frame,
            wrap='word',
            font=("Consolas", 11),
            fg_color=self.COLORS['white'],
            text_color=self.COLORS['black'],
            border_width=2,
            border_color=self.COLORS['yellow']
        )
        self.result_text.pack(fill='both', expand=True, padx=15, pady=10)

        # Bouton génération
        self.generate_btn = ctk.CTkButton(
            right_frame,
            text="Générer le document Word",
            command=self._generate_document,
            font=("Arial", 14, "bold"),
            height=45,
            state='disabled',
            fg_color=self.COLORS['yellow'],
            text_color=self.COLORS['black'],
            hover_color="#FFD700"
        )
        self.generate_btn.pack(fill='x', padx=15, pady=15)

        # Barre de statut
        self.status_label = ctk.CTkLabel(
            prosit_container,
            text="Prêt",
            font=("Arial", 11),
            text_color=self.COLORS['dark_gray']
        )
        self.status_label.pack(side='bottom', pady=10)

    def _show_settings_page(self):
        """Affiche la page des paramètres"""
        self._clear_content()
        self._highlight_nav_button('settings')

        # Container principal
        settings_container = ctk.CTkFrame(self.content_frame, fg_color=self.COLORS['white'])
        settings_container.pack(fill='both', expand=True, padx=40, pady=40)

        # En-tête
        header = ctk.CTkLabel(
            settings_container,
            text="⚙️ Paramètres",
            font=("Arial", 28, "bold"),
            text_color=self.COLORS['black']
        )
        header.pack(pady=(10, 30))

        # Frame pour les paramètres
        settings_frame = ctk.CTkFrame(settings_container, fg_color=self.COLORS['gray'], corner_radius=15)
        settings_frame.pack(fill='both', expand=True, padx=50, pady=20)

        # Section Informations personnelles
        section1 = ctk.CTkLabel(
            settings_frame,
            text="Informations personnelles",
            font=("Arial", 18, "bold"),
            text_color=self.COLORS['black']
        )
        section1.pack(pady=(30, 15), padx=30, anchor='w')

        # Nom
        nom_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        nom_frame.pack(fill='x', padx=30, pady=10)

        ctk.CTkLabel(
            nom_frame,
            text="Nom complet:",
            font=("Arial", 14),
            text_color=self.COLORS['black'],
            width=150,
            anchor='w'
        ).pack(side='left', padx=(0, 20))

        self.nom_entry = ctk.CTkEntry(
            nom_frame,
            width=400,
            height=40,
            font=("Arial", 12),
            fg_color=self.COLORS['white'],
            border_color=self.COLORS['yellow'],
            border_width=2
        )
        self.nom_entry.insert(0, self.config['nom'])
        self.nom_entry.pack(side='left')

        # Formation
        formation_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        formation_frame.pack(fill='x', padx=30, pady=10)

        ctk.CTkLabel(
            formation_frame,
            text="Formation:",
            font=("Arial", 14),
            text_color=self.COLORS['black'],
            width=150,
            anchor='w'
        ).pack(side='left', padx=(0, 20))

        self.formation_entry = ctk.CTkEntry(
            formation_frame,
            width=400,
            height=40,
            font=("Arial", 12),
            fg_color=self.COLORS['white'],
            border_color=self.COLORS['yellow'],
            border_width=2
        )
        self.formation_entry.insert(0, self.config['formation'])
        self.formation_entry.pack(side='left')

        # Séparateur
        separator = ctk.CTkFrame(settings_frame, height=2, fg_color=self.COLORS['yellow'])
        separator.pack(fill='x', padx=30, pady=30)

        # Section Template
        section2 = ctk.CTkLabel(
            settings_frame,
            text="Template de document",
            font=("Arial", 18, "bold"),
            text_color=self.COLORS['black']
        )
        section2.pack(pady=(0, 15), padx=30, anchor='w')

        # Template
        template_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        template_frame.pack(fill='x', padx=30, pady=10)

        ctk.CTkLabel(
            template_frame,
            text="Chemin du template:",
            font=("Arial", 14),
            text_color=self.COLORS['black'],
            width=150,
            anchor='w'
        ).pack(side='left', padx=(0, 20))

        self.template_entry = ctk.CTkEntry(
            template_frame,
            width=400,
            height=40,
            font=("Arial", 12),
            fg_color=self.COLORS['white'],
            border_color=self.COLORS['yellow'],
            border_width=2
        )
        self.template_entry.insert(0, self.config['template_path'])
        self.template_entry.pack(side='left', padx=(0, 10))

        self.browse_btn = ctk.CTkButton(
            template_frame,
            text="Parcourir",
            command=self._browse_template,
            width=120,
            height=40,
            fg_color=self.COLORS['black'],
            text_color=self.COLORS['white'],
            hover_color=self.COLORS['dark_gray']
        )
        self.browse_btn.pack(side='left')

        # Bouton sauvegarder
        save_btn = ctk.CTkButton(
            settings_frame,
            text="💾 Sauvegarder la configuration",
            command=self._save_config,
            font=("Arial", 16, "bold"),
            height=50,
            fg_color=self.COLORS['yellow'],
            text_color=self.COLORS['black'],
            hover_color="#FFD700"
        )
        save_btn.pack(pady=30, padx=30)

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
            # Parser le CR
            self.parsed_data = self.parser.parse(cr_text)

            # Afficher les résultats
            formatted_result = self.parser.format_for_display(self.parsed_data)
            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", formatted_result)

            # Activer le bouton de génération
            self.generate_btn.configure(state='normal')

            self.status_label.configure(text="✓ Analyse terminée avec succès", text_color=self.COLORS['yellow'])

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'analyse:\n{str(e)}")
            self.status_label.configure(text="✗ Erreur lors de l'analyse", text_color="red")

    def _clear_cr(self):
        """Efface le contenu du CR"""
        self.cr_text.delete("1.0", "end")
        self.result_text.delete("1.0", "end")
        self.parsed_data = None
        self.generate_btn.configure(state='disabled')
        self.status_label.configure(text="Prêt", text_color=self.COLORS['dark_gray'])

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
                text_color=self.COLORS['yellow']
            )
            messagebox.showinfo("Succès", f"Document généré avec succès!\n\n{save_path}")

            # Demander si on veut ouvrir le fichier
            if messagebox.askyesno("Ouvrir le fichier", "Voulez-vous ouvrir le document généré?"):
                os.startfile(save_path)

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la génération:\n{str(e)}")
            self.status_label.configure(text="✗ Erreur lors de la génération", text_color="red")

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
