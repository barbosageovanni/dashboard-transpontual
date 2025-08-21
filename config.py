import os
from datetime import timedelta
import urllib.parse

class Config:
    '''Configuração base - Transpontual'''
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'transpontual-secret-key-2025'
    
    # Database PostgreSQL Supabase
    @staticmethod
    def get_database_url():
        '''Obter URL do banco Supabase'''
        return os.environ.get('DATABASE_URL') or 'postgresql://postgres:Mariaana953%407334@db.lijtncazuwnbydeqtoyz.supabase.co:5432/postgres'
    
    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 120,
        'pool_pre_ping': True,
        'max_overflow': 20,
        'echo': False  # SEM LOGS SQL
    }
    
    # Flask-Login
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    
    # Upload files
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    
    # App settings
    APP_NAME = 'Dashboard Transpontual'
    APP_VERSION = '3.1.0'
    COMPANY_NAME = 'Transpontual'

class DevelopmentConfig(Config):
    '''Configuração desenvolvimento'''
    DEBUG = True
    
class ProductionConfig(Config):
    '''Configuração produção'''
    DEBUG = False
    # Logs mínimos em produção
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'max_overflow': 30,
        'echo': False  # NUNCA logs SQL em produção
    }

# Configuração padrão
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
