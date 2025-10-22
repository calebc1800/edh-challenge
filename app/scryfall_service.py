"""
Scryfall API integration service.
Handles all interactions with the Scryfall API for card data.
"""

import requests
import time
from flask import current_app

class ScryfallService:
    """Service for interacting with Scryfall API."""

    def __init__(self):
        self.base_url = 'https://api.scryfall.com'
        self.last_request_time = 0
        self.rate_limit = 0.1  # 10 requests per second

    def _rate_limit_wait(self):
        """Ensure we don't exceed Scryfall's rate limits."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit:
            time.sleep(self.rate_limit - time_since_last)
        self.last_request_time = time.time()

    def _make_request(self, endpoint, params=None):
        """Make a request to Scryfall API with rate limiting."""
        self._rate_limit_wait()
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if current_app:
                current_app.logger.error(f"Scryfall API error: {str(e)}")
            return None

    def search_cards(self, query, page=1, unique='cards'):
        """
        Search for cards using Scryfall syntax.

        Args:
            query: Scryfall search query
            page: Page number for pagination
            unique: Uniqueness strategy ('cards', 'art', 'prints')

        Returns:
            Dictionary with search results
        """
        params = {
            'q': query,
            'page': page,
            'unique': unique
        }
        return self._make_request('/cards/search', params)

    def get_card_by_id(self, card_id):
        """Get a single card by Scryfall ID."""
        return self._make_request(f'/cards/{card_id}')

    def get_card_by_name(self, card_name, exact=True):
        """
        Get a card by name.

        Args:
            card_name: Name of the card
            exact: If True, search for exact match; if False, fuzzy search
        """
        if exact:
            return self._make_request('/cards/named', {'exact': card_name})
        else:
            return self._make_request('/cards/named', {'fuzzy': card_name})

    def get_all_printings(self, card_name):
        """
        Get all printings of a card by name.

        Args:
            card_name: Name of the card

        Returns:
            List of all printings with their details
        """
        # Search for all prints of this card
        result = self.search_cards(f'!"{card_name}"', unique='prints')

        if not result or 'data' not in result:
            return []

        printings = []
        for card_data in result['data']:
            printing = {
                'id': card_data.get('id'),
                'name': card_data.get('name'),
                'set_code': card_data.get('set'),
                'set_name': card_data.get('set_name'),
                'collector_number': card_data.get('collector_number'),
                'rarity': card_data.get('rarity'),
                'image_url': None,
                'image_url_small': None
            }

            # Get image URLs
            if 'image_uris' in card_data:
                printing['image_url'] = card_data['image_uris'].get('normal')
                printing['image_url_small'] = card_data['image_uris'].get('small')
            elif 'card_faces' in card_data and card_data['card_faces']:
                first_face = card_data['card_faces'][0]
                if 'image_uris' in first_face:
                    printing['image_url'] = first_face['image_uris'].get('normal')
                    printing['image_url_small'] = first_face['image_uris'].get('small')

            printings.append(printing)

        return printings

    def get_random_card(self, query=None):
        """Get a random card, optionally matching a query."""
        params = {'q': query} if query else None
        return self._make_request('/cards/random', params)

    def autocomplete(self, query):
        """Get card name autocomplete suggestions."""
        result = self._make_request('/cards/autocomplete', {'q': query})
        return result.get('data', []) if result else []

    def is_legal_commander(self, card_data):
        """
        Check if a card can be a commander.

        Args:
            card_data: Card data from Scryfall

        Returns:
            Boolean indicating if card can be a commander
        """
        if not card_data:
            return False

        # Check if legendary
        type_line = card_data.get('type_line', '')
        if 'Legendary' not in type_line:
            # Check for special commander text
            oracle_text = card_data.get('oracle_text', '')
            if 'can be your commander' not in oracle_text.lower():
                return False

        # Check if creature or planeswalker
        if 'Creature' in type_line or 'Planeswalker' in type_line:
            # Check commander legality
            legalities = card_data.get('legalities', {})
            if legalities.get('commander') in ['legal', 'restricted']:
                return True

        return False

    def parse_card_data(self, scryfall_data):
        """
        Parse Scryfall card data into our format.

        Args:
            scryfall_data: Raw card data from Scryfall

        Returns:
            Dictionary with parsed card data
        """
        if not scryfall_data:
            return None

        # Handle double-faced cards
        image_url = None
        image_url_small = None

        if 'image_uris' in scryfall_data:
            image_url = scryfall_data['image_uris'].get('normal')
            image_url_small = scryfall_data['image_uris'].get('small')
        elif 'card_faces' in scryfall_data and scryfall_data['card_faces']:
            first_face = scryfall_data['card_faces'][0]
            if 'image_uris' in first_face:
                image_url = first_face['image_uris'].get('normal')
                image_url_small = first_face['image_uris'].get('small')

        return {
            'id': scryfall_data.get('id'),
            'name': scryfall_data.get('name'),
            'mana_cost': scryfall_data.get('mana_cost', ''),
            'cmc': scryfall_data.get('cmc', 0),
            'type_line': scryfall_data.get('type_line', ''),
            'oracle_text': scryfall_data.get('oracle_text', ''),
            'colors': ','.join(scryfall_data.get('colors', [])),
            'color_identity': ','.join(scryfall_data.get('color_identity', [])),
            'power': scryfall_data.get('power'),
            'toughness': scryfall_data.get('toughness'),
            'loyalty': scryfall_data.get('loyalty'),
            'image_url': image_url,
            'image_url_small': image_url_small,
            'is_legal_commander': self.is_legal_commander(scryfall_data),
            'is_banned': scryfall_data.get('legalities', {}).get('commander') == 'banned',
            'set_code': scryfall_data.get('set'),
            'set_name': scryfall_data.get('set_name'),
            'rarity': scryfall_data.get('rarity'),
            'collector_number': scryfall_data.get('collector_number')
        }

# Create a singleton instance
scryfall_service = ScryfallService()
