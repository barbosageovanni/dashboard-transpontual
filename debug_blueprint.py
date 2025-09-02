#!/usr/bin/env python3
"""
Script para listar todos os endpoints do blueprint
"""

from flask import Flask
import importlib

app = Flask(__name__)

try:
    # Import direto
    from app.routes.analise_financeira import bp
    
    print("✅ Blueprint importado com sucesso!")
    print(f"Nome do blueprint: {bp.name}")
    print(f"Prefix: {bp.url_prefix}")
    
    # Listar todas as rotas definidas no blueprint
    print("\n📋 Rotas definidas no blueprint:")
    for rule in bp.deferred_functions:
        print(f"  {rule}")
    
    # Registrar no Flask temporariamente
    with app.app_context():
        app.register_blueprint(bp)
        
        print("\n🔗 Endpoints registrados:")
        for rule in app.url_map.iter_rules():
            if 'analise_financeira' in str(rule.endpoint):
                print(f"  {rule.endpoint}: {rule.rule}")
        
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
