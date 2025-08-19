import os
from datetime import timedelta
import urllib.parse

class Config:
    """Configuração base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-baker-2025'
    
    # Database PostgreSQL Supabase
    @staticmethod
    def get_database_uri():
        # Tentar DATABASE_URL primeiro (produção)
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            return database_url
            
        # Fallback para componentes individuais
        host = os.environ.get('DB_HOST', 'db.lijtncazuwnbydeqtoyz.supabase.co')
        database = os.environ.get('DB_NAME', 'postgres')
        user = os.environ.get('DB_USER', 'postgres')
        password = os.environ.get('DB_PASSWORD', 'Mariaana953@7334')
        port = os.environ.get('DB_PORT', '5432')
        
        # Escapar senha para URL
        password_escaped = urllib.parse.quote_plus(password)
        
        # Montar URI
        uri = f'postgresql://{user}:{password_escaped}@{host}:{port}/{database}'
        return uri
    
    # Usar método estático para obter URI
    SQLALCHEMY_DATABASE_URI = get_database_uri.__func__()
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {'sslmode': 'require'},
        'echo': False
    }
    
    # Upload
    UPLOAD_FOLDER = 'app/static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Criar pasta de upload
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class DevelopmentConfig(Config):
    """Configuração de desenvolvimento"""
    DEBUG = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        **Config.SQLALCHEMY_ENGINE_OPTIONS,
        'echo': True
    }

class ProductionConfig(Config):
    """Configuração de produção"""
    DEBUG = False
    
    # Configurações específicas de produção
    SQLALCHEMY_ENGINE_OPTIONS = {
        **Config.SQLALCHEMY_ENGINE_OPTIONS,
        'echo': False,
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 30
    }
    
    # Security headers
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'