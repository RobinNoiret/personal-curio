"""
Widget d'autocomplete pour les notes Obsidian
"""
import customtkinter as ctk
from typing import List, Callable


class AutocompleteEntry(ctk.CTkEntry):
    """Entry avec autocomplete pour les notes Obsidian"""

    def __init__(self, master, search_function: Callable[[str], List[str]], **kwargs):
        """
        Args:
            master: Widget parent
            search_function: Fonction qui prend une query et retourne une liste de suggestions
            **kwargs: Arguments pour CTkEntry
        """
        super().__init__(master, **kwargs)

        self.search_function = search_function
        self.suggestions_window = None
        self.suggestions_listbox = None
        self.suggestions = []

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
        print(f"[AutocompleteEntry] Texte actuel: '{text}'")

        # Si le texte se termine par [[, activer l'autocomplete
        if '[[' in text:
            # Extraire ce qui est après [[
            start_idx = text.rfind('[[')
            query = text[start_idx + 2:]
            print(f"[AutocompleteEntry] Détection de [[, query='{query}'")

            # Chercher des suggestions
            self.suggestions = self.search_function(query)
            print(f"[AutocompleteEntry] Nombre de suggestions: {len(self.suggestions)}")

            if self.suggestions:
                print(f"[AutocompleteEntry] Affichage des suggestions: {self.suggestions[:3]}")
                self._show_suggestions()
            else:
                print("[AutocompleteEntry] Aucune suggestion, masquage")
                self._hide_suggestions()
        else:
            self._hide_suggestions()

    def _show_suggestions(self):
        """Affiche la fenêtre de suggestions"""
        print(f"[AutocompleteEntry] _show_suggestions() appelée")
        if not self.suggestions:
            print("[AutocompleteEntry] Pas de suggestions, retour")
            return

        # Créer la fenêtre si elle n'existe pas
        if not self.suggestions_window:
            print("[AutocompleteEntry] Création de la fenêtre de suggestions")
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
        print(f"[AutocompleteEntry] Ajout de {len(self.suggestions[:10])} suggestions")
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
        print(f"[AutocompleteEntry] Position de la fenêtre: x={x}, y={y}")
        self.suggestions_window.geometry(f"300x150+{x}+{y}")
        self.suggestions_window.deiconify()
        self.suggestions_window.lift()
        print("[AutocompleteEntry] Fenêtre affichée")

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
            # Remplacer ce qui est après [[ par la suggestion avec ]]
            new_text = text[:start_idx + 2] + suggestion + ']]'
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
