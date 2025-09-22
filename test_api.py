from app import create_app
from flask import url_for

app = create_app()

with app.app_context():
    try:
        # Listar todas as rotas registradas
        print("=== ROTAS REGISTRADAS ===")
        for rule in app.url_map.iter_rules():
            if 'dashboard' in rule.rule or 'api' in rule.rule:
                print(f"{rule.methods} -> {rule.rule} -> {rule.endpoint}")

        print("\n=== TESTE DE URLs ===")
        try:
            dashboard_url = url_for('dashboard.index')
            print(f"Dashboard URL: {dashboard_url}")
        except Exception as e:
            print(f"Erro dashboard URL: {e}")

        try:
            api_url = url_for('dashboard.api_dashboard_metricas')
            print(f"API Métricas URL: {api_url}")
        except Exception as e:
            print(f"Erro API URL: {e}")

    except Exception as e:
        print(f"Erro geral: {e}")