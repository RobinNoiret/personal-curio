"""
Extracteur de mots-clés depuis documents Word vers notes Obsidian
"""
import re
import os
from typing import List, Dict, Optional
from datetime import datetime
from docx import Document
import yaml


class ObsidianNote:
    """Représente une note Obsidian avec son frontmatter et son contenu"""

    def __init__(self, title: str, definition: str, metadata: Dict = None):
        self.title = title.strip()
        self.definition = definition.strip()
        # Métadonnées par défaut (nouveau template)
        default_metadata = {
            'type': 'note',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'from': '',
            'about': '',
            'related': '',
            'tags': ['draft', 'to_complete', 'permanent']
        }
        # Fusionner avec les métadonnées fournies
        if metadata:
            default_metadata.update(metadata)
        self.metadata = default_metadata

    def to_markdown(self, template: Dict = None) -> str:
        """Convertit la note en format markdown avec frontmatter"""
        # Construire le frontmatter en utilisant les métadonnées de l'objet
        frontmatter_lines = ["---"]
        frontmatter_lines.append(f"type: {self.metadata.get('type', 'note')}")
        frontmatter_lines.append(f"date: {self.metadata.get('date', '')}")

        # From - un seul lien entre guillemets
        from_value = self.metadata.get('from', '')
        if from_value:
            # Si c'est un lien [[note]], le quoter
            if from_value.strip().startswith('[[') and from_value.strip().endswith(']]'):
                frontmatter_lines.append(f'from: "{from_value}"')
            else:
                frontmatter_lines.append(f"from: {from_value}")
        else:
            frontmatter_lines.append("from:")

        # About
        about_value = self.metadata.get('about', '')
        if about_value and about_value.strip().startswith('[['):
            frontmatter_lines.append(f'about: "{about_value}"')
        else:
            frontmatter_lines.append(f"about: {about_value}")

        # Related - liste YAML de liens
        related_value = self.metadata.get('related', '')
        if related_value:
            # Parser les liens séparés par des virgules: [[Note 1]], [[Note 2]]
            import re
            links = re.findall(r'\[\[([^\]]+)\]\]', related_value)
            if links:
                frontmatter_lines.append("related:")
                for link in links:
                    frontmatter_lines.append(f'  - "[[{link}]]"')
            else:
                # Pas de liens détectés, mettre la valeur brute
                frontmatter_lines.append(f"related: {related_value}")
        else:
            frontmatter_lines.append("related:")

        # Tags - liste YAML standard
        tags = self.metadata.get('tags', [])
        if tags:
            frontmatter_lines.append("tags:")
            for tag in tags:
                frontmatter_lines.append(f"  - {tag}")
        else:
            frontmatter_lines.append("tags:")

        frontmatter_lines.append("---")
        frontmatter_lines.append("___")
        frontmatter_lines.append("#### Ressources :")
        frontmatter_lines.append("- ")
        frontmatter_lines.append("____")
        frontmatter_lines.append("### Définition")
        frontmatter_lines.append("")
        frontmatter_lines.append(self.definition)

        return "\n".join(frontmatter_lines)

    def get_filename(self) -> str:
        """Génère un nom de fichier valide à partir du titre"""
        # Remplacer les caractères invalides
        filename = re.sub(r'[<>:"/\\|?*]', '_', self.title)
        # Limiter la longueur
        filename = filename[:100]
        return f"{filename}.md"


class WordToObsidianExtractor:
    """Extracteur de définitions depuis Word vers Obsidian"""

    def __init__(self, config_path: str = None):
        """
        Initialise l'extracteur

        Args:
            config_path: Chemin vers le fichier de configuration YAML
        """
        if config_path is None:
            # Par défaut, chercher dans config/
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            config_path = os.path.join(base_dir, 'config', 'obsidian_extractor.yaml')

        self.config = self._load_config(config_path)
        self.notes: List[ObsidianNote] = []

    def _load_config(self, config_path: str) -> Dict:
        """Charge la configuration depuis le fichier YAML"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Erreur lors du chargement de la config: {e}")
            # Configuration par défaut
            return {
                'vault_path': '~/Obsidian/MyVault',
                'default_folder': '/Imports',
                'date_format': 'YYYY-MM-DD',
                'max_file_size_mb': 50,
                'note_template': {
                    'type': 'réunion',
                    'default_tags': ['réunion', 'vicat', 'project', 'raw'],
                    'data_quality': 'raw'
                },
                'extraction': {
                    'section_title': 'Définition des mots clés',
                    'definition_pattern': r'^(.+?)\s*[:\u2009\u00a0]\s*(.+)$'
                }
            }

    def extract_from_text(self, text: str, source_date: str = None) -> List[ObsidianNote]:
        """
        Extrait les définitions depuis du texte brut

        Args:
            text: Texte contenant les définitions
            source_date: Date associée au texte (optionnel)

        Returns:
            Liste des notes extraites
        """
        self.notes = []

        # Métadonnées communes
        metadata = {
            'date': source_date or datetime.now().strftime('%Y-%m-%d'),
            'source': 'texte_copié'
        }

        # Diviser le texte en lignes
        lines = text.split('\n')

        for line in lines:
            line = line.strip()

            # Essayer d'extraire une définition
            # Gérer plusieurs séparateurs possibles : '=', ':', etc.
            # et nettoyer les puces en début de ligne (•, -, *, etc.)
            if line and ('=' in line or ':' in line):
                # Nettoyer la ligne des puces et espaces en début
                cleaned_text = re.sub(r'^[\s•\-\*\u2022\u2023\u2043]+', '', line)

                # Rechercher le séparateur (= ou :)
                # On préfère '=' si présent, sinon on utilise ':'
                if '=' in cleaned_text:
                    split_match = re.split(r'\s*=\s*', cleaned_text, maxsplit=1)
                else:
                    split_match = re.split(r'\s*[:]\s*', cleaned_text, maxsplit=1)

                if len(split_match) == 2:
                    term = split_match[0].strip()
                    definition = split_match[1].strip()

                    # Vérifier que le terme et la définition ne sont pas vides
                    # Filtrer les cas où le "terme" est juste "Définition" (titre de section)
                    if term and definition and term.lower() not in ['définition', 'definition']:
                        # Créer une note
                        note = ObsidianNote(term, definition, metadata.copy())
                        self.notes.append(note)

        return self.notes

    def extract_from_docx(self, docx_path: str, source_date: str = None) -> List[ObsidianNote]:
        """
        Extrait les définitions depuis un fichier Word

        Args:
            docx_path: Chemin vers le fichier .docx
            source_date: Date associée au document (optionnel)

        Returns:
            Liste des notes extraites
        """
        # Vérifier la taille du fichier
        file_size_mb = os.path.getsize(docx_path) / (1024 * 1024)
        max_size = self.config.get('max_file_size_mb', 50)
        if file_size_mb > max_size:
            raise ValueError(f"Le fichier est trop volumineux ({file_size_mb:.1f} MB > {max_size} MB)")

        # Charger le document
        doc = Document(docx_path)

        # Trouver la section "Définition des mots clés"
        section_title = self.config['extraction']['section_title']
        in_section = False
        section_count = 0  # Compter les occurrences
        self.notes = []

        # Métadonnées communes
        metadata = {
            'date': source_date or datetime.now().strftime('%Y-%m-%d'),
            'source': os.path.basename(docx_path)
        }

        # Pattern pour détecter les définitions
        pattern = self.config['extraction']['definition_pattern']

        for para in doc.paragraphs:
            text = para.text.strip()

            # Détecter le début de la section
            if section_title in text:
                section_count += 1
                # On veut la dernière occurrence (généralement la deuxième)
                in_section = True
                continue

            # Si on est dans la section et qu'on trouve une ligne vide ou un nouveau titre
            if in_section:
                # Arrêter si on trouve un nouveau titre majeur (sauf Heading 3 qui peut être dans la section)
                if text and para.style.name in ['Heading 1', 'Heading 2'] and 'Définition' not in text:
                    # Ne pas break immédiatement, on continue pour trouver d'autres sections
                    in_section = False
                    continue

                # Essayer d'extraire une définition
                # Gérer plusieurs séparateurs possibles : '=', ':', etc.
                # et nettoyer les puces en début de ligne (•, -, *, etc.)
                if text and ('=' in text or ':' in text):
                    # Nettoyer la ligne des puces et espaces en début
                    cleaned_text = re.sub(r'^[\s•\-\*\u2022\u2023\u2043]+', '', text)

                    # Rechercher le séparateur (= ou :)
                    # On préfère '=' si présent, sinon on utilise ':'
                    if '=' in cleaned_text:
                        split_match = re.split(r'\s*=\s*', cleaned_text, maxsplit=1)
                    else:
                        split_match = re.split(r'\s*[:]\s*', cleaned_text, maxsplit=1)

                    if len(split_match) == 2:
                        term = split_match[0].strip()
                        definition = split_match[1].strip()

                        # Vérifier que le terme et la définition ne sont pas vides
                        # Filtrer les cas où le "terme" est juste "Définition" (titre de section)
                        if term and definition and term.lower() not in ['définition', 'definition']:
                            # Créer une note
                            note = ObsidianNote(term, definition, metadata.copy())
                            self.notes.append(note)

        return self.notes

    def get_notes(self) -> List[ObsidianNote]:
        """Retourne la liste des notes extraites"""
        return self.notes

    def add_note(self, title: str, definition: str, metadata: Dict = None) -> ObsidianNote:
        """Ajoute une nouvelle note manuellement"""
        note = ObsidianNote(title, definition, metadata or {})
        self.notes.append(note)
        return note

    def remove_note(self, index: int) -> bool:
        """Supprime une note par son index"""
        if 0 <= index < len(self.notes):
            self.notes.pop(index)
            return True
        return False

    def update_note(self, index: int, title: str = None, definition: str = None, metadata: Dict = None) -> bool:
        """Met à jour une note existante"""
        if 0 <= index < len(self.notes):
            if title is not None:
                self.notes[index].title = title
            if definition is not None:
                self.notes[index].definition = definition
            if metadata is not None:
                self.notes[index].metadata.update(metadata)
            return True
        return False

    def export_notes(self, output_dir: str) -> List[str]:
        """
        Exporte toutes les notes vers des fichiers markdown

        Args:
            output_dir: Répertoire de destination

        Returns:
            Liste des chemins des fichiers créés
        """
        # Créer le répertoire si nécessaire
        os.makedirs(output_dir, exist_ok=True)

        created_files = []
        template = self.config.get('note_template', {})

        for note in self.notes:
            filename = note.get_filename()
            filepath = os.path.join(output_dir, filename)

            # Écrire la note
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(note.to_markdown(template))

            created_files.append(filepath)

        return created_files

    def get_vault_path(self) -> str:
        """Retourne le chemin du vault Obsidian configuré"""
        vault_path = self.config.get('vault_path', '~/Obsidian/MyVault')
        # Expansion du tilde
        vault_path = os.path.expanduser(vault_path)

        # Ajouter le dossier par défaut
        default_folder = self.config.get('default_folder', '/Imports').lstrip('/')
        return os.path.join(vault_path, default_folder)
