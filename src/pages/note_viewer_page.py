"""
Page de visualisation d'une note Obsidian
"""
import customtkinter as ctk
import re
import yaml
import os
import subprocess
import platform
from typing import Dict, Tuple, Optional
from .base_page import BasePage
from ..ui_components import Button, Container, Label
from ..utils.obsidian_scanner import ObsidianVaultScanner


class NoteViewerPage(BasePage):
    """Page de visualisation d'une note Obsidian"""

    def __init__(self, parent, colors: Dict, note_name: str, notes_path: str, on_navigate=None):
        super().__init__(parent, colors, on_navigate)
        self.note_name = note_name
        self.notes_path = notes_path

    def _open_in_obsidian(self):
        """Ouvre la note dans Obsidian"""
        try:
            # Chercher le fichier de la note
            scanner = ObsidianVaultScanner(self.notes_path)
            import glob
            note_file = None
            for md_file in glob.glob(os.path.join(self.notes_path, '**', f'{self.note_name}.md'), recursive=True):
                note_file = md_file
                break

            if not note_file:
                return

            # Utiliser l'URI scheme d'Obsidian
            # Format: obsidian://open?path=chemin_encodé
            import urllib.parse
            encoded_path = urllib.parse.quote(note_file)
            obsidian_uri = f"obsidian://open?path={encoded_path}"

            # Ouvrir l'URI selon l'OS
            system = platform.system()
            if system == "Windows":
                os.startfile(obsidian_uri)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", obsidian_uri])
            else:  # Linux
                subprocess.run(["xdg-open", obsidian_uri])

        except Exception as e:
            print(f"Erreur lors de l'ouverture dans Obsidian: {e}")

    def _parse_note_content(self, content: str) -> Tuple[Optional[Dict], str]:
        """
        Parse le contenu d'une note pour séparer le frontmatter YAML et le markdown

        Returns:
            Tuple (frontmatter_dict, markdown_content)
        """
        # Regex pour détecter le frontmatter YAML (entre --- ... ---)
        frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
        match = re.match(frontmatter_pattern, content, re.DOTALL)

        if match:
            yaml_content = match.group(1)
            markdown_content = match.group(2)

            try:
                frontmatter = yaml.safe_load(yaml_content)
                return frontmatter, markdown_content
            except:
                # Si le parsing YAML échoue, retourner le contenu brut
                return None, content
        else:
            # Pas de frontmatter
            return None, content

    def _clean_obsidian_links(self, text: str) -> str:
        """Nettoie les liens Obsidian [[ ]] pour afficher juste le texte"""
        # Remplacer [[Lien]] par Lien
        text = re.sub(r'\[\[([^\]]+)\]\]', r'\1', text)
        return text

    def _render_frontmatter(self, parent, frontmatter: Dict):
        """Affiche le frontmatter de manière structurée et jolie (replié par défaut)"""
        # Container pour le frontmatter
        frontmatter_frame = ctk.CTkFrame(
            parent,
            fg_color=self.colors['gray'],
            corner_radius=15
        )
        frontmatter_frame.pack(fill='x', pady=(0, 20))

        # Header cliquable pour déplier/replier
        header_frame = ctk.CTkFrame(frontmatter_frame, fg_color="transparent")
        header_frame.pack(fill='x', padx=25, pady=(20, 10))

        # Variable pour l'état
        expanded = [False]

        # Label titre cliquable
        toggle_label = ctk.CTkLabel(
            header_frame,
            text="▶ Métadonnées",
            font=("Arial", 16, "bold"),
            text_color=self.colors['black'],
            anchor='w',
            cursor="hand2"
        )
        toggle_label.pack(anchor='w')

        # Container pour le contenu (caché par défaut)
        content_frame = ctk.CTkFrame(frontmatter_frame, fg_color="transparent")

        # Afficher chaque champ dans le content_frame
        for key, value in frontmatter.items():
            field_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            field_frame.pack(fill='x', pady=5, padx=25)

            # Clé
            ctk.CTkLabel(
                field_frame,
                text=f"{key.capitalize()}:",
                font=("Arial", 13, "bold"),
                text_color=self.colors['text_gray'],
                width=120,
                anchor='w'
            ).pack(side='left', padx=(0, 10))

            # Valeur
            if isinstance(value, list):
                # Pour les listes (tags, related, etc.)
                value_text = ", ".join(self._clean_obsidian_links(str(v)) for v in value) if value else "—"
            else:
                value_text = self._clean_obsidian_links(str(value)) if value else "—"

            ctk.CTkLabel(
                field_frame,
                text=value_text,
                font=("Arial", 13),
                text_color=self.colors['black'],
                anchor='w',
                wraplength=500
            ).pack(side='left', fill='x', expand=True)

        # Fonction pour basculer
        def toggle_metadata():
            if expanded[0]:
                content_frame.pack_forget()
                toggle_label.configure(text="▶ Métadonnées")
                expanded[0] = False
            else:
                content_frame.pack(fill='x', pady=(0, 20))
                toggle_label.configure(text="▼ Métadonnées")
                expanded[0] = True

        toggle_label.bind("<Button-1>", lambda e: toggle_metadata())

    def _render_markdown(self, parent, markdown: str):
        """Affiche le contenu markdown de manière formatée"""
        # Container pour le markdown
        markdown_frame = ctk.CTkFrame(
            parent,
            fg_color=self.colors['gray'],
            corner_radius=15
        )
        markdown_frame.pack(fill='both', expand=True)

        inner = Container.transparent(markdown_frame)
        inner.pack(fill='both', expand=True, padx=25, pady=20)

        # Parser et afficher le markdown section par section
        lines = markdown.strip().split('\n')

        for line in lines:
            line = line.rstrip()

            # Headers (### Définition, etc.)
            if line.startswith('###'):
                text = line.replace('###', '').strip()
                # Nettoyer les liens Obsidian
                text = self._clean_obsidian_links(text)
                ctk.CTkLabel(
                    inner,
                    text=text,
                    font=("Arial", 18, "bold"),
                    text_color=self.colors['black'],
                    anchor='w'
                ).pack(anchor='w', pady=(15, 10))

            # Séparateurs (___,  ----)
            elif line.strip() in ['___', '---', '____']:
                ctk.CTkFrame(
                    inner,
                    height=2,
                    fg_color=self.colors['border']
                ).pack(fill='x', pady=10)

            # Listes (- item)
            elif line.strip().startswith('- '):
                text = line.strip()[2:]  # Enlever le "- "
                if text:  # Si pas vide
                    # Nettoyer les liens Obsidian
                    text = self._clean_obsidian_links(text)
                    bullet_frame = ctk.CTkFrame(inner, fg_color="transparent")
                    bullet_frame.pack(fill='x', pady=2, padx=(15, 0))

                    ctk.CTkLabel(
                        bullet_frame,
                        text=f"• {text}",
                        font=("Arial", 14),
                        text_color=self.colors['black'],
                        anchor='w',
                        wraplength=650
                    ).pack(anchor='w')

            # Lignes vides
            elif not line.strip():
                ctk.CTkLabel(inner, text="", height=5).pack()

            # Texte normal
            else:
                if line.strip():  # Ne pas afficher les lignes complètement vides
                    # Nettoyer les liens Obsidian
                    cleaned_line = self._clean_obsidian_links(line)
                    ctk.CTkLabel(
                        inner,
                        text=cleaned_line,
                        font=("Arial", 14),
                        text_color=self.colors['black'],
                        anchor='w',
                        wraplength=650,
                        justify='left'
                    ).pack(anchor='w', pady=3, fill='x')

    def render(self) -> ctk.CTkFrame:
        """Rend la page de visualisation"""
        self.container = ctk.CTkFrame(self.parent, fg_color=self.colors['white'])
        self.container.pack(fill='both', expand=True)

        # En-tête avec bouton retour
        header = ctk.CTkFrame(self.container, fg_color=self.colors['white'], height=80)
        header.pack(fill='x', padx=40, pady=(30, 0))
        header.pack_propagate(False)

        # Bouton retour
        Button.outline(
            header,
            "← Retour à l'accueil",
            lambda: self.on_navigate('home') if self.on_navigate else None,
            width=160,
            height=40
        ).pack(side='left', pady=20)

        # Bouton ouvrir dans Obsidian
        ctk.CTkButton(
            header,
            text="Ouvrir dans Obsidian",
            command=self._open_in_obsidian,
            font=("Arial", 13, "bold"),
            fg_color=self.colors['yellow'],
            hover_color="#FFD700",
            text_color=self.colors['black'],
            width=180,
            height=40,
            corner_radius=8
        ).pack(side='right', pady=20)

        # Zone de contenu principale avec scroll
        content_scroll = ctk.CTkScrollableFrame(
            self.container,
            fg_color=self.colors['white']
        )
        content_scroll.pack(fill='both', expand=True, padx=40, pady=(20, 30))

        # Titre de la note
        title_frame = Container.transparent(content_scroll)
        title_frame.pack(fill='x', pady=(0, 20))

        Label.title(title_frame, self.note_name, size='medium').pack(anchor='w')

        # Ligne de séparation
        separator = ctk.CTkFrame(content_scroll, height=2, fg_color=self.colors['border'])
        separator.pack(fill='x', pady=(0, 20))

        # Charger et afficher le contenu
        scanner = ObsidianVaultScanner(self.notes_path)
        content = scanner.get_note_content(self.note_name)

        if content:
            # Parser le contenu
            frontmatter, markdown = self._parse_note_content(content)

            # Afficher le frontmatter s'il existe
            if frontmatter:
                self._render_frontmatter(content_scroll, frontmatter)

            # Afficher le markdown
            self._render_markdown(content_scroll, markdown)
        else:
            # Message d'erreur
            error_frame = ctk.CTkFrame(
                content_scroll,
                fg_color=self.colors['gray'],
                corner_radius=15
            )
            error_frame.pack(fill='both', expand=True)

            Label.text(
                error_frame,
                "❌ Impossible de charger la note",
                font=("Arial", 16)
            ).pack(pady=40)

        return self.container
