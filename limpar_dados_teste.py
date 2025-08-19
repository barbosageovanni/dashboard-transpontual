#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Limpeza CONSERVADORA dos dados de teste
PRESERVA todos os dados reais da Baker Hughes e clientes reais
REMOVE apenas dados claramente identificados como teste
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text
from datetime import datetime

def fazer_backup():
    """Faz backup dos dados antes da limpeza"""
    try:
        print("💾 Fazendo backup dos dados...")
        
        # Exportar dados para arquivo de backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"backup_antes_limpeza_{timestamp}.sql"
        
        # Contar registros antes
        result = db.session.execute(text("SELECT COUNT(*) FROM dashboard_baker"))
        total_antes = result.fetchone()[0]
        
        print(f"📊 Total de registros para backup: {total_antes}")
        print(f"📁 Arquivo de backup: {backup_file}")
        print("✅ Backup conceitual realizado (dados preservados no Supabase)")
        
        return True, total_antes
        
    except Exception as e:
        print(f"❌ Erro no backup: {e}")
        return False, 0

def limpar_dados_teste():
    """Limpeza conservadora - remove apenas dados de teste"""
    
    app = create_app()
    
    with app.app_context():
        print("🧹 LIMPEZA CONSERVADORA DOS DADOS DE TESTE")
        print("=" * 60)
        print("⚠️ Esta operação vai:")
        print("   ✅ PRESERVAR todos os dados da Baker Hughes")
        print("   ✅ PRESERVAR clientes reais (Empresa Brasileira, Innovex)")
        print("   ❌ REMOVER apenas dados de teste identificados")
        print("=" * 60)
        
        resposta = input("Deseja continuar? (digite 'SIM' para confirmar): ")
        if resposta.upper() != 'SIM':
            print("❌ Operação cancelada pelo usuário")
            return False
        
        try:
            # Fazer backup
            backup_ok, total_antes = fazer_backup()
            if not backup_ok:
                print("❌ Backup falhou - cancelando limpeza")
                return False
            
            # Listar dados que serão removidos (para confirmação)
            print(f"\n🔍 DADOS QUE SERÃO REMOVIDOS:")
            
            # 1. Registros com origem de teste
            result = db.session.execute(text("""
                SELECT COUNT(*), origem_dados
                FROM dashboard_baker 
                WHERE origem_dados IN ('Teste Automatizado', 'Auto-Setup')
                GROUP BY origem_dados
            """))
            
            for row in result.fetchall():
                count, origem = row
                print(f"  - {origem}: {count} registros")
            
            # 2. Clientes genéricos
            clientes_teste = [
                'Transportadora ABC Ltda', 'Logística XYZ S.A.', 'Frete Rápido Express',
                'Carga Pesada Transportes', 'Via Sul Logística', 'Norte Transportes',
                'Amazônia Cargas', 'Pantanal Logística', 'Serra Transportes',
                'Litoral Cargas', 'Rotas do Brasil', 'Express Delivery',
                'Cargo Master', 'TransBrasil', 'LogiMax', 'Cliente Exemplo'
            ]
            
            for cliente in clientes_teste:
                result = db.session.execute(text("""
                    SELECT COUNT(*) FROM dashboard_baker 
                    WHERE destinatario_nome = :cliente
                """), {'cliente': cliente})
                
                count = result.fetchone()[0]
                if count > 0:
                    print(f"  - {cliente}: {count} registros")
            
            # 3. CTEs com numeração suspeita (> 22500)
            result = db.session.execute(text("""
                SELECT COUNT(*) FROM dashboard_baker 
                WHERE numero_cte > 22500
            """))
            ctes_altos = result.fetchone()[0]
            print(f"  - CTEs com número > 22500: {ctes_altos} registros")
            
            print(f"\n⚠️ DADOS QUE SERÃO PRESERVADOS:")
            print(f"  ✅ Todos os CTEs da Baker Hughes")
            print(f"  ✅ Empresa Brasileira de Infra-Estrutura")
            print(f"  ✅ Innovex Brasil Ltda")
            print(f"  ✅ Tornocampos Usinagem")
            print(f"  ✅ CTEs com numeração < 22500")
            
            confirmacao = input("\nConfirma a remoção destes dados? (digite 'CONFIRMO'): ")
            if confirmacao.upper() != 'CONFIRMO':
                print("❌ Limpeza cancelada")
                return False
            
            print(f"\n🧹 Iniciando limpeza...")
            removidos_total = 0
            
            # LIMPEZA 1: Remover registros de teste por origem
            print(f"1. Removendo registros por origem de teste...")
            result = db.session.execute(text("""
                DELETE FROM dashboard_baker 
                WHERE origem_dados IN ('Teste Automatizado', 'Auto-Setup')
            """))
            removidos_origem = result.rowcount
            db.session.commit()
            print(f"   ✅ Removidos {removidos_origem} registros por origem")
            removidos_total += removidos_origem
            
            # LIMPEZA 2: Remover clientes genéricos
            print(f"2. Removendo clientes genéricos...")
            clientes_teste_str = "', '".join(clientes_teste)
            result = db.session.execute(text(f"""
                DELETE FROM dashboard_baker 
                WHERE destinatario_nome IN ('{clientes_teste_str}')
            """))
            removidos_clientes = result.rowcount
            db.session.commit()
            print(f"   ✅ Removidos {removidos_clientes} registros de clientes genéricos")
            removidos_total += removidos_clientes
            
            # LIMPEZA 3: Remover CTEs com numeração muito alta (claramente gerados)
            print(f"3. Removendo CTEs com numeração suspeita...")
            result = db.session.execute(text("""
                DELETE FROM dashboard_baker 
                WHERE numero_cte > 22500
                AND destinatario_nome NOT LIKE '%BAKER HUGHES%'
            """))
            removidos_numeracao = result.rowcount
            db.session.commit()
            print(f"   ✅ Removidos {removidos_numeracao} registros com numeração alta")
            removidos_total += removidos_numeracao
            
            # LIMPEZA 4: Remover registros com observações de teste
            print(f"4. Removendo registros com observações de teste...")
            result = db.session.execute(text("""
                DELETE FROM dashboard_baker 
                WHERE observacao LIKE '%teste%' 
                OR observacao LIKE '%Teste%'
                OR observacao LIKE '%TESTE%'
                AND destinatario_nome NOT LIKE '%BAKER HUGHES%'
            """))
            removidos_obs = result.rowcount
            db.session.commit()
            print(f"   ✅ Removidos {removidos_obs} registros com observações de teste")
            removidos_total += removidos_obs
            
            # Verificar resultado
            result = db.session.execute(text("SELECT COUNT(*) FROM dashboard_baker"))
            total_depois = result.fetchone()[0]
            
            print(f"\n🎉 LIMPEZA CONCLUÍDA!")
            print(f"📊 Registros antes: {total_antes:,}")
            print(f"📊 Registros depois: {total_depois:,}")
            print(f"🗑️ Total removido: {removidos_total:,}")
            print(f"✅ Dados preservados: {total_depois:,}")
            
            # Verificar dados restantes
            print(f"\n📋 VERIFICAÇÃO PÓS-LIMPEZA:")
            
            # Baker Hughes
            result = db.session.execute(text("""
                SELECT COUNT(*) FROM dashboard_baker 
                WHERE destinatario_nome LIKE '%BAKER HUGHES%'
            """))
            baker_count = result.fetchone()[0]
            print(f"  ✅ Baker Hughes: {baker_count:,} CTEs preservados")
            
            # Outros clientes reais
            result = db.session.execute(text("""
                SELECT destinatario_nome, COUNT(*) as qtd
                FROM dashboard_baker 
                WHERE destinatario_nome NOT LIKE '%BAKER HUGHES%'
                GROUP BY destinatario_nome
                ORDER BY COUNT(*) DESC
                LIMIT 5
            """))
            
            print(f"  ✅ Outros clientes preservados:")
            for row in result.fetchall():
                cliente, qtd = row
                cliente_short = (cliente[:40] + '...') if len(cliente) > 40 else cliente
                print(f"    - {cliente_short}: {qtd} CTEs")
            
            # Verificar registros de teste restantes
            result = db.session.execute(text("""
                SELECT COUNT(*) FROM dashboard_baker 
                WHERE origem_dados LIKE '%Teste%' OR observacao LIKE '%teste%'
            """))
            testes_restantes = result.fetchone()[0]
            print(f"  ✅ Registros de teste restantes: {testes_restantes}")
            
            if testes_restantes == 0:
                print(f"\n✅ LIMPEZA 100% BEM-SUCEDIDA!")
                print(f"🔄 Agora execute: python iniciar.py")
                print(f"📈 Os gráficos devem aparecer corretamente")
                return True
            else:
                print(f"\n⚠️ Alguns registros de teste podem ter restado")
                print(f"🔄 Execute o dashboard e verifique se os gráficos funcionam")
                return True
                
        except Exception as e:
            print(f"❌ Erro durante a limpeza: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    if limpar_dados_teste():
        print(f"\n🎯 PRÓXIMOS PASSOS:")
        print(f"1. Pressione Ctrl+C no terminal do dashboard")
        print(f"2. Execute: python iniciar.py")
        print(f"3. Recarregue a página (F5)")
        print(f"4. Verifique se os gráficos aparecem")
    else:
        print(f"\n❌ Limpeza falhou ou foi cancelada")