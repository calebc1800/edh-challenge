#!/usr/bin/env python
"""
Database migration script to add new columns for print selection.
Run this if you have an existing database from the previous version.
"""

import sqlite3
import os

def migrate_database():
    """Add new columns to existing database."""
    db_path = 'mtg_commander.db'

    if not os.path.exists(db_path):
        print("No existing database found. Run init_db.py first.")
        return

    print("Migrating database...")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Add new columns to cards table
        print("Adding image_url_small column to cards table...")
        cursor.execute('''
            ALTER TABLE cards ADD COLUMN image_url_small VARCHAR(500)
        ''')

        print("Adding collector_number column to cards table...")
        cursor.execute('''
            ALTER TABLE cards ADD COLUMN collector_number VARCHAR(20)
        ''')

        # Add new columns to deck_cards table
        print("Adding selected_printing_id column to deck_cards table...")
        cursor.execute('''
            ALTER TABLE deck_cards ADD COLUMN selected_printing_id VARCHAR(50)
        ''')

        print("Adding selected_image_url column to deck_cards table...")
        cursor.execute('''
            ALTER TABLE deck_cards ADD COLUMN selected_image_url VARCHAR(500)
        ''')

        print("Adding selected_set_code column to deck_cards table...")
        cursor.execute('''
            ALTER TABLE deck_cards ADD COLUMN selected_set_code VARCHAR(10)
        ''')

        print("Adding selected_collector_number column to deck_cards table...")
        cursor.execute('''
            ALTER TABLE deck_cards ADD COLUMN selected_collector_number VARCHAR(20)
        ''')

        conn.commit()
        print("✓ Migration completed successfully!")

    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e).lower():
            print("Columns already exist. Database is up to date.")
        else:
            print(f"Error during migration: {e}")
            conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
