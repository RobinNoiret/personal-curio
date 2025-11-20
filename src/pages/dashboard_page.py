"""
Page Dashboard pour visualiser les données du journaling
"""
import customtkinter as ctk
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from .base_page import BasePage
from ..ui_components import Container
from ..utils.daily_note_parser import DailyNoteParser
from ..utils.logger import get_logger
from ..constants import TITLE_FONT, TEXT_FONT, FONTS


class DashboardPage(BasePage):
    """Page Dashboard pour la visualisation des données de journaling"""

    def __init__(self, parent, colors, config=None, on_navigate=None):
        super().__init__(parent, colors, on_navigate)
        self.config = config or {}
        self.logger = get_logger()
        self.parser = DailyNoteParser()
        self.data = []
        self.current_period = 'week'  # 'week', 'month', 'custom'

        # Couleurs personnalisées pour le dashboard
        self.yellow_pale = '#FFF9E6'  # Jaune très pâle
        self.yellow_main = '#FFD93D'  # Jaune principal
        self.yellow_dark = '#FFC107'  # Jaune foncé

    def render(self) -> ctk.CTkFrame:
        """Rend la page dashboard"""
        self.container = ctk.CTkFrame(self.parent, fg_color=self.colors['white'])
        self.container.pack(fill='both', expand=True)

        # Header
        self._create_header()

        # Charger les données
        self._load_data()

        # Container principal avec scroll
        main_scroll = ctk.CTkScrollableFrame(
            self.container,
            fg_color=self.colors['white']
        )
        main_scroll.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        # Si pas de données
        if not self.data:
            self._show_no_data_message(main_scroll)
            return self.container

        # Statistiques en haut
        self._create_stats_cards(main_scroll)

        # Graphiques
        self._create_charts(main_scroll)

        return self.container

    def _create_header(self):
        """Crée le header avec titre et filtres"""
        header = ctk.CTkFrame(self.container, fg_color=self.colors['white'], height=100)
        header.pack(fill='x', padx=0, pady=0)
        header.pack_propagate(False)

        # Container interne pour centrer verticalement
        inner = Container.transparent(header)
        inner.pack(fill='both', expand=True, padx=30, pady=20)

        # Titre à gauche
        title_frame = Container.transparent(inner)
        title_frame.pack(side='left')

        ctk.CTkLabel(
            title_frame,
            text="Daily Dashboard",
            font=FONTS['title_medium'],
            text_color=self.colors['black']
        ).pack(anchor='w')

        # Filtres à droite
        filter_frame = Container.transparent(inner)
        filter_frame.pack(side='right')

        # Boutons de période
        period_frame = Container.transparent(filter_frame)
        period_frame.pack()

        ctk.CTkLabel(
            period_frame,
            text="Période:",
            font=FONTS['body_bold'],
            text_color=self.colors['black']
        ).pack(side='left', padx=(0, 10))

        # Boutons de sélection
        self.period_buttons = {}
        periods = [
            ('week', 'Semaine'),
            ('month', 'Mois'),
            ('30days', '30 jours')
        ]

        for key, label in periods:
            btn = ctk.CTkButton(
                period_frame,
                text=label,
                command=lambda k=key: self._change_period(k),
                width=90,
                height=38,
                font=FONTS['body_bold'],
                fg_color=self.yellow_main if key == self.current_period else self.colors['white'],
                text_color=self.colors['black'],
                border_width=2,
                border_color=self.yellow_main,
                hover_color=self.yellow_dark,
                corner_radius=8
            )
            btn.pack(side='left', padx=3)
            self.period_buttons[key] = btn

    def _change_period(self, period: str):
        """Change la période affichée"""
        self.current_period = period

        # Mettre à jour les boutons
        for key, btn in self.period_buttons.items():
            if key == period:
                btn.configure(fg_color=self.yellow_main)
            else:
                btn.configure(fg_color=self.colors['white'])

        # Recharger les données et rafraîchir
        self._reload_page()

    def _reload_page(self):
        """Recharge la page complète"""
        # Nettoyer et re-rendre
        self.clear()
        self.render()

    def _load_data(self):
        """Charge les données selon la période sélectionnée"""
        vault_path = self.config.get('obsidian_vault_path', '')

        if not vault_path or not os.path.exists(vault_path):
            self.logger.warning("Chemin vault Obsidian non configuré", "Dashboard")
            self.data = []
            return

        try:
            if self.current_period == 'week':
                self.data = self.parser.get_current_week(vault_path)
            elif self.current_period == 'month':
                self.data = self.parser.get_current_month(vault_path)
            elif self.current_period == '30days':
                self.data = self.parser.get_last_n_days(vault_path, 30)
            else:
                self.data = self.parser.get_current_week(vault_path)

            self.logger.info(f"Données chargées: {len(self.data)} jours", "Dashboard")

        except Exception as e:
            self.logger.error(f"Erreur chargement données: {e}", "Dashboard")
            self.data = []

    def _show_no_data_message(self, parent):
        """Affiche un message si pas de données"""
        message_frame = Container.transparent(parent)
        message_frame.pack(expand=True, pady=100)

        ctk.CTkLabel(
            message_frame,
            text="📭",
            font=("Inter", 72)
        ).pack(pady=20)

        ctk.CTkLabel(
            message_frame,
            text="Aucune donnée trouvée",
            font=("Degular Medium", 24, "bold"),
            text_color=self.colors['black']
        ).pack()

        ctk.CTkLabel(
            message_frame,
            text="Vérifiez que le chemin vers votre vault Obsidian est correctement configuré",
            font=("Inter", 14),
            text_color=self.colors['text_gray']
        ).pack(pady=(10, 0))

    def _create_stats_cards(self, parent):
        """Crée les cartes de statistiques"""
        stats_container = ctk.CTkFrame(parent, fg_color='transparent')
        stats_container.pack(fill='x', pady=(0, 30))

        # Calculer les statistiques
        stats = self._calculate_stats()

        # Cartes principales (3 grandes cartes en jaune pâle)
        main_row = Container.transparent(stats_container)
        main_row.pack(fill='x', pady=(0, 10))

        main_cards = [
            ("Sommeil moyen", f"{stats['avg_sleep']:.1f}h", self.yellow_pale),
            ("Temps d'écran", f"{stats['avg_screen']:.1f}h", self.yellow_pale),
            ("Gourdes/jour", f"{stats['avg_gourdes']:.1f}", self.yellow_pale),
        ]

        for label, value, bg_color in main_cards:
            self._create_main_stat_card(main_row, label, value, bg_color)

    def _create_main_stat_card(self, parent, label: str, value: str, bg_color: str):
        """Crée une grande carte de statistique (pour les 3 principales)"""
        card = ctk.CTkFrame(
            parent,
            fg_color=bg_color,
            corner_radius=15,
            border_width=2,
            border_color=self.yellow_main
        )
        card.pack(side='left', fill='both', expand=True, padx=8)

        # Padding interne - centré verticalement et horizontalement
        inner = Container.transparent(card)
        inner.pack(fill='both', expand=True, padx=25, pady=25)
        inner.place(relx=0.5, rely=0.5, anchor='center')

        # Label centré
        ctk.CTkLabel(
            inner,
            text=label,
            font=FONTS['body_bold'],
            text_color=self.colors['text_gray'],
            anchor='center'
        ).pack()

        # Valeur centrée
        ctk.CTkLabel(
            inner,
            text=value,
            font=FONTS['title_medium'],
            text_color=self.colors['black'],
            anchor='center'
        ).pack(pady=(8, 0))


    def _calculate_stats(self) -> Dict:
        """Calcule les statistiques à partir des données"""
        if not self.data:
            return {
                'avg_sleep': 0, 'avg_energy': 0, 'avg_gourdes': 0,
                'avg_screen': 0, 'avg_wake': 'N/A', 'reading_days': 0,
                'total_days': 0, 'best_habit': 'N/A', 'dominant_mood': 'N/A'
            }

        # Calculs de base
        sleep_values = [d['sleep_hours'] for d in self.data if 'sleep_hours' in d and d['sleep_hours']]
        energy_values = [d['energy'] for d in self.data if 'energy' in d and d['energy']]
        gourdes_values = [d['gourdes_count'] for d in self.data if 'gourdes_count' in d and d['gourdes_count']]
        screen_values = [d['screen_hours'] for d in self.data if 'screen_hours' in d and d['screen_hours']]
        wake_values = [d['wake_time_decimal'] for d in self.data if 'wake_time_decimal' in d and d['wake_time_decimal']]

        reading_days = sum(1 for d in self.data if d.get('reading', False))

        # Moyennes
        avg_sleep = sum(sleep_values) / len(sleep_values) if sleep_values else 0
        avg_energy = sum(energy_values) / len(energy_values) if energy_values else 0
        avg_gourdes = sum(gourdes_values) / len(gourdes_values) if gourdes_values else 0
        avg_screen = sum(screen_values) / len(screen_values) if screen_values else 0
        avg_wake_decimal = sum(wake_values) / len(wake_values) if wake_values else 0

        # Formater l'heure de réveil
        if avg_wake_decimal > 0:
            hours = int(avg_wake_decimal)
            minutes = int((avg_wake_decimal - hours) * 60)
            avg_wake = f"{hours}h{minutes:02d}"
        else:
            avg_wake = "N/A"

        # Meilleure habitude (celle avec le plus de 🟩)
        habit_scores = {}
        for day_data in self.data:
            for habit, status in day_data.get('habits', {}).items():
                if habit not in habit_scores:
                    habit_scores[habit] = 0
                if status == '🟩':
                    habit_scores[habit] += 1

        best_habit = max(habit_scores.items(), key=lambda x: x[1])[0] if habit_scores else "N/A"
        # Raccourcir le nom si trop long
        if len(best_habit) > 12:
            best_habit = best_habit[:12] + "..."

        # Humeur dominante
        mood_counts = {}
        for day_data in self.data:
            mood = day_data.get('mood_emoji')
            if mood:
                mood_counts[mood] = mood_counts.get(mood, 0) + 1

        dominant_mood = max(mood_counts.items(), key=lambda x: x[1])[0] if mood_counts else "N/A"

        return {
            'avg_sleep': avg_sleep,
            'avg_energy': avg_energy,
            'avg_gourdes': avg_gourdes,
            'avg_screen': avg_screen,
            'avg_wake': avg_wake,
            'reading_days': reading_days,
            'total_days': len(self.data),
            'best_habit': best_habit,
            'dominant_mood': dominant_mood
        }

    def _create_charts(self, parent):
        """Crée les graphiques"""
        charts_container = ctk.CTkFrame(parent, fg_color='transparent')
        charts_container.pack(fill='both', expand=True)

        # Ligne 1: Sommeil et Gourdes
        row1 = Container.transparent(charts_container)
        row1.pack(fill='x', pady=15)

        self._create_sleep_chart(row1)
        self._create_gourdes_chart(row1)

        # Ligne 2: Humeur et Habitudes en parallèle
        row2 = Container.transparent(charts_container)
        row2.pack(fill='x', pady=15)

        self._create_mood_chart(row2)
        self._create_habits_heatmap(row2)

    def _create_chart_container(self, parent, title: str, full_width: bool = False) -> ctk.CTkFrame:
        """Crée un container pour un graphique"""
        container = ctk.CTkFrame(
            parent,
            fg_color=self.colors['white'],
            corner_radius=12,
            border_width=0
        )

        if full_width:
            container.pack(fill='both', expand=True, padx=0)
        else:
            container.pack(side='left', fill='both', expand=True, padx=10)

        # Titre
        title_label = ctk.CTkLabel(
            container,
            text=title,
            font=FONTS['title_small'],
            text_color=self.colors['black'],
            anchor='w'
        )
        title_label.pack(fill='x', padx=15, pady=(15, 5))

        return container

    def _create_sleep_chart(self, parent):
        """Crée le graphique du sommeil"""
        container = self._create_chart_container(parent, "Temps de sommeil")

        # Préparer les données
        dates = []
        sleep_hours = []

        for day_data in self.data:
            if 'date' in day_data and 'sleep_hours' in day_data and day_data['sleep_hours']:
                dates.append(datetime.strptime(day_data['date'], '%Y-%m-%d'))
                sleep_hours.append(day_data['sleep_hours'])

        if not dates:
            ctk.CTkLabel(
                container,
                text="Pas de données disponibles",
                font=("Inter", 12),
                text_color=self.colors['text_gray']
            ).pack(pady=50)
            return

        # Créer la figure
        fig = Figure(figsize=(5, 3.2), dpi=100, facecolor='white')
        ax = fig.add_subplot(111)

        # Ligne avec couleur jaune
        ax.plot(dates, sleep_hours, marker='o', linewidth=2.5, markersize=7,
                color=self.yellow_dark, markerfacecolor=self.yellow_main,
                markeredgewidth=0)
        ax.axhline(y=7, color='#D1D5DB', linestyle='--', linewidth=1.5, alpha=0.8)

        ax.set_ylabel('')
        ax.set_ylim(min(sleep_hours) - 0.5, max(sleep_hours) + 0.5)
        ax.grid(False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#E5E7EB')
        ax.spines['bottom'].set_color('#E5E7EB')

        # Contrôler explicitement les ticks de l'axe X pour éviter les duplications
        ax.set_xticks(dates)  # Définir exactement quelles dates afficher
        ax.set_xticklabels([d.strftime('%d/%m') for d in dates])  # Labels manuels
        ax.tick_params(axis='x', labelsize=9, colors='#6B7280', pad=5, rotation=0)
        ax.tick_params(axis='y', labelsize=9, colors='#6B7280')

        # Ajuster les marges et désactiver l'auto-ajustement
        fig.subplots_adjust(left=0.08, right=0.98, top=0.95, bottom=0.15)
        fig.set_tight_layout(False)

        # Intégrer dans tkinter
        canvas = FigureCanvasTkAgg(fig, container)
        canvas.draw_idle()  # draw_idle au lieu de draw pour éviter les redessins multiples
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=(5, 10))


    def _create_gourdes_chart(self, parent):
        """Crée le graphique des gourdes"""
        container = self._create_chart_container(parent, "Hydratation")

        # Préparer les données
        dates = []
        gourdes = []

        for day_data in self.data:
            if 'date' in day_data and 'gourdes_count' in day_data and day_data['gourdes_count']:
                dates.append(datetime.strptime(day_data['date'], '%Y-%m-%d'))
                gourdes.append(day_data['gourdes_count'])

        if not dates:
            ctk.CTkLabel(
                container,
                text="Pas de données disponibles",
                font=("Inter", 12),
                text_color=self.colors['text_gray']
            ).pack(pady=50)
            return

        # Créer la figure
        fig = Figure(figsize=(5, 3.2), dpi=100, facecolor='white')
        ax = fig.add_subplot(111)

        # Barres en jaune
        ax.bar(dates, gourdes, color=self.yellow_main, alpha=0.9, width=0.6,
               edgecolor='none')

        ax.set_ylabel('')
        ax.set_ylim(0, max(gourdes) + 1)
        ax.grid(False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#E5E7EB')
        ax.spines['bottom'].set_color('#E5E7EB')

        # Contrôler explicitement les ticks de l'axe X pour éviter les duplications
        ax.set_xticks(dates)  # Définir exactement quelles dates afficher
        ax.set_xticklabels([d.strftime('%d/%m') for d in dates])  # Labels manuels
        ax.tick_params(axis='x', labelsize=9, colors='#6B7280', pad=5, rotation=0)
        ax.tick_params(axis='y', labelsize=9, colors='#6B7280')

        # Ajuster les marges et désactiver l'auto-ajustement
        fig.subplots_adjust(left=0.08, right=0.98, top=0.95, bottom=0.15)
        fig.set_tight_layout(False)

        # Intégrer dans tkinter
        canvas = FigureCanvasTkAgg(fig, container)
        canvas.draw_idle()  # draw_idle au lieu de draw pour éviter les redessins multiples
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=(5, 10))

    def _create_mood_chart(self, parent):
        """Crée le graphique d'humeur"""
        container = self._create_chart_container(parent, "Humeur")

        # Préparer les données
        dates = []
        moods = []
        mood_mapping = {'🌞': 4, '🌤️': 3, '🌥️': 2, '🌧️': 1}

        for day_data in self.data:
            if 'date' in day_data and 'mood_emoji' in day_data and day_data['mood_emoji']:
                dates.append(datetime.strptime(day_data['date'], '%Y-%m-%d'))
                mood_value = mood_mapping.get(day_data['mood_emoji'], 0)
                moods.append(mood_value)

        if not dates:
            ctk.CTkLabel(
                container,
                text="Pas de données disponibles",
                font=("Inter", 12),
                text_color=self.colors['text_gray']
            ).pack(pady=50)
            return

        # Créer la figure
        fig = Figure(figsize=(6, 3.2), dpi=100, facecolor='white')
        ax = fig.add_subplot(111)

        # Couleurs selon l'humeur (jaune pour positif, gris pour négatif)
        colors = [self.yellow_main if m >= 3 else '#D1D5DB' for m in moods]
        ax.scatter(dates, moods, c=colors, s=120, alpha=0.9, edgecolors='none')

        ax.set_ylabel('')
        ax.set_ylim(0.5, 4.5)
        ax.set_yticks([1, 2, 3, 4])
        ax.set_yticklabels(['🌧️', '🌥️', '🌤️', '🌞'], fontsize=18)  # Augmenter la taille
        ax.grid(False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)  # Cacher l'axe gauche pour un meilleur rendu
        ax.spines['bottom'].set_color('#E5E7EB')

        # Contrôler explicitement les ticks de l'axe X pour éviter les duplications
        ax.set_xticks(dates)  # Définir exactement quelles dates afficher
        ax.set_xticklabels([d.strftime('%d/%m') for d in dates])  # Labels manuels
        ax.tick_params(axis='x', labelsize=9, colors='#6B7280', pad=5, rotation=0)
        ax.tick_params(axis='y', labelsize=9, colors='#6B7280')

        # Ajuster les marges et désactiver l'auto-ajustement
        fig.subplots_adjust(left=0.08, right=0.98, top=0.95, bottom=0.15)
        fig.set_tight_layout(False)

        # Intégrer dans tkinter
        canvas = FigureCanvasTkAgg(fig, container)
        canvas.draw_idle()  # draw_idle au lieu de draw pour éviter les redessins multiples
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=(5, 10))

    def _create_habits_heatmap(self, parent):
        """Crée la heatmap des habitudes"""
        container = ctk.CTkFrame(
            parent,
            fg_color=self.colors['white'],
            corner_radius=12,
            border_width=0
        )
        container.pack(fill='x', padx=0)

        # Titre
        ctk.CTkLabel(
            container,
            text="✅ Suivi des habitudes",
            font=FONTS['title_small'],
            text_color=self.colors['black'],
            anchor='w'
        ).pack(fill='x', padx=15, pady=(15, 10))

        # Récupérer toutes les habitudes uniques
        all_habits = set()
        for day_data in self.data:
            all_habits.update(day_data.get('habits', {}).keys())

        if not all_habits:
            ctk.CTkLabel(
                container,
                text="Pas de données d'habitudes disponibles",
                font=("Inter", 12),
                text_color=self.colors['text_gray']
            ).pack(pady=20)
            return

        # Frame pour le tableau
        table_frame = Container.transparent(container)
        table_frame.pack(fill='x', padx=20, pady=(0, 20))

        # Header avec les dates
        header_row = Container.transparent(table_frame)
        header_row.pack(fill='x', pady=(0, 8))

        # Cellule vide en haut à gauche
        ctk.CTkLabel(
            header_row,
            text="",
            width=150,
            font=("Inter", 10)
        ).pack(side='left', padx=2)

        # Dates
        for day_data in self.data:
            if 'date' in day_data:
                date_obj = datetime.strptime(day_data['date'], '%Y-%m-%d')
                date_label = date_obj.strftime('%d/%m')

                ctk.CTkLabel(
                    header_row,
                    text=date_label,
                    width=45,
                    font=("Inter", 10, "bold"),
                    text_color=self.colors['black']
                ).pack(side='left', padx=2)

        # Une ligne par habitude
        for habit in sorted(all_habits):
            habit_row = Container.transparent(table_frame)
            habit_row.pack(fill='x', pady=3)

            # Nom de l'habitude
            ctk.CTkLabel(
                habit_row,
                text=habit,
                width=150,
                font=("Inter", 12, "bold"),
                text_color=self.colors['black'],
                anchor='w'
            ).pack(side='left', padx=2)

            # Statuts pour chaque jour
            for day_data in self.data:
                status = day_data.get('habits', {}).get(habit, '')

                # Couleur selon le statut (vert/rouge pastel)
                if status == '🟩':
                    bg_color = '#A7F3D0'  # Vert pastel pour succès
                elif status == '🟨':
                    bg_color = '#FEF08A'  # Jaune pastel
                elif status == '🟧':
                    bg_color = '#FECACA'  # Rouge pastel pour échec
                else:
                    bg_color = '#E5E7EB'  # Gris clair pour vide

                status_cell = ctk.CTkFrame(
                    habit_row,
                    width=45,
                    height=35,
                    fg_color=bg_color,
                    corner_radius=8
                )
                status_cell.pack(side='left', padx=2)
                status_cell.pack_propagate(False)
