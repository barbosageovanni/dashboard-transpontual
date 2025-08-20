# app/routes/health_check.py
from flask import Blueprint, current_app, jsonify, request, abort
from datetime import datetime
import os
import platform
import socket

from app import db

bp = Blueprint("health_check", __name__)

STARTED_AT = datetime.utcnow()

def _mask_db_url():
    try:
        eng = db.get_engine()
        # SQLAlchemy 2.x: esconder senha
        return eng.url.render_as_string(hide_password=True)
    except Exception as e:
        return f"unavailable ({e})"

def _is_writable(path: str) -> bool:
    try:
        test_file = os.path.join(path, ".writable_check")
        with open(test_file, "w") as f:
            f.write("ok")
        os.remove(test_file)
        return True
    except Exception:
        return False

def _require_debug_token():
    token_env = os.getenv("DEBUG_TOKEN")
    if not token_env:
        abort(403, description="DEBUG_TOKEN não configurado")
    token_hdr = request.headers.get("X-Debug-Token", "")
    if token_hdr != token_env:
        abort(403, description="Token inválido")

@bp.route("/health")
def health():
    return jsonify({"status": "ok", "service": "dashboard-transpontual"})

@bp.route("/debug")
def debug():
    # Proteção por token
    _require_debug_token()

    # Teste DB
    db_ok = False
    db_error = None
    try:
        db.session.execute(db.text("SELECT 1"))
        db_ok = True
    except Exception as e:
        db_error = str(e)

    upload_folder = current_app.config.get("UPLOAD_FOLDER", "app/static/uploads")

    info = {
        "app": {
            "name": current_app.config.get("APP_NAME", "Dashboard Baker"),
            "env": os.getenv("FLASK_ENV", "production"),
            "debug": bool(current_app.debug),
            "started_at_utc": STARTED_AT.isoformat() + "Z",
            "version": current_app.config.get("APP_VERSION", "3.0"),
        },
        "host": {
            "hostname": socket.gethostname(),
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "database": {
            "connected": db_ok,
            "url_masked": _mask_db_url(),
            "error": db_error,
        },
        "storage": {
            "upload_folder": upload_folder,
            "exists": os.path.isdir(upload_folder),
            "writable": _is_writable(upload_folder),
        },
        "packages": {
            # versões úteis (tolerante a ausência)
            "flask": __import__("flask").__version__,
            "werkzeug": __import__("werkzeug").__version__,
            "pandas": getattr(__import__("pandas"), "__version__", "not-installed"),
        },
    }
    return jsonify(info)
