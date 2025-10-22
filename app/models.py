"""
Database models for MTG Commander Deck Builder.
"""

from datetime import datetime
from app import db

class Deck(db.Model):
    """Represents a Commander deck."""
    __tablename__ = 'decks'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    color_identity = db.Column(db.String(10), nullable=False)
    commander_id = db.Column(db.String(50))  # Scryfall ID of commander
    commander_name = db.Column(db.String(200))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    cards = db.relationship('DeckCard', backref='deck', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Deck {self.name} ({self.color_identity})>'

    def to_dict(self, include_cards=False):
        """Convert deck to dictionary."""
        result = {
            'id': self.id,
            'name': self.name,
            'color_identity': self.color_identity,
            'commander_id': self.commander_id,
            'commander_name': self.commander_name,
            'description': self.description,
            'card_count': sum(dc.quantity for dc in self.cards),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_cards:
            result['cards'] = [dc.to_dict() for dc in self.cards]

        return result

class Card(db.Model):
    """Represents a Magic card from Scryfall."""
    __tablename__ = 'cards'

    id = db.Column(db.String(50), primary_key=True)  # Scryfall ID
    name = db.Column(db.String(200), nullable=False, index=True)
    mana_cost = db.Column(db.String(50))
    cmc = db.Column(db.Float)
    type_line = db.Column(db.String(200))
    oracle_text = db.Column(db.Text)
    colors = db.Column(db.String(20))
    color_identity = db.Column(db.String(20))
    power = db.Column(db.String(10))
    toughness = db.Column(db.String(10))
    loyalty = db.Column(db.String(10))
    image_url = db.Column(db.String(500))
    image_url_small = db.Column(db.String(500))  # Small version for hover
    is_legal_commander = db.Column(db.Boolean, default=False)
    is_banned = db.Column(db.Boolean, default=False)
    set_code = db.Column(db.String(10))
    set_name = db.Column(db.String(100))
    rarity = db.Column(db.String(20))
    collector_number = db.Column(db.String(20))

    # Relationships
    deck_cards = db.relationship('DeckCard', backref='card', lazy=True)

    def __repr__(self):
        return f'<Card {self.name}>'

    def to_dict(self):
        """Convert card to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'mana_cost': self.mana_cost,
            'cmc': self.cmc,
            'type_line': self.type_line,
            'oracle_text': self.oracle_text,
            'colors': self.colors,
            'color_identity': self.color_identity,
            'power': self.power,
            'toughness': self.toughness,
            'loyalty': self.loyalty,
            'image_url': self.image_url,
            'image_url_small': self.image_url_small,
            'is_legal_commander': self.is_legal_commander,
            'is_banned': self.is_banned,
            'set_code': self.set_code,
            'set_name': self.set_name,
            'rarity': self.rarity,
            'collector_number': self.collector_number
        }

class DeckCard(db.Model):
    """Many-to-many relationship between Decks and Cards."""
    __tablename__ = 'deck_cards'

    id = db.Column(db.Integer, primary_key=True)
    deck_id = db.Column(db.Integer, db.ForeignKey('decks.id'), nullable=False)
    card_id = db.Column(db.String(50), db.ForeignKey('cards.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    is_commander = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(50))
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    # New fields for print selection
    selected_printing_id = db.Column(db.String(50))  # Specific print Scryfall ID
    selected_image_url = db.Column(db.String(500))  # Image URL for selected print
    selected_set_code = db.Column(db.String(10))  # Set code for selected print
    selected_collector_number = db.Column(db.String(20))  # Collector number

    def __repr__(self):
        return f'<DeckCard deck_id={self.deck_id} card_id={self.card_id}>'

    def to_dict(self):
        """Convert deck card to dictionary."""
        return {
            'id': self.id,
            'deck_id': self.deck_id,
            'card_id': self.card_id,
            'quantity': self.quantity,
            'is_commander': self.is_commander,
            'category': self.category,
            'selected_printing_id': self.selected_printing_id,
            'selected_image_url': self.selected_image_url,
            'selected_set_code': self.selected_set_code,
            'selected_collector_number': self.selected_collector_number,
            'card': self.card.to_dict() if self.card else None
        }
