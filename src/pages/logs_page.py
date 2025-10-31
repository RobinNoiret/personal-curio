"""
Page de gestion des logs
"""
import customtkinter as ctk
from typing import Dict, Optional
from ..utils import get_logger, LogLevel
from .base_page import BasePage
import tkinter as tk
from tkinter import filedialog
from datetime import datetime


class LogsPage(BasePage):
    """Page d'affichage et de gestion des logs"""

    def __init__(self, parent, colors: Dict, **kwargs):
        super().__init__(parent, colors)
        self.log_manager = get_logger()
        self.current_filter = None
        self.auto_scroll = True

        # Widgets
        self.log_display = None
        self.filter_buttons = {}
        self.auto_scroll_var = None

    def render(self):
        """Affiche la page"""
        # Container principal avec padding
        main_container = ctk.CTkFrame(self.parent, fg_color=self.colors['white'])
        main_container.pack(fill='both', expand=True, padx=40, pady=30)

        # En-tête
        self._create_header(main_container)

        # Barre de contrôle
        self._create_control_bar(main_container)

        # Zone d'affichage des logs
        self._create_log_display(main_container)

        # S'abonner aux nouveaux logs
        self.log_manager.add_observer(self._on_new_log)

        # Charger les logs existants
        self._refresh_logs()

    def _create_header(self, parent):
        """Crée l'en-tête de la page"""
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill='x', pady=(0, 20))

        # Titre
        title = ctk.CTkLabel(
            header,
            text="Logs",
            font=("Arial", 32, "bold"),
            text_color=self.colors['black']
        )
        title.pack(side='left')

        # Info du niveau actuel
        level_info = ctk.CTkLabel(
            header,
            text=f"Niveau actuel: {self.log_manager.current_level.value}",
            font=("Arial", 12),
            text_color=self.colors['text_gray']
        )
        level_info.pack(side='left', padx=20)

    def _create_control_bar(self, parent):
        """Crée la barre de contrôle avec filtres et actions"""
        control_frame = ctk.CTkFrame(parent, fg_color=self.colors['gray'], corner_radius=10)
        control_frame.pack(fill='x', pady=(0, 20), padx=0)

        # Section gauche - Filtres
        left_section = ctk.CTkFrame(control_frame, fg_color="transparent")
        left_section.pack(side='left', padx=20, pady=15)

        # Label
        filter_label = ctk.CTkLabel(
            left_section,
            text="Filtrer par niveau:",
            font=("Arial", 13, "bold"),
            text_color=self.colors['black']
        )
        filter_label.pack(side='left', padx=(0, 10))

        # Boutons de filtre
        levels = [
            ("Tous", None, self.colors['text_gray']),
            ("DEBUG", LogLevel.DEBUG, "#6B7280"),
            ("INFO", LogLevel.INFO, "#3B82F6"),
            ("WARNING", LogLevel.WARNING, "#F59E0B"),
            ("ERROR", LogLevel.ERROR, "#EF4444"),
            ("CRITICAL", LogLevel.CRITICAL, "#DC2626"),
        ]

        for text, level, color in levels:
            btn = ctk.CTkButton(
                left_section,
                text=text,
                font=("Arial", 11),
                fg_color=self.colors['white'] if level != self.current_filter else color,
                text_color=color if level != self.current_filter else self.colors['white'],
                hover_color=color,
                border_width=1,
                border_color=color,
                width=80,
                height=30,
                corner_radius=6,
                command=lambda l=level, c=color: self._set_filter(l, c)
            )
            btn.pack(side='left', padx=3)
            self.filter_buttons[(text, level)] = (btn, color)

        # Section droite - Actions
        right_section = ctk.CTkFrame(control_frame, fg_color="transparent")
        right_section.pack(side='right', padx=20, pady=15)

        # Auto-scroll checkbox
        self.auto_scroll_var = ctk.BooleanVar(value=True)
        auto_scroll_cb = ctk.CTkCheckBox(
            right_section,
            text="Auto-scroll",
            font=("Arial", 12),
            text_color=self.colors['black'],
            variable=self.auto_scroll_var,
            fg_color=self.colors['yellow'],
            hover_color="#FFD700",
            command=self._toggle_auto_scroll
        )
        auto_scroll_cb.pack(side='left', padx=5)

        # Bouton Rafraîchir
        refresh_btn = ctk.CTkButton(
            right_section,
            text="↻ Rafraîchir",
            font=("Arial", 12),
            fg_color=self.colors['yellow'],
            text_color=self.colors['black'],
            hover_color="#FFD700",
            width=100,
            height=30,
            corner_radius=6,
            command=self._refresh_logs
        )
        refresh_btn.pack(side='left', padx=5)

        # Bouton Exporter
        export_btn = ctk.CTkButton(
            right_section,
            text="⬇ Exporter",
            font=("Arial", 12),
            fg_color=self.colors['white'],
            text_color=self.colors['text_gray'],
            hover_color=self.colors['gray'],
            border_width=1,
            border_color=self.colors['border'],
            width=100,
            height=30,
            corner_radius=6,
            command=self._export_logs
        )
        export_btn.pack(side='left', padx=5)

        # Bouton Effacer
        clear_btn = ctk.CTkButton(
            right_section,
            text="✕ Effacer",
            font=("Arial", 12),
            fg_color=self.colors['white'],
            text_color="#EF4444",
            hover_color="#FEE2E2",
            border_width=1,
            border_color="#EF4444",
            width=100,
            height=30,
            corner_radius=6,
            command=self._clear_logs
        )
        clear_btn.pack(side='left', padx=5)

        # Section centre - Changement de niveau
        center_section = ctk.CTkFrame(control_frame, fg_color="transparent")
        center_section.pack(side='left', expand=True, padx=20, pady=15)

        level_label = ctk.CTkLabel(
            center_section,
            text="Niveau de log:",
            font=("Arial", 12, "bold"),
            text_color=self.colors['black']
        )
        level_label.pack(side='left', padx=(0, 10))

        # Dropdown pour changer le niveau
        self.level_var = ctk.StringVar(value=self.log_manager.current_level.value)
        level_dropdown = ctk.CTkOptionMenu(
            center_section,
            values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            variable=self.level_var,
            font=("Arial", 12),
            fg_color=self.colors['yellow'],
            button_color=self.colors['yellow'],
            button_hover_color="#FFD700",
            dropdown_fg_color=self.colors['white'],
            width=120,
            height=30,
            corner_radius=6,
            command=self._change_log_level
        )
        level_dropdown.pack(side='left', padx=5)

    def _create_log_display(self, parent):
        """Crée la zone d'affichage des logs"""
        # Container avec scrollbar
        display_container = ctk.CTkFrame(parent, fg_color=self.colors['white'])
        display_container.pack(fill='both', expand=True)

        # Textbox pour les logs
        self.log_display = ctk.CTkTextbox(
            display_container,
            font=("Consolas", 11),
            fg_color=self.colors['gray'],
            text_color=self.colors['black'],
            border_width=1,
            border_color=self.colors['border'],
            corner_radius=10,
            wrap='none'
        )
        self.log_display.pack(fill='both', expand=True)

        # Configurer les tags pour les couleurs
        self._configure_log_tags()

    def _configure_log_tags(self):
        """Configure les tags de couleur pour les différents niveaux"""
        # Accéder au widget Text interne
        text_widget = self.log_display._textbox

        text_widget.tag_config("DEBUG", foreground="#6B7280")
        text_widget.tag_config("INFO", foreground="#3B82F6")
        text_widget.tag_config("WARNING", foreground="#F59E0B")
        text_widget.tag_config("ERROR", foreground="#EF4444")
        text_widget.tag_config("CRITICAL", foreground="#DC2626", font=("Consolas", 11, "bold"))
        text_widget.tag_config("timestamp", foreground="#9CA3AF")
        text_widget.tag_config("source", foreground="#6366F1")

    def _set_filter(self, level: Optional[LogLevel], color: str):
        """Change le filtre actif"""
        self.current_filter = level

        # Mettre à jour l'apparence des boutons
        for (text, btn_level), (btn, btn_color) in self.filter_buttons.items():
            if btn_level == level:
                btn.configure(
                    fg_color=btn_color,
                    text_color=self.colors['white']
                )
            else:
                btn.configure(
                    fg_color=self.colors['white'],
                    text_color=btn_color
                )

        # Rafraîchir l'affichage
        self._refresh_logs()

    def _toggle_auto_scroll(self):
        """Active/désactive l'auto-scroll"""
        self.auto_scroll = self.auto_scroll_var.get()

    def _change_log_level(self, new_level_str: str):
        """Change le niveau de log global"""
        new_level = LogLevel[new_level_str]
        self.log_manager.set_level(new_level)
        self.log_manager.info(f"Niveau de log changé à {new_level.value}", "LogsPage")

    def _refresh_logs(self):
        """Rafraîchit l'affichage des logs"""
        self.log_display.configure(state='normal')
        self.log_display.delete('1.0', 'end')

        # Récupérer les logs filtrés
        logs = self.log_manager.get_logs(level=self.current_filter)

        # Afficher les logs
        for log in logs:
            self._insert_log(log)

        self.log_display.configure(state='disabled')

        # Auto-scroll
        if self.auto_scroll:
            self.log_display.see('end')

    def _insert_log(self, log):
        """Insère un log dans l'affichage avec formatage"""
        text_widget = self.log_display._textbox

        # Timestamp
        time_str = log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        text_widget.insert('end', f"[{time_str}] ", "timestamp")

        # Niveau
        text_widget.insert('end', f"[{log.level.value:8}] ", log.level.value)

        # Source
        text_widget.insert('end', f"{log.source}: ", "source")

        # Message
        text_widget.insert('end', f"{log.message}\n")

    def _on_new_log(self, log):
        """Callback appelé lors d'un nouveau log"""
        # Vérifier si le log correspond au filtre
        if self.current_filter and log.level != self.current_filter:
            return

        # Ajouter le log à l'affichage
        self.log_display.configure(state='normal')
        self._insert_log(log)
        self.log_display.configure(state='disabled')

        # Auto-scroll
        if self.auto_scroll:
            self.log_display.see('end')

    def _export_logs(self):
        """Exporte les logs vers un fichier"""
        # Dialogue de sauvegarde
        filename = filedialog.asksaveasfilename(
            title="Exporter les logs",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"logs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        if filename:
            try:
                self.log_manager.export_logs(filename, level=self.current_filter)
                self.log_manager.info(f"Logs exportés avec succès vers {filename}", "LogsPage")
            except Exception as e:
                self.log_manager.error(f"Erreur lors de l'export: {str(e)}", "LogsPage")

    def _clear_logs(self):
        """Efface tous les logs"""
        # Confirmation (simple pour l'instant)
        self.log_manager.clear_logs()
        self._refresh_logs()

    def clear(self):
        """Nettoie la page"""
        # Se désabonner des logs
        self.log_manager.remove_observer(self._on_new_log)
        super().clear()
