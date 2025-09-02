#!/usr/bin/env python3
"""
Teste mínimo para identificar conflito de rotas
"""

from flask import Flask
from app.routes import analise_financeira

app = Flask(__name__)

try:
    from app.routes.analise_financeira import bp
    app.register_blueprint(bp)
    print("✅ Blueprint registrado com sucesso!")
    
    # Listar todas as rotas
    print("\n📋 Rotas registradas:")
    for rule in app.url_map.iter_rules():
        if 'analise_financeira' in str(rule.endpoint):
            print(f"  {rule.endpoint}: {rule.rule}")
            
except Exception as e:
    print(f"❌ Erro ao registrar blueprint: {e}")
    print(f"Tipo do erro: {type(e).__name__}")
