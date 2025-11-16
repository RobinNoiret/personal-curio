"""
Widget d'autocomplete pour les notes Obsidian
"""
import customtkinter as ctk
from typing import List, Callable
from .utils.logger import get_logger


class AutocompleteEntry(ctk.CTkEntry):
    """Entry avec autocomplete pour les notes Obsidian"""

    def __init__(self, master, search_function: Callable[[str], List[str]], allow_multiple: bool = False, **kwargs):
        """
        Args:
            master: Widget parent
            search_function: Fonction qui prend une query et retourne une liste de suggestions
            allow_multiple: Si True, permet plusieurs liens séparés par virgule (pour 'related')
            **kwargs: Arguments pour CTkEntry
        """
        super().__init__(master, **kwargs)

        self.search_function = search_function
        self.allow_multiple = allow_multiple
        self.suggestions_window = None
        self.suggestions_listbox = None
        self.suggestions = []
        self.logger = get_logger()

        # Bind les événements
        self.bind('<KeyRelease>', self._on_key_release)
        self.bind('<FocusOut>', self._hide_suggestions)
        self.bind('<Down>', self._on_down)
        self.bind('<Up>', self._on_up)
        self.bind('<Return>', self._on_return)

    def _on_key_release(self, event):
        """Appelé quand une touche est relâchée"""
        # Ignorer les touches spéciales
        if event.keysym in ['Down', 'Up', 'Return', 'Escape']:
            return

        # Récupérer le texte actuel
        text = self.get()
        self.logger.debug(f"Texte actuel: '{text}'", "AutocompleteEntry")

        # Si le texte se termine par [[, activer l'autocomplete
        if '[[' in text:
            # Extraire ce qui est après [[
            start_idx = text.rfind('[[')
            query = text[start_idx + 2:]
            self.logger.debug(f"Détection de [[, query='{query}'", "AutocompleteEntry")

            # Chercher des suggestions
            self.suggestions = self.search_function(query)
            self.logger.debug(f"Nombre de suggestions: {len(self.suggestions)}", "AutocompleteEntry")

            if self.suggestions:
                self.logger.debug(f"Affichage des suggestions: {self.suggestions[:3]}", "AutocompleteEntry")
                self._show_suggestions()
            else:
                self.logger.debug("Aucune suggestion, masquage", "AutocompleteEntry")
                self._hide_suggestions()
        else:
            self._hide_suggestions()

    def _show_suggestions(self):
        """Affiche la fenêtre de suggestions"""
        self.logger.debug("_show_suggestions() appelée", "AutocompleteEntry")
        if not self.suggestions:
            self.logger.debug("Pas de suggestions, retour", "AutocompleteEntry")
            return

        # Créer la fenêtre si elle n'existe pas
        if not self.suggestions_window:
            self.logger.debug("Création de la fenêtre de suggestions", "AutocompleteEntry")
            self.suggestions_window = ctk.CTkToplevel(self)
            self.suggestions_window.withdraw()
            self.suggestions_window.overrideredirect(True)

            # Listbox pour les suggestions
            self.suggestions_listbox = ctk.CTkScrollableFrame(
                self.suggestions_window,
                width=300,
                height=150
            )
            self.suggestions_listbox.pack(fill='both', expand=True)

        # Nettoyer la listbox
        for widget in self.suggestions_listbox.winfo_children():
            widget.destroy()

        # Ajouter les suggestions
        self.logger.debug(f"Ajout de {len(self.suggestions[:10])} suggestions", "AutocompleteEntry")
        for suggestion in self.suggestions[:10]:  # Limiter à 10 suggestions
            btn = ctk.CTkButton(
                self.suggestions_listbox,
                text=suggestion,
                command=lambda s=suggestion: self._select_suggestion(s),
                fg_color="transparent",
                hover_color="#E5E7EB",
                text_color="#1A1A18",
                anchor="w",
                height=30
            )
            btn.pack(fill='x', pady=2)

        # Positionner la fenêtre sous l'entry
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        self.logger.debug(f"Position de la fenêtre: x={x}, y={y}", "AutocompleteEntry")
        self.suggestions_window.geometry(f"300x150+{x}+{y}")
        self.suggestions_window.deiconify()
        self.suggestions_window.lift()
        self.logger.debug("Fenêtre affichée", "AutocompleteEntry")

    def _hide_suggestions(self, event=None):
        """Cache la fenêtre de suggestions"""
        if self.suggestions_window:
            self.suggestions_window.withdraw()

    def _select_suggestion(self, suggestion: str):
        """Sélectionne une suggestion"""
        # Récupérer le texte actuel
        text = self.get()

        # Trouver la position de [[
        start_idx = text.rfind('[[')

        if start_idx != -1:
            if self.allow_multiple:
                # Mode multiple (related) : remplacer seulement après le dernier [[
                new_text = text[:start_idx] + f"[[{suggestion}]], "
            else:
                # Mode single (from) : remplacer tout le contenu
                new_text = f"[[{suggestion}]]"

            self.delete(0, 'end')
            self.insert(0, new_text)

        self._hide_suggestions()
        self.focus_set()

    def _on_down(self, event):
        """Flèche bas - naviguer dans les suggestions"""
        # TODO: implémenter la navigation au clavier
        pass

    def _on_up(self, event):
        """Flèche haut - naviguer dans les suggestions"""
        # TODO: implémenter la navigation au clavier
        pass

    def _on_return(self, event):
        """Entrée - sélectionner la suggestion courante"""
        # TODO: implémenter la sélection
        pass
