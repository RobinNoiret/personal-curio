"""
Scanner de vault Obsidian pour l'autocomplete
"""
import os
from typing import List, Set
import glob


class ObsidianVaultScanner:
    """Scanne un vault Obsidian pour trouver toutes les notes"""

    def __init__(self, vault_path: str = None):
        """
        Initialise le scanner

        Args:
            vault_path: Chemin vers le vault Obsidian
        """
        self.vault_path = vault_path
        self._notes_cache: Set[str] = set()

    def scan_notes(self, vault_path: str = None) -> List[str]:
        """
        Scanne le vault pour trouver toutes les notes .md

        Args:
            vault_path: Chemin vers le vault (optionnel, utilise celui de l'init si non fourni)

        Returns:
            Liste des noms de notes (sans extension)
        """
        path = vault_path or self.vault_path

        if not path or not os.path.exists(path):
            return []

        # Chercher tous les fichiers .md récursivement
        notes = set()
        try:
            for md_file in glob.glob(os.path.join(path, '**', '*.md'), recursive=True):
                # Extraire le nom du fichier sans extension
                note_name = os.path.splitext(os.path.basename(md_file))[0]
                notes.add(note_name)

            self._notes_cache = notes
            return sorted(list(notes))

        except Exception as e:
            print(f"Erreur lors du scan du vault: {e}")
            return []

    def get_notes(self) -> List[str]:
        """Retourne la liste des notes en cache"""
        return sorted(list(self._notes_cache))

    def search_notes(self, query: str, limit: int = 10) -> List[str]:
        """
        Recherche des notes correspondant à la requête

        Args:
            query: Texte de recherche
            limit: Nombre maximum de résultats

        Returns:
            Liste des notes correspondantes
        """
        if not query:
            return self.get_notes()[:limit]

        query_lower = query.lower()

        # Filtrer les notes qui contiennent la requête
        matches = [
            note for note in self._notes_cache
            if query_lower in note.lower()
        ]

        # Trier par pertinence (celles qui commencent par la requête d'abord)
        matches.sort(key=lambda x: (
            not x.lower().startswith(query_lower),  # Priorité à celles qui commencent par la requête
            x.lower()  # Puis ordre alphabétique
        ))

        return matches[:limit]
