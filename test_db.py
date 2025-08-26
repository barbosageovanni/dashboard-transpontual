# Salve como test_db.py e execute: python test_db.py
import psycopg2

try:
    conn = psycopg2.connect(
        host="db.lijtncazuwnbydeqtoyz.supabase.co",
        port="5432", 
        database="postgres",
        user="postgres",
        password="Mariaana953@7334",
        sslmode="require"
    )
    print("Conexao OK")
    conn.close()
except Exception as e:
    print(f"Erro: {e}")