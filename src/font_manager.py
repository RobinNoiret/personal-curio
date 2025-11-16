"""
Gestionnaire de polices personnalisées pour l'application
"""
import os
import sys
from tkinter import font as tkfont
import customtkinter as ctk
from .utils.logger import get_logger


class FontManager:
    """Gère le chargement et l'utilisation des polices personnalisées"""

    def __init__(self):
        self.fonts_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'assets',
            'fonts'
        )
        self.degular_loaded = False
        self.inter_loaded = False
        self.logger = get_logger()

        # Charger les polices
        self._load_fonts()

    def _load_fonts(self):
        """Charge les polices personnalisées"""
        # Essayer de charger Degular (format .otf et .ttf)
        degular_paths = [
            os.path.join(self.fonts_dir, 'Degular-Regular.otf'),
            os.path.join(self.fonts_dir, 'Degular-Medium.otf'),
            os.path.join(self.fonts_dir, 'Degular-Semibold.otf'),
            os.path.join(self.fonts_dir, 'Degular-Bold.otf'),
            os.path.join(self.fonts_dir, 'Degular-Regular.ttf'),
            os.path.join(self.fonts_dir, 'Degular-Bold.ttf'),
        ]

        for path in degular_paths:
            if os.path.exists(path):
                try:
                    if sys.platform == 'win32':
                        import ctypes
                        from ctypes import wintypes

                        gdi32 = ctypes.WinDLL('gdi32', use_last_error=True)
                        FR_PRIVATE = 0x10

                        num_fonts = gdi32.AddFontResourceExW(
                            path, FR_PRIVATE, 0
                        )
                        if num_fonts > 0:
                            self.degular_loaded = True
                            self.logger.info(f"Police chargée : {os.path.basename(path)}", "FontManager")
                    else:
                        # Pour macOS/Linux, utiliser pyglet ou autre méthode
                        pass
                except Exception as e:
                    self.logger.error(f"Erreur lors du chargement de Degular ({os.path.basename(path)}): {e}", "FontManager")

        # Essayer de charger Inter (format variable font et standard)
        inter_paths = [
            os.path.join(self.fonts_dir, 'Inter-VariableFont_opsz,wght.ttf'),
            os.path.join(self.fonts_dir, 'Inter-Regular.ttf'),
            os.path.join(self.fonts_dir, 'Inter-Bold.ttf'),
        ]

        for path in inter_paths:
            if os.path.exists(path):
                try:
                    if sys.platform == 'win32':
                        import ctypes
                        from ctypes import wintypes

                        gdi32 = ctypes.WinDLL('gdi32', use_last_error=True)
                        FR_PRIVATE = 0x10

                        num_fonts = gdi32.AddFontResourceExW(
                            path, FR_PRIVATE, 0
                        )
                        if num_fonts > 0:
                            self.inter_loaded = True
                            self.logger.info(f"Police chargée : {os.path.basename(path)}", "FontManager")
                    else:
                        # Pour macOS/Linux, utiliser pyglet ou autre méthode
                        pass
                except Exception as e:
                    self.logger.error(f"Erreur lors du chargement d'Inter ({os.path.basename(path)}): {e}", "FontManager")

    def get_title_font(self):
        """Retourne le nom de la police pour les titres (Degular)"""
        if self.degular_loaded:
            return "Degular"
        return "Arial"  # Fallback

    def get_text_font(self):
        """Retourne le nom de la police pour le texte (Inter)"""
        if self.inter_loaded:
            return "Inter"
        return "Arial"  # Fallback


# Instance globale
_font_manager = None

def get_font_manager():
    """Retourne l'instance du gestionnaire de polices"""
    global _font_manager
    if _font_manager is None:
        _font_manager = FontManager()
    return _font_manager
