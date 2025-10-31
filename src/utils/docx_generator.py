"""
Module pour générer des documents Word à partir du template et des données extraites
"""
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from typing import Dict, List
import os
import re


class DocxGenerator:
    """Générateur de documents Word pour les prosits"""

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
        # Charger le template
        doc = Document(template_path)

        # Remplacer les informations en en-tête
        self._replace_text_in_document(doc, 'NOIRET Robin', nom)
        self._replace_text_in_document(doc, 'A3 FISA INFO', formation)
        self._replace_text_in_document(doc, 'Bloc XX', f"Bloc {data['bloc']}")
        self._replace_text_in_document(doc, 'Prosit 1 – Nom du prosit',
                                       f"Prosit {data['prosit_number']} – {data['prosit_title']}")
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
