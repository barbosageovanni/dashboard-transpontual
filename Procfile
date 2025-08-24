web: gunicorn wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120 --max-requests 1000
release: python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('Banco inicializado')"
