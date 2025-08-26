import os
import urllib.parse
from datetime import timedelta


def _normalize_db_url(url: str) -> str:
    """
    Normaliza a URL do banco para um formato aceito pelo SQLAlchemy/psycopg2.

    - Converte postgres:// -> postgresql+psycopg2://
    - Garante sslmode=require para hosts Supabase
    - Mantém querystring existente
    """
    if not url:
        return url

    url = url.strip()

    # 1) Corrigir o scheme
    if url.startswith("postgres://"):
        url = "postgresql+psycopg2://" + url[len("postgres://"):]
    elif url.startswith("postgresql://"):
        url = "postgresql+psycopg2://" + url[len("postgresql://"):]

    # 2) Garantir SSL para Supabase, se não houver
    if "supabase.co" in url and "sslmode=" not in url:
        separador = "&" if "?" in url else "?"
        url = f"{url}{separador}sslmode=require"

    return url


class Config:
    """Configuração base - Transpontual"""
    SECRET_KEY = os.getenv("SECRET_KEY", "transpontual-secret-key-2025")

    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 180,
        "pool_size": 10,
        "max_overflow": 20,
        "echo": False,  # mantenha False em produção
    }

    # Sessão / Cookies
    REMEMBER_COOKIE_DURATION = timedelta(days=7)

    # Uploads
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB

    # App
    APP_NAME = "Dashboard Transpontual"
    APP_VERSION = "3.1.0"
    COMPANY_NAME = "Transpontual"

    @staticmethod
    def get_database_url() -> str:
        """
        Ordem de precedência:
        1) SQLALCHEMY_DATABASE_URI (se você já setou diretamente)
        2) DATABASE_URL
        3) Componentes DB_* (host, porta, etc.)
        """
        # 1) Honrar se já vier pronta
        raw = os.getenv("SQLALCHEMY_DATABASE_URI")
        if raw:
            return _normalize_db_url(raw)

        # 2) DATABASE_URL
        raw = os.getenv("DATABASE_URL")
        if raw:
            return _normalize_db_url(raw)

        # 3) Montar pela família DB_*
        host = os.getenv("DB_HOST", "db.lijtncazuwnbydeqtoyz.supabase.co")
        port = os.getenv("DB_PORT", "5432")
        name = os.getenv("DB_NAME", "postgres")
        user = os.getenv("DB_USER", "postgres")
        pwd = os.getenv("DB_PASSWORD", "")

        pwd_enc = urllib.parse.quote_plus(pwd) if pwd else ""
        url = f"postgresql+psycopg2://{user}:{pwd_enc}@{host}:{port}/{name}"

        if "supabase.co" in host:
            url = f"{url}?sslmode=require"

        return url

    # Definimos um valor imediato (será sobrescrito em create_app com o método acima)
    SQLALCHEMY_DATABASE_URI = get_database_url.__func__()


class DevelopmentConfig(Config):
    """Config desenvolvimento"""
    DEBUG = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        **Config.SQLALCHEMY_ENGINE_OPTIONS,
        "echo": False,  # pode ativar True se quiser ver SQL no console
        "pool_recycle": 120,
    }


class ProductionConfig(Config):
    """Config produção"""
    DEBUG = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        **Config.SQLALCHEMY_ENGINE_OPTIONS,
        "echo": False,
        "pool_size": 20,
        "max_overflow": 30,
        "pool_recycle": 300,
    }

    # Cookies de sessão mais rígidos
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


# Mapa padrão (se você usa em algum lugar)
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
