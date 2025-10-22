"""
Deck validation logic for Commander format rules.
"""

from flask import current_app
from app.models import Deck, Card, DeckCard

class DeckValidator:
    """Validates Commander deck against format rules."""

    def __init__(self, deck):
        self.deck = deck
        self.errors = []
        self.warnings = []

    def validate(self):
        """
        Validate the deck against all Commander rules.

        Returns:
            Dictionary with validation results
        """
        self.errors = []
        self.warnings = []

        self._validate_size()
        self._validate_commander()
        self._validate_singleton()
        self._validate_color_identity()
        self._validate_banned_cards()

        return {
            'valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings
        }

    def _validate_size(self):
        """Validate deck has exactly 100 cards."""
        total = sum(dc.quantity for dc in self.deck.cards)
        if total != 100:
            self.errors.append(f"Deck must be exactly 100 cards (current: {total})")
        elif total < 100:
            self.warnings.append(f"Deck needs {100 - total} more cards")

    def _validate_commander(self):
        """Validate commander requirements."""
        commanders = [dc for dc in self.deck.cards if dc.is_commander]

        if len(commanders) == 0:
            self.errors.append("Deck must have a commander")
        elif len(commanders) > 1:
            self.errors.append("Deck can only have one commander (partners not yet supported)")
        else:
            commander = commanders[0]
            if commander.card:
                if not commander.card.is_legal_commander:
                    self.errors.append(
                        f"{commander.card.name} is not a legal commander. "
                        "Must be a legendary creature or planeswalker."
                    )

    def _validate_singleton(self):
        """Validate singleton format (no duplicates except basic lands)."""
        basic_lands = current_app.config['BASIC_LANDS']
        card_counts = {}

        for dc in self.deck.cards:
            if dc.card and dc.card.name not in basic_lands:
                card_counts[dc.card.name] = card_counts.get(dc.card.name, 0) + dc.quantity

        for name, count in card_counts.items():
            if count > 1:
                self.errors.append(
                    f"{name} appears {count} times (singleton format allows only 1 copy)"
                )

    def _validate_color_identity(self):
        """Validate cards match commander's color identity."""
        if not self.deck.color_identity:
            return

        deck_colors = set(self.deck.color_identity) if self.deck.color_identity != 'C' else set()

        for dc in self.deck.cards:
            if dc.card and dc.card.color_identity:
                card_colors = set(dc.card.color_identity.split(',')) if dc.card.color_identity else set()
                card_colors.discard('')  # Remove empty strings

                if not card_colors.issubset(deck_colors):
                    self.errors.append(
                        f"{dc.card.name} ({dc.card.color_identity}) is outside "
                        f"commander's color identity ({self.deck.color_identity})"
                    )

    def _validate_banned_cards(self):
        """Check for banned cards in Commander format."""
        banned = current_app.config['COMMANDER_BANNED']

        for dc in self.deck.cards:
            if dc.card and dc.card.name in banned:
                self.errors.append(f"{dc.card.name} is banned in Commander format")

def validate_deck(deck):
    """
    Convenience function to validate a deck.

    Args:
        deck: Deck model instance

    Returns:
        Dictionary with validation results
    """
    validator = DeckValidator(deck)
    return validator.validate()
