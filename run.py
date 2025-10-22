#!/usr/bin/env python
"""
MTG Commander Deck Builder - Application Entry Point
Run this script to start the Flask development server.
"""

import os
from app import create_app

# Get configuration from environment variable or use default
config_name = os.environ.get('FLASK_CONFIG', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting MTG Commander Deck Builder on http://localhost:{port}")
    print("Press Ctrl+C to quit")
    app.run(host='127.0.0.1', port=port, debug=True)
