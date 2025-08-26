import os
import socket
from datetime import timedelta
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

def _append_query_params(url: str, extra: dict) -> str:
    """Anexa/mescla parâmetros de query na URL (ex.: sslmode=require)."""
    parsed = urlparse(url)
    q = dict(parse_qsl(parsed.query, keep_blank_values=True))
    q.update(extra)
    new_query = urlencode(q)
    return urlunparse(parsed._replace(query=new_query))

def _force_ipv4_hostaddr(url: str) -> str:
    """
    Resolve IPv4 (A record) e injeta ?hostaddr=<ipv4> mantendo o host
    (necessário para SNI do TLS). Funciona com psycopg2/libpq.
    """
    parsed = urlparse(url)
    host = parsed.hostname
    port = parsed.port or 5432
    if not host:
        return url
    try:
        infos = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
        if not infos:
            return _append_query_params(url, {"sslmode": "require"})
        ipv4 = infos[0][4][0]
        return _append_query_params(url, {"hostaddr": ipv4, "sslmode": "require"})
    except Exception:
        # fallback: pelo menos garante sslmode
        return _append_query_params(url, {"sslmode": "require"})

class Config:
    """Configuração base - Transpontual"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'transpontual-secret-key-2025'

    @staticmethod
    def get_database_url() -> str:
        """
        Prioriza DATABASE_URL do ambiente.
        Recomendo usar a URL Pooled (pgbouncer) da Supabase, ex.:
        postgresql://USER:PASS@aws-0-XXXX.pooler.supabase.com:6543/postgres
        """
        url = os.environ.get('DATABASE_URL')
        if url:
            url = _append_query_params(url, {"sslmode": "require"})
            if os.environ.get("FORCE_IPV4", "0") == "1":
                url = _force_ipv4_hostaddr(url)
            return url

        # Fallback SOMENTE para desenvolvimento local (sem segredos no código!)
        # -> substitua por suas variáveis de ambiente locais se precisar
        user = os.environ.get('DB_USER', 'postgres')
        password = os.environ.get('DB_PASSWORD', '')
        host = os.environ.get('DB_HOST', 'db.lijtncazuwnbydeqtoyz.supabase.co')
        port = os.environ.get('DB_PORT', '5432')
        database = os.environ.get('DB_NAME', 'postgres')

        base = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        base = _append_query_params(base, {"sslmode": "require"})
        if os.environ.get("FORCE_IPV4", "0") == "1":
            base = _force_ipv4_hostaddr(base)
        return base


    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        # pooling
        'pool_size': int(os.environ.get('DB_POOL_SIZE', 10)),
        'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', 20)),
        'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', 300)),
        'pool_pre_ping': True,
        # garante TLS quando o driver respeita connect_args
        'connect_args': {'sslmode': 'require'},
        'echo': False,
    }

    # Flask-Login
    REMEMBER_COOKIE_DURATION = timedelta(days=7)

    # Upload files
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # App settings
    APP_NAME = 'Dashboard Transpontual'
    APP_VERSION = '3.1.0'
    COMPANY_NAME = 'Transpontual'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        **Config.SQLALCHEMY_ENGINE_OPTIONS,
        'pool_size': int(os.environ.get('DB_POOL_SIZE', 20)),
        'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', 30)),
        'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', 300)),
        'echo': False,
    }

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
