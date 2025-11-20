"""
Page Dashboard pour visualiser les données du journaling
"""
import customtkinter as ctk
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from .base_page import BasePage
from ..ui_components import Container
from ..utils.daily_note_parser import DailyNoteParser
from ..utils.logger import get_logger


class DashboardPage(BasePage):
    """Page Dashboard pour la visualisation des données de journaling"""

    def __init__(self, parent, colors, config=None, on_navigate=None):
        super().__init__(parent, colors, on_navigate)
        self.config = config or {}
        self.logger = get_logger()
        self.parser = DailyNoteParser()
        self.data = []
        self.current_period = 'week'  # 'week', 'month', 'custom'

        # Configuration matplotlib pour un style moderne
        plt.style.use('seaborn-v0_8-darkgrid')

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
        header = ctk.CTkFrame(self.container, fg_color=self.colors['gray'], height=100)
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
            font=("Degular Medium", 32, "bold"),
            text_color=self.colors['black']
        ).pack(anchor='w')

        ctk.CTkLabel(
            title_frame,
            text="Visualisez vos données de journaling",
            font=("Inter", 14),
            text_color=self.colors['text_gray']
        ).pack(anchor='w', pady=(5, 0))

        # Filtres à droite
        filter_frame = Container.transparent(inner)
        filter_frame.pack(side='right')

        # Boutons de période
        period_frame = Container.transparent(filter_frame)
        period_frame.pack()

        ctk.CTkLabel(
            period_frame,
            text="Période:",
            font=("Inter", 12),
            text_color=self.colors['text_gray']
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
                width=80,
                height=35,
                font=("Inter", 12),
                fg_color=self.colors['yellow'] if key == self.current_period else self.colors['white'],
                text_color=self.colors['black'],
                border_width=1,
                border_color=self.colors['border'],
                hover_color=self.colors['yellow']
            )
            btn.pack(side='left', padx=2)
            self.period_buttons[key] = btn

    def _change_period(self, period: str):
        """Change la période affichée"""
        self.current_period = period

        # Mettre à jour les boutons
        for key, btn in self.period_buttons.items():
            if key == period:
                btn.configure(fg_color=self.colors['yellow'])
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
        stats_container.pack(fill='x', pady=(0, 20))

        # Calculer les statistiques
        stats = self._calculate_stats()

        # Grid de cartes (2 lignes x 4 colonnes)
        cards_data = [
            ("😴 Sommeil moyen", f"{stats['avg_sleep']:.1f}h", self.colors['blue']),
            ("⚡ Énergie moyenne", f"{stats['avg_energy']:.1f}/10", self.colors['yellow']),
            ("💧 Gourdes/jour", f"{stats['avg_gourdes']:.1f}", self.colors['blue']),
            ("📱 Temps d'écran", f"{stats['avg_screen']:.1f}h", self.colors['yellow']),
            ("⏰ Réveil moyen", stats['avg_wake'], self.colors['blue']),
            ("📚 Jours de lecture", f"{stats['reading_days']}/{stats['total_days']}", self.colors['yellow']),
            ("✅ Meilleure habitude", stats['best_habit'], self.colors['blue']),
            ("😊 Humeur dominante", stats['dominant_mood'], self.colors['yellow']),
        ]

        # Créer 2 lignes
        for row in range(2):
            row_frame = Container.transparent(stats_container)
            row_frame.pack(fill='x', pady=5)

            for col in range(4):
                idx = row * 4 + col
                if idx < len(cards_data):
                    label, value, color = cards_data[idx]
                    self._create_stat_card(row_frame, label, value, color)

    def _create_stat_card(self, parent, label: str, value: str, accent_color: str):
        """Crée une carte de statistique"""
        card = ctk.CTkFrame(
            parent,
            fg_color=self.colors['gray'],
            corner_radius=10
        )
        card.pack(side='left', fill='both', expand=True, padx=5)

        # Padding interne
        inner = Container.transparent(card)
        inner.pack(fill='both', expand=True, padx=15, pady=15)

        # Label
        ctk.CTkLabel(
            inner,
            text=label,
            font=("Inter", 12),
            text_color=self.colors['text_gray'],
            anchor='w'
        ).pack(fill='x')

        # Valeur
        ctk.CTkLabel(
            inner,
            text=value,
            font=("Degular Medium", 24, "bold"),
            text_color=self.colors['black'],
            anchor='w'
        ).pack(fill='x', pady=(5, 0))

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

        # Ligne 1: Sommeil et Énergie
        row1 = Container.transparent(charts_container)
        row1.pack(fill='x', pady=10)

        self._create_sleep_chart(row1)
        self._create_energy_chart(row1)

        # Ligne 2: Gourdes et Humeur
        row2 = Container.transparent(charts_container)
        row2.pack(fill='x', pady=10)

        self._create_gourdes_chart(row2)
        self._create_mood_chart(row2)

        # Ligne 3: Habitudes (pleine largeur)
        row3 = Container.transparent(charts_container)
        row3.pack(fill='x', pady=10)

        self._create_habits_heatmap(row3)

    def _create_chart_container(self, parent, title: str) -> ctk.CTkFrame:
        """Crée un container pour un graphique"""
        container = ctk.CTkFrame(
            parent,
            fg_color=self.colors['gray'],
            corner_radius=10
        )
        container.pack(side='left', fill='both', expand=True, padx=5)

        # Titre
        title_label = ctk.CTkLabel(
            container,
            text=title,
            font=("Degular Medium", 16, "bold"),
            text_color=self.colors['black'],
            anchor='w'
        )
        title_label.pack(fill='x', padx=15, pady=(15, 10))

        return container

    def _create_sleep_chart(self, parent):
        """Crée le graphique du sommeil"""
        container = self._create_chart_container(parent, "😴 Temps de sommeil")

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
        fig = Figure(figsize=(5, 3), dpi=100, facecolor=self.colors['gray'])
        ax = fig.add_subplot(111)

        ax.plot(dates, sleep_hours, marker='o', linewidth=2, markersize=6, color='#3B82F6')
        ax.axhline(y=7, color='#10B981', linestyle='--', linewidth=1, alpha=0.5, label='Objectif 7h')

        ax.set_ylabel('Heures', fontsize=10)
        ax.set_ylim(min(sleep_hours) - 0.5, max(sleep_hours) + 0.5)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)

        # Format des dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        fig.autofmt_xdate(rotation=45)

        fig.tight_layout()

        # Intégrer dans tkinter
        canvas = FigureCanvasTkAgg(fig, container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=(0, 10))

    def _create_energy_chart(self, parent):
        """Crée le graphique de l'énergie"""
        container = self._create_chart_container(parent, "⚡ Niveau d'énergie")

        # Préparer les données
        dates = []
        energy_levels = []

        for day_data in self.data:
            if 'date' in day_data and 'energy' in day_data and day_data['energy']:
                dates.append(datetime.strptime(day_data['date'], '%Y-%m-%d'))
                energy_levels.append(day_data['energy'])

        if not dates:
            ctk.CTkLabel(
                container,
                text="Pas de données disponibles",
                font=("Inter", 12),
                text_color=self.colors['text_gray']
            ).pack(pady=50)
            return

        # Créer la figure
        fig = Figure(figsize=(5, 3), dpi=100, facecolor=self.colors['gray'])
        ax = fig.add_subplot(111)

        ax.plot(dates, energy_levels, marker='o', linewidth=2, markersize=6, color='#F59E0B')
        ax.axhline(y=7, color='#10B981', linestyle='--', linewidth=1, alpha=0.5, label='Objectif 7/10')

        ax.set_ylabel('Niveau', fontsize=10)
        ax.set_ylim(0, 10)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)

        # Format des dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        fig.autofmt_xdate(rotation=45)

        fig.tight_layout()

        # Intégrer dans tkinter
        canvas = FigureCanvasTkAgg(fig, container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=(0, 10))

    def _create_gourdes_chart(self, parent):
        """Crée le graphique des gourdes"""
        container = self._create_chart_container(parent, "💧 Hydratation (gourdes)")

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
        fig = Figure(figsize=(5, 3), dpi=100, facecolor=self.colors['gray'])
        ax = fig.add_subplot(111)

        ax.bar(dates, gourdes, color='#06B6D4', alpha=0.7, width=0.8)

        ax.set_ylabel('Nombre', fontsize=10)
        ax.set_ylim(0, max(gourdes) + 1)
        ax.grid(True, alpha=0.3, axis='y')

        # Format des dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        fig.autofmt_xdate(rotation=45)

        fig.tight_layout()

        # Intégrer dans tkinter
        canvas = FigureCanvasTkAgg(fig, container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=(0, 10))

    def _create_mood_chart(self, parent):
        """Crée le graphique d'humeur"""
        container = self._create_chart_container(parent, "😊 Évolution de l'humeur")

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
        fig = Figure(figsize=(5, 3), dpi=100, facecolor=self.colors['gray'])
        ax = fig.add_subplot(111)

        # Couleurs selon l'humeur
        colors = ['#FBBF24' if m >= 3 else '#F87171' for m in moods]
        ax.scatter(dates, moods, c=colors, s=100, alpha=0.7)

        ax.set_ylabel('Humeur', fontsize=10)
        ax.set_ylim(0.5, 4.5)
        ax.set_yticks([1, 2, 3, 4])
        ax.set_yticklabels(['🌧️', '🌥️', '🌤️', '🌞'])
        ax.grid(True, alpha=0.3)

        # Format des dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        fig.autofmt_xdate(rotation=45)

        fig.tight_layout()

        # Intégrer dans tkinter
        canvas = FigureCanvasTkAgg(fig, container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=(0, 10))

    def _create_habits_heatmap(self, parent):
        """Crée la heatmap des habitudes"""
        container = ctk.CTkFrame(
            parent,
            fg_color=self.colors['gray'],
            corner_radius=10
        )
        container.pack(fill='x', padx=5)

        # Titre
        ctk.CTkLabel(
            container,
            text="✅ Suivi des habitudes",
            font=("Degular Medium", 16, "bold"),
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
        table_frame.pack(fill='x', padx=15, pady=(0, 15))

        # Header avec les dates
        header_row = Container.transparent(table_frame)
        header_row.pack(fill='x', pady=2)

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
                    width=40,
                    font=("Inter", 9),
                    text_color=self.colors['text_gray']
                ).pack(side='left', padx=1)

        # Une ligne par habitude
        for habit in sorted(all_habits):
            habit_row = Container.transparent(table_frame)
            habit_row.pack(fill='x', pady=2)

            # Nom de l'habitude
            ctk.CTkLabel(
                habit_row,
                text=habit,
                width=150,
                font=("Inter", 11),
                text_color=self.colors['black'],
                anchor='w'
            ).pack(side='left', padx=2)

            # Statuts pour chaque jour
            for day_data in self.data:
                status = day_data.get('habits', {}).get(habit, '')

                # Couleur selon le statut
                if status == '🟩':
                    bg_color = '#10B981'
                elif status == '🟨':
                    bg_color = '#FBBF24'
                elif status == '🟧':
                    bg_color = '#F97316'
                else:
                    bg_color = self.colors['border']

                status_cell = ctk.CTkFrame(
                    habit_row,
                    width=40,
                    height=30,
                    fg_color=bg_color,
                    corner_radius=5
                )
                status_cell.pack(side='left', padx=1)
                status_cell.pack_propagate(False)
