"""
Module pour générer des documents Word à partir du template et des données extraites
"""
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from typing import Dict, List
import os
import re
from .logger import get_logger


class DocxGenerator:
    """Générateur de documents Word pour les prosits"""

    def __init__(self):
        self.logger = get_logger()
        self.logger.debug("DocxGenerator initialisé", "DocxGenerator")

    def generate(self, template_path: str, output_path: str, data: Dict, nom: str, formation: str):
        """
        Génère un document Word à partir du template et des données

        Args:
            template_path: Chemin vers le template .docx
            output_path: Chemin de sortie pour le document généré
            data: Dictionnaire contenant les données extraites du CR
            nom: Nom de l'étudiant
            formation: Formation de l'étudiant
        """
        self.logger.info(f"Génération du document DOCX pour Prosit {data['prosit_number']}", "DocxGenerator")

        # Charger le template
        doc = Document(template_path)
        self.logger.debug(f"Template chargé: {template_path}", "DocxGenerator")

        # Remplacer les informations en en-tête
        self._replace_text_in_document(doc, 'NOIRET Robin', nom)
        self._replace_text_in_document(doc, 'A3 FISA INFO', formation)
        self._replace_text_in_document(doc, 'Bloc XX', f"Bloc {data['bloc']}")

        # Remplacer le titre du prosit (gérer différents formats de tirets)
        self._replace_prosit_title(doc, data['prosit_number'], data['prosit_title'])

        self._replace_text_in_document(doc, '[Date]', data['date'])

        # Remplir les sections de l'introduction
        self._fill_section_content(doc, 'Mots clés', data['mots_cles'], list_type='bullet')
        self._fill_section_content(doc, 'Contexte', data['contexte'], list_type='text')
        self._fill_section_content(doc, 'Problématique', data['problematique'], list_type='text')
        self._fill_section_content(doc, 'Contraintes', data['contraintes'], list_type='bullet')
        self._fill_section_content(doc, 'Livrables', data['livrables'], list_type='bullet')
        self._fill_section_content(doc, 'Généralisation', data['generalisation'], list_type='bullet')
        self._fill_section_content(doc, 'Hypothèses', data['hypotheses'], list_type='numbered')
        self._fill_section_content(doc, 'Plan d\'actions', data['plan_actions'], list_type='numbered')

        # Ajouter un saut de page avant "Recherches & Expérimentations"
        self._add_page_break_before_section(doc, 'Recherches & Expérimentations')

        # Sauvegarder
        doc.save(output_path)
        self.logger.info(f"Document généré avec succès: {output_path}", "DocxGenerator")

    def _replace_prosit_title(self, doc: Document, prosit_number: str, prosit_title: str):
        """
        Remplace le titre du prosit en gérant différents formats de tirets
        Préserve les images, le formatage et tous les éléments du paragraphe

        Args:
            doc: Document Word
            prosit_number: Numéro du prosit
            prosit_title: Titre du prosit
        """
        import re
        from docx.oxml.ns import qn

        # Nouveau texte avec un tiret cadratin
        new_text = f"Prosit {prosit_number} – {prosit_title}"

        # Pattern pour matcher "Prosit X [tiret] Nom du prosit" avec différents tirets
        pattern = r'Prosit\s+\d+\s*[\-–—\u2013\u2014]\s*Nom du prosit'

        # Fonction pour remplacer le texte dans un paragraphe
        def replace_in_paragraph(paragraph):
            if not re.search(pattern, paragraph.text, re.IGNORECASE):
                return

            # Parcourir les runs et remplacer uniquement le texte
            full_text = paragraph.text
            if not re.search(pattern, full_text, re.IGNORECASE):
                return

            # Accumuler le texte à travers les runs pour trouver où se trouve le pattern
            accumulated_text = ""
            runs_to_process = []

            for run in paragraph.runs:
                run_start = len(accumulated_text)
                accumulated_text += run.text
                run_end = len(accumulated_text)
                runs_to_process.append((run, run_start, run_end))

            # Trouver la position du match dans le texte accumulé
            match = re.search(pattern, accumulated_text, re.IGNORECASE)
            if not match:
                return

            match_start = match.start()
            match_end = match.end()

            # Remplacer le texte dans les runs concernés
            for run, run_start, run_end in runs_to_process:
                # Ce run est avant le match
                if run_end <= match_start:
                    continue
                # Ce run est après le match
                elif run_start >= match_end:
                    continue
                # Ce run contient une partie du match
                else:
                    # Calculer quelle partie du run fait partie du match
                    overlap_start = max(0, match_start - run_start)
                    overlap_end = min(len(run.text), match_end - run_start)

                    # Construire le nouveau texte pour ce run
                    before = run.text[:overlap_start]
                    after = run.text[overlap_end:]

                    # Si c'est le premier run du match, ajouter le nouveau texte
                    if run_start <= match_start < run_end:
                        run.text = before + new_text + after
                    else:
                        # Pour les runs suivants, on enlève juste la partie qui matchait
                        run.text = before + after

        # Remplacer dans les paragraphes
        for paragraph in doc.paragraphs:
            replace_in_paragraph(paragraph)

        # Remplacer dans les tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        replace_in_paragraph(paragraph)

    def _replace_text_in_document(self, doc: Document, old_text: str, new_text: str):
        """
        Remplace du texte dans tout le document (paragraphes et tables)

        Args:
            doc: Document Word
            old_text: Texte à remplacer
            new_text: Nouveau texte
        """
        # Remplacer dans les paragraphes
        for paragraph in doc.paragraphs:
            if old_text in paragraph.text:
                self._replace_text_in_paragraph(paragraph, old_text, new_text)

        # Remplacer dans les tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        if old_text in paragraph.text:
                            self._replace_text_in_paragraph(paragraph, old_text, new_text)

    def _replace_text_in_paragraph(self, paragraph, old_text: str, new_text: str):
        """
        Remplace du texte dans un paragraphe en préservant le formatage

        Args:
            paragraph: Paragraphe Word
            old_text: Texte à remplacer
            new_text: Nouveau texte
        """
        if old_text in paragraph.text:
            # Reconstruire le paragraphe
            inline = paragraph.runs
            for run in inline:
                if old_text in run.text:
                    run.text = run.text.replace(old_text, new_text)

    def _find_section_index(self, doc: Document, section_title: str):
        """
        Trouve l'index du paragraphe contenant le titre de section

        Args:
            doc: Document Word
            section_title: Titre de la section à trouver

        Returns:
            Index du paragraphe, ou None si non trouvé
        """
        # Normaliser les apostrophes pour la comparaison
        def normalize_text(text):
            return text.replace("'", "'").replace("'", "'").replace("'", "'")

        normalized_title = normalize_text(section_title)

        # Pour "Plan d'actions", chercher aussi juste "Plan"
        alternatives = [normalized_title]
        if "Plan" in section_title:
            alternatives.append("Plan d'actions")
            alternatives.append("Plan dactions")
            alternatives.append("Plan d actions")

        for i, paragraph in enumerate(doc.paragraphs):
            text = paragraph.text.strip()
            normalized_text = normalize_text(text)

            # Vérifier correspondance exacte ou partielle pour Plan
            for alt in alternatives:
                if normalized_text == normalize_text(alt):
                    return i
                # Chercher "Plan" au début de la ligne
                if alt == "Plan d'actions" and normalized_text.startswith("Plan"):
                    return i

        return None

    def _fill_section_content(self, doc: Document, section_title: str, content, list_type='text'):
        """
        Remplit une section en remplaçant tous les placeholders

        Args:
            doc: Document Word
            section_title: Titre de la section
            content: Contenu à insérer (str ou list)
            list_type: Type de liste ('text', 'bullet', 'numbered')
        """
        section_idx = self._find_section_index(doc, section_title)

        if section_idx is None:
            return

        # Trouver la prochaine section Heading ou section importante
        next_heading_idx = None
        for i in range(section_idx + 1, len(doc.paragraphs)):
            p = doc.paragraphs[i]
            p_text = p.text.strip()

            # Arrêter à un Heading ou à une section connue (comme "Recherches & Expérimentations")
            if p.style.name.startswith('Heading') or p_text == 'Recherches & Expérimentations':
                next_heading_idx = i
                break

        # Déterminer la plage de paragraphes à traiter
        if next_heading_idx:
            content_range = range(section_idx + 1, next_heading_idx)
        else:
            content_range = range(section_idx + 1, len(doc.paragraphs))

        # Supprimer tous les paragraphes placeholders dans cette section
        indices_to_delete = list(content_range)
        for idx in reversed(indices_to_delete):
            if idx < len(doc.paragraphs):
                self._delete_paragraph(doc.paragraphs[idx])

        # Insérer le nouveau contenu
        if not content:
            return

        # Obtenir l'élément XML du paragraphe de section
        section_para = doc.paragraphs[section_idx]
        parent = section_para._element.getparent()
        section_element = section_para._element

        if list_type == 'bullet' and isinstance(content, list):
            # Créer des paragraphes avec puces
            for item in content:
                # Créer un nouvel élément de paragraphe
                from docx.oxml import parse_xml
                from docx.oxml.ns import qn

                new_p_xml = parse_xml(r'<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:r><w:t></w:t></w:r></w:p>')
                # Insérer après le dernier élément ajouté
                section_element.addnext(new_p_xml)
                section_element = new_p_xml

                # Récupérer le paragraphe Python correspondant
                # On doit reconstruire le document pour récupérer le nouveau paragraphe
                for p in doc.paragraphs:
                    if p._element == new_p_xml:
                        p.text = f"• {item}"
                        p.paragraph_format.left_indent = Inches(0.25)
                        break

        elif list_type == 'numbered' and isinstance(content, list):
            # Créer des paragraphes numérotés
            for i, item in enumerate(content, 1):
                from docx.oxml import parse_xml

                new_p_xml = parse_xml(r'<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:r><w:t></w:t></w:r></w:p>')
                section_element.addnext(new_p_xml)
                section_element = new_p_xml

                for p in doc.paragraphs:
                    if p._element == new_p_xml:
                        p.text = f"{i}. {item}"
                        p.paragraph_format.left_indent = Inches(0.25)
                        break

        elif list_type == 'text':
            # Texte simple
            if isinstance(content, list):
                content = ' '.join(content)

            from docx.oxml import parse_xml

            new_p_xml = parse_xml(r'<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:r><w:t></w:t></w:r></w:p>')
            section_element.addnext(new_p_xml)

            for p in doc.paragraphs:
                if p._element == new_p_xml:
                    p.text = content
                    break

    def _add_page_break_before_section(self, doc: Document, section_title: str):
        """
        Ajoute un saut de page avant une section

        Args:
            doc: Document Word
            section_title: Titre de la section avant laquelle ajouter le saut de page
        """
        section_idx = self._find_section_index(doc, section_title)

        if section_idx is None:
            return

        # Récupérer le paragraphe de la section
        section_para = doc.paragraphs[section_idx]

        # Ajouter un saut de page avant ce paragraphe
        # On insère un nouveau paragraphe vide juste avant avec un saut de page
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn

        # Insérer un paragraphe vide avant la section
        new_para = section_para.insert_paragraph_before('')

        # Ajouter le saut de page à ce paragraphe
        run = new_para.runs[0] if new_para.runs else new_para.add_run()
        run.add_break(WD_BREAK.PAGE)

    def _delete_paragraph(self, paragraph):
        """
        Supprime un paragraphe du document

        Args:
            paragraph: Paragraphe à supprimer
        """
        p = paragraph._element
        p.getparent().remove(p)
