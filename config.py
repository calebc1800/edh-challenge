import os
from datetime import timedelta

class Config:
    """Base configuration."""
    # Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database config
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///mtg_commander.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Scryfall API config
    SCRYFALL_API_BASE = 'https://api.scryfall.com'
    SCRYFALL_RATE_LIMIT = 0.1  # seconds between requests (10 requests per second)

    # Application config
    CARDS_PER_PAGE = 50
    MAX_DECKS = 32
    CARDS_PER_DECK = 100

    # Commander format banned list (as of October 2025)
    COMMANDER_BANNED = [
        'Ancestral Recall', 'Balance', 'Biorhythm', 'Black Lotus',
        'Braids, Cabal Minion', 'Chaos Orb', 'Coalition Victory',
        'Channel', 'Dockside Extortionist', 'Emrakul, the Aeons Torn',
        'Erayo, Soratami Ascendant', 'Falling Star', 'Fastbond',
        'Flash', 'Gifts Ungiven', 'Golos, Tireless Pilgrim',
        'Griselbrand', 'Hullbreacher', 'Iona, Shield of Emeria',
        'Jeweled Lotus', 'Karakas', 'Leovold, Emissary of Trest',
        'Library of Alexandria', 'Limited Resources', 'Lutri, the Spellchaser',
        'Mana Crypt', 'Mox Emerald', 'Mox Jet', 'Mox Pearl',
        'Mox Ruby', 'Mox Sapphire', 'Nadu, Winged Wisdom',
        'Paradox Engine', 'Panoptic Mirror', 'Primeval Titan',
        'Prophet of Kruphix', 'Recurring Nightmare', 'Rofellos, Llanowar Emissary',
        'Shahrazad', 'Sundering Titan', 'Sway of the Stars',
        'Sylvan Primordial', 'Time Vault', 'Time Walk',
        'Tinker', 'Tolarian Academy', 'Trade Secrets',
        'Upheaval', 'Worldfire', 'Yawgmoths Bargain'
    ]

    # Basic lands
    BASIC_LANDS = [
        'Plains', 'Island', 'Swamp', 'Mountain', 'Forest', 'Wastes',
        'Snow-Covered Plains', 'Snow-Covered Island', 'Snow-Covered Swamp',
        'Snow-Covered Mountain', 'Snow-Covered Forest'
    ]

    # Color combinations for the 32 deck challenge
    COLOR_COMBINATIONS = {
        'C': 'Colorless',
        'W': 'White (Mono-White)',
        'U': 'Blue (Mono-Blue)',
        'B': 'Black (Mono-Black)',
        'R': 'Red (Mono-Red)',
        'G': 'Green (Mono-Green)',
        'WU': 'Azorius (White-Blue)',
        'WB': 'Orzhov (White-Black)',
        'WR': 'Boros (White-Red)',
        'WG': 'Selesnya (White-Green)',
        'UB': 'Dimir (Blue-Black)',
        'UR': 'Izzet (Blue-Red)',
        'UG': 'Simic (Blue-Green)',
        'BR': 'Rakdos (Black-Red)',
        'BG': 'Golgari (Black-Green)',
        'RG': 'Gruul (Red-Green)',
        'WUB': 'Esper (White-Blue-Black)',
        'WUR': 'Jeskai (White-Blue-Red)',
        'WUG': 'Bant (White-Blue-Green)',
        'WBR': 'Mardu (White-Black-Red)',
        'WBG': 'Abzan (White-Black-Green)',
        'WRG': 'Naya (White-Red-Green)',
        'UBR': 'Grixis (Blue-Black-Red)',
        'UBG': 'Sultai (Blue-Black-Green)',
        'URG': 'Temur (Blue-Red-Green)',
        'BRG': 'Jund (Black-Red-Green)',
        'WUBR': 'Yore-Tiller (No Green)',
        'WUBG': 'Witch-Maw (No Red)',
        'WURG': 'Ink-Treader (No Black)',
        'WBRG': 'Dune-Brood (No Blue)',
        'UBRG': 'Glint-Eye (No White)',
        'WUBRG': 'Five-Color'
    }

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
