#!/usr/bin/env python3
"""
WSGI simples - Importa do app.py funcionando
"""

from app import app

if __name__ == "__main__":
    app.run()