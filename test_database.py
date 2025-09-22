from app import create_app
from app.models.cte import CTE

app = create_app()
with app.app_context():
    try:
        total_ctes = CTE.query.count()
        print(f'Total CTEs na base: {total_ctes}')

        if total_ctes > 0:
            primeiro_cte = CTE.query.first()
            print(f'Primeiro CTE: {primeiro_cte.numero_cte}, Valor: R$ {primeiro_cte.valor_total}')

            # Teste da query das métricas
            from app import db
            import pandas as pd

            sql_query = "SELECT COUNT(*) as total FROM dashboard_baker"
            df = pd.read_sql_query(sql_query, db.engine)
            print(f'Total registros na tabela dashboard_baker: {df.iloc[0]["total"]}')

            sql_query2 = "SELECT SUM(valor_total) as soma FROM dashboard_baker"
            df2 = pd.read_sql_query(sql_query2, db.engine)
            print(f'Soma valores na tabela: R$ {df2.iloc[0]["soma"]}')

        else:
            print('Nenhum CTE encontrado na base de dados!')

    except Exception as e:
        print(f'Erro ao acessar dados: {e}')