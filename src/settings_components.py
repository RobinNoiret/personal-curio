"""
Composants réutilisables pour la page des paramètres
"""
import customtkinter as ctk
from typing import Dict, Callable


class SettingsSection:
    """Crée une section de paramètres avec titre"""

    @staticmethod
    def create(parent, title: str, colors: Dict) -> ctk.CTkFrame:
        """Crée une section avec un titre"""
        # Titre de la section
        section_title = ctk.CTkLabel(
            parent,
            text=title,
            font=("Arial", 20, "bold"),
            text_color=colors['black']
        )
        section_title.pack(anchor='w', pady=(20, 15))

        # Frame pour le contenu de la section
        section_frame = ctk.CTkFrame(parent, fg_color=colors['gray'], corner_radius=15)
        section_frame.pack(fill='x', pady=(0, 20))

        return section_frame


class FormField:
    """Crée un champ de formulaire avec label"""

    @staticmethod
    def create_text_field(parent, label: str, placeholder: str, default_value: str, colors: Dict) -> ctk.CTkEntry:
        """Crée un champ de texte avec label"""
        field_container = ctk.CTkFrame(parent, fg_color="transparent")
        field_container.pack(fill='x', padx=20, pady=10)

        # Label
        ctk.CTkLabel(
            field_container,
            text=label,
            font=("Arial", 12),
            text_color=colors['text_gray'],
            anchor='w'
        ).pack(anchor='w', pady=(0, 5))

        # Entry
        entry = ctk.CTkEntry(
            field_container,
            height=40,
            font=("Arial", 13),
            fg_color=colors['white'],
            border_color=colors['border'],
            border_width=1,
            corner_radius=8,
            placeholder_text=placeholder
        )
        if default_value:
            entry.insert(0, default_value)
        entry.pack(fill='x')

        return entry

    @staticmethod
    def create_file_field(parent, label: str, default_value: str, browse_command: Callable, colors: Dict) -> ctk.CTkEntry:
        """Crée un champ de fichier avec bouton parcourir"""
        field_container = ctk.CTkFrame(parent, fg_color="transparent")
        field_container.pack(fill='x', padx=20, pady=10)

        # Label
        ctk.CTkLabel(
            field_container,
            text=label,
            font=("Arial", 12),
            text_color=colors['text_gray'],
            anchor='w'
        ).pack(anchor='w', pady=(0, 5))

        # Frame pour entry + bouton
        input_frame = ctk.CTkFrame(field_container, fg_color="transparent")
        input_frame.pack(fill='x')

        # Entry
        entry = ctk.CTkEntry(
            input_frame,
            height=40,
            font=("Arial", 13),
            fg_color=colors['white'],
            border_color=colors['border'],
            border_width=1,
            corner_radius=8
        )
        if default_value:
            entry.insert(0, default_value)
        entry.pack(side='left', fill='x', expand=True, padx=(0, 10))

        # Bouton parcourir
        browse_btn = ctk.CTkButton(
            input_frame,
            text="Parcourir",
            command=lambda: browse_command(entry),
            width=100,
            height=40,
            fg_color=colors['white'],
            text_color=colors['black'],
            hover_color=colors['gray'],
            border_width=1,
            border_color=colors['border'],
            corner_radius=8,
            font=("Arial", 12)
        )
        browse_btn.pack(side='left')

        return entry

    @staticmethod
    def create_combo_field(parent, label: str, description: str, options: list, default_value: str, colors: Dict) -> ctk.CTkComboBox:
        """Crée un champ de sélection (ComboBox) avec label et description"""
        field_container = ctk.CTkFrame(parent, fg_color="transparent")
        field_container.pack(fill='x', padx=20, pady=10)

        # Label
        ctk.CTkLabel(
            field_container,
            text=label,
            font=("Arial", 12),
            text_color=colors['text_gray'],
            anchor='w'
        ).pack(anchor='w', pady=(0, 5))

        # Description
        if description:
            ctk.CTkLabel(
                field_container,
                text=description,
                font=("Arial", 10),
                text_color=colors['text_gray'],
                anchor='w'
            ).pack(anchor='w', pady=(0, 8))

        # ComboBox
        combo = ctk.CTkComboBox(
            field_container,
            values=options,
            height=40,
            font=("Arial", 13),
            button_color=colors['yellow'],
            button_hover_color="#FFD700",
            border_color=colors['border'],
            border_width=1,
            fg_color=colors['white'],
            dropdown_fg_color=colors['white'],
            dropdown_hover_color=colors['gray'],
            corner_radius=8
        )
        combo.pack(fill='x')
        if default_value:
            combo.set(default_value)

        return combo


class AboutSection:
    """Crée une section À propos avec les informations de l'application"""

    @staticmethod
    def create(parent, app_info: Dict, colors: Dict):
        """Crée la section À propos"""
        # Titre de la section
        section_title = ctk.CTkLabel(
            parent,
            text="À propos",
            font=("Arial", 20, "bold"),
            text_color=colors['black']
        )
        section_title.pack(anchor='w', pady=(20, 15))

        # Frame pour le contenu
        about_frame = ctk.CTkFrame(parent, fg_color=colors['gray'], corner_radius=15)
        about_frame.pack(fill='x', pady=(0, 20))

        # Contenu
        content_frame = ctk.CTkFrame(about_frame, fg_color="transparent")
        content_frame.pack(fill='x', padx=20, pady=20)

        # Nom de l'application
        ctk.CTkLabel(
            content_frame,
            text=app_info.get('name', 'Prosit Manager'),
            font=("Arial", 18, "bold"),
            text_color=colors['black']
        ).pack(anchor='w', pady=(0, 10))

        # Version
        version_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        version_frame.pack(fill='x', pady=5)

        ctk.CTkLabel(
            version_frame,
            text="Version:",
            font=("Arial", 12),
            text_color=colors['text_gray']
        ).pack(side='left', padx=(0, 10))

        ctk.CTkLabel(
            version_frame,
            text=app_info.get('version', '1.0.0'),
            font=("Arial", 12, "bold"),
            text_color=colors['black']
        ).pack(side='left')

        # Auteur
        author_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        author_frame.pack(fill='x', pady=5)

        ctk.CTkLabel(
            author_frame,
            text="Auteur:",
            font=("Arial", 12),
            text_color=colors['text_gray']
        ).pack(side='left', padx=(0, 10))

        ctk.CTkLabel(
            author_frame,
            text=app_info.get('author', 'NOIRET Robin'),
            font=("Arial", 12),
            text_color=colors['black']
        ).pack(side='left')

        # Description
        if app_info.get('description'):
            ctk.CTkLabel(
                content_frame,
                text=app_info['description'],
                font=("Arial", 11),
                text_color=colors['text_gray'],
                wraplength=600
            ).pack(anchor='w', pady=(10, 0))
