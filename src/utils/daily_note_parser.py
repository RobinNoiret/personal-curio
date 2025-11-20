"""
Parser pour extraire les indicateurs des daily notes
"""
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from ..utils.logger import get_logger


class DailyNoteParser:
    """Parse les daily notes pour extraire les indicateurs clés"""

    def __init__(self):
        self.logger = get_logger()

    def parse_time_duration(self, time_str: str) -> Optional[float]:
        """
        Convertit une durée en heures (format: 7h50, 1h, 3min)

        Returns:
            Durée en heures (float) ou None si parsing échoue
        """
        if not time_str:
            return None

        time_str = time_str.strip().lower()
        hours = 0.0
        minutes = 0.0

        # Pattern pour heures
        hour_match = re.search(r'(\d+)h', time_str)
        if hour_match:
            hours = float(hour_match.group(1))

        # Pattern pour minutes
        min_match = re.search(r'(\d+)min', time_str)
        if min_match:
            minutes = float(min_match.group(1))

        if hours == 0 and minutes == 0:
            return None

        return hours + (minutes / 60.0)

    def parse_wake_time(self, time_str: str) -> Optional[float]:
        """
        Convertit une heure de réveil en heures décimales (format: 6h20, 7h00)

        Returns:
            Heure en format décimal (6h20 -> 6.33) ou None
        """
        if not time_str:
            return None

        time_str = time_str.strip().lower()

        # Pattern pour heure
        time_match = re.search(r'(\d+)h(\d+)?', time_str)
        if time_match:
            hours = int(time_match.group(1))
            minutes = int(time_match.group(2)) if time_match.group(2) else 0
            return hours + (minutes / 60.0)

        return None

    def parse_gourdes(self, gourde_str: str) -> Optional[int]:
        """
        Compte le nombre de gourdes (format: III, II, I)

        Returns:
            Nombre de gourdes ou None
        """
        if not gourde_str:
            return None

        gourde_str = gourde_str.strip()

        # Compter les I
        count = gourde_str.count('I')
        return count if count > 0 else None

    def parse_mood_emoji(self, mood_str: str) -> Optional[str]:
        """
        Extrait l'emoji d'humeur (🌞🌤️🌥️🌧️)

        Returns:
            Emoji d'humeur ou None
        """
        if not mood_str:
            return None

        mood_emojis = ['🌞', '🌤️', '🌥️', '🌧️']
        for emoji in mood_emojis:
            if emoji in mood_str:
                return emoji

        return None

    def parse_habits(self, content: str) -> Dict[str, Optional[str]]:
        """
        Parse le tableau de tracker d'habitudes

        Returns:
            Dict avec les habitudes et leurs statuts (🟩/🟨/🟧)
        """
        habits = {}

        # Trouver le tableau d'habitudes
        habit_section = re.search(
            r'# Tracker d\'habitudes\s+\|([^\n]+)\|\s+\|([^\n]+)\|\s+\|([^\n]+)\|',
            content,
            re.MULTILINE | re.DOTALL
        )

        if not habit_section:
            return habits

        # Extraire les noms des habitudes (ligne 1)
        header_line = habit_section.group(1)
        # Extraire les valeurs (ligne 3 - ligne 2 est la ligne de séparation)
        values_line = habit_section.group(3)

        # Parser les colonnes
        habit_names = [h.strip() for h in header_line.split('|') if h.strip()]
        habit_values = [v.strip() for v in values_line.split('|') if v.strip()]

        # Créer le dictionnaire
        for i, name in enumerate(habit_names):
            if i < len(habit_values):
                value = habit_values[i]
                # Nettoyer le nom (enlever les emojis pour avoir un nom simple)
                clean_name = re.sub(r'[^\w\s]', '', name).strip()
                habits[clean_name] = value if value in ['🟩', '🟨', '🟧'] else None

        return habits

    def parse_daily_note(self, file_path: str) -> Optional[Dict]:
        """
        Parse une daily note complète

        Returns:
            Dict avec tous les indicateurs extraits ou None si erreur
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extraire le nom du fichier pour la date
            filename = os.path.basename(file_path)
            date_match = re.match(r'(\d{4}-\d{2}-\d{2})', filename)
            date_str = date_match.group(1) if date_match else None

            data = {
                'date': date_str,
                'file_path': file_path
            }

            # Extraire chaque indicateur avec regex
            indicators = {
                'sleep_time': r'🛌\s*\*Temps de sommeil\s*:\*\s*([^\n]+)',
                'wake_time': r'⏰\s*\*Heure de réveil\s*:\*\s*([^\n]+)',
                'energy_level': r'🔋\s*\*Niveau d\'énergie.*?:\*\s*(\d+)',
                'mood': r'😄\s*\*Humeur.*?:\*\s*([^\n]+)',
                'gourdes': r'🍼\s*\*Nombre de gourde\s*:\*\s*([^\n]+)',
                'screen_time': r'📱\s*\*Temps d\'écran\s*:\*\s*([^\n]+)',
                'shower_time': r'🚿\s*\*Temps de douche\s*:\*\s*([^\n]+)',
                'reading': r'📚\s*\*Lecture\s*:\*\s*([^\n]+)',
            }

            for key, pattern in indicators.items():
                match = re.search(pattern, content)
                if match:
                    value = match.group(1).strip()

                    # Parser selon le type
                    if key == 'sleep_time':
                        data['sleep_hours'] = self.parse_time_duration(value)
                        data['sleep_raw'] = value
                    elif key == 'wake_time':
                        data['wake_time_decimal'] = self.parse_wake_time(value)
                        data['wake_time_raw'] = value
                    elif key == 'energy_level':
                        data['energy'] = int(value)
                    elif key == 'mood':
                        data['mood_emoji'] = self.parse_mood_emoji(value)
                        data['mood_raw'] = value
                    elif key == 'gourdes':
                        data['gourdes_count'] = self.parse_gourdes(value)
                        data['gourdes_raw'] = value
                    elif key == 'screen_time':
                        data['screen_hours'] = self.parse_time_duration(value)
                        data['screen_raw'] = value
                    elif key == 'shower_time':
                        data['shower_minutes'] = self.parse_time_duration(value) * 60 if self.parse_time_duration(value) else None
                        data['shower_raw'] = value
                    elif key == 'reading':
                        data['reading'] = value.lower() in ['yes', 'oui', 'y', 'o']
                        data['reading_raw'] = value

            # Parser les habitudes
            data['habits'] = self.parse_habits(content)

            return data

        except Exception as e:
            self.logger.error(f"Erreur lors du parsing de {file_path}: {e}", "DailyNoteParser")
            return None

    def get_daily_notes_in_range(
        self,
        vault_path: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """
        Récupère et parse toutes les daily notes dans une période

        Args:
            vault_path: Chemin vers le vault Obsidian
            start_date: Date de début
            end_date: Date de fin

        Returns:
            Liste de dictionnaires avec les données parsées
        """
        notes_data = []
        current_date = start_date

        while current_date <= end_date:
            # Construire le chemin du fichier
            year = current_date.strftime('%Y')
            month = current_date.strftime('%Y-%m')
            date_str = current_date.strftime('%Y-%m-%d')

            # Essayer plusieurs emplacements possibles
            possible_paths = [
                # 1. Directement dans journaling/ (structure plate)
                os.path.join(vault_path, '2-Caps', 'journaling', f'{date_str}.md'),
                # 2. Dans journaling/année/mois/ (structure par mois)
                os.path.join(vault_path, '2-Caps', 'journaling', year, month, f'{date_str}.md'),
                # 3. Dans journaling/année/ (structure par année seulement)
                os.path.join(vault_path, '2-Caps', 'journaling', year, f'{date_str}.md'),
            ]

            # Essayer chaque chemin
            found = False
            for file_path in possible_paths:
                if os.path.exists(file_path):
                    self.logger.debug(f"Note trouvée: {file_path}", "DailyNoteParser")
                    data = self.parse_daily_note(file_path)
                    if data:
                        notes_data.append(data)
                    found = True
                    break  # Arrêter dès qu'on trouve le fichier

            if not found:
                self.logger.debug(f"Note non trouvée pour {date_str}", "DailyNoteParser")

            current_date += timedelta(days=1)

        self.logger.info(f"Parsé {len(notes_data)} daily notes sur la période", "DailyNoteParser")
        return notes_data

    def get_last_n_days(self, vault_path: str, n_days: int = 30) -> List[Dict]:
        """
        Récupère les N derniers jours de notes

        Args:
            vault_path: Chemin vers le vault Obsidian
            n_days: Nombre de jours à récupérer

        Returns:
            Liste de dictionnaires avec les données parsées
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=n_days - 1)

        return self.get_daily_notes_in_range(vault_path, start_date, end_date)

    def get_current_week(self, vault_path: str) -> List[Dict]:
        """Récupère les notes de la semaine actuelle (lundi à aujourd'hui)"""
        today = datetime.now()
        # Trouver le lundi de cette semaine (0 = lundi)
        days_since_monday = today.weekday()
        start_date = today - timedelta(days=days_since_monday)

        return self.get_daily_notes_in_range(vault_path, start_date, today)

    def get_current_month(self, vault_path: str) -> List[Dict]:
        """Récupère les notes du mois actuel"""
        today = datetime.now()
        start_date = today.replace(day=1)

        return self.get_daily_notes_in_range(vault_path, start_date, today)
