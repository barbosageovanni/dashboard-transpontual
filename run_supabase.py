#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para executar o Dashboard Baker Flask com banco Supabase (dados reais)
"""

import os
import sys
from app import create_app, db

def run_supabase():
    """Executa a aplicação com banco Supabase"""

    # Configurar variáveis de ambiente para desenvolvimento com Supabase
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('FLASK_DEBUG', '1')

    # NÃO forçar DATABASE_URL - deixar pegar do .env (Supabase)
    # As variáveis DB_HOST, DB_PORT, etc já estão no .env

    # Criar aplicação
    app = create_app()

    # Verificar conexão com banco
    with app.app_context():
        try:
            # Testar conexão
            from sqlalchemy import text
            result = db.session.execute(text('SELECT 1')).scalar()

            if result == 1:
                print("[OK] Conectado ao Supabase PostgreSQL")
                print(f"[INFO] Host: {os.getenv('DB_HOST', 'N/A')}")
                print(f"[INFO] Database: {os.getenv('DB_NAME', 'N/A')}")

                # Verificar tabelas
                from sqlalchemy import inspect
                inspector = inspect(db.engine)
                tables = inspector.get_table_names()
                print(f"[INFO] Tabelas encontradas: {len(tables)}")

                if 'ctes' in tables:
                    # Contar CTEs
                    from app.models.cte import CTE
                    total_ctes = CTE.query.count()
                    print(f"[INFO] Total de CTEs no banco: {total_ctes}")
                else:
                    print("[WARNING] Tabela 'ctes' nao encontrada")

            else:
                print("[ERROR] Falha no teste de conexao")

        except Exception as e:
            print(f"[ERROR] Erro ao conectar no Supabase: {e}")
            print("[INFO] Verifique as credenciais no arquivo .env")
            return False

    # Executar aplicação
    print("\n" + "="*50)
    print("[STARTUP] Iniciando Dashboard Baker Flask com Supabase")
    print("[INFO] Acesse: http://localhost:5000")
    print("[INFO] Para parar: Ctrl+C")
    print("="*50 + "\n")

    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=True
        )
    except KeyboardInterrupt:
        print("\n[INFO] Aplicacao encerrada pelo usuario")
    except Exception as e:
        print(f"[ERROR] Erro ao iniciar aplicacao: {e}")
        return False

    return True

if __name__ == '__main__':
    success = run_supabase()
    sys.exit(0 if success else 1)
