# Routes
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Routes Package - Dashboard Baker Flask
app/routes/__init__.py - ATUALIZADO COM ANÁLISE FINANCEIRA
"""

# Importar todos os blueprints disponíveis
from . import auth
from . import dashboard  
from . import baixas
from . import ctes
from . import api
from . import analise_financeira  # ✨ NOVO
from . import admin

# Lista de todos os blueprints para facilitar registro
__all__ = [
    'auth',
    'dashboard', 
    'baixas',
    'ctes',
    'api',
    'analise_financeira',  # ✨ NOVO
    'admin'
]

# Metadados do pacote
PACKAGE_VERSION = "3.1.0"
MODULES_LOADED = [
    "🔐 Autenticação e Usuários",
    "📊 Dashboard Principal", 
    "💳 Sistema de Baixas",
    "📋 Gestão de CTEs",
    "🔗 API REST",
    "📈 Análise Financeira",  # ✨ NOVO
    "🛠️ Administração"
]

def get_routes_info():
    """Retorna informações sobre as rotas carregadas"""
    return {
        'version': PACKAGE_VERSION,
        'modules': MODULES_LOADED,
        'blueprints': __all__,
        'total_modules': len(__all__)
    }