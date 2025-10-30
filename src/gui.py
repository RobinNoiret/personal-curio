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

    def __init__(self):
        # Configuration du thème
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Fenêtre principale
        self.root = ctk.CTk()
        self.root.title("Prosit Manager")
        self.root.geometry("1200x800")

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

        # Créer l'interface
        self._create_widgets()
        self._load_config()

    def _create_widgets(self):
        """Crée tous les widgets de l'interface"""

        # === En-tête avec configuration ===
        header_frame = ctk.CTkFrame(self.root)
        header_frame.pack(fill='x', padx=10, pady=10)

        # Nom
        ctk.CTkLabel(header_frame, text="Nom:", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.nom_entry = ctk.CTkEntry(header_frame, width=200)
        self.nom_entry.insert(0, self.config['nom'])
        self.nom_entry.grid(row=0, column=1, padx=5, pady=5)

        # Formation
        ctk.CTkLabel(header_frame, text="Formation:", font=("Arial", 12, "bold")).grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.formation_entry = ctk.CTkEntry(header_frame, width=200)
        self.formation_entry.insert(0, self.config['formation'])
        self.formation_entry.grid(row=0, column=3, padx=5, pady=5)

        # Template
        ctk.CTkLabel(header_frame, text="Template:", font=("Arial", 12, "bold")).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.template_entry = ctk.CTkEntry(header_frame, width=400)
        self.template_entry.insert(0, self.config['template_path'])
        self.template_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5)

        self.browse_btn = ctk.CTkButton(header_frame, text="Parcourir", command=self._browse_template, width=100)
        self.browse_btn.grid(row=1, column=3, padx=5, pady=5)

        # Bouton sauvegarder config
        self.save_config_btn = ctk.CTkButton(header_frame, text="Sauvegarder config", command=self._save_config, width=150)
        self.save_config_btn.grid(row=0, column=4, padx=5, pady=5)

        # === Zone principale avec 2 colonnes ===
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Colonne gauche - Saisie du CR
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=5)

        ctk.CTkLabel(left_frame, text="Compte-Rendu de réunion", font=("Arial", 16, "bold")).pack(pady=10)

        self.cr_text = ctk.CTkTextbox(left_frame, wrap='word', font=("Consolas", 11))
        self.cr_text.pack(fill='both', expand=True, padx=10, pady=10)

        # Boutons d'action
        btn_frame = ctk.CTkFrame(left_frame)
        btn_frame.pack(fill='x', padx=10, pady=5)

        self.analyze_btn = ctk.CTkButton(btn_frame, text="Analyser le CR", command=self._analyze_cr,
                                         font=("Arial", 14, "bold"), height=40)
        self.analyze_btn.pack(side='left', expand=True, padx=5)

        self.clear_btn = ctk.CTkButton(btn_frame, text="Effacer", command=self._clear_cr,
                                       fg_color="gray", hover_color="darkgray", width=100)
        self.clear_btn.pack(side='left', padx=5)

        # Colonne droite - Données extraites
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=5)

        ctk.CTkLabel(right_frame, text="Données extraites", font=("Arial", 16, "bold")).pack(pady=10)

        self.result_text = ctk.CTkTextbox(right_frame, wrap='word', font=("Consolas", 11))
        self.result_text.pack(fill='both', expand=True, padx=10, pady=10)

        # Bouton génération
        self.generate_btn = ctk.CTkButton(right_frame, text="Générer le document Word",
                                          command=self._generate_document,
                                          font=("Arial", 14, "bold"), height=40,
                                          state='disabled')
        self.generate_btn.pack(fill='x', padx=10, pady=10)

        # === Barre de statut ===
        self.status_label = ctk.CTkLabel(self.root, text="Prêt", font=("Arial", 10))
        self.status_label.pack(side='bottom', fill='x', padx=10, pady=5)

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

            self.status_label.configure(text="✓ Analyse terminée avec succès")

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'analyse:\n{str(e)}")
            self.status_label.configure(text="✗ Erreur lors de l'analyse")

    def _clear_cr(self):
        """Efface le contenu du CR"""
        self.cr_text.delete("1.0", "end")
        self.result_text.delete("1.0", "end")
        self.parsed_data = None
        self.generate_btn.configure(state='disabled')
        self.status_label.configure(text="Prêt")

    def _generate_document(self):
        """Génère le document Word à partir des données extraites"""
        if not self.parsed_data:
            messagebox.showwarning("Attention", "Veuillez d'abord analyser un compte-rendu.")
            return

        template_path = self.template_entry.get().strip()
        if not template_path or not os.path.exists(template_path):
            messagebox.showwarning("Attention", "Veuillez sélectionner un template valide.")
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
            # Générer le document
            self.generator.generate(
                template_path=template_path,
                output_path=save_path,
                data=self.parsed_data,
                nom=self.nom_entry.get(),
                formation=self.formation_entry.get()
            )

            self.status_label.configure(text=f"✓ Document généré: {os.path.basename(save_path)}")
            messagebox.showinfo("Succès", f"Document généré avec succès!\n\n{save_path}")

            # Demander si on veut ouvrir le fichier
            if messagebox.askyesno("Ouvrir le fichier", "Voulez-vous ouvrir le document généré?"):
                os.startfile(save_path)

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la génération:\n{str(e)}")
            self.status_label.configure(text="✗ Erreur lors de la génération")

    def _save_config(self):
        """Sauvegarde la configuration"""
        self.config['nom'] = self.nom_entry.get()
        self.config['formation'] = self.formation_entry.get()
        self.config['template_path'] = self.template_entry.get()

        try:
            # Sauvegarder dans un fichier config
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config.txt')
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(f"nom={self.config['nom']}\n")
                f.write(f"formation={self.config['formation']}\n")
                f.write(f"template_path={self.config['template_path']}\n")

            self.status_label.configure(text="✓ Configuration sauvegardée")
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

                # Mettre à jour les champs
                self.nom_entry.delete(0, 'end')
                self.nom_entry.insert(0, self.config['nom'])

                self.formation_entry.delete(0, 'end')
                self.formation_entry.insert(0, self.config['formation'])

                self.template_entry.delete(0, 'end')
                self.template_entry.insert(0, self.config['template_path'])

        except Exception as e:
            print(f"Erreur lors du chargement de la config: {e}")

    def run(self):
        """Lance l'application"""
        self.root.mainloop()
