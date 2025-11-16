"""
Système de logging pour l'application Prosit Manager
"""
import logging
import os
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum
import json


class LogLevel(Enum):
    """Niveaux de log disponibles"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogEntry:
    """Représente une entrée de log"""

    def __init__(self, level: LogLevel, message: str, source: str = None):
        self.timestamp = datetime.now()
        self.level = level
        self.message = message
        self.source = source or "Application"

    def to_dict(self) -> Dict:
        """Convertit l'entrée en dictionnaire"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'level': self.level.value,
            'message': self.message,
            'source': self.source
        }

    def __str__(self) -> str:
        """Représentation textuelle"""
        time_str = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return f"[{time_str}] [{self.level.value}] {self.source}: {self.message}"


class LogManager:
    """Gestionnaire central des logs"""

    _instance = None
    _observers = []

    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super(LogManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialise le gestionnaire de logs"""
        if self._initialized:
            return

        self._initialized = True
        self.logs: List[LogEntry] = []
        self.max_logs = 1000  # Limite d'historique en mémoire
        self.current_level = LogLevel.INFO
        self.log_file_path = None
        self.file_logging_enabled = True

        # Créer le dossier de logs
        self._setup_log_directory()

        # Configurer le logging Python standard
        self._setup_python_logging()

    def _setup_log_directory(self):
        """Crée le dossier de logs dans le dossier utilisateur approprié"""
        import sys

        # Déterminer le dossier de logs approprié selon l'OS
        if sys.platform == 'win32':
            # Windows: utiliser APPDATA
            base = os.environ.get('APPDATA', os.path.expanduser('~'))
            log_dir = os.path.join(base, 'Curio', 'logs')
        elif sys.platform == 'darwin':
            # macOS: utiliser ~/Library/Logs
            log_dir = os.path.join(os.path.expanduser('~'), 'Library', 'Logs', 'Curio')
        else:
            # Linux et autres: utiliser ~/.local/share/Curio/logs
            log_dir = os.path.join(os.path.expanduser('~'), '.local', 'share', 'Curio', 'logs')

        os.makedirs(log_dir, exist_ok=True)

        # Fichier de log avec date
        log_filename = f"curio_{datetime.now().strftime('%Y%m%d')}.log"
        self.log_file_path = os.path.join(log_dir, log_filename)

    def _setup_python_logging(self):
        """Configure le système de logging Python"""
        # Configuration du logger root
        logger = logging.getLogger('PrositManager')
        logger.setLevel(logging.DEBUG)

        # Handler pour fichier
        if self.file_logging_enabled and self.log_file_path:
            file_handler = logging.FileHandler(self.log_file_path, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

        # Handler pour console (optionnel)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)  # Seulement warnings et erreurs en console
        console_formatter = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        self.logger = logger

    def set_level(self, level: LogLevel):
        """Change le niveau de log actuel"""
        self.current_level = level

        # Mapper vers les niveaux Python logging
        level_map = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL
        }
        self.logger.setLevel(level_map.get(level, logging.INFO))

    def add_observer(self, callback):
        """Ajoute un observateur qui sera notifié des nouveaux logs"""
        if callback not in self._observers:
            self._observers.append(callback)

    def remove_observer(self, callback):
        """Retire un observateur"""
        if callback in self._observers:
            self._observers.remove(callback)

    def _notify_observers(self, log_entry: LogEntry):
        """Notifie tous les observateurs d'un nouveau log"""
        for observer in self._observers:
            try:
                observer(log_entry)
            except Exception as e:
                print(f"Erreur lors de la notification d'un observateur: {e}")

    def _should_log(self, level: LogLevel) -> bool:
        """Vérifie si le message doit être loggé selon le niveau actuel"""
        level_priority = {
            LogLevel.DEBUG: 0,
            LogLevel.INFO: 1,
            LogLevel.WARNING: 2,
            LogLevel.ERROR: 3,
            LogLevel.CRITICAL: 4
        }
        return level_priority[level] >= level_priority[self.current_level]

    def _add_log(self, level: LogLevel, message: str, source: str = None):
        """Ajoute un log à l'historique"""
        if not self._should_log(level):
            return

        entry = LogEntry(level, message, source)
        self.logs.append(entry)

        # Limiter la taille de l'historique
        if len(self.logs) > self.max_logs:
            self.logs = self.logs[-self.max_logs:]

        # Notifier les observateurs
        self._notify_observers(entry)

        # Logger avec le système Python
        log_method = {
            LogLevel.DEBUG: self.logger.debug,
            LogLevel.INFO: self.logger.info,
            LogLevel.WARNING: self.logger.warning,
            LogLevel.ERROR: self.logger.error,
            LogLevel.CRITICAL: self.logger.critical
        }
        log_func = log_method.get(level, self.logger.info)
        log_func(f"{source or 'Application'}: {message}")

    def debug(self, message: str, source: str = None):
        """Log un message de debug"""
        self._add_log(LogLevel.DEBUG, message, source)

    def info(self, message: str, source: str = None):
        """Log un message d'information"""
        self._add_log(LogLevel.INFO, message, source)

    def warning(self, message: str, source: str = None):
        """Log un warning"""
        self._add_log(LogLevel.WARNING, message, source)

    def error(self, message: str, source: str = None):
        """Log une erreur"""
        self._add_log(LogLevel.ERROR, message, source)

    def critical(self, message: str, source: str = None):
        """Log une erreur critique"""
        self._add_log(LogLevel.CRITICAL, message, source)

    def get_logs(self, level: Optional[LogLevel] = None, limit: Optional[int] = None) -> List[LogEntry]:
        """
        Récupère les logs filtrés

        Args:
            level: Filtre par niveau (None = tous)
            limit: Nombre maximum de logs à retourner (None = tous)
        """
        filtered_logs = self.logs

        if level:
            filtered_logs = [log for log in filtered_logs if log.level == level]

        if limit:
            filtered_logs = filtered_logs[-limit:]

        return filtered_logs

    def clear_logs(self):
        """Efface tous les logs en mémoire"""
        self.logs.clear()
        self.info("Logs effacés", "LogManager")

    def export_logs(self, filepath: str, level: Optional[LogLevel] = None):
        """
        Exporte les logs vers un fichier JSON

        Args:
            filepath: Chemin du fichier de destination
            level: Filtre par niveau (None = tous)
        """
        logs_to_export = self.get_logs(level=level)

        data = {
            'export_date': datetime.now().isoformat(),
            'log_level_filter': level.value if level else 'ALL',
            'total_logs': len(logs_to_export),
            'logs': [log.to_dict() for log in logs_to_export]
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        self.info(f"Logs exportés vers {filepath}", "LogManager")


# Instance globale
_log_manager = None


def get_logger() -> LogManager:
    """Récupère l'instance du gestionnaire de logs"""
    global _log_manager
    if _log_manager is None:
        _log_manager = LogManager()
    return _log_manager
