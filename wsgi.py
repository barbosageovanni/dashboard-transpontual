#!/usr/bin/env python3
import os
import sys

print("🚀 SISTEMA TRANSPONTUAL - IMPORTAÇÃO LIMPA")

# Configuração básica
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('DATABASE_URL', 'postgresql://postgres:Mariaana953%407334@db.lijtncazuwnbydeqtoyz.supabase.co:5432/postgres')

# Desabilitar logs
import logging
logging.getLogger().setLevel(logging.ERROR)

# Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # IMPORTAR APENAS SEU SISTEMA - SEM MODIFICAÇÕES
    from app import create_app
    from config import ProductionConfig
    
    # CRIAR APLICAÇÃO ORIGINAL
    application = create_app(ProductionConfig)
    
    print("✅ SISTEMA ORIGINAL CARREGADO!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    
    # Fallback mínimo
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def erro():
        return f'''
        <h1>Sistema Transpontual</h1>
        <p>Erro ao carregar sistema original: {e}</p>
        <p>Verifique os arquivos do projeto.</p>
        '''

# Exportar
app = application

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port)
