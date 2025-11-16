"""
Constantes de l'application
"""
from .font_manager import get_font_manager

# Initialiser le gestionnaire de polices
_fm = get_font_manager()
TITLE_FONT = _fm.get_title_font()  # Degular (ou Arial en fallback)
TEXT_FONT = _fm.get_text_font()    # Inter (ou Arial en fallback)

# Palette de couleurs
COLORS = {
    'yellow': '#FFC92C',
    'white': '#FFFFFF',
    'black': '#1A1A18',
    'gray': '#F8F9FA',
    'navbar_bg': '#F7F7F7',  # Fond de la navbar
    'text_gray': '#6B7280',
    'border': '#E5E7EB',
    'blue': '#3B82F6'
}

# Dimensions
WINDOW_SIZE = "1800x1000"
SIDEBAR_WIDTH = 280  # Largeur de la sidebar
LOGO_SIZE = 90  # Hauteur du logo
NAV_BUTTON_HEIGHT = 70  # Hauteur de chaque bouton de navigation

# Polices
# Utilisation de Degular pour les titres et Inter pour le texte
FONTS = {
    # Titres - Degular
    'title_large': (TITLE_FONT, 42, "bold"),
    'title_medium': (TITLE_FONT, 36, "bold"),
    'title_small': (TITLE_FONT, 20, "bold"),
    'curio_brand': (TITLE_FONT, 24, "bold"),  # Pour le logo
    
    # Petits titres en Inter (utilisés ponctuellement quand on veut le même
    # style/size que les titres mais avec la police texte Inter)
    'title_small_inter': (TEXT_FONT, 20, "bold"),

    # Textes - Inter
    'subtitle': (TEXT_FONT, 18),
    'subtitle_bold': (TEXT_FONT, 18, "bold"),
    'body': (TEXT_FONT, 14),
    'body_bold': (TEXT_FONT, 14, "bold"),
    'body_small': (TEXT_FONT, 12),
    'text_large': (TEXT_FONT, 16),
    'text_medium': (TEXT_FONT, 14),
    'text_small': (TEXT_FONT, 12),
    'text_tiny': (TEXT_FONT, 8),

    # Icons et code
    'icon_large': (TEXT_FONT, 48),
    'icon_medium': (TEXT_FONT, 36),
    'code': ("Consolas", 12),
}

# Navigation items
NAV_ITEMS = [
    ('prosit', '', 'Prosit manager'),
    ('obsidian', '', 'Notes extractor'),
]
