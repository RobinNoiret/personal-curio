"""
Scanner de vault Obsidian pour l'autocomplete
"""
import os
import random
from typing import List, Set, Optional
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

    def get_random_note(self) -> Optional[str]:
        """
        Retourne une note aléatoire du cache

        Returns:
            Nom d'une note aléatoire, ou None si le cache est vide
        """
        if not self._notes_cache:
            return None

        return random.choice(list(self._notes_cache))

    def get_note_content(self, note_name: str) -> Optional[str]:
        """
        Récupère le contenu d'une note Obsidian

        Args:
            note_name: Nom de la note (sans extension)

        Returns:
            Contenu de la note en markdown, ou None si non trouvée
        """
        if not self.vault_path or not os.path.exists(self.vault_path):
            return None

        # Chercher le fichier avec ce nom
        try:
            for md_file in glob.glob(os.path.join(self.vault_path, '**', f'{note_name}.md'), recursive=True):
                with open(md_file, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            print(f"Erreur lors de la lecture de la note {note_name}: {e}")

        return None
