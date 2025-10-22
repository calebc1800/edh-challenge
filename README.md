# MTG Commander Deck Builder - 32 Deck Challenge

A web-based application for building Magic: The Gathering Commander decks following the 32 deck challenge rules.

## New Features in v1.1

✨ **Print Selection** - Choose specific card printings/art versions for each card in your deck
✨ **Quantity Control** - Set card quantities when adding or edit them later
✨ **Card Image Hover** - Hover over card names to see card images
✨ **Image Thumbnails** - View card images directly in the decklist
✨ **Enhanced Card Options** - Edit quantity and print selection for cards already in your deck
✨ **Commander Display Fix** - Commanders now display correctly on the My Decks page

## Challenge Rules

- Create one deck for each of the 32 color combinations (including colorless)
- No card (except basic lands) can be used in more than one deck
- All decks must follow Commander format rules:
  - Exactly 100 cards (including commander)
  - Legal commander (legendary creature or valid planeswalker)
  - Singleton format (no duplicates except basic lands)
  - Color identity restrictions
  - No banned cards

## Features

- **Card Search**: Search the complete MTG card database using Scryfall API with advanced query syntax
- **Deck Management**: Create, edit, and manage up to 32 Commander decks
- **Print Selection**: Choose from all available printings of each card
- **Quantity Control**: Add multiple copies of basic lands and adjust quantities
- **Visual Deck Builder**: See card images with hover previews
- **Deck Validation**: Automatic validation of Commander format rules
- **Challenge Tracking**: Track progress across all 32 color combinations
- **Card Usage Tracking**: Ensures no card is used in multiple decks (except basic lands)
- **Import/Export**: Import and export decklists in standard formats
- **Deck Analytics**: View color distribution, mana curve, card type breakdowns
- **Quick Deck Switching**: Easily navigate between your 32 decks

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Extract the ZIP file to a directory

2. Open terminal/command prompt in that directory

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python init_db.py
```

5. **(If upgrading from v1.0)** Run migration script:
```bash
python migrate_db.py
```

6. Run the application:
```bash
python run.py
```

7. Open your browser and navigate to:
```
http://localhost:5000
```

## Using the Application

### Building Your First Deck

1. **Select a Color Combination**
   - Click on any color combination in the grid
   - Enter a name for your deck
   - Click "Create"

2. **Add Cards to Your Deck**
   - Use the search bar to find cards
   - Click on a card to add it
   - **NEW**: Select which printing/art version you want
   - **NEW**: Choose the quantity (for basic lands)
   - Confirm your selection

3. **Set Your Commander**
   - Search for a legendary creature
   - When adding, you'll be prompted to make it your commander
   - The app will automatically suggest making legendary creatures commanders

4. **Edit Card Options**
   - Click on any card in your decklist
   - Change the quantity
   - Select a different printing/art version
   - Save your changes

5. **View Card Details**
   - Hover over card names to see the card image
   - Click on card images for full details
   - View oracle text, power/toughness, and more

### Validation

- The app validates your deck in real-time
- Shows errors if:
  - Deck doesn't have exactly 100 cards
  - Missing commander
  - Duplicate cards (singleton violation)
  - Cards outside color identity
  - Banned cards included

### Challenge Progress

- Return to the home page to see your progress
- Green boxes indicate completed decks
- Click on completed decks to edit them
- The app tracks duplicate cards across all decks
- Challenge is complete when all 32 combinations have decks

## API Endpoints

### Cards
- `GET /api/cards/search` - Search for cards
- `GET /api/cards/<card_id>` - Get card details
- `GET /api/cards/<card_name>/printings` - Get all printings of a card

### Decks
- `GET /api/decks` - List all decks
- `GET /api/decks/<deck_id>` - Get deck details
- `POST /api/decks` - Create new deck
- `PUT /api/decks/<deck_id>` - Update deck
- `DELETE /api/decks/<deck_id>` - Delete deck

### Deck Cards
- `POST /api/decks/<deck_id>/cards` - Add card to deck
- `PUT /api/decks/<deck_id>/cards/<card_id>` - Update card options
- `DELETE /api/decks/<deck_id>/cards/<card_id>` - Remove card from deck

### Challenge
- `GET /api/challenge/status` - Get 32 deck challenge progress
- `GET /api/challenge/validate` - Validate challenge rules

## Running Tests

Run the full test suite:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

## Technologies Used

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Card Data**: Scryfall API
- **Testing**: pytest, pytest-cov

## Troubleshooting

### Database Issues
```bash
# Reset the database
rm mtg_commander.db
python init_db.py
```

### Upgrading from v1.0
```bash
# Run the migration script
python migrate_db.py
```

### API Rate Limiting
If you encounter Scryfall API rate limits, wait a few seconds between searches.

### Card Images Not Loading
Ensure you have an active internet connection. Images are loaded from Scryfall's CDN.

## Changelog

### v1.1 (Latest)
- ✨ Added print/art version selection for each card
- ✨ Added quantity control when adding cards
- ✨ Added ability to edit card quantity and printing after adding
- ✨ Added card image hover previews in decklist
- ✨ Added card image thumbnails in decklist
- ✨ Fixed commander not displaying on My Decks page
- ✨ Added modal dialogs for better UX
- 🎨 Enhanced UI with better visual feedback
- 📊 Improved deck statistics display

### v1.0
- Initial release with core features

## License

This project is for personal use. Magic: The Gathering is © Wizards of the Coast. Card data and images provided by Scryfall.

## Credits

- Card data provided by [Scryfall](https://scryfall.com/)
- Built using Perplexity Labs. See the AGENTS.md file to see the original prompt
- Built for the MTG Commander community

---

**Version**: 1.1.0  
**Last Updated**: October 2025
