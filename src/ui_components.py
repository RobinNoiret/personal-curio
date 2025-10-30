"""
Composants UI réutilisables
"""
import customtkinter as ctk
from typing import Dict, Callable, Optional, Tuple
from .constants import COLORS, FONTS


class Button:
    """Factory pour créer différents types de boutons"""

    @staticmethod
    def primary(parent, text: str, command: Callable, **kwargs) -> ctk.CTkButton:
        """Bouton principal (jaune)"""
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            font=kwargs.get('font', FONTS['text_large']),
            height=kwargs.get('height', 50),
            fg_color=COLORS['yellow'],
            text_color=COLORS['black'],
            hover_color="#FFD700",
            corner_radius=kwargs.get('corner_radius', 10),
            **{k: v for k, v in kwargs.items() if k not in ['font', 'height', 'corner_radius']}
        )

    @staticmethod
    def secondary(parent, text: str, command: Callable, **kwargs) -> ctk.CTkButton:
        """Bouton secondaire (noir)"""
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            font=kwargs.get('font', FONTS['text_large']),
            height=kwargs.get('height', 50),
            fg_color=COLORS['black'],
            text_color=COLORS['white'],
            hover_color="#333333",
            corner_radius=kwargs.get('corner_radius', 10),
            **{k: v for k, v in kwargs.items() if k not in ['font', 'height', 'corner_radius']}
        )

    @staticmethod
    def outline(parent, text: str, command: Callable, **kwargs) -> ctk.CTkButton:
        """Bouton avec bordure"""
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            font=kwargs.get('font', FONTS['text_large']),
            height=kwargs.get('height', 50),
            fg_color=COLORS['white'],
            text_color=COLORS['black'],
            hover_color=COLORS['gray'],
            border_width=kwargs.get('border_width', 2),
            border_color=COLORS['border'],
            corner_radius=kwargs.get('corner_radius', 10),
            **{k: v for k, v in kwargs.items() if k not in ['font', 'height', 'border_width', 'corner_radius']}
        )


class Label:
    """Factory pour créer différents types de labels"""

    @staticmethod
    def title(parent, text: str, size: str = 'large', **kwargs) -> ctk.CTkLabel:
        """Titre"""
        font_map = {
            'large': FONTS['title_large'],
            'medium': FONTS['title_medium'],
            'small': FONTS['title_small']
        }
        return ctk.CTkLabel(
            parent,
            text=text,
            font=font_map.get(size, FONTS['title_large']),
            text_color=COLORS['black'],
            **kwargs
        )

    @staticmethod
    def text(parent, text: str, color: str = 'text_gray', **kwargs) -> ctk.CTkLabel:
        """Texte normal"""
        return ctk.CTkLabel(
            parent,
            text=text,
            font=kwargs.get('font', FONTS['text_medium']),
            text_color=COLORS.get(color, COLORS['text_gray']),
            **{k: v for k, v in kwargs.items() if k != 'font'}
        )


class Container:
    """Factory pour créer différents types de conteneurs"""

    @staticmethod
    def section(parent, title: Optional[str] = None, **kwargs) -> Tuple[ctk.CTkFrame, ctk.CTkFrame]:
        """Crée une section avec titre optionnel et frame de contenu"""
        # Titre si fourni
        if title:
            Label.title(parent, title, size='small').pack(anchor='w', pady=(20, 15))

        # Frame de contenu
        content = ctk.CTkFrame(
            parent,
            fg_color=kwargs.get('fg_color', COLORS['gray']),
            corner_radius=kwargs.get('corner_radius', 15)
        )
        content.pack(fill='x', pady=(0, 20))

        return content

    @staticmethod
    def scrollable(parent, **kwargs) -> ctk.CTkScrollableFrame:
        """Conteneur scrollable"""
        return ctk.CTkScrollableFrame(
            parent,
            fg_color=kwargs.get('fg_color', COLORS['white']),
            **{k: v for k, v in kwargs.items() if k != 'fg_color'}
        )

    @staticmethod
    def transparent(parent, **kwargs) -> ctk.CTkFrame:
        """Frame transparent"""
        return ctk.CTkFrame(parent, fg_color="transparent", **kwargs)


class Input:
    """Factory pour créer différents types d'inputs"""

    @staticmethod
    def text_entry(parent, placeholder: str = "", default: str = "", **kwargs) -> ctk.CTkEntry:
        """Champ de texte"""
        entry = ctk.CTkEntry(
            parent,
            height=kwargs.get('height', 40),
            font=FONTS['text_medium'],
            fg_color=COLORS['white'],
            border_color=COLORS['border'],
            border_width=kwargs.get('border_width', 1),
            corner_radius=kwargs.get('corner_radius', 8),
            placeholder_text=placeholder,
            **{k: v for k, v in kwargs.items() if k not in ['height', 'border_width', 'corner_radius']}
        )
        if default:
            entry.insert(0, default)
        return entry

    @staticmethod
    def textbox(parent, **kwargs) -> ctk.CTkTextbox:
        """Zone de texte multiligne"""
        return ctk.CTkTextbox(
            parent,
            wrap='word',
            font=kwargs.get('font', FONTS['code']),
            fg_color=kwargs.get('fg_color', COLORS['white']),
            text_color=kwargs.get('text_color', COLORS['black']),
            border_width=kwargs.get('border_width', 2),
            border_color=COLORS['border'],
            corner_radius=kwargs.get('corner_radius', 10),
            **{k: v for k, v in kwargs.items() if k not in ['font', 'fg_color', 'text_color', 'border_width', 'corner_radius']}
        )


class Spacer:
    """Crée des espacements"""

    @staticmethod
    def vertical(parent, height: int = 20):
        """Espace vertical"""
        ctk.CTkFrame(parent, fg_color="transparent", height=height).pack()

    @staticmethod
    def horizontal(parent, width: int = 20):
        """Espace horizontal"""
        ctk.CTkFrame(parent, fg_color="transparent", width=width).pack(side='left')
