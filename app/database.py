"""
Database utilities and helper functions.
"""

from app import db
from app.models import Deck, Card, DeckCard

def reset_database():
    """Drop all tables and recreate them. WARNING: Destroys all data!"""
    db.drop_all()
    db.create_all()

def get_deck_stats(deck_id):
    """
    Get statistics for a deck.

    Args:
        deck_id: ID of the deck

    Returns:
        Dictionary with deck statistics
    """
    deck = Deck.query.get(deck_id)
    if not deck:
        return None

    stats = {
        'total_cards': 0,
        'creatures': 0,
        'instants': 0,
        'sorceries': 0,
        'artifacts': 0,
        'enchantments': 0,
        'planeswalkers': 0,
        'lands': 0,
        'avg_cmc': 0,
        'color_distribution': {'W': 0, 'U': 0, 'B': 0, 'R': 0, 'G': 0, 'C': 0}
    }

    total_cmc = 0
    non_land_count = 0

    for dc in deck.cards:
        if not dc.card:
            continue

        stats['total_cards'] += dc.quantity
        type_line = dc.card.type_line.lower()

        # Count by type
        if 'creature' in type_line:
            stats['creatures'] += dc.quantity
        if 'instant' in type_line:
            stats['instants'] += dc.quantity
        if 'sorcery' in type_line:
            stats['sorceries'] += dc.quantity
        if 'artifact' in type_line:
            stats['artifacts'] += dc.quantity
        if 'enchantment' in type_line:
            stats['enchantments'] += dc.quantity
        if 'planeswalker' in type_line:
            stats['planeswalkers'] += dc.quantity
        if 'land' in type_line:
            stats['lands'] += dc.quantity

        # Calculate average CMC (exclude lands)
        if 'land' not in type_line and dc.card.cmc is not None:
            total_cmc += dc.card.cmc * dc.quantity
            non_land_count += dc.quantity

        # Color distribution
        if dc.card.colors:
            for color in dc.card.colors.split(','):
                if color in stats['color_distribution']:
                    stats['color_distribution'][color] += dc.quantity
        else:
            stats['color_distribution']['C'] += dc.quantity

    # Calculate average CMC
    if non_land_count > 0:
        stats['avg_cmc'] = round(total_cmc / non_land_count, 2)

    return stats
