"""
Classe de base pour toutes les pages
"""
import customtkinter as ctk
from abc import ABC, abstractmethod
from typing import Callable


class BasePage(ABC):
    """Classe de base abstraite pour les pages"""

    def __init__(self, parent, colors: dict, on_navigate: Callable = None):
        """
        Args:
            parent: Widget parent
            colors: Dictionnaire des couleurs
            on_navigate: Callback de navigation
        """
        self.parent = parent
        self.colors = colors
        self.on_navigate = on_navigate
        self.container = None

    @abstractmethod
    def render(self) -> ctk.CTkFrame:
        """Rend la page et retourne le conteneur principal"""
        pass

    def clear(self):
        """Nettoie les widgets de la page"""
        if self.container and self.container.winfo_exists():
            self.container.destroy()
            self.container = None
