#!/usr/bin/env python
"""
Database initialization script.
Run this script to create the database schema.
"""

import os
from app import create_app, db
from app.models import Deck, Card, DeckCard

def init_database():
    """Initialize the database with schema."""
    app = create_app('development')

    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()

        # Check if we need to populate with initial data
        deck_count = Deck.query.count()
        if deck_count == 0:
            print("Database is empty. Ready for use!")
            print("You can now start building your 32 Commander decks!")
        else:
            print(f"Database already contains {deck_count} decks.")

        print("\nDatabase initialization complete!")
        print(f"Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print("\nRun 'python run.py' to start the application.")

if __name__ == '__main__':
    init_database()
