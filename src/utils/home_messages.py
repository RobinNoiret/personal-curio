"""
Messages et citations pour la page d'accueil
"""
import random
from typing import Tuple


# Phrases fixes possibles
FIXED_PHRASES = [
    ("prêt à gérer tes", "prosits comme un chef ?"),
    ("let's cook", "some prosits !"),
    ("transforme tes prosits", "en chefs-d'œuvre !"),
    ("tes prosits", "n'attendent que toi !"),
]


# Citations inspirantes
QUOTES = [
    ("la curiosité", "c'est le carburant de l'apprentissage."),
    ("un prosit par jour,", "éloigne l'ennui pour toujours !"),
    ("apprendre ensemble,", "c'est grandir ensemble."),
    ("chaque question", "est une nouvelle aventure."),
    ("la connaissance se partage,", "le savoir se multiplie."),
    ("pose des questions,", "trouve des solutions."),
    ("aujourd'hui est un bon jour", "pour apprendre quelque chose de nouveau."),
    ("le travail d'équipe", "fait rêver les projets."),
    ("un petit pas pour toi,", "un grand prosit pour l'équipe !"),
    ("la seule limite", "c'est celle qu'on se fixe."),
    ("transforme ta curiosité", "en compétence."),
    ("ensemble on va plus loin,", "ensemble on va mieux."),
]


def get_fixed_message() -> Tuple[str, str]:
    """Retourne une phrase fixe aléatoire"""
    return random.choice(FIXED_PHRASES)


def get_random_quote() -> Tuple[str, str]:
    """Retourne une citation aléatoire"""
    return random.choice(QUOTES)


def get_note_reminder(note_title: str) -> Tuple[str, str]:
    """
    Retourne un rappel basé sur une note

    Args:
        note_title: Titre de la note à rappeler

    Returns:
        Tuple (première ligne, deuxième ligne)
    """
    # Variantes de questions
    questions = [
        ("est-ce que tu sais", f"ce que c'est {note_title} ?"),
        ("tu te souviens", f"de la définition de {note_title} ?"),
        ("petit rappel :", f"c'est quoi {note_title} ?"),
        ("révision du jour :", f"{note_title} ?"),
    ]
    return random.choice(questions)
