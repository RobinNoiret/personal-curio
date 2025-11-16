"""
Widget d'autocomplete pour les notes Obsidian
Version améliorée avec dropdown intégré
"""
import customtkinter as ctk
from typing import List, Callable, Optional
from .utils.logger import get_logger


class AutocompleteEntry(ctk.CTkFrame):
    """Entry avec autocomplete intégré pour les notes Obsidian"""

    def __init__(self, master, search_function: Callable[[str], List[str]], allow_multiple: bool = False, **kwargs):
        """
        Args:
            master: Widget parent
            search_function: Fonction qui prend une query et retourne une liste de suggestions
            allow_multiple: Si True, permet plusieurs liens séparés par virgule (pour 'related')
            **kwargs: Arguments pour le frame conteneur
        """
        # Extraire les paramètres spécifiques à l'Entry
        entry_kwargs = {}
        for key in ['height', 'width', 'fg_color', 'border_color', 'border_width',
                    'corner_radius', 'placeholder_text', 'font']:
            if key in kwargs:
                entry_kwargs[key] = kwargs.pop(key)

        # Initialiser le frame parent
        super().__init__(master, fg_color="transparent", **kwargs)

        self.search_function = search_function
        self.allow_multiple = allow_multiple
        self.suggestions = []
        self.logger = get_logger()
        self.selected_index = -1
        self.suggestion_buttons = []

        # Créer l'entry
        self.entry = ctk.CTkEntry(self, **entry_kwargs)
        self.entry.pack(fill='x')

        # Créer le conteneur pour le dropdown (caché par défaut)
        self.dropdown_frame = None

        # Bind les événements
        self.entry.bind('<KeyRelease>', self._on_key_release)
        self.entry.bind('<FocusOut>', self._on_focus_out)
        self.entry.bind('<Down>', self._on_down)
        self.entry.bind('<Up>', self._on_up)
        self.entry.bind('<Return>', self._on_return)
        self.entry.bind('<Escape>', lambda e: self._hide_suggestions())

    def get(self):
        """Récupère le texte de l'entry"""
        return self.entry.get()

    def delete(self, first, last=None):
        """Supprime le texte de l'entry"""
        if last is None:
            self.entry.delete(first)
        else:
            self.entry.delete(first, last)

    def insert(self, index, string):
        """Insère du texte dans l'entry"""
        self.entry.insert(index, string)

    def _on_key_release(self, event):
        """Appelé quand une touche est relâchée"""
        # Ignorer les touches spéciales
        if event.keysym in ['Down', 'Up', 'Return', 'Escape']:
            return

        # Réinitialiser l'index de sélection
        self.selected_index = -1

        # Récupérer le texte actuel
        text = self.get()
        self.logger.debug(f"Texte actuel: '{text}'", "AutocompleteEntry")

        # Vérifier si on est dans un contexte de lien en cours (après [[ mais avant ]])
        # Pour cela, on cherche le dernier [[ et on vérifie qu'il n'y a pas de ]] après
        last_open = text.rfind('[[')

        if last_open != -1:
            # Il y a un [[ dans le texte, vérifier s'il y a un ]] après
            text_after_open = text[last_open:]

            # Si on trouve ]] après le dernier [[, le lien est fermé, cacher le dropdown
            if ']]' in text_after_open:
                self.logger.debug("Lien fermé détecté (]]), masquage du dropdown", "AutocompleteEntry")
                self._hide_suggestions()
                return

            # Sinon, extraire la query (ce qui est après [[)
            query = text[last_open + 2:]
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
            # Pas de [[ dans le texte, cacher le dropdown
            self._hide_suggestions()

    def _show_suggestions(self):
        """Affiche le dropdown de suggestions intégré"""
        self.logger.debug("_show_suggestions() appelée", "AutocompleteEntry")
        if not self.suggestions:
            self.logger.debug("Pas de suggestions, retour", "AutocompleteEntry")
            return

        # Créer le dropdown s'il n'existe pas
        if not self.dropdown_frame:
            self.logger.debug("Création du dropdown de suggestions", "AutocompleteEntry")
            self.dropdown_frame = ctk.CTkScrollableFrame(
                self,
                fg_color="#FFFFFF",
                border_color="#D1D5DB",
                border_width=1,
                corner_radius=8,
                height=0  # Initialement caché
            )
            # Ne pas utiliser pack pour éviter le décalage, on va gérer la visibilité différemment
            # On va créer le frame mais le garder sans pack initialement

        # Nettoyer les suggestions précédentes
        self.suggestion_buttons = []
        for widget in self.dropdown_frame.winfo_children():
            widget.destroy()

        # Ajouter les suggestions (max 8 pour ne pas être trop long)
        max_suggestions = min(8, len(self.suggestions))
        self.logger.debug(f"Ajout de {max_suggestions} suggestions", "AutocompleteEntry")

        for idx, suggestion in enumerate(self.suggestions[:max_suggestions]):
            btn = ctk.CTkButton(
                self.dropdown_frame,
                text=suggestion,
                command=lambda s=suggestion: self._select_suggestion(s),
                fg_color="transparent",
                hover_color="#F3F4F6",
                text_color="#1F2937",
                anchor="w",
                height=32,
                corner_radius=4,
                font=("Arial", 12),
                border_width=0
            )
            btn.pack(fill='x', padx=4, pady=1)
            self.suggestion_buttons.append(btn)

        # Calculer la hauteur appropriée (max 200px)
        dropdown_height = min(200, max_suggestions * 34 + 8)

        # S'assurer que le dropdown est affiché (pack si pas déjà fait)
        if not self.dropdown_frame.winfo_ismapped():
            self.dropdown_frame.pack(fill='x', pady=(2, 0))

        self.dropdown_frame.configure(height=dropdown_height)

        self.logger.debug(f"Dropdown affiché avec hauteur {dropdown_height}px", "AutocompleteEntry")

    def _hide_suggestions(self):
        """Cache le dropdown de suggestions"""
        if self.dropdown_frame and self.dropdown_frame.winfo_ismapped():
            self.dropdown_frame.pack_forget()
            self.selected_index = -1
            self.logger.debug("Dropdown caché", "AutocompleteEntry")

    def _on_focus_out(self, event):
        """Appelé quand le champ perd le focus"""
        # Utiliser after pour laisser le temps au clic sur une suggestion
        self.after(200, self._hide_suggestions)

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
        self.entry.focus_set()

    def _update_selection_highlight(self):
        """Met à jour le highlight de la suggestion sélectionnée"""
        for idx, btn in enumerate(self.suggestion_buttons):
            if idx == self.selected_index:
                btn.configure(fg_color="#E5E7EB")
            else:
                btn.configure(fg_color="transparent")

    def _on_down(self, event):
        """Flèche bas - naviguer dans les suggestions"""
        if self.suggestion_buttons and self.dropdown_frame and self.dropdown_frame.cget("height") > 0:
            self.selected_index = min(self.selected_index + 1, len(self.suggestion_buttons) - 1)
            self._update_selection_highlight()
            return 'break'  # Empêcher le comportement par défaut

    def _on_up(self, event):
        """Flèche haut - naviguer dans les suggestions"""
        if self.suggestion_buttons and self.dropdown_frame and self.dropdown_frame.cget("height") > 0:
            self.selected_index = max(self.selected_index - 1, 0)
            self._update_selection_highlight()
            return 'break'  # Empêcher le comportement par défaut

    def _on_return(self, event):
        """Entrée - sélectionner la suggestion courante"""
        if self.selected_index >= 0 and self.selected_index < len(self.suggestions):
            self._select_suggestion(self.suggestions[self.selected_index])
            return 'break'  # Empêcher le comportement par défaut
