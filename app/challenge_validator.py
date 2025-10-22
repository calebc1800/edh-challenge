"""
32 Deck Challenge validation logic.
"""

from flask import current_app
from app.models import Deck, DeckCard
from app import db

class ChallengeValidator:
    """Validates the 32 deck challenge rules."""

    def validate_challenge(self):
        """
        Validate all 32 deck challenge rules.

        Returns:
            Dictionary with challenge status and validation results
        """
        decks = Deck.query.all()

        # Check 32 deck requirement
        color_combos = current_app.config['COLOR_COMBINATIONS']
        deck_colors = {d.color_identity for d in decks}
        missing = set(color_combos.keys()) - deck_colors

        # Check card uniqueness across decks
        card_usage = {}
        basic_lands = current_app.config['BASIC_LANDS']

        for deck in decks:
            for dc in deck.cards:
                if dc.card and dc.card.name not in basic_lands:
                    if dc.card.name not in card_usage:
                        card_usage[dc.card.name] = []
                    card_usage[dc.card.name].append({
                        'deck_id': deck.id,
                        'deck_name': deck.name,
                        'color_identity': deck.color_identity
                    })

        # Find cards used in multiple decks
        duplicates = {
            name: decks_list for name, decks_list in card_usage.items()
            if len(decks_list) > 1
        }

        return {
            'complete': len(missing) == 0,
            'total_decks': len(decks),
            'progress': f"{len(decks)}/32",
            'missing_colors': [
                {'code': code, 'name': color_combos[code]}
                for code in sorted(missing)
            ],
            'duplicate_cards': duplicates,
            'duplicate_count': len(duplicates),
            'valid': len(missing) == 0 and len(duplicates) == 0
        }

    def get_color_progress(self):
        """
        Get progress for each color combination.

        Returns:
            Dictionary mapping color codes to deck info
        """
        decks = Deck.query.all()
        color_combos = current_app.config['COLOR_COMBINATIONS']

        progress = {}
        for code, name in color_combos.items():
            deck = next((d for d in decks if d.color_identity == code), None)
            progress[code] = {
                'name': name,
                'completed': deck is not None,
                'deck_id': deck.id if deck else None,
                'deck_name': deck.name if deck else None
            }

        return progress

def validate_challenge():
    """
    Convenience function to validate the challenge.

    Returns:
        Dictionary with challenge validation results
    """
    validator = ChallengeValidator()
    return validator.validate_challenge()

def get_challenge_progress():
    """
    Get challenge progress details.

    Returns:
        Dictionary with progress information
    """
    validator = ChallengeValidator()
    return validator.get_color_progress()
