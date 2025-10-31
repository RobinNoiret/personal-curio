"""
Module pour parser les comptes-rendus de réunion et extraire les données structurées
Version robuste qui s'adapte à différents formats
"""
import re
from typing import Dict, List, Optional


class CRParser:
    """Parser robuste pour extraire les informations d'un compte-rendu de prosit"""

    def __init__(self):
        self.section_titles = [
            'Mots clés',
            'Contexte',
            'Problématique',
            'Contraintes',
            'Livrables',
            'Généralisation',
            'Hypothèses',
            'Plan'  # Simplifié - cherche juste "Plan" au lieu de "Plan d'actions"
        ]

    def parse(self, text: str) -> Dict[str, any]:
        """
        Parse le texte du CR et extrait toutes les informations structurées
        Fonctionne avec différents formats de CR

        Args:
            text: Le texte complet du compte-rendu

        Returns:
            Dictionnaire contenant toutes les données extraites
        """
        data = {
            'bloc': '',
            'prosit_title': '',
            'prosit_number': '',
            'date': '',
            'mots_cles': [],
            'contexte': '',
            'problematique': '',
            'contraintes': [],
            'livrables': [],
            'generalisation': [],
            'hypotheses': [],
            'plan_actions': []
        }

        # Nettoyer et normaliser le texte
        text = self._normalize_text(text)
        lines = text.split('\n')

        # Extraire le bloc (première ligne)
        if lines:
            bloc_match = re.search(r'Bloc\s+(?:SF\s+)?(?:Ingénieur\s+)?(\d+|[A-Z]+)', lines[0], re.IGNORECASE)
            if bloc_match:
                data['bloc'] = bloc_match.group(1)

        # Extraire le titre et numéro du prosit
        prosit_match = re.search(r'Prosit\s+(?:aller\s+)?(\d+)\s*[–-]\s*(.+)', text, re.IGNORECASE)
        if prosit_match:
            data['prosit_number'] = prosit_match.group(1)
            title = prosit_match.group(2).strip()
            title = title.split('\n')[0].strip()
            data['prosit_title'] = title

        # Extraire la date
        date_match = re.search(r'(\d{1,2}[./]\d{1,2}[./]\d{4})', text)
        if date_match:
            data['date'] = date_match.group(1)

        # Extraire les sections par zones délimitées
        sections_map = self._extract_sections_by_zones(text)

        # Remplir les données selon le type de section
        for section_name, content in sections_map.items():
            content = content.strip()

            if section_name == 'Mots clés':
                data['mots_cles'] = self._extract_items(content)
            elif section_name == 'Contexte':
                data['contexte'] = self._clean_text(content)
            elif section_name == 'Problématique':
                data['problematique'] = self._clean_text(content)
            elif section_name == 'Contraintes':
                data['contraintes'] = self._extract_items(content)
            elif section_name == 'Livrables':
                data['livrables'] = self._extract_items(content)
            elif section_name == 'Généralisation':
                data['generalisation'] = self._extract_items(content)
            elif section_name == 'Hypothèses':
                data['hypotheses'] = self._extract_items(content)
            elif section_name == 'Plan':  # Correspondre au nouveau nom simplifié
                data['plan_actions'] = self._extract_items(content)

        return data

    def _normalize_text(self, text: str) -> str:
        """Normalise le texte en gérant les différentes apostrophes"""
        # Normaliser les apostrophes
        text = text.replace("'", "'").replace("'", "'").replace("'", "'")
        # Supprimer les lignes vides multiples
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        return text

    def _extract_sections_by_zones(self, text: str) -> Dict[str, str]:
        """
        Extrait les sections en trouvant leurs positions et le contenu entre elles
        Méthode robuste qui fonctionne même si le format varie

        Returns:
            Dictionnaire {nom_section: contenu}
        """
        sections_content = {}

        # Trouver toutes les positions des sections
        section_positions = []
        for section_name in self.section_titles:
            # Chercher la section (avec variantes)
            # Pour "Plan", on cherche "Plan" suivi de n'importe quoi ou de la fin
            if section_name == 'Plan':
                patterns = [
                    r"^Plan\s*d[\'\u2019]?\s*actions?\b",  # Plan d'actions avec différentes apostrophes
                    r'^Plan\b',  # Plan seul
                ]
            else:
                patterns = [
                    rf'^{re.escape(section_name)}(?:\s*[:\-]|\s*$)',  # Section avec : ou - ou seule
                    rf'^{re.escape(section_name)}\s*&',  # Section avec & (ex: Mots clés & Mots inconnus)
                ]

            # Chercher avec tous les patterns et prendre la première position
            all_matches = []
            for pattern in patterns:
                matches = list(re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE))
                all_matches.extend(matches)

            if all_matches:
                # Trier par position et prendre la première
                all_matches.sort(key=lambda m: m.start())
                match = all_matches[0]
                section_positions.append({
                    'name': section_name,
                    'start': match.start(),
                    'end': match.end()
                })

        # Trier par position
        section_positions.sort(key=lambda x: x['start'])

        # Extraire le contenu entre chaque section
        for i, section_info in enumerate(section_positions):
            section_name = section_info['name']
            content_start = section_info['end']

            # Trouver la fin (début de la section suivante ou fin du texte)
            if i + 1 < len(section_positions):
                content_end = section_positions[i + 1]['start']
            else:
                content_end = len(text)

            # Extraire le contenu
            content = text[content_start:content_end]

            # Nettoyer le contenu (enlever la première ligne si c'est le titre)
            lines = content.split('\n')
            if lines and lines[0].strip() == '':
                lines = lines[1:]
            content = '\n'.join(lines)

            sections_content[section_name] = content.strip()

        return sections_content

    def _extract_items(self, content: str) -> List[str]:
        """
        Extrait les items d'une section (liste à puces, numérotée ou texte libre)
        S'adapte au format trouvé

        Args:
            content: Le contenu de la section

        Returns:
            Liste des items extraits
        """
        if not content:
            return []

        items = []
        lines = content.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Nettoyer les puces, tirets, numéros
            cleaned = re.sub(r'^[•\-\*]\s*', '', line)  # Puces
            cleaned = re.sub(r'^\d+\.\s*', '', cleaned)  # Numéros

            if cleaned:
                items.append(cleaned)

        return items

    def _clean_text(self, content: str) -> str:
        """
        Nettoie un texte en joinant les lignes et en enlevant les espaces multiples

        Args:
            content: Le texte à nettoyer

        Returns:
            Texte nettoyé
        """
        if not content:
            return ''

        # Joindre les lignes multiples en un seul paragraphe
        lines = [line.strip() for line in content.split('\n') if line.strip()]

        # Nettoyer les puces/tirets en début
        cleaned_lines = []
        for line in lines:
            line = re.sub(r'^[•\-\*]\s*', '', line)
            if line:
                cleaned_lines.append(line)

        return ' '.join(cleaned_lines)

    def format_for_display(self, data: Dict[str, any]) -> str:
        """
        Formate les données extraites pour affichage dans l'interface

        Args:
            data: Dictionnaire des données extraites

        Returns:
            Texte formaté pour affichage
        """
        output = []
        output.append(f"Bloc: {data['bloc']}")
        output.append(f"Prosit {data['prosit_number']}: {data['prosit_title']}")
        output.append(f"Date: {data['date']}")
        output.append("")

        if data['mots_cles']:
            output.append("Mots clés:")
            for mot in data['mots_cles']:
                output.append(f"  • {mot}")
            output.append("")

        if data['contexte']:
            output.append(f"Contexte:\n{data['contexte']}")
            output.append("")

        if data['problematique']:
            output.append(f"Problématique:\n{data['problematique']}")
            output.append("")

        if data['contraintes']:
            output.append("Contraintes:")
            for c in data['contraintes']:
                output.append(f"  • {c}")
            output.append("")

        if data['livrables']:
            output.append("Livrables:")
            for l in data['livrables']:
                output.append(f"  • {l}")
            output.append("")

        if data['generalisation']:
            output.append("Généralisation:")
            if isinstance(data['generalisation'], list):
                for g in data['generalisation']:
                    output.append(f"  • {g}")
            else:
                output.append(data['generalisation'])
            output.append("")

        if data['hypotheses']:
            output.append("Hypothèses:")
            for i, h in enumerate(data['hypotheses'], 1):
                output.append(f"  {i}. {h}")
            output.append("")

        if data['plan_actions']:
            output.append("Plan d'actions:")
            for i, p in enumerate(data['plan_actions'], 1):
                output.append(f"  {i}. {p}")

        return '\n'.join(output)
