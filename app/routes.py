"""
API routes and view endpoints for MTG Commander Deck Builder.
"""

from flask import Blueprint, request, jsonify, render_template
from app import db
from app.models import Deck, Card, DeckCard
from app.scryfall_service import scryfall_service
from app.deck_validator import validate_deck
from app.challenge_validator import validate_challenge, get_challenge_progress

# Create blueprints
main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)

# ============================================================================
# MAIN ROUTES (HTML pages)
# ============================================================================

@main_bp.route('/')
def index():
    """Home page with 32 deck challenge overview."""
    return render_template('index.html')

@main_bp.route('/deck-builder/<int:deck_id>')
def deck_builder(deck_id):
    """Deck builder interface for a specific deck."""
    return render_template('deck-builder.html', deck_id=deck_id)

@main_bp.route('/deck-list')
def deck_list():
    """List all decks."""
    return render_template('deck-list.html')

# ============================================================================
# API ROUTES - Cards
# ============================================================================

@api_bp.route('/cards/search', methods=['GET'])
def search_cards():
    """Search for cards using Scryfall API."""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)

    if not query:
        return jsonify({'error': 'Query parameter required'}), 400

    # Search Scryfall
    results = scryfall_service.search_cards(query, page)

    if not results:
        return jsonify({'error': 'Search failed'}), 500

    if 'data' not in results:
        return jsonify({'error': 'No results found'}), 404

    # Store cards in database
    cards = []
    for card_data in results['data']:
        parsed = scryfall_service.parse_card_data(card_data)
        if parsed:
            # Check if card exists, update or create
            card = Card.query.get(parsed['id'])
            if not card:
                card = Card(**parsed)
                db.session.add(card)
            else:
                for key, value in parsed.items():
                    setattr(card, key, value)
            cards.append(card.to_dict())

    db.session.commit()

    return jsonify({
        'cards': cards,
        'has_more': results.get('has_more', False),
        'total_cards': results.get('total_cards', 0)
    })

@api_bp.route('/cards/<card_id>', methods=['GET'])
def get_card(card_id):
    """Get details for a specific card."""
    card = Card.query.get(card_id)

    if not card:
        # Try fetching from Scryfall
        card_data = scryfall_service.get_card_by_id(card_id)
        if card_data:
            parsed = scryfall_service.parse_card_data(card_data)
            card = Card(**parsed)
            db.session.add(card)
            db.session.commit()
        else:
            return jsonify({'error': 'Card not found'}), 404

    return jsonify(card.to_dict())

@api_bp.route('/cards/<card_name>/printings', methods=['GET'])
def get_card_printings(card_name):
    """Get all printings of a card."""
    printings = scryfall_service.get_all_printings(card_name)

    if not printings:
        return jsonify({'error': 'No printings found'}), 404

    return jsonify({'printings': printings})

@api_bp.route('/cards/autocomplete', methods=['GET'])
def autocomplete_cards():
    """Get autocomplete suggestions for card names."""
    query = request.args.get('q', '')

    if not query or len(query) < 2:
        return jsonify({'suggestions': []})

    suggestions = scryfall_service.autocomplete(query)
    return jsonify({'suggestions': suggestions})

# ============================================================================
# API ROUTES - Decks
# ============================================================================

@api_bp.route('/decks', methods=['GET'])
def get_decks():
    """Get all decks."""
    decks = Deck.query.all()
    return jsonify({'decks': [d.to_dict(include_cards=False) for d in decks]})

@api_bp.route('/decks/<int:deck_id>', methods=['GET'])
def get_deck(deck_id):
    """Get details for a specific deck."""
    deck = Deck.query.get_or_404(deck_id)

    deck_dict = deck.to_dict(include_cards=True)

    # Add validation results
    validation = validate_deck(deck)
    deck_dict['validation'] = validation

    return jsonify(deck_dict)

@api_bp.route('/decks', methods=['POST'])
def create_deck():
    """Create a new deck."""
    data = request.get_json()

    if not data or 'name' not in data or 'color_identity' not in data:
        return jsonify({'error': 'Name and color_identity required'}), 400

    # Check if color combination already exists
    existing = Deck.query.filter_by(color_identity=data['color_identity']).first()
    if existing:
        return jsonify({'error': f'Deck for {data["color_identity"]} already exists'}), 400

    deck = Deck(
        name=data['name'],
        color_identity=data['color_identity'],
        commander_id=data.get('commander_id'),
        commander_name=data.get('commander_name'),
        description=data.get('description', '')
    )

    db.session.add(deck)
    db.session.commit()

    return jsonify(deck.to_dict()), 201

@api_bp.route('/decks/<int:deck_id>', methods=['PUT'])
def update_deck(deck_id):
    """Update a deck."""
    deck = Deck.query.get_or_404(deck_id)
    data = request.get_json()

    if 'name' in data:
        deck.name = data['name']
    if 'description' in data:
        deck.description = data['description']
    if 'commander_id' in data:
        deck.commander_id = data['commander_id']
    if 'commander_name' in data:
        deck.commander_name = data['commander_name']

    db.session.commit()
    return jsonify(deck.to_dict())

@api_bp.route('/decks/<int:deck_id>', methods=['DELETE'])
def delete_deck(deck_id):
    """Delete a deck."""
    deck = Deck.query.get_or_404(deck_id)
    db.session.delete(deck)
    db.session.commit()
    return jsonify({'message': 'Deck deleted'}), 200

# ============================================================================
# API ROUTES - Deck Cards
# ============================================================================

@api_bp.route('/decks/<int:deck_id>/cards', methods=['POST'])
def add_card_to_deck(deck_id):
    """Add a card to a deck with optional print selection."""
    deck = Deck.query.get_or_404(deck_id)
    data = request.get_json()

    if not data or 'card_id' not in data:
        return jsonify({'error': 'card_id required'}), 400

    card = Card.query.get(data['card_id'])
    if not card:
        return jsonify({'error': 'Card not found'}), 404

    # Check if card already in deck
    existing = DeckCard.query.filter_by(
        deck_id=deck_id,
        card_id=data['card_id']
    ).first()

    if existing:
        return jsonify({'error': 'Card already in deck'}), 400

    # Determine if this should be the commander
    is_commander = data.get('is_commander', False)
    if not is_commander and card.is_legal_commander:
        # Check if deck doesn't have a commander yet
        existing_commander = DeckCard.query.filter_by(
            deck_id=deck_id,
            is_commander=True
        ).first()
        if not existing_commander:
            is_commander = True

    deck_card = DeckCard(
        deck_id=deck_id,
        card_id=data['card_id'],
        quantity=data.get('quantity', 1),
        is_commander=is_commander,
        category=data.get('category'),
        selected_printing_id=data.get('selected_printing_id', data['card_id']),
        selected_image_url=data.get('selected_image_url', card.image_url),
        selected_set_code=data.get('selected_set_code', card.set_code),
        selected_collector_number=data.get('selected_collector_number', card.collector_number)
    )

    # Update deck commander info if this is the commander
    if is_commander:
        deck.commander_id = data['card_id']
        deck.commander_name = card.name

    db.session.add(deck_card)
    db.session.commit()

    return jsonify(deck_card.to_dict()), 201

@api_bp.route('/decks/<int:deck_id>/cards/<card_id>', methods=['PUT'])
def update_deck_card(deck_id, card_id):
    """Update card properties in a deck (quantity, print selection)."""
    deck_card = DeckCard.query.filter_by(
        deck_id=deck_id,
        card_id=card_id
    ).first_or_404()

    data = request.get_json()

    if 'quantity' in data:
        deck_card.quantity = data['quantity']
    if 'category' in data:
        deck_card.category = data['category']
    if 'selected_printing_id' in data:
        deck_card.selected_printing_id = data['selected_printing_id']
    if 'selected_image_url' in data:
        deck_card.selected_image_url = data['selected_image_url']
    if 'selected_set_code' in data:
        deck_card.selected_set_code = data['selected_set_code']
    if 'selected_collector_number' in data:
        deck_card.selected_collector_number = data['selected_collector_number']

    db.session.commit()

    return jsonify(deck_card.to_dict())

@api_bp.route('/decks/<int:deck_id>/cards/<card_id>', methods=['DELETE'])
def remove_card_from_deck(deck_id, card_id):
    """Remove a card from a deck."""
    deck_card = DeckCard.query.filter_by(
        deck_id=deck_id,
        card_id=card_id
    ).first_or_404()

    # If removing commander, clear deck commander info
    if deck_card.is_commander:
        deck = Deck.query.get(deck_id)
        if deck:
            deck.commander_id = None
            deck.commander_name = None

    db.session.delete(deck_card)
    db.session.commit()

    return jsonify({'message': 'Card removed from deck'}), 200

@api_bp.route('/decks/<int:deck_id>/validate', methods=['GET'])
def validate_deck_endpoint(deck_id):
    """Validate a deck against Commander rules."""
    deck = Deck.query.get_or_404(deck_id)
    validation = validate_deck(deck)
    return jsonify(validation)

# ============================================================================
# API ROUTES - Challenge
# ============================================================================

@api_bp.route('/challenge/status', methods=['GET'])
def challenge_status():
    """Get 32 deck challenge status."""
    status = validate_challenge()
    return jsonify(status)

@api_bp.route('/challenge/progress', methods=['GET'])
def challenge_progress():
    """Get detailed progress for each color combination."""
    progress = get_challenge_progress()
    return jsonify(progress)

# ============================================================================
# API ROUTES - Import/Export
# ============================================================================

@api_bp.route('/decks/<int:deck_id>/import', methods=['POST'])
def import_decklist(deck_id):
    """Import a decklist from text format."""
    deck = Deck.query.get_or_404(deck_id)
    data = request.get_json()

    if not data or 'decklist' not in data:
        return jsonify({'error': 'decklist required'}), 400

    lines = data['decklist'].strip().split('\n')
    added = []
    errors = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('//'):
            continue

        # Parse line (format: "1 Card Name" or "Card Name")
        parts = line.split(' ', 1)
        if len(parts) == 2 and parts[0].isdigit():
            quantity = int(parts[0])
            card_name = parts[1]
        else:
            quantity = 1
            card_name = line

        # Search for card
        card_data = scryfall_service.get_card_by_name(card_name, exact=True)
        if card_data:
            parsed = scryfall_service.parse_card_data(card_data)
            card = Card.query.get(parsed['id'])
            if not card:
                card = Card(**parsed)
                db.session.add(card)
                db.session.flush()

            # Add to deck
            deck_card = DeckCard(
                deck_id=deck_id,
                card_id=card.id,
                quantity=quantity,
                selected_printing_id=card.id,
                selected_image_url=card.image_url,
                selected_set_code=card.set_code,
                selected_collector_number=card.collector_number
            )
            db.session.add(deck_card)
            added.append(card_name)
        else:
            errors.append(f"Card not found: {card_name}")

    db.session.commit()

    return jsonify({
        'added': len(added),
        'errors': errors,
        'cards': added
    })

@api_bp.route('/decks/<int:deck_id>/export', methods=['GET'])
def export_decklist(deck_id):
    """Export a deck as text."""
    deck = Deck.query.get_or_404(deck_id)
    format_type = request.args.get('format', 'text')

    if format_type == 'json':
        deck_dict = deck.to_dict(include_cards=True)
        return jsonify(deck_dict)

    # Text format
    lines = [f"# {deck.name}", f"# Commander: {deck.commander_name or 'None'}", ""]

    # Group by category or type
    commander = [dc for dc in deck.cards if dc.is_commander]
    other = [dc for dc in deck.cards if not dc.is_commander]

    if commander:
        lines.append("Commander:")
        for dc in commander:
            lines.append(f"1 {dc.card.name}")
        lines.append("")

    lines.append("Deck:")
    for dc in sorted(other, key=lambda x: x.card.name):
        lines.append(f"{dc.quantity} {dc.card.name}")

    return '\n'.join(lines), 200, {'Content-Type': 'text/plain'}
